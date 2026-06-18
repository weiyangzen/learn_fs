# Group Research: group_841_linux_sources_os_linux_linux_fs_smb_server_smb2pdu_h_sources_os_linu_e114b4eccbbc

Scope: `Docs/research_subset_a.md`, source tree `sources/os/linux/linux`.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/smb/server/smb2pdu.h -->
# File Research: sources/os/linux/linux/fs/smb/server/smb2pdu.h

Defines ksmbd server-side SMB2/SMB3 protocol constants, wire response structures, query-info payload structures, and command handler prototypes.

Key contents:
- SMB2/SMB3 sizing defaults and limits: credits, I/O sizes, transform/message sizes, durable handle timeout.
- Create-context structures for allocation size, durable handles, POSIX create response, extended attributes, and security descriptors.
- File information and filesystem information response-size constants.
- Packed wire structs for file access, alignment, alternate name, stream, standard, EA, allocation, disposition, mode, compression, attribute/tag, and POSIX directory info.
- Public SMB2/SMB3 lifecycle and command entry points, including negotiate, session setup, tree connect, open, read/write, ioctl, notify, signing, encryption, and credit handling.
- POSIX file type constants used by POSIX extensions.

Dependencies:
- Includes `ntlmssp.h` and `smbacl.h`.
- Uses common SMB2 constants from shared protocol headers via included types such as `smb2_hdr`, `create_context_hdr`, and `smb_ntsd`.

Role in subsystem:
- This is a protocol ABI header for ksmbd SMB2/3 server code. It does not implement behavior; it pins the wire layouts and exported handler surface used by SMB2 PDU processing.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/smb/server/smb2pdu.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/smb/server/smb_common.c -->
# File Research: sources/os/linux/linux/fs/smb/server/smb_common.c

Implements protocol negotiation, common SMB request validation, directory pseudo-entry population, 8.3 short-name generation, share-mode checks, credential override, and generic access mapping.

Key behaviors:
- Defines supported SMB dialect tables for SMB1 negotiate upgrade paths and SMB2/SMB3 dialect IDs.
- Negotiates dialects from both SMB1-style dialect strings and SMB2 dialect ID arrays, respecting `server_conf.min_protocol` and `server_conf.max_protocol`.
- Validates inbound SMB frames, rejecting unsupported compression transform requests and non-SMB protocol IDs.
- Provides minimal SMB1 negotiate support solely to upgrade clients to SMB2+ negotiation; SMB1 commands otherwise return invalid/no response.
- Populates `"."` and `".."` directory entries through caller-provided query-dir formatting callbacks.
- Generates DOS 8.3 short names using uppercased basename/extension plus checksum mangling.
- Enforces SMB share-mode compatibility across existing opens on the same ksmbd inode, including delete/read/write sharing and stream-file distinctions.
- Overrides/reverts kernel credentials to a session/share fsuid/fsgid and supplementary groups before VFS operations.
- Maps SMB generic desired access bits to concrete file access masks.

Dependencies:
- Depends on connection, work, session, user, tree connect, share config, VFS, Unicode conversion, and SMB2 handler code.
- Consumes `server_conf` and connection ops/values to initialize dialect-specific server behavior.

Role in subsystem:
- Provides the common control-plane glue between raw SMB negotiation, ksmbd connection state, Windows access semantics, and Linux credentials.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/smb/server/smb_common.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/smb/server/smb_common.h -->
# File Research: sources/os/linux/linux/fs/smb/server/smb_common.h

Declares common protocol identifiers, SMB1 negotiate structures, access-mask expansions, version operation tables, and shared helper APIs.

Key contents:
- Protocol indexes from SMB1 through SMB 3.1.1 and `BAD_PROT`.
- SMB open-result constants and generic read/write/execute/all access-mask definitions.
- SMB1 negotiate response struct and SMB flag constants used for SMB1 negotiate upgrade.
- Common directory info structs and server version dispatch tables: `smb_version_ops` and `smb_version_cmds`.
- Prototypes for dialect lookup, message validation, server initialization, dot entry population, short-name extraction, negotiation, share-mode checks, fsid override, server-side copy limits, wildcard checks, and generic access mapping.
- Inline `smb_get_msg()` helper to skip the 4-byte RFC1002 header.

Role in subsystem:
- Central header that lets connection/request code call version-specific SMB handlers through common ops while sharing access and negotiation helpers.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/smb/server/smb_common.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/smb/server/smbacl.c -->
# File Research: sources/os/linux/linux/fs/smb/server/smbacl.c

Implements translation between Windows security descriptors/SIDs/ACEs and Linux ownership, mode bits, POSIX ACLs, and ksmbd NTACL xattrs.

Key behaviors:
- Defines built-in SIDs for ksmbd domain, creator owner/group, everyone, authenticated users, Unix users/groups, and NFS-style UID/GID/mode SIDs.
- Compares and copies SIDs, maps Unix IDs to SIDs, and maps SIDs back to `kuid_t`/`kgid_t` through mount idmaps.
- Converts SMB access masks to POSIX mode bits and POSIX mode bits to SMB access masks.
- Parses DACLs defensively with bounds checks on ACL size, ACE count, SID subauthority count, and ACE sizes.
- Builds POSIX ACL state from recognized owner/group/everyone/named-user ACEs and optional default ACLs for directories.
- Builds Windows security descriptors from inode owner/group/mode and POSIX ACLs, optionally preserving existing NT DACL entries.
- Computes scratch length for security descriptor construction with overflow checks.
- Inherits DACLs from parent NTACL xattrs, handling creator owner/group substitution, inheritance flags, no-propagate behavior, and directory/file differences.
- Checks requested access against stored Windows ACL xattrs, falling back through POSIX ACL entries and everyone ACEs.
- Applies `SET_INFO` security changes by parsing incoming descriptors, updating inode uid/gid/mode, setting POSIX ACLs, and persisting NTACL xattrs when share config enables ACL xattrs.
- Initializes the server domain SID from user-space startup subauthorities.

Dependencies:
- Uses VFS xattr helpers from `vfs.c`, access mapping from `smb_common.c`, share config flags, POSIX ACL APIs, and mount idmapping APIs.

Role in subsystem:
- Primary security semantic bridge for ksmbd. It lets Windows clients see and update NT-style ACLs while keeping Linux inode metadata and POSIX ACLs coherent.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/smb/server/smbacl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/smb/server/smbacl.h -->
# File Research: sources/os/linux/linux/fs/smb/server/smbacl.h

Declares ksmbd ACL state structures, security descriptor flags, ACL conversion APIs, permission checks, inheritance helpers, and idmapped POSIX ACL translation helpers.

Key contents:
- Security descriptor control flags such as `DACL_PRESENT`, `SELF_RELATIVE`, inheritance/protection flags, and defaulted flags.
- `smb_fattr`, carrying translated uid/gid/mode, desired access, and access/default POSIX ACL pointers.
- Intermediate POSIX ACL state structures used while converting SMB ACEs.
- Public APIs for parsing/building security descriptors, inheriting/checking DACLs, setting security info, SID conversion, domain initialization, and scratch sizing.
- Inline helpers to translate POSIX ACL uid/gid through mount idmaps into init-user-namespace userspace IDs visible to ksmbd.

Role in subsystem:
- Exposes the ACL conversion contract used by SMB create/query/set-info paths and VFS xattr persistence.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/smb/server/smbacl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/smb/server/smbfsctl.h -->
# File Research: sources/os/linux/linux/fs/smb/server/smbfsctl.h

Defines SMB/CIFS/SMB2 FSCTL and reparse-tag numeric constants used by ioctl handling.

Key contents:
- DFS, oplock, volume, compression, sparse, object ID, reparse point, copychunk, pipe, resume key, network interface, and negotiate-validation FSCTL codes.
- Reparse tags for mount points, HSM, SIS, and WSL/Linux special files: symlink, AF_UNIX socket, FIFO, character device, and block device.
- Many constants include comments noting missing local struct definitions or future remote-use evaluation.

Role in subsystem:
- Wire-level constant registry for SMB2 ioctl/FSCTL dispatch. It contains no behavior.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/smb/server/smbfsctl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/smb/server/stats.h -->
# File Research: sources/os/linux/linux/fs/smb/server/stats.h

Defines ksmbd runtime counters and inline counter helpers.

Key contents:
- Counter indexes for sessions, tree connections, total requests, read bytes, write bytes, and per-request-command counters.
- `struct ksmbd_counters` wraps a `percpu_counter` array when `CONFIG_PROC_FS` is enabled.
- Inline increment/decrement/add/subtract/sum helpers compile to no-ops when procfs support is disabled.
- Per-command request increments are bounds-checked against `KSMBD_COUNTER_MAX_REQS`.

Role in subsystem:
- Lightweight stats abstraction for server accounting without forcing counter overhead when procfs stats are disabled.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/smb/server/stats.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/smb/server/transport_ipc.c -->
# File Research: sources/os/linux/linux/fs/smb/server/transport_ipc.c

Implements Generic Netlink IPC between the kernel ksmbd server and the user-space ksmbd tools daemon.

Key behaviors:
- Registers a Generic Netlink family with event operations for startup, login/share/tree/RPC/SPNEGO responses, and unsupported event rejection.
- Maintains a hash table of outstanding IPC requests keyed by handle, with wait queues for synchronous request/response correlation.
- Validates daemon/kernel protocol version on inbound messages.
- Handles daemon startup, populating `server_conf` with signing, flags, port, IPC timeout, deadtime, fake fs caps, protocol bounds, max credits, max connections, interfaces, NetBIOS/server/workgroup strings, SMBDirect I/O size, and domain SID.
- Sends heartbeat requests and schedules a delayed heartbeat watchdog; missing daemon response transitions server state to resetting and queues reset work.
- Allocates and frees IPC message handles through ksmbd IDA helpers.
- Validates variable-length responses for RPC payload size, SPNEGO session key/blob lengths, share config payload/veto-list sizing, and extended-login group count.
- Provides request APIs for login, extended login, share config, tree connect/disconnect, logout, SPNEGO auth, and RPC open/close/read/write/ioctl.
- Enforces payload caps via `KSMBD_IPC_MAX_PAYLOAD` for SPNEGO and RPC data-bearing requests.

Dependencies:
- Ties together user/session/share/tree management, TCP/RDMA startup configuration, connection state, and server control work.
- Uses Generic Netlink, IDA, hash tables, wait queues, mutex/rwsem locking, and delayed work.

Role in subsystem:
- The trust boundary and configuration/authentication bridge between in-kernel SMB serving and the privileged user-space daemon.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/smb/server/transport_ipc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/smb/server/transport_ipc.h -->
# File Research: sources/os/linux/linux/fs/smb/server/transport_ipc.h

Declares the ksmbd IPC request API and lifecycle hooks.

Key contents:
- `KSMBD_IPC_MAX_PAYLOAD` fixed at 4096 bytes.
- Login, extended-login, tree connect, tree disconnect, logout, share config, SPNEGO authentication, and RPC command APIs.
- IPC handle allocation/free helpers.
- IPC release, soft reset, and init lifecycle functions.

Role in subsystem:
- Public kernel-internal interface for code that needs user-space daemon decisions or named-pipe/RPC mediation.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/smb/server/transport_ipc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/smb/server/transport_rdma.c -->
# File Research: sources/os/linux/linux/fs/smb/server/transport_rdma.c

Implements ksmbd’s SMBDirect/RDMA transport adapter on top of the shared `smbdirect_socket` infrastructure.

Key behaviors:
- Defines SMBDirect listener ports: 445 for InfiniBand/RoCE and 5445 for iWARP.
- Sets SMBDirect negotiation timeout, keepalive timings, initiator depth, send/receive credits, max send/receive sizes, fragmented receive size, and max read/write size.
- Clamps configured SMBDirect max I/O size to `SMBD_MIN_IOSIZE..SMBD_MAX_IOSIZE`.
- Allocates `ksmbd_transport` instances with ksmbd connections and inserts them into the global connection hash.
- Implements transport ops for read, writev, RDMA read, RDMA write, disconnect, shutdown, and free.
- Creates kernel SMBDirect sockets, sets initial parameters and kernel polling settings, binds/listens on the RDMA ports, and starts listener kthreads.
- Accepts SMBDirect connections and starts per-connection ksmbd handler kthreads.
- Stops and releases RDMA listeners on shutdown.
- Detects RDMA-capable netdevices using common SMBDirect node-type probing.
- Bridges SMBDirect logging into ksmbd debug/error logging.

Dependencies:
- Requires `CONFIG_SMB_SERVER_SMBDIRECT` through the header and imports namespace `SMBDIRECT`.
- Uses connection allocation/free and `ksmbd_conn_handler_loop`.

Role in subsystem:
- Optional high-performance transport layer for SMB3 over RDMA, sharing the same ksmbd connection/request engine as TCP.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/smb/server/transport_rdma.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/smb/server/transport_rdma.h -->
# File Research: sources/os/linux/linux/fs/smb/server/transport_rdma.h

Declares SMBDirect transport limits and RDMA lifecycle/query APIs.

Key contents:
- Default/min/max SMBDirect I/O sizes: 8 MiB default, 512 KiB minimum, 16 MiB maximum.
- When `CONFIG_SMB_SERVER_SMBDIRECT` is enabled, exports init, stop-listening, netdev capability, max I/O initialization, and active transport max read/write size helpers.
- When disabled, provides no-op or false/zero inline stubs.
- Includes public `<linux/smbdirect.h>`.

Role in subsystem:
- Lets core ksmbd code call RDMA support conditionally without scattering config guards.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/smb/server/transport_rdma.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/smb/server/transport_tcp.c -->
# File Research: sources/os/linux/linux/fs/smb/server/transport_tcp.c

Implements ksmbd’s TCP transport: interface binding, listener kthreads, connection accept limits, socket read/write, and network-device event handling.

Key behaviors:
- Tracks configured interfaces with listener socket, listener kthread, name, and state.
- Allocates a `tcp_transport` per client socket, creates a ksmbd connection, records IPv4/IPv6 peer address/hash, and inserts it into the global connection table.
- Accept loop enforces optional per-IP and global max-connection limits before spawning per-connection handler kthreads.
- Configures accepted sockets with receive/send timeouts.
- Implements robust `readv` with retry handling, freezer support, reconnect detection, and connection-alive checks.
- Implements `writev` using `kernel_sendmsg(... MSG_NOSIGNAL)`.
- Creates IPv6 dual-stack listener sockets when possible, falls back to IPv4, sets `TCP_NODELAY`, `SO_REUSEADDR`, and `SO_BINDTODEVICE`, then binds/listens on configured server port.
- Registers a netdevice notifier to start listeners on `NETDEV_UP` and shut them down on `NETDEV_DOWN`.
- Supports “bind all additional interfaces” when startup supplies no explicit interface list.
- Cleans interface list and unregisters notifier on destroy.

Dependencies:
- Uses server config populated by IPC startup, connection allocation/free, auth/connection helpers, kernel socket APIs, and netdevice notifications.

Role in subsystem:
- Default network transport for SMB over TCP, responsible for connection admission and byte-stream I/O before common ksmbd request handling takes over.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/smb/server/transport_tcp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/smb/server/transport_tcp.h -->
# File Research: sources/os/linux/linux/fs/smb/server/transport_tcp.h

Declares TCP transport setup, lookup, teardown, and interface configuration APIs.

Key contents:
- Interface-list configuration from startup IPC.
- Lookup of configured interface by netdevice name.
- Transport free helper.
- TCP init/destroy lifecycle functions.

Role in subsystem:
- Small public surface connecting server startup/shutdown and netdevice management to the TCP transport implementation.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/smb/server/transport_tcp.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/smb/server/unicode.c -->
# File Research: sources/os/linux/linux/fs/smb/server/unicode.c

Implements SMB string conversion between local codepages/UTF-8 and SMB UTF-16LE wire strings.

Key behaviors:
- Converts single UTF-16 code units or multiword sequences to local codepage bytes, including mapped reserved SMB characters.
- Computes converted UTF-16LE string byte length before allocation.
- Converts UTF-16LE input to local charset with destination bounds and null termination.
- Converts local strings to UTF-16LE, with a fast UTF-8 path via `utf8s_to_utf16s`.
- Falls back to `?` on invalid/unrepresentable characters.
- Supports surrogate pairs and IVS-style multiword UTF-16/UTF-8 handling for UTF-8 codepages.
- Maps POSIX-visible reserved characters such as `:`, `*`, `?`, `<`, `>`, and `|` to SMB private Unicode code points when requested.
- Provides `smb_strndup_from_utf16()` for allocating converted inbound strings.

Dependencies:
- Uses Linux NLS tables, Unicode helpers, unaligned endian access, and constants from `nls_ucs2_utils.h`.

Role in subsystem:
- Essential path/name conversion layer between SMB wire format and Linux VFS strings.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/smb/server/unicode.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/smb/server/unicode.h -->
# File Research: sources/os/linux/linux/fs/smb/server/unicode.h

Declares ksmbd Unicode/string conversion APIs.

Key contents:
- Includes byteorder, NLS, Unicode, and UCS-2 utility headers.
- Exports UTF-16 conversion, UTF-16 string duplication to local codepage, mapped UTF-16 conversion, and share-name extraction helpers under `__KERNEL__`.

Role in subsystem:
- Header for SMB path/share-name encoding and decoding helpers used by protocol and VFS paths.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/smb/server/unicode.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/smb/server/vfs.c -->
# File Research: sources/os/linux/linux/fs/smb/server/vfs.c

Implements ksmbd’s Linux VFS operation layer, mapping SMB file semantics onto kernel path, file, xattr, ACL, sparse, copy, and metadata APIs.

Key behaviors:
- Performs share-root-relative path lookup with `LOOKUP_BENEATH`, optional cross-mount following, symlink avoidance where requested, and special removal/creation lookup flows.
- Supports caseless lookup by scanning directories and comparing names with Unicode-aware `utf8_strncasecmp` when available, falling back to `strncasecmp`.
- Creates files and directories, optionally inheriting parent owner based on share config.
- Implements read/write for normal files and alternate data streams stored as xattrs.
- Enforces SMB byte-range lock conflicts before read/write/truncate/copy when POSIX extensions are not active.
- Breaks level-II oplocks before writes, truncates, zero-data, and copy-to-destination operations.
- Implements fsync, getattr, unlink/rmdir, hardlink, rename, truncate, directory-empty checks, and delete helper flows with proper mount write acquisition.
- Wraps list/get/set/remove xattr operations, including case-insensitive xattr lookup for streams.
- Maps SMB caching hints to Linux flags/readahead behavior.
- Implements sparse zero/punch operations and allocated-range queries using `SEEK_DATA`/`SEEK_HOLE`.
- Encodes and verifies NT security descriptor xattrs using NDR plus SHA-256 hashes of both NTSD and current POSIX ACL state.
- Encodes/decodes Samba-compatible DOS attribute xattrs for Windows attributes and creation time.
- Fills ksmbd stat wrappers with NT time conversion, allocation size, file attributes, and optional stored DOS attributes.
- Builds SMB stream xattr names using `user.DosStream.<name>:$DATA` or `:$INDEX_ALLOCATION`.
- Implements server-side copy chunk handling with access checks, lock checks, overlap fallback through splice, and cross-filesystem fallback.
- Initializes and inherits POSIX ACLs for new objects.

Dependencies:
- Uses VFS, xattr, POSIX ACL, NDR, SHA-256, oplock, stats, share config, session/user config, and ACL conversion helpers.

Role in subsystem:
- Main syscall-facing compatibility layer. It is where SMB file operations become safe Linux VFS operations while preserving Windows-visible metadata through xattrs.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/smb/server/vfs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/smb/server/vfs.h -->
# File Research: sources/os/linux/linux/fs/smb/server/vfs.h

Declares ksmbd VFS data structures, stream constants, create-option flags, and VFS helper APIs.

Key contents:
- Stream type enum for data streams and directory/index-allocation streams.
- Create option flags for tree connection, oplock filter reservation, readonly, and internal special handling.
- `ksmbd_dir_info`, `ksmbd_readdir_data`, and `ksmbd_kstat` structures used for directory enumeration and stat formatting.
- Prototypes for create, mkdir, read/write, fsync, remove, link, getattr, rename, truncate, copy ranges, xattrs, stream xattr names, path lookup/create/remove flows, empty directory check, fadvise, zero data, allocated ranges, unlink, stat conversion, lock wait/unblock, ACL/security descriptor xattrs, DOS attribute xattrs, and POSIX ACL init/inherit.

Role in subsystem:
- Public VFS abstraction boundary used by SMB command handlers and ACL/security code.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/smb/server/vfs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/smb/server/vfs_cache.c -->
# File Research: sources/os/linux/linux/fs/smb/server/vfs_cache.c

Implements ksmbd open-file caching, inode state tracking, file ID allocation, durable-handle preservation/reconnect, and close teardown.

Key behaviors:
- Maintains a global inode hash keyed by dentry/superblock and protected by `inode_hash_lock`.
- Tracks per-inode open file list, oplock list, delete-pending/delete-on-close flags, and attributes in `struct ksmbd_inode`.
- Maintains global durable file table and per-session volatile file tables with IDR-backed IDs.
- Enforces configurable fd limit through an atomic counter.
- Publishes open files through volatile IDs and optional durable persistent IDs.
- Provides fast/slow/foreign/global/durable lookups with refcount acquisition and tree/persistent ID sanity checks.
- Handles delete-on-close for normal files and stream xattrs; final inode close unlinks pending-delete files.
- Cleans oplocks, byte-range locks, connection references, stream names, durable owner names, and file references during final close.
- Provides tree-connection and session-wide fd close loops with careful locking/refcount handling for in-flight opens and durable preservation.
- Preserves reconnectable durable/resilient/persistent handles across session teardown by detaching `conn`/`tcon`, clearing volatile IDs, storing durable owner identity, removing connection lock/oplock associations, and setting scavenger timeout.
- Runs a durable handle scavenger kthread that expires preserved handles after timeout and safely disposes them.
- Validates durable reconnect path name and reopens durable fds into a new session/connection with lock/oplock reattachment.
- Provides procfs file listing of open handles, access masks, refcounts, and oplock/lease state when procfs is enabled.
- Initializes/destroys file tables, global file table, inode hash, and file slab cache.

Dependencies:
- Uses oplock management, VFS unlink/xattr helpers, connection refs, session/tree/user config, IDR, rwlocks, rwsems, wait queues, freezer-aware kthreads, and procfs helpers.

Role in subsystem:
- Lifetime and identity core for ksmbd open files. It prevents stale handle use, supports SMB durable handles, and coordinates delete-on-close and oplock cleanup.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/smb/server/vfs_cache.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/smb/server/vfs_cache.h -->
# File Research: sources/os/linux/linux/fs/smb/server/vfs_cache.h

Declares ksmbd file/inode cache structures, fid constants, lock/stream state, durable owner metadata, and file-table APIs.

Key contents:
- Windows generic access constants and fid sentinel values.
- `ksmbd_lock` for SMB byte-range lock tracking across connection/file/global lists.
- `stream` for alternate data stream xattr state.
- `ksmbd_inode` for per-dentry shared state: locks, refcounts, open lists, oplocks, attributes, delete flags.
- `ksmbd_file` for per-open handle state: file pointer, persistent/volatile IDs, connection/tree, access/share/create options, times, GUIDs, stream, locks, readdir state, durable/resilient/persistent flags, POSIX-context flag, and durable owner.
- `ksmbd_file_table` wrapping an IDR with lock.
- Inline helpers for valid file IDs and stream handles.
- Public APIs for file-table init/destroy, open/close/lookup/put, inode lookup/put/status, durable lookup/open/reopen/scavenger, tree/session close, global file table init/free, fd limit, file state update, durable owner comparison, inode hash lifecycle, delete-on-close flags, and file cache lifecycle.

Role in subsystem:
- Shared type and API definition for ksmbd handle management.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/smb/server/vfs_cache.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/smb/server/xattr.h -->
# File Research: sources/os/linux/linux/fs/smb/server/xattr.h

Defines Samba-compatible xattr metadata formats used by ksmbd to preserve Windows filesystem semantics on POSIX filesystems.

Key contents:
- DOS attribute validity flags for attribute, EA size, size, allocation size, create time, change time, and initial time.
- `xattr_dos_attrib` for DOS attributes and Windows timestamps stored in `user.DOSATTRIB`.
- POSIX ACL entry/tag enums and `xattr_smb_acl` flexible-array structure used to hash current POSIX ACL state.
- NTACL xattr hash constants and `xattr_ntacl`, storing version, encoded security descriptor, hash type, descriptor label, timestamp, NTSD hash, and POSIX ACL hash.
- Xattr name prefixes and lengths for DOS attributes, alternate data streams, and security descriptors: `user.DOSATTRIB`, `user.DosStream.`, and `security.NTACL`.

Role in subsystem:
- On-disk metadata contract for interoperability with Samba and for preserving Windows attributes, streams, creation time, and NT ACLs.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/smb/server/xattr.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/smb/smbdirect/Kconfig -->
# File Research: sources/os/linux/linux/fs/smb/smbdirect/Kconfig

Defines the `SMBDIRECT` kernel configuration option.

Key contents:
- `config SMBDIRECT` defaults to `n`.
- Depends on `INFINIBAND` and `INFINIBAND_ADDR_TRANS`.
- Requires module-compatible InfiniBand availability through `depends on m || INFINIBAND=y`.
- Selects `SG_POOL`.

Role in subsystem:
- Build-time gate for the common SMBDirect support module used by ksmbd RDMA transport.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/smb/smbdirect/Kconfig -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/smb/smbdirect/Makefile -->
# File Research: sources/os/linux/linux/fs/smb/smbdirect/Makefile

Build rules for the SMBDirect support module.

Key contents:
- Builds `smbdirect.o` when `CONFIG_SMBDIRECT` is enabled.
- Aggregates SMBDirect implementation objects: `socket.o`, `connection.o`, `mr.o`, `rw.o`, `debug.o`, `connect.o`, `listen.o`, `accept.o`, `devices.o`, and `main.o`.

Role in subsystem:
- Connects the common SMBDirect object set to Kbuild so server/client RDMA transport users can import the `SMBDIRECT` namespace.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/smb/smbdirect/Makefile -->