# sources/distributed-fs/ceph-client/drivers/rtc/rtc-imx-sc.c

Purpose: exposes the NXP i.MX System Controller RTC as a Linux RTC using SCU RPC for reads/alarms and an ARM SMCCC SMC call for setting time.

Important APIs/types/functions: global `rtc_ipc_handle` and `imx_sc_rtc` hold the SCU handle and RTC device. `imx_sc_rtc_read_time()` sends `IMX_SC_TIMER_FUNC_GET_RTC_SEC1970`. `imx_sc_rtc_set_time()` packs calendar fields into SMC arguments for `IMX_SIP_SRTC_SET_TIME`. `imx_sc_rtc_set_alarm()` sends `IMX_SC_TIMER_FUNC_SET_RTC_ALARM` then toggles SCU IRQ enable. `imx_sc_rtc_alarm_notify()` maps SCU RTC notifications to `rtc_update_irq()`.

Control flow: probe obtains the SCU IPC handle, marks wake-capable, allocates/registers the RTC, then registers an SCU IRQ notifier. Alarm enable calls `imx_scu_irq_group_enable()` for RTC group/bit. Notification ignores non-RTC events and reports alarm events.

State and persistence: time and alarm state are owned by system controller firmware. Driver state is global, implying single-instance design.

Dependencies and integration: depends on i.MX SCU firmware APIs, ARM SMCCC, device tree match `fsl,imx8qxp-sc-rtc`, RTC core, and SCU IRQ notifier infrastructure.

Risks and test signals: notifier registration is not devm-managed in this file, and global state limits multi-instance safety. `set_time()` returns firmware `res.a0` directly. Test SCU handle failure, SMC error propagation, alarm enable/disable, notification filtering, wake capability, and U32 range boundary.
