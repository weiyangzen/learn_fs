# sources/distributed-fs/beegfs/client_module/source/common/net/sock/ibv/No_IBVSocket.c

Purpose: Provides non-RDMA stub implementations of the `IBVSocket` API when `BEEGFS_RDMA` is not enabled.

Important APIs/types/functions: All public `IBVSocket_*` functions are present; most log `no_ibvsocket_err()` and return failure values, while setters are no-ops, `rdmaDevicesExist` returns false, and `getDevice`/`getNicStats` return NULL.

Control flow: Any accidental use of RDMA operations in a non-RDMA build fails fast by return code and informational logging rather than linking missing symbols.

State and persistence behavior: No RDMA state is allocated or persisted.

Dependencies and integration points: Lets `RDMASocket` and NIC discovery compile while reporting no RDMA devices.

Risks: Return conventions vary by method (`false`, `-1`, `~0`, NULL), so callers must use the appropriate failure check. Unexpected log messages indicate a caller reached a path that should have been gated by RDMA availability.

Test signals: Non-RDMA build tests should confirm discovery reports no RDMA, RDMA socket init/connect fail cleanly, and standard TCP paths continue to work.
