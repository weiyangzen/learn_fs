# sources/distributed-fs/ceph-client/drivers/firmware/arm_scmi/power.c

Purpose: implements the SCMI Power Domain protocol provider. It discovers power domains, exposes domain name and state get/set operations, supports power state change notifications, and registers itself as `SCMI_PROTOCOL_POWER`.

Important APIs/types/functions: commands include domain attributes, state set/get, state notify, and extended domain name get. `struct power_dom_info` stores per-domain synchronous/asynchronous set support, notification support, and name. `struct scmi_power_info` stores domain count, stats address/size, state notification command availability, and the domain table. `power_proto_ops` exposes `num_domains_get`, `name_get`, `state_set`, and `state_get`. Event support uses `SCMI_EVENT_POWER_STATE_CHANGED` and `struct scmi_power_state_changed_report`.

Control flow: `scmi_power_protocol_init()` allocates state, reads protocol attributes, allocates the domain table, and queries each domain. Protocol attributes supply domain count and stats area and check whether `POWER_STATE_NOTIFY` is supported. Domain attributes read capability flags and short names, then optionally replace names through the common extended-name helper for protocol v3 and newer. State set/get issue simple SCMI xfers carrying domain id and state.

Notification flow: during protocol event registration the notification core asks `scmi_power_get_num_sources()` for domain count and `scmi_power_notify_supported()` for each source. When a client registers a notifier, `scmi_power_set_notify_enabled()` issues `POWER_STATE_NOTIFY` with enable bit. RX event payloads are converted by `scmi_power_fill_custom_report()` into timestamp, agent id, domain id, and power state, with source id equal to the domain id.

State and persistence behavior: state is in-memory and devm-managed for the protocol instance lifetime. Domain names and support flags are cached after init. Firmware power domain state persists in platform firmware/hardware, but this driver only sends commands and does not persist requested state locally.

Dependencies and integration points: depends on SCMI xfer/helper operations, public SCMI power protocol types, and the notification core. It integrates with generic Linux power-domain consumers through `scmi_power_proto_ops` and with the SCMI notification core through `power_protocol_events`.

Risks and test signals: `scmi_power_name_get()` assumes callers pass a valid domain index and does not locally validate before indexing. Domain attribute query errors during init are ignored in the loop, so malformed individual domains may leave default capability/name data while protocol init succeeds. Tests should cover domain count discovery, v3 extended names, state get/set return statuses, notification enable only on supported domains, invalid event payload sizes, unsupported notification command handling, and consumers avoiding out-of-range domain ids.
