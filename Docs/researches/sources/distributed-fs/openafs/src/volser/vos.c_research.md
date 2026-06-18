# sources/distributed-fs/openafs/src/volser/vos.c

## Purpose

`vos.c` implements the OpenAFS `vos` administrative command-line client for volume-server and VLDB operations. It registers subcommands with the OpenAFS command parser, initializes Rx/Ubik security and VLDB client state before command execution, and dispatches each operation to higher-level volume utility routines (`UV_*`) or direct VLDB ubik RPC stubs (`ubik_VL_*`). The file is the user-facing orchestration layer for creating, deleting, moving, copying, cloning, backing up, releasing, dumping, restoring, listing, synchronizing, locking, and repairing volume metadata and volume-server state.

The implementation is intentionally broad: it does argument parsing and validation, maps names to volume IDs and server addresses, checks partition validity, chooses the correct RW/RO/BK site from VLDB entries, streams dump data over Rx calls, formats human and machine-readable output, and reports operational errors.

## Important APIs, Types, and Functions

- Command and initialization surface: `main`, `cmd_CreateSyntax`, `cmd_AddParm`, `COMMONPARMS`, `cmd_SetBeforeProc(MyBeforeProc)`, and `cmd_Dispatch` define the `vos` command set and common options (`-cell`, `-noauth`, `-localauth`, `-verbose`, `-encrypt`, `-noresolve`, `-config`, `-rxgk`).
- Security/client setup: `MyBeforeProc` builds `AFSCONF_SECOPTS_*` flags, chooses client or server config directories, calls `vsu_ClientInit(..., UV_SetSecurity, &cstruct)`, sets globals `rxInitDone`, `verbose`, and `noresolve`, and leaves teardown to `main` via `ubik_ClientDestroy` and `rx_Finalize`.
- Address and partition helpers: `GetServerNoresolve`, `GetServer`, `IsPartValid`, `volutil_GetPartitionID`, `MapPartIdIntoName`, and `hostutil_GetNameByINet` translate CLI input into AFS network identifiers and validate volserver partitions with `UV_ListPartitions`.
- Volume/VLDB lookup helpers: `vsu_GetVolumeID`, `GetVolumeInfo`, `GetServerAndPart`, `VLDB_GetEntryByID`, `VLDB_GetEntryByName`, `VLDB_ListAttributes`, `VLDB_ListAttributesN2`, `MapHostToNetwork`, `Lp_GetRwIndex`, `Lp_AnyMatch`, and `VLDB_IsSameAddrs` bridge user volume names/IDs to concrete RW/RO/BK sites.
- Output helpers: `DisplayFormat`, `XDisplayFormat`, `DisplayFormat2`, `XDisplayFormat2`, `DisplayVolumes`, `XDisplayVolumes`, `EnumerateEntry`, `SubEnumerateEntry`, `PrintLocked`, and comparators for `qsort` produce standard, long, fast, extended, and machine-readable listings.
- Dump/restore streaming: `CheckDumpFile`, `SendFile`, `ReceiveFile`, and `DumpFunction` use `usd_*` file handles and `rx_Read`/`rx_Write` callbacks for `UV_DumpVolume`, `UV_DumpClonedVolume`, and `UV_RestoreVolume2`.
- Command handlers: key handlers include `CreateVolume`, `DeleteVolume`, `MoveVolume`, `CopyVolume`, `ShadowVolume`, `CloneVolume`, `BackupVolume`, `ReleaseVolume`, `DumpVolumeCmd`, `RestoreVolumeCmd`, `AddSite`, `RemoveSite`, `ChangeLocation`, `ListVolumes`, `ListVLDB`, `BackSys`, `DeleteEntry`, `PartitionInfo`, `ChangeAddr`, `ListAddrs`, `SetAddrs`, `RemoveAddrs`, `ConvertRO`, `Sizes`, and `EndTrans`.

## Control Flow

Process startup registers every `vos` subcommand, attaches common options, and dispatches through the command package. `MyBeforeProc` runs before command handlers, initializes Rx/Ubik/VLDB access, and configures authentication, encryption, rxgk security level, config directory, verbosity, and address-resolution behavior. After dispatch, `main` destroys the Ubik client and finalizes Rx if initialization occurred.

Most volume-mutating commands follow the same pattern: resolve a volume ID, resolve/validate server and partition input or infer it from the VLDB, reject invalid volume names or ambiguous RO locations, then call a `UV_*` operation. Examples include `UV_CreateVolume3`, `UV_DeleteVolume`, `UV_MoveVolume2`, `UV_CopyVolume2`, `UV_CloneVolume`, `UV_BackupVolume`, `UV_ReleaseVolume`, `UV_SetVolumeInfo`, and `UV_SetVolume`. The CLI mostly returns the library error code, but several legacy paths call `exit(1)` directly inside handlers.

Listing and inspection commands either query the volume server directly (`UV_ListVolumes`, `UV_XListVolumes`, `UV_ListOneVolume`, `UV_XListOneVolume`) or enumerate VLDB entries (`VLDB_ListAttributes*`). Results are optionally sorted, rendered in human or machine-readable formats, and summarized. Busy or unattached volumes are queued in the local `tqHead` lists so problem messages can be printed after the main listing.

Dump and restore have a streaming callback flow. Dumps resolve the target site, optionally parse an incremental date, refuse stdout when it is a tty, extend Rx dead times, and call `UV_DumpVolume` or `UV_DumpClonedVolume` with `DumpFunction`. Restore opens a file or stdin, validates dump magic with `CheckDumpFile`, decides full vs incremental behavior from VLDB state and `-overwrite`, sets timestamp and state flags, and passes `SendFile` to `UV_RestoreVolume2`.

VLDB repair and address commands operate closer to the VLDB RPC layer. `delentry`, `lock`, `unlockvldb`, `changeaddr`, `setaddrs`, `remaddrs`, and `listaddrs` call direct `ubik_VL_*` procedures and manage XDR-allocated arrays with `xdr_free`.

## State and Persistence Behavior

Persistent effects occur outside this process in AFS volume servers and the VLDB. Volume server state changes include on-disk volume creation/deletion, movement/copy/shadowing, backup and clone creation, online/offline flags, zapping volumes outside normal VLDB coordination, active transaction ending, and dump/restore writes. VLDB state changes include volume entries, sites, locks, locations, server address registrations, and synchronization repairs.

Local process state is limited but important. `cstruct` is the global Ubik VLDB client; `rxInitDone`, `verbose`, and `noresolve` gate teardown and behavior; `busyHead` and `notokHead` are temporary global queues used by listing output; `DisplayFormat2` and `XDisplayFormat2` cache the last server/partition formatting data in static variables. Dump/restore file handles are transient `usd_handle_t` objects and must be closed after streaming.

The file contains no durable local configuration writes. It reads AFS config and credentials through `vsu_ClientInit`, writes dump output files when requested, and consumes dump input files during restore.

## Dependencies and Integration Points

This source depends on OpenAFS Rx, XDR, Ubik, VLDB, volser, volume, partition, command-parser, authentication/configuration, and utility layers. Key includes are `rx/rx.h`, `ubik.h`, `afs/vlserver.h`, `afs/cellconfig.h`, `afs/cmd.h`, `afs/usd.h`, `volser.h`, `volint.h`, `dump.h`, and local `*_prototypes.h` headers.

The `UV_*` routines abstract most multi-step volser/VLDB workflows, while direct `AFSVol*` and `ubik_VL_*` calls are used for specialized operations such as ending transactions and server-address/VLDB-lock maintenance. Hostname resolution integrates with libc `gethostbyname`/`gethostname` and OpenAFS host utilities; partition handling integrates with volutil naming conventions. Optional POSIX regex support controls `backupsys` prefix filtering. Windows and AIX have platform-specific branches for registry-based crypto defaults and full-core signal behavior.

## Risks and Edge Cases

- Many handlers call `exit(1)` instead of returning errors. That makes cleanup and caller-level error handling inconsistent and can bypass common post-command paths except process teardown.
- Several operational commands perform preflight free-space checks using current `UV_PartitionInfo64` and `UV_ListOneVolume` data, but the comments acknowledge success is not guaranteed; space can change before the actual move/copy/shadow RPC.
- `GetServer` rejects loopback addresses and falls back from a loopback-resolving name to the local hostname, which is useful for server identity but can surprise tests or deployments with unusual DNS.
- Restore has complex overwrite semantics and can prompt interactively unless `-overwrite` is provided; it aborts when stdin is not a tty and the existing-volume policy is ambiguous.
- `zap` and `nuke` intentionally bypass normal VLDB coordination and can leave divergent VLDB/on-disk state if used incorrectly.
- Machine-readable formats are handcrafted with `fprintf`; consumers may depend on exact labels, spelling, and ordering, including historical typos.
- Regex patterns in `backupsys` are recompiled repeatedly inside loops despite a comment noting this should be optimized.
- Address-changing logic protects multi-homed server entries unless `-force` is used, but the legacy `changeaddr -remove` path uses a sentinel `0xffffffff` protocol convention and compatibility checks.

## Test Signals

Useful validation should include command-parser smoke tests for every registered syntax and common option, especially `-rxgk`, `-config`, `-noresolve`, and aliases like `volinfo`, `e`, and `release -f`. Mocked or integration-style volser/VLDB tests should verify RW/RO/BK site resolution, partition validation failures, VLDB fallback behavior for old servers (`RXGEN_OPCODE`), and cleanup of XDR-allocated lists.

Behavioral tests should cover dump/restore streaming on seekable files, stdin/stdout tty refusal, invalid dump begin/end magic, incremental date parsing, `-overwrite` modes, `-omitdirs` fallback, and dead-time configuration. Listing tests should assert sorted vs unsorted output, fast/long/extended/machine-readable formats, busy/unattached volume summaries, and `-quiet` behavior. Mutation tests should exercise name validation, numeric-name rejection, explicit volume IDs, free-space preflight failures, dry-run/noexecute modes, VLDB lock/unlock paths, multi-homed address refusal, and force flags for dangerous repair operations.
