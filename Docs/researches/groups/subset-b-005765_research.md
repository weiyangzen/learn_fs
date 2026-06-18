# Research Report: subset-b-005765

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/server/smb_common.c -->
## sources/distributed-fs/ceph-client/fs/smb/server/smb_common.c

Purpose: implements ksmbd's common SMB negotiation, request validation, SMB1-negotiation shim, short-name generation, share-mode conflict checks, per-request credential override, and generic desired-access mapping. It is the protocol-selection glue used before SMB2/3 command handlers take over.

Important APIs and functions: exported entry points include `ksmbd_min_protocol`, `ksmbd_max_protocol`, `ksmbd_get_protocol_string`, `ksmbd_lookup_protocol_idx`, `ksmbd_verify_smb_message`, `ksmbd_smb_request`, `ksmbd_lookup_dialect_by_id`, `ksmbd_init_smb_server`, `ksmbd_populate_dot_dotdot_entries`, `ksmbd_extract_shortname`, `ksmbd_smb_negotiate_common`, `ksmbd_smb_check_shared_mode`, `__ksmbd_override_fsids`, `ksmbd_override_fsids`, `ksmbd_revert_fsids`, `is_asterisk`, and `smb_map_generic_desired_access`. Internal dialect tables describe SMB 2.1, wildcard SMB2, SMB 3.0, 3.02, and 3.1.1.

Control flow: incoming data is first checked by `ksmbd_smb_request` for RFC1002 framing and SMB1/SMB2/transform signatures, rejecting unsupported compression transforms. `ksmbd_verify_smb_message` validates SMB2 with `ksmbd_smb2_check_message` or permits only SMB1 negotiate. Negotiation decodes either SMB2 dialect ids or SMB1 dialect strings, filters them through `server_conf.min_protocol/max_protocol`, and upgrades SMB1 negotiate to SMB2 server ops when the selected dialect is SMB2. Directory enumeration helpers synthesize `.` and `..` entries before normal readdir output, while share-mode checks scan the inode's open-file list to enforce Windows sharing semantics.

State and persistence behavior: this file mutates per-connection protocol state (`conn->dialect`, `conn->ops`, `conn->vals`, `conn->cmds`, outstanding credits), per-open sharing state through `ksmbd_file` fields, and per-work credential state through `work->saved_cred`. Credential overrides build temporary kernel creds from the authenticated ksmbd user plus share `force_uid/force_gid`, install supplemental groups, and must be reverted after VFS work. No on-disk state is stored here.

Dependencies and integration points: depends on ksmbd global server config, SMB1/SMB2 common headers, SMB2 negotiation handlers, connection/work/session/share management, VFS directory attribute fill, NLS Unicode conversion, file-cache stream detection, and Linux credential/group APIs. It is called from the transport connection loop, SMB2 create/open paths, directory query paths, and VFS wrappers that need user fsids.

Risks: dialect parsing is wire-input-facing and must keep size checks ahead of flexible-array access. `next_dialect` relies on NUL-terminated SMB1 dialect strings inside the declared byte count. Credential override leaks or missing reverts would execute unrelated kernel work under client fsids. Share-mode checks are concurrency-sensitive because they walk the inode open list under `m_lock` and have special handling for alternate streams and attribute-only opens.

Test signals: SMB1 negotiate with SMB2 dialect upgrade, SMB2 negotiate with min/max protocol bounds, malformed dialect counts/byte counts, compression-transform rejection, dot/dotdot directory enumeration with single-entry queries, 8.3 short-name output, share-mode deny-read/write/delete combinations, forced share uid/gid, supplemental group propagation, and generic access mask expansion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/server/smb_common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/server/smb_common.h -->
## sources/distributed-fs/ceph-client/fs/smb/server/smb_common.h

Purpose: declares common SMB server constants, wire helper structs, protocol-version operation tables, and cross-module helpers shared by ksmbd negotiation, command dispatch, VFS access checks, and directory response formatting.

Important APIs and types: defines protocol indexes (`SMB1_PROT` through `SMB311_PROT`, `BAD_PROT`), open disposition response constants, generic/read/write/execute/all access bit expansions, SMB1 negotiate flags, `struct smb_negotiate_rsp`, `struct fs_extended_info`, `struct object_id_info`, directory info wire structs, `struct smb_version_ops`, and `struct smb_version_cmds`. It declares negotiation, dialect lookup, message validation, short-name, share-mode, credential override, server-side-copy limit, and generic access mapping functions. `smb_get_msg` strips the four-byte RFC1002 header.

Control flow: the header has no active control flow, but `smb_version_ops` is the dispatch contract installed on `struct ksmbd_conn`; command processing calls its callbacks for command id extraction, response allocation/header initialization, session/tcon lookup, signing, encryption, and transform handling. Access-mask macros are consumed before permission and share-mode checks.

State and persistence behavior: all state named here is runtime state owned by connections, sessions, work items, files, or VFS objects. The packed structs describe wire or metadata layouts but are not themselves persistent storage in this header.

Dependencies and integration points: includes ksmbd global headers plus SMB1, SMB2, and FSCC protocol definitions. It is central to `smb_common.c`, SMB2 PDU handling, directory enumeration, VFS file open checks, signing/encryption setup, and server-side copy FSCTL handling.

Risks: packed wire structs and endian-tagged access masks must stay aligned with protocol definitions. The ops table contains security-critical hooks; a partially initialized connection could skip signing, session validation, or encryption. `smb_get_msg` assumes a valid RFC1002-prefixed buffer, so callers must validate buffer length separately.

Test signals: build coverage across SMB1-disabled and enabled configurations, protocol negotiation for every dialect constant, response header initialization, access-mask mapping against Windows generic rights, and command dispatch paths that exercise every non-NULL `smb_version_ops` callback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/server/smb_common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/server/smbacl.c -->
## sources/distributed-fs/ceph-client/fs/smb/server/smbacl.c

Purpose: translates between Windows security descriptors/ACLs and Linux ownership, mode bits, POSIX ACLs, and ksmbd's NTACL xattr format. It also handles DACL inheritance, SID comparison/mapping, access checks against stored Windows ACLs, and applying client `SET_INFO` security updates.

Important APIs and functions: exported functions include `compare_sids`, `id_to_sid`, `parse_sec_desc`, `build_sec_desc`, `smb_acl_sec_desc_scratch_len`, `init_acl_state`, `free_acl_state`, `posix_state_to_acl`, `smb_inherit_flags`, `smb_inherit_dacl`, `smb_check_perm_dacl`, `set_info_sec`, and `ksmbd_init_domain`. Internal helpers map access masks to POSIX modes, emit ACEs for SIDs, parse bounded SIDs/DACLs, merge existing NTACL ACEs with POSIX ACL entries, and append inherited ACEs.

Control flow: parsing starts at `parse_sec_desc`, validates owner/group/DACL offsets within the provided buffer, maps owner and group SIDs through the mount idmap, preserves selected descriptor control bits, and calls `parse_dacl`. DACL parsing bounds-checks each ACE, expands generic rights, detects NFS mode ACEs, owner/group/everyone ACEs, and named Unix user/group ACEs, then builds access/default POSIX ACLs. Building a descriptor allocates owner/group SIDs from `smb_fattr`, optionally copies and validates an existing NT DACL, and appends generated POSIX-derived ACEs. Security updates parse the descriptor, set inode uid/gid/mode/ACLs, and optionally store the Windows ACL in xattrs.

State and persistence behavior: runtime conversion state lives in `struct smb_fattr` and `struct posix_acl_state`. Persistent effects are VFS owner/group/mode changes, POSIX ACL xattrs, and optional `security.NTACL` xattr writes through `ksmbd_vfs_set_sd_xattr`. `ksmbd_init_domain` stores the server domain SID in global `server_conf`.

Dependencies and integration points: uses common SMB ACL definitions, VFS and xattr helpers, share configuration flags, POSIX ACL APIs, mount idmapping, Linux id conversion, and ksmbd global domain configuration. SMB2 create/set-info/query-info paths use this file for security descriptor handling and ACL-based access checks.

Risks: this is directly exposed to untrusted descriptor buffers, so every offset, size, ACE count, and SID subauthority count must stay bounded. `compare_sids` returns equality once common subauthorities match, so callers depend on surrounding SID conventions. Inheritance allocates based on parent ACE count and copies owner/group offsets from the parent descriptor, making overflow and offset validation important. POSIX ACL and NTACL hashes can diverge after local filesystem changes, causing stored Windows ACLs to be rejected.

Test signals: owner/group SID mapping on idmapped mounts, malformed descriptors with short offsets or oversized ACE counts, generic rights expansion, NFS mode ACE parsing, named user/group ACE conversion, default ACL inheritance on files and directories, `DACL_PROTECTED` and auto-inherited flags, `FILE_MAXIMAL_ACCESS`, guest/everyone access checks, and share configs with and without ACL xattr storage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/server/smbacl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/server/smbacl.h -->
## sources/distributed-fs/ceph-client/fs/smb/server/smbacl.h

Purpose: defines ksmbd's security descriptor control flags, ACL conversion state, and the public API for Windows security descriptor parsing/building, DACL inheritance, and ACL permission checks.

Important APIs and types: defines descriptor revision/control flags such as `DACL_PRESENT`, `DACL_PROTECTED`, `DACL_AUTO_INHERITED`, and `SELF_RELATIVE`; `struct smb_fattr` for uid/gid/mode/access/POSIX ACL conversion output; `struct posix_ace_state`, `struct posix_user_ace_state`, `struct posix_ace_state_array`, and `struct posix_acl_state`; and declarations for SID comparison/mapping, descriptor conversion, inheritance, permission checks, and `set_info_sec`. Inline helpers translate POSIX ACL uid/gid entries through mount idmaps into init-namespace ids visible to ksmbd.

Control flow: callers allocate/populate `smb_fattr`, pass wire descriptors to `parse_sec_desc` for VFS changes, call `build_sec_desc` when returning security descriptors, and use `smb_check_perm_dacl` during open/access evaluation. The inline id translation helpers are used while emitting ACEs from POSIX ACL entries.

State and persistence behavior: the header only declares in-memory conversion state. Persistent ACL state is applied by implementation functions to inode metadata, POSIX ACL xattrs, and ksmbd NTACL xattrs.

Dependencies and integration points: includes common SMB ACL wire structures, VFS/namei/POSIX ACL/mount-idmap headers, and tree-connect management types. It bridges SMB2 security-information handling with Linux VFS permissions and share configuration.

Risks: conversion state owns POSIX ACL references that must be released by callers. The idmapped-mount translation helpers rely on `init_user_ns` as the ksmbd userspace id view; incorrect use would emit wrong SIDs for idmapped exports. Control flag values must remain protocol-accurate because they are stored and sent on the wire.

Test signals: compile with and without `CONFIG_FS_POSIX_ACL`, idmapped mount ACL round trips, descriptor build/query/set paths for owner/group/DACL combinations, and leak checks for `smb_fattr.cf_acls/cf_dacls` ownership.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/server/smbacl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/server/smbfsctl.h -->
## sources/distributed-fs/ceph-client/fs/smb/server/smbfsctl.h

Purpose: centralizes SMB/CIFS/SMB2 FSCTL and reparse-tag numeric constants used by server IOCTL handling.

Important APIs and types: defines FSCTL codes for DFS referrals, oplock requests, compression/encryption/sparse/zero-data operations, allocated-range queries, duplicate extents, named-pipe operations, negotiate validation, network interface information, and server-side copychunk. It also defines classic and WSL/Linux reparse tags such as `IO_REPARSE_TAG_LX_SYMLINK_LE`, FIFO, character device, block device, and AF_UNIX.

Control flow: the header has no control flow; IOCTL handlers switch on these constants and encode/decode operation-specific payloads elsewhere.

State and persistence behavior: no runtime or persistent state is owned here. The reparse constants may influence persisted xattr or response data in other modules.

Dependencies and integration points: consumed by SMB2 IOCTL/FSCTL processing, copychunk handling, network-interface reporting, sparse/zero range VFS calls, and reparse-point support. It depends on endian conversion macros for little-endian WSL tags.

Risks: wrong numeric constants create wire-incompatible behavior that clients surface as unsupported or malformed FSCTL responses. Several entries are placeholders marked as future work, so handlers must reject unsupported codes cleanly instead of assuming struct definitions exist.

Test signals: FSCTL dispatch for validate-negotiate-info, query-network-interface-info, copychunk/copychunk-write, query-allocated-ranges, set-zero-data, pipe transceive, unsupported code status mapping, and WSL reparse tag endian output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/server/smbfsctl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/server/stats.h -->
## sources/distributed-fs/ceph-client/fs/smb/server/stats.h

Purpose: provides lightweight ksmbd server counters for procfs reporting and no-op stubs when procfs support is disabled.

Important APIs and types: defines counter indexes for sessions, tree connects, total requests, read/write bytes, and per-command request buckets from `KSMBD_COUNTER_FIRST_REQ` through `KSMBD_COUNTER_LAST_REQ`. `struct ksmbd_counters` wraps an array of `percpu_counter`. Inline helpers increment, decrement, add, subtract, increment a request command bucket, and sum a counter.

Control flow: with `CONFIG_PROC_FS`, call sites update `ksmbd_counters.counters[type]`; request bucket updates are bounded by `KSMBD_COUNTER_MAX_REQS`. Without procfs, all helpers compile to no-ops and sums return zero.

State and persistence behavior: counters are in-memory percpu accounting state only. They are reset by module lifetime and are not persisted.

Dependencies and integration points: used by VFS read/write byte accounting, command dispatch request accounting, session/tree connection management, and procfs status rendering. Depends on the global `ksmbd_counters` object defined outside this header.

Risks: helper callers must pass valid base counter indexes; only the per-command helper bounds checks command numbers. Disabled procfs builds silently remove accounting, so tests that assert stats must account for configuration.

Test signals: procfs-enabled read/write byte increments, session/tree counter changes, command counter bounds at 0 and 18, counter sums under parallel I/O, and procfs-disabled compile coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/server/stats.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/server/transport_ipc.c -->
## sources/distributed-fs/ceph-client/fs/smb/server/transport_ipc.c

Purpose: implements ksmbd's generic-netlink control plane between the kernel server and the userspace daemon. It receives startup configuration and daemon responses, sends login/share/tree/RPC/SPNEGO requests, validates replies, manages request handles, and monitors daemon liveness with heartbeats.

Important APIs and functions: exported entry points include `ksmbd_ipc_login_request`, `ksmbd_ipc_login_request_ext`, `ksmbd_ipc_spnego_authen_request`, `ksmbd_ipc_tree_connect_request`, `ksmbd_ipc_tree_disconnect_request`, `ksmbd_ipc_logout_request`, `ksmbd_ipc_share_config_request`, `ksmbd_rpc_open`, `ksmbd_rpc_close`, `ksmbd_rpc_write`, `ksmbd_rpc_read`, `ksmbd_rpc_ioctl`, `ksmbd_ipc_id_alloc`, `ksmbd_rpc_id_free`, `ksmbd_ipc_release`, `ksmbd_ipc_soft_reset`, and `ksmbd_ipc_init`. Internal pieces include the generic-netlink family/ops/policy, `ipc_msg_table`, `ipc_ida`, `handle_startup_event`, `handle_generic_event`, `ipc_msg_send_request`, `ipc_validate_msg`, and heartbeat work.

Control flow: userspace sends `KSMBD_EVENT_STARTING_UP`; the handler validates version/capability, serializes startup, applies daemon-provided server config, starts control init work, stores daemon portid, and schedules heartbeat. Kernel request helpers allocate a message, acquire a handle when a response is expected, hash a wait entry, send netlink unicast to the daemon, wait up to two seconds, validate response size against embedded lengths, remove the entry, and return the response buffer to the caller. Generic response events look up the handle, copy payload, and wake the waiter. Heartbeat work resets server state and queues reset work when the daemon stops responding.

State and persistence behavior: runtime global state includes daemon portid, an IDA of IPC/RPC handles, a small hash table of outstanding requests, server configuration fields, delayed heartbeat work, and `server_conf.ipc_last_active`. No durable storage is written, but startup config controls TCP/RDMA limits, protocol bounds, domain SID, netbios/server/workgroup strings, interfaces, file limits, and IPC timeout behavior.

Dependencies and integration points: integrates generic netlink, net namespaces, wait queues, IDA, delayed work, server control work, connection/session/share/user management, TCP interface setup, RDMA max I/O sizing, SMB2 max read/write/trans/credits setup, and durable file-table limits. RPC helpers coordinate with session `rpc_lock` and guest restriction flags.

Risks: IPC is untrusted userspace input. Response validation must reject inconsistent payload lengths, oversized group counts, undersized handles, and mismatched response types. Startup can reconnect to a new daemon only after heartbeat failure, so races around `ksmbd_tools_pid` and `startup_lock` are important. Synchronous two-second waits can fail under daemon stalls. Payload allocation uses flexible buffers and maximum payload checks; missing checks would expose overreads or memory pressure.

Test signals: daemon startup with valid/invalid genl version, startup config overflow for `deadtime`, min/max protocol strings, interface list parsing, daemon reconnect after heartbeat failure, login/share/tree/SPNEGO request-response paths, malformed response lengths, ext-login `ngroups` bounds, RPC read/write/ioctl payload limit, guest restricted RPC flag, IPC timeout reset, and init/release netlink registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/server/transport_ipc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/server/transport_ipc.h -->
## sources/distributed-fs/ceph-client/fs/smb/server/transport_ipc.h

Purpose: declares the kernel-to-userspace IPC API used by ksmbd authentication, share lookup, tree connect/disconnect, SPNEGO, RPC named pipe operations, and IPC lifecycle management.

Important APIs and types: defines `KSMBD_IPC_MAX_PAYLOAD` as 4096 and declares login, extended-login, tree-connect, tree-disconnect, logout, share-config, SPNEGO, RPC open/close/read/write/ioctl, IPC/RPC id allocation/free, release, soft-reset, and init functions. It forward-declares session/share/tree/socket types to keep consumers decoupled from implementation details.

Control flow: callers use request functions that either return daemon-allocated response payloads to be freed by the caller or integer status for fire-and-forget notifications. Init registers the netlink family; soft reset drops daemon association; release unregisters.

State and persistence behavior: the header owns no state. Implementation state is in `transport_ipc.c`; response payload ownership crosses this API boundary.

Dependencies and integration points: consumed by user/session/share management, SMB2 authentication/session setup, tree connect handling, named pipe/RPC handling, server startup/shutdown, and control reset paths.

Risks: callers must respect payload limits, validate NULL responses as daemon errors/timeouts, and free successful response buffers. RPC handle lifetime is split between generic IPC IDs and pipe/session code, so mismatched `ksmbd_ipc_id_alloc`/`ksmbd_rpc_id_free` can leak handles.

Test signals: build consumers with this header alone, NULL-response handling for every request API, oversize RPC/SPNEGO payload rejection, and init/soft-reset/release lifecycle tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/server/transport_ipc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/server/transport_rdma.c -->
## sources/distributed-fs/ceph-client/fs/smb/server/transport_rdma.c

Purpose: adapts the common `smbdirect` RDMA socket implementation to ksmbd's server transport interface. It starts SMB Direct listeners, accepts RDMA clients, creates ksmbd connections, and implements read/write/RDMA read/RDMA write transport operations.

Important APIs and functions: exported functions include `init_smbd_max_io_size`, `get_smbd_max_read_write_size`, `ksmbd_rdma_init`, `ksmbd_rdma_stop_listening`, and `ksmbd_rdma_capable_netdev`. Internal functions allocate/free transports, wrap `smbdirect_connection_recvmsg`, `smbdirect_connection_send_iter`, and `smbdirect_connection_rdma_xmit`, manage listener kthreads, configure SMB Direct socket parameters, and translate debug logging.

Control flow: `ksmbd_rdma_init` initializes two listeners: port 445 for InfiniBand/RoCE and port 5445 for iWARP. Each listener creates a kernel SMBDirect socket, sets negotiation, credit, send/receive, read/write, keepalive, polling, and logging parameters, binds and listens, then starts an accept kthread. Accepted sockets are wrapped in `struct smb_direct_transport`, a ksmbd connection is allocated and inserted into the connection hash, and a per-connection handler thread is launched. Transport ops pass normal SMB messages or RDMA payloads through the SMBDirect socket.

State and persistence behavior: runtime state consists of listener sockets/threads, per-connection `smb_direct_transport` objects, negotiated SMBDirect socket parameters, and a configurable max read/write size clamped between 512 KiB and 16 MiB. No persistent storage is written.

Dependencies and integration points: depends on `linux/smbdirect.h`, RDMA/InfiniBand availability, ksmbd connection allocation/handler loop, global connection list locking, SMB common sizing setup via IPC startup, and netdev RDMA capability reporting for SMB2 network-interface info.

Risks: listener startup is all-or-nothing and must destroy both listeners on partial failure. Port flags intentionally split iWARP and IB/RoCE behavior. Accepted transport cleanup must release both SMBDirect socket and ksmbd connection exactly once. The transport only reports max RDMA I/O size for its own ops table, so callers must handle TCP returning zero.

Test signals: `CONFIG_SMB_SERVER_SMBDIRECT` builds, listener startup/teardown on systems with and without RDMA devices, port 445 and 5445 binding failures, accepted client connection thread launch, negotiated max read/write size clamp, RDMA read/write success and failure paths, keepalive timeout, and network-interface capability reporting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/server/transport_rdma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/server/transport_rdma.h -->
## sources/distributed-fs/ceph-client/fs/smb/server/transport_rdma.h

Purpose: declares ksmbd SMB Direct/RDMA transport lifecycle and capability APIs, with stubs when SMBDirect server support is disabled.

Important APIs and types: defines default/min/max SMBDirect I/O sizes (`8 MiB`, `512 KiB`, `16 MiB`) and declares `ksmbd_rdma_init`, `ksmbd_rdma_stop_listening`, `ksmbd_rdma_capable_netdev`, `init_smbd_max_io_size`, and `get_smbd_max_read_write_size`. Disabled builds return success/no-op/false/zero as appropriate.

Control flow: server startup can call RDMA init unconditionally because the header supplies disabled stubs. Runtime sizing and network-interface info call the capability helpers without depending on the configuration.

State and persistence behavior: this header owns no state. Enabled implementation stores listener and negotiated transport state in `transport_rdma.c`.

Dependencies and integration points: includes `linux/smbdirect.h` and is used by IPC startup config, server transport initialization/shutdown, and network-interface enumeration.

Risks: disabled stubs make RDMA absence look like a successful no-op, so startup tests must distinguish "feature unavailable" from "listener started." Consumers must include this header with `struct net_device` and `struct ksmbd_transport` visible or forward-declared by surrounding includes.

Test signals: compile with `CONFIG_SMB_SERVER_SMBDIRECT=y/m/n`, startup behavior when disabled, I/O size clamp tests when enabled, and interface capability output for RDMA and non-RDMA netdevices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/server/transport_rdma.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/server/transport_tcp.c -->
## sources/distributed-fs/ceph-client/fs/smb/server/transport_tcp.c

Purpose: implements ksmbd's TCP transport: interface-bound listener management, accept loops, per-client connection creation, socket read/write helpers, connection limits, and netdevice up/down reaction.

Important APIs and functions: exported functions include `ksmbd_tcp_init`, `ksmbd_tcp_destroy`, `ksmbd_tcp_set_interfaces`, and `ksmbd_find_netdev_name_iface_list`. Internal helpers allocate/free `tcp_transport`, create listener sockets, start/stop listener kthreads, accept clients, read exact byte ranges with retry behavior, send kvec responses, and disconnect transports. `struct interface` tracks a netdev name, listener socket/thread, list membership, and state.

Control flow: initialization registers a netdevice notifier. Startup configuration populates `iface_list`; if the daemon provided no list, future NETDEV_UP events bind additional interfaces. On NETDEV_UP, `create_socket` creates an IPv6 socket with IPv4 fallback, disables IPv6-only mode, enables nodelay/reuseaddr, tries `SO_BINDTODEVICE`, binds to `server_conf.tcp_port`, listens, and starts an accept thread. The accept loop enforces optional per-IP and global connection limits, sets socket timeouts, wraps accepted sockets in ksmbd transports, and starts a per-connection handler thread. Reads loop until the requested byte count is satisfied or connection/reconnect/retry limits terminate.

State and persistence behavior: runtime state includes `iface_list`, `bind_additional_ifaces`, listener socket/thread pointers, `active_num_conn`, per-transport cached iov arrays, and each connection's IPv4/IPv6 address hash in the global connection table. There is no persistent storage.

Dependencies and integration points: uses Linux kernel sockets, netdevice notifier API, freezer support, ksmbd connection allocation/handler loop, global connection list, server configuration from IPC startup, transport ops consumed by generic ksmbd I/O, and TCP timeout constants from connection/server headers.

Risks: netdevice event handling must avoid leaking sockets or stale interface entries on bind/listen/thread failures. Per-IP limiting scans the global connection hash and must release the just-accepted socket on rejection. `active_num_conn` is decremented only when max-connections accounting is enabled, so all failure/close paths must match that condition. `kvec_array_init` and cached iov resizing are sensitive to partial reads. `SO_BINDTODEVICE` tolerates `-ENODEV`, so unexpected interface names can still bind broadly depending on kernel behavior.

Test signals: IPv6 listener with IPv4 fallback, interface list and bind-additional modes, NETDEV_UP/DOWN cycles, port bind failures, global and per-IP connection limits, accepted connection thread failure unwind, socket read retry on `-EAGAIN/-ERESTARTSYS`, reconnect shutdown path, writev with `MSG_NOSIGNAL`, and destroy cleanup after active listeners.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/server/transport_tcp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/server/transport_tcp.h -->
## sources/distributed-fs/ceph-client/fs/smb/server/transport_tcp.h

Purpose: declares the public TCP transport setup and interface-management API for ksmbd.

Important APIs and types: declares `ksmbd_tcp_set_interfaces`, `ksmbd_find_netdev_name_iface_list`, `ksmbd_free_transport`, `ksmbd_tcp_init`, and `ksmbd_tcp_destroy`. `struct interface` is intentionally opaque to most users and defined in the implementation.

Control flow: server startup initializes TCP notifier state, daemon startup config passes the interface list through `ksmbd_tcp_set_interfaces`, netdevice events create/destroy sockets, and server teardown calls `ksmbd_tcp_destroy`.

State and persistence behavior: no state is stored in the header. Implementation state lives in the interface list and per-transport objects.

Dependencies and integration points: included by IPC startup config and server lifecycle code that needs TCP initialization and interface binding. The declared `ksmbd_free_transport` is part of the broader transport abstraction even though TCP frees through its ops table in this file set.

Risks: consumers should not depend on `struct interface` layout. Interface-list strings are NUL-separated and size-bounded by the caller; malformed lists can produce partial configuration.

Test signals: compile users of the header, interface-list parsing through the public function, lookup by netdev name after startup config, and init/destroy ordering relative to server start/stop.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/server/transport_tcp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/server/unicode.c -->
## sources/distributed-fs/ceph-client/fs/smb/server/unicode.c

Purpose: converts SMB wire UTF-16LE strings to/from local kernel/NLS strings, including selected Windows/POSIX character remapping and UTF-8 surrogate-pair handling.

Important APIs and functions: exported functions are `smb_strtoUTF16`, `smb_strndup_from_utf16`, and `smbConvertToUTF16`. Internal helpers include `cifs_mapchar`, `smb_utf16_bytes`, and `smb_from_utf16`. Character mapping covers colon, asterisk, question mark, pipe, greater-than, and less-than when mapchars behavior is requested.

Control flow: UTF-16-to-local conversion first computes output byte length, allocates a destination, then walks 16-bit little-endian words with unaligned reads, converting through NLS `uni2char` or UTF-8 fallback for surrogate pairs/variation selectors. Local-to-UTF16 conversion uses direct UTF-8-to-UTF16 for UTF-8 codepages when possible, falls back through NLS `char2uni`, and optionally maps reserved POSIX characters to private Unicode values used by SMB clients.

State and persistence behavior: no persistent state is owned. Functions allocate returned strings for callers and write converted output into caller-provided buffers. Conversion behavior depends on the connection's loaded NLS table and unicode map state held elsewhere.

Dependencies and integration points: uses Linux NLS and Unicode helpers, unaligned endian access, ksmbd default allocation flags, and SMB Unicode constants from the shared NLS utility header. It is used by path, tree-name/share-name, directory entry, short-name, and request parsing code.

Risks: conversion is buffer-bound but caller-supplied lengths must be correct in bytes versus UTF-16 words. UTF-8 fallback advances source indexes for surrogate pairs and IVS sequences; off-by-one bugs can truncate or overrun converted names. Slash/backslash remapping is intentionally not handled because path building uses separators. Unknown characters become `?`, which may interact with wildcard behavior.

Test signals: UTF-16LE path conversion with unaligned source buffers, non-Unicode SMB1 strings, UTF-8 astral-plane characters, variation selectors, mapchars on reserved characters, destination buffer boundary truncation, invalid UTF-8 fallback to `?`, and NLS codepages other than UTF-8.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/server/unicode.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/server/unicode.h -->
## sources/distributed-fs/ceph-client/fs/smb/server/unicode.h

Purpose: exposes ksmbd Unicode conversion helpers and pulls in the SMB/CIFS Unicode constants and Linux NLS/unicode types needed by server path and name handling.

Important APIs and types: declares `smb_strtoUTF16`, `smb_strndup_from_utf16`, `smbConvertToUTF16`, and `ksmbd_extract_sharename`. Includes byteorder, Linux types, NLS, Unicode, and UCS-2 utility definitions.

Control flow: callers convert local names to UTF-16 for responses, duplicate UTF-16 request strings into local codepage strings, and extract share names from tree-connect requests via the declared helper implemented in `misc.c`.

State and persistence behavior: no state is owned. Returned strings from duplication/extraction helpers are heap allocations owned by callers.

Dependencies and integration points: used by SMB1/SMB2 request parsing, directory response emission, short-name generation, tree connect handling, and misc path helpers. It bridges server code to shared NLS utilities under `fs/smb/nls`.

Risks: declarations expose byte-length based APIs; mismatched length units are a common integration hazard. The duplicate declaration of `ksmbd_extract_sharename` with `misc.h` means signature changes must stay synchronized.

Test signals: compile coverage of all users, UTF-16 round trips across codepages, tree-connect share-name extraction, and caller ownership/error handling for `ERR_PTR` returns.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/server/unicode.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/server/vfs.c -->
## sources/distributed-fs/ceph-client/fs/smb/server/vfs.c

Purpose: provides ksmbd's VFS adapter layer for file creation, directory creation, reads/writes, fsync, unlink/rmdir, hardlink, rename, truncate, xattrs, alternate data streams, directory lookup, sparse/zero/copy operations, ACL/NTACL xattr storage, DOS attributes, directory stat formatting, and POSIX lock wait/unblock helpers.

Important APIs and functions: major exported functions include `ksmbd_vfs_create`, `ksmbd_vfs_mkdir`, `ksmbd_vfs_read`, `ksmbd_vfs_write`, `ksmbd_vfs_fsync`, `ksmbd_vfs_remove_file`, `ksmbd_vfs_link`, `ksmbd_vfs_getattr`, `ksmbd_vfs_rename`, `ksmbd_vfs_truncate`, `ksmbd_vfs_listxattr`, `ksmbd_vfs_getxattr`, `ksmbd_vfs_setxattr`, `ksmbd_vfs_remove_xattr`, `ksmbd_vfs_kern_path`, `ksmbd_vfs_kern_path_start_removing`, `ksmbd_vfs_kern_path_end_removing`, `ksmbd_vfs_kern_path_create`, `ksmbd_vfs_empty_dir`, `ksmbd_vfs_set_fadvise`, `ksmbd_vfs_zero_data`, `ksmbd_vfs_fqar_lseek`, `ksmbd_vfs_unlink`, `ksmbd_vfs_set/get_sd_xattr`, `ksmbd_vfs_set/get_dos_attrib_xattr`, `ksmbd_vfs_copy_file_ranges`, `ksmbd_vfs_set_init_posix_acl`, and `ksmbd_vfs_inherit_posix_acl`.

Control flow: path lookup is share-root constrained with `LOOKUP_BENEATH`, optional cross-mount following, removal/create helpers that hold the right VFS locks, and optional caseless lookup by iterating directory names with Unicode-aware comparison. Normal reads/writes enforce requested SMB access bits, stream I/O maps to xattr values, non-POSIX-extension opens check byte-range locks, writes/truncates/copies break level-II oplocks, and sync writes call `vfs_fsync_range`. NTACL xattr storage encodes the security descriptor plus a hash of current POSIX ACL state; reads decode and verify that hash before returning the stored descriptor.

State and persistence behavior: persistent effects include files/directories/links/renames/deletions, file contents, inode size, xattrs for alternate streams (`user.DosStream.*`), DOS attributes (`user.DOSATTRIB`), NTACLs (`security.NTACL`), and POSIX ACL xattrs. Runtime state includes file positions, stream positions, readdir counters, VFS locks, temporary NDR buffers, and stats counters for bytes read/written.

Dependencies and integration points: integrates with Linux VFS, xattr, fallocate, copy_file_range/splice, ACL, idmapped mounts, unicode casefolding, SMB oplocks, ksmbd file-cache lookup, share config flags, session/work credential override from `smb_common.c`, NDR encode/decode, and stats counters. SMB2 create/read/write/query-info/set-info/ioctl handlers call this layer instead of raw VFS APIs.

Risks: path containment and symlink avoidance are security-critical. Stream data stored in xattrs is capped by `XATTR_SIZE_MAX`, and stream reads/writes must manage allocation and partial range semantics. NTACL verification rejects descriptors when POSIX ACL hashes change, which is correct but can surprise clients after local edits. Remove/rename/create paths must pair VFS start/end helpers and mount write references. Copychunk needs overlap handling and fallback behavior. Lock-range checks are skipped for POSIX extensions, so protocol mode changes affect behavior.

Test signals: create/mkdir with owner inheritance, share-root escape attempts, symlink rejection, caseless lookup on Unicode and ASCII names, read/write access denial, alternate data stream read/write/delete, byte-range lock conflicts, oplock break before write/truncate/copy, fsync by volatile/persistent id, hardlink cross-mount rejection, rename delete-share conflicts, xattr list/get/set/remove, DOS attribute round trip, NTACL hash mismatch, sparse zeroing and allocated-range queries, copychunk overlap/fallback, POSIX ACL init/inherit, and directory empty checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/server/vfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/server/vfs.h -->
## sources/distributed-fs/ceph-client/fs/smb/server/vfs.h

Purpose: declares the ksmbd VFS abstraction used by SMB command handlers and defines helper structures for directory enumeration, stat conversion, and stream typing.

Important APIs and types: defines stream type constants `DATA_STREAM` and `DIR_STREAM`, create-option helper flags, `struct ksmbd_dir_info`, `struct ksmbd_readdir_data`, and `struct ksmbd_kstat`. It declares VFS helpers for create/mkdir/read/write/fsync/remove/link/getattr/rename/truncate/copychunk, xattr and stream names, path lookup/create/remove, fadvise, zero data, allocated ranges, unlink, stat formatting, lock wait/unblock, ACL/SD/DOS xattrs, and POSIX ACL initialization/inheritance.

Control flow: SMB2 command handlers populate work/file/path structures, call these helpers for filesystem operations, and translate returned Linux errors to SMB status. Directory query code uses `ksmbd_dir_info` and `ksmbd_readdir_data` to track output cursor state and fill callbacks.

State and persistence behavior: structures hold per-request and per-open enumeration state. Persistent filesystem changes are performed by implementation functions in `vfs.c`.

Dependencies and integration points: includes Linux file/fs/namei/xattr/POSIX ACL/unicode headers plus ksmbd ACL and xattr definitions. It is the main contract between SMB PDU handlers, ACL handling, file-cache lifetime, and VFS persistence.

Risks: many APIs require paired cleanup (`ksmbd_vfs_kern_path_start_removing` with `ksmbd_vfs_kern_path_end_removing`, xattr buffers freed by callers, file references put elsewhere). Misusing idmapped mount arguments can apply permissions or ACLs under the wrong id view. Directory info buffer fields are mutable cursors and must be initialized per query.

Test signals: compile coverage for all SMB2 handlers, path-start/end pairing, xattr buffer ownership, directory enumeration cursor behavior, idmapped mount operations, and error translation for every declared VFS helper.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/server/vfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/server/vfs_cache.c -->
## sources/distributed-fs/ceph-client/fs/smb/server/vfs_cache.c

Purpose: manages ksmbd open-file state, volatile and persistent file IDs, inode-level open aggregation, delete-on-close state, durable/resilient handle preservation and scavenging, per-session file tables, global durable-handle table, procfs file reporting, and file cache allocation.

Important APIs and functions: exported functions include `ksmbd_set_fd_limit`, `ksmbd_inode_lookup_lock`, `ksmbd_inode_put`, `ksmbd_query_inode_status`, `ksmbd_inode_pending_delete`, `ksmbd_set_inode_pending_delete`, `ksmbd_clear_inode_pending_delete`, `ksmbd_fd_set_delete_on_close`, `ksmbd_close_fd`, `ksmbd_fd_put`, `ksmbd_lookup_fd_fast`, `ksmbd_lookup_foreign_fd`, `ksmbd_lookup_fd_slow`, `ksmbd_lookup_global_fd`, `ksmbd_lookup_durable_fd`, `ksmbd_put_durable_fd`, `ksmbd_lookup_fd_cguid`, `ksmbd_lookup_fd_inode`, `ksmbd_open_durable_fd`, `ksmbd_open_fd`, `ksmbd_update_fstate`, `ksmbd_launch_ksmbd_durable_scavenger`, `ksmbd_stop_durable_scavenger`, `ksmbd_close_tree_conn_fds`, `ksmbd_close_session_fds`, `ksmbd_init_global_file_table`, `ksmbd_free_global_file_table`, `ksmbd_validate_name_reconnect`, `ksmbd_reopen_durable_fd`, `ksmbd_init_file_table`, `ksmbd_destroy_file_table`, `ksmbd_init_file_cache`, and `ksmbd_exit_file_cache`.

Control flow: `ksmbd_open_fd` allocates a `ksmbd_file`, pins the connection, attaches or creates a shared `ksmbd_inode`, assigns a volatile id from the session table, and returns the not-yet-initialized fp for the create path to publish with `ksmbd_update_fstate`. Closing marks the fp closed under the table lock, cancels blocked works, drops idr references, removes durable/global IDs, closes oplocks/locks, performs delete-on-close if the last inode reference disappears, releases the filp and connection, and frees the slab object. Session teardown can preserve reconnectable durable handles by unpublishing them from the session idr, clearing conn/tcon, saving the owner identity, detaching locks/oplocks from the old connection, and setting a scavenger deadline. Durable reopen republishes the fp in a new session and reconnects locks/oplocks.

State and persistence behavior: runtime state is substantial: an inode hash table keyed by dentry, per-session `idr` file tables, a global durable `idr`, atomic fd-limit counter, `ksmbd_file` slab cache, durable scavenger thread/wait queue, open-file counters, lock lists, oplock lists, delete flags, and durable owner identity. Persistent effects happen indirectly on final close through VFS unlink or stream xattr removal for delete-on-close.

Dependencies and integration points: integrates with VFS unlink/xattr removal, oplock close/reconnect, ksmbd connection/session/tree/user objects, share durable-handle config, server task storage, procfs reporting, Linux IDR/rwlock/rwsem/atomic APIs, kernel freezer, and file lock APIs. SMB2 create/close/durable reconnect, tree disconnect, session logoff, lease/oplock, byte-range locking, and query directory all depend on this state.

Risks: reference counting and table publication are the main risks. The code has explicit comments about races among FP_NEW openers, teardown, durable preservation, scavenger disposal, and inode-list walkers. Any mismatch can underflow open-file stats, double-remove an idr id, use a stale connection pointer, or leak durable handles. Delete-on-close is inode-level and can delete after the final open closes. Durable owner comparison relies on uid/gid/name captured at preservation time. The scavenger handles concurrent lookups by taking transient refs before unlinking.

Test signals: open/close lifecycle, close during in-flight create before `FP_INITED`, lookup fast/slow/foreign/global/durable, fd-limit depletion, delete-on-close for file and stream, tree disconnect preserving other tree opens, session logoff preserving reconnectable durable handles, durable timeout scavenging, durable reconnect with owner/name validation, lease/oplock reconnect state, concurrent `ksmbd_lookup_fd_inode` during scavenger close, procfs file listing, and module init/exit with non-empty tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/server/vfs_cache.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/server/vfs_cache.h -->
## sources/distributed-fs/ceph-client/fs/smb/server/vfs_cache.h

Purpose: defines ksmbd's core open-file and inode cache data structures and declares file-table, durable-handle, lookup, close, delete-on-close, and cache lifecycle APIs.

Important APIs and types: defines Windows generic access constants, FID sentinel values, `struct ksmbd_lock`, `struct stream`, `struct ksmbd_inode`, fp states (`FP_NEW`, `FP_INITED`, `FP_CLOSED`), `struct durable_owner`, `struct ksmbd_file`, `struct ksmbd_file_table`, `has_file_id`, `ksmbd_stream_fd`, and all open/close/lookup/durable/scavenger/file-cache/inode-status declarations. `struct ksmbd_file` carries filp, volatile/persistent ids, access/share/create options, timestamps, stream state, lock/oplock linkage, durable flags, owner identity, connection/tcon pointers, and readdir state.

Control flow: SMB command handlers use lookup helpers to pin an fp, operate through VFS/oplock/lock paths, and release with `ksmbd_fd_put`. Create paths allocate with `ksmbd_open_fd`, populate metadata, and publish via `ksmbd_update_fstate`. Close, tree/session teardown, and durable reconnect use the declared close and reopen helpers.

State and persistence behavior: structures are runtime state, but `ksmbd_inode` flags drive persistent delete-on-close effects in the implementation. `stream.name` maps an open to xattr-backed alternate data streams. Durable owner fields persist identity across a disconnected handle's in-memory lifetime only.

Dependencies and integration points: includes Linux file/fs/rwsem/spinlock/idr/workqueue plus ksmbd VFS and share config headers. It is shared by SMB2 create/close/read/write/ioctl/query-directory, oplock/lease code, byte-range lock handling, tree/session management, and VFS helpers.

Risks: consumers must respect fp state and reference rules. `has_file_id` treats ids below `INT_MAX` as valid; SMB2 all-ones ids are invalid. `ksmbd_stream_fd` is a simple name check, so stream metadata must be initialized atomically with open setup. `ksmbd_file` mixes RCU, spinlock, rwsem, list, and atomic fields, making lock ordering important.

Test signals: compile across all users, open/close reference pairing, stream fd detection, compound fid fallback, delete-on-close flags, durable owner compare, id sentinel handling, and lockdep coverage for inode/file-table locks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/server/vfs_cache.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/server/xattr.h -->
## sources/distributed-fs/ceph-client/fs/smb/server/xattr.h

Purpose: defines ksmbd/Samba-compatible xattr metadata layouts and names used to persist Windows filesystem semantics on POSIX filesystems.

Important APIs and types: defines DOS attribute validity flags and `struct xattr_dos_attrib`, POSIX ACL hash tags and permission bits, `struct xattr_acl_entry`, flexible `struct xattr_smb_acl`, NTACL hash constants, `struct xattr_ntacl`, and xattr names/prefixes for DOS attributes (`user.DOSATTRIB`), alternate streams (`user.DosStream.`), and security descriptors (`security.NTACL`).

Control flow: no active control flow. `vfs.c` encodes/decodes these structures through NDR helpers when storing DOS attributes, stream data, and NTACLs.

State and persistence behavior: the structures describe persistent xattr payloads. DOS attributes store Windows attribute bits, EA size, size/allocation, creation/change/initial times. NTACL xattrs store the security descriptor plus hashes of the descriptor and POSIX ACL state to detect drift. Stream prefixes map SMB alternate data streams to user xattrs.

Dependencies and integration points: used by VFS xattr helpers, SMB2 query/set info, ACL conversion, NDR encode/decode, Samba interoperability, and stream read/write/delete paths.

Risks: layout compatibility with Samba is explicitly required; field changes or name changes can make existing metadata unreadable. `XATTR_SD_HASH_SIZE` is 64 although the hash type is SHA-256, so encode/decode code must remain consistent. Stream xattrs are constrained by filesystem xattr size and namespace support.

Test signals: Samba interoperability for DOSATTRIB and NTACL, DOS attribute round trip, NTACL hash validation after POSIX ACL changes, alternate stream name construction, xattr namespace availability, and big-endian/little-endian NDR compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/server/xattr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/smbdirect/Kconfig -->
## sources/distributed-fs/ceph-client/fs/smb/smbdirect/Kconfig

Purpose: declares the shared SMBDirect kernel configuration option used by SMB RDMA support.

Important APIs and types: defines `config SMBDIRECT` as a tristate defaulting to disabled. It depends on `INFINIBAND` and `INFINIBAND_ADDR_TRANS`, additionally requiring module builds when InfiniBand is modular or built-in InfiniBand for built-in use, and selects `SG_POOL`.

Control flow: Kconfig dependency resolution decides whether the smbdirect object set can be built. Server-side `CONFIG_SMB_SERVER_SMBDIRECT` code imports the `SMBDIRECT` namespace and relies on these common objects being available.

State and persistence behavior: no runtime state; build-time configuration only.

Dependencies and integration points: integrates SMB client/server RDMA code with the Linux RDMA stack, scatter-gather pool support, and the `fs/smb/smbdirect/Makefile` object list.

Risks: dependency mismatches can produce unresolved symbols or unavailable RDMA support even when server code is enabled. Default `n` means RDMA paths may receive less build/test coverage than TCP.

Test signals: Kconfig resolution for `SMBDIRECT=m/y/n`, builds with InfiniBand disabled/modular/built-in, selected `SG_POOL`, and server SMBDirect namespace import linking.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/smbdirect/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/smbdirect/Makefile -->
## sources/distributed-fs/ceph-client/fs/smb/smbdirect/Makefile

Purpose: builds the common SMBDirect support module/object set when `CONFIG_SMBDIRECT` is enabled.

Important APIs and types: maps `obj-$(CONFIG_SMBDIRECT)` to `smbdirect.o` and composes it from `socket.o`, `connection.o`, `mr.o`, `rw.o`, `debug.o`, `connect.o`, `listen.o`, `accept.o`, `devices.o`, and `main.o`.

Control flow: the kernel build system links the listed objects into the smbdirect unit according to the Kconfig value. The resulting namespace/functions are consumed by server `transport_rdma.c` and likely SMB client RDMA code.

State and persistence behavior: build metadata only; no runtime state.

Dependencies and integration points: tied to `fs/smb/smbdirect/Kconfig`, Linux RDMA/SMBDirect APIs, and module namespace import by ksmbd RDMA transport.

Risks: missing an object can remove essential socket, connection, memory-registration, read/write, listener, accept, device, or module initialization code. Object ordering should keep initialization/namespace behavior compatible with the kernel build.

Test signals: `CONFIG_SMBDIRECT=m` and `=y` builds, modpost namespace checks, RDMA client/server smoke tests, and symbol availability for server `transport_rdma.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/smbdirect/Makefile -->
