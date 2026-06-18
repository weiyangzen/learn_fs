# Group Research: group_1083_linux_stable_sources_os_linux_linux_stable_fs_smb_server_smb_common_865cdf6ffce1

Scope: `Docs/research_subset_a.md`; all listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/server/smb_common.c -->
# File Research: sources/os/linux/linux-stable/fs/smb/server/smb_common.c

## Summary
Implements shared ksmbd SMB protocol helpers: dialect selection, SMB1 negotiate fallback/upgrade handling, request validation, 8.3 short-name generation, directory dot/dotdot population, share-mode conflict checks, temporary fsuid/fsgid credential overrides, and generic access-mask expansion.

## Main Responsibilities
- Maintain SMB dialect tables for SMB1 negotiate names and SMB2/SMB3 dialect IDs.
- Select min/max protocol versions and map protocol indexes to user-visible strings.
- Validate incoming SMB1/SMB2/SMB3 transform request framing before protocol dispatch.
- Negotiate dialects from SMB1 dialect-name arrays or SMB2 dialect-id arrays, honoring `server_conf.min_protocol` and `server_conf.max_protocol`.
- Provide minimal SMB1 negotiate response plumbing, including upgrading SMB1 negotiate requests to SMB2 when the selected dialect is SMB2+.
- Populate `.` and `..` directory entries through caller-supplied directory-info encoders.
- Generate mangled 8.3 short names and convert them to UTF-16.
- Enforce Windows share-mode compatibility among existing and new opens on the same inode/stream.
- Override current credentials to the authenticated user or forced share uid/gid for VFS calls, then restore them.
- Expand generic SMB desired-access bits into concrete file rights.

## Key Interfaces
- Protocol selection: `ksmbd_min_protocol()`, `ksmbd_max_protocol()`, `ksmbd_get_protocol_string()`, `ksmbd_lookup_protocol_idx()`, `ksmbd_lookup_dialect_by_id()`.
- Request setup: `ksmbd_verify_smb_message()`, `ksmbd_smb_request()`, `ksmbd_init_smb_server()`, `ksmbd_smb_negotiate_common()`.
- Directory/open helpers: `ksmbd_populate_dot_dotdot_entries()`, `ksmbd_extract_shortname()`, `ksmbd_smb_check_shared_mode()`.
- Credentials/access: `__ksmbd_override_fsids()`, `ksmbd_override_fsids()`, `ksmbd_revert_fsids()`, `smb_map_generic_desired_access()`.

## Important Behavior
SMB1 support here is negotiate-only. If an SMB1 negotiate packet selects an SMB2 dialect, the connection is initialized as SMB3.1.1-capable and an SMB2 negotiate response is prepared. Other SMB1 commands are rejected.

Share-mode checking walks the inode’s open-file list under `m_lock` and compares requested desired access against previously granted share access and desired access. It special-cases named streams, attribute-only opens, and delete/read/write conflicts.

Credential override builds kernel credentials from ksmbd user config, applies forced share ids, fills supplementary groups, drops fs capabilities for non-root fsuid, and stores the previous cred in `work->saved_cred`.

## Cross-File Interactions
Used by connection dispatch, SMB2 negotiate code, directory enumeration, open/create handling, VFS operations, user/session/share config, and access-control conversion. It depends on `smb2pdu.c` for SMB2 negotiate handling and on `vfs.c`/`vfs_cache.c` types for directory and open-file state.

## Risks
Dialect negotiation and request validation are externally controlled input paths. Share-mode checks are concurrency-sensitive because they depend on open-file list lifetime and stream identity. Credential override/revert must stay balanced around every VFS operation to avoid running later filesystem work under the wrong identity.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/server/smb_common.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/server/smb_common.h -->
# File Research: sources/os/linux/linux-stable/fs/smb/server/smb_common.h

## Summary
Defines common ksmbd SMB protocol constants, shared wire structures, protocol operation tables, and helper prototypes used across the SMB server implementation.

## Main Responsibilities
- Define ksmbd protocol indexes for SMB1, SMB2.0/2.1, SMB3.0/3.02/3.1.1, and invalid protocol values.
- Define generic access-right expansions and file-open result constants.
- Provide SMB1 negotiate response and selected SMB query-directory structures.
- Declare `struct smb_version_ops` and `struct smb_version_cmds`, the per-dialect dispatch contract used by connections.
- Export common negotiation, request-validation, directory, share-mode, credential, copychunk-limit, and access-mask helpers.
- Provide `smb_get_msg()` to skip the four-byte RFC1002 length prefix.

## Key Interfaces
Important declarations include `ksmbd_verify_smb_message()`, `ksmbd_smb_request()`, `ksmbd_init_smb_server()`, `ksmbd_smb_negotiate_common()`, `ksmbd_smb_check_shared_mode()`, `ksmbd_override_fsids()`, `ksmbd_revert_fsids()`, and `smb_map_generic_desired_access()`.

## Cross-File Interactions
Included by most server protocol, transport, VFS, ACL, and connection files. The operation-table definitions are installed by SMB1 compatibility code and SMB2 dialect setup code.

## Risks
This header is a broad internal ABI. Changing access constants, operation-table callbacks, or wire structures affects protocol dispatch, negotiate behavior, and open/access checks across ksmbd.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/server/smb_common.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/server/smbacl.c -->
# File Research: sources/os/linux/linux-stable/fs/smb/server/smbacl.c

## Summary
Implements conversion between SMB/NT security descriptors and Linux ownership, mode bits, POSIX ACLs, and ksmbd xattr-backed Windows ACL behavior. It handles SID construction/comparison, NT DACL parsing/building, ACL inheritance, permission checks, and applying security-info updates to filesystem objects.

## Main Responsibilities
- Define well-known SIDs used by ksmbd: domain SID template, creator owner/group, Everyone, Authenticated Users, Unix user/group SIDs, and NFS-style Unix uid/gid/mode SIDs.
- Compare and copy SMB SIDs and map uid/gid values to SIDs or SIDs back to kernel ids with idmapped-mount support.
- Convert ACE access masks into POSIX mode bits and POSIX mode/ACL entries back into SMB ACE access masks.
- Parse incoming security descriptors, validate owner/group/DACL offsets and SID/ACE bounds, and fill `struct smb_fattr`.
- Build self-relative NT security descriptors from current inode metadata, POSIX ACLs, and optionally a previous NT descriptor.
- Preserve inherited or existing NT ACEs while adding POSIX ACL-derived ACEs.
- Inherit DACLs from parent NTACL xattrs, including creator-owner/group substitution and inheritance flag handling.
- Check requested SMB access against stored Windows ACL xattrs and fallback POSIX ACL entries.
- Apply `SET_INFO` security changes: update uid/gid/mode, replace POSIX ACL xattrs, and store NTACL xattrs when configured.
- Initialize ksmbd’s configured domain SID.

## Key Interfaces
- Conversion: `parse_sec_desc()`, `build_sec_desc()`, `smb_acl_sec_desc_scratch_len()`.
- ACL state helpers: `init_acl_state()`, `free_acl_state()`, `posix_state_to_acl()`.
- SID helpers: `compare_sids()`, `id_to_sid()`, `ksmbd_init_domain()`.
- Inheritance/access: `smb_inherit_flags()`, `smb_inherit_dacl()`, `smb_check_perm_dacl()`, `set_info_sec()`.

## Important Behavior
`parse_sec_desc()` accepts self-relative NT security descriptors, validates offsets against the supplied buffer length, maps owner/group SIDs through the mount idmap, preserves DACL control flags, and delegates ACE parsing to `parse_dacl()`.

`build_sec_desc()` constructs owner, group, and DACL sections according to requested security-info bits. Without a previous descriptor it derives a DACL from mode/POSIX ACLs; with one it copies valid existing ACEs and appends POSIX ACL-derived entries.

Inheritance reads the parent `security.NTACL` xattr, validates parent SID and DACL bounds, filters ACEs by object/container inheritance flags, substitutes creator owner/group with the new child uid/gid, and stores a new NTACL xattr on the child.

Permission checking prefers NTACL xattrs, computes maximal access when requested, searches matching user/NFS-mode/Everyone ACEs, consults POSIX ACLs for named user/group fallback, and rejects access when requested bits exceed allowed bits plus always-permitted metadata rights.

## Cross-File Interactions
Uses `smb_map_generic_desired_access()` from `smb_common.c`, xattr helpers from `vfs.c`, xattr formats from `xattr.h`, share flags from management config, and common SMB ACL wire types from `../common/smbacl.h`. Called by SMB2 create/query/set security paths and VFS ACL initialization/inheritance paths.

## Risks
This file parses attacker-controlled security descriptors and xattr-backed ACL blobs. Bounds checks around offsets, ACE sizes, SID subauthority counts, inherited ACE allocation, and descriptor size arithmetic are critical. Semantics are also subtle: small changes can break Windows ACL compatibility, POSIX ACL preservation, idmapped mount ownership, or durable Samba/ksmbd xattr interoperability.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/server/smbacl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/server/smbacl.h -->
# File Research: sources/os/linux/linux-stable/fs/smb/server/smbacl.h

## Summary
Declares ksmbd’s SMB ACL conversion API and supporting POSIX ACL state structures.

## Main Responsibilities
- Define security descriptor revision and control flag bits.
- Define `struct smb_fattr`, the intermediate owner/group/mode/access/POSIX-ACL container.
- Define POSIX ACL accumulation structures used while converting NT ACEs.
- Declare security descriptor parse/build, SID mapping, DACL inheritance, DACL permission checking, and security-info update functions.
- Provide idmapped-mount-aware POSIX ACL uid/gid translation helpers.

## Key Interfaces
`parse_sec_desc()`, `build_sec_desc()`, `smb_acl_sec_desc_scratch_len()`, `smb_inherit_dacl()`, `smb_check_perm_dacl()`, `set_info_sec()`, `id_to_sid()`, and `ksmbd_init_domain()` are the main exported contracts.

## Cross-File Interactions
Consumed by `smbacl.c`, `vfs.c`, SMB2 security query/set handlers, and xattr-backed NTACL storage.

## Risks
The structures here are shared conversion state. Changes to `smb_fattr` or ACL state layout affect both descriptor parsing and descriptor construction.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/server/smbacl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/server/smbfsctl.h -->
# File Research: sources/os/linux/linux-stable/fs/smb/server/smbfsctl.h

## Summary
Defines SMB/CIFS/SMB2 FSCTL and reparse-tag numeric constants used by ksmbd IOCTL handling.

## Main Responsibilities
- List filesystem, pipe, copychunk, network-interface, validate-negotiate, sparse, compression, object-id, reparse-point, and DFS FSCTL operation codes.
- Define common reparse tags and WSL/Linux reparse tags in little-endian form.

## Cross-File Interactions
Included by SMB2 IOCTL handling and reparse/symlink logic. Constants such as `FSCTL_VALIDATE_NEGOTIATE_INFO`, `FSCTL_QUERY_NETWORK_INTERFACE_INFO`, `FSCTL_COPYCHUNK`, and WSL reparse tags drive protocol-specific dispatch.

## Risks
These values are wire protocol constants. Any typo or endian mismatch causes clients to receive incorrect IOCTL behavior or incompatible reparse metadata.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/server/smbfsctl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/server/stats.h -->
# File Research: sources/os/linux/linux-stable/fs/smb/server/stats.h

## Summary
Defines ksmbd server counters and inline counter operations, enabled when `CONFIG_PROC_FS` is available and compiled to no-ops otherwise.

## Main Responsibilities
- Enumerate counters for sessions, tree connections, requests, read/write bytes, and per-command request counts.
- Define `struct ksmbd_counters` as an array of percpu counters.
- Provide inline increment/decrement/add/subtract/sum helpers.
- Bound per-command request counters with `KSMBD_COUNTER_MAX_REQS`.

## Cross-File Interactions
Read/write paths in `vfs.c` update byte counters; request dispatch paths can update request counters; proc/debug code can report sums.

## Risks
Counter indexes must match allocation size. The no-op fallback means code must not rely on these helpers for correctness when procfs is disabled.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/server/stats.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/server/transport_ipc.c -->
# File Research: sources/os/linux/linux-stable/fs/smb/server/transport_ipc.c

## Summary
Implements ksmbd’s generic-netlink IPC channel to the user-space ksmbd daemon. It handles daemon startup configuration, synchronous request/response correlation, authentication and share lookups, SPNEGO authentication, named-pipe RPC forwarding, heartbeat timeout detection, IPC ids, and netlink family registration.

## Main Responsibilities
- Register the `KSMBD_GENL_NAME` generic-netlink family and supported event operations.
- Validate daemon/kernel IPC protocol version.
- Receive startup configuration from user space and apply server settings: limits, flags, signing, ports, protocol bounds, SMB2 sizes, RDMA size, domain SID, names, workgroup, and interface binding.
- Track daemon port id and heartbeat activity, resetting the server if the daemon stops responding.
- Allocate IPC messages and correlate synchronous responses through a hash table keyed by request handle.
- Validate response payload sizes for RPC, SPNEGO, share config, and extended login responses.
- Send login, extended login, share config, tree connect/disconnect, logout, SPNEGO, and RPC open/read/write/ioctl/close requests.
- Enforce payload limits and account/share-name length limits.

## Key Interfaces
- Authentication/config: `ksmbd_ipc_login_request()`, `ksmbd_ipc_login_request_ext()`, `ksmbd_ipc_share_config_request()`, `ksmbd_ipc_spnego_authen_request()`.
- Tree/session notifications: `ksmbd_ipc_tree_connect_request()`, `ksmbd_ipc_tree_disconnect_request()`, `ksmbd_ipc_logout_request()`.
- RPC forwarding: `ksmbd_ipc_id_alloc()`, `ksmbd_rpc_id_free()`, `ksmbd_rpc_open()`, `ksmbd_rpc_close()`, `ksmbd_rpc_write()`, `ksmbd_rpc_read()`, `ksmbd_rpc_ioctl()`.
- Lifecycle: `ksmbd_ipc_init()`, `ksmbd_ipc_release()`, `ksmbd_ipc_soft_reset()`.

## Important Behavior
Requests that expect responses create an `ipc_msg_table_entry`, publish it under `ipc_msg_table_lock`, send a netlink message to the daemon, and wait up to `IPC_WAIT_TIMEOUT`. Responses are accepted only if the type equals request type plus one and the payload length matches event-specific validation.

Startup is serialized with `startup_lock`. If a daemon is already registered, the kernel checks liveness with a heartbeat before accepting a replacement daemon. Heartbeat work uses `server_conf.ipc_timeout` and schedules server reset when the daemon is inactive.

RPC operations include session-derived method flags and restricted context for guest users. Write/ioctl payloads are capped by `KSMBD_IPC_MAX_PAYLOAD`.

## Cross-File Interactions
Feeds configuration into `server_conf`, TCP interface setup, RDMA sizing, SMB2 max size/credit settings, file descriptor limits, and domain SID initialization. Used by user/session/share/tree management and IPC named-pipe RPC paths.

## Risks
This is a kernel/user trust boundary. Response size validation, handle correlation, version checking, daemon liveness, netlink capability checks, and payload length caps are security-critical. Races around daemon replacement, reset, and pending request wakeups can affect server availability.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/server/transport_ipc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/server/transport_ipc.h -->
# File Research: sources/os/linux/linux-stable/fs/smb/server/transport_ipc.h

## Summary
Declares the ksmbd IPC API used by kernel server code to communicate with the user-space daemon.

## Main Responsibilities
- Define the maximum IPC payload size.
- Declare login, SPNEGO, share config, tree connect/disconnect, logout, IPC id, and RPC forwarding helpers.
- Declare IPC lifecycle functions for init, release, and soft reset.

## Cross-File Interactions
Used by management, authentication, tree connection, and named-pipe/RPC code. Implemented entirely by `transport_ipc.c`.

## Risks
Prototype and payload-size contract changes must remain synchronized with the netlink message formats shared with user-space ksmbd tools.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/server/transport_ipc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/server/transport_rdma.c -->
# File Research: sources/os/linux/linux-stable/fs/smb/server/transport_rdma.c

## Summary
Implements the ksmbd SMB Direct server transport adapter using the shared kernel `smbdirect_socket` API. It listens on RDMA-capable SMB Direct ports, accepts RDMA connections, creates ksmbd connection threads, and exposes SMB Direct read/write/RDMA operations through `ksmbd_transport_ops`.

## Main Responsibilities
- Define SMB Direct listener defaults: ports, negotiate timeout, keepalive interval/timeout, RDMA read/write depth, credits, and message sizes.
- Clamp user-configured maximum RDMA read/write I/O size.
- Create two listeners: port 445 for InfiniBand/RoCE and port 5445 for iWARP.
- Configure `smbdirect_socket_parameters`, kernel polling, and logging callbacks.
- Accept SMB Direct sockets in listener kthreads and start per-connection `ksmbd_conn_handler_loop` threads.
- Wrap receive, send iterator, RDMA read, RDMA write, shutdown, disconnect, and free operations.
- Check net devices for RDMA capability via the common smbdirect layer.

## Key Interfaces
`ksmbd_rdma_init()`, `ksmbd_rdma_stop_listening()`, `ksmbd_rdma_capable_netdev()`, `init_smbd_max_io_size()`, and `get_smbd_max_read_write_size()`.

## Important Behavior
Accepted RDMA sockets are wrapped in `struct smb_direct_transport`, associated with a newly allocated `ksmbd_conn`, inserted into the global connection hash, and dispatched to the common ksmbd connection handler. Transport operations delegate wire movement to `smbdirect_connection_recvmsg()`, `smbdirect_connection_send_iter()`, and `smbdirect_connection_rdma_xmit()`.

## Cross-File Interactions
Called from server startup/shutdown and configured by IPC startup. SMB2 read/write paths can use `kt->ops->rdma_read` and `rdma_write`. The header provides stubs when SMB Direct server support is disabled.

## Risks
Listener lifetime, socket shutdown, and connection-thread startup must be ordered carefully to avoid leaked sockets or use-after-free. Negotiated RDMA sizes and credits must stay compatible with SMB Direct protocol constraints and the shared smbdirect implementation.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/server/transport_rdma.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/server/transport_rdma.h -->
# File Research: sources/os/linux/linux-stable/fs/smb/server/transport_rdma.h

## Summary
Declares ksmbd SMB Direct server transport entry points and default/min/max RDMA I/O sizing.

## Main Responsibilities
- Define `SMBD_DEFAULT_IOSIZE`, `SMBD_MIN_IOSIZE`, and `SMBD_MAX_IOSIZE`.
- Expose RDMA init, listener stop, netdev capability, max I/O configuration, and negotiated max read/write size helpers when `CONFIG_SMB_SERVER_SMBDIRECT` is enabled.
- Provide no-op/false/zero stubs when SMB Direct server support is disabled.
- Include the common `linux/smbdirect.h` API.

## Risks
The enabled and disabled APIs must remain source-compatible so callers do not need conditional code. Size bounds must stay aligned with SMB Direct negotiation limits.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/server/transport_rdma.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/server/transport_tcp.c -->
# File Research: sources/os/linux/linux-stable/fs/smb/server/transport_tcp.c

## Summary
Implements ksmbd’s TCP transport listener and per-connection socket I/O. It manages configured network interfaces, accepts SMB clients, enforces global and per-IP connection limits, creates ksmbd connection threads, reads/writes SMB messages, and responds to netdevice up/down events.

## Main Responsibilities
- Track configured interfaces and dynamically bind additional interfaces when requested.
- Create IPv6 dual-stack sockets with IPv4 fallback, bind to `server_conf.tcp_port`, set `SO_BINDTODEVICE`, enable reuseaddr/nodelay, and listen.
- Accept client sockets in per-interface listener kthreads.
- Enforce `server_conf.max_connections` and `server_conf.max_ip_connections`.
- Allocate `struct tcp_transport`, associate it with `struct ksmbd_conn`, populate IPv4/IPv6 peer identity and connection hash, and start `ksmbd_conn_handler_loop`.
- Provide transport `read`, `writev`, `disconnect`, and `free_transport` operations.
- Read exact byte counts with retry handling, freezer support, reconnect/shutdown checks, and reusable kvec arrays.
- Register a netdevice notifier to create sockets on interface up and tear them down on interface down.

## Key Interfaces
`ksmbd_tcp_set_interfaces()`, `ksmbd_find_netdev_name_iface_list()`, `ksmbd_free_transport()`, `ksmbd_tcp_init()`, and `ksmbd_tcp_destroy()`.

## Important Behavior
If the daemon provides no interface list, `bind_additional_ifaces` is enabled and sockets are created for suitable interfaces as they appear. If an interface list is provided, only those names are tracked. Accepted sockets get receive/send timeouts and then are handed to per-client ksmbd threads.

`ksmbd_tcp_readv()` retries `-ERESTARTSYS`/`-EAGAIN` according to `max_retries`, supports unlimited retries for inactive sessions, and returns shutdown/reconnect errors when connection state changes.

## Cross-File Interactions
Configured by IPC startup, used by server lifecycle, and integrated with the common connection handler through `ksmbd_transport_ops`.

## Risks
Connection accounting must stay balanced on accept failure, new-connection failure, and disconnect. Netdevice down handling must stop listener threads and release sockets without racing accept. Read retry behavior affects idle sessions and teardown responsiveness.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/server/transport_tcp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/server/transport_tcp.h -->
# File Research: sources/os/linux/linux-stable/fs/smb/server/transport_tcp.h

## Summary
Declares the ksmbd TCP transport management API.

## Main Responsibilities
- Expose interface configuration and lookup helpers.
- Expose transport free, TCP init, and TCP destroy lifecycle functions.

## Cross-File Interactions
Used by IPC startup configuration and server lifecycle code. Implemented by `transport_tcp.c`.

## Risks
Small header, but the opaque `struct interface` contract is used across transport setup code and must remain consistent with TCP internals.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/server/transport_tcp.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/server/unicode.c -->
# File Research: sources/os/linux/linux-stable/fs/smb/server/unicode.c

## Summary
Implements ksmbd character-set conversion helpers between local NLS strings and SMB UTF-16LE wire strings, including special SMB character remapping and limited surrogate/variation-sequence handling for UTF-8.

## Main Responsibilities
- Convert individual UTF-16 characters to the configured local codepage with optional SMB special-character mapping.
- Compute the output byte length of a UTF-16LE string in a target codepage.
- Convert UTF-16LE strings to local strings with bounds-aware null termination.
- Convert local strings to UTF-16LE using the configured NLS table.
- Duplicate SMB wire strings into allocated local strings.
- Convert local path/name strings to UTF-16LE with optional remapping of `:`, `*`, `?`, `<`, `>`, and `|` to private Unicode values.

## Key Interfaces
`smb_strtoUTF16()`, `smb_strndup_from_utf16()`, and `smbConvertToUTF16()`.

## Important Behavior
UTF-8 receives special handling through `utf8s_to_utf16s()`, `utf16s_to_utf8s()`, and `utf8_to_utf32()` to support non-plane-0 characters better than plain NLS callbacks. Unknown or invalid characters fall back to `?`. Backslash/slash remapping is intentionally not handled because path construction uses separators internally.

## Cross-File Interactions
Used by short-name generation, path/name conversion, directory encoding, and SMB request parsing. The header also declares `ksmbd_extract_sharename()`, implemented outside this file.

## Risks
Conversion functions are length-sensitive and operate on wire-controlled buffers. Off-by-one errors, incorrect surrogate advancement, or mismatched null-termination assumptions can corrupt SMB names or truncate paths.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/server/unicode.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/server/unicode.h -->
# File Research: sources/os/linux/linux-stable/fs/smb/server/unicode.h

## Summary
Declares ksmbd Unicode/NLS conversion helpers and includes kernel NLS/Unicode support headers.

## Main Responsibilities
- Declare local-to-UTF16 and UTF16-to-local conversion functions.
- Declare `ksmbd_extract_sharename()` for extracting share names from tree names.
- Include UCS-2 utility support used by SMB Unicode handling.

## Cross-File Interactions
Consumed by SMB path parsing, name encoding, short-name generation, and tree/share-name handling.

## Risks
The declared functions are used on SMB wire strings, so their callers depend on strict buffer length and null-termination semantics.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/server/unicode.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/server/vfs.c -->
# File Research: sources/os/linux/linux-stable/fs/smb/server/vfs.c

## Summary
Implements ksmbd’s VFS abstraction layer: path lookup inside shares, file and directory create/remove/rename/link, read/write/fsync/truncate, named-stream xattr I/O, extended attributes, sparse/allocated-range operations, copychunk, directory helpers, Windows metadata xattr storage, security descriptor xattr storage, and POSIX ACL initialization/inheritance.

## Main Responsibilities
- Resolve share-relative paths with `LOOKUP_BENEATH`, optional case-insensitive directory walking, optional cross-mount following, and removal/create-specific locking.
- Create files and directories, optionally inheriting owner from parent.
- Enforce SMB desired-access rights and byte-range lock conflicts before reads, writes, truncates, and copychunk.
- Read/write normal files through `kernel_read()`/`kernel_write()` and named streams through `user.DosStream.*` xattrs.
- Break level-II oplocks before writes, truncates, zeroing, and copy-range writes.
- Remove files/directories, hardlink, rename, unlink by open file, and test directory emptiness.
- List, get, set, remove, and case-insensitively find xattrs.
- Convert SMB caching options into Linux file flags/readahead behavior.
- Implement zero-data and allocated-range queries with fallocate/lseek.
- Store and retrieve DOS attribute xattrs via NDR encoding.
- Store and retrieve NT security descriptor xattrs with NDR encoding and SHA-256 hashes of the descriptor and current POSIX ACL state.
- Fill SMB directory/stat metadata from `kstat`, DOS attributes, and timestamps.
- Initialize POSIX ACLs from mode and inherit POSIX ACLs from parent default ACLs.

## Key Interfaces
Major exported helpers include `ksmbd_vfs_create()`, `ksmbd_vfs_mkdir()`, `ksmbd_vfs_read()`, `ksmbd_vfs_write()`, `ksmbd_vfs_fsync()`, `ksmbd_vfs_remove_file()`, `ksmbd_vfs_link()`, `ksmbd_vfs_rename()`, `ksmbd_vfs_truncate()`, `ksmbd_vfs_copy_file_ranges()`, `ksmbd_vfs_kern_path()`, `ksmbd_vfs_kern_path_start_removing()`, `ksmbd_vfs_kern_path_create()`, `ksmbd_vfs_set_sd_xattr()`, `ksmbd_vfs_get_sd_xattr()`, `ksmbd_vfs_set_dos_attrib_xattr()`, and `ksmbd_vfs_fill_dentry_attrs()`.

## Important Behavior
Path lookup keeps clients inside the share with `LOOKUP_BENEATH` for non-root paths. Case-insensitive lookup retries by iterating each path component directory and replacing the requested component with the actual on-disk spelling.

Named streams are represented as xattrs whose names are built from `user.DosStream.<stream>:$DATA` or `:$INDEX_ALLOCATION`. Stream writes are capped at `XATTR_SIZE_MAX` and rewrite the whole xattr value.

NTACL xattr storage uses Samba-compatible NDR v4 structures. Before storing, security descriptor offsets are shifted by `NDR_NTSD_OFFSETOF`; on load they are shifted back. A hash of current POSIX ACL state is checked before accepting the stored NT security descriptor.

Copychunk verifies source and destination access, rejects named streams, checks byte-range locks, avoids overlapping same-inode copy with direct `vfs_copy_file_range()`, and falls back to splice-based copying when needed.

## Cross-File Interactions
Uses access/credential helpers from `smb_common.c`, open state from `vfs_cache.c`, oplock breaking from `oplock.c`, ACL conversion from `smbacl.c`, NDR helpers, xattr formats from `xattr.h`, share config flags, and stats counters.

## Risks
This is a high-risk file because it bridges SMB semantics to Linux VFS semantics. Path traversal containment, write-mount acquisition/drop, xattr size handling, NTACL hash validation, stream xattr rewriting, lock conflict checks, idmapped ownership, and close/delete interactions must stay correct under concurrent client activity.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/server/vfs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/server/vfs.h -->
# File Research: sources/os/linux/linux-stable/fs/smb/server/vfs.h

## Summary
Declares ksmbd’s VFS helper API, stream types, create-option constants, directory enumeration state, and kstat wrapper used by SMB directory/stat responses.

## Main Responsibilities
- Define data and directory stream type constants.
- Define ksmbd-only create option flags and SMB create-option values.
- Define `struct ksmbd_dir_info`, `struct ksmbd_readdir_data`, and `struct ksmbd_kstat`.
- Declare path lookup, create, I/O, metadata, xattr, security descriptor, DOS attribute, copychunk, sparse range, lock, and POSIX ACL helpers.

## Cross-File Interactions
Used by SMB2 command handlers, directory enumeration, ACL code, file cache code, and xattr/metadata handling.

## Risks
The declarations here are a wide internal VFS contract. Changes to ownership, buffer, or path-locking expectations require coordinated updates in SMB2 command handlers and cache/lifetime code.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/server/vfs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/server/vfs_cache.c -->
# File Research: sources/os/linux/linux-stable/fs/smb/server/vfs_cache.c

## Summary
Implements ksmbd open-file and inode caching: per-session volatile FID tables, global durable/persistent handle tables, inode-open lists, delete-on-close state, lock cleanup, durable handle preservation/reconnect, durable scavenging, open-file proc reporting, and file-cache lifecycle.

## Main Responsibilities
- Maintain a global inode hash mapping dentries to `struct ksmbd_inode`.
- Track per-inode open file lists, oplock lists, delete-pending/delete-on-close flags, and file attributes.
- Allocate and free `struct ksmbd_file` objects from a kmem cache.
- Allocate volatile ids in per-session file tables and persistent ids in the global durable table using IDR.
- Enforce a configured open-file limit.
- Lookup file handles by volatile id, persistent id, create GUID, or inode/dentry.
- Close file handles, cancel blocked works, remove oplocks, release byte-range locks, drop connection refs, free stream/owner strings, and `fput()` files.
- Handle delete-on-close for files and named streams.
- Preserve reconnectable durable/resilient/persistent handles across session teardown.
- Run a durable-handle scavenger kthread that expires preserved handles after timeout.
- Reopen durable handles onto a new connection/session and restore lock/oplock connection associations.
- Validate durable reconnect names and owner identity.
- Close all handles for a tree connection or session.

## Key Interfaces
- Table lifecycle: `ksmbd_init_file_table()`, `ksmbd_destroy_file_table()`, `ksmbd_init_global_file_table()`, `ksmbd_free_global_file_table()`.
- Open/close/lookup: `ksmbd_open_fd()`, `ksmbd_close_fd()`, `ksmbd_fd_put()`, `ksmbd_lookup_fd_fast()`, `ksmbd_lookup_fd_slow()`, `ksmbd_lookup_global_fd()`, `ksmbd_lookup_durable_fd()`, `ksmbd_lookup_fd_cguid()`, `ksmbd_lookup_fd_inode()`.
- Durable handles: `ksmbd_open_durable_fd()`, `ksmbd_reopen_durable_fd()`, `ksmbd_put_durable_fd()`, `ksmbd_launch_ksmbd_durable_scavenger()`, `ksmbd_stop_durable_scavenger()`, `ksmbd_validate_name_reconnect()`, `ksmbd_vfs_compare_durable_owner()`.
- Inode/delete state: `ksmbd_inode_lookup_lock()`, `ksmbd_inode_put()`, `ksmbd_query_inode_status()`, `ksmbd_inode_pending_delete()`, `ksmbd_set_inode_pending_delete()`, `ksmbd_clear_inode_pending_delete()`, `ksmbd_fd_set_delete_on_close()`.

## Important Behavior
Each open file owns a strong connection reference while `fp->conn` is non-NULL. Session teardown can detach reconnectable durable handles by clearing `conn`, `tcon`, and `volatile_id`, removing them from the session table, and leaving them reachable through the global durable table until reconnect or scavenger expiry.

Close paths distinguish volatile table removal, durable table removal, inode-list unlink, final reference drop, and delayed finalization. Several comments document race fixes around FP_NEW/FP_INITED transitions, stale IDR ids, m_fp_list walkers, and open-file counter accounting.

A handle is reconnectable only if it is resilient/persistent, or durable with lease handle caching, or durable with batch oplock, and its oplock state is not in transition. Durable reconnect verifies owner uid/gid/name and can validate the path name relative to the share.

## Cross-File Interactions
Interacts with VFS deletion/unlink, oplock state, connection/session/tree management, SMB2 durable handle create/reconnect contexts, byte-range lock tracking, and proc debug output.

## Risks
This file is highly concurrency-sensitive. IDR publication/removal, refcount transitions, durable session teardown, scavenger expiry, inode list walking, connection reference ownership, delete-on-close, and open-file accounting all have race-prone edge cases.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/server/vfs_cache.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/server/vfs_cache.h -->
# File Research: sources/os/linux/linux-stable/fs/smb/server/vfs_cache.h

## Summary
Defines ksmbd file-handle, inode-cache, lock, stream, durable-owner, and file-table structures plus the public cache/lifetime API.

## Main Responsibilities
- Define Windows-style generic file permission constants and sentinel FID values.
- Define `struct ksmbd_lock` for byte-range lock tracking.
- Define `struct ksmbd_inode` for per-dentry shared open/oplock/delete state.
- Define `struct ksmbd_file` for per-open state, ids, access/share modes, oplock pointer, stream state, readdir state, durable flags, client/create GUIDs, owner identity, and lists.
- Define `struct ksmbd_file_table` wrapping an IDR and lock.
- Provide helpers for dir-context actor setup, FID validity, and stream detection.
- Declare all open/close/lookup, durable handle, inode status, file-table, fd-limit, and file-cache lifecycle functions.

## Cross-File Interactions
Consumed by SMB2 open/close/read/write/lock/durable-handle paths, VFS operations, oplock handling, connection/session cleanup, and proc reporting.

## Risks
The structures encode object ownership and synchronization assumptions. Layout or semantic changes can break handle lookup, durable reconnect, lock cleanup, delete-on-close, or oplock lifetime.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/server/vfs_cache.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/server/xattr.h -->
# File Research: sources/os/linux/linux-stable/fs/smb/server/xattr.h

## Summary
Defines ksmbd on-disk xattr metadata formats for Samba-compatible DOS attributes, named streams, POSIX ACL hashes, and NT security descriptors.

## Main Responsibilities
- Define DOS attribute valid-field flags and `struct xattr_dos_attrib`.
- Define simplified ACL entry/tag constants used to hash POSIX ACL state.
- Define `struct xattr_smb_acl` for encoded POSIX ACL hash input.
- Define `struct xattr_ntacl` for NDR v4 NTACL storage, descriptor hashes, POSIX ACL hashes, timestamp, and descriptor metadata.
- Define xattr name prefixes for DOS attributes, named streams, and NTACL security descriptors.

## Cross-File Interactions
Used by `vfs.c` for DOS attribute, stream, and NTACL xattr storage; by ACL code for security descriptor interoperability; and by NDR encode/decode helpers.

## Risks
These are persistent metadata formats. Changing fields, versions, prefixes, or hash semantics can break compatibility with existing ksmbd/Samba xattrs.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/server/xattr.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/smbdirect/Kconfig -->
# File Research: sources/os/linux/linux-stable/fs/smb/smbdirect/Kconfig

## Summary
Defines the `SMBDIRECT` kernel config option for common SMB Direct support.

## Main Responsibilities
- Provide a tristate option defaulting to disabled.
- Require InfiniBand core and address translation support.
- Restrict builds so SMB Direct can be modular when InfiniBand is modular, or built-in when InfiniBand is built-in.
- Select `SG_POOL`.

## Cross-File Interactions
Controls building the common `fs/smb/smbdirect` module used by SMB Direct client/server transport adapters.

## Risks
Dependency mistakes can produce invalid built-in/module combinations for RDMA SMB Direct support.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/smbdirect/Kconfig -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/smbdirect/Makefile -->
# File Research: sources/os/linux/linux-stable/fs/smb/smbdirect/Makefile

## Summary
Builds the common SMB Direct support object set when `CONFIG_SMBDIRECT` is enabled.

## Main Responsibilities
- Add `smbdirect.o` to the build for `CONFIG_SMBDIRECT`.
- Compose `smbdirect-y` from socket, connection, memory registration, RDMA read/write, debug, connect/listen/accept, device, and main implementation objects.

## Cross-File Interactions
Produces the common SMB Direct implementation imported by ksmbd server RDMA transport and CIFS client SMB Direct wrappers.

## Risks
Object list changes must stay synchronized with the common SMB Direct API surface; missing objects would cause link failures or incomplete RDMA transport support.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/smbdirect/Makefile -->