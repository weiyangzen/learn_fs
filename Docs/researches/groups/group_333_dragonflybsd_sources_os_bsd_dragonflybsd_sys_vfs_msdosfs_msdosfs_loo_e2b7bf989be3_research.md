# Group Research: group_333_dragonflybsd_sources_os_bsd_dragonflybsd_sys_vfs_msdosfs_msdosfs_loo_e2b7bf989be3

Research scope: `Docs/research_subset_a.md`, covering `sources/os/bsd/dragonflybsd` as part of OS/VFS and filesystem kernel sources.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/msdosfs/msdosfs_lookup.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/msdosfs/msdosfs_lookup.c

## Role

Implements MSDOSFS pathname lookup and directory-entry mutation helpers. It bridges VFS component names to FAT short names and Win95 long-name directory slots, records insertion/removal offsets in parent denodes, and provides directory safety checks used by create, delete, rename, mkdir, and rmdir paths.

## Major Entry Points

- `msdosfs_lookup()` searches a directory for a component, handles root `.`/`..` fakery, translates Unix names to DOS names, matches Win95 long-name slots, and returns locked vnodes according to old lookup flags.
- `createde()` writes a new FAT directory entry and any needed long-name entries into the parent directory.
- `dosdirempty()` scans a directory and verifies that it contains only `.` and `..`.
- `doscheckpath()` prevents renaming a directory into one of its own descendants.
- `readep()` and `readde()` load the disk block containing a particular directory entry.
- `removede()` marks a directory entry and preceding Win95 long-name slots deleted.
- `uniqdosname()` generates a collision-free short 8.3 name, with generation suffixes for long names.

## Implementation Notes

- Lookup stores `de_fndoffset` and `de_fndcnt` in the parent denode so later create, rename, or remove operations know where to write or delete directory slots.
- Long-name matching uses `mbnambuf`, `win2unixfn()`, `winChkName()`, and checksum validation against the following short entry.
- `MSDOSFSMNT_SHORTNAME` disables long-name search and forces a single short-name slot.
- Empty-slot tracking is active only for create and rename, since only those paths need insertion space.
- Root directory `.` and `..` are synthesized because non-FAT32 DOS root directories have no real entries for them.
- FAT32 root cluster aliases are normalized between `MSDOSFSROOT` and `pm_rootdirblk`.
- Lookup releases the directory block before `deget()` to avoid deadlocks reading the same entry back through the denode cache.
- `msdosfs_lookup_checker()` guards against corrupted filesystems that make a non-dot lookup resolve to the directory vnode itself.
- `doscheckpath()` walks upward through `..` entries, dropping and reacquiring denodes as it climbs, and always releases the target denode before returning.
- `removede()` deliberately deletes preceding Win95 entries aggressively because unmatched long-name entries are considered invalid orphan slots.

## Dependencies

Depends on FAT block mapping (`pcbmap()`), denode lookup/cache (`deget()`), FAT directory format helpers, Win95 long-name conversion/checksum helpers, buffer-cache I/O, and old DragonFly namei/VOP lookup conventions.

## Research Notes

This file is the namespace consistency core for MSDOSFS. Its main invariant is that directory blocks and in-memory denodes are kept synchronized by reading the directory block before mutation, then updating both disk entry state and denode-derived lookup state in a controlled order.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/msdosfs/msdosfs_lookup.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/msdosfs/msdosfs_vfsops.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/msdosfs/msdosfs_vfsops.c

## Role

Implements DragonFly VFS operations for mounting, unmounting, syncing, exporting, and statting MSDOSFS volumes. It parses the FAT boot sector/BPB, derives filesystem geometry, initializes the mount control block, builds the in-use cluster bitmap, and wires MSDOSFS vnode operations into the mount.

## Major Entry Points

- `msdosfs_mount()` handles initial mounts, update mounts, read-only/read-write transitions, device lookup, permission checks, export updates, and mount stat population.
- `mountmsdosfs()` opens the backing disk, validates the boot sector, computes FAT12/FAT16/FAT32 geometry, allocates `msdosfsmount`, and fills the in-use cluster map.
- `msdosfs_unmount()` flushes vnodes, closes the device, releases iconv handles, frees FAT/mount memory, and clears device mount state.
- `msdosfs_root()` returns the root denode vnode.
- `msdosfs_statfs()` and `msdosfs_statvfs()` report FAT cluster counts and free-space state.
- `msdosfs_sync()` flushes dirty denodes, device metadata, and FSInfo state.
- `msdosfs_fsiflush()` writes FAT32 FSInfo free-cluster and next-free hints.
- `msdosfs_fhtovp()`, `msdosfs_checkexp()`, and `msdosfs_vptofh()` support NFS export file handles.

## Implementation Notes

- `update_mp()` applies owner/group/mode masks, mount flags, and optional kernel iconv conversion handles.
- FAT32 detection is based on zero root directory entries, nonzero big FAT sectors, and compatible FS version fields.
- The mount code validates sector size, sectors-per-cluster power-of-two constraints, FAT sector count, total sector count, overflow, and maximum block size compatibility.
- Cluster count determines FAT12 versus FAT16 when the BPB did not already imply FAT32.
- FAT block I/O size is tuned separately: FAT12 uses `3 * 512`, while other FAT types use `PAGE_SIZE`, rounded to physical sector size.
- `pm_bpcluster`, `pm_crbomask`, `pm_cnshift`, and `pm_bnshift` provide the offset/block conversion basis used throughout the filesystem.
- FAT32 FSInfo is trusted only if all three signatures match; otherwise it is ignored.
- `fillinusemap()` requires `pm_devvp` and `pm_dev` to be installed before scanning the FAT.
- `MNT_SYNCHRONOUS` maps to `MSDOSFSMNT_WAITONFAT`.
- The sync scanner calls `VOP_FSYNC()` on dirty denode vnodes and repeats while rescans are requested.

## Dependencies

Uses DragonFly VFS mount/update/unmount APIs, device vnode operations, buffer cache, FAT BPB/boot-sector structures, denode and FAT allocation code, kernel iconv, netexport, and VFS vnode scanning.

## Research Notes

The file is the mount-time geometry authority for MSDOSFS. Most lower-level FAT macros and vnode operations rely on fields initialized here, especially cluster size, root directory location, FAT width, and the in-use cluster bitmap.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/msdosfs/msdosfs_vfsops.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/msdosfs/msdosfs_vnops.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/msdosfs/msdosfs_vnops.c

## Role

Implements the DragonFly vnode operations for MSDOSFS files and directories. It adapts FAT directory-entry metadata and cluster chains to VFS create, access, getattr, setattr, read, write, fsync, remove, rename, mkdir, rmdir, readdir, bmap, and strategy operations.

## Major Entry Points

- `msdosfs_create()` creates regular files by generating a unique short name, setting FAT attributes, timestamps, and calling `createde()`.
- `msdosfs_access()`, `msdosfs_getattr()`, and `msdosfs_setattr()` translate FAT attributes, mount uid/gid/masks, timestamps, archive/read-only bits, and file size changes into VFS semantics.
- `msdosfs_read()` reads regular files through the file vnode and directories through the device vnode to avoid buffer-cache aliasing.
- `msdosfs_write()` extends FAT cluster chains, fills holes with zeroes via `deextend()`, updates buffer-cache blocks, and handles synchronous/unit writes.
- `msdosfs_fsync()` flushes vnode buffers, device metadata, and the denode’s directory entry.
- `msdosfs_remove()` and `msdosfs_rmdir()` remove directory entries and truncate deleted directory clusters.
- `msdosfs_rename()` implements file and directory renames, target replacement, denode rehashing, `..` repair, and directory-cycle prevention.
- `msdosfs_mkdir()` allocates a cluster, writes `.` and `..`, and inserts the parent directory entry.
- `msdosfs_readdir()` converts FAT directory entries and Win95 long-name entries into DragonFly `dirent` records.
- `msdosfs_bmap()` maps file offsets through FAT chains and reports contiguous run lengths.
- `msdosfs_strategy()` translates BIO offsets to backing device offsets and dispatches I/O to the mounted device vnode.
- `msdosfs_pathconf()` reports FAT name length, link count, chown restrictions, truncation, and file size bit limits.

## Implementation Notes

- DOS files are treated as always executable; owner write permission maps to clearing or setting `ATTR_READONLY`.
- Root-directory metadata is special: attribute changes are rejected because classic FAT root directories do not have self entries.
- File IDs in `getattr()` deliberately match `readdir()`’s `d_fileno` computation so tools such as `pwd` work.
- Reads of regular files support clustering and readahead; directory reads use `pm_devvp` because directory data and metadata share device-vnode cache identity.
- Writes pre-extend cluster chains to improve contiguity and roll back on `IO_UNIT` failure.
- Full-cluster writes can avoid read-before-write, except for `UIO_NOCOPY` where the buffer contents are not overwritten.
- Rename is complex because denode cache identity depends on directory cluster and offset; file renames across directories call `msdosfs_reinsert()`.
- Directory renames set `DE_RENAME` to block rmdir/rename races and use `doscheckpath()` when changing parents.
- `mkdir()` writes the child directory cluster before linking it from the parent, reducing crash exposure.
- `readdir()` synthesizes root `.`/`..`, skips deleted entries and volume labels, reconstructs long names with checksum validation, and supports NFS cookies.
- `bmap()` saves and restores the last FAT mapping cache after probing run lengths to avoid moving the sequential cache too far ahead.
- Symlinks, hard links, special nodes, and non-regular writes are unsupported.

## Dependencies

Uses denode metadata and cache operations, FAT allocation/truncation/mapping, lookup helper functions from `msdosfs_lookup.c`, buffer-cache clustering, vnode pager size updates, DragonFly old VOP interfaces, and FAT directory-entry conversion routines.

## Research Notes

This is the main behavioral surface for MSDOSFS. It consistently exposes a Unix-like vnode API while preserving FAT’s limitations: no hard links, no symlinks, no holes, fixed owner/group from mount options, and directory metadata stored directly in parent directory entries.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/msdosfs/msdosfs_vnops.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/msdosfs/msdosfsmount.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/msdosfs/msdosfsmount.h

## Role

Defines the MSDOSFS mount control block, mount arguments, mount flags, and core block/cluster/offset conversion macros used by FAT vnode, lookup, FAT, and mount code.

## Main Data Structures

- `struct msdosfsmount` stores the DragonFly mount pointer, synthetic uid/gid/masks, backing device vnode/device, BPB fields, FAT/root/cluster geometry, free-space state, FAT in-use bitmap, mount flags, export state, and optional iconv handles.
- `struct msdosfs_args` is the userspace mount argument ABI: device path, export args, uid/gid/masks, mount flags, charset names, and directory mask.

## Important Macros

- `VFSTOMSDOSFS(mp)` extracts the filesystem mount object from `mnt_data`.
- `FATOFS(pmp, cn)` computes a cluster’s byte offset within the FAT.
- `bptoep()` converts a buffer and directory offset into a `struct direntry *`.
- `de_bn2cn()`, `de_cn2bn()`, `de_cluster()`, `de_clcount()`, `de_blk()`, `de_cn2off()`, `de_bn2off()`, `de_bn2doff()`, and `de_cn2doff()` perform block, cluster, and byte-offset conversions.
- `cntobn()` maps FAT cluster numbers to filesystem-relative block numbers.
- `roottobn()` and `detobn()` map directory-entry locations to backing blocks.
- `DOINGASYNC(vp)` checks the mount async flag.
- `ASSERT_VOP_LOCKED()` and `ASSERT_VOP_ELOCKED()` wrap DragonFly vnode lock assertions.

## Mount Flags

- User-visible options include `MSDOSFSMNT_SHORTNAME`, `MSDOSFSMNT_LONGNAME`, `MSDOSFSMNT_NOWIN95`, and `MSDOSFSMNT_KICONV`.
- Internal flags include `MSDOSFSMNT_RONLY`, `MSDOSFSMNT_WAITONFAT`, `MSDOSFS_FATMIRROR`, and `MSDOSFS_FSIMOD`.

## Implementation Notes

- BPB fields are exposed through shorthand macros such as `pm_BytesPerSec`, `pm_FATs`, `pm_RootDirEnts`, and `pm_HugeSectors`.
- `pm_BlkPerSec` captures physical-sector-to-`DEV_BSIZE` scaling and is folded into most geometry fields at mount time.
- Root directory handling is macro-level special-cased because pre-FAT32 root directories are fixed regions, not normal cluster chains.
- `MSDOSFS_LOCK_MP()` and related macros are currently no-ops in this header, so mount-level serialization must come from surrounding code or single-threaded assumptions.

## Dependencies

Included by MSDOSFS mount, vnode, lookup, denode, FAT, and makefs-related code. It depends on FAT BPB definitions, DragonFly mount/vnode/device types, netexport for kernel builds, and iconv constants for mount charset fields.

## Research Notes

This header is the in-memory geometry contract for the MSDOSFS implementation. Errors in these conversions would affect lookup, read/write, FAT allocation, directory mutation, and export file handles.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/msdosfs/msdosfsmount.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/nfs/Makefile -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/nfs/Makefile

## Role

Builds the DragonFly NFS kernel module.

## Contents

- Sets `KMOD=nfs`.
- Lists NFS module sources including client BIO, node, Kerberos, server, socket, service cache, syscall, VFS, IOD, XDR helper, and vnode operation files.
- Includes generated option headers: `opt_inet.h`, `opt_nfs.h`, `opt_bootp.h`, and `opt_nfsroot.h`.
- Defines `NFS_INET?=1`.
- Generates `opt_inet.h`, writing `#define INET 1` when `NFS_INET` is enabled.
- Includes `<bsd.kmod.mk>`.

## Implementation Notes

- The module build assumes INET support by default because the NFS code in this tree is IPv4-oriented.
- BOOTP/NFS-root option headers are named as build inputs even though this small Makefile only generates `opt_inet.h`.

## Dependencies

Depends on DragonFly kernel module build infrastructure and the NFS source files named in `SRCS`.

## Research Notes

This file is a compact build manifest. It shows that the NFS IOD code is built into the NFS module along with both client and server implementations.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/nfs/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/nfs/bootp_subr.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/nfs/bootp_subr.c

## Role

Implements kernel BOOTP/DHCP discovery for diskless NFS boot. It probes suitable network interfaces, temporarily configures them for broadcast discovery, accepts BOOTP/DHCP replies, decodes root/swap/hostname/network options, configures final interface state/routes, and obtains NFS root/swap file handles from mountd.

## Main Data Structures

- `struct bootp_packet` is the RFC951 packet format with large vendor option storage.
- `struct bootpc_ifcontext` tracks per-interface request/reply packets, socket, ifreq, link address, DHCP state, discovered IP/netmask/gateway/root flags, and DHCP server ID.
- `struct bootpc_tagcontext` accumulates DHCP option data and records malformed options or oversized tags.
- `struct bootpc_globalcontext` tracks all interfaces, global transaction IDs, root/swap/hostname selection, aggregate reply storage, and temporary option contexts.

## Major Entry Points

- `bootpc_init()` is the top-level diskless bootstrap routine.
- `bootpc_fakeup_interface()` brings candidate interfaces up and configures temporary address/netmask/broadcast state for discovery.
- `bootpc_compose_query()` builds BOOTP, DHCP Discover, or DHCP Request packets.
- `bootpc_call()` sends repeated broadcast requests and receives matching replies.
- `bootpc_received()` validates DHCP message transitions and decides whether a reply improves the current per-interface state.
- `bootpc_tag()` and `bootpc_tag_helper()` parse vendor options, including option-overload use of `file` and `sname`.
- `bootpc_decode_reply()` converts accepted replies into `nfsv3_diskless` root, swap, hostname, netmask, gateway, and mount option data.
- `bootpc_adjust_interface()` applies final interface addresses, broadcast address, netmask, and default route, or shuts failed interfaces down.
- Debug-only `bootpboot_p_*()` helpers print route and interface state.

## Implementation Notes

- DHCP is the default unless `BOOTP_NO_DHCP` is configured; code can fall back to BOOTP unless forced DHCP is configured.
- Each candidate interface receives a distinct transaction ID derived from a global base.
- The discovery socket is UDP broadcast with `SO_BROADCAST`, `SO_DONTROUTE`, and a one-second receive timeout.
- Replies are accepted only when the packet is long enough, is a BOOTP reply, matches the xid, matches hardware address length, and matches hardware address bytes.
- DHCP state advances from Discover to Offered to Request to Resolved; BOOTP replies may resolve directly.
- The send loop prefers interfaces with root paths and applies a settle delay once the needed root path is found.
- Option parser detects malformed tag lengths and concatenates repeated options up to `TAG_MAXLEN`.
- Recognized options include subnet mask, routers, hostname, root path, root options, swap path, swap options, swap size, DHCP message type/server/requested address/lease, and a site-specific cookie exported through `kern.bootp_cookie`.
- If no subnet mask is provided, classful defaults are used; if no gateway is provided, the client address is used for proxy ARP behavior.
- `bootpc_init()` calls `md_mount()` for root and optional swap, `md_lookup_swap()` for per-client swap lookup, and marks `nfs_diskless_valid = 3` after success.

## Dependencies

Uses DragonFly networking interfaces, sockets, routing, sysctl, NFS diskless structures, mountd RPC helpers, NFS mount option parsing, kernel RPC/XDR headers, and BOOTP/NFS-root compile options.

## Research Notes

This file is a full kernel network bootstrap path, not a normal NFS data path. It mutates interface state during early boot and treats missing root path as fatal only when BOOTP NFS root support requires it.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/nfs/bootp_subr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/nfs/krpc.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/nfs/krpc.h

## Role

Declares the small kernel SunRPC helper API used during NFS diskless boot and mountd/portmapper bootstrap work.

## API

- `krpc_call()` performs a UDP RPC call to an IPv4 server and returns the reply mbuf chain.
- `krpc_portmap()` asks portmapper for a program/version UDP port.
- `xdr_string_encode()` creates an mbuf containing an XDR string.

## Constants

Defines portmapper program, version, fixed port, and procedure numbers:

- `PMAPPORT`
- `PMAPPROG`
- `PMAPVERS`
- `PMAPPROC_NULL`
- `PMAPPROC_SET`
- `PMAPPROC_UNSET`
- `PMAPPROC_GETPORT`
- `PMAPPROC_DUMP`
- `PMAPPROC_CALLIT`

## Dependencies

Forward declares `mbuf`, `thread`, and socket address structures. The implementation lives in `krpc_subr.c`.

## Research Notes

The header is intentionally narrow and IPv4-specific. It is infrastructure for bootstrapping NFS-root support before higher-level NFS client machinery is available.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/nfs/krpc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/nfs/krpc_subr.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/nfs/krpc_subr.c

## Role

Implements a minimal kernel UDP SunRPC client for diskless NFS bootstrap. It performs portmapper lookups, constructs AUTH_UNIX RPC calls, binds to reserved local ports, retransmits with backoff, validates replies, strips RPC reply headers, and encodes XDR strings.

## Major Entry Points

- `krpc_portmap()` returns the UDP port for an RPC program/version using `PMAPPROC_GETPORT`, with a fast path for portmapper itself.
- `krpc_call()` sends a single RPC request, repeatedly retransmits until a valid reply arrives, and returns the decoded reply payload mbuf.
- `xdr_string_encode()` builds an mbuf containing XDR length plus padded string data.

## Implementation Notes

- The RPC code is IPv4-only and rejects non-`AF_INET` addresses.
- The socket is UDP with a one-second receive timeout; broadcast is enabled when the caller requests the response source address.
- Local binding searches downward from `IPPORT_RESERVED` so servers requiring privileged source ports accept the request.
- RPC headers are prepended in a separate mbuf containing XID, RPC version 2, program, version, procedure, AUTH_UNIX credentials, and null verifier.
- XIDs are allocated from a static counter with atomic increment and skip zero.
- Retransmission timeout grows linearly up to `MAX_RESEND_DELAY`, after which timeout messages are printed.
- Replies must have enough bytes for the minimum header, must be RPC replies, must match the XID, must be accepted, and must have success status.
- Program mismatch maps to `EBADRPC`; other denied statuses are logged and ignored until another reply or timeout.
- Accepted replies have the auth verifier skipped before the remaining mbuf payload is returned to the caller.
- `xdr_string_encode()` refuses strings that would exceed `MCLBYTES`.

## Dependencies

Uses DragonFly sockets, mbufs, socket buffers, RPC/XDR constants, portmapper constants from `krpc.h`, and kernel memory allocation.

## Research Notes

This helper is deliberately small compared with the normal NFS RPC machinery. It exists so early NFS-root code can contact portmapper and mountd before a fully mounted NFS client filesystem is active.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/nfs/krpc_subr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/nfs/nfs.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/nfs/nfs.h

## Role

Central NFS internal header for DragonFly’s legacy NFS client/server implementation. It defines tunables, mount argument ABI, mount/status flags, service syscall structures, client request state, server socket/request state, WebNFS helpers, globals, and function prototypes shared across NFS source files.

## Major Definitions

- Tunables for timeouts, retransmits, I/O sizes, readdir size, read-ahead, async BIO limits, uid hash sizes, attribute cache lifetimes, and server write-gather delay.
- `struct nfs_args` defines the user/kernel mount argument ABI with server address, socket/protocol, file handle, flags, I/O sizes, timeout, retransmit, group limit, read-ahead, dead threshold, hostname, and attribute-cache timers.
- `NFSMNT_*` flags configure soft/hard behavior, I/O sizes, timeouts, interruptibility, unconnected sockets, NFSv3, Kerberos, cache/swapcache, read-ahead, reserved ports, readdirplus, and retry/cache timers.
- `NFSSTA_*` flags track runtime mount state such as write verifier, pathconf/fsinfo availability, mountd association, dismount state, send-space warning, and Kerberos auth state.
- `struct nfsd_args`, `struct nfsd_srvargs`, and `struct nfsd_cargs` define `nfssvc()` arguments for server sockets and Kerberos credential exchange.
- `struct nfsstats` records client and server cache/RPC counters when protocol constants are available.
- `struct nfsreq` represents an outstanding client RPC request.
- `struct nfsuid` caches server-side uid/auth mappings.
- `struct nfssvc_sock` represents an NFS server socket, queued raw records, uid hash tables, write-delay lists, and locking/token state.
- `struct nfsd` tracks a server daemon thread and associated authentication/request state.
- `struct nfsrv_descript` describes an NFS server request, including write-gather fields, mbufs, credentials, file handle, reply state, and NFSv3 flags.

## Important Flags and Macros

- `NFS_CMPFH()` compares file handles.
- `NFS_ISV3()` checks mount protocol version.
- `NFS_SRVMAXDATA()` chooses server max data size.
- `NFSINT_SIGMASK()` identifies signals that can interrupt interruptible NFS mounts.
- `NFSIGNORE_SOERROR()` filters ignorable socket errors for datagram sockets.
- `R_*` flags track client request send/timer/soft/intr/socket/async/queue/lock state.
- `SLP_*` flags track server socket receive/disconnect/stream state.
- `ND_*` flags identify server request read/write/check/NFSv3/Kerberos state.
- `NFSW_CONTIG()` and `NFSW_SAMECRED()` support server write gathering.
- WebNFS escape helpers define `%` decoding and native-character handling.
- `NFS_DPF()` provides category-filtered debug printing when `NFS_DEBUG` is enabled.

## API Surface

The header declares broad NFS subsystem APIs, including:

- Initialization and teardown: `nfs_init()`, `nfs_uninit()`, `nfsrv_initcache()`, `nfsrv_destroycache()`, `nfs_nhinit()`, `nfs_nhdestroy()`.
- Client I/O: `nfs_bioread()`, `nfs_vinvalbuf()`, `nfs_readrpc_uio()`, `nfs_writerpc_uio()`, `nfs_commitrpc_uio()`, `nfs_readdirrpc_uio()`, `nfs_readdirplusrpc_uio()`, `nfs_startio()`, `nfs_doio()`, `nfs_asyncio()`, `nfs_asyncok()`.
- RPC/socket handling: `nfs_reply()`, `nfs_send()`, `nfs_connect()`, `nfs_disconnect()`, `nfs_safedisconnect()`, request cancellation, timer, and auth helpers.
- Server request handling for all major NFS procedures: lookup, getattr, setattr, read, write, create, remove, rename, mkdir, rmdir, readdir, readdirplus, symlink, link, fsinfo, pathconf, commit, access, null, and noop.
- Server socket upcalls, receive path, credential mapping, file-handle-to-vnode lookup, public file handle support, write gather, and error mapping.
- IOD thread controls: `nfssvc_iod_reader()`, `nfssvc_iod_writer()`, stop functions, and wakeups.

## Dependencies

Includes vnode, mutex, thread, signal, mbuf, socket, RPC, NFS protocol, mount, and diskless structures through surrounding source files. It is consumed by nearly every NFS client/server implementation file.

## Research Notes

This header is the NFS subsystem contract. It mixes public-ish mount ABI, private client/server state, and cross-file prototypes, so changes here have broad blast radius across NFS VFS, vnode, socket, server, BIO, Kerberos, and diskless boot paths.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/nfs/nfs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/nfs/nfs_bio.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/nfs/nfs_bio.c

## Role

Implements NFS client buffered I/O through DragonFly’s buffer/BIO layer. It handles read caching, directory and symlink reads, write buffering, file-size extension/truncation metadata, async BIO dispatch, synchronous BIO execution, and NFSv3 unstable write/commit handling.

## Major Entry Points

- `nfs_bioread()` services vnode reads for regular files, symlinks, and directories.
- `nfs_write()` services regular-file writes through buffer-cache blocks.
- `nfs_vinvalbuf()` flushes and invalidates vnode buffers with NFS interruptible-mount semantics.
- `nfs_asyncok()` decides whether async NFS BIO submission is currently allowed.
- `nfs_asyncio()` queues a BIO for the per-mount IOD writer thread.
- `nfs_startio()` starts an asynchronous BIO after the writer thread dequeues it.
- `nfs_doio()` executes a BIO synchronously and returns its error.
- `nfs_meta_setsize()` updates `n_size` and calls VM buffer truncate/extend helpers.
- `nfs_readrpc_bio()` and `nfs_readrpc_bio_done()` implement asynchronous BIO read RPCs.
- `nfs_writerpc_bio()` and `nfs_writerpc_bio_done()` implement asynchronous BIO write RPCs.
- `nfs_commitrpc_bio()` and `nfs_commitrpc_bio_done()` implement asynchronous NFSv3 commit RPCs.

## Implementation Notes

- `nfs_bioread()` checks NFSv3 FSINFO lazily before enforcing max file size.
- Approximate cache consistency is maintained by invalidating modified directories, refreshing attributes, and flushing buffers when remote modifications are detected.
- Regular-file reads issue readahead only when async BIO queues and IOD threads are healthy.
- Directory reads use `NFS_DIRBLKSIZ` buffers, cache directory EOF in `n_direofoffset`, and recover from `NFSERR_BAD_COOKIE` by invalidating and rereading directory blocks from the beginning.
- `nfs_check_dirent()` validates server-supplied directory records so arbitrary seek offsets cannot panic the kernel.
- Writes take the mount token, honor pending `NWRITEERR`, load FSINFO, flush local modifications for append or sync writes, and use `nfs_rslock()` for append/extension races.
- File extension updates `n_size` before acquiring buffers so VM/buffer state matches the new logical size.
- Discontiguous dirty ranges in a single buffer force the old dirty range out before accepting the new write, avoiding client-side merging that would worsen multi-client coherency.
- Non-sync full-buffer writes may use async unstable NFSv3 writes when `nfs_async` is enabled; otherwise they stay as delayed writes.
- `nfs_getcacheblk()` uses `GETBLK_PCATCH` for interruptible mounts and stores the logical byte offset directly in `bio_offset`.
- `nfs_asyncio()` tags the BIO with its vnode, inserts it into `nm_bioq`, increments `nm_bioqlen`, and wakes the IOD writer.
- `nfs_startio()` uses dedicated BIO RPC paths for regular-file async reads/writes/commits; symlink and directory async paths are disabled and fall back to synchronous `nfs_doio()`.
- `nfs_doio()` converts BIOs to kernel `uio` operations, handles short-read zero fill, text-file modification kill behavior, directory readdirplus fallback, and synchronous write/commit logic.
- NFSv3 write verifier changes call `nfs_clearcommit()` and force pending unstable data to be rewritten or recommitted.
- Commit failure chains back to a write RPC so dirty data is not silently discarded.

## Dependencies

Uses NFS RPC marshalling helpers, `nfsm_info` request state, NFS mount/node structures, NFS IOD wakeups, buffer cache, BIO callbacks, VM vnode buffer resize APIs, vnode pager sizing, tokens, and NFSv2/v3 protocol constants.

## Research Notes

This file is the client data-path bridge between DragonFly’s VM/buffer cache and NFS RPCs. The highest-risk logic centers on dirty-range accounting, NFSv3 unstable write verifier handling, directory cookie recovery, and async queue state shared with `nfs_iod.c`.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/nfs/nfs_bio.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/nfs/nfs_iod.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/nfs/nfs_iod.c

## Role

Implements per-mount NFS IOD reader and writer kernel threads. These threads drive asynchronous client BIOs, RPC transmission/retransmission, reply processing, shutdown, and wakeup state transitions.

## Major Entry Points

- `nfssvc_iod_reader()` processes requests that have received replies on `nm_reqrxq`.
- `nfssvc_iod_writer()` drains queued BIOs from `nm_bioq` and retransmit/auth work from `nm_reqtxq`.
- `nfssvc_iod_stop1()` marks both IOD directions stopping.
- `nfssvc_iod_stop2()` wakes and waits for both threads to exit.
- `nfssvc_iod_writer_wakeup()` moves the writer from waiting to pending and wakes it.
- `nfssvc_iod_reader_wakeup()` moves the reader from waiting to pending and wakes it.

## Implementation Notes

- Both threads hold the mount token while running their state loops.
- Initial `NFSSVC_INIT` state transitions to `NFSSVC_PENDING`; active loops set state to `NFSSVC_WAITING` until work arrives.
- The reader sleeps only when both the primary request queue and receive queue are empty; otherwise it may call `nfs_reply()` to avoid shutdown hard loops.
- Reader-side reply processing calls `nfs_request()` from `NFSM_STATE_PROCESSREPLY` to `NFSM_STATE_DONE`.
- If reply processing returns `EINPROGRESS`, the request is moved back to the transmit queue for authentication or retransmission work.
- Successful reader completion decrements `nm_bioqlen` and invokes `info->done(info)`.
- The writer throttles new BIO processing when `nm_reqqlen > nfs_maxasyncbio` to avoid exhausting mbufs.
- Dequeued BIOs call `nfs_startio()`, which turns them into RPC requests or synchronous fallback I/O.
- Transmit-queue requests call `nfs_request()` from `NFSM_STATE_AUTH` to `NFSM_STATE_WAITREPLY`.
- Requests that do not enter wait-reply state complete immediately with `info->done(info)` and decrement async BIO accounting.
- Shutdown sets thread pointers to `NULL`, marks state `NFSSVC_DONE`, releases the token, and wakes waiters on the thread pointer.

## Dependencies

Works with `struct nfsmount` queues and state fields, `struct nfsreq`, `struct nfsm_info`, NFS request state machine helpers, `nfs_startio()`, `nfs_reply()`, and async BIO accounting used by `nfs_bio.c`.

## Research Notes

This file is small but central to NFS async progress. It separates send-side work from receive-side completion, and `nm_bioqlen` is only decremented when the associated async request reaches a terminal path.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/nfs/nfs_iod.c -->