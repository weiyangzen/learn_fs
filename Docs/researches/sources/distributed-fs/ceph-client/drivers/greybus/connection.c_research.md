# sources/distributed-fs/ceph-client/drivers/greybus/connection.c

Purpose: core Greybus connection lifecycle and state machine. A connection represents a bidirectional link between a host CPort and a remote interface CPort and owns active operation state.

Important APIs and functions: creation APIs cover static, control, normal, flagged, and offloaded connections. Runtime APIs include `gb_connection_enable`, `enable_tx`, `disable_rx`, `disable`, `disable_forced`, `destroy`, latency-tag enable/disable, and mode-switch prepare/complete. `greybus_data_rcvd()` dispatches host-driver received data to the matching connection.

Control flow: creation serializes against destroy, checks remote CPort reuse, allocates a host CPort, initializes locks/workqueue/kref, and links the connection into host and bundle lists. Enable performs host CPort enable, SVC route creation, host connected notification, state transition to TX or full RX/TX, then control connected notification. Disable transitions to disconnecting, cancels operations, flushes host CPort, sends control disconnecting, performs two-phase CPort shutdown with quiesce between phases, sends disconnected/mode-switch handling, destroys SVC route, clears and disables the host CPort.

State and persistence: connection state includes IDs, flags, mode-switch flag, operation cycle, operation list, ordered workqueue, kref, and state enum. Global host connection lookup is protected by `gb_connections_lock`; lifecycle serialization uses `gb_connection_mutex` and per-connection mutex/spinlock.

Dependencies and integration: depends on host-device CPort driver callbacks, SVC connection management, Greybus control operations, operation core, bundles, interfaces, workqueues, and tracepoints.

Risks: state transitions and lock ordering are complex. Forced disable skips remote communication for disconnected interfaces. Error unwind in enable must mirror teardown. Offloaded connections depend on host driver shutdown support.

Test signals: Greybus device enumeration, connect/disconnect traces, operation cancellation behavior, CPort shutdown/quiesce logs, mode-switch paths, and host-driver callback failures.
