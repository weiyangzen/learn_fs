# sources/distributed-fs/ceph-client/drivers/rtc/rtc-mpfs.c

Purpose: implements the Microchip PolarFire SoC RTC as a memory-mapped seconds counter with wake alarm support, prescaler setup, and wake IRQ integration.

Important APIs/types/functions: `struct mpfs_rtc_dev` holds the `rtc_device` and register base. `mpfs_rtc_start()` starts the counter, `mpfs_rtc_clear_irq()` disables/clears alarm state and flushes the posted write, `mpfs_rtc_readtime()`/`settime()` read and upload the 64-bit datetime split across lower/upper registers, and `mpfs_rtc_readalarm()`/`setalarm()` program alarm and compare registers. `mpfs_rtc_alarm_irq_enable()` toggles alarm-on/off control bits, and `mpfs_rtc_wakeup_irq_handler()` reports `RTC_AF`.

Control flow: probe allocates the RTC, gets/enables the `rtc` clock, maps MMIO, requests the wakeup IRQ, reads the `rtcref` clock rate to program the prescaler as rate minus one, initializes wakeup plus wake IRQ, and registers the device. Set-time writes the split datetime registers, sets `CONTROL_UPLOAD_BIT`, polls for upload completion with `read_poll_timeout()`, and restarts the RTC. Set-alarm disables the alarm, writes split alarm seconds, writes compare registers to all ones for alarm mode, then optionally sets wake mode and starts the counter.

State and persistence: hardware persists the seconds counter, prescaler, mode bits, control bits, alarm registers, and compare bypass values. Driver state is stateless beyond base address and RTC pointer. Alarm enabled state is derived from `MODE_WAKE_EN`; pending state is not returned by `read_alarm()`.

Dependencies and integration: depends on platform MMIO, two clocks named `rtc` and `rtcref`, `pm_wakeirq`, IRQ 0 as wakeup interrupt, and OF compatible `microchip,mpfs-rtc`.

Risks and test signals: `mpfs_rtc_readalarm()` reconstructs alarm time as lower register shifted by 32 plus masked upper register, which is the inverse of the set-time split and should be verified against the hardware register definition. Probe calls `devm_clk_get_enabled("rtc")` then separately `devm_clk_get("rtcref")`; missing or zero-rate `rtcref` needs coverage. Alarm mode writes `mode = MODE_WAKE_EN | MODE_WAKE_CONTINUE` only when enabling, leaving prior mode bits when disabling. Test upload timeout, posted interrupt clear, prescaler maximum, wake IRQ registration, alarm enable/disable, 42-bit range cap, and split lower/upper encoding for time and alarm.
