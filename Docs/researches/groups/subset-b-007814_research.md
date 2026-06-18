# subset-b-007814 Research

This grouped report covers the OpenAFS fileserver `viced` state/I/O sources and the `vlserver` build, conversion, opcode, and interactive client sources listed for subset B. Each section is delimited for reconciliation into the source-tree-aligned per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/viced/physio.c -->
# sources/distributed-fs/openafs/src/viced/physio.c

## Purpose

`physio.c` supplies the low-level physical page I/O hooks used by the directory buffer package in the fileserver. It translates a `DirHandle` into an `IHandle_t` file descriptor, reads or writes fixed 2048-byte directory pages, and maintains helper routines for copying, clearing, releasing, and comparing directory handles.

## Important APIs, Types, And Functions

- `ReallyRead(DirHandle *file, int block, char *data, int *physerr)` opens `file->dirh_handle`, performs `FDH_PREAD` of `PAGESIZE` bytes at `block * PAGESIZE`, returns `0` on success or `EIO` on short/failed read, and distinguishes logical short reads from physical errno via optional `physerr`.
- `ReallyWrite(DirHandle *file, int block, char *data)` opens the handle and writes one page with `FDH_PWRITE`; it logs errors and stores failure evidence in globals `lpErrno` and `lpCount`.
- `SetDirHandle(DirHandle *dir, Vnode *vnode)` copies vnode identity, volume cache generation, and ihandle into a buffer-package-compatible `DirHandle`.
- `FidZap`, `FidZero`, `FidEq`, `FidVolEq`, and `FidCpy` manage `DirHandle` lifetime and identity comparison.
- `PAGESIZE` is forced to `2048`, matching the directory page size expected by this layer rather than the platform VM page size.

## Control Flow

The read/write path is intentionally narrow: open the inode handle, perform a positional full-page read or write, close or really-close the fd handle, and log on failure with device, inode, volume id, and errno context. `ReallyRead` has clearer error propagation than `ReallyWrite`: it returns `EIO` for both physical and short-read errors and can return physical errno through `physerr`. `ReallyWrite` always returns `0`, including failure cases, so callers must rely on historical global side effects if they need details.

Handle helpers are simple state transitions. `SetDirHandle` increments/copies the vnode ihandle reference with `IH_COPY`; `FidZap` releases the stored handle and clears the structure; `FidCpy` copies the structure and then takes another ihandle reference.

## State And Persistence Behavior

This file performs persistent directory object I/O through OpenAFS inode-handle abstractions. It does not own higher-level transaction state. The durable data unit is a 2048-byte directory page at a deterministic file offset. `DirHandle` includes copied device, inode, volume id, vnode id, uniquifier, and `cacheCheck` fields so cached directory pages can be invalidated when a vnode/volume identity changes even if the underlying handle object is reused.

## Dependencies And Integration Points

It depends on `afs/ihandle.h`, vnode/volume definitions, `viced.h` for `DirHandle`, and `viced_prototypes.h`. It is an integration layer between the directory buffer package and the fileserver's inode-handle package. Logging goes through `ViceLog`, and inode formatting uses `PrintInode`/`afs_printable_VolumeId_lu`.

## Risks And Edge Cases

- `ReallyWrite` returns success even when open or write fails; this is a legacy API trap and makes callers easy to misread.
- Short reads are converted to logical `EIO` with `physerr = 0`, so diagnostics must preserve both `code` and `physerr`.
- `FidZap` assumes `dirh_handle` is valid enough for `IH_RELEASE`; callers should not double-zap a copied/zeroed handle.
- The fixed 2048-byte page size must stay consistent with the directory package.

## Test Signals

Useful tests are fault-injection around `IH_OPEN`, short `FDH_PREAD`, short/failed `FDH_PWRITE`, and reference-count/lifetime checks for `SetDirHandle`, `FidCpy`, and `FidZap`. Integration tests should verify directory cache invalidation when vnode uniquifier or volume `cacheCheck` changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/viced/physio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/viced/serialize_state.c -->
# sources/distributed-fs/openafs/src/viced/serialize_state.c

## Purpose

`serialize_state.c` implements demand-attach fileserver state dump and restore for host and callback state. It creates, invalidates, loads, commits, reads, writes, maps, syncs, and verifies the state dump file at `AFSDIR_SERVER_FSSTATE_FILEPATH`. The implementation is compiled only under `AFS_DEMAND_ATTACH_FS`.

## Important APIs, Types, And Functions

- Public entry points `fs_stateSave()` and `fs_stateRestore()` orchestrate full save/restore under `H_LOCK`.
- Public I/O helpers `fs_stateWrite`, `fs_stateRead`, `fs_stateWriteV`, `fs_stateReadV`, `fs_stateWriteHeader`, `fs_stateReadHeader`, `fs_stateIncEOF`, `fs_stateSeek`, `fs_stateSync`, and `fs_stateFileOpen` are used by host/callback serialization code.
- Internal lifecycle helpers `fs_stateCreateDump`, `fs_stateLoadDump`, `fs_stateInvalidateDump`, `fs_stateCommitDump`, and `fs_stateCloseDump` manage dump-file validity.
- Mmap helpers `fs_stateSizeFile`, `fs_stateResizeFile`, `fs_stateTruncateFile`, `fs_stateMapFile`, `fs_stateUnmapFile`, `fs_stateIncCursor`, and `fs_stateCheckIOSafety` provide fast sequential I/O on non-Windows platforms.
- Header helpers `fs_stateFillHeader` and `fs_stateCheckHeader` encode/check magic, format version, sysname, endianness, stats mode, timestamp, server UUID, and version string.

## Control Flow

Save flow: take `H_LOCK`, allocate `fs_dump_state`, optionally run `h_stateVerify` and `cb_stateVerify`, create a new dump after renaming any existing file to `.old`, write an invalid header, serialize host state, serialize callback state, and commit by truncating/syncing data before writing a valid header. If pre-save verification failed, `state.bail` keeps the final header invalid even though the dump file was written.

Restore flow: take `H_LOCK`, allocate state, open and mmap the dump, read/check the main header, immediately invalidate the dump so it cannot be replayed after a failed restore, skip host/callback restore if the dump timestamp is older than `HOST_STATE_VALID_WINDOW`, otherwise restore host and callback tables and remap their indices, optionally verify both tables, log elapsed milliseconds and restored FE/CB counts, then invalidate and close the file on exit.

## State And Persistence Behavior

The file persists process-local host and callback structures so DAFS can restart without forcing all clients through full callback reinitialization. The validity protocol is two-phase: header `valid = 0` while a dump is in progress or consumed, and `valid = 1` only after all data has been synced and the final header is rewritten. The header is tied to this server by `FS_HostUUID`, endianness, `FS_STATE_MAGIC`, `FS_STATE_VERSION`, and detailed-statistics mode. Old dumps can be loaded only for limited host/callback restore; older than 30 minutes means restore continues with host restore disabled.

## Dependencies And Integration Points

This file sits between `viced.c` shutdown/startup and the `host.c`/`callback.c` serializers declared in `serialize_state.h`. It depends on global `fs_state.options`, `FS_HostUUID`, `cml_version_number`, `H_LOCK`, `ViceLog`, OpenAFS integer macros, and platform file/mmap APIs. `viced.c` invokes `fs_stateRestore()` before Rx request service starts and invokes `fs_stateSave()` after shutdown quiesces background host/callback threads.

## Risks And Edge Cases

- Restore exits the process on host/callback corruption paths, preventing a partially corrupted in-memory server from continuing.
- `msync` return value is ignored in the mmap `fs_stateSync` implementation, so sync failures may be invisible.
- Mmap `fs_stateSeek` does not bounds-check the target offset; callers must validate offsets.
- Header version mismatch is fatal, but component version-string mismatch is warning-only.
- Host/callback restore is skipped when the dump is too old; tests must distinguish "restore succeeded without host restore" from full restore.

## Test Signals

Strong signals include save/restore round trips, invalid-header rejection, wrong UUID/endian/version rejection, old timestamp skip behavior, pre-save verification failure producing an invalid dump, forced mmap resize while writing large callback tables, and recovery behavior after a crash between data sync and valid-header rewrite.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/viced/serialize_state.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/viced/serialize_state.h -->
# sources/distributed-fs/openafs/src/viced/serialize_state.h

## Purpose

`serialize_state.h` defines the on-disk and runtime contracts for demand-attach fileserver state serialization. It is the schema used by `serialize_state.c`, the host package, the callback package, and `state_analyzer.c`.

## Important APIs, Types, And Functions

- Magic/version constants define independent format stamps for the main fs state, host state, callback state, callback timeout/hash blocks, callback entries, active-volume state, and active-volume hash blocks.
- `struct fs_state_header` is the main 1024-byte header carrying timestamp, sysname, server UUID, validity, endianness, detailed-statistics flag, offsets for active volumes, host, callback, and VLRU state, plus a version string.
- Host schema: `host_state_header`, `host_state_entry_header`, and `hostDiskEntry` encode host records, interfaces, CPS data lengths, callback list index, and activity timestamps.
- Callback schema: `callback_state_header`, timeout/FE-hash headers, `callback_state_entry_header`, `FEDiskEntry`, and `CBDiskEntry` encode FileEntry and CallBack arrays plus index values for remapping.
- Active volume schema: `active_volume_state_header`, `active_volume_state_avehash_header`, `active_volume_state_avehash_entry`, and `AVDiskEntry` reserve layout for active-volume salvage support.
- `struct idx_map_entry_t` and `struct fs_dump_state` describe runtime restore maps and file/mmap cursors.
- Prototypes expose fs-state I/O helpers and host/callback save/restore/verify/index-remap hooks.

## Control Flow

This header does not implement control flow, but it dictates the flow order: write/read the main header, then use offsets to locate host and callback subheaders, then process variable-length host entries and callback FE/CB entries while building old-to-new index maps. Restore uses `h_OldToNew`, `fe_OldToNew`, and `cb_OldToNew` mappings to reconnect references serialized from the old process.

## State And Persistence Behavior

The header is explicitly an on-disk ABI. Structures include reserved expansion fields and fixed-size headers, so changing sizes, field order, magic, or version values affects dump compatibility. The `valid` bit is the primary persistence cursor. The index-map valid states distinguish populated entries from skipped entries, allowing restore to tolerate records that were omitted during save due to inconsistent/busy runtime state.

## Dependencies And Integration Points

The schema references fileserver host/callback structures such as `struct host`, `struct FileEntry`, and `struct CallBack`, and OpenAFS primitive types such as `afs_uint32`, `afs_uint64`, `afsUUID`, `VolumeId`, and `byte`. It is included by `serialize_state.c` and `state_analyzer.c`, and its host/callback prototypes are implemented outside this file.

## Risks And Edge Cases

- The disk structures embed native C types such as `time_t`; portability is guarded mostly by endianness/version checks, not by a canonical XDR format.
- `FS_STATE_H_MAX_LIST_LEN` is intentionally huge, so sanity checks elsewhere must still prevent memory exhaustion from corrupt record counts.
- Active-volume offsets exist in `fs_state_header`, but the current serializer file in this subset only drives host/callback state.
- Any consumer must respect `HOST_STATE_VALID_WINDOW` or stale callbacks can be revived.

## Test Signals

Useful validation includes static layout/size checks for the documented header sizes, dump compatibility tests after structure changes, magic/version mismatch tests, index-map old-to-new remap tests, and analyzer/serializer agreement tests over generated dumps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/viced/serialize_state.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/viced/state_analyzer.c -->
# sources/distributed-fs/openafs/src/viced/state_analyzer.c

## Purpose

`state_analyzer.c` is an interactive diagnostic tool for demand-attach fileserver state dumps. It mmaps a dump file, decodes the serialized headers, host entries, FileEntry records, CallBack records, timeout queues, and file-entry hash buckets, and lets an operator navigate or search those structures.

## Important APIs, Types, And Functions

- `main`, `openFile`, `initState`, `banner`, and `prompt` implement program startup and the REPL.
- `dump_hdr`, `dump_h_hdr`, `dump_cb_hdr`, `dump_cb_timeout`, `dump_cb_fehash`, `dump_he`, `dump_fe`, `dump_cb`, and related navigation wrappers render decoded structures.
- `get_hdr`, `get_h_hdr`, `get_cb_hdr`, `get_cb_timeout_hdr`, `get_cb_timeout`, `get_cb_fehash_hdr`, `get_cb_fehash`, `get_he`, `get_fe`, and `get_cb` lazily decode and cache memory-map positions.
- `find_fe_by_index`, `find_fe_by_fid`, and `find_cb_by_index` provide linear searches over decoded records.
- Static cursor/cache structs hold current host, FE, and CB positions and decoded data.

## Control Flow

Startup opens either the provided path or `AFSDIR_SERVER_FSSTATE_FILEPATH`, mmaps it read-only, then enters a prompt with global, host, FE, and CB modes. Commands switch modes, dump headers, dump current/next/previous/first/last/all records, hex-dump raw bytes, or search by index/FID. Decoding is lazy: top-level headers are read once, variable-length record offsets are cached as the user walks to specific indices, and CB navigation is relative to the currently selected FE.

## State And Persistence Behavior

The analyzer does not persist new state. It consumes the dump schema from `serialize_state.h` and reconstructs enough pointer-like state from offsets and record lengths to inspect the dump. Host records include optional interface and CPS arrays; callback records include FE headers followed by one FE disk entry and then that FE's CB disk entries. The analyzer validates magic/version values during display and performs bounds checks for major top-level offsets before copying structures out of the mmap.

## Dependencies And Integration Points

The tool depends directly on the same `viced.h`, `host.h`, `callback.h`, and `serialize_state.h` definitions used by the serializer. It includes volume, vnode, RX, partition, ACL, PT, and utility headers because the serialized structures embed fileserver types. Its output is a troubleshooting bridge between production dumps and source-level host/callback structures.

## Risks And Edge Cases

- It opens the dump with `O_RDWR` even though it maps with `PROT_READ`; this may unnecessarily fail for read-only dump copies.
- Top-level offset checks are present, but many later `memcpy` operations rely on record counts/lengths from the file and do not fully revalidate every variable-length record boundary.
- The REPL parser uses fixed-size input and simple tokenization; malformed commands are rejected but not robustly quoted.
- `get_h_hdr` copies the host header but does not set `hdrs.h_hdr_valid`, so repeated calls may recopy it.

## Test Signals

Tests should run analyzer commands against a small synthetic valid dump, corrupt magic/version fields, bad top-level offsets, zero-record dumps, host records with/without interfaces and CPS arrays, FE records with multiple CBs, and `find by fid` / `find by index` paths. Fuzzing record lengths would be valuable because this tool is commonly used on suspect dumps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/viced/state_analyzer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/viced/viced.c -->
# sources/distributed-fs/openafs/src/viced/viced.c

## Purpose

`viced.c` is the OpenAFS fileserver main program. It parses fileserver options, initializes logging, audit, directory buffers, RX services, host/callback/protection/VL libraries, the volume package, and background maintenance threads. Under demand-attach fileserver builds, it also coordinates startup restore and shutdown save of fileserver state.

## Important APIs, Types, And Functions

- Global configuration/state includes RX/logging flags, CPS lists, `confDir`, cache sizes, vnode/cache/callback counts, server addresses, `FS_HostUUID`, and DAFS `struct fs_state fs_state`.
- Signal/admin functions: `CheckSignal_Signal`, `ShutDown_Signal`, `viced_SuperUser`, `fs_IsLocalRealmMatch`, and `viced_syscall`.
- Maintenance threads: `FiveMinuteCheckLWP`, `HostCheckLWP`, `FsyncCheckLWP`, and `ShutdownWatchdogLWP`.
- Shutdown: `ShutDownAndCore` tranquilizes RX/volumes, flushes, prints counters, shuts down volume state, and optionally saves DAFS state.
- Option handling: `ParseRights`, `max_fileserver_thread`, `ParseArgs`, and `CheckParms`.
- External initialization: `InitPR`, `vl_Initialize`, `ReadSysIdFile`, `WriteSysIdFile`, `Do_VLRegisterRPC`, `SetupVL`, and `InitVL`.
- `main` performs process initialization and then sleeps indefinitely after server startup.

## Control Flow

`main` initializes directory paths and ihandle defaults, parses command options, opens the config directory and logs, registers soft signals, initializes audit and directory buffers, initializes `fs_state`, raises fd limits, configures volume callback hooks, initializes ACL and RX, binds the fileserver RX service on port 7000, creates RX stats service, initializes host and callback packages, registers with VLDB, initializes PR, initializes the volume package, attaches volumes, restores DAFS state before starting RX worker threads in DAFS builds, starts background maintenance pthreads, records host identity/start time, then loops forever.

Shutdown starts by making RX and volumes tranquil. DAFS shutdown marks `fs_state.mode = FS_MODE_SHUTDOWN`, shuts down the volume package, waits until the five-minute, host-check, and fsync-check threads report tranquil, then calls `fs_stateSave()` unless this is an abnormal panic shutdown or state saving was disabled.

## State And Persistence Behavior

Persistent identity is stored in the SysID file with magic/version, UUID, and registered server addresses. `ReadSysIdFile` validates it and populates `FS_HostUUID` and addresses unless NetInfo/NetRestrict supplied addresses; `WriteSysIdFile` rewrites it after successful VL address registration. DAFS state persistence is delegated to `serialize_state.c`, but this file determines when restore/save is safe relative to RX request serving and helper-thread quiescence.

## Dependencies And Integration Points

`viced.c` integrates nearly every server subsystem in this subset: RX/RXKAD/RX stats, Ubik/VL client calls, PR client calls, volume package APIs, host/callback packages, audit, command parsing, logging, directory buffers, ihandle cache, and platform soft signals. It exposes `viced_SuperUser` for RX stats authorization and sets `V_BreakVolumeCallbacks` to delayed callback-break integration unless `-novbc` is used.

## Risks And Edge Cases

- Startup ordering is critical: DAFS must restore state before RX request processing begins.
- Shutdown waits for helper threads via condition variables; bugs in tranquil flags can hang shutdown/state save.
- `ReadSysIdFile` uses `if (!(fd = afs_open(...)))`, which treats fd `0` as failure.
- VL registration conflict `VL_MULTIPADDR` is not fatal in `main`, but it indicates address ownership problems requiring repair.
- Many command-line options tune resource limits; invalid combinations can silently clamp values, so behavior depends on logs.

## Test Signals

High-value tests include option parsing boundaries, RX bind address selection with NetInfo/NetRestrict, SysID read/write round trip, VL registration retry/conflict paths, DAFS restore-before-RX ordering, shutdown state-save only after helper-thread quiescence, and abnormal shutdown skipping state save.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/viced/viced.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/viced/viced.h -->
# sources/distributed-fs/openafs/src/viced/viced.h

## Purpose

`viced.h` is the primary fileserver header for shared types, counters, statistics structures, restart constants, locks, and DAFS runtime mode state. It defines the `DirHandle` contract used by physical directory I/O and the `fs_state` contract used by DAFS startup/shutdown coordination.

## Important APIs, Types, And Functions

- `DirHandle` stores volume/device/inode/vnode/uniquifier/cache-check identity plus an `IHandle_t *`.
- Opcode/stat constants define server call counter indexes and fetch/store size buckets.
- `struct AFSCallStatistics`, `struct AFSDisk`, and `struct AFSStatistics` define legacy statistics surfaces.
- Global flags `busyonrst`, `saneacls`, and `enable_old_store_acl` are declared for cross-file policy checks.
- Restart/panic constants and thread limits define fileserver control values.
- `FS_LOCK`, `FS_UNLOCK`, `FSYNC_LOCK`, and `FSYNC_UNLOCK` wrap global pthread mutexes.
- Under `AFS_DEMAND_ATTACH_FS`, `struct fs_state` tracks server mode, helper-thread tranquility, salvage sync fatal state, state-save/restore/verify options, a condition variable, and an rwlock. `FS_STATE_*` macros initialize and lock that state.
- `viced_SuperUser(struct rx_call *call)` is declared for RX stats authorization.

## Control Flow

This header encodes shared control primitives rather than executable flow. `DirHandle` is filled by `SetDirHandle` before directory buffer I/O and compared by `FidEq`. DAFS code uses `FS_STATE_WRLOCK` to transition from normal to shutdown, helper threads use the same lock to publish tranquil flags, and shutdown waits on `worker_done_cv` while checking these flags.

## State And Persistence Behavior

The `DirHandle` fields are deliberately copied out of the underlying ihandle so cached directory pages remain tied to the original volume/vnode generation even if an ihandle is later reused. `fs_state.options` fields are immutable after multithreaded startup and determine whether `serialize_state.c` writes or reads persistent host/callback state.

## Dependencies And Integration Points

It includes system-call utility headers and `fs_stats.h`, and it exposes shared locks for `viced.c`, file procedure code, and fsync paths. It also provides `DirHandle` to `physio.c` and DAFS mode definitions to `serialize_state.c`.

## Risks And Edge Cases

- Comments warn that `DirHandle` size and field ordering matter to `dir/buffer.c`; layout changes can break cache hashing.
- Lock hierarchy notes put `fs_state.state_lock` directly above `FS_LOCK`; inversions can deadlock shutdown.
- `volatile` fields in `fs_state` are not a synchronization substitute; correct use depends on the provided locks.

## Test Signals

Static ABI/layout checks for `DirHandle`, lock-order review tests, and DAFS thread-state transition tests are important. Statistics consumers should also compile-check all counter constants against generated RPC opcode ranges.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/viced/viced.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/viced/viced_prototypes.h -->
# sources/distributed-fs/openafs/src/viced/viced_prototypes.h

## Purpose

`viced_prototypes.h` is a small cross-module declaration header for fileserver globals and functions needed by multiple `viced` components. It avoids local extern duplication for error translation, quota spare settings, callback initialization/break helpers, and DAFS state persistence entry points.

## Important APIs, Types, And Functions

- `sendBufSize` is the global fileserver send buffer size.
- `sys_error_to_et` and `init_sys_error_to_et` expose system-error to OpenAFS error-table translation.
- `BlocksSpare` and `PctSpare` expose quota/partition spare policy from `afsfileprocs.c`.
- `InitCallBack`, `BreakLaterCallBacks`, and `BreakVolumeCallBacksLater` expose callback package operations.
- Under `AFS_DEMAND_ATTACH_FS`, `fs_stateSave` and `fs_stateRestore` expose serialized state lifecycle calls.

## Control Flow

This header does not implement flow, but the declarations connect startup/shutdown and maintenance logic: `viced.c` initializes callbacks with `InitCallBack`, the fsync maintenance thread drains delayed callback breaks via `BreakLaterCallBacks`, the volume package can use `BreakVolumeCallBacksLater`, and DAFS shutdown/startup invokes `fs_stateSave`/`fs_stateRestore`.

## State And Persistence Behavior

The DAFS prototypes are the persistence bridge to `serialize_state.c`. The spare-space globals affect fileserver write/quota behavior but are not persisted here.

## Dependencies And Integration Points

The file assumes common OpenAFS typedefs such as `afs_int32` and `VolumeId` are already visible to includers. It is included by `physio.c`, `serialize_state.c`, and `viced.c`.

## Risks And Edge Cases

- Because it is a broad extern header, type drift between declarations and implementations can cause subtle ABI or compile failures.
- The conditional DAFS declarations mean non-DAFS builds must not reference state save/restore.

## Test Signals

The main signal is full matrix compilation with and without `AFS_DEMAND_ATTACH_FS`, plus link checks for callback and error translation symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/viced/viced_prototypes.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/vlserver/Makefile.in -->
# sources/distributed-fs/openafs/src/vlserver/Makefile.in

## Purpose

`Makefile.in` builds the OpenAFS volume location server components, generated VL RPC stubs, helper utilities, static/shared VLDB libraries, and installable headers. It wires RXGEN, COMPILE_ET, Ubik/RX/auth dependencies, and install/dest targets for `vlserver`, `vlclient`, `cnvldb`, and `vldb_check`.

## Important Targets And Variables

- `INCLS`, `LIBS`, `LT_objs`, and `LT_deps` define compile/link dependencies.
- `all` builds servers/tools, generated stubs, `liboafs_vldb.la`, `libvlserver_pic.la`, `libvldb.a`, and `depinstall`.
- `generated` produces `vl_errors.c`, `vlserver.h`, RX client/server/XDR sources, and headers from `vldbint.xg` and `vl_errors.et`.
- RXGEN rules create `vldbint.cs.c`, `vldbint.ss.c`, `vldbint.xdr.c`, `vldbint.h`, `Kvldbint.cs.c`, and `Kvldbint.xdr.c`.
- `install` and `dest` install binaries conditionally when pthreaded Ubik is not enabled, but always install libraries and public headers.
- `clean` removes generated/object/archive/binary artifacts.

## Control Flow

Build flow starts from generated RPC/error-table sources, compiles server/client/tool objects against VL headers, links utilities with LWP Ubik/RX/auth libraries, then stages generated headers into top-level include directories via `depinstall`. Install flow creates server sbin/lib/include directories and places versioned artifacts into either configured destinations or legacy `DEST` paths.

## State And Persistence Behavior

This file does not manage runtime state, but it controls which generated protocol artifacts and conversion/checking tools are available. Installing `cnvldb` as `vldb_convert` and `vldb_check` is important for VLDB persistence migration and validation workflows.

## Dependencies And Integration Points

It includes shared config makefiles, LWP make rules, RXGEN, COMPILE_ET, roken, XLIBS, Ubik, auth, RXKAD, RXSTAT, command, audit, util, and crypto libraries. It exports headers under `afs/` for clients like `viced.c` and `vlclient.c`.

## Risks And Edge Cases

- `all` lists `vlserver` and `cnvldb` twice, which is harmless but noisy.
- Install skips server binaries when `ENABLE_PTHREADED_UBIK=yes`; packaging must ensure an alternate pthreaded build installs equivalent binaries.
- Generated-file dependency order matters; stale RXGEN outputs can create protocol mismatches.

## Test Signals

Run clean builds, generated-only builds, `make install DESTDIR=...`, pthreaded and non-pthreaded Ubik variants, and ABI checks that installed `vl_opcodes.h`, `vlserver.h`, `vldbint.h`, and `cnvldb.h` match the build outputs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/vlserver/Makefile.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/vlserver/cnvldb.c -->
# sources/distributed-fs/openafs/src/vlserver/cnvldb.c

## Purpose

`cnvldb.c` is the VLDB on-disk conversion utility. It reads a Ubik VLDB file, detects or validates its VLDB version, optionally prints version/entries, converts headers and entries between supported versions 1 through 4, repairs some multihome extent block pointers, writes a temporary database, fsyncs it, and renames it over the original path.

## Important APIs, Types, And Functions

- `handleit` is the command dispatcher for `-to`, `-from`, `-path`, `-showversion`, and `-dumpvldb`.
- `readheader`, `readentry`, and `printentry` consume existing VLDB bytes after the 64-byte Ubik header.
- `read_mhentries` reads and validates v4 multihomed extent blocks into `base[]`.
- `convert_mhentries` repairs multihome pointers and converts multihome address references back to single addresses for v4-to-v3.
- `convert_header` rewrites header versions, sizes, EOF/free pointers, hash table pointers, and server address arrays.
- `Conv4to3` adjusts record offsets when v4 multihome blocks are removed.
- `convert_vlentry` rewrites per-volume entries between old/new struct layouts and handles multihome info blocks.
- `rewrite_header` seeks back after entry conversion to write final header state.

## Control Flow

The converter opens the database read-only, reads the version at offset 64, reads the 64-byte Ubik header, decodes the VL header, and, for v3/v4-style headers, reads multihome extent blocks before resuming sequential entry processing. In display mode it prints version or entries and exits. In conversion mode it verifies requested versions and multihome downgrade constraints, changes to the database parent directory, writes `XXnewvldb`, copies the Ubik header, converts the VL header and each entry sequentially, performs multihome fixups, rewrites the final header, fsyncs, closes, and renames the temp file to the requested path.

## State And Persistence Behavior

This utility mutates the persistent VLDB file by replacement. It preserves the Ubik header verbatim and rewrites VLDB content in network byte order. Header conversions adjust offsets by header-size differences. Version 4 multihome continuation blocks are preserved only when converting to version 4 or higher; downgrading to version 3 removes them, rewrites hash/list offsets, clears `SIT`, and chooses the first IP address from a multihomed set.

## Dependencies And Integration Points

It depends on `vlserver.h` for current VLDB constants and `cnvldb.h` for legacy on-disk layouts. It is built by `vlserver/Makefile.in` and installed as `vldb_convert`. It complements `vldb_check` and the VL server's Ubik database format.

## Risks And Edge Cases

- It replaces the original database after `fsync(new)` but does not fsync the parent directory after rename.
- Several error paths call `exit`, so library-style recovery is impossible.
- Some read/write checks use `int` for byte counts and offsets; large/corrupt databases can stress assumptions.
- A likely bug in `convert_header` for v2/3/4 to v1 writes `sizeof(struct vlheader_1)` but compares against `sizeof(struct vlheader_2)`.
- Downgrading multihomed entries loses all but one IP address.

## Test Signals

Use golden VLDB fixtures for versions 1, 2, 3, and 4; round-trip conversions where lossless; v4-to-v3 tests with multihomed extent blocks; corrupted SIT/extent pointer repair tests; `-showversion` and `-dumpvldb` smoke tests; and failure-injection tests for short reads/writes, fsync, and rename.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/vlserver/cnvldb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/vlserver/cnvldb.h -->
# sources/distributed-fs/openafs/src/vlserver/cnvldb.h

## Purpose

`cnvldb.h` defines legacy VLDB on-disk header and entry structures used by `cnvldb.c` to convert older VLDB formats. It captures versions 1, 2, and 3 layout differences around server address capacity, hash tables, SIT multihome pointers, and per-entry server arrays.

## Important APIs, Types, And Structures

- `vital_vlheader_1` and typedefs `vital_vlheader1`, `vital_vlheader2`, and `vital_vlheader3` describe shared vital header fields: version, header size, free/eof pointers, alloc/free counts, max volume id, and per-type totals.
- `vlheader_1` has 31 mapped addresses plus name/id hash tables.
- `vlheader_2` and `vlheader_3` expand mapped addresses to 255 and add `SIT`.
- `vlentry_1` and `vlentry_2` use fixed 8-element server arrays and include legacy spare fields.
- `vlentry_3` uses `MAXSERVERS` server arrays and removes most spare fields unless `obsolete_vldb_fields` is enabled.

## Control Flow

There is no executable control flow. Conversion code casts these layouts over database bytes, copies shared fields, and conditionally expands/shrinks headers and entries based on requested source/target version.

## State And Persistence Behavior

These structs are persistent ABI definitions for historical VLDB files. Their field order, sizes, and network-byte-order usage determine how conversion preserves volume ids, lock data, clone ids, hash links, names, server ids, partitions, and flags.

## Dependencies And Integration Points

The header relies on OpenAFS integer types, `MAXSERVERS`, and VL constants supplied by includers such as `vlserver.h`. It is installed by the vlserver makefile for tooling that needs legacy conversion layouts.

## Risks And Edge Cases

- No include guard is present in this file.
- The structs intentionally mirror old binary layouts; normal cleanup or padding changes would corrupt conversion.
- Version 1 has only 31 address slots and versions 1/2 have only 8 server slots per entry, so downgrade conversions can fail or lose unsupported topology.

## Test Signals

Compile tests should include this header through `cnvldb.c` and installed headers. Binary fixture tests should assert exact `sizeof` values and offsets for each legacy header/entry layout.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/vlserver/cnvldb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/vlserver/vl_opcodes.h -->
# sources/distributed-fs/openafs/src/vlserver/vl_opcodes.h

## Purpose

`vl_opcodes.h` defines the numeric RX operation codes for the VLDB service, currently spanning `501` through `534`. It is a protocol compatibility header consumed by generated stubs, clients, servers, diagnostics, and statistics code.

## Important APIs, Types, And Constants

The constants cover original VL operations (`VLCREATEENTRY` through `VLCHANGEADDR`), N variants for newer entry structures, U variants for UUID/multihome address support, address registration and lookup (`VLREGADDR`, `VLGETADDRSU`), and `VLLISTATTRIBUTESN2`.

## Control Flow

There is no executable flow. Runtime dispatch and generated RX code use these numbers to identify VL RPCs on the wire; `vlclient.c` keeps a parallel ordered name table for statistics display.

## State And Persistence Behavior

The file does not persist state directly, but opcode stability is part of the wire protocol ABI. Reusing or renumbering values would break clients and servers across versions.

## Dependencies And Integration Points

The header is installed under `afs/vl_opcodes.h` by `Makefile.in` and aligns with `vldbint.xg`, VL server implementations, and client calls such as `ubik_VL_RegisterAddrs`.

## Risks And Edge Cases

- Adding a new opcode requires coordinated updates to RXGEN definitions, server implementation, client statistics name tables, and tests.
- `vlclient.c` assumes `VL_NUMBER_OPCODESX` matches the number of entries through `VLLISTATTRIBUTESN2`.

## Test Signals

Protocol tests should verify generated stubs use these numeric values, mixed-version clients can still call old operations, and stats rendering remains aligned when opcodes are added.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/vlserver/vl_opcodes.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/vlserver/vlclient.c -->
# sources/distributed-fs/openafs/src/vlserver/vlclient.c

## Purpose

`vlclient.c` is an interactive and partially non-interactive VLDB test/maintenance client. It initializes a Ubik VL client connection, optionally probes VL servers or prints stats, then accepts commands that exercise create, delete, replace, update, list, lookup, hash repair, address, multihome, and stats RPCs.

## Important APIs, Types, And Functions

- `vl_Initialize` wraps `ugen_ClientInitServer` for VLDB service connections.
- `GetServer` parses dotted IPv4 or resolves a hostname to network-byte-order address.
- `handleit` parses top-level command options and runs the interactive command loop.
- `GetVolume` supports duplicate-volume detection using an in-memory hash of `struct Vlent`.
- Fill/display helpers build and print `vldbentry`, `VldbUpdateEntry`, `VldbListByAttributes`, `nvldbentry`, stats, and command usage.
- Interactive commands include `cr`, `rm`, `re`, `up`, `ls`, `ldups`, `checkhash`, `fixhash`, `la`, `lan2`, `ln`, `lnn`, `di`, `rmnh`, `undelete`, `dn`, `nv`, `gs`, `ga`, `gau`, `mhc`, `regaddr`, `ca`, and `caid`.

## Control Flow

Startup defaults to client config paths, processes options such as `-cellpath`, `-server`, `-noauth`, `-host`, `-cell`, `-getstats`, and `-probe`, then initializes the VLDB Ubik client. Probe mode sends `VL_ProbeServer` to each connection and exits; getstats mode prints VL dynamic and header stats and exits. Interactive mode tokenizes each input line with whitespace splitting, dispatches by short command name, calls the corresponding `ubik_VL_*` RPC, prints results and return codes, and loops until EOF or quit.

## State And Persistence Behavior

The client itself has transient state: `cstruct`, server connections, command args, duplicate-check hash tables, and allocated bulk result arrays. It can mutate persistent VLDB state through create/delete/replace/update, hash repair, undelete, address registration, and address changes. The hash-check/fix commands compare sequential listing with name/id lookups and can trigger server-side rehash updates.

## Dependencies And Integration Points

It depends on RX, RXKAD, Ubik, cell config, command parsing, VL generated interfaces from `vlserver.h`, host utility resolution, and OpenAFS config paths. It is built with `libvldb.a` and the same VL protocol artifacts generated by the makefile.

## Risks And Edge Cases

- Parsing is intentionally simple and uses fixed global `args[50]`; missing or extra arguments can lead to bad reads or nonsensical RPC input.
- Several buffers use `strcpy` into fixed-size fields, so this is not hardened as an untrusted-input CLI.
- Some maintenance commands mutate production VLDB state (`fixhash`, `undelete`, `regaddr`, `ca`); they need operational caution.
- `GetVolume` appears to copy `entry->name` into `VL->name` in the wrong direction, weakening duplicate diagnostics.
- Memory allocated for duplicate-check arrays is not always freed before continuing, acceptable for short tooling but visible in long sessions.

## Test Signals

Useful tests include command parser/usage smoke tests, noauth/auth initialization, probe mode against fake/mocked connections, stats rendering, list/get/listattributes output with bounded bulk lengths, hash-check/fix behavior on a controlled VLDB, multihome address display/duplicate checks, and fuzzing malformed interactive input to document tool limitations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/vlserver/vlclient.c -->
