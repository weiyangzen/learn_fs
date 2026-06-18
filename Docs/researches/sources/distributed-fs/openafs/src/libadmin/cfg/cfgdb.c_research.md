# sources/distributed-fs/openafs/src/libadmin/cfg/cfgdb.c

## Purpose
Implements the `cfg_CellServDb*` API for managing cell-wide server CellServDB membership. It can enumerate database hosts from a server's BOS CellServDB and can add/remove the host being configured across database/file servers using parallel detached worker threads.

## Important APIs, Types, And Functions
Exported functions are `cfg_CellServDbAddHost`, `cfg_CellServDbRemoveHost`, `cfg_CellServDbEnumerate`, and `cfg_CellServDbStatusDeallocate`. Local structures include `cfg_server_iteration_t`, `cfg_csdb_update_ctrl_t`, `cfg_csdb_update_name_t`, and `cfg_csdb_nameblock_iteration_t`. Key helpers are `CellServDbUpdate`, `StartUpdateWorkerThread`, `UpdateWorkerThread`, `CfgHostGetCellServDbAlias`, `NameBlockGetBegin/Next/Done`, and `ServerNameGetBegin/Next/Done`.

## Control Flow
`cfg_CellServDbEnumerate` opens a null cell handle, opens the specified BOS server, iterates its host list with `bos_HostGetBegin/Next/Done`, retrieves the BOS cell name, closes handles, and returns a heap-allocated multistring of database hosts plus a heap-allocated cell name.

`CellServDbUpdate` validates the host handle, callback, optional system-control host, and max-update output. It resolves the system-control host when present, allocates a shared control block, computes the configured host alias as it appears in existing server CellServDB entries, builds server-name blocks of up to `SERVER_NAME_BLOCK_SIZE`, starts one detached worker per block, then atomically releases all workers by changing the disposition from `CSDB_WAIT` to `CSDB_GO` or `CSDB_ABORT` and broadcasting a condition variable. Name enumeration uses database servers only when a system-control host is provided; otherwise it enumerates all AFS servers, then ensures the configuration host and optional system-control host are included.

Each `UpdateWorkerThread` waits for the shared disposition, opens each target BOS server, calls `bos_HostCreate` or `bos_HostDelete` with the alias from the control block, invokes the user callback with an allocated `cfg_cellServDbStatus_t`, and lets the last worker invoke the termination callback with `statusItemP == NULL`.

## State And Persistence
Persistent state modified by workers is the server CellServDB host list on each targeted BOS server. The operation is designed to appear atomic from the worker-start perspective: workers are created first and then released together. The user callback receives heap records that must be deallocated with `cfg_CellServDbStatusDeallocate`. The shared control block and name blocks are transient heap state used by detached threads.

## Dependencies And Integration Points
The file depends on pthreads, BOS admin APIs, client admin APIs for server enumeration, utility database-server enumeration, host utility functions from `cfginternal`, and OpenAFS bnode/cellconfig definitions. It is part of higher-level server setup where adding a new database server must propagate to existing server CellServDB files.

## Risks And Test Signals
The largest risk is threading cleanup: the last worker frees the shared control block before unlocking its mutex, producing a potential use-after-free. Mutexes and condition variables are also not destroyed. Detached workers mean the initiating function returns before updates complete, so callers must rely on callbacks and must not reenter the configuration library except for deallocation as documented. Other risks include callback allocation loops that sleep until memory is available, assuming all server CellServDB aliases are identical, duplicate target names, and treating `BZNOENT` as success for removals.

Test signals should cover zero/one/many target servers, callback ordering including final `NULL` callback, add/remove idempotence, system-control-host and no-system-control paths, alias discovery failures, worker abort after setup error, and thread sanitizer or asan coverage around last-worker cleanup.
