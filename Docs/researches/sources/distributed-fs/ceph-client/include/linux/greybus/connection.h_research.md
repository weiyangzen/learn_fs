<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/greybus/connection.h -->
# sources/distributed-fs/ceph-client/include/linux/greybus/connection.h

Purpose: This header defines Greybus CPort connections, which are the transport endpoints over which protocol operations are exchanged.

Important APIs/types/functions: Connection flags cover CSD/e2efc behavior, no flow control, offload, CDSI1, control, and high priority. `enum gb_connection_state` tracks disabled, TX-enabled, enabled, and disconnecting. `struct gb_connection` stores host/interface/bundle pointers, refcount, host/interface CPort IDs, link nodes, request handler, flags, mutex/spinlock, state, operation list, name, workqueue, operation cycle counter, private data, and mode-switch flag. Creation APIs support static, control, normal, flagged, and offloaded connections. Enable/disable, forced disable, RX disable, mode-switch prepare/complete, received-data dispatch, latency tag, and data get/set APIs are declared.

Control flow, state, and persistence: A driver creates a connection, enables TX or full RX/TX, sends operations, and disables/destroys it during disconnect. Incoming data is demultiplexed from host device and CPort into a connection, then into operations or request handlers. State is protected by mutex/spinlock and refcounting.

Dependencies/integration: It integrates host controller CPort operations, bundles/interfaces, workqueues, krefs, kfifo infrastructure, and `gb_operation`.

Risks and test signals: State transitions during mode switch and disconnect are race-prone. Flow-control flags must match SVC/APBridge setup. Tests should cover create/destroy variants, enable failure unwinding, incoming request dispatch, operation cancellation on disable, offloaded/control flags, latency tag enable/disable, and CPort ID mismatch.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/greybus/connection.h -->
