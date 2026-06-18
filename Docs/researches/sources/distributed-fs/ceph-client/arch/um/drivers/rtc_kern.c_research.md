<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/drivers/rtc_kern.c -->
# sources/distributed-fs/ceph-client/arch/um/drivers/rtc_kern.c

Purpose: implements a UML RTC class device that can wake the guest from suspend and integrate with UML time-travel mode.

Important APIs/types/functions: global state includes `uml_rtc_alarm_time`, `uml_rtc_alarm_enabled`, `uml_rtc`, `uml_rtc_irq_fd`, and `uml_rtc_irq`. RTC ops are `uml_rtc_read_time()`, `uml_rtc_read_alarm()`, `uml_rtc_alarm_irq_enable()`, and `uml_rtc_set_alarm()`. Driver lifecycle functions are `uml_rtc_setup()`, `uml_rtc_cleanup()`, `uml_rtc_probe()`, `uml_rtc_remove()`, and `uml_rtc_init()`.

Control flow: probe starts a host interrupt source with `uml_rtc_start()`, registers a read IRQ, marks it wake-capable, allocates/registers an RTC device, and enables device wakeup. Alarm enable computes seconds from persistent clock to target time; in normal mode it programs host `timerfd`, while time-travel mode schedules a relative `time_travel_event`. IRQ handling disables the alarm, drains the FD, calls `pm_system_wakeup()`, and reports `RTC_IRQF | RTC_AF`.

State and persistence: alarm target/enabled state is in memory only. Time reading uses persistent clock so time-travel mode sees simulated time. No RTC NVRAM is implemented.

Dependencies and integration points: depends on platform device/driver, RTC class, PM wakeup, UML IRQs, `read_persistent_clock64()`, time-travel APIs, and host helpers in `rtc_user.c`.

Risks: negative or past alarm deltas are not deeply validated before unsigned conversion. Cleanup must free IRQ and stop host timer/pipe. Time-travel and normal modes have different FD semantics.

Test signals: register `/dev/rtc*`, read time, set/read/enable/disable alarms, suspend wakeup via `rtcwake`, time-travel alarm delivery, remove driver, and verify IRQ wake flag behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/drivers/rtc_kern.c -->
