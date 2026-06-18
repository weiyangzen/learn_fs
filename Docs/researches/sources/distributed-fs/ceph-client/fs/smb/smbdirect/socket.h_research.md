## sources/distributed-fs/ceph-client/fs/smb/smbdirect/socket.h

Purpose: Defines the central SMBDirect socket state machine, in-memory transport structures, logging helpers, send/receive/MR/RW IO objects, initialization routine, status-check macros, and constants shared by the SMBDirect implementation.

Important APIs and types: `enum smbdirect_socket_status` covers created, listening, active connect phases, negotiate, connected, error, disconnecting, disconnected, and destroyed. `smbdirect_socket_status_string()` maps status to diagnostics. `struct smbdirect_socket` contains status/error, workqueues, krefs, RDMA CM and IB resources, negotiated parameters, connect/listen/accept state, send/receive credit and buffer state, MR and RW credit state, statistics, and logging callbacks. It also defines `struct smbdirect_send_io`, `struct smbdirect_send_batch`, `struct smbdirect_recv_io`, `struct smbdirect_mr_io`, `struct smbdirect_rw_io`, MR state enum, logging macros, `smbdirect_socket_init()`, status-check macros, page-count helper, and RDMA CM retry constants.

Control flow: The inline `smbdirect_socket_init()` establishes initial state for every socket: zeroes memory, initializes wait queues/locks/lists, copies global workqueues, disables work items until real handlers are installed, initializes krefs, marks RDMA expected event internal, sets default poll context and GFP masks, initializes credit counters and logging stubs. Status-check macros centralize warnings and optional disconnect scheduling when code observes an unexpected state.

State and persistence: This header defines all volatile socket state but does not persist anything. The state machine is enforced cooperatively by accept/connect/listen/connection/socket code. Atomic counters and wait queues represent flow-control state; spinlocks protect lists; krefs protect lifetime; work items drive async progress.

Dependencies and integration points: Includes wait queues, workqueues, krefs, mempool, spinlock, mutex, completion, and `rdma/rw.h`. It is included through `internal.h` by all SMBDirect implementation files and aligns with public `linux/smbdirect.h` types embedded in parameters and descriptors.

Risks and edge cases: Because `struct smbdirect_socket` is large and shared across all files, field layout and locking rules are easy to violate. Disabled placeholder work functions intentionally warn if queued before initialization. Logging callbacks are mandatory for logging macros; default stubs warn if callers forget to install real logging but code logs anyway. Status ordering is used by cleanup force-status comparisons, so enum reordering has behavioral consequences.

Test signals: Compile coverage for all users, initialization assertions, logging callback installation, status string coverage for every enum, status-check macro behavior, refcounted release paths, and runtime tests that exercise all status transitions.
