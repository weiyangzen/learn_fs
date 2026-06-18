# sources/distributed-fs/ceph-client/drivers/leds/leds-is31fl319x.c

Purpose: I2C/regmap LED driver for ISSI/Si-En IS31FL3190/3191/3193/3196/3199 light-effect controllers with 1, 3, 6, or 9 channels.

Important APIs/types/functions: `struct is31fl319x_chipdef` captures channel count, reset register, regmap config, current limits, and brightness callback. `is31fl3190_brightness_set()` and `is31fl3196_brightness_set()` write PWM registers, read cached PWM values to compute enabled channel bits, apply data-update registers, and enter/leave shutdown. `is31fl319x_parse_fw()` parses shutdown GPIO, child `reg`, labels/triggers, `led-max-microamp`, and optional audio gain.

Control flow: probe checks I2C functionality, initializes mutex, parses firmware, toggles optional shutdown GPIO, initializes regmap with unreadable-register cache, writes reset as a chip presence test, aggregates the minimum configured LED current for global current setting, then registers configured channels.

State and persistence: regmap is intentionally used as a write cache because hardware reads can hang. Configured child slots, max current, audio gain, and cached PWM values are software state; hardware shutdown and PWM registers hold runtime state.

Dependencies/integration: I2C, regmap flat cache, GPIO descriptor, firmware-node properties, OF compatible match data, LED class.

Risks: because hardware registers are not readable, cache correctness is essential for enable-bit computation. Per-LED current properties are collapsed to a global minimum, which may surprise board authors. Duplicate or out-of-range child `reg` values abort probe.

Test signals: check all compatible chipdefs, cache-based enable-bit updates, shutdown GPIO sequencing, current conversion for 3190 vs 3196 families, duplicate child rejection, and no hardware reads after initialization.
