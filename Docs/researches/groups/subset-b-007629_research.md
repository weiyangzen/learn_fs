# Research Group: subset-b-007629

This grouped report covers the LizardFS master-side master/shadow and client protocol entry points assigned to `subset-b-007629`. Each section preserves its source path for reconciliation into the final source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/master/masterconn.cc -->
# sources/distributed-fs/lizardfs/src/master/masterconn.cc

## Purpose

`masterconn.cc` owns the outbound connection from a metalogger or shadow master to the active master. It registers the process with the master, receives metadata changelog updates, downloads full metadata/changelog/session images when needed, and integrates with the event loop for reconnects, packet I/O, reloads, shutdown, and shadow promotion cleanup.

The file is compiled in two distinct modes. With `METALOGGER`, it behaves as a metalogger client that stores metadata and changelog files locally. Without `METALOGGER`, it is the shadow-master replication client and applies changelog entries into in-memory filesystem state with `restore()`.

## Important APIs, Types, And Functions

- `struct masterconn`: singleton connection state, including socket/mode, packet buffers, outbound packet queue, resolved master address, download state, temp metadata fd, file offsets, event-loop handles, master version, replication state, and changelog-apply-error retry timer.
- `MasterConnectionState`: high-level replication state: none, synchronized, downloading, dump request pending, or limbo after the master refuses/fails to dump metadata.
- `masterconn_init()`: configures `MASTER_HOST`, `MASTER_PORT`, `BIND_HOST`, timeouts, metadata backup count, optional metalogger changelog state, creates the singleton, starts the initial connection, and registers event-loop callbacks.
- `masterconn_is_connected()`: reports true only after the socket is in header/data mode and shadow registration has returned a nonzero master version.
- `masterconn_sendregister()`, `masterconn_registered()`: build and process registration messages. Shadow registrations include local metadata version when synchronized; metaloggers register with package version and last changelog version.
- `masterconn_metachanges_log()`: validates and applies `MATOML_METACHANGES_LOG`, detects changelog gaps, restores entries into shadow memory when synchronized, appends to changelog, and advances `lastlogversion`.
- `masterconn_download_init()`, `masterconn_download_start()`, `masterconn_download_data()`, `masterconn_download_next()`, `masterconn_download_end()`: implement the metadata/changelog/session download pipeline with offsets, CRC checks, temp files, fsync, retries, renames, and shadow `fs_loadall()` after a complete set.
- `masterconn_handle_changelog_apply_error()`, `masterconn_request_metadata_dump()`, `masterconn_changelog_apply_error()`: recover from malformed or inconsistent changelogs by forcing a fresh download for old masters or asking newer masters to prepare an up-to-date metadata image.
- `masterconn_read()`, `masterconn_write()`, `masterconn_desc()`, `masterconn_serve()`, `masterconn_reconnect()`: nonblocking packet I/O and event-loop integration.
- `masterconn_reload()`, `masterconn_become_master()`, `masterconn_term()`: config reload, promotion cleanup, and destruction.

## Control Flow

Initialization is gated by personality in non-metalogger builds: only shadow masters start this module. The module reads config, optionally initializes metalogger changelog state, creates `masterconnsingleton`, attempts `masterconn_initconnect()`, and registers poll/time/reload/exit callbacks.

Connection setup resolves bind and master addresses, creates a nonblocking TCP socket, optionally binds to `BIND_HOST`, and either completes immediately or enters `CONNECTING`. `masterconn_connecttest()` finalizes async connect. `masterconn_connected()` switches to header-read mode, initializes packet queues, sends registration, and starts a metadata download if `lastlogversion` is zero.

Packet reads use a two-state framing loop: read 8-byte header, allocate a payload if the declared size is nonzero and below `MaxPacketSize`, then dispatch by type in `masterconn_gotpacket()`. Unknown packet types and deserialization failures kill the session. Writes drain a linked list of packet buffers and update byte counters.

Metadata synchronization proceeds as a fixed sequence: metadata image, first changelog, second changelog, sessions. Each `DOWNLOAD_DATA` reply is checked for expected offset, bounded length, file-size limits, write result, CRC, and fsync success. On completion, temp files are renamed into their live names. For shadow masters, after sessions are downloaded the module loads all downloaded state with `fs_loadall()`, sets `lastlogversion` to filesystem version minus one, and enters synchronized state.

Changelog streaming is linear. If the incoming version is not `lastlogversion + 1`, the module considers changes lost and requests recovery. Shadow masters apply entries through `restore()` only while synchronized; metaloggers primarily persist the changelog.

The periodic reconnect hook starts a new connection while free and running. If in `kLimbo`, it periodically resends the metadata dump request when the timer expires.

## State And Persistence Behavior

Persistent effects are centered on metadata, changelog, and sessions files. File names are selected by build mode: normal master metadata names for shadow masters, `_ml` names for metaloggers. Downloads write `*.tmp` files first, then rename into live paths. Metadata downloads are verified with `metadataGetVersion()`, and successful metadata replacement rotates old copies according to `BACK_META_KEEP_PREVIOUS`.

`lastlogversion` is the replication cursor. Metaloggers recover it by scanning the tail of the changelog file and truncating garbage after the last complete newline if needed. Shadow masters update it from loaded filesystem metadata and every accepted changelog entry.

In-memory connection state is singleton-based and manually owns packet buffers, file descriptors, event-loop handles, address resolution cache, and temp download progress. `masterconn_beforeclose()` closes the metadata fd and unlinks temp files on disconnect.

## Dependencies And Integration Points

This module depends on the common event loop, TCP helpers, config, datapack encoding, CRC, metadata validation, file rotation, slogger, watchdogs, and protocol serializers from `protocol/matoml.h`, `protocol/mltoma.h`, and `protocol/MFSCommunication.h`.

For shadow masters it integrates with `filesystem.h`, `restore.h`, and `personality.h`: it unloads/loads metadata, applies changelog entries, erases lockfile messages before download, and unregisters itself when promoted to master. It also sends the client-listen port to newer masters via `mltoma::matoclport` so the active master can know the shadow's client endpoint.

For metaloggers it integrates with changelog initialization, changelog migration, forced log rotation, and periodic metadata downloads.

## Risks And Edge Cases

- Packet parsing is manual and stateful. Header/payload size mismatches, payloads above `MaxPacketSize`, and unknown packet types correctly kill the session, but malformed inputs exercise raw allocation/free paths.
- Download retry logic retries failed writes, CRC mismatches, and fsync failures up to five times, but the same offset is requested again. Tests should cover partial writes and repeated bad chunks.
- `fsync()` is called after each downloaded block, which favors safety but can make large metadata downloads expensive.
- Changelog gap handling depends on master version. Old masters force local metadata discard immediately; newer masters require the dump-request/limbo flow.
- The singleton/event-loop lifecycle is delicate during promotion. `masterconn_become_master()` unregisters selected time hooks and calls `masterconn_term()`.
- Several paths are build-mode dependent under `METALOGGER`; behavior should be tested in both build configurations.
- `masterconn_is_connected()` is stricter than socket connected: it also requires a successful registration response.

## Test Signals

Useful tests include registration against old and new master protocol versions, shadow metadata-version mismatch forcing a download, changelog gap recovery, malformed changelog restore error paths, full metadata/changelog/session download with CRC and offset checks, temp-file cleanup on disconnect, config reload changing master address, NOP keepalive timeout behavior, and promotion from shadow to master. Fault injection around `write`, `pwrite`, `fsync`, `rename`, and metadata validation would exercise the highest-risk branches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/master/masterconn.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/master/masterconn.h -->
# sources/distributed-fs/lizardfs/src/master/masterconn.h

## Purpose

`masterconn.h` is the small public interface for the master-to-master/metalogger connection module implemented in `masterconn.cc`. It exposes initialization and a connection-status query to other master components while hiding the singleton connection internals.

## Important APIs

- `int masterconn_init(void)`: starts the module when applicable. In non-metalogger builds it is a no-op unless the metadata server personality is shadow. In active mode it reads config, opens the master connection, and registers event-loop hooks.
- `bool masterconn_is_connected()`: returns whether the shadow/metalogger connection is registered and usable, not merely whether the socket exists.

The header includes `common/platform.h`, `<inttypes.h>`, and `<stdio.h>`. The latter two are not needed by the declarations themselves but are consistent with older C-style headers in this codebase.

## Control Flow And Integration

Other master modules call `masterconn_init()` during startup to attach the replication/metalogger client to the event loop. `matoclserv.cc` calls `masterconn_is_connected()` when answering metadata-server status requests so clients/admin tools can distinguish shadow-connected from shadow-disconnected states.

## State And Persistence Behavior

The header declares no state. All connection, packet, metadata-download, and changelog cursor state is private to `masterconn.cc`.

## Dependencies And Risks

The interface is intentionally narrow. The main risk is semantic: callers must understand that `masterconn_is_connected()` reports successful protocol registration, not just TCP connectivity. Tests that mock or drive status reporting should account for this distinction.

## Test Signals

Compile-level tests should ensure both `METALOGGER` and normal master builds include this header cleanly. Integration tests should verify that status consumers report disconnected before registration and connected only after the master version is known.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/master/masterconn.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/master/matoclserv.cc -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/master/matoclserv.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/master/matoclserv.h -->
# sources/distributed-fs/lizardfs/src/master/matoclserv.h

## Purpose

`matoclserv.h` declares the public interface for the master-to-client service implemented by `matoclserv.cc`. It exposes statistics, chunk-operation callbacks, session/open-file helpers, startup/shutdown hooks, and admin broadcast notifications used by other master subsystems.

## Important APIs

- `void matoclserv_stats(uint64_t stats[5])`: returns and resets packet/byte counters. The implementation fills received packets, sent packets, received bytes, and sent bytes; the fifth array slot is currently unused by the implementation.
- `void matoclserv_chunk_status(uint64_t chunkid, uint8_t status)`: callback from the chunk layer when a delayed write/truncate-related chunk operation finishes. It finds the waiting connection and serializes the delayed client response.
- `void matoclserv_add_open_file(uint32_t sessionid, uint32_t inode)`: records an open inode for a session, creating a session entry for old filesystem-created sessions if necessary.
- `void matoclserv_remove_open_file(uint32_t sessionid, uint32_t inode)`: removes an inode from a session open-file list and logs corruption if the session is absent.
- `int matoclserv_sessionsinit(void)`: loads or initializes persisted client session state and session timeout configuration.
- `int matoclserv_networkinit(void)`: initializes the listening socket, reloadable configuration, I/O limits, and event-loop callbacks.
- `void matoclserv_session_unload(void)`: frees all session records and their open-file/info allocations.
- `void matoclserv_broadcast_metadata_saved(uint8_t status)`: sends delayed admin save-metadata responses to clients waiting for completion.
- `void matoclserv_broadcast_metadata_checksum_recalculated(uint8_t status)`: sends delayed admin checksum-recalculation responses.

Several older notify declarations are left commented out, suggesting previous or planned client notification hooks for attribute/link/unlink/parent changes that are not part of the active interface.

## Control Flow And Integration

Startup code calls `matoclserv_sessionsinit()` before or alongside master metadata startup, then `matoclserv_networkinit()` to expose the client/admin port. Chunkserver or filesystem code calls `matoclserv_chunk_status()` after operations that were delayed in `matoclserv.cc`. Filesystem/session code can call the open-file helpers to keep persisted sessions aligned with acquired inodes.

Metadata dumping/checksum code calls the broadcast helpers when background admin-requested operations finish. Shutdown code can call `matoclserv_session_unload()` through the event-loop destructor path, though `matoclserv_term()` also invokes it.

## State And Persistence Behavior

The header declares no concrete state, but the APIs expose stateful behavior. Session initialization and unload manage the global session list and the sessions file. Chunk status and open-file helpers mutate live sessions/connections in `matoclserv.cc`. Broadcast helpers scan live client connections for matching admin tasks.

## Dependencies And Risks

The header depends only on `common/platform.h` and integer types, keeping callers decoupled from the large protocol implementation. The main API risk is callback ordering: `matoclserv_chunk_status()` and broadcast functions assume the network module is initialized and live connection/session lists are valid. `matoclserv_stats()` requires callers to pass an array with at least five entries even though only four counters are populated.

## Test Signals

Compile tests should include this header from chunk, filesystem, and startup modules. Integration tests should verify chunk-status callbacks after client disconnect, stats reset behavior, open-file add/remove on restored and missing sessions, session init with absent/corrupt sessions files, and admin broadcast delivery only to clients waiting for the corresponding task.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/master/matoclserv.h -->
