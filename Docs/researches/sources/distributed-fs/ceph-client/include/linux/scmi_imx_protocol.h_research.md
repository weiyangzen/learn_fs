# sources/distributed-fs/ceph-client/include/linux/scmi_imx_protocol.h

Purpose: declares NXP i.MX vendor SCMI protocol IDs, notification payloads, and operation tables for BBM, MISC, LMM, and CPU extension protocols.

Important APIs and types: protocol IDs `SCMI_PROTOCOL_IMX_LMM`, `SCMI_PROTOCOL_IMX_BBM`, `SCMI_PROTOCOL_IMX_CPU`, `SCMI_PROTOCOL_IMX_MISC`, vendor strings, `struct scmi_imx_bbm_proto_ops`, notification event IDs, `struct scmi_imx_bbm_notif_report`, `struct scmi_imx_misc_ctrl_notify_report`, `struct scmi_imx_misc_proto_ops`, LMM constants/state enum/info struct, `struct scmi_imx_lmm_proto_ops`, and `struct scmi_imx_cpu_proto_ops` define the contract.

Control flow: SCMI protocol drivers expose operation tables through protocol handles; consumers set/get RTC time and alarms, read button state, control miscellaneous registers and notifications, fetch syslog data, control life-cycle manager power/reset/shutdown, and set/start/query CPU reset vectors.

State and persistence: persistent platform state is remote firmware-owned: RTC values, alarms, control settings, LMM state, reset vectors, and CPU started state. Kernel state is limited to reports and protocol handle dispatch.

Dependencies and integration points: depends on SCMI protocol framework, device/notifier infrastructure, bitfield helpers, and NXP i.MX firmware ABI documentation. It integrates platform drivers with vendor SCMI extensions.

Risks and test signals: risks include protocol ID collisions, firmware ABI mismatch, endian/width mistakes for 64-bit times/vectors, notification flag drift, and unsafe buffer sizing for syslog. Test with i.MX SCMI firmware, RTC/alarm/button notifications, MISC control get/set/notify, LMM boot/shutdown/reset-vector flows, CPU start/query, and absent-protocol error paths.
