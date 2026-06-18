# sources/distributed-fs/ceph-client/drivers/regulator/tps65132-regulator.c

Purpose: I2C regulator driver for TPS65132 positive and negative display bias supplies.

Important APIs/types/functions: `struct tps65132_regulator` owns per-device state; `struct tps65132_reg_pdata` stores optional enable and active-discharge GPIOs, discharge duration, and cached enable GPIO state. Two descriptors expose `outp` and `outn` with linear 4.0 V to 6.0 V selectors, regmap active discharge, and custom GPIO-aware enable/disable/is-enabled operations.

Control flow: probe allocates state, creates a no-cache regmap with inaccessible register ranges, and registers two regulators. Each regulator’s OF parse callback optionally obtains an enable GPIO and an active-discharge GPIO. Enable asserts the GPIO and, if constraints request active discharge disabled, clears the hardware discharge bit. Disable deasserts enable and pulses active-discharge GPIO for the configured time.

State and persistence: voltage and active-discharge bits live in I2C registers. Enable state is cached only when an enable GPIO is available; without it `is_enabled` reports true because the driver has no readable enable bit. Active discharge timing is per-regulator DT state.

Dependencies and integration points: I2C, regmap access tables, GPIO descriptors, OF regulator child nodes, and regulator constraints.

Risks: missing optional GPIOs are ignored except deferred probe, so boards without enable GPIOs cannot observe actual enabled state. If active-discharge GPIO is present, `ti,active-discharge-time-us` is mandatory. `TPS65132_REG_CONTROL` is `0x0FF` while reg bits are 8, a value worth checking against regmap expectations.

Test signals: both regulators with and without GPIOs, deferred GPIO probe, active-discharge pulse timing, voltage selector boundaries, inaccessible register filtering, and active-discharge constraint handling.
