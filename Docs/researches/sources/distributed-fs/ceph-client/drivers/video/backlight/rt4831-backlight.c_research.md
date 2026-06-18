# sources/distributed-fs/ceph-client/drivers/video/backlight/rt4831-backlight.c

Purpose: Richtek RT4831 backlight subdriver. It uses the parent MFD regmap to configure OVP/OCP/channel selection and expose a raw linear backlight up to 2048 levels.

Important APIs/types/functions: `struct rt4831_priv` stores device, regmap, and backlight pointer. `rt4831_bl_update_status()` writes 11-bit brightness split across `RT4831_REG_BLDIML` and the following byte, then toggles `RT4831_BLEN_MASK`. `rt4831_bl_get_brightness()` reads enable and brightness registers. `rt4831_parse_backlight_properties()` handles common and Richtek-specific device properties.

Control flow: probe allocates private data, obtains parent regmap, parses `max-brightness`, `default-brightness`, `richtek,pwm-enable`, `richtek,bled-ovp-sel`, optional OCP microamp, and required `richtek,channel-use`, registers the backlight, and applies initial status. Remove sets brightness to zero and updates hardware.

State and persistence: brightness/power state is stored in RT4831 registers and reflected by `get_brightness`; the driver holds no separate cache.

Dependencies and integration: platform child of RT4831 MFD, device properties/OF, regmap, dt-bindings constants, backlight core suspend/resume.

Risks: brightness zero skips dim register writes and only clears enable; this is intentional but means stale brightness is restored when re-enabled. OCP uses rounded-up step after clamp. Required channel-use validation is strong, but no duplicate-channel semantics are needed because it is a bitmask. Tests should cover max/default clamping, enable/disable, raw brightness encoding/decoding, missing channel-use, OVP clamp, OCP limits, and remove path.
