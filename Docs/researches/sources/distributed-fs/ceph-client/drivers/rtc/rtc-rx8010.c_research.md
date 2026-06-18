<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-rx8010.c -->
# sources/distributed-fs/ceph-client/drivers/rtc/rtc-rx8010.c

Purpose: implements the Epson RX-8010SJ I2C RTC with time, alarm, update/periodic/alarm interrupt reporting, voltage-low ioctl, and reserved-register initialization.

Important APIs/types/functions: `struct rx8010_data` stores the regmap, RTC, and cached control register. `rx8010_init()` initializes reserved registers, clears stale flags, and caches control state. `rx8010_irq_1_handler()` reports PF/AF/UF events. RTC ops cover time, alarm, alarm IRQ enable, and `RTC_VL_READ`.

Control flow: probe allocates state, initializes I2C regmap, runs hardware init, allocates RTC, requests optional IRQ, clears alarm feature when IRQ is absent, sets range 2000-2099, and registers. Time reads reject VLF and decode seven BCD registers. Set-time sets STOP, writes time, clears STOP, and clears VLF. Alarm programming disables AIE/UIE from the cached control byte, clears AF, writes minute/hour, configures day-of-month matching by clearing WADA, writes day or AE wildcard, and re-enables AIE/UIE based on RTC core timers.

State and persistence: time, alarm, flags, extension, control, timer, and reserved registers live in hardware. The cached `ctrlreg` mirrors control bits and is used to avoid read-modify-write drift during alarm operations.

Dependencies and integration points: depends on I2C regmap, RTC core, OF/I2C IDs, optional IRQ from firmware, and RTC UIE/AIE timer state.

Risks and test signals: no explicit I2C functionality check is done before regmap creation. `tm_wday` read uses `ffs()` without subtracting one. `set_alarm()` bulk-writes only two bytes initially, then writes the day register separately, so partial failures can leave mixed alarm state. Test reserved-register initialization, VLF read/set/clear, IRQ flag clearing, alarm with day wildcard, UIE/AIE combination, missing IRQ feature clearing, and weekday interpretation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-rx8010.c -->
