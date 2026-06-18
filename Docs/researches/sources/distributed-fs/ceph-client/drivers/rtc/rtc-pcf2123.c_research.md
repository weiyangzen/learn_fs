# sources/distributed-fs/ceph-client/drivers/rtc/rtc-pcf2123.c

Purpose: implements the NXP/Philips PCF2123 and compatible RV2123 SPI RTC using regmap, with BCD time, minute-resolution alarm, offset calibration, optional IRQ, and reset/probe validation.

Important APIs/types/functions: `struct pcf2123_data` stores RTC device and SPI regmap. `pcf2123_regmap_config` sets 8-bit registers, read/write flag masks, and max register. `pcf2123_read_offset()`/`set_offset()` convert the signed 7-bit plus coarse-bit offset register to/from ppb using 2170 ppb steps. Time callbacks bulk-read/write seconds through year and use `OSC_HAS_STOPPED` validity. Alarm callbacks use minute/hour/day/month-day registers and `CTRL2_AIE/AF`. `pcf2123_rtc_irq()` checks/clears `CTRL2_AF`. `pcf2123_reset()` sends software reset, verifies STOP, and restarts.

Control flow: probe allocates state, initializes SPI regmap, tries to read current time, resets and presence-checks the chip if read-time fails, logs SPI speed, allocates RTC, optionally requests a threaded IRQ and enables wakeup, marks alarm resolution as minute, clears update interrupt feature, sets range 2000-2099 and start-time behavior, then registers. Set-time stops the counter, bulk-writes BCD time, then clears control to restart. Set-alarm disables AIE, clears AF, writes minute/hour/day and disables weekday matching, then re-enables if requested.

State and persistence: hardware persists time, alarm, control flags, oscillator-stopped flag, offset calibration, countdown timer/clockout state, and alarm flag. Driver state only stores regmap and RTC pointer. Reset clears/reinitializes control state but not Linux-side cache.

Dependencies and integration: depends on SPI, regmap, optional IRQ, OF compatibles `nxp,pcf2123`, `microcrystal,rv2123`, deprecated `nxp,rtc-pcf2123`, and SPI IDs. The device requires active-high chip select at board level.

Risks and test signals: probe resets the chip whenever read-time fails, including failures caused by an oscillator-stopped validity bit, which may clear useful diagnostic state. Offset conversion prefers coarse mode for overlapping values and clamps out-of-range requests. `pcf2123_rtc_irq()` ignores regmap read/update errors and can return `IRQ_NONE` on bus failure. Test SPI mode/CS polarity, oscillator-stopped read failure, reset presence check, offset clamp/coarse/fine mapping, alarm minute-resolution behavior, optional IRQ/fwnode trigger flags, AF clear, and 2000-2099 range.
