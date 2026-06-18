# sources/distributed-fs/openafs/src/libadmin/bos/afs_bosAdmin.c

## Purpose
Implements the public BOS admin API declared in `afs_bosAdmin.h`. It opens authenticated Rx connections to a BOS server, validates BOS handles, wraps bozo RPCs for process/admin/key/cell/host/executable/log/auth/command operations, uses the shared libadmin iterator framework for BOS enumerations, and orchestrates remote salvage operations.

## Important APIs, Types, And Functions
`bos_server_t` is the private handle with magic fields and three Rx connections: normal BOS service, encrypted BOS service, and stats service. Public lifecycle functions are `bos_ServerOpen` and `bos_ServerClose`; validation is done by `isValidServerHandle` and the local `IsValidCellHandle`. Major API groups include process creation/deletion/state/info/parameters/notifier/restart/all-stop/all-start, admin create/delete/list, key create/delete/list, cell get/set, host create/delete/list, executable install/revert/timestamps/prune/restart-time get/set, log retrieval, noauth setting, remote command execution, and `bos_Salvage`.

Iterators use local structs such as `process_name_get_t`, `param_get_t`, `admin_get_t`, `key_get_t`, and `host_get_t`, each plugged into `IteratorInit`. Secret-key operations use `server_encrypt` and the `kas_to_bozoptr` adapter from the header.

## Control Flow
`bos_ServerOpen` validates that the cell handle has tokens, resolves `serverName` through `util_AdminServerAddressGetFromName`, and creates cached Rx connections to `AFSCONF_NANNYPORT`. Most simple wrappers validate the handle and arguments, call one `BOZO_*` RPC, and return `1` only when the RPC status is zero. Process and host/admin/key enumeration functions allocate iterator-specific state, call a `BOZO_*` enumerate/list RPC by increasing index, translate `BZDOM` or similar end conditions into `ADMITERATORDONE`, and copy cached results into caller buffers.

Executable installation uses a split Rx RPC: it opens a local file, stats it, starts `BOZO_Install`, streams the file in 512-byte chunks with `rx_Write`, and ends the call. Log retrieval starts `BOZO_GetLog`, reads one byte at a time until a NUL terminator, stores up to the caller's buffer size, and reports `ADMMOREDATA` when the caller buffer is too small. Restart-time functions map libadmin restart enums to bozo restart types and `bozo_netKTime`.

`bos_Salvage` validates cell and BOS handles, optionally resolves partition names, opens a local salvage-log output file, temporarily stops the `fs` bnode for non-volume-specific salvages, constructs a salvager command line, creates a temporary cron bnode named `salvage-tmp` with time `now`, polls until the bnode disappears, optionally retrieves the server SalvageLog, and restarts the fileserver if it had been stopped.

## State And Persistence
The private BOS handle owns cached Rx connections and validity markers. Remote persistent state affected by this file includes BosConfig bnodes, process goals, `UserList`, `KeyFile`, server `ThisCell`/CellServDB host list, executable files and `.BAK`/`.OLD` rotations, restart schedules, noauth flag, command execution effects, and salvage results. Local persistent side effects include reading source executable files and writing optional salvage logs. Iterators keep transient heap caches and background worker threads through the shared iterator framework.

## Dependencies And Integration Points
The file depends on Rx, RxStat, bozo RPC stubs from `bosint`, bnode constants, `ktime`, directory-path constants, `afs_utilAdmin`, `afs_AdminInternal`, KAS key types, and VOS partition conversion for salvage. It is used by configuration code in `cfgdb.c` and `cfghost.c` to update CellServDB, UserList, KeyFile, BOS process state, and salvage operations.

## Risks And Test Signals
Several cleanup and correctness risks are visible. `bos_ServerClose` releases only `server`, not `server_encrypt` or `server_stats`, so opened handles can leak cached connections. `bos_ExecutableCreate` does not close the opened local file descriptor on success or failure. `bos_LogGet` can overwrite an earlier `ADMMOREDATA` or read error with the status from `rx_EndCall`, hiding the real reason for failure. `bos_Salvage` builds a command with repeated `sprintf` into a fixed `BOS_MAX_NAME_LEN` buffer and checks length after writes, so long options can overflow before detection. Iterator copies use `strcpy` into caller buffers that are assumed to be `BOS_MAX_NAME_LEN`.

Test signals should cover BOS open/close connection accounting, process create/delete/state transitions, all iterator end conditions, encrypted key create/list/delete, executable upload and revert against a test bosserver, log retrieval with exact/small/large buffers, noauth toggling, restart-time validation, and salvage command construction with long partition/volume/tmp paths.
