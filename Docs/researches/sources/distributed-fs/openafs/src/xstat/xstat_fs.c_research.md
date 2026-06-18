# sources/distributed-fs/openafs/src/xstat/xstat_fs.c

## Purpose
`xstat_fs.c` implements the client side of OpenAFS File Server extended statistics. It initializes Rx client connections to one or more file servers, starts a callback listener so file servers can treat the collector like a minimal Cache Manager, runs a probe thread that periodically calls `RXAFS_GetXStats`, exports the latest result through global state, and provides helpers for waiting, forced probes, cleanup, and cross-platform full-performance-stat decoding.

## Important APIs, Types, And Functions
Exported state includes `xstat_fs_numServers`, `xstat_fs_ConnInfo`, `xstat_fs_Results`, and the backing `xstat_fsData` collection buffer. Exported functions are `xstat_fs_Init`, `xstat_fs_Cleanup`, `xstat_fs_ForceProbeNow`, `xstat_fs_DecodeFullPerfStats`, and `xstat_fs_Wait`. Private functions are `xstat_fs_CleanupInit` and the probe-thread body `xstat_fs_LWP`. The implementation uses `struct xstat_fs_ConnectionInfo`, `struct xstat_fs_ProbeResults`, Rx security/service APIs, `RXAFS_GetXStats`, the AFSCB callback dispatcher, pthreads, and OpenAFS `opr_mutex_t`/`opr_cv_t`.

## Control Flow
`xstat_fs_Init` validates arguments, records flags and collection IDs, initializes the force-probe condition variable, verifies callback stubs through `xstat_fs_CleanupInit`, allocates connection records, initializes Rx, creates null Rx client/server security objects, resolves host names, creates Rx connections to AFS service 1 on the supplied file-server sockets, starts an AFSCB callback service, starts the Rx server, and creates `xstat_fs_LWP`. The probe thread increments the probe number, iterates each server and each requested collection ID, zeroes the shared collection buffer, calls `RXAFS_GetXStats`, and invokes the caller-provided handler after each server/collection result. It exits after one pass in one-shot mode or sleeps until the next frequency timeout, with `xstat_fs_ForceProbeNow` waking the condition variable early.

## State And Persistence
The module is intentionally global and single-instance. It persists in memory the connection array, copied collection ID array, latest result metadata, shared data buffer, debug/one-shot flags, callback service, Rx connections, thread handle, and synchronization primitives. It writes no disk state. `xstat_fs_Cleanup` destroys Rx connections and optionally frees the connection array, but the copied collection ID array is not freed in the visible cleanup path.

## Dependencies And Integration Points
The module depends on OpenAFS Rx, the AFS file-server RPC interface, callback RPC stubs from `xstat_fs_callback.c`, `afs/fs_stats.h`, pthreads, and host utilities. Consumers link to this module through `xstat_fs.h` and provide a no-argument handler that reads `xstat_fs_Results`.

## Risks And Test Signals
Risks include unsynchronized access to global result buffers between the probe thread and handler consumers, partial cleanup after failed initialization, allocation of collection IDs before `xstat_fs_CleanupInit`, fixed `AFS_MAX_XSTAT_LONGS` buffering, and compatibility complexity in `xstat_fs_DecodeFullPerfStats` for 32-bit versus 64-bit `timeval` and remote word order. Tests should cover invalid init arguments, unreachable servers returning `-2`, one-shot thread join, forced probe wakeups, handler error logging, cleanup after partial setup, and decoding of small and large full-performance-stat payloads from opposite-endian hosts.
