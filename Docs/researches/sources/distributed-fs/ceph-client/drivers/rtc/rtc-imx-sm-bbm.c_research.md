# sources/distributed-fs/ceph-client/drivers/rtc/rtc-imx-sm-bbm.c

Purpose: provides an RTC driver for the i.MX System Manager BBM service through the SCMI i.MX BBM protocol. It supports time read/write, alarm programming, and SCMI event notification.

Important APIs/types/functions: `struct scmi_imx_bbm` stores protocol ops, RTC device, protocol handle, and notifier block. `scmi_imx_bbm_read_time()`/`set_time()` call `rtc_time_get()` and `rtc_time_set()`. `scmi_imx_bbm_set_alarm()` calls `rtc_alarm_set()` with enable=true and the alarm timestamp. `scmi_imx_bbm_alarm_irq_enable()` only handles disable by calling `rtc_alarm_set(..., false, 0)`. `scmi_imx_bbm_rtc_notifier()` reports RTC BBM events.

Control flow: SCMI probe obtains protocol operations, enables wake capability, stores driver data, allocates the RTC, registers an SCMI event notifier for `SCMI_EVENT_IMX_BBM_RTC`, and registers the RTC. Alarm events are delivered asynchronously through SCMI notifications.

State and persistence: RTC time and alarm persist in the BBM/System Manager firmware domain. Runtime state is the SCMI protocol binding and notifier.

Dependencies and integration: depends on SCMI core, i.MX SCMI BBM protocol headers, RTC core, and `module_scmi_driver()` with protocol ID matching.

Risks and test signals: alarm enable ignores `enable=1` unless an alarm is set, which is intentional but different from drivers that toggle an existing alarm. Unexpected non-RTC BBM events are logged. Test protocol-get failure, notifier registration, alarm disable path, event delivery, wake setup rollback on init failure, and U32 range behavior.
