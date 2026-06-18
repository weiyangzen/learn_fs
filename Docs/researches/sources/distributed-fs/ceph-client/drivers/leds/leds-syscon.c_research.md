# sources/distributed-fs/ceph-client/drivers/leds/leds-syscon.c

Purpose: generic syscon-backed register-bit LED driver. It exposes a LED whose state is one bit in a parent syscon regmap.

Important APIs, types, and functions: `struct syscon_led` stores LED class device, parent regmap, register offset, mask, and cached boolean state. `syscon_led_set()` writes the bit with `regmap_update_bits()`. `syscon_led_probe()` reads `reg` or legacy `offset`, reads `mask`, applies default state, and registers the LED with fwnode init data.

Control flow: probe requires a parent device and parent syscon regmap, allocates state, parses properties, handles `default-state` as on/off/keep, then registers the LED. Brightness set maps off to zero and any nonzero brightness to the mask value.

State and persistence: hardware register bit is authoritative; `state` tracks the last known driver state but is not exposed through a get callback. `LEDS_DEFSTATE_KEEP` reads the current register bit at probe.

Dependencies and integration points: syscon MFD/regmap, OF, LED class, built-in platform driver, compatible `register-bit-led`, and `suppress_bind_attrs` to avoid manual bind/unbind.

Risks and test signals: test default-state handling, mask/offset parsing, parent regmap lookup errors, and shared register updates with other syscon consumers. Since there is no lock beyond regmap internals, concurrent updates rely on `regmap_update_bits()` atomicity.
