# sources/distributed-fs/ceph-client/drivers/firmware/arm_scmi/vendors/imx/imx-sm-bbm.c

Purpose: This file implements the NXP i.MX SCMI BBM vendor protocol for RTC time/alarm, button state, GPR counts, and RTC/button notifications.

Important APIs/types/functions: `struct scmi_imx_bbm_info` caches RTC and GPR counts. Protocol ops include `rtc_time_get`, `rtc_time_set`, `rtc_alarm_set`, and `button_get`. Notification helpers map `SCMI_EVENT_IMX_BBM_RTC` and `SCMI_EVENT_IMX_BBM_BUTTON` to `IMX_BBM_RTC_NOTIFY` and `IMX_BBM_BUTTON_NOTIFY`, and `scmi_imx_bbm_fill_custom_report()` decodes flags into `scmi_imx_bbm_notif_report`.

Control flow: Init logs protocol version, reads protocol attributes for RTC/GPR counts, and stores private state. RTC set/get/alarm validate `rtc_id` against `nr_rtc`, build command payloads with 64-bit seconds split low/high, and send xfers. Button get reads a 32-bit state. Notification enablement sends RTC notification flags for update/rollover/alarm or a button enable flag. Report filling distinguishes RTC vs button events and sets source ID.

State and persistence: Runtime private state stores counts only. RTC time/alarm state is persisted by platform firmware/hardware, not by the driver. Notification subscription is runtime firmware/core state.

Dependencies and integration points: It depends on SCMI core protocol handles, notification framework, public `linux/scmi_imx_protocol.h`, and i.MX vendor IDs. It registers with `module_scmi_protocol()` using `SCMI_PROTOCOL_IMX_BBM`, vendor, and subvendor.

Risks and edge cases: Notification `src_id` is ignored for RTC enablement and always sends RTC ID 0, which may be intentional but limits multi-RTC handling. RTC report sets `*src_id` to `rtc_evt` rather than RTC ID, which affects notification source routing. Attribute parsing assumes firmware returns valid counts. RTC time units are seconds.

Test signals: Test RTC count validation, get/set/alarm enable/disable, button state, notification enable/disable for RTC/button, report decoding for all RTC flags, multi-RTC firmware behavior, and module alias matching by vendor protocol ID.
