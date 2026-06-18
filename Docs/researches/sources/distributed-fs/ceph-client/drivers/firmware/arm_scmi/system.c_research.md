# sources/distributed-fs/ceph-client/drivers/firmware/arm_scmi/system.c

Purpose: This file implements the SCMI System Power protocol notification decoder. It does not expose normal protocol ops; it registers event support so consumers such as `scmi_power_control.c` can subscribe to platform-originated system power state notifications.

Important APIs/types/functions: `struct scmi_system_info` records graceful timeout support and whether `SYSTEM_POWER_STATE_NOTIFY` exists. `scmi_system_request_notify()` sends notify enable/disable. `scmi_system_set_notify_enabled()` is the notification core hook. `scmi_system_fill_custom_report()` decodes agent ID, flags, state, and optional timeout into `scmi_system_power_state_notifier_report`. `system_protocol_events` describes one source and one event.

Control flow: Protocol init allocates private state, marks graceful timeout support for major version 2 or later, checks whether notify command is supported, and stores private state. The notification core calls support checks, enablement, and report filling when a P2A event arrives. Timeout is accepted only for graceful shutdown when the protocol version supports it.

State and persistence: Runtime private state is devm-managed. There is a fixed `SCMI_SYSTEM_NUM_SOURCES` of 1. No persistent storage is used.

Dependencies and integration points: It depends on `protocols.h`, `notify.h`, SCMI public system power report types, and the SCMI notification framework. It registers as `SCMI_PROTOCOL_SYSTEM` and feeds the system power control driver.

Risks and edge cases: Payload size differs by version because the timeout field is optional. Report filling rejects unexpected sizes and unsupported event IDs. Timeout is zeroed for non-shutdown or non-graceful requests even if payload includes a value. The protocol exposes no ops, only events.

Test signals: Test version 1 vs version 2 payload sizes, notify command absent/present, graceful shutdown timeout parsing, non-shutdown timeout zeroing, invalid payload sizes, and notifier registration by the system power driver.
