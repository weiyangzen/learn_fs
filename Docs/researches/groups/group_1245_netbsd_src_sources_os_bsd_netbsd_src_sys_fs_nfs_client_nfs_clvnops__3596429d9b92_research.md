# Group Research: group_1245_netbsd_src_sources_os_bsd_netbsd_src_sys_fs_nfs_client_nfs_clvnops__3596429d9b92

Static research for the listed NetBSD NFS client/common files in subset A. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/nfs/client/nfs_clvnops.c -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/nfs/client/nfs_clvnops.c

## Purpose
Implements the main vnode operation layer for the “newnfs” client, covering NFSv2, NFSv3, and NFSv4 regular vnode operations plus FIFO wrappers and buffer write operations. It is the bridge between NetBSD/FreeBSD-style VFS vnode calls and lower NFS RPC helpers such as `nfsrpc_*`, `ncl_bioread`, `ncl_doio`, `ncl_flush`, and NFSv4 delegation/state helpers.

## Main Interfaces
- Exports `newnfs_vnodeops`, the vnode op vector for normal NFS vnodes: lookup, open, close, getattr, setattr, read/write, create/remove/rename/link, directory ops, strategy, fsync, ACL, locks, and paging hooks.
- Exports `newnfs_fifoops`, the vnode op vector for NFS-hosted FIFOs, wrapping FIFO operations while updating NFS-side access/update timestamps.
- Exports lower helper entry points used by other NFS client modules: `ncl_readlinkrpc`, `ncl_readrpc`, `ncl_writerpc`, `ncl_readdirrpc`, `ncl_readdirplusrpc`, `ncl_commit`, `ncl_flush`, `ncl_removeit`, and `ncl_writebp`.
- Exports `buf_ops_newnfs`, connecting buffer-cache writes to `nfs_bwrite`/`ncl_writebp`.

## Key Behavior
- `nfs_access` implements local read-only mount checks, NFSv3/v4 `ACCESS` RPC checks, access-result caching by UID, and NFSv2 fallback behavior using local mode checks plus a root-read probe.
- `nfs_open` performs NFSv4 `OPEN` before cache validation, then enforces close-to-open coherency by comparing cached modify/change state, invalidating buffers when needed, handling `O_DIRECT`, and storing write credentials for later pageout.
- `nfs_close` pushes dirty VM pages and buffers on close, handles NFSv3 commit policy, NFSv4 close/delegation requirements, propagates delayed write errors, updates change attributes, and unwinds direct I/O open state.
- `nfs_getattr` first consults the attribute cache, optionally primes the access cache, falls back to `GETATTR`, and overlays delegated local modify time.
- `nfs_setattr` validates unsupported fields, handles truncation carefully through `ncl_meta_setsize` and buffer invalidation, rolls back size on RPC failure, and invalidates access/delegation state through `nfs_setattrrpc`.
- `nfs_lookup` combines namecache hits with NFS attribute/change validation, negative cache validation, NFSv4 remove-in-progress waits, special dot/dotdot locking rules, RPC lookup, node instantiation, and namecache entry creation.
- Create-like operations (`nfs_create`, `nfs_mknod`, `nfs_symlink`, `nfs_mkdir`) issue RPCs, load returned attributes when present, perform lookup fallback when handles are not returned, and mark parent directories modified.
- Remove/rename behavior includes sillyrename support for active files, directory and vnode cache purging, ENOENT retry-success mapping for idempotency edge cases, NFSv4 name metadata updates, and parent attr invalidation.
- Directory reads use logical offset to NFS cookie mapping through `ncl_getcookie`, EOF offset caching, and separate `READDIR`/`READDIRPLUS` RPC paths.
- `ncl_flush` is the central dirty-buffer flush/commit loop: it collects `B_NEEDCOMMIT` buffers, issues range commits, handles stale write verifiers, writes dirty buffers, waits for output/direct I/O completion, updates `NMODIFIED`, and retries boundedly.
- Advisory locking supports NFSv4 byte-range locks via RPC with RFC3530 coherency flush/invalidation behavior, and falls back to local/lockd paths for older NFS depending on mount flags.
- NFSv4 ACL vnode ops delegate to `nfsrpc_getacl`/`nfsrpc_setacl`; `nfs_pathconf` uses NFS pathconf/getattr where useful and fakes stable POSIX values otherwise.

## Important State
- Uses `struct nfsnode` fields including `n_flag`, `n_size`, `n_vattr`, `n_attrstamp`, `n_accesscache`, `n_mtime`, `n_change`, `n_direofoffset`, `n_cookies`, `n_sillyrename`, `n_directio_opens`, `n_directio_asyncwr`, and `n_writecred`.
- Uses `struct nfsmount` fields for mount flags, negative/positive namecache timeouts, pNFS capability, async I/O, write verifier state, and timeout/interruption behavior.
- Sysctls tune access cache timeout, access-cache priming, commit-on-close, clean-pages-on-close, direct I/O behavior, and dirty-page retry policy.

## Dependencies
Depends heavily on `nfsnode.h`, `nfsmount.h`, client RPC helpers, NFSv4 state/delegation helpers, VFS namecache and vnode locking APIs, VM object/page cleaning APIs, buffer-cache APIs, lockf/lockd integration, and DTrace probe macros from `nfs_kdtrace.h`.

## Risks and Edge Cases
- Cache coherency is distributed across namecache timestamps, attribute cache stamps, delegation state, directory EOF cookies, and close/open flushes; changes must preserve these interactions.
- `ncl_flush` has complex buffer locking, two-pass commit/write behavior, and signal/forced-unmount exits; regression risk is high for deadlocks, dirty-buffer loss, and spurious EINTR/EIO.
- Sillyrename intentionally approximates local unlink semantics over stateless NFS and has race windows with other clients.
- NFSv4 error mapping and state-sequence handling are delegated to lower RPC/state layers; vnode ops often must map only after RPC helpers return protocol errors.
- The file carries FreeBSD-derived API assumptions and NetBSD porting glue, so portability edits need careful kernel API verification.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/nfs/client/nfs_clvnops.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/nfs/client/nfs_kdtrace.h -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/nfs/client/nfs_kdtrace.h

## Purpose
Declares DTrace/KDTRACE probe identifiers and probe-call macros for NFS client access-cache and attribute-cache events.

## Main Interfaces
- Declares access-cache probe IDs: flush done, get hit, get miss, and load done.
- Declares attribute-cache probe IDs: flush done, get hit, get miss, and load done.
- When `KDTRACE_HOOKS` is enabled, macros invoke function pointers from `<sys/dtrace_bsd.h>` only if the relevant probe is registered.
- When `KDTRACE_HOOKS` is disabled, all macros compile to no-ops.

## Integration
Used by `nfs_clvnops.c` and related cache code to instrument cache invalidation, lookup hits/misses, and cache reload completion without imposing runtime overhead when tracing is disabled.

## Risks
- Probe macros assume the DTrace hook declarations match the argument signatures exactly.
- Since the non-KDTRACE path is empty, tracing code must not rely on side effects inside macro arguments.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/nfs/client/nfs_kdtrace.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/nfs/client/nfsmount.h -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/nfs/client/nfsmount.h

## Purpose
Defines the client-side `struct nfsmount`, the per-mount state object for NFS client mounts.

## Main Data
- Embeds `struct nfsmount_common nm_com`, sharing mount lock, flags, state, timeout, hostname, and callback hooks with common NFS/NLM code.
- Stores root file handle, socket/RPC transport state (`struct nfssockreq`), timeout counters, negotiated read/write/readdir sizes, readahead, commit size, attr-cache lifetimes, write verifier, async buffer queue state, and max file size.
- Tracks namecache lifetimes with `nm_nametimeo` and `nm_negnametimeo`.
- Adds NFSv4/newnfs state: session list, client pointer, mount/system UID, client-id discriminator, fsid, minor version, Kerberos principal lengths, server principal length, and variable-length name storage.

## Main Macros
- `VFSTONFS(mp)` converts a mount to its NFS mount state.
- `NFSMNT_MDSSESSION(m)` returns the metadata-server session, assumed to be the first session.
- `NFSMNT_DIRPATH(m)` and `NFSMNT_SRVKRBNAME(m)` slice variable-length name storage.
- Field aliases expose common and socket fields as direct `nm_*` names.

## Integration
Consumed by vnode operations, RPC connection setup, NFSv4 session/state management, pNFS paths, and mount option handling.

## Risks
- Variable-length `nm_name[1]` storage depends on allocation sizing and offset macros; incorrect length accounting can corrupt principal/path strings.
- `NFSMNT_MDSSESSION` assumes the session queue is non-empty and ordered.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/nfs/client/nfsmount.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/nfs/client/nfsnode.h -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/nfs/client/nfsnode.h

## Purpose
Defines the client-side `struct nfsnode`, the NFS equivalent of an inode attached to each active NFS vnode, plus related directory-cookie, access-cache, and sillyrename structures.

## Main Data
- `struct sillyrename` stores credentials, parent directory vnode, and temporary `.nfs...` name for deferred unlink of active files.
- `struct nfsdmap` stores logical directory offset to NFS cookie mappings in chunks of `NFSNUMCOOKIES`.
- `struct nfs_accesscache` caches NFS `ACCESS` result bits by UID and timestamp.
- `struct nfsnode` stores mutex-protected per-vnode state: file size, attribute cache, access cache, mtimes/change attributes, NFS file handle, vnode/parent pointers, lockf pointer, write error, special-file times or directory cookie verifier/EOF, sillyrename or directory cookie list, flags, direct I/O counters, NFSv4 node extension, and write credential.

## Flags
Important `n_flag` bits include directory cookie lock, fsync wait, modified/write-error state, create/truncate markers, size/cache invalidation markers, special-file access/update/change flags, delegation recall/modified flags, remove-in-progress/wait flags, node sleep lock flags, pNFS layout denial, write-open tracking, and “has been locked” tracking.

## Interfaces
Declares vnode/page/cache helpers implemented elsewhere: `ncl_getpages`, `ncl_putpages`, `ncl_write`, inactive/reclaim, `ncl_removeit`, `ncl_nget`, `ncl_getcookie`, directory invalidation, vnode lock upgrade/downgrade, and directory-cookie lock/unlock.

## Integration
Used directly by `nfs_clvnops.c` for nearly every vnode operation and by lower I/O and node-cache code.

## Risks
- Several unions reuse storage depending on vnode type, so callers must respect regular-file, directory, symlink, and special-file contexts.
- Many fields are protected by `n_mtx`; missed locking can corrupt cache stamps, flags, size, direct I/O counters, and sillyrename state.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/nfs/client/nfsnode.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/nfs/client/nlminfo.h -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/nfs/client/nlminfo.h

## Purpose
Defines `struct nlminfo`, small per-process/per-locking context state used by NLM-based advisory locking.

## Main Data
- `msg_seq`: sequence counter for lock requests.
- `retcode`: return code from lock requests.
- `set_getlk_pid` and `getlk_pid`: PID bookkeeping for `F_GETLK` style interactions.
- `pid_start`: process start time used to disambiguate lock owners across PID reuse.

## Integration
Used by NFS/NLM lock manager code outside this group to preserve state needed by the master lockd process and by processes doing NLM locking.

## Risks
Small state carrier only; correctness depends on external lockd/NLM code updating sequence and PID fields consistently.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/nfs/client/nlminfo.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/nfs/common/bootp_subr.c -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/nfs/common/bootp_subr.c

## Purpose
Implements kernel BOOTP/DHCP discovery for diskless NFS-root boot. It finds eligible network interfaces, temporarily configures them, sends BOOTP/DHCP packets, decodes replies, configures the selected interface, retrieves an NFS root file handle from mountd, and fills `nfsv3_diskless`.

## Main Data
- `struct bootp_packet` models RFC951 BOOTP packets with a large vendor/options area.
- `struct bootpc_ifcontext` stores per-interface query/reply packets, ifreq/in_aliasreq state, link address, IP/netmask/gateway, DHCP negotiation state, root-path flags, and MTU.
- `struct bootpc_tagcontext` stores decoded option data and parser error/overload state.
- `struct bootpc_globalcontext` tracks all interface contexts, global xid/time, root-path/hostname selection, current reply, and temporary option buffers.
- Global `bootp_cookie` stores site option 134 for sysctl/userland exposure; `bootp_so` is the UDP socket used for discovery.

## Key Flow
- `bootpc_init` exits if diskless config is already valid, allocates contexts, finds broadcast-capable Ethernet/FDDI/Token Ring interfaces or a `BOOTP_WIRED_TO` interface, creates a UDP socket, fakes interfaces up with `0.0.0.0/8`, composes queries, calls `bootpc_call`, decodes accepted replies, adjusts or shuts down interfaces, and optionally performs root mount discovery.
- `bootpc_compose_query` builds BOOTP or DHCP DISCOVER/REQUEST packets with RFC1048 cookie, maximum message size, vendor identifier, requested address/server ID, lease time, and broadcast flag.
- `bootpc_call` sets socket timeout/broadcast/dontroute, binds to client port 68, sends packets to broadcast server port 67, temporarily switches interface masks for sending, receives replies, matches xid/hardware address, accepts or ignores replies through `bootpc_received`, and handles retries/settle delays/timeouts.
- `bootpc_received` validates option parsing, enforces expected DHCP message type, stores better replies, advances DHCP state, and notes root path, router, netmask, and DHCP server ID availability.
- `bootpc_decode_reply` extracts assigned IP, server/gateway, subnet mask, routers, root path, root mount options, hostname, cookie, and MTU. It supports environment/rootdev overrides for NFS root.
- `bootpc_adjust_interface` installs final IP/netmask/broadcast/MTU on resolved interfaces; failed interfaces are shut down.
- `md_mount` uses `krpc_portmap` and `krpc_call` to talk to mountd, optionally tries NFSv3 first, falls back to v2, decodes mount reply file handle and auth flavors, and resolves the NFS service port.

## Helpers
Includes IPv4 parser helpers (`getip`, `getdec`), root path parser (`setmyfs`), NFS mount option defaults (`mountopts`), local XDR decode helpers, BOOTP option parsing with overload support, default route add/remove around mountd access, and optional BOOTP debug route/interface printers.

## Dependencies
Depends on kernel sockets, interface ioctl APIs, routing APIs, NFS diskless structures, NFS mount argument parsing, NFS protocol constants, and the small KRPC helper API in `krpc.h`/`krpc_subr.c`.

## Risks and Edge Cases
- Runs during early boot and uses `panic` for many unexpected interface/ioctl/parser failures.
- Only IPv4 BOOTP/DHCP is implemented.
- Option parsing supports overload and concatenated tags, but malformed options can invalidate replies.
- Interface manipulation is invasive: temporary addresses/masks/routes must be restored or adjusted correctly.
- Root selection has precedence interactions between server-provided root path, `vfs.root.mountfrom`, `ROOTDEVNAME`, and boot flags.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/nfs/common/bootp_subr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/nfs/common/krpc.h -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/nfs/common/krpc.h

## Purpose
Declares the minimal kernel SunRPC helper API used primarily by diskless NFS boot code.

## Interfaces
- `krpc_call`: performs a UDP RPC call to an IPv4 server and returns reply mbuf data.
- `krpc_portmap`: resolves an RPC program/version to a UDP port using portmapper.
- `xdr_string_encode`: creates an mbuf containing an XDR-counted padded string.
- Defines portmapper constants: fixed port 111, program/version, and procedures including `GETPORT`.

## Integration
Used by `bootp_subr.c` to contact mountd and resolve NFS/mountd ports while bootstrapping NFS root.

## Risks
Header prototypes mix `struct thread` forward declaration with `struct lwp *td` in the declarations, reflecting porting compatibility assumptions in this source tree.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/nfs/common/krpc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/nfs/common/krpc_subr.c -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/nfs/common/krpc_subr.c

## Purpose
Implements a small kernel UDP SunRPC client for NFS diskless bootstrapping. It is simpler than the main reconnecting NFS RPC layer and is used for portmapper/mountd calls during early NFS-root setup.

## Main Interfaces
- `krpc_portmap` builds a portmapper `GETPORT` request and calls `krpc_call`; it special-cases the portmapper program itself to return port 111.
- `krpc_call` creates a UDP socket, sets receive timeout, optionally enables broadcast, binds a reserved local port, prepends an AUTH_UNIX-root RPC header, retransmits with increasing timeout, validates replies by xid/direction/status, strips the RPC reply header, and returns the result mbuf.
- `xdr_string_encode` encodes a counted, padded XDR string into an mbuf.

## Protocol Details
- Uses AUTH_UNIX credentials with root-like empty host/group fields and AUTH_NULL verifier.
- Supports only `AF_INET`/UDP.
- Uses a static monotonically increasing xid.
- Retransmit delay grows up to `MAX_RESEND_DELAY`, then prints timeout messages.
- Handles RPC accept errors, program mismatch, and status errors, but keeps retrying for many denial/status cases unless a hard mismatch is detected.

## Dependencies
Uses kernel socket APIs (`socreate`, `sosetopt`, `sobind`, `sosend`, `soreceive`, `soclose`), mbuf APIs, XDR byte-order helpers, and constants from `krpc.h`.

## Risks
- Not a general-purpose RPC layer: IPv4-only, UDP-only, AUTH_UNIX-only.
- Static xid is not explicitly synchronized.
- `xdr_string_encode` returns `NULL` for strings larger than one cluster but callers must handle that.
- Long retry loop is intended for bootstrapping but can block boot progress on unreachable servers.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/nfs/common/krpc_subr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/nfs/common/nfs.h -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/nfs/common/nfs.h

## Purpose
Defines shared NFS constants, flags, request descriptors, credential structures, file-handle structures, and helper macros used by client, server, callback, locking, and RPC code.

## Main Constants
- Timeout/retry/window constants for NFS client RPC, callbacks, upcalls, retransmits, read/write/readdir defaults, async daemon limits, uid hash sizes, lease lifetimes, cache high-water marks, and NFSv4 callback port.
- NFSv4 server/client state limits for delegations, layouts, clients, sessions, and locks.
- Attribute bitset word count and macros for supported, get, write, pathconf, statfs, readdirplus, referral, callback-getattr, settable/fillable, equality, nonzero, set/clear/copy operations.

## Main Structures
- `nfsd_addsock_args`, `nfsd_nfsd_args`, `nfsd_nfscbd_args`, `nfscbd_args`, `nfsd_idargs`, and `nfsd_oidargs` define `nfssvc(2)`/daemon/user-id mapping arguments.
- Dump/list structures describe NFSv4 clients, locks, client IDs, lock owners, and callback addresses.
- `nfsreferral` stores referral server-list metadata.
- `nfscred` stores UID and groups associated with acquired stateids.
- `nfssockreq` stores per-connection RPC transport state: address, socket type/protocol/flags, credential, lock bits, mutex, RPC program/version, client handle, and cached auth handle.
- `nfsrv_descript` is the central request/reply XDR descriptor: mbuf chains and positions, socket addresses, proc number, flags, status, xid/cache pointers, file handle, credentials, GSS principal, session/slot data, and server transport.
- `nfsv4_opflag`, `nfsfh`, `nfsrvfh`, `nfsv4lock`, and `nfsslot` define operation metadata, client/server file handles, sleep locks, and NFSv4.1 slot state.

## Main Flags
- Client/server flags for NFS versions, GSS modes, stream sockets, public lookup, implied client IDs, NFSv4.1/session/sequence state, callback direction, reply caching, and no-more-data parsing.
- NFSv4 client flags (`LCL_*`) for callback, GSS, confirmation, cleanup, reclaim, and lease/client state.
- NFS lock/state flags (`NFSLCK_*`) encode access/deny bits, lock/read/write/blocking/test/open/close/release/delegation/reclaim/downgrade/setattr/want states.
- `NFSR_*` bits describe send/receive/reserved-port/local transport state.

## Integration
This is a core include for files in this group: `nfsmount.h` embeds `nfssockreq`; `nfs_commonkrpc.c` operates on `nfsrv_descript` and `nfssockreq`; `nfs_clvnops.c` depends on flags, attr bit macros, timeouts, and file-handle comparisons.

## Risks
- Many macros manually assume `NFSATTRBIT_MAXWORDS == 3`; changing the attribute bitset size requires coordinated macro updates.
- Several structures are ABI-facing through `nfssvc(2)` or daemon interaction; field changes are compatibility-sensitive.
- The file mixes client, server, callback, and syscall concepts, so “small” edits can have broad blast radius.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/nfs/common/nfs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/nfs/common/nfs_common.h -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/nfs/common/nfs_common.h

## Purpose
Provides shared NFS XDR build/dissection helpers and type-conversion macros for common NFS encode/decode paths.

## Main Interfaces
- Extern arrays `nv3tov_type` and `nfsv3_type` convert between NFSv3 wire file types and vnode types.
- `vtonfsv2_mode`, `nfsv3tov_type`, and `vtonfsv3_type` convert vnode type/mode to NFS wire values.
- Declares lower helpers `nfs_adv`, `nfsm_disct`, `nfs_realign`, `nfsm_build_xx`, `nfsm_dissect_xx`, `nfsm_dissect_xx_nonblock`, `nfsm_strsiz_xx`, and `nfsm_adv_xx`.
- Macros `nfsm_build`, `nfsm_dissect`, `nfsm_dissect_nonblock`, `nfsm_strsiz`, `nfsm_mtouio`, and `nfsm_adv` wrap helper calls and enforce common error handling via `goto nfsmout`.
- Defines `nfsm_rndup` for XDR four-byte alignment and `nfsm_aligned` depending on strict-alignment architecture.

## Integration
Used by NFS encode/decode code that follows the classic local-variable convention (`mb`, `bpos`, `md`, `dpos`, `mrep`, `error`, `nfsmout`).

## Risks
- Macro control flow requires callers to define expected local variable names and a `nfsmout` label.
- Incorrect size/alignment inputs can cause bad XDR parsing or mbuf traversal errors.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/nfs/common/nfs_common.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/nfs/common/nfs_commonacl.c -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/nfs/common/nfs_commonacl.c

## Purpose
Implements common NFSv4 ACL encode/decode, permission-mask translation, ACL setting, and ACL comparison helpers shared by NFS client/server code.

## Main Interfaces
- `nfsrv_dissectace` decodes one NFSv4 ACE from XDR into a kernel `acl_entry`, resolving special principals and named users/groups.
- `nfsrv_buildacl` serializes a kernel NFSv4 ACL to XDR ACEs and writes the entry count.
- `nfsrv_setacl` validates ACL support and size constraints, then calls `VOP_SETACL`.
- `nfsrv_compareacl` compares two ACLs for count, tag/id, and permission equality.
- Static `nfsrv_acemasktoperm` maps NFSv4 ACE mask bits to kernel ACL permission bits.

## Decode Behavior
- Handles special principals `OWNER@`, `GROUP@`, and `EVERYONE@`.
- Uses `nfsv4_strtouid`/`nfsv4_strtogid` for named user/group principals.
- Converts NFSv4 flags to `ACL_ENTRY_*` inheritance/audit flags.
- Converts allow/deny/audit/alarm ACE types to kernel entry types.
- Rejects unsupported flag or mask bits with `NFSERR_ATTRNOTSUPP`.
- Treats zero-length who strings from some NetApp filers as an undefined deny entry.

## Encode Behavior
- Converts kernel ACL tags back to special strings or user/group name strings using `nfsv4_uidtostr`/`nfsv4_gidtostr`.
- Maps directory permissions to `LISTDIRECTORY`, `ADDFILE`, `ADDSUBDIRECTORY`, `SEARCH`, etc., and non-directory permissions to `READDATA`, `WRITEDATA`, `APPENDDATA`, `EXECUTE`, etc.
- Preserves supported inheritance/audit flags and group identifier flag.

## Dependencies
Depends on NFS XDR macros, NFSv4 ACL constants, kernel ACL types, uid/gid string mapping helpers, `nfs_supportsnfsv4acls`, and `VOP_SETACL`.

## Risks
- Directory and regular-file permission masks differ; using the wrong vnode type when building ACEs changes wire semantics.
- Name-string conversion can allocate dynamically; callers rely on correct free behavior for returned buffers.
- `nfsrv_compareacl` compares only selected fields and does not consider all possible ACE metadata such as entry type/flags in every case.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/nfs/common/nfs_commonacl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/nfs/common/nfs_commonkrpc.c -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/nfs/common/nfs_commonkrpc.c

## Purpose
Implements the main reconnecting RPC transport path used by the new NFS client and NFSv4 callback/upcall code. It manages RPC client creation, authentication, request execution, NFS reply parsing, NFSv4 sequence-slot handling, retry/backoff policy, interruptible mount signal handling, and server up/down notifications.

## Main Interfaces
- `newnfs_connect` creates/configures an RPC client for an `nfssockreq`, including socket buffer reservation sizing, reserved-port/connect behavior, soft/hard retry settings, UDP retry timeout, and optional NFSv4 backchannel setup.
- `newnfs_disconnect` purges GSS state, closes, and releases an RPC client.
- `newnfs_request` sends an NFS request mbuf, handles auth selection, RPC invocation, reply realignment/parsing, NFSv4 compound status handling, retryable errors, slot freeing, stale cache invalidation, DTrace probes, and cleanup.
- `newnfs_nmcancelreqs` closes an active client to cancel requests during forced unmount.
- `newnfs_set_sigmask`, `newnfs_restore_sigmask`, `newnfs_msleep`, and `newnfs_sigintr` implement signal handling for interruptible NFS mounts.

## Connection Behavior
- Temporarily switches thread credentials to mount/socket credentials while creating and configuring sockets.
- Selects `udp`, `tcp`, `udp6`, or `tcp6` netconfig based on address family and socket type.
- Preflights socket buffer reservation with `soreserve`, shrinking `nfs_bufpackets` scale if needed.
- Uses `clnt_reconnect_create` and sets wait channel, interruptibility, reserved-port use, retries, UDP retry timeout, and optional NFSv4.1 backchannel transport.
- Protects `nr_client` publication with `nr_mtx` so concurrent connect attempts do not install duplicate clients.

## Authentication
- `nfs_getauth` selects RPCSEC_GSS Kerberos modes (`krb5`, integrity, privacy) when requested, otherwise falls back to AUTH_SYS.
- `newnfs_request` chooses credentials from the caller, mount system credential, host principal, server principal, callback client flags, or NFSv4 system-operation flags.
- Cached host-principal auth may be stored in `nrp->nr_auth` and refreshed instead of destroyed per request.

## Request/Reply Flow
- Rejects requests during forced unmount and masks selected signals for interruptible client mounts.
- Connects lazily if no RPC client exists.
- Maps NFSv2 proc numbers through `nfsv2_procid`; NFSv4 non-null client calls use COMPOUND.
- Optionally records outstanding NFSv4 requests in `nfsd_reqq` for recovery-related flags.
- Emits KDTRACE start/done probes when compiled with hooks.
- Invokes `CLNT_CALL_MBUF` or `clnt_bck_call` for backchannel calls.
- Converts RPC-level failures to kernel errors and frees request mbufs on failure.
- Realigns reply mbufs, extracts NFS status, strips NFSv4 compound tag/op-count/sequence results, updates session slot sequence/window state, and detects op status.
- Retries `NFSERR_DELAY`, `NFSERR_GRACE`, and resource-style errors with exponential delay, with exceptions for non-idempotent/state-changing NFSv4 operations.
- Invalidates vnode/name caches on stale file-handle replies when possible.
- Marks `ND_INCRSEQID`, `ND_NOMOREDATA`, or `NFSERR_STALEDONTRECOVER` according to NFSv4 operation status.

## Notification and Signal Helpers
- `nfs_feedback` receives RPC reconnect/retransmit/OK callbacks and triggers `nfs_down`/`nfs_up`.
- `nfs_down`/`nfs_up` update mount state bits, emit VFS events (`VQ_NOTRESP`, `VQ_NOTRESPLOCK`), and print user-visible server status messages.
- `newnfs_sigintr` detects selected pending signals for `NFSMNT_INT` mounts and forced unmounts.

## Tunables
Defines sysctls for buffer packet scaling, reconnect count, NFSv3 jukebox delay, and weak-cache-consistency-on-error behavior.

## Dependencies
Depends on kernel RPC client APIs, GSS/Kerberos hooks, NFS mount/session structures, NFS request queues and locks, VFS events, signal APIs, mbuf XDR helpers, and DTrace probe arrays.

## Risks
- `newnfs_request` is highly stateful: changes can affect authentication lifetime, request mbuf ownership, NFSv4 slot leaks, seqid increments, retries, and stale-state recovery.
- Lazy connect and concurrent publication require careful `nr_mtx` discipline.
- Signal masking for interruptible mounts modifies thread signal state around sleeps/RPCs and must always restore it.
- Retry policy deliberately avoids replaying certain NFSv4 state-changing operations; broadening retries can break protocol correctness.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/nfs/common/nfs_commonkrpc.c -->