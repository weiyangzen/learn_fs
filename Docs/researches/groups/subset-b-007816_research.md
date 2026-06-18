# Research: subset-b-007816

Grouped research for the exact source files assigned to `subset-b-007816`. Each section preserves the source path in its title and is wrapped for reconciliation into the mapped per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/vol/daemon_com.h -->
## sources/distributed-fs/openafs/src/vol/daemon_com.h

Purpose: common SYNC protocol declaration layer used by volume daemons and their clients. It defines the generic command/response namespace, reason and flag ranges, endpoint representation, socket-domain selection, server/client state, and the on-wire framing structures used by protocols such as FSSYNC and SALVSYNC.

Important APIs/types/functions: `SYNC_COM_CODE_DECL`, `SYNC_RES_CODE_DECL`, and `SYNC_REASON_CODE_DECL` reserve the low 0-65535 range for global SYNC values and let protocol users define higher-level codes. `enum SYNCOpCode` currently exposes `SYNC_COM_CHANNEL_CLOSE`; `enum SYNCReasonCode` names generic response classes such as `SYNC_OK`, `SYNC_DENIED`, `SYNC_COM_ERROR`, `SYNC_BAD_COMMAND`, and `SYNC_FAILED`. `SYNC_endpoint_t` abstracts either an AF_UNIX socket name or localhost TCP port. `SYNC_server_state_t` and `SYNC_client_state` hold socket descriptors, endpoint metadata, protocol version/name, retry/listen settings, and packet/command/response sequence counters. `SYNC_command_hdr` and `SYNC_response_hdr` are the wire headers, while `SYNC_command` and `SYNC_response` attach caller-owned payload buffers and receive lengths. The prototypes delegate implementation to `daemon_com.c`: `SYNC_getSock`, `SYNC_getAddr`, `SYNC_connect`, `SYNC_ask`, `SYNC_closeChannel`, `SYNC_getCom`, `SYNC_putRes`, `SYNC_bindSock`, and cleanup/validation helpers.

Control flow: this header is declarative, but it fixes the runtime flow used elsewhere. Clients connect through `SYNC_client_state`, send a `SYNC_command` with a filled header and payload pointer, and receive a `SYNC_response`. Servers bind using `SYNC_server_state_t`, accept sockets, decode commands with `SYNC_getCom`, and return framed responses with `SYNC_putRes`. `SYNC_COM_CHANNEL_CLOSE` plus `SYNC_FLAG_CHANNEL_SHUTDOWN` provide a graceful close path.

State and persistence: no state is allocated in this header. Runtime state is explicitly held in client/server structs, including sequence counters that identify packet, command, and response ordering. The protocol has no disk persistence, but socket files may exist when `USE_UNIX_SOCKETS` is enabled; `SYNC_cleanupSock` and `SYNC_bindSock` manage those external endpoint artifacts.

Dependencies: depends on AFS integer/socket types and platform socket headers. `USE_UNIX_SOCKETS` selects `sockaddr_un` and a filesystem socket name; otherwise `sockaddr_in` and `FSSYNC_IN_PORT`-style ports are used. `SYNC_PROTO_BUF_DECL` uses an `afs_int64` backing array so payload buffers can be safely cast to aligned structures.

Integration points: consumed by `fssync.h`, `fssync-client.c`, `fssync-server.c`, `fssync-debug.c`, and similar daemon protocols. The `SYNC_FLAG_DAFS_EXTENSIONS` bit lets peers signal demand-attach fileserver capabilities, and `SYNC_SELECT_TIMEOUT` works around Linux select wakeup behavior in server loops.

Risks: packet structures are host-C structs, so all peers must share ABI assumptions about integer size, layout, and endianness. Fixed `SYNC_PROTO_MAX_LEN` makes payload sizing simple but requires every server handler to check response buffer capacity. String fields inside protocol-specific payloads need explicit null-termination validation because this layer only frames bytes. The global/user code ranges must be coordinated to avoid collisions.

Test signals: useful tests include malformed `command_len`/`response_len`, protocol-version mismatch, channel close behavior, payloads near `SYNC_PROTO_MAX_LEN`, UNIX versus INET endpoint construction, sequence counter progression, and server cleanup of stale UNIX socket paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/vol/daemon_com.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/vol/daemon_com_inline.h -->
## sources/distributed-fs/openafs/src/vol/daemon_com_inline.h

Purpose: tiny diagnostic helper header for the generic SYNC protocol. It converts generic SYNC response codes into stable string names for logs and debug tools.

Important APIs/types/functions: `SYNC_res2string(afs_int32 response)` is a `static_inline` switch that recognizes `SYNC_OK`, `SYNC_DENIED`, `SYNC_COM_ERROR`, `SYNC_BAD_COMMAND`, and `SYNC_FAILED`. The private `SYNC_ENUMCASE` macro keeps case labels and returned strings synchronized, then is undefined at the end of the file.

Control flow: runtime behavior is only a switch lookup. Unknown or protocol-specific response values fall through to `"**UNKNOWN**"`.

State and persistence: no mutable state and no persistence. The returned strings are string literals.

Dependencies: includes `daemon_com.h` and relies on the repository's `static_inline` definition from platform headers included before this header in normal OpenAFS builds.

Integration points: used by `fssync-server.c` for verbose response logging and by `fssync-debug.c` for command-line output. It intentionally covers only generic SYNC response codes, while protocol-specific command/reason stringification lives in `fssync_inline.h`.

Risks: new generic response codes added to `daemon_com.h` need a matching case here or debug output degrades to unknown. The function returns `char *` rather than `const char *`, so callers could technically attempt to mutate literals.

Test signals: compile inclusion with `daemon_com.h`, one assertion for every known response code, and an unknown-value assertion returning `"**UNKNOWN**"`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/vol/daemon_com_inline.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/vol/devname.c -->
## sources/distributed-fs/openafs/src/vol/devname.c

Purpose: legacy non-NAMEI helper for mapping a mounted `/vicep*` partition's device number back to a block device basename and for deriving raw character-device paths. It is excluded under `AFS_NAMEI_ENV`.

Important APIs/types/functions: `vol_DevName(dev_t adev, char *wpath)` scans the platform mount database, filters for writable `/vicep` partitions, stats candidate mountpoints, compares `st_dev` with `adev`, and returns the device basename in static storage. If `wpath` is non-NULL, it also copies the parent directory of the device path. `afs_rawname(char *devfile)` walks backward through a device path, inserting `r` after each directory separator until it finds an existing character device.

Control flow: `vol_DevName` has separate mount-iteration branches for AIX `getmount`, Solaris `MNTTAB`, SGI/Sun/HPUX `getmntent`, and BSD-style `getfsent`. For each record it rejects read-only, remote, removable, non-UFS, or non-`/vicep` entries according to platform checks, then compares the root inode and device number. `afs_rawname` repeatedly builds candidate raw names and returns on the first `S_ISCHR` stat match.

State and persistence: both functions return pointers into static buffers (`pbuffer` and `rawname`), so callers must copy results before the next call. No files are modified. Mount-table and device-node state are external runtime dependencies.

Dependencies: platform mount headers, filesystem headers, `ihandle.h`, `partition.h`, `VICE_PARTITION_PREFIX`, `ROOTINO`, and `OS_DIRSEPC`. The code is deeply conditional for old server platforms.

Integration points: used by inode-based salvager and volume utilities that need raw device access for `ListViceInodes`. `listinodes.c` calls `afs_rawname` in generic non-NAMEI scanning. The `wpath` output is later used to rebuild raw device paths.

Risks: static buffers and `strcpy`/`strcat` assume short device paths and are not thread-safe. Mount-table filtering is conservative and old-platform-specific; newer filesystem naming can be missed. `vol_DevName` intentionally ignores non-`/vicep` partitions, which is correct for AFS partitions but surprising for generic callers. Failure paths may leak open mount table handles on early returns in some platform branches.

Test signals: platform-specific tests should mock or run against mount tables containing writable `/vicep` entries, read-only entries, non-AFS mounts, matching and non-matching `st_dev`, device names with and without directory separators, and raw-device candidates that exist only at different path depths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/vol/devname.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/vol/fssync-client.c -->
## sources/distributed-fs/openafs/src/vol/fssync-client.c

Purpose: client-side implementation of the FSSYNC protocol, compiled when `FSSYNC_BUILD_CLIENT` is set. It lets volume utilities, salvagers, debug tools, and other non-fileserver processes coordinate with the fileserver's volume package through the generic SYNC transport.

Important APIs/types/functions: static `fssync_state` defines the FSSYNC endpoint, protocol version, retry limit, hard timeout, and protocol name. `FSYNC_clientInit`, `FSYNC_clientFinis`, and `FSYNC_clientChildProcReconnect` wrap SYNC connect/close/reconnect. `FSYNC_askfs` serializes requests through `vol_fsync_mutex` under pthread builds and normalizes logging for response classes. `FSYNC_GenericOp` builds a `SYNC_command` from a caller-supplied extension header. `FSYNC_VolOp`, `FSYNC_StatsOp`, `FSYNC_VGCQuery`, `FSYNC_VGCAdd`, `FSYNC_VGCDel`, and `FSYNC_VGCScan` are typed convenience wrappers. `FSYNC_VerifyCheckout` protects demand-attach checkout flows after a lock is obtained.

Control flow: callers initialize the client, fill or request a response buffer, and use a wrapper that sets `programType`, command, reason, total command length, and payload pointer. `FSYNC_askfs` sends the request via `SYNC_ask`, logs exceptional outcomes, and returns the generic SYNC result. Volume group updates funnel through `_FSYNC_VGCUpdate`; scans choose `FSYNC_VG_SCAN` or `FSYNC_VG_SCAN_ALL` depending on whether a partition was supplied. `FSYNC_VerifyCheckout` queries `FSYNC_VOL_QUERY_VOP`, interprets unknown volume or wrong partition as safe, treats missing or mismatched pending operations as a possible fileserver restart, and returns `SYNC_DENIED` when checkout should be retried.

State and persistence: client state is process-global in `fssync_state`. Under pthread builds, a single mutex protects the socket/channel state. No disk state is written by this file; persistence effects are indirect through server-side volume state changes.

Dependencies: generic SYNC APIs, `fssync.h`, volume package globals such as `programType`, logging, partition/volume definitions, and OpenAFS threading primitives. The code assumes protocol payload structs from `fssync.h` match the server ABI.

Integration points: called by volume utilities, salvagers, `fssync-debug.c`, and conversion helpers in `listinodes.c`. It is the narrow client boundary between external utilities and the fileserver's in-memory volume registry.

Risks: a single static socket state makes calls process-global and requires reconnect after fork. `FSYNC_GenericOp` trusts caller-supplied payload length and pointer. The fixed 16-byte partition field truncates through `strlcpy`, so invalid or too-long partition names can be rejected server-side or refer to unintended names. `FSYNC_VerifyCheckout` compares program type, pid, command, and reason, but deliberately avoids thread id due portability concerns.

Test signals: tests should cover init/reconnect/finalize, mutex serialization, response logging for each generic result, null versus caller-owned response buffers, VGC add/delete/scan command selection, checkout verification for matching vop, no pending vop, unknown volume, wrong partition, and mismatched pid/program/command/reason.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/vol/fssync-client.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/vol/fssync-debug.c -->
## sources/distributed-fs/openafs/src/vol/fssync-debug.c

Purpose: command-line administration/debug utility for issuing FSSYNC requests and decoding returned volume, vnode, volume-operation, volume-group-cache, and statistics structures. It defines `MAIN` so common OpenAFS globals are provided in this translation unit.

Important APIs/types/functions: `main` registers subcommands with `cmd_CreateSyntax`: `online`, `offline`, `mode/needvolume`, `detach`, `callback/cbk`, `move`, `list/ls`, `leaveoff`, `attach`, `error`, `query/qry`, `header/hdr`, `volop/vop`, `vnode`, `stats`, `vgcquery/vgcqry`, `vgcadd`, `vgcdel`, `vgcscan`, and `vgcscanall`. `common_prolog` initializes server paths, the volume package in `debugUtility` mode, directory package state, reason/program type overrides, and the FSSYNC client connection. `common_volop_prolog`, `vn_prolog`, `do_volop`, and `do_vnqry` build request state. `debug_response` and `read_result` report protocol metadata and handle size mismatches. Demand-attach builds add state/flag stringify helpers for `Volume`, `Vnode`, VLRU, and vnode flags.

Control flow: each command parses common parameters, calls `VConnectFS`, sends an FSSYNC request through client wrappers, prints response metadata, optionally decodes the payload, and disconnects. Non-DAFS builds run `dafs_prolog`, which sends a no-op `LISTVOLUMES` request to detect `SYNC_FLAG_DAFS_EXTENSIONS` and tries to exec a `dafssync_debug` variant if needed. Query commands allocate a maximum protocol response buffer and copy the returned payload into local structures before printing fields.

State and persistence: process-local command state includes selected reason, program type, volume/vnode ids, and partition strings. The tool does not persist files directly, but it can cause fileserver state transitions: taking volumes offline/online, forcing error state, marking moved/done, breaking callbacks, and triggering volume group cache scans.

Dependencies: OpenAFS `cmd` parser, directory/path initialization, volume package initialization, FSSYNC client APIs, protocol string helpers, vnode/volume structs, VGC structs, and Windows event/winsock setup where applicable.

Integration points: operational companion to `fssync-server.c`. It is also a protocol compatibility probe: output warns when DAFS/non-DAFS utility and server extensions do not match. The decoded structures mirror server-side payloads and are therefore tightly coupled to server build configuration.

Risks: many arguments are parsed with `atoi`, so invalid numbers become zero. Several allocated `state.vop` objects are not freed because the process exits quickly. Query output exposes raw server pointers that are useful only diagnostically. Payload decoding proceeds after version/size mismatch warnings, so fields may be misleading across ABI-skewed builds. Commands can mutate live fileserver state and should not be treated as read-only except the query/stat paths.

Test signals: CLI tests should cover command registration/aliases, missing required arguments, DAFS prolog behavior, program type names and numeric override, reason override, all query printers with short/exact/oversized payloads, VGC operations, stats subcommands and help, and server-extension mismatch messages.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/vol/fssync-debug.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/vol/fssync-server.c -->
## sources/distributed-fs/openafs/src/vol/fssync-server.c

Purpose: server-side FSSYNC implementation inside the fileserver volume package. It listens for external volume utility requests, decodes SYNC-framed FSSYNC commands, coordinates volume online/offline/state transitions, provides diagnostic query payloads, maintains per-client offline tracking, and handles DAFS-specific pending volume operations and volume group cache maintenance.

Important APIs/types/functions: `FSYNC_fsInit` starts the listener thread/process and initializes handler locking. `FSYNC_sync` waits for volume initialization, binds the endpoint, initializes the DAFS VGC package when enabled, and enters a poll/select dispatch loop. `FSYNC_com` reads one command, validates framing/protocol version, dispatches by opcode, and writes responses. `FSYNC_com_VolOp` validates `FSSYNC_VolOp_hdr`, locates the client offline slot, and dispatches volume operations. Key handlers include `FSYNC_com_VolOn`, `FSYNC_com_VolOff`, `FSYNC_com_VolMove`, `FSYNC_com_VolDone`, `FSYNC_com_VolError`, `FSYNC_com_VolBreakCBKs`, `FSYNC_com_VolQuery`, `FSYNC_com_VolHdrQuery`, `FSYNC_com_VolOpQuery`, `FSYNC_com_VnQry`, `FSYNC_com_StatsOp*`, and `FSYNC_com_VG*`. Handler-array functions (`AddHandler`, `RemoveHandler`, `CallHandler`, `GetHandler`) multiplex up to `MAXHANDLERS` sockets.

Control flow: after binding, the accept handler adds client sockets until the handler table fills, then disables accepting. Each readable client socket is processed synchronously. Volume commands run under `VOL_LOCK`; some callback operations drop it around `V_BreakVolumeCallbacks`. Non-DAFS paths use heavyweight volume attachment APIs. DAFS paths use lightweight lookups, reservations, exclusive-state waits, `VRegisterVolOp_r`, `VDeregisterVolOp_r`, attach-state checks, and background salvage handoff. `FSYNC_Drop` runs on errors/channel close and brings any volumes tracked in that client's `OfflineVolumes` slot back into a sane state.

State and persistence: persistent effects are indirect but significant: volume attach state, `specialStatus`, pending volume op metadata, salvage requests, volume group cache entries/scans, header cache/stat counters, and callback invalidations. Process-local state includes the listening `SYNC_server_state_t`, handler table, `OfflineVolumes[MAXHANDLERS][MAXOFFLINEVOLUMES]`, and DAFS salvage queue/condition variable.

Dependencies: generic SYNC transport, FSSYNC/SALVSYNC headers, volume/vnode/partition/VGC internals, LWP or pthreads, `poll` or `select`, AFS locks, callback hook `V_BreakVolumeCallbacks`, and many demand-attach-only state-machine APIs.

Integration points: all external volume utilities coordinate through this server. `fssync-client.c` builds the request payloads; `fssync-debug.c` exercises all major handlers; salvagers and volserver rely on offline checkout semantics; VGC requests integrate with `vg_cache`.

Risks: ABI-copied in-memory structs are exposed over the local protocol and require matching builds. The handler table is small by design; more than four clients disables accepts until a slot frees. Malformed packet lengths close channels. DAFS state transitions are complex, with denial reasons depending on pending operations, salvage state, partition match, and attach state. Some handlers assert payload capacity instead of returning graceful size errors. `FSYNC_Drop` must be reliable because it releases volumes after client death.

Test signals: strong coverage includes protocol version mismatch, malformed payload sizes, channel close, handler table full/accept reenable, VolOff/VolOn lifecycle, offline client disconnect recovery, partition mismatch, pending vol-op exclusivity, salvage-denial cases, DAFS and non-DAFS builds, query/header/vnode payload sizing, VGC query/add/delete/scan error mappings, and callback break lock release behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/vol/fssync-server.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/vol/fssync.h -->
## sources/distributed-fs/openafs/src/vol/fssync.h

Purpose: public protocol and API contract for fileserver synchronization over the generic SYNC layer. It defines the FSSYNC protocol version, command/reason codes, payload structures, endpoint constants, and client/server prototypes.

Important APIs/types/functions: `FSYNC_PROTO_VERSION` is 3. `enum FSYNCOpCode` defines volume lifecycle operations (`FSYNC_VOL_ON`, `OFF`, `NEEDVOLUME`, `DONE`, `ATTACH`, `LEAVE_OFF`, `FORCE_ERROR`), volume queries (`QUERY`, `QUERY_HDR`, `QUERY_VOP`, `QUERY_VNODE`), callback/move/list commands, statistics commands, and DAFS volume group cache commands (`FSYNC_VG_QUERY`, `ADD`, `DEL`, `SCAN`, `SCAN_ALL`). `enum FSYNCReasonCode` names operational reasons and denial causes such as salvage, move, exclusive checkout, unknown volume, wrong partition, bad state, and partition scanning. Payload types include `offlineInfo`, `FSSYNC_VolOp_hdr`, `FSSYNC_VolOp_command`, `FSSYNC_VolOp_info`, `FSSYNC_StatsOp_hdr`, `FSSYNC_VnQry_hdr`, `FSSYNC_VGQry_response_t`, and `FSSYNC_VGUpdate_command_t`.

Control flow: callers use the client prototypes to initialize a connection, send a generic operation or typed volume/stat/VGC operation, and disconnect. The fileserver calls `FSYNC_fsInit` to start the server side. `FSYNC_VerifyCheckout` is part of the checkout-lock verification flow for DAFS utilities.

State and persistence: the header declares state-bearing wire payloads but owns no storage. `FSSYNC_VolOp_info` is important persistent in-memory metadata attached to `Volume` objects while an external volume operation is pending.

Dependencies: includes `voldefs.h` and depends on `daemon_com.h` symbols being available to command/reason code macros and command/response header pointer types. Volume ids and volume group limits come from OpenAFS volume headers.

Integration points: shared by client, server, debug utility, volume utilities, salvagers, and VGC code. Endpoint constants bind FSSYNC to port 2040 or `fssync.sock` depending on socket mode.

Risks: fixed-size `partName[16]` is a protocol limit and must be null-validated by receivers. Adding opcodes requires updating documentation, stringification in `fssync_inline.h`, client wrappers if needed, server dispatch, and debug support. Struct layout is the local ABI between processes.

Test signals: compile/link all declared APIs under client/server build flags, check every opcode/reason maps to expected values above the SYNC user base, validate payload sizes against `SYNC_PROTO_MAX_LEN`, and verify all server/client/debug switch statements handle newly added opcodes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/vol/fssync.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/vol/fssync_inline.h -->
## sources/distributed-fs/openafs/src/vol/fssync_inline.h

Purpose: diagnostic stringification for FSSYNC command and reason codes. It complements `daemon_com_inline.h` by covering protocol-specific values.

Important APIs/types/functions: `FSYNC_com2string(afs_int32 command)` returns names for `SYNC_COM_CHANNEL_CLOSE` and every `FSYNC_*` command currently declared in `fssync.h`. `FSYNC_reason2string(afs_int32 reason)` returns names for generic SYNC reasons plus FSSYNC reasons from `FSYNC_WHATEVER` through `FSYNC_PART_SCANNING`. Unknown values return `"**UNKNOWN**"`.

Control flow: both functions are inline switch statements with macro-generated cases.

State and persistence: no mutable state or persistence. Returned values are string literals.

Dependencies: includes `fssync.h`; callers normally include OpenAFS headers that define `static_inline` and integer types.

Integration points: used in server verbose logging and debug tool output. It is the main human-readable bridge for FSSYNC packet traces.

Risks: the command table must be kept in sync with `enum FSYNCOpCode`, and the reason table should include generic and protocol-specific reason values. It currently omits `SYNC_REASON_PAYLOAD_TOO_BIG`, so that generic reason will display as unknown. Return type is mutable `char *` despite literals.

Test signals: assert every command/reason in `fssync.h` stringifies as expected, include at least one generic SYNC reason, and check unknown numeric values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/vol/fssync_inline.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/vol/gi.c -->
## sources/distributed-fs/openafs/src/vol/gi.c

Purpose: small legacy utility for opening and dumping a raw inode from a mounted inode-fileserver partition. It is not supported on NT or NAMEI builds.

Important APIs/types/functions: `Perror` formats a message into a fixed buffer and passes it to `perror`. `main` parses optional `-stat`, requires a partition path and inode number, stats the partition to obtain `st_dev`, opens the inode with `iopen(dev, inode, 0)`, and either prints inode metadata via `fstat` or streams the inode contents to stdout.

Control flow: argument parsing is linear. Unsupported platforms exit with an explanatory error. On supported builds, failures to stat/open/fstat exit nonzero; otherwise the program loops `read(fd, buf, sizeof(buf))` and writes each block to fd 1.

State and persistence: no persistent writes. It reads arbitrary inode content and may write that content to stdout. `statflag` is a global command option.

Dependencies: legacy inode syscall `iopen`, POSIX `stat`, `fstat`, `read`, `write`, and OpenAFS component version linkage. It assumes inode-based vice partitions, not NAMEI file layout.

Integration points: operator/debug tool for inode-level investigation outside the normal volume package. The output can be redirected to inspect special volume files or vnode data.

Risks: uses `atoi` for inode parsing and `int` fields in printf, so large inode/stat values may truncate. `Perror` uses `sprintf` into a 200-byte stack buffer. No short-write handling is present when dumping to stdout. Running it on the wrong partition/inode can expose raw data without volume-level checks.

Test signals: usage errors, unsupported build branch, valid inode dump, `-stat` output, failed partition stat, failed `iopen`, failed `fstat`, and stdout short-write/error behavior under injected write failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/vol/gi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/vol/ihandle.c -->
## sources/distributed-fs/openafs/src/vol/ihandle.c

Purpose: implementation of the inode-handle and file-descriptor-handle cache used by the volume package. It centralizes inode identity, descriptor reuse, buffered stream I/O, configurable fsync behavior, and portable low-level I/O wrappers.

Important APIs/types/functions: initialization/configuration functions are `ih_PkgDefaults`, `ih_SetSyncBehavior`, `ih_Initialize`, and `ih_UseLargeCache`. Handle lifecycle functions are `ih_init`, `ih_copy`, `ih_open`, `ih_attachfd`, `fd_close`, `fd_reallyclose`, `ih_reallyclose`, `ih_release`, and `ih_condsync`. Buffered I/O is implemented by `stream_fdopen`, `stream_open`, `stream_read`, `stream_write`, `stream_aseek`, `stream_flush`, and `stream_close`. OS support includes `ih_icreate`, `ih_icreate_init`, `ih_size`, fallback `ih_pread`/`ih_pwrite`, `ih_isunlinked`, `ih_fdsync`, and `fd_blocksize`.

Control flow: `ih_init` hashes `(dev, vid, ino)` and reuses an existing `IHandle_t` or allocates a chunk from the free list. `ih_open` first tries reusable descriptors on the handle, otherwise opens with `OS_IOPEN`, evicting from the global LRU when too many descriptors are open or `EMFILE` occurs. `fd_close` either returns a descriptor to the LRU cache or delegates to `fd_reallyclose`; `fd_reallyclose` closes and returns the descriptor handle to the free list. `ih_reallyclose` handles deferred syncs and closes all cached descriptors for one inode. Streams use positioned I/O and a fixed 2048-byte buffer, with explicit seek/flush needed to switch direction.

State and persistence: global mutable state includes free lists for inode/fd/stream handles, descriptor LRU, `ihashTable`, initialization flag, cache sizes, open descriptor count, global lock, and `vol_io_params`. Persistent effects are file creation, reads/writes/truncates/syncs through OS/namei/inode operations. `IH_SYNC_ONCLOSE` records `ih_synced` and defers fsync until `ih_reallyclose`.

Dependencies: `ihandle.h`, `viceinode.h`, OpenAFS assertions/logging, platform resource limits, pthread locks where enabled, OS open/read/write/seek/sync/stat calls, and NAMEI or inode syscall macros selected by the header.

Integration points: volume, vnode, salvager, and partition code use `IH_*`, `FDH_*`, and `STREAM_*` macros that map here. `listinodes.c` and volume conversion helpers rely on `FDH_PREAD/PWRITE`, `IH_CREATE`, and link-count operations.

Risks: one global lock simplifies correctness but limits concurrency and is temporarily dropped around close/sync operations. Header comments warn that concurrent `IH_OPEN` and `IH_REALLYCLOSE` on the same handle can race semantically. The cache shrinks after `EMFILE`, and descriptor accounting must remain exact. Stream write paths do not retry partial positioned writes. `IH_SYNC_NEVER` trades durability for speed.

Test signals: handle hash reuse/refcounts, chunk allocation, LRU reuse and eviction, `EMFILE` retry path, concurrent open/close stress, `IH_REALLY_CLOSED` behavior with in-use descriptors, sync behavior modes, stream read/write/seek/flush/close, fallback pread/pwrite seek semantics, blocksize/stat failures, and NAMEI versus inode build variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/vol/ihandle.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/vol/ihandle.h -->
## sources/distributed-fs/openafs/src/vol/ihandle.h

Purpose: public abstraction layer for OpenAFS inode/file handling. It hides whether the backing store is traditional inode syscalls, NAMEI files, or NT file handles, and exposes inode handles, descriptor handles, stream handles, cache parameters, lock macros, and portable OS operation macros.

Important APIs/types/functions: `IHandle_t` identifies a stored object by volume id, device, inode, flags, sync state, refcount, and descriptor list. `FdHandle_t` wraps a real fd/HANDLE with status, refcount, parent handle, LRU/free links, and per-ihandle links. `StreamHandle_t` implements simple buffered positioned I/O. Status constants include `FD_HANDLE_AVAIL`, `OPEN`, `INUSE`, and `CLOSING`; stream directions; `IH_SYNC_ALWAYS`, `IH_SYNC_ONCLOSE`, and `IH_SYNC_NEVER`; cache sizing defaults; and `IH_REALLY_CLOSED`. The header declares lifecycle functions and maps public macros such as `IH_INIT`, `IH_OPEN`, `FDH_CLOSE`, `FDH_SYNC`, `FDH_PREAD`, `IH_CREATE`, `IH_INC`, and `IH_DEC` to implementation or platform-specific backends.

Control flow: callers generally allocate/acquire an `IHandle_t`, open it to an `FdHandle_t`, use `FDH_*` operations, then close or really close descriptor handles and release the inode handle. The macros intentionally mutate pointer variables for close/release paths to reduce stale pointer use.

State and persistence: the header defines state layout but not storage. Runtime state is managed by `ihandle.c`. Persistent behavior is backend-dependent: NAMEI paths create/read/write ordinary files and link-count metadata; traditional inode paths invoke inode syscalls; NT paths map to Win32 handle operations.

Dependencies: pthread and OpenAFS lock wrappers, AFSSYSCALLS, NAMEI/NT headers when selected, filesystem large-file feature macros, stat/statfs variants, and platform lock/unlink/path separator APIs.

Integration points: this is a central include for volume, vnode, salvage, list-inodes, and utility code. It also documents an important contract: `IH_REALLYCLOSE` is not safe to race with `IH_OPEN` on the same handle.

Risks: heavy macro indirection makes behavior build-configuration-sensitive. Some macro close/release forms evaluate and null the argument, so callers must pass lvalues. The fixed hash function depends on `IHandle_t` layout assumptions used by the dir package. Cache-size defaults reflect old stdio fd limitations and must be tuned carefully. Platform branches can drift because many are rarely built.

Test signals: compile matrix for NAMEI, non-NAMEI, NT, large-file, positional-I/O, and vector-I/O configurations; macro expansion/link tests for all declared operations; cache parameter defaults; path separator behavior; lock macros under pthread and non-pthread builds; and structure-size/layout assumptions used by dependent code.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/vol/ihandle.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/vol/listinodes.c -->
## sources/distributed-fs/openafs/src/vol/listinodes.c

Purpose: platform-specific inode enumeration and conversion support for traditional inode-based OpenAFS partitions. The primary exported behavior is `ListViceInodes`, which scans a partition, identifies AFS vice inodes, optionally filters them through a judge callback, and writes `ViceInodeInfo` records for salvaging and volume utilities. The file is excluded under NAMEI except for conversion-related guarded code.

Important APIs/types/functions: `ListViceInodes` has multiple mutually exclusive implementations: Linux non-NAMEI stub returning unimplemented, AIX/JFS scanner, SGI/XFS scanner, and generic UFS/HPUX/BSD/Sun scanner. Helpers include `ReadSuper`, `IsBigFilesFileSystem`, `ginode`, XFS-specific `xfs_VerifyInode`, `xfs_RenameFiles`, `xfs_ListViceInodes`, generic `bread`, `convertVolumeInfo`, `UpdateThisVolume`, `getDevName`, and client-side `inode_ConvertROtoRWvolume`.

Control flow: scanners sync and briefly sleep to stabilize on-disk state, open raw devices, validate superblocks, iterate inode tables or XFS directory/attribute namespaces, construct `ViceInodeInfo`, run `judgeInode` when supplied, and write records to `inodeFile` if provided. They fsync and size-check output files before returning. XFS additionally validates/chowns attributes, repairs parent inode/tag metadata, queues renames, and can rename files after directory iteration. `inode_ConvertROtoRWvolume` locks/checks out a RO volume, finds special inodes, creates new RW special inodes, copies or converts content, rewrites the volume disk header, removes the old header, and notifies FSSYNC.

State and persistence: global `partition`, `Testing`, and raw-device fd `pfd` support scanner helpers. Persistent effects include optional inode-list file writes, raw device reads, XFS attribute/chown/rename repairs, special inode creation/decrement during RO-to-RW conversion, volume header creation/destruction, and FSSYNC volume state transitions.

Dependencies: old filesystem headers and disk layouts, `osi_inode`, `viceinode.h`, `volinodes.h`, `ihandle.h`, partition/volume APIs, FSSYNC client APIs, XFS attribute syscalls where enabled, and many platform macros.

Integration points: salvager and volume conversion code use `ListViceInodes` to discover vice inodes. `inode_ConvertROtoRWvolume` bridges raw inode scanning, inode-handle I/O, volume headers, and FSSYNC callback/state notifications.

Risks: this file is high-risk because it reads raw filesystem structures and contains many rarely built legacy branches. Several paths use fixed-size buffers and old-style prototypes. XFS repair code mutates namespace/attributes during listing. Generic scanners rely on superblock consistency checks and old disk layout macros. Partial output write/fsync failures return `-2`, distinct from scan failures. There appears to be a suspicious XFS rename loop condition around finding a new name that merits targeted review in that platform branch.

Test signals: platform compile coverage is essential. Behavioral signals include unimplemented Linux path, superblock validation failures, raw-device open/read failures, force-salvage marker detection, judge callback filtering, inode output size/fsync mismatch, XFS attribute version skew, XFS repair/rename dry-run via `Testing`, generic forced-read recovery, and RO-to-RW conversion rollback/error paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/vol/listinodes.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/vol/namei_map.c -->
## sources/distributed-fs/openafs/src/vol/namei_map.c

Purpose: tiny diagnostic utility that maps a numeric volume id to the flipbase64 directory components used by the NAMEI filesystem layout.

Important APIs/types/functions: `main` parses a single volume id with `strtoul`, calls `int32_to_flipbase64` first on the low byte (`vol & 0xff`) and then on the whole volume id, and prints both resulting components.

Control flow: if no argument is provided, it prints usage and exits with status 1. Otherwise it emits two `Component is ...` lines and exits 0.

State and persistence: no persistent state or file I/O. It only writes to stdout/stderr.

Dependencies: `afs/afsutil.h` for `lb64_string_t` and `int32_to_flipbase64`, plus standard C library parsing and printing.

Integration points: useful for operators/developers inspecting NAMEI partition trees or debugging volume-id-to-path mapping. It mirrors a small slice of logic from NAMEI storage helpers without needing a full fileserver.

Risks: only checks `argc < 2`, ignores extra arguments, and does not validate parse errors or overflow from `strtoul`. Output wording is duplicated for the two different components, so callers must know the first is low-byte and the second is full-volume. It casts through `int64_t` after parsing to `unsigned long`, so behavior depends on platform widths for very large inputs.

Test signals: no-argument usage exit, decimal/hex/octal input forms accepted by base 0 parsing, low-byte component for boundary values, full-volume component for large values, and invalid string parsing behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/vol/namei_map.c -->
