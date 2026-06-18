# sources/distributed-fs/ceph-client/drivers/rtc/rtc-em3027.c

Purpose: provides a minimal I2C RTC driver for the EM Microelectronic EM3027, covering only calendar read/write operations.

Important APIs/types/functions: `em3027_get_time()` reads seven watch registers starting at `EM3027_REG_WATCH_SEC` and converts BCD fields. `em3027_set_time()` writes the same watch register block from `struct rtc_time`. `em3027_probe()` checks `I2C_FUNC_I2C` and registers the RTC with `em3027_rtc_ops`.

Control flow: reads issue a two-message I2C transaction: write the starting register address, then read the seven time/date bytes. Writes send an eight-byte I2C message containing the start register followed by BCD second, minute, hour, day, weekday, month, and year. Probe does not initialize control, alarm, or status registers.

State and persistence: the hardware stores time/date. The driver stores only the `rtc_device` in client data and has no private cache.

Dependencies and integration: depends on I2C, RTC core, BCD helpers, and optional OF matching (`emmicro,em3027`).

Risks and test signals: years are assumed to be 2000-2099 via `+100` and `% 100`; alarm registers are defined but unused. No invalid-clock/status checks are performed. Test block read/write transactions, year boundary handling, adapter functionality rejection, and behavior after battery loss or invalid register contents.
