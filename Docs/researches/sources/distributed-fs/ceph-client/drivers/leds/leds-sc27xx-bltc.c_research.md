# sources/distributed-fs/ceph-client/drivers/leds/leds-sc27xx-bltc.c

Purpose: Spreadtrum SC27xx breathing light controller driver for up to three PMIC LED channels. It supports direct brightness and hardware breathing patterns through PMIC regmap registers.

Important APIs, types, and functions: `struct sc27xx_led_priv` holds regmap, base offset, mutex, and channel array. `sc27xx_led_init()` enables PMIC BLTC and RTC clocks and clears RGB power-down. `sc27xx_led_set()` selects enable/disable. `sc27xx_led_pattern_set()` accepts exactly four pattern tuples for rise, high, fall, and low times. `sc27xx_led_pattern_clear()` clears curve registers and disables run/type bits.

Control flow: probe validates child count and parent regmap, reads the controller `reg`, records active child channels by child `reg`, initializes the mutex, then registers active LEDs. Brightness writes update the duty register and per-line control bits. Pattern writes clamp/align each duration to 125 ms hardware steps, writes curve registers, writes duty from the high-stage brightness, and enables breathing mode.

State and persistence: active channel selection and fwnodes are stored in driver memory. Hardware registers hold run/type, duty, and curve state. Pattern clear updates `ldev->brightness` to off.

Dependencies and integration points: uses regmap from the parent PMIC, OF child nodes, LED pattern APIs, and `sprd,sc2731-bltc` compatible binding. The default LED trigger is `pattern`.

Risks and test signals: test invalid child counts, duplicate/out-of-range channel `reg`, exact four-tuple pattern validation, clamping at min/max duration, direct-to-pattern transitions, and mutex coverage when multiple LED channels are written concurrently.
