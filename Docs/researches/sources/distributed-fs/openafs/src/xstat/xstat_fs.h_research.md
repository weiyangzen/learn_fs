# sources/distributed-fs/openafs/src/xstat/xstat_fs.h

## Purpose
`xstat_fs.h` is the public interface for the OpenAFS File Server xstat client. It defines initialization flags, connection/result data structures, exported module state, and the functions needed to initialize polling, force an immediate collection, wait for collection activity, decode full-performance statistics, and clean up.

## Important APIs, Types, And Functions
The key flags are `XSTAT_FS_INITFLAG_DEBUGGING` and `XSTAT_FS_INITFLAG_ONE_SHOT`. `struct xstat_fs_ConnectionInfo` stores the server socket, Rx connection, and computed host name. `struct xstat_fs_ProbeResults` stores probe number/time, current connection, collection ID, `AFS_CollData`, and probe status. Public functions are `xstat_fs_Init`, `xstat_fs_ForceProbeNow`, `xstat_fs_Cleanup`, `xstat_fs_Wait`, and `xstat_fs_DecodeFullPerfStats`.

## Control Flow
Consumers call `xstat_fs_Init` once with file-server socket addresses, polling frequency, handler, flags, and collection IDs. The handler reads `xstat_fs_Results` after each probe. Long-running callers use `xstat_fs_Wait` or `xstat_fs_ForceProbeNow`, then eventually call `xstat_fs_Cleanup`.

## State And Persistence
The header declares process-global state owned by `xstat_fs.c`: server count, connection array, and latest probe results. There is no durable persistence, but the exported variables make the module stateful and non-reentrant.

## Dependencies And Integration Points
It includes platform networking headers, Rx, `afs/afsint.h`, and `afs/fs_stats.h`, and sets `FSINT_COMMON_XG` to allow coexistence with the Cache Manager xstat header. It is consumed by tests and any xstat file-server monitoring tool.

## Risks And Test Signals
Because consumers access mutable globals directly, ABI and struct-layout stability matter. Compile coverage with both Unix and Windows networking environments, plus runtime collection tests that verify handlers see valid `connP`, `collectionNumber`, and `data` fields, are the main signals.
