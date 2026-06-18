# sources/distributed-fs/ceph-client/drivers/rtc/rtc-sd3078.c

Purpose: I2C RTC driver for the SD3078. It provides read/set time using BCD time registers and optional write-protection support compiled out by default.

Important APIs/types/functions: `sd3078_enable_reg_write()` writes key bits in the documented order. `sd3078_disable_reg_write()` is present under `WRITE_PROTECT_EN`. `sd3078_rtc_read_time()` bulk reads seven time registers and converts 12-hour/24-hour modes into Linux `rtc_time`. `sd3078_rtc_set_time()` bulk writes BCD time in 24-hour mode. `sd3078_probe()` initializes the 8-bit regmap, allocates RTC, sets range 2000..2099, registers it, then enables register writes.

Control flow/state/persistence: after probe, the driver leaves register writes enabled because `WRITE_PROTECT_EN` is `0` and `sd3078_enable_reg_write()` is called after registration. Time state persists in chip registers; there is no alarm, nvmem, or oscillator-validity handling.

Dependencies/integration: I2C core, regmap, BCD helpers, RTC core, OF compatible `whwave,sd3078`, I2C ID `sd3078`.

Risks/test signals: all write-key operations ignore regmap return values, so bus failures in protection setup can be silent. Time conversion mutates no caller-owned fields except in normal RTC ops. Test 12-hour PM/AM reads, 24-hour writes, write protection build option, month/year rebasing, and I2C/regmap failure paths.
