# Group Research: group_1250_netbsd_src_sources_os_bsd_netbsd_src_sys_fs_nfs_server_nfs_nfsdstat_38f75151ed88

Scope: `Docs/research_subset_a.md`, limited to the listed NetBSD NFS server and NILFS files. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/nfs/server/nfs_nfsdstate.c -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/nfs/server/nfs_nfsdstate.c

This is the NFS server's NFSv4 state engine. It owns clientid lifecycle, open owners, opens, byte-range lock owners, lock ranges, delegations, NFSv4.1 sessions, callback/backchannel state, lease expiry, stable-storage replay, and state cleanup. Global hash tables track clients, lock-file records keyed by file handle, and sessions; tunables control hash sizes, state limits, delegation issuance, local locking, and write-delegation policy.

Major flows include `nfsrv_setclient`/`nfsrv_getclient` for SETCLIENTID/confirmation/renewal, `nfsrv_opencheck` and `nfsrv_openctrl` for open conflict checking and state creation, `nfsrv_lockctrl` for Lock/LockT/LockU/check/setattr state checks, `nfsrv_openupdate` for confirm/close/downgrade, `nfsrv_delegupdate` and delegation recall helpers, and `nfsrv_checksequence`/session helpers for NFSv4.1 sequencing and reply caching. It also implements administrative revoke, client/lock dumping for `nfssvc`, server timer expiry, old open-owner pruning, and full state teardown.

The file uses two important synchronization layers: the state mutex for normal state list/hash access, and `nfsv4rootfs_lock` to block other nfsd threads while revoking expired clients or rewriting stable state. Several paths deliberately drop vnode/state locks around callbacks, stable-storage writes, local lock syscalls, or sleeps, then retry after state may have changed.

Stable storage is append-log based. `nfsrv_setupstable` reads prior boot/lease/client records to decide which clients may reclaim; `nfsrv_updatestable` rewrites the file after grace; `nfsrv_writestable` appends new-state or revoke records. If the file cannot be read or written reliably, reclaim behavior is constrained and `NFSNSF_OK` is cleared.

Delegation handling performs CB_NULL, CB_RECALL, and CB_GETATTR callbacks, supports NFSv4.1 CB_SEQUENCE/backchannel sessions, delays recalled-delegation timeout up to a limit, and writes revocation records before deleting expired delegation/client state. Local byte-range lock mirroring is optional and maintains a rollback list so vnode advisory locks can be undone if later NFS state checks fail.

Integration points: called by NFSv4 operation handlers, server timer/maintenance paths, `nfssvc` administrative interfaces, vnode/filehandle helpers, RPC callback transport code, reply cache code, stable-storage file I/O, and NFSv4.1 session machinery. It depends heavily on structures and macros from `nfsport.h` and companion server files.

Risks: this file is concurrency- and protocol-sensitive. Correctness depends on strict lock ordering, retry behavior after callbacks/sleeps, stateid sequence semantics, stable-storage durability, and list/hash membership invariants. Several comments document uncertain protocol edge cases, especially delegation conflict policy, same-client read delegation behavior, truncating recalls, and reclaim handling. Counter updates and high-water checks are sometimes approximate by design.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/nfs/server/nfs_nfsdstate.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/nfs/server/nfs_nfsdsubs.c -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/nfs/server/nfs_nfsdsubs.c

This file provides lower-level NFS server support routines for XDR/mbuf manipulation, attribute encoding, filehandle parsing, operation-specific error filtering, name parsing, export security checks, and one-time NFS server state-table initialization.

The first half is dominated by NFSv2, NFSv3, and NFSv4 error maps. `nfsd_errmap` converts kernel errno/NFS internal errors into protocol status values, filtering NFSv3/v4 replies through operation-specific allowed-error tables. NFSv4.1 is treated differently: unsupported ops are normalized and `nfsrv_isannfserr` accepts the broader NFSv4 error range.

Serialization helpers include `nfsrv_adj` for trimming mbuf chains with optional zero-fill, `nfsrv_wcc` and `nfsrv_postopattr` for weak-cache-consistency/post-op attributes, `nfsrv_fillattr` for NFSv2/v3 fattr encoding, and `nfsrv_mtofh` for extracting fixed or counted filehandles, including public-filehandle lookup handling.

NFSv4-specific helpers include `nfsrv_checkuidgid` and `nfsrv_fixattr` for owner/group/time/ACL setattr policy, `nfsrv_errmoved` and `nfsrv_putreferralattr` for referral attributes, `nfsrv_parsename` for component-name extraction and validation, and `nfsd_getminorvers` for parsing the start of a compound and setting the NFSv4.1 flag. UTF-8, nobody, and nogroup checks are sysctl-controlled.

`nfsd_init` allocates and initializes the client, lock-file, and session hash tables used by `nfs_nfsdstate.c`. `nfsd_checkrootexp` checks that a request's security flavor is allowed by the NFSv4 pseudo-root export.

Integration points: used by most NFS server operation handlers and by the NFSv4 state code. It is a protocol boundary file: it translates between mbuf/XDR wire data, NetBSD vnode attributes, kernel credentials, export flags, and NFS status codes.

Risks: the error-map arrays are indexed by protocol operation numbers, so ordering drift is a high-impact maintenance hazard. `nfsrv_fixattr` temporarily mutates `nd_cred->cr_uid` to perform allowed group changes and must restore it. Public-filehandle name parsing includes percent-decoding and slash rules, so small changes can alter externally visible lookup behavior. Disabling UTF-8/nobody/nogroup sysctls relaxes RFC/policy checks.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/nfs/server/nfs_nfsdsubs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/nilfs/Makefile -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/nilfs/Makefile

This kernel include makefile installs NILFS public headers under `/usr/include/fs/nilfs`. It exports `nilfs_mount.h` and `nilfs_fs.h` through NetBSD's `bsd.kinc.mk` include-install machinery.

Integration points: userland and kernel consumers that need NILFS mount arguments or on-disk structure definitions depend on this installed header set. Internal implementation header `nilfs.h` and endian helper `nilfs_bswap.h` are not installed here.

Risk is mainly export drift: if mount ABI or on-disk declarations move to another header, this file must be kept aligned with what userland tools need.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/nilfs/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/nilfs/nilfs.h -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/nilfs/nilfs.h

This is the internal NILFS kernel header. It defines debug categories/macros, inode hash sizing, mount/device/node forward declarations, malloc pools, and core in-memory structures for mounted NILFS devices and per-vnode NILFS nodes.

`struct nilfs_device` represents a backing device and shared filesystem state: device vnode, mount pointer, reference count, device/block sizes, primary and secondary superblocks, metadata file nodes for DAT/CP/SU, metadata layout descriptors, segment/checkpoint running state, last segment summary, super root, sync state, and lists of mounts. `struct nilfs_mount` represents a mounted head/checkpoint/snapshot view. `struct nilfs_node` embeds `genfs_node`, links to vnode/mount/device, stores inode contents, directory hash, node lock fields, file flags, lockf list, and hash-chain membership.

The header also defines NILFS node flag bits such as access/change/update/modify requests, modified/accessed markers, rename/delete state, sleep-lock state, sync state, callback unlock, and node rebuild.

Integration points: included by NILFS vnode, mount, allocation, translation, directory, and sync code. It ties NetBSD genfs/vnode infrastructure to NILFS on-disk structures from `nilfs_fs.h`.

Risks: comments explicitly warn that `node_mutex` should be held before reading/writing node state, and several fields/comments are marked `XXX`, suggesting incomplete or evolving locking/sync design. The in-memory structs are private but central; changes affect every NILFS kernel source file.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/nilfs/nilfs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/nilfs/nilfs_bswap.h -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/nilfs/nilfs_bswap.h

This header defines endian conversion helpers for NILFS scalar fields. On big-endian machines, `nilfs_rw16`, `nilfs_rw32`, and `nilfs_rw64` call byte-swap routines; on little-endian machines they are identity casts.

Integration points: NILFS on-disk structures are little-endian oriented, so callers use these helpers when reading or writing multi-byte on-disk fields across host endian variants.

Risk is caller discipline: this header only provides primitive scalar conversion. Struct fields must be individually converted at every on-disk boundary; missing a conversion on big-endian systems would silently corrupt interpretation.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/nilfs/nilfs_bswap.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/nilfs/nilfs_fs.h -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/nilfs/nilfs_fs.h

This public NILFS on-disk format header defines file flags, bmap/B-tree layout, reserved inode numbers, inode structure, super-root structure, superblock structure, directory entries, segment summaries, DAT entries, checkpoint file entries, and segment-usage file entries.

The bmap definitions describe small direct maps stored inside the inode and larger hierarchical B-trees with `(dkey, dptr)` pairs. Dedicated inode numbers identify root, DAT, checkpoint, segment-usage, ifile, and reserved metadata files. `struct nilfs_inode` stores size, blocks, times, uid/gid, mode, link count, flags, bmap/device code, xattr pointer, and generation.

The super-root records CRC/size/flags/time and embeds DAT, CP, and SU metadata inodes. The superblock records disk revision, magic, CRC data, block/segment geometry, last checkpoint/partial segment/sequence, free blocks, timestamps, mount/check state, creator OS, default reserved uid/gid, inode and metadata-entry sizes, UUID, volume name, commit tuning, and reserved padding. Directory entries are ext2-like with 8-byte alignment.

Segment structures describe log-oriented NILFS partial segments: `nilfs_segment_summary`, per-file `nilfs_finfo`, virtual/DAT block-info records, segment flags, and minimum segment constraints. Metadata-file structures cover block group descriptors, DAT virtual-to-physical validity ranges, checkpoint/snapshot lists and flags, CP file header, segment usage flags, and SU file header.

Integration points: installed for userland tools and included by kernel NILFS code. It is the contract for parsing and constructing NILFS media, so fsck/newfs/mount/debug tools and kernel code must agree on these layouts and constants.

Risks: this is disk-format ABI. Field order, integer width, alignment, endian conversion, CRC byte-count macros, and offset macros must remain stable. The header contains several comments noting reserved/unknown/Linux-derived fields, so compatibility with Linux NILFS and older media depends on conservative interpretation.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/nilfs/nilfs_fs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/nilfs/nilfs_mount.h -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/nilfs/nilfs_mount.h

This public header defines the NILFS mount argument ABI. `NILFSMNT_VERSION` is `1`, and `struct nilfs_args` carries the version, filesystem specifier path, NILFS mount flags, timezone offset, checkpoint number, and reserved expansion space.

Integration points: installed through the NILFS makefile and consumed by mount tooling and kernel mount code. The checkpoint number supports mounting a checkpoint/snapshot view rather than only the live head.

Risks: this is a user/kernel ABI structure. Field ordering, integer widths, pointer handling, and the reserved bytes should remain stable across versions. `NILFSMNT_BITS` is currently empty, so any future mount flags need coordinated definition and decoding.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/nilfs/nilfs_mount.h -->