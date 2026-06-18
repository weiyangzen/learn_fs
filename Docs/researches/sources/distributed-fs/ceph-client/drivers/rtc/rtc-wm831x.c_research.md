## sources/distributed-fs/ceph-client/drivers/rtc/rtc-wm831x.c

Purpose: Implements RTC support for Wolfson WM831x PMICs using a 32-bit seconds counter split across two 16-bit registers, plus a similarly split alarm counter and PM-aware alarm enable handling.

Important APIs/types/functions: `struct wm831x_rtc` stores the parent `wm831x`, RTC device, and cached alarm-enabled state. Key callbacks are `wm831x_rtc_readtime`, `wm831x_rtc_settime`, `wm831x_rtc_readalarm`, `wm831x_rtc_setalarm`, and `wm831x_rtc_alarm_irq_enable`. Alarm helpers `wm831x_rtc_start_alarm` and `wm831x_rtc_stop_alarm` manipulate `WM831X_RTC_ALM_ENA`. PM callbacks suspend/resume/freeze alarm state. `wm831x_rtc_add_randomness` feeds the write counter into kernel randomness.

Control flow: Probe reads RTC control, caches whether alarm is enabled, marks wakeup capable, allocates/registers RTC with `range_max = U32_MAX`, requests the alarm IRQ via `wm831x_irq`, and contributes the write counter to device randomness. Time reads first require `WM831X_RTC_VALID`, then bulk-read the two time registers twice until stable or retry exhaustion. Time writes split `rtc_tm_to_time64`, write high/low halves, poll the sync bit, then read back and require the update to be within one second. Alarm writes stop the alarm, write high/low alarm halves, and optionally restart. The alarm IRQ simply reports `RTC_IRQF | RTC_AF`.

State and persistence: The PMIC stores time, alarm, valid/sync/alarm-enable bits, and write counter. Driver state caches desired alarm enable so suspend can disable non-wakeup alarms and resume can restore them.

Dependencies/integration: Uses WM831x MFD register APIs, platform child device, RTC core, threaded IRQ, PM callbacks, and kernel randomness infrastructure.

Risks: The polling loop uses the hardware sync bit semantics; changes must preserve the intended wait condition. Readback verification can reject writes blocked by PMIC security policy. No explicit alarm pending state is reported. Probe logs IRQ request failure but still returns success, leaving a registered RTC without alarm interrupts if IRQ setup fails.

Test signals: Stable double-read under rollover, write acceptance/rejection paths, alarm set/enable/disable, PM suspend with and without wakeup, freeze/thaw alarm disabling, and IRQ request failure behavior.
