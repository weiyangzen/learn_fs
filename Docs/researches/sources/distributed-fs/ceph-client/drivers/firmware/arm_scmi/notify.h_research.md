# sources/distributed-fs/ceph-client/drivers/firmware/arm_scmi/notify.h

Purpose: defines the private SCMI notification contract between protocol implementations, the notification core, and the main SCMI driver. It describes supported protocol events, protocol-specific notification callbacks, and the notification core entry points.

Important APIs/types/functions: `SCMI_PROTO_QUEUE_SZ` is the default per-protocol notification kfifo size. `struct scmi_event` defines an event id plus maximum raw payload and converted report sizes. `struct scmi_event_ops` provides protocol callbacks for source support checks, source count discovery, enable/disable commands, and custom report construction. `struct scmi_protocol_events` groups queue size, operations, event array, event count, and optional static source count. The function declarations cover notification init/exit, protocol event registration/deregistration, and ISR-side event queuing through `scmi_notify()`.

Control flow: protocol files populate static `scmi_event`, `scmi_event_ops`, and `scmi_protocol_events` tables and attach them to their `struct scmi_protocol`. During protocol instance initialization, `driver.c` passes these descriptors to `scmi_register_protocol_events()`. Client notifier registration and RX dispatch are implemented in `notify.c`, using the callback table defined here.

State and persistence behavior: this header owns no storage. It defines sizing and callback contracts for runtime state allocated by `notify.c`; those allocations are per SCMI platform instance and per initialized protocol.

Dependencies and integration points: includes Linux device, ktime, and type headers, and forward-declares `struct scmi_protocol_handle`. It is included by `driver.c`, `notify.c`, and protocol implementations such as power, performance, and powercap that publish events.

Risks and test signals: the correctness of notification handling depends on accurate `max_payld_sz`, `max_report_sz`, and source counts from each protocol. Tests should verify that each event table matches the corresponding SCMI payload/report structs and that protocols with dynamic source counts provide a reliable `get_num_sources()` callback before notifier registration is used.
