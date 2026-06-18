# sources/distributed-fs/ceph-client/drivers/rtc/rtc-sd2405al.c

Purpose: I2C/regmap RTC driver for the DFRobot SD2405AL chip. It implements time read/write only, using BCD-encoded hardware registers and a protected write-enable sequence.

Important APIs/types/functions: `struct sd2405al` stores `dev` and `regmap`. `sd2405al_enable_reg_write()` and `sd2405al_disable_reg_write()` perform the ordered `WRTC1/WRTC2/WRTC3` control-bit sequence. `sd2405al_read_time()` bulk reads time registers and handles both 24-hour and 12-hour PM formats. `sd2405al_set_time()` writes BCD data in 24-hour mode, clears the time-trim flag register, then disables writes. `sd2405al_probe()` checks I2C functionality, creates an 8-bit regmap, allocates and registers the RTC with a 2000..2099 range.

Control flow/state/persistence: probe is simple and does not initialize the chip time. Runtime state is in battery-backed chip registers and control write-enable bits. `set_time` temporarily opens write access and should normally leave writes disabled.

Dependencies/integration: I2C core, regmap I2C, RTC core, BCD helpers, compatible `dfrobot,sd2405al`, I2C ID `sd2405al`, address documented as 0x32.

Risks/test signals: the error path in `sd2405al_set_time()` can return before disabling register writes if the bulk write or flag clear fails. Tests should cover 12-hour PM conversion, month/year offsets, write-enable ordering, failed-regmap cleanup behavior, and range boundaries 2000/2099.
