# sources/distributed-fs/moosefs/mfsmaster/matoclserv.c

## Purpose
`matoclserv.c` implements the MooseFS master service that accepts client, mount, and admin-tool connections on the master-client TCP port. It owns the client socket lifecycle, packet framing, protocol dispatch, FUSE request handling, session registration/reconnect/close flows, metadata and chunk operation replies, open-file and lock notifications, administrative queries, storage-class and pattern administration, trash/sustained-file commands, per-interval traffic statistics, and reload/shutdown integration with the master event loop.

The file is the protocol adapter between raw `CLTOMA_*`/`ANTOAN_*`/`MATOCL_*` messages from `MFSCommunication.h` and the master subsystems that actually own durable state: sessions, exports, filesystem metadata, chunks, chunkserver database, open-file tables, locks, storage classes, patterns, charts, metadata logs, missing-chunk logs, and data-cache tracking.

## Important Types And State
The central connection type is the private `matoclserventry`. Each entry stores registration state, connection mode (`KILL`, `DATA`, `FINISH`), socket and poll index, last read/write times, input framing state, queued input packets, queued output packets, negotiated client version and attribute-record size, peer IP/string form, timeout, working flags, authentication challenge and password digest, export path and client info strings retained for reload/session changes, session pointer, and linked-list membership under `matoclservhead`.

`out_packetstruct` and `in_packetstruct` are heap-allocated linked queue nodes. Outbound packets include an 8-byte type/length header written by `matoclserv_create_packet()`, then payload bytes filled by handlers. Inbound packets are assembled by `matoclserv_read()` into complete `in_packetstruct` nodes and later consumed by `matoclserv_parse()`.

Chunk-related asynchronous state is split into two hash tables keyed by low eight bits of `chunkid`: `lwchunkshashhead`/`lwchunkshashtail` for lock/busy waits and `swchunkshash` for status waits. `lwchunks` remembers deferred read, write, or truncate requests that hit `MFS_ERROR_LOCKED` or `MFS_ERROR_CHUNKBUSY`; `swchunks` remembers write/create/truncate operations waiting for a later chunk status callback. These tables hold client pointers, message ids, inode/chunk indexes, credentials or flags needed to retry/finish, and must be cleaned on disconnect.

Configuration and service globals include `ListenHost`, `ListenPort`, resolved listen address, `DefaultTimeout`, `ForceTimeout`, `RestrictIncompatibleClientVersions`, `InstanceName`, and a generated `master_processid` sent to newer clients. Statistics counters track packets/bytes received and sent, mount-reported IO counters, and lock request count; `matoclserv_stats()` copies them into a 12-slot array and resets them.

The file also uses static reusable buffers in `matoclserv_read()`, `matoclserv_gid_storage()`, `matoclserv_mass_resolve_paths()`, `matoclserv_fuse_sustained_inodes()`, and `matoclserv_fuse_amtime_inodes()`. This is appropriate for the single-threaded event-loop model but is not reentrant.

## Main APIs And Function Families
The public functions exported through `matoclserv.h` are:

- `matoclserv_init()`, `matoclserv_close_lsock()`, `matoclserv_disconnect_all()`, and `matoclserv_no_more_pending_jobs()` for service lifecycle and master orchestration.
- `matoclserv_stats()` and `matoclserv_get_min_cl_version()` for observability/compatibility checks by other master modules.
- `matoclserv_chunk_unlocked()` and `matoclserv_chunk_status()` for chunk subsystem callbacks into deferred client operations.
- `matoclserv_fuse_flock_wake_up()` and `matoclserv_fuse_posix_lock_wake_up()` for lock subsystem callbacks.
- `matoclserv_fuse_invalidate_chunk_cache()` for broadcasting cache invalidation to connected mounts.

Connection and event-loop APIs are private but critical: `matoclserv_desc()` contributes the listen socket and active client sockets to the global poll array; `matoclserv_serve()` accepts new sockets, reads, parses, writes, sends idle NOP keepalives, enforces timeouts, and removes killed entries; `matoclserv_keep_alive()` performs a lighter read/write/keepalive pass when called outside normal polling; `matoclserv_term()` frees sockets, queues, deferred chunk records, static helper buffers, and config strings.

Registration is handled by `matoclserv_fuse_register()`. It accepts only the ACL register blob and supports random challenge retrieval, new normal sessions, new metadata sessions, reconnects, and close-session requests. It negotiates client version/attribute size, checks storage-class erasure-coding compatibility against client version, validates exports/passwords, resolves mount root inode for normal sessions, creates/changes/reconnects `sessions` records, attaches the connection to the session, and emits version-specific response layouts.

General admin/query handlers include chunkserver list/commands, session list/remove, charts and chart data, monotonic data, version/config/config-file queries, module info, open files, acquired locks, mass path resolution, storage-class info/list, missing chunk data, node info, full directory data, all-node attribute updates, global info, memory info, filesystem/chunk test info, chunk matrix, quota/export info, metadata log list, and instance name.

FUSE metadata and data handlers cover statfs, access, lookup/path lookup, getattr/setattr, truncate, readlink/symlink, mknod/mkdir/create, unlink/rmdir/rename/link, readdir/full-directory data, open, read/write chunk, write chunk end, flock/POSIX locks, repair/check, trash retention, storage class get/set, extended attributes, parents/paths, xattrs, POSIX ACLs, append-slice, snapshot, quota control, archive control, directory stats, trash/detached/sustained metadata, undelete, purge, and trash path operations.

Storage policy administration is handled by `matoclserv_sclass_create()`, `matoclserv_sclass_change()`, `matoclserv_sclass_delete()`, `matoclserv_sclass_duplicate()`, `matoclserv_sclass_rename()`, and `matoclserv_sclass_list()`. Pattern administration is handled by `matoclserv_pattern_add()`, `matoclserv_pattern_delete()`, `matoclserv_pattern_list()`, and `matoclserv_pattern_info()`. Mutating storage-class and pattern operations require `SESFLAG_ADMIN`.

## Control Flow
Initialization calls `matoclserv_reload_common()` to load instance name and timeout policy, reads listen host/port from `MATOCL_*` settings with deprecated `MATOCU_*` fallback, creates a nonblocking TCP listen socket, resolves/binds/listens, registers poll, keepalive, reload, destructor, periodic waiting-op timeout, and force-timeout broadcast callbacks with `main_*`, then returns to the master event loop.

For socket input, `matoclserv_read()` accumulates bytes into a growable static buffer, advances each connection's two-stage frame parser (8-byte header, then payload), rejects payloads larger than `CLTOMA_MAXPACKETSIZE`, allocates complete inbound packet nodes, and appends them to the connection input queue. End-of-stream, poll errors, and real read errors set `input_end`, which becomes `KILL` after queued packets are consumed.

`matoclserv_parse()` processes queued packets only while the connection remains `DATA` and uses a 10 ms time budget per pass to avoid monopolizing the master loop. `matoclserv_gotpacket()` is the main dispatch table. Before registration, it allows version/register and a limited set of unauthenticated monitor/admin query packets; after registration, it requires `sesdata` and enables the full FUSE/admin protocol surface. Unknown packets log a warning and kill the connection.

Outbound flow starts in handlers calling `matoclserv_create_packet()`. The packet is appended to the connection output queue and later drained by `matoclserv_write()`, using `writev()` when available or single `write()` calls otherwise. Sent packet and byte statistics are updated as packet nodes are fully drained. Idle connections receive an `ANTOAN_NOP` packet every second when no output is pending.

FUSE handlers follow a recurring parse/check/delegate/pack pattern. They validate exact packet sizes and variable-length counts, decode ids/names/paths/credentials/flags with `datapack` helpers, enforce `MFS_GIDS_MAX`, remap user/group ids through `sessions_ugid_remap()`, consult session flags and disable masks, call an owning subsystem such as `fs_*`, `chunk_*`, `sclass_*`, `patterns_*`, `of_*`, `flock_*`, or `posix_*`, then pack either a status byte or version-specific success payload. Many successful filesystem operations increment per-session operation stats.

Read/write/truncate chunk operations are asynchronous when the chunk is locked, busy, or requires a background chunk operation. `matoclserv_fuse_write_chunk_common()`, `matoclserv_fuse_read_chunk_common()`, and `matoclserv_fuse_truncate_common()` either complete immediately, enqueue `lwchunks` for retry after `matoclserv_chunk_unlocked()`, or enqueue `swchunks` for completion by `matoclserv_chunk_status()`. `matoclserv_timeout_waiting_ops()` replies with the remembered lock/busy status after 30 seconds. Disconnect cleanup rolls back pending status-wait writes/truncates through `fs_rollback()`.

Cache and multi-client coherence are handled by open-file checks. When chunks or file length change, `matoclserv_fuse_chunk_has_changed()` and `matoclserv_fuse_fleng_has_changed()` walk all other registered clients and notify those with the inode open, using protocol additions available from client version 3.0.74 and adding invalidated byte ranges for newer clients. `matoclserv_fuse_invalidate_chunk_cache()` broadcasts a whole-cache invalidation packet to clients new enough to understand it.

Reload first calls `matoclserv_reload_sessions()`, which reloads exports and kills registered connections whose session export checksum no longer matches. It then reloads common config and, if listen address changed, attempts to create and bind a replacement socket before swapping it in. Failures keep the old listen socket and old config strings.

## State And Persistence Behavior
This file persists no durable state directly. Durable metadata changes are delegated to filesystem, chunk, session, export, storage-class, pattern, quota, trash, and metadata modules. It does, however, maintain live in-memory protocol state that affects correctness: attached sessions, pending output replies, input packet queues, open delayed chunk operations, lock wait callbacks, per-connection registration/authentication state, and data-cache notifications.

Session state is semipersistent via the `sessions` subsystem. Registration can create a new session, change an existing session after export changes, reconnect to a session id, or close a session. Connections store `path`, `info`, password state, and `sesdata` so reloads and disconnects can update session attachment and exported policy correctly.

Pending chunk operations are volatile but can affect filesystem consistency. On normal completion, the chunk subsystem calls back with status and this file finalizes replies and metadata changes. On disconnect before completion, `matoclserv_beforedisconnect()` rolls back status-wait chunk operations and drops lock waiters. On service termination, pending `swchunks` are freed without the rollback call active in disconnect cleanup; the rollback line in `matoclserv_term()` is commented out, so termination semantics depend on broader master shutdown ordering.

The service's observed counters are reset on read by `matoclserv_stats()`. Static temporary buffers are retained across requests for performance and freed only via `matoclserv_read(NULL, 0.0)` and `matoclserv_gid_storage(0)` during termination.

## Dependencies And Integration Points
Protocol constants and packet types come from `MFSCommunication.h`; integer packing is through `datapack.h`. Socket operations use the local `sockets.h` wrappers (`tcpsocket`, `tcpaccept`, `tcpnonblock`, `tcpnodelay`, `tcpreuseaddr`, `tcpresolve`, `tcpnumlisten`, `tcpclose`, `tcpsetacceptfilter`, `tcpgetpeer`) rather than direct POSIX calls except for read/write/writev/close.

Core subsystem dependencies include `sessions`, `exports`, `filesystem`, `chunks`, `csdb`, `matocsserv`, `matomlserv`, `openfiles`, `flocklocks`, `posixlocks`, `metadata`, `storageclass`, `patterns`, `datacachemgr`, `charts`, `chartsdata`, `missinglog`, `iptosesid`, `multilan`, `cfg`, `main`, logging/assert/allocation utilities, and monotonic clock helpers. This file is one of the densest integration points in the MooseFS master because it translates network requests into nearly every metadata-plane subsystem.

`main_*` registration makes this module part of the master process lifecycle. `matoclserv_chunk_unlocked()` and `matoclserv_chunk_status()` are integration hooks expected by the chunk layer. Lock wake-up functions are callbacks expected by flock/POSIX lock modules. The exported `matoclserv_get_min_cl_version()` lets other code decide whether connected clients can understand a feature.

## Compatibility Concerns
Protocol compatibility dominates the implementation. Response sizes, status mappings, attribute record sizes, extra fields, storage-class encodings, EC split handling, append-only/direct-mode/cache flags, quota grace-period fields, master process id, and chunkserver location encodings all vary by client version. The registration path explicitly rejects or warns on clients too old for configured erasure-coding features, controlled by `RESTRICT_INCOMPATIBLE_CLIENT_VERSIONS`.

Several handlers include legacy fallbacks for very old clients: one-group-id packet formats, renamed/deprecated listen config, old `MATOCU_*` options, old storage-class mask encodings, path-to-session patches via `iptosesid`, old truncate flag behavior, old xattr packet ordering, and old `ENOENT_NOCACHE` downgrading.

## Risks
The largest risk is protocol drift: almost every handler has exact byte-size checks and many version-specific packet shapes. A missing version branch or wrong payload size can disconnect clients, corrupt parsing, or make old mounts misinterpret replies.

The asynchronous chunk tables hold raw `matoclserventry *` pointers and delayed credential/operation data. Correct cleanup in `matoclserv_beforedisconnect()` is essential to avoid use-after-free or stale replies. Timeout paths reply with the originally remembered lock/busy status, so they need to stay consistent with chunk-layer behavior.

Memory ownership is manual and widespread. Most packet buffers are short-lived queue nodes, but static scratch buffers grow to the largest request seen and remain allocated until shutdown. Any future threading would be unsafe without redesigning static buffers and global lists.

Security-sensitive behavior includes export/password authentication, root/user/group remapping, admin-only storage policy operations, session reconnect validation, dynamic-IP sessions, and disable masks. Because some information and control packets are accepted before registration, the unauthenticated dispatch list should remain intentionally narrow and reviewed when adding new cases.

Packet length validation is generally strict, but the file contains many variable-length calculations. Integer overflows in `length` arithmetic, large group/name/path counts, or mismatched const-size calculations are the main parser-risk areas. The code checks many maximums (`MFS_PATH_MAX`, `MFS_GIDS_MAX`, `MFS_XATTR_SIZE_MAX`, `MaxPacketSize`) but changes to constants or packet versions should be fuzzed.

Operationally, `ForceTimeout` broadcasts can change client behavior at runtime, reload kills sessions when export checksums change, and listen socket reload swaps sockets only after successful bind/listen. These are intended but can surprise long-lived mounts.

## Test Signals
High-value test signals include protocol round trips for representative client versions: pre-2.0 xattr formats, 3.x attr-size transitions, 4.x EC split support, 4.40 master process id, 4.48 write invalidation ranges, and 4.51 quota fields. Registration tests should cover random challenge, password/no-password/bad-password exports, new session, metadata session, reconnect, close-session, wrong meta id, dynamic-IP restrictions, and EC compatibility restrictions.

Filesystem operation tests should cover every major FUSE family under normal, readonly, and disable-mask sessions: lookup/open/create/read/write/truncate/readdir/rename/unlink/xattr/facl/quota/snapshot/trash. Multi-client tests should verify chunk/file-length change notifications only reach clients with the inode open and that data-cache manager state changes on open, access, modify, and invalidation.

Async chunk tests should force `MFS_ERROR_LOCKED`, `MFS_ERROR_CHUNKBUSY`, delayed write/truncate status, successful chunk status, error status with rollback, timeout after `CHUNK_WAIT_TIMEOUT`, and disconnect while pending. Lock tests should cover immediate and waiting flock/POSIX lock responses plus disconnect cleanup.

Service-loop tests should include fragmented packet headers/payloads, multiple packets in one read, packet too large, idle NOP writes, read/write errors, FINISH close after close-session response, timeout disconnects, listen address reload success/failure, and destructor cleanup under pending queues. Fuzzing packet lengths against `matoclserv_gotpacket()` handlers would be especially useful because the parsing surface is large and security-sensitive.
