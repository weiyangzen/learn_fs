# Group Research: group_493_illumos_gate_sources_os_illumos_illumos_gate_usr_src_uts_common_fs_s_ba431f6c6c2b

Scope: subset A from `Docs/research_subset_a.md`, covering the listed illumos SMB client `netsmb` and `smbfs` files. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbclnt/netsmb/smb_subrs.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbclnt/netsmb/smb_subrs.c

## Scope

This file provides shared netsmb helpers for credential lifetime, debug/error reporting, SMB/NT status translation, on-the-wire string conversion, SMB1/SMB2 create/close dispatch, and common read/write UIO chunking.

## APIs And Behavior

- `smb_credinit()` and `smb_credrele()` wrap kernel credentials for SMB operations. On labeled systems, credentials are duplicated and marked `NET_MAC_AWARE`.
- `smb_errmsg()` backs SMB debug/error macros, sending debug events to DTrace and non-debug errors to `vcmn_err()`.
- `m_dumpm()` emits DTrace probes describing STREAMS mblk chains.
- Large static tables map NT status values to Unix errno and DOS error class/code values.
- `smb_maperr32()` maps NT status to errno, first through direct NT-to-errno mapping, then through NT-to-DOS and DOS-to-errno fallback.
- `smb_doserr2status()` maps DOS class/code pairs back to NT status.
- `smb_maperror()` maps classic SMB DOS/SRV/HRD error classes to errno, logging unknown values.
- `smb_get_dstring()` decodes SMB strings from wire form into UTF-8, using UTF-16LE conversion when Unicode negotiation is active.
- `smb_put_dmem()` and `smb_put_dstring()` encode SMB path/name data into mbchains, with UTF-8 to UTF-16LE conversion and Unicode alignment padding.
- `smb_smb_ntcreate()` and `smb_smb_close()` dispatch common file-handle operations to SMB2 or SMB1 implementations based on `SMBV_SMB2`.
- `smb_rwuio()` dispatches SMB1 readx/writex or SMB2 read/write and chunks transfers according to negotiated maximum I/O sizes.

## State And Dependencies

- Depends on `netsmb/smb_conn.h`, `smb_rq.h`, `smb_subr.h`, mchain helpers, NT status constants, SMB1/SMB2 request implementations, and illumos credential/DTrace facilities.
- `smb1_large_io_max` caps SMB1 large read/write requests at 60 KiB despite protocol maxima.

## Risks And Invariants

- NT/DOS error mapping is policy-sensitive; unmapped statuses collapse to `EIO`.
- String conversion assumes modern Unicode-capable servers; non-Unicode paths are copied as-is with comments noting missing OEM conversion.
- `smb_rwuio()` relies on lower-level I/O functions updating the `uio`; double-updating would corrupt offsets and residuals.
- On partial transfer followed by error, `smb_rwuio()` suppresses the error to preserve POSIX short-I/O semantics.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbclnt/netsmb/smb_subrs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbclnt/netsmb/smb_time.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbclnt/netsmb/smb_time.c

## Scope

This file implements SMB time conversion helpers between NT time, Unix `timespec`, and old SMB server-local second values.

## APIs And Behavior

- `DIFF1970TO1601` is the seconds offset between the Unix epoch and NT epoch.
- `TEN_MIL` is the number of 100 ns NT time units per second.
- `smb_time_NT2local()` converts NT time to Unix seconds/nanoseconds, clamping pre-1970 values to zero.
- `smb_time_local2NT()` converts Unix time to NT time, preserving Unix time zero as NT time zero.
- `smb_time_local2server()` converts Unix time to old server seconds by subtracting a timezone offset in minutes, clamping underflow to zero.
- `smb_time_server2local()` converts old server seconds to Unix `timespec` by adding the timezone offset and zeroing nanoseconds.

## Dependencies

- Used by SMB file attribute encoding and decoding paths.
- Includes SMB connection and subr headers, but the implementation is self-contained arithmetic.

## Risks And Invariants

- NT time conversions are GMT-based and deliberately do not apply timezone offsets.
- Old dialect conversions use minute offsets and preserve server zero as local zero.
- Nanosecond precision is truncated to 100 ns units when converting to NT time.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbclnt/netsmb/smb_time.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbclnt/netsmb/smb_tran.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbclnt/netsmb/smb_tran.c

## Scope

This file contains small transport support helpers for sockaddr sizing, comparison, duplication, and freeing.

## APIs And Behavior

- Static `SA_LEN()` returns the sockaddr storage length for `AF_INET`, `AF_INET6`, and `AF_NETBIOS`, falling back to generic `struct sockaddr` for unknown families.
- `smb_cmp_sockaddr()` compares two sockaddr structures by family-specific length and content.
- `smb_dup_sockaddr()` allocates and copies a sockaddr using the correct family length.
- `smb_free_sockaddr()` frees an address allocated by `smb_dup_sockaddr()`.

## Dependencies

- Used by SMB transport connection logic and potentially future transports.
- Depends on `smb_tran.h`, `smb_conn.h`, and NetBIOS sockaddr definitions.

## Risks And Invariants

- `smb_free_sockaddr()` must receive an address whose length matches `SA_LEN()` or the kmem free size will be wrong.
- Unknown families are debug-logged and treated as generic sockaddr, which is safe only for limited fallback use.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbclnt/netsmb/smb_tran.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbclnt/netsmb/smb_tran.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbclnt/netsmb/smb_tran.h

## Scope

This header defines the netsmb transport abstraction and the known NetBIOS-over-TCP transport descriptor interface.

## APIs And Definitions

- Defines `SMBT_NBTCP` as the known transport type.
- Defines transport parameter IDs for TCP_NODELAY, TCP connect timeout, keepalive, send/receive buffer sizes, and receive timeout.
- `struct smb_tran_desc` is the transport vtable with callbacks for create, destroy, bind, unbind, connect, disconnect, send, receive, poll, get/set parameter, and fatal-error classification.
- `SMB_TRAN_*` macros dispatch through `vcp->vc_tdesc`.
- Declares `smb_tran_nbtcp_desc`.

## Dependencies

- Consumed by virtual circuit setup and transport implementations.
- Uses kernel socket and STREAMS types, and `struct smb_vc`.

## Risks And Invariants

- All transport operations assume `vc_tdesc` is initialized.
- The abstraction currently exposes one concrete transport, but callers are insulated from that via the vtable macros.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbclnt/netsmb/smb_tran.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbclnt/netsmb/smb_trantcp.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbclnt/netsmb/smb_trantcp.c

## Scope

This file implements the NetBIOS session transport over TCP using illumos KTLI/TLI and STREAMS mblks.

## APIs And Behavior

- `nb_getmsg_mlen()` accumulates STREAMS messages until at least a requested byte length is available, handling `M_DATA`, TLI protocol indications, disconnects, orderly release, and timeouts.
- `nb_snddis()` sends a TLI disconnect request.
- `nb_sethdr()` writes the 4-byte NetBIOS session header.
- `nbssn_peekhdr()` waits for and validates a NetBIOS header without consuming it.
- `nbssn_recv()` reads a complete NetBIOS message, splits surplus data into `nbp_frag`, drops keepalives/zero-length messages, and returns session payloads.
- `smb_nbst_create()` opens a TCP or TCP6 KTLI endpoint and initializes `nbpcb`.
- `smb_nbst_done()` disconnects, closes the endpoint, frees addresses and credentials, and destroys locks.
- `smb_nbst_bind()`, `smb_nbst_unbind()`, and `smb_nbst_connect()` implement endpoint setup and transition to `NBST_SESSION`.
- `nb_disconnect()` clears connected state and sends disconnect once.
- `nbssn_send()` prepends or allocates a NetBIOS header and sends the mblk chain.
- `smb_nbst_send()` and `smb_nbst_recv()` serialize send and receive paths with `NBF_SENDLOCK` and `NBF_RECVLOCK`.
- `smb_nbst_setparam()` negotiates TCP/socket options through `t_koptmgmt()`.
- `smb_nbst_fatal()` classifies disconnect/reset/pipe errors as fatal.
- `smb_tran_nbtcp_desc` publishes this implementation through `smb_tran_desc`.

## State And Dependencies

- Uses `struct nbpcb` from `smb_trantcp.h`, `t_kopen`, `t_kconnect`, `tli_send`, `tli_recv`, `t_kspoll`, STREAMS mblk helpers, and NetBIOS constants.
- `nbp_frag` stores surplus received data after message splitting.

## Risks And Invariants

- Receive and send functions assert that higher layers serialize each direction.
- Header validation rejects reserved bits, bogus packet types, and packets larger than `NB_MAXPKTLEN`.
- The receive loop treats 15-second inactivity as `ETIME`, feeding server-not-responding behavior.
- Any unexpected protocol indication can force disconnect and `ENOTCONN`.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbclnt/netsmb/smb_trantcp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbclnt/netsmb/smb_trantcp.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbclnt/netsmb/smb_trantcp.h

## Scope

This header defines NetBIOS-over-TCP transport state and connection control block fields.

## APIs And Definitions

- `enum nbstate` models closed, idle, request-sent, session, retarget, and refused states.
- `struct nbpcb` stores the SMB virtual circuit pointer, KTLI handle, receive fragment, local/peer NetBIOS addresses, select ID, held credential, flags, file mode, state, timeout, buffer sizes, mutex, and condition variable.
- Flag bits include local address present, connected, receive lock, send lock, and lock wait.
- Defines nominal send/receive queue sizes, receive chunk size, and socket buffer timeout constants.

## Dependencies

- Used directly by `smb_trantcp.c`.
- Depends on `struct smb_vc`, `struct tiuser`, STREAMS `mblk_t`, sockaddr NetBIOS, credentials, mutexes, and condition variables.

## Risks And Invariants

- `nbp_frag` ownership belongs to the receive path and must be freed with endpoint teardown.
- `NBF_RECVLOCK` and `NBF_SENDLOCK` are required to prevent concurrent directional transport access.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbclnt/netsmb/smb_trantcp.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbclnt/netsmb/smb_usr.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbclnt/netsmb/smb_usr.c

## Scope

This file implements the kernel side of netsmb user ioctls for session, tree, file handle, I/O, named pipe transaction, print job, IOD, and password-key operations.

## APIs And Behavior

- `smb_usr_get_ssnkey()` returns the active session key to userland for RPC encryption use.
- `smb_usr_xnp()` handles transact-named-pipe using SMB2 IOCTL `FSCTL_PIPE_TRANSCEIVE` or SMB1 transaction2 named pipe.
- `smb_cpdatain()` copies ioctl payload data into an mbchain.
- `smb_usr_rw()` converts SMBIOC read/write arguments into a one-element `uio` and calls `smb_rwuio()`.
- `smb_usr_ntcreate()` opens a named file on the current share and stores the resulting file handle in the device state.
- `smb_usr_printjob()` creates a print queue file, validating the print job title against invalid SMB filename characters.
- `smb_usr_closefh()` closes and releases the current file handle.
- `smb_usr_get_ssn()` finds or creates a VC/session, validates requested ownership against caller credentials, optionally marks the device as IOD, and waits for active state on find.
- `smb_usr_drop_ssn()` releases or kills the current VC and any attached share.
- `smb_usr_get_tree()` finds or connects a share and returns actual share type.
- `smb_usr_drop_tree()` releases or kills the current share.
- `smb_usr_iod_ioctl()` handles userland IOD state-machine calls for connect, negotiate, session setup, work, idle, and reconnect failure.
- `smb_usr_ioctl()` serializes ioctls per device and dispatches all SMBIOC commands.

## State And Dependencies

- Operates on `smb_dev_t` fields `sd_vc`, `sd_share`, `sd_fh`, `sd_flags`, and `sd_level`.
- Depends on connection/session/share lookup, SMB1/SMB2 request functions, mchain, credential helpers, password-key ioctls, and IOD functions.

## Risks And Invariants

- All per-device ioctl handlers assume serialization via `NSMBFL_IOCTL`.
- Reconnect generation mismatches return `ESTALE` for open file handles.
- Tree-connect structures may contain cleartext passwords and are zeroed before free.
- IOD ownership is enforced by `NSMBFL_IOD` and `vcp->iod_thr`.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbclnt/netsmb/smb_usr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbclnt/netsmb/subr_mchain.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbclnt/netsmb/subr_mchain.c

## Scope

This file implements BSD mbuf-style mbchain/mdchain packing and unpacking on top of illumos STREAMS mblks.

## APIs And Behavior

- Provides UIO helpers `uio_curriovbase()`, `uio_curriovlen()`, and `uio_update()`.
- `m_getblk()` allocates STREAMS mblks with minimum size `MLEN` of 4096 bytes.
- `mb_init()` allocates a new send chain and reserves 4 bytes for a later NetBIOS header.
- `mb_done()`, `mb_initm()`, `mb_detach()`, `m_fixhdr()`, and `mb_fixhdr()` manage mbchain lifetime and length.
- `mb_reserve()` reserves contiguous space in the current mblk, appending blocks as needed.
- `mb_put_*()` functions append fixed-width integers in big/little endian form.
- `mb_put_padbyte()` aligns Unicode strings; `mb_put_align8()` pads to an 8-byte boundary.
- `mb_put_mem()`, `mb_put_mbuf()`, `mb_put_mbchain()`, and `mb_put_uio()` copy system, user, zero, inline, mblk, mbchain, or UIO data into outgoing chains.
- `md_initm()`, `md_done()`, `md_append_record()`, and `md_next_record()` manage receive chains and multi-record responses using `b_next`.
- `md_get_*()` functions decode fixed-width integers.
- `md_get_mem()`, `md_get_mbuf()`, and `md_get_uio()` extract bytes to system/user buffers, copied mblks, or UIOs.
- Solaris shims `m_cat()`, `m_copym()`, `m_pullup()`, `m_split()`, and `md_tell()` emulate mbuf-style operations.

## State And Dependencies

- Uses STREAMS mblk fields `b_rptr`, `b_wptr`, `b_cont`, `b_next`, data-block bounds, `dupmsg`, `dupb`, `adjmsg`, `pullupmsg`, and copyin/copyout.
- Used throughout SMB1/SMB2 request building and response parsing.

## Risks And Invariants

- `mb_init()` intentionally leaves 4 bytes headroom for NetBIOS transport headers.
- `md_done()` frees all chained records, including unusual `b_next` record lists.
- Some inline macros depend on local variable names and are intentionally macro-based because compiler options prevented effective inlining.
- Incorrect mblk splitting/copying can corrupt receive fragment ownership or leak message chains.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbclnt/netsmb/subr_mchain.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbclnt/smbfs/smbfs.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbclnt/smbfs/smbfs.h

## Scope

This header defines SMBFS mount-level state, mount flags, statfs cache metadata, filesystem attribute info, and helper macros.

## APIs And Definitions

- `SMB_MAXFNAMELEN` defines component length excluding terminating null.
- Statfs cache constants and status bits cover busy, waiter, timeout, and dead mount states.
- Declares SMBFS vnodeops template and vnodeops pointer.
- Defines mount flags for interruptible operations, no attribute cache, local locking, ACL support, direct I/O, extended attributes, and dead mounts.
- `smb_fs_attr_info_t` stores filesystem attribute flags, maximum name length, and filesystem type name.
- `smbmntinfo_t` stores VFS pointer, root node, netsmb share, taskq, lock, flags/status, cached statvfs, FS attributes, per-mount node AVL tree, kstats, zone list membership, owner/group/mode defaults, and attribute cache timeout settings.
- Defines default and maximum attribute cache timeouts.
- Defines `SEC2HR()`, `VTOSMI()`, `VFTOSMI()`, and `SMBINTR()` helpers.

## Dependencies

- Used by all SMBFS vnode, mount, ACL, client, and protocol bridge code.
- Depends on VFS, AVL, taskq, zone, mount argument, and netsmb share types.

## Risks And Invariants

- `smi_hash_avl` is the per-mount node cache despite historical “hash” names.
- `smi_lock` protects flags/status; `smi_hash_lk` protects the node AVL.
- Cache timeout values are stored as high-resolution nanoseconds.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbclnt/smbfs/smbfs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbclnt/smbfs/smbfs_acl.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbclnt/smbfs/smbfs_acl.c

## Scope

This file implements SMBFS ACL and security descriptor support for ioctl, `VOP_GETSECATTR`, `VOP_SETSECATTR`, and owner/group attribute refresh.

## APIs And Behavior

- `smbfs_getsd()` obtains a security descriptor by temporary-opening the node with read-control and optional system-security rights, retrying with a larger buffer when the server reports more data.
- `smbfs_setsd()` temporary-opens with rights implied by owner/group/DACL/SACL selectors, invalidates the cached security attributes, and sends a remote set-security operation.
- `smbfs_acl_iocget()` handles `SMBFSIO_GETSD`, returning required/used buffer size and copying the raw descriptor to user memory.
- `smbfs_acl_iocset()` handles `SMBFSIO_SETSD`, validates descriptor size, copies user data into an mbchain, and sends it.
- `smbfs_acl_refresh()` fetches owner, group, and DACL information, parses the NT security descriptor, converts it to ZFS ACL form, and updates `r_secattr`, `n_uid`, and `n_gid`.
- `smbfs_acl_getids()` refreshes cached UID/GID when stale.
- `smbfs_acl_getvsa()` refreshes and duplicates requested ACL fields into caller-supplied `vsecattr_t`.
- `smbfs_acl_store()` converts ZFS ACL/UID/GID inputs to an NT security descriptor and sends it.
- `smbfs_acl_setids()` updates owner and/or group security fields.
- `smbfs_acl_setvsa()` sets DACL information using current owner/group for owner/group ACE expansion.

## State And Dependencies

- Depends on `smbfs_ntacl.h` conversion/marshalling helpers, mchain, temporary open/close helpers, and SMBFS SMB security operations.
- Uses `r_sectime` as ACL cache expiry and `r_statelock` for cached security fields.

## Risks And Invariants

- Raw security descriptors are bounded by `MAX_RAW_SD_SIZE` and `SMALL_SD_SIZE` retry logic.
- Extended attribute files/directories report `ENOSYS` because their ACLs are derived from parents.
- `smbfs_setsd()` consumes the passed mblk pointer and clears it.
- Old cached ACL allocations must be freed after replacement.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbclnt/smbfs/smbfs_acl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbclnt/smbfs/smbfs_client.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbclnt/smbfs/smbfs_client.c

## Scope

This file contains SMBFS client-side cache validation, attribute conversion, flush-all traversal, and per-zone mount list lifecycle.

## APIs And Behavior

- `smbfs_waitfor_purge_complete()` waits interruptibly for another thread’s cache purge to finish.
- `smbfs_validate_caches()` uses the attribute cache when valid or fetches fresh attributes from the server.
- `smbfs_purge_caches()` invalidates cached vnode pages through `VOP_PUTPAGE(..., B_INVAL, ...)`.
- `smbfs_cache_check()` compares cached and fresh mtime/size/ctime to decide page-cache and ACL-cache invalidation.
- `smbfs_attrcache_fa()` stores fresh SMB attributes, computes adaptive cache expiry based on time since detected modification, updates vnode type/mode, and reconciles client-visible size.
- `smbfs_getattr_cache()` returns cached SMB attributes when not expired.
- `smbfs_getattr_otw()` fetches attributes via an existing open FID or path/attribute open, handles fake XATTR directories, prunes caches on remove/rename errors, and refreshes caches.
- `smbfsgetattr()` combines UID/GID ACL refresh, cached/remote SMB attributes, and conversion to `vattr`.
- `smbfattr_to_vattr()` maps SMB attributes to vnode attributes, including client-side size, inode number, mode, uid/gid, times, and block count.
- `smbfattr_to_xvattr()` maps SMB creation time and DOS archive/system/readonly/hidden bits to extensible attributes.
- `smbfs_flushall()` walks per-zone SMBFS mounts and calls `smbfs_rflush()`.
- Zone callbacks initialize, shut down, destroy, add, and remove per-zone mount lists.
- `smbfs_clntinit()` creates the zone key and optional callback hooks; `smbfs_clntfini()` tears them down.

## State And Dependencies

- Uses `smbnode_t` cached attributes, `r_attrtime`, `r_mtime`, `r_size`, `r_secattr`, `r_serial`, mount timeout settings, and per-zone `smi_globals`.
- Depends on SMBFS protocol helpers, vnode page cache operations, zones, lists, kstats, and ACL helpers.

## Risks And Invariants

- Attribute cache timing deliberately avoids assuming synchronized client/server clocks.
- Size updates avoid overwriting dirty or actively referenced cached file data.
- Zone destroy may defer freeing globals until late VFS teardown removes the final mount.
- `smbfs_zonelist_remove()` frees globals while holding the zone list lock on the deferred destroy path.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbclnt/smbfs/smbfs_client.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbclnt/smbfs/smbfs_node.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbclnt/smbfs/smbfs_node.c

## Scope

This file implements small SMBFS node helpers for pseudo-inode hashing, name allocation, lookup/create glue, and attribute cache invalidation.

## APIs And Behavior

- `smbfs_hash()` is an FNV-style 32-bit hash helper.
- `smbfs_gethash()` computes a hash of a full remote path.
- `smbfs_getino()` computes a child pseudo-inode number from the parent inode hash, optional separator, and child name.
- `smbfs_name_alloc()` allocates and null-terminates a fixed-length name.
- `smbfs_name_free()` frees names allocated by `smbfs_name_alloc()`.
- `smbfs_nget()` validates a lookup name, builds/finds/creates a node through `smbfs_node_findcreate()`, propagates `N_XATTR` from parent to child, and returns the vnode.
- `smbfs_attr_touchdir()` updates a directory’s local modification time and invalidates its attribute cache.
- `smbfs_attrcache_remove()` expires a node’s attribute cache.
- `smbfs_attrcache_rm_locked()` expires a node’s attribute cache while caller holds `r_statelock`.

## Dependencies

- Relies on node cache functionality declared elsewhere, mount/node structures, and SMBFS subr helpers.
- Uses `SMBFS_DNP_SEP()` for remote path separator semantics.

## Risks And Invariants

- Node identity is the full server-form remote path relative to the share root.
- Empty, `.` and `..` names are rejected before node creation.
- Pseudo-inode numbers are hashes and may collide; they are not server-provided stable IDs.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbclnt/smbfs/smbfs_node.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbclnt/smbfs/smbfs_node.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbclnt/smbfs/smbfs_node.h

## Scope

This header defines SMBFS node structures, directory cache placeholders, custom rwlock state, node-cache AVL identity fields, smbnode state fields, and node flag bits.

## APIs And Definitions

- `rddir_cache` describes a whole-directory cache entry, though comments state directory caching is not yet active.
- `smbfs_rwlock_t` is a homegrown reader/writer lock that supports interruptible entry and writer re-entry.
- `smbfs_node_hdr_t` contains AVL linkage and remote path identity fields used by the per-mount node cache.
- `smbnode_t` is the SMBFS inode-equivalent, containing mount/vnode pointers, free-list links, rw locks, state lock, open file and directory search handle state, credentials, readahead state, map counts, flags, readdir cache AVL, modified address tracking, delete-map tracking, cached SMB attributes, ACL cache, pseudo-inode, uid/gid, and mode.
- Defines `n_flag` bits such as flush in progress, modified, parent reference, IDs known, readdir serialization, mapped, attribute changed, allocating, waiting allocation, and XATTR.
- Defines `r_flags` bits for dirty data, stale handles, modification/commit state, hashed state, direct I/O, lookup, write-attribute origin, and delmap tracking.
- Provides `VTOSMB()`, `SMBTOV()`, and `SMBFS_DNP_SEP()` helpers.

## Locking Contract

- Header comments document lock roles and ordering: `r_rwlock > r_lkserlock > r_statelock`.
- `r_rwlock` serializes writes/setattr and directory reads/updates.
- `r_lkserlock` serializes lock requests with map/write/readahead operations.
- `r_statelock` protects most smbnode fields, including 64-bit `r_size`.

## Risks And Invariants

- `r_size` must be read/written under `r_statelock` on 32-bit architectures.
- `n_rpath` and `n_rplen` define node identity in the AVL cache.
- XATTR directory separator behavior changes path construction via `SMBFS_DNP_SEP()`.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbclnt/smbfs/smbfs_node.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbclnt/smbfs/smbfs_rwlock.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbclnt/smbfs/smbfs_rwlock.c

## Scope

This file implements the SMBFS custom reader/writer lock, borrowed from NFS, with interruptible entry and writer re-entry.

## APIs And Behavior

- `smbfs_rw_enter_sig()` enters as reader or writer. Readers wait behind active writers or waiting writers. Writers wait for active readers or owners. Current writer owner may re-enter recursively by decrementing count further.
- Interruptible waits use `cv_wait_sig()` and temporarily increment `lwp_nostop`.
- `smbfs_rw_tryenter()` attempts non-blocking reader or writer acquisition with the same recursive-writer behavior.
- `smbfs_rw_exit()` releases reader or writer ownership, unwinding recursive writer count and broadcasting when the lock becomes available.
- `smbfs_rw_lock_held()` reports whether the lock is held in reader or writer mode based on `count`.
- `smbfs_rw_init()` initializes count, waiters, owner, mutex, and condition variable.
- `smbfs_rw_destroy()` destroys synchronization primitives.

## State Model

- `count > 0` means active reader count.
- `count < 0` means writer hold depth.
- `owner` identifies the writer thread.
- `waiters` biases readers behind waiting writers to avoid writer starvation.

## Risks And Invariants

- Recursive entry is allowed only for the writer owner.
- Every recursive writer enter must be paired with an exit.
- `smbfs_rw_lock_held(RW_WRITER)` reports any writer hold, not necessarily ownership by the current thread.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbclnt/smbfs/smbfs_rwlock.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbclnt/smbfs/smbfs_smb.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbclnt/smbfs/smbfs_smb.c

## Scope

This file is the protocol-neutral SMBFS operation facade that dispatches VFS-facing operations to SMB1 or SMB2 implementations.

## APIs And Behavior

- `smbfs_smb_getfattr()` queries attributes using an existing open file handle.
- `smbfs_smb_getpattr()` queries attributes by path or temporary SMB2 attribute open.
- `smbfs_smb_qfsattr()` queries filesystem attributes and marks FAT-like shares to clamp dates before 1980.
- `smbfs_smb_statfs()` queries filesystem size info and converts it to `statvfs64_t`.
- `smbfs_smb_setdisp()` sets delete disposition.
- `smbfs_smb_setfsize()` sets end-of-file size.
- `smbfs_smb_setfattr()` builds FILE_BASIC_INFORMATION and sends DOS/time metadata updates, clamping FAT timestamps before 1980.
- `smbfs_smb_flush()` flushes an open handle.
- `smbfs_smb_ntcreatex()` builds a full SMB path and performs common create/open through `smb_smb_ntcreate()`.
- `smbfs_smb_tmpopen()` borrows an existing node FID when it has sufficient rights, otherwise opens a temporary handle.
- `smbfs_smb_tmpclose()` releases temporary or borrowed handles.
- `smbfs_smb_open()`, `smbfs_smb_close()`, and `smbfs_smb_create()` manage normal file opens/creates.
- `smbfs_smb_rename()` selects SMB2 rename, SMB1 trans2 same-directory rename, or SMB1 old rename.
- `smbfs_smb_mkdir()` creates a directory through create/open semantics and closes the temporary handle.
- `smbfs_smb_findopen()`, `smbfs_smb_findnext()`, and `smbfs_smb_findclose()` abstract directory enumeration across SMB2, SMB1, and extended attributes.
- `smbfs_smb_lookup()` implements lookup via single-entry directory enumeration.
- `smbfs_smb_getsec()` and `smbfs_smb_setsec()` dispatch raw security descriptor get/set.

## Dependencies

- Bridges SMBFS vnode code to `smbfs_smb1.c`, `smbfs_smb2.c`, extended attribute helpers, file-handle helpers, path builders, and mchain.

## Risks And Invariants

- Temporary open rights must match the operation or later SMB set/query calls fail.
- File handles include VC generation; borrowed handles are used only when generation matches.
- Directory enumeration skips `.` and `..` after UTF-8 conversion.
- Security descriptor get corrects returned length down to actual mblk payload size.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbclnt/smbfs/smbfs_smb.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbclnt/smbfs/smbfs_smb1.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbclnt/smbfs/smbfs_smb1.c

## Scope

This file implements SMB1-specific SMBFS protocol operations using classic SMB requests, TRANS2, and NT_TRANSACT.

## APIs And Behavior

- A disabled `smbfs_smb1_lockandx()` block sketches future over-the-wire locking.
- `smbfs_smb1_trans2_query()` performs query-file-information or query-path-information and decodes `SMB_QFILEINFO_ALL_INFO`.
- `smbfs_smb1_query_fs_info()` issues `SMB_TRANS2_QUERY_FS_INFORMATION`.
- `smbfs_smb1_qfsattr()` decodes filesystem attribute information.
- `smbfs_smb1_statfs()` queries size/full-size information depending on pass-through capability.
- `smbfs_smb1_flush()` sends `SMB_COM_FLUSH`.
- `smbfs_smb1_setinfo_file()` is the common TRANS2 set-file-information helper.
- `smbfs_smb1_seteof()`, `smbfs_smb1_setdisp()`, and `smbfs_smb1_setfattr()` set EOF, delete disposition, and basic metadata.
- `smbfs_smb1_t2rename()` builds same-directory `SMB_SFILEINFO_RENAME_INFORMATION` for open-file rename cases.
- `smbfs_smb1_oldrename()` sends `SMB_COM_RENAME` for cross-directory or fallback rename.
- `smbfs_smb1_trans2find2()` drives FIND_FIRST2/FIND_NEXT2, including resume keys/names, end-of-search handling, and response payload transfer to the find context.
- `smbfs_smb1_findclose2()` closes SMB1 directory search handles.
- `smbfs_smb_findopenLM2()`, `smbfs_smb_findcloseLM2()`, and `smbfs_smb_findnextLM2()` manage LM2-style directory enumeration.
- `smbfs_smb1_get_streaminfo()` queries named stream information.
- `smbfs_smb1_getsec()` gets a raw security descriptor via `NT_TRANSACT_QUERY_SECURITY_DESC`.
- `smbfs_smb1_setsec()` sets a raw security descriptor via `NT_TRANSACT_SET_SECURITY_DESC`.

## State And Dependencies

- Uses `smb_t2rq`, `smb_ntrq`, `smb_rq`, mchain/mdchain, SMB1 info-level constants, path construction, and decode helpers.

## Risks And Invariants

- SMB1 info levels vary depending on `SMB_CAP_INFOLEVEL_PASSTHRU`.
- FIND response parsing forces EOF on malformed data to avoid infinite directory loops.
- FIND close uses `SMBR_NOINTR_SEND` to avoid losing track of server search handles.
- `smbfs_smb1_setsec()` consumes the caller’s mblk chain.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbclnt/smbfs/smbfs_smb1.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbclnt/smbfs/smbfs_smb2.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbclnt/smbfs/smbfs_smb2.c

## Scope

This file implements SMB2-specific SMBFS protocol operations for query/set info, statfs, flush, rename, directory enumeration, stream info, and security descriptors.

## APIs And Behavior

- A disabled `smbfs_smb2_locking()` block reserves future over-the-wire locking support.
- `smbfs_smb2_getpattr()` opens the target with read-attributes/read-control rights, uses create response attributes, and closes the handle.
- `smbfs_smb2_query_info()` builds and sends SMB2 QUERY_INFO requests, validates response structure size, skips to payload offsets, and returns payload as an mdchain.
- `smbfs_smb2_qfileinfo()` queries `FileAllInformation` and decodes it.
- `smbfs_smb2_query_fs_info()` opens the share root directly and queries filesystem information.
- `smbfs_smb2_qfsattr()` queries and decodes `FileFsAttributeInformation`.
- `smbfs_smb2_statfs()` queries `FileFsFullSizeInformation`.
- `smbfs_smb2_flush()` sends SMB2 FLUSH with persistent and volatile FID parts and disables reconnect for the request.
- `smbfs_smb2_set_info()` builds common SMB2 SET_INFO requests with payload length backpatching.
- `smbfs_smb2_seteof()`, `smbfs_smb2_setdisp()`, and `smbfs_smb2_setfattr()` set EOF, disposition, and basic metadata.
- `smbfs_smb2_rename()` builds `FileRenameInformation` with a full target path.
- `smbfs_smb2_qdir()` sends SMB2 QUERY_DIRECTORY, caps buffers at 64 KiB or negotiated max transact size, transfers the response payload to the find context, and marks EOF on parse errors or empty responses.
- `smbfs_smb2_findopen()` opens a directory handle for enumeration and initializes the find context.
- `smbfs_smb2_findclose()` releases directory handle, request, name buffer, and mdchain.
- `smbfs_smb2_findnext()` refills directory buffers as needed and decodes one directory entry.
- `smbfs_smb2_get_streaminfo()` opens the object and queries `FileStreamInformation`.
- `smbfs_smb2_getsec()` queries SMB2 security information and returns the payload mblk.
- `smbfs_smb2_setsec()` consumes a caller mblk and sends SMB2 security SET_INFO.

## State And Dependencies

- Uses SMB2 request opcodes, `smb2fid_t`, mchain/mdchain helpers, common path/create/close helpers, and SMBFS decode functions.

## Risks And Invariants

- SMB2 payload offsets are validated against expected header-relative positions to catch malformed responses.
- Directory query receive is marked non-interruptible to avoid server-side enumeration offset corruption.
- Query-directory lacks entry count, so parsing tracks byte offsets through `f_left` and `f_eofs`.
- Security set consumes the input mblk and clears the caller pointer.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbclnt/smbfs/smbfs_smb2.c -->