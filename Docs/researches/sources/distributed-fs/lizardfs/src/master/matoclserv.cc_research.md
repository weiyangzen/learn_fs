# sources/distributed-fs/lizardfs/src/master/matoclserv.cc

## Purpose

`matoclserv.cc` is the master-side server for clients, tools, and admin commands. It accepts TCP connections on `MATOCL_LISTEN_*`, registers FUSE mounts and tools, maintains session state, dispatches a large matrix of `CLTOMA`/`LIZ_CLTOMA` requests, calls filesystem/chunkserver/job/lock/admin subsystems, serializes `MATOCL` replies, and participates in reload, shutdown, and master-promotion lifecycle events.

The file is the protocol hub between network clients and master metadata state. It supports legacy MooseFS packet formats, newer LizardFS packet formats, normal FUSE clients, old tools, unauthenticated monitoring commands, and authenticated admin commands.

## Important APIs, Types, And Functions

- `struct session`: persistent client session record. It stores session id, client info string, peer IP, export flags, goal/trash-time limits, UID/GID remapping data, root inode, disconnect/socket counts, operation stats, group-cache entries, and a sorted open-file list.
- `struct matoclserventry`: live TCP connection record. It stores client state, packet read/write state, socket, peer/version, password challenge data, session pointer, admin challenge/task state, delayed chunk operations, and linked-list membership.
- `ClientState`: distinguishes unregistered clients, registered mounts/new tools, old tools, and authenticated admins.
- `AdminTask`: tracks admin requests that need delayed responses, including terminate, reload, save metadata, and checksum recalculation.
- `chunklist`: tracks delayed write/truncate operations waiting for chunkserver status before replying to the client.
- `PacketSerializer`, `MooseFsPacketSerializer`, `LizardFsPacketSerializer`, `LizardFsStdXorPacketSerializer`: compatibility layer for read/write/truncate packet serialization across old MooseFS, normal LizardFS, and older LizardFS clients that cannot consume EC2 chunk parts.
- Public functions from `matoclserv.h`: `matoclserv_stats`, `matoclserv_chunk_status`, open-file add/remove helpers, `matoclserv_sessionsinit`, `matoclserv_networkinit`, `matoclserv_session_unload`, and admin broadcast helpers.

Major internal function families:

- Session persistence: `matoclserv_new_session`, `matoclserv_find_session`, `matoclserv_close_session`, `matoclserv_store_sessions`, `matoclserv_load_sessions`, `matocl_session_check`, `matocl_session_statsmove`, `matocl_session_timedout`.
- Packet queueing and context creation: `matoclserv_createpacket`, `matoclserv_get_context`, `matoclserv_ugid_remap`, `matoclserv_check_group_cache`, `matoclserv_update_credentials`.
- Registration and monitoring: `matoclserv_fuse_register`, chunkserver/session/info/chart/export/status/list handlers, I/O limit status/config, metadata-server status, goals, health, tape servers, defective files, task list/stop.
- FUSE operations: stat/access/lookup/getattr/setattr/truncate/readlink/symlink/mknod/mkdir/unlink/rmdir/rename/link/getdir/open/read/write chunks/repair/check/trash/reserved/xattr/ACL/quota/locks/snapshot/recursive remove/whole-path lookup.
- Admin operations: challenge-response registration, become master, stop without metadata dump, reload, save metadata, checksum recalculation, lock management.
- Network lifecycle: `matoclserv_networkinit`, `matoclserv_desc`, `matoclserv_serve`, `matoclserv_read`, `matoclserv_write`, `matoclserv_reload`, `matoclserv_term`, `matoclserv_canexit`.

## Control Flow

Startup is split into session initialization and network initialization. `matoclserv_sessionsinit()` loads `sessions.mfs` if present, writes an empty sessions file for fresh installs, and clamps `SESSION_SUSTAIN_TIME`. `matoclserv_networkinit()` reads listen config, loads global I/O limits, opens a nonblocking listening socket, registers event-loop callbacks, and calls `matoclserv_become_master()` immediately if this process is already master.

The event loop calls `matoclserv_desc()` to add the listening socket and all active client sockets to the poll vector. `matoclserv_serve()` accepts new connections, initializes `matoclserventry`, reads ready sockets, writes queued packets, sends periodic NOP keepalives, times out inactive clients, and removes killed entries after `matocl_beforedisconnect()` releases per-connection delayed state.

Packet reads follow the same 8-byte header plus payload model as `masterconn.cc`, with `MaxPacketSize` of 1,000,000 bytes. Once a full packet is available, `matoclserv_gotpacket()` dispatches by server role and client state:

- Shadow state only accepts metadata-server status, hostname, and a limited admin set such as registration, become-master, stop, reload, and save-metadata.
- Unregistered/admin state accepts registration, monitoring/tool queries, I/O limit status, admin auth/control, lock-management admin calls, task queries, and similar commands.
- Registered mount state accepts the full FUSE operation set plus selected tool/admin-like status requests.
- Old-tools state accepts a smaller compatibility subset such as read chunk, check, trash time, goal operations, append, directory stats, truncate, repair, snapshot, and extra attributes.

Registration is complex. `matoclserv_fuse_register()` supports no-ACL legacy blobs for old mounts/tools, ACL challenge-response for new sessions, metadata sessions, reconnects, tools registration, and close-session requests. It checks `REJECT_OLD_CLIENTS`, export permissions, root inode resolution, peer IP/dynamic-IP rules, session id existence, version-specific response shape, and enables I/O limit negotiation for sufficiently new clients.

FUSE handlers generally deserialize request fields, validate exact packet length or protocol version, check group-cache availability for cached credential IDs, build an `FsContext` using session root/export/remap data, call a filesystem or chunk subsystem function, then serialize either status or result data. Operation counters in `currentopstats` are updated for common FUSE categories.

Some operations intentionally delay replies. Chunk writes and truncates store `chunklist` entries until `matoclserv_chunk_status()` is called by the chunk layer. Recursive remove, set trash time, set goal, snapshot, locks, admin metadata save, admin checksum recalculation, and termination can also respond later through callbacks or broadcast helpers.

Reload first replies to admins waiting for reload, updates config and session sustain time, reloads I/O limits and broadcasts new configs, then replaces the listening socket if address/port changed.

Shutdown stops accepting new clients, waits until output queues and delayed chunk operations drain, handles the special admin termination response path, then frees connections, sessions, packets, and listen strings.

## State And Persistence Behavior

Session state is persisted to `kSessionsFilename` through `matoclserv_store_sessions()`. The format starts with an `MFSSIGNATURE` session header and supports several historical versions on load. Stored fields include session id, info, peer IP, root inode, flags, goal/trash limits, root and mapall IDs, and per-operation stats. Only sessions with `newsession == 1` are stored.

Open files are tracked per session in sorted linked lists. `matoclserv_insert_openfile()` calls `fs_acquire()` before adding a file; release happens when reserved inode lists are reconciled, when sessions time out, or when sessions unload. `matocl_locks_release()` clears flock and POSIX locks on timeout/release and wakes any newly applied pending lock owners.

Credentials may be cached per session with `GenericLruCache<uint32_t, FsContext::GroupsContainer, 1024>`. Client requests can pass encoded group-cache IDs; handlers reject missing cache IDs with `LIZARDFS_ERROR_GROUPNOTREGISTERED`.

I/O limit state is global to the module: config id, refresh/accumulation intervals, subsystem name, and `IoLimitsDatabase`. Reloading increments the config id and broadcasts the new config to connected clients that negotiated I/O limits.

Connection state is not persistent. Live connections own packet queues, input payload buffers, delayed chunk operations, admin challenges, and admin task markers. The code uses manual allocation for packets, sessions' `info`, open-file nodes, and delayed chunk nodes, with some newer state held by `std::unique_ptr` or STL containers.

## Dependencies And Integration Points

The module depends on common config, charts, packet serialization, event loop, sockets, statistics, user groups, goals, ACLs, I/O limits, metadata constants, and logging. It depends heavily on master subsystems:

- `filesystem.h`, `filesystem_operations.h`, `filesystem_periodic.h`, and `filesystem_snapshot.h` for metadata operations.
- `chunks.h`, `chunkserver_db.h`, and chunk location/type helpers for chunk read/write/truncate and chunkserver listing.
- `datacachemgr.h` for data-cache access/modify/open decisions.
- `exports.h` for mount authorization.
- `matocsserv.h`, `matomlserv.h`, `masterconn.h`, and metadata-server personality for cluster and status integration.
- `settrashtime_task.h`, job/task APIs, and lock APIs for asynchronous work.
- Protocol namespaces `cltoma` and `matocl` plus legacy MooseFS serialization for wire compatibility.

`masterconn_is_connected()` is used to answer shadow metadata-server status. Promotion hooks call `matoclserv_become_master()` so a promoted shadow starts master-only session timers and startup gating.

## Risks And Edge Cases

- The file is a large manual dispatcher with many protocol versions. Adding or changing packet formats requires updates in deserialization, reply serialization, dispatch state, and client-state permissions.
- Many handlers enforce exact packet lengths manually; integer length arithmetic involving variable string lengths is a key fuzzing surface.
- The read loop processes only one completed packet per call after dispatch, while write drains until blocked or watchdog expiry. This affects fairness and should be considered in load tests.
- `matoclserv_serve()` kills clients after 10 seconds without reads when not exiting, while also sending NOPs every 2 seconds to most clients. Slow or half-open clients exercise this path.
- Manual memory management is mixed with C++ containers. Packet queues, open-file lists, sessions, and delayed chunk lists need leak/double-free coverage on disconnect, shutdown, and error paths.
- Delayed replies depend on finding the original session/connection by session id. If clients disconnect before callbacks fire, wake-up functions silently drop replies.
- Admin control is challenge-response MD5 over configured `ADMIN_PASSWORD`; empty password disables admin access. Admin-only handlers kill non-admin connections rather than returning ordinary permission errors in several places.
- Compatibility serializers deliberately hide unsupported EC parts from older clients. Read/write behavior for EC/XOR chunks depends on client packet type and version.
- Session persistence has several legacy format branches; corrupt or partial sessions files can prevent session restoration and require clients to remount.
- Some readonly or permission checks occur in filesystem functions, while others are explicit in protocol handlers, such as write-end lock id and readonly checks.

## Test Signals

High-value tests include registration matrix coverage for old no-ACL clients, ACL challenge sessions, metadata sessions, reconnects, tools, dynamic IP, and close-session. Protocol fuzzing should target packet lengths, variable string lengths, bad packet versions, oversized packets, and missing group-cache IDs.

Integration tests should cover session file load/store across legacy headers, open-file acquire/release and timeout, I/O limit reload/broadcast/request behavior, master versus shadow dispatch restrictions, admin authentication and delayed admin responses, listener reload, graceful shutdown drain, and promotion startup gating.

FUSE operation tests should cover representative metadata reads, metadata mutations, chunk read/write/truncate delayed flows, EC compatibility filtering, ACL/quota/xattr paths, lock wait/wakeup/interrupt/admin-unlock flows, async snapshot/recursive remove/setgoal/settrashtime callbacks, and trash/reserved pagination. Fault tests should disconnect clients while delayed operations are pending and verify cleanup.
