# sources/distributed-fs/ceph-client/drivers/leds/leds-lm3692x.c

Purpose: TI LM36922/LM36923 I2C backlight driver supporting one LED class device, optional enable GPIO/regulator, boost configuration, fault checking, and selectable LED string sync.

Important APIs/types/functions: `struct lm3692x_led` stores mutex, client, classdev, regmap, enable GPIO, regulator, selected LED enable, model id, cached boost/brightness config, and enabled flag. `lm3692x_leds_enable()` powers supplies, clears faults, writes initialization sequence, and enables selected strings. `lm3692x_brightness_set()` disables on zero or writes 11-bit brightness split across MSB/LSB registers. `lm3692x_probe_dt()` parses OVP, child `reg`, and `led-max-microamp`.

Control flow: probe allocates state, initializes regmap, registers the LED from the first child, then enables hardware immediately. Brightness ON calls enable if needed, checks faults, writes brightness registers; OFF disables device bit, GPIO, and regulator.

State and persistence: enabled state is cached under mutex. Boost control and selected LED string are parsed once. Hardware initialization is repeated on re-enable after complete OFF.

Dependencies/integration: I2C regmap with maple cache, GPIO, optional regulator `vled`, fwnode child properties, OF and I2C ids distinguishing LM36922/LM36923.

Risks: `lm3692x_brightness_set()` ignores the return value of `lm3692x_leds_enable()` before continuing. Fault check reads twice but ignores second read errors. Probe only consumes the first child node. Max-brightness formula needs boundary validation for low currents.

Test signals: LM36922 vs LM36923 LED3 selection, OVP property values, regulator/GPIO sequencing, fault flag clear/read behavior, brightness split writes, and ignored enable-error path.
