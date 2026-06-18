# sources/distributed-fs/ceph-client/drivers/firmware/arm_scmi/base.c

## Purpose
Implements the SCMI Base protocol. It discovers firmware identity, implementation version, number of protocols/agents, implemented protocol IDs, agent names, and Base error notifications.

## APIs, Types, And Functions
Defines Base protocol command IDs and response payload structures. Important functions include `scmi_base_attributes_get()`, `scmi_base_vendor_id_get()`, `scmi_base_implementation_version_get()`, `scmi_base_implementation_list_get()`, `scmi_base_discover_agent_get()`, and notification helpers for `BASE_NOTIFY_ERRORS`. The protocol registers through `DEFINE_SCMI_PROTOCOL_REGISTER_UNREGISTER(base, scmi_base)`.

## Control Flow
Protocol init obtains the shared revision area, stores version fields, reads attributes, allocates the implemented-protocol list, retrieves vendor/subvendor/implementation data, enumerates implemented protocols in batches, publishes them to SCMI core, logs firmware identity, and optionally logs agent names. Error notifications can be enabled or disabled through SCMI notification ops; incoming payloads are converted into `struct scmi_base_error_report`.

## State, Persistence, And Dependencies
Runtime state is written into SCMI core revision/protocol implementation areas and devm-managed protocol data. No disk persistence exists. Dependencies include SCMI transfer ops, protocol handle ops, notifications, and endian/unaligned helpers.

## Integration Points
The Base protocol underpins SCMI core enumeration, allowing later protocol clients to know which protocols are implemented. Its event descriptor integrates with the common SCMI notifier framework.

## Risks And Test Signals
Risks include malformed protocol-list replies, truncated RX payloads, overreported protocol counts, and very large Base error command counts. The code has explicit protocol-size validation and warning paths. Test signals are SCMI boot logs showing firmware version/protocol counts, protocol availability to clients, and Base error notification injection.
