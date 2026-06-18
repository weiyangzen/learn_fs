# Group Research: group_528_illumos_gate_sources_os_illumos_illumos_gate_usr_src_uts_common_fs_z_253aebb8f23a

Scope: `Docs/research_subset_a.md`  
Repository: `/home/sansha/Github/learn_fs`  
Files read completely: 29

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/zfs_acl.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/zfs_acl.h

Defines ZFS ACL on-disk and in-memory structures. It covers legacy fixed-size ACE ACLs, newer FUID-aware variable-size ACEs, ACL node lists, ACL operation vectors, and create-time ACL identity bundles.

Key elements:
- `zfs_ace_hdr_t`, `zfs_ace_t`, `zfs_object_ace_t`, and `zfs_oldace_t` describe the supported ACE layouts.
- `zfs_acl_phys_v0_t` and `zfs_acl_phys_t` describe old and current ACL physical storage.
- `acl_ops_t` abstracts ACE accessors so ACL code can operate across ACE formats.
- `zfs_acl_t` and `zfs_acl_node_t` represent in-memory ACL chunks.
- `zfs_acl_ids_t` bundles owner/group FUIDs, mode, ACL, and FUID replay info for file creation.

Main dependencies and interactions:
- Depends on `sys/acl.h`, DMU, SA, and `zfs_fuid.h`.
- Used by znode creation, chmod/chown, access checks, ZIL ACL logging, and FUID replay.
- Kernel prototypes expose ACL conversion, allocation, access checking, inheritance transformation, external ACL lookup, and mode computation.

Implementation notes:
- ACL versioning is explicit: initial v0 ACLs use fixed `zfs_oldace_t`; FUID ACLs support variable-size entries.
- `ZFS_ACL_COUNT_SIZE` exists because the count field must be interpreted across both v0 and v1 layouts.
- The file is mostly ABI/structure contract; changing layouts would affect on-disk compatibility and replay.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/zfs_acl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/zfs_bootenv.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/zfs_bootenv.h

Defines string keys used in ZFS label boot-environment nvlists.

Key elements:
- Vendor prefixes: `illumos`, `freebsd`, and `grub`.
- Bootonce and bootonce-used keys for FreeBSD and illumos.
- NV store keys for FreeBSD and illumos.
- `BOOTENV_OS` selects illumos as the local OS namespace.
- `OS_BOOTONCE`, `OS_BOOTONCE_USED`, and `OS_NVSTORE` alias the active OS namespace.

Main dependencies and interactions:
- No subsystem dependencies beyond C++ linkage guards.
- Used wherever ZFS labels store or retrieve boot environment metadata.

Implementation notes:
- This is a shared key contract. Compatibility depends on stable strings, not binary structure layout.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/zfs_bootenv.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/zfs_context.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/zfs_context.h

Provides the illumos kernel context umbrella for ZFS code. It centralizes common kernel headers, prediction macros, CPU sequence access, and AVL/tree comparison helpers.

Key elements:
- Includes kernel primitives for locks, atomics, memory allocation, taskqs, buffers, random data, byte order, lists, uio, zones, sysevents, FMA, DDI, cyclics, and callbacks.
- Defines `_zfs_expect`, `likely`, and `unlikely`.
- Defines `CPU_SEQID` as `CPU->cpu_seqid`.
- Defines `TREE_ISIGN`, `TREE_CMP`, and `TREE_PCMP`.

Main dependencies and interactions:
- Included by many ZFS headers and C files to normalize kernel API availability.
- `TREE_CMP` is used by local AVL comparators such as `unique_compare()`.

Implementation notes:
- The AVL comparison macros are intentionally scoped to ZFS rather than globally modifying illumos `sys/avl.h`.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/zfs_context.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/zfs_ctldir.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/zfs_ctldir.h

Declares the `.zfs` control directory interface, including snapshot control operations and synthetic control-node lookup helpers.

Key elements:
- `ZFS_CTLDIR_NAME` is `.zfs`.
- `zfs_has_ctldir()` checks whether a root znode has an attached control directory.
- `zfs_show_ctldir()` also checks the mount setting controlling visibility.
- Declares create/destroy/init/fini, root lookup, snapshot rename/destroy/unmount, FID creation, and objset lookup functions.
- Defines synthetic inode constants `ZFSCTL_INO_ROOT` and `ZFSCTL_INO_SNAPDIR`.

Main dependencies and interactions:
- Depends on pathname, vnode, `zfs_vfsops.h`, and `zfs_znode.h`.
- Bridges root-directory lookup behavior with mounted snapshot handling.

Implementation notes:
- The macros assume a `znode_t` with `z_zfsvfs`, `z_root`, `z_ctldir`, and `z_show_ctldir`.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/zfs_ctldir.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/zfs_debug.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/zfs_debug.h

Defines ZFS debug flags, debug printf plumbing, panic recovery hook, and debug-message buffering interfaces.

Key elements:
- `ZFS_DEBUG` is enabled for debug builds or non-kernel builds.
- Global controls include `zfs_flags`, `zfs_recover`, and `zfs_free_leak_on_eio`.
- Debug flag bits cover dprintf, dbuf/dnode verification, snapnames, modify, zio free, histogram, metaslab, indirect remap, trim, and log spacemap verification.
- `dprintf_zfs()` emits through `__dprintf()` when `ZFS_DEBUG_DPRINTF` is set.
- `zfs_dbgmsg_t` stores timestamped variable-length debug messages.

Main dependencies and interactions:
- Used broadly by txg and storage code for conditional diagnostics.
- Non-kernel builds expose `dprintf_find_string()`.

Implementation notes:
- `dprintf_zfs()` compiles to no-op outside debug mode.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/zfs_debug.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/zfs_dir.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/zfs_dir.h

Declares ZFS directory-entry locking, lookup, link mutation, node creation/removal, unlinked-set draining, sticky-bit access, and xattr-directory helpers.

Key elements:
- `zfs_dirent_lock()` flags include `ZNEW`, `ZEXISTS`, `ZSHARED`, `ZXATTR`, `ZRENAMING`, `ZCILOOK`, `ZCIEXACT`, and `ZHAVELOCK`.
- Mknode flags: `IS_ROOT_NODE` and `IS_XATTR`.
- Declares link create/destroy, directory lookup, mknode/rmnode, name switching, empty-directory checks, unlinked drain control, sticky remove access, and xattr directory creation/get.

Main dependencies and interactions:
- Depends on pathname, DMU, and `zfs_znode.h`.
- Uses `zfs_dirlock_t`, `znode_t`, `zfsvfs_t`, `zfs_acl_ids_t`, and transactions.

Implementation notes:
- Directory operations are coupled with ZIL logging and znode-level name locks defined in `zfs_znode.h`.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/zfs_dir.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/zfs_fuid.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/zfs_fuid.h

Defines FUID handling for ZFS identity mapping, including domain indexing, log replay support, and user/group/ACE identity categories.

Key elements:
- `zfs_fuid_type_t` distinguishes owner, group, ACE user, and ACE group.
- `FUID_INDEX`, `FUID_RID`, and `FUID_ENCODE` pack and unpack 64-bit FUIDs.
- `zfs_fuid_t` tracks converted ids and log-domain indexes.
- `zfs_fuid_domain_t` tracks unique domain strings.
- `zfs_fuid_info_t` accumulates FUID and domain data needed for create, setattr, and setacl logging/replay.

Main dependencies and interactions:
- Kernel mode depends on kidmap, SID, DMU, and `zfs_vfsops.h`.
- Closely tied to ACLs, ZIL replay, and filesystem FUID tables.
- Shared functions load and destroy FUID AVL tables.

Implementation notes:
- The header documents why FUID replay cannot depend on idmap availability and compresses unique domain strings in the log.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/zfs_fuid.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/zfs_ioctl.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/zfs_ioctl.h

Defines user/kernel ioctl ABI structures, send-stream record formats, feature flags, injection records, sharing state, case-sensitivity modes, and kernel-side ZFS device soft-state helpers.

Key elements:
- Comments require 32-bit and 64-bit layout compatibility, avoiding `long` and adding explicit padding.
- Send stream fields include header type, feature flags, magic, stream flags, replay record union, and payload-size helpers.
- Backup features include dedup, dedupprops, SA spill, embedded data, LZ4, large blocks, resumable, compressed, large dnode, raw, and holds.
- `dmu_replay_record_t` defines BEGIN, OBJECT, FREEOBJECTS, WRITE, FREE, END, WRITE_BYREF, SPILL, WRITE_EMBEDDED, and OBJECT_RANGE layouts.
- `zfs_cmd_t` is the broad ioctl command carrier with nvlist pointers/sizes, legacy fields, replay begin record, inject record, stat data, and send/receive fields.
- `zinject_record_t` and `zinject_type_t` define fault-injection control data.

Main dependencies and interactions:
- Depends on credentials, DMU, ZIO, delegation, SPA, and `zfs_stat.h`.
- Consumed by userland `zfs`/`zpool` tools and kernel ioctl handlers.
- Kernel-only declarations include security policy helpers, `getzfsvfs`, minor allocation, soft-state lookup, and control-device/zvol type selection.

Implementation notes:
- This is a high-risk ABI header: record ordering, field sizes, padding, and feature masks must remain compatible.
- `DMU_STREAM_SUPPORTED()` rejects unknown feature bits outside `DMU_BACKUP_FEATURE_MASK`.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/zfs_ioctl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/zfs_onexit.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/zfs_onexit.h

Declares per-control-device on-exit callback management used to register cleanup actions tied to a ZFS device fd/minor.

Key elements:
- Kernel `zfs_onexit_t` contains a mutex and action list.
- `zfs_onexit_action_node_t` stores callback function and opaque data.
- Declares init/destroy plus fd hold/release, callback add/delete, and callback data lookup.

Main dependencies and interactions:
- Includes `zfs_context.h`.
- Related to `zfs_ioctl.h` soft state, where control device minors can point to `zfs_onexit_t`.

Implementation notes:
- Public helper prototypes are outside `_KERNEL`, indicating user/kernel shared declarations for ioctl support.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/zfs_onexit.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/zfs_project.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/zfs_project.h

Defines ZFS project-id and project-inheritance ioctl compatibility types/constants.

Key elements:
- Maps `ZFS_PROJINHERIT_FL` to `FS_PROJINHERIT_FL` when available, otherwise uses `0x20000000`.
- Uses native `struct fsxattr` and `FS_IOC_FSGETXATTR`/`FS_IOC_FSSETXATTR` when present.
- Otherwise defines fallback `zfsxattr_t` with `fsx_xflags` and `fsx_projid`, plus illumos ioctl numbers.
- Defines `ZFS_DEFAULT_PROJID` as 0 and `ZFS_INVALID_PROJID` as all-ones.
- `zpl_is_valid_projid()` rejects the 32-bit projection of `ZFS_INVALID_PROJID`.

Main dependencies and interactions:
- Used by znode flags/project ID handling and project quota code.
- Has userland include hack to avoid pulling `sys/mount.h`.

Implementation notes:
- The inline validity check handles the mismatch between 32-bit ioctl project IDs and 64-bit internal invalid sentinel.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/zfs_project.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/zfs_rlock.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/zfs_rlock.h

Defines ZFS range-lock structures for coordinating byte-range reads, writes, appends, truncates, and hole punching.

Key elements:
- `rangelock_type_t` has `RL_READER`, `RL_WRITER`, and `RL_APPEND`.
- `rangelock_t` contains an AVL tree, mutex, callback, and callback argument.
- `locked_range_t` records offset, length, type, refcount, condition variables, proxy state, and waiter flags.
- Declares init/fini, enter/exit, and range reduction.

Main dependencies and interactions:
- `znode_t` embeds a `rangelock_t`.
- Used by read/write/truncate paths described in `zfs_znode.h`.

Implementation notes:
- The structure supports coalesced range locks and waiting readers/writers.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/zfs_rlock.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/zfs_sa.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/zfs_sa.h

Defines ZPL system-attribute IDs, legacy znode physical layout, SA offsets, attribute registration tables, and SA helper prototypes.

Key elements:
- `zpl_attr_t` lists ZPL attributes such as times, generation, mode, size, parent, links, xattr, rdev, flags, uid/gid, ACL, symlink, scanstamp, and project ID.
- `ZFS_OLD_ZNODE_PHYS_SIZE` and `ZFS_SA_BASE_ATTR_SIZE` bridge legacy bonus-buffer layout to SA storage.
- Offset constants describe legacy attribute positions.
- `znode_phys_t` is the deprecated pre-ZPL-v5 physical znode layout.
- Kernel prototypes support SA readlink, symlink storage, upgrade, scanstamp get/set, and txholds.

Main dependencies and interactions:
- Kernel includes DMU, ZFS ACL, znode, SA, and ZIL.
- Works with `zfs_znode.h` macros that index `zfsvfs_t->z_attr_table`.

Implementation notes:
- Attribute enum values are not on-disk IDs; actual numeric IDs come from SA registration per filesystem.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/zfs_sa.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/zfs_stat.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/zfs_stat.h

Defines a small ZPL statistics structure exported through ioctl paths.

Key elements:
- `zfs_stat_t` contains generation, mode, link count, and ctime.
- Declares `zfs_obj_to_stats()` to convert an object number into stats and optional path/name buffer data.

Main dependencies and interactions:
- Used by `zfs_ioctl.h` inside `zfs_cmd_t`.
- Current documented consumer is `zfs diff`.

Implementation notes:
- This is a deliberately limited stat ABI, not a full vnode/stat replacement.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/zfs_stat.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/zfs_vfsops.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/zfs_vfsops.h

Defines mount-wide ZFS filesystem state (`zfsvfs_t`), NFS filehandle formats, quota/user accounting entry points, and filesystem lifecycle helpers.

Key elements:
- `zfsvfs_t` stores VFS pointer, parent filesystem, objset, root/unlinked objects, max block size, FUID state, ZIL pointer, ACL settings, case/UTF-8/normalization settings, atime, teardown locks, znode lists, root/control vnodes, snapshot and SA/FUID flags, quota object IDs, replay state, SA attribute table, znode hold mutexes, and unlink-drain task.
- `zfid_short_t` and `zfid_long_t` encode normal and snapshot filehandles under object/generation/objset size constraints.
- Defines `SHORT_FID_LEN` and `LONG_FID_LEN`.

Main dependencies and interactions:
- Includes VFS, ZIL, SA, rrwlock, ioctl, and DSL dataset headers.
- Used by znode, control directory, FUID, quota, mount, suspend/resume, and temporary property code.

Implementation notes:
- Filehandle layout is constrained by NFSv2/NFSv3 historical limits and DMU 48-bit object IDs.
- `ZFS_OBJ_MTX_SZ` controls the hash table used by znode object-hold locks.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/zfs_vfsops.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/zfs_znode.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/zfs_znode.h

Defines per-file znode state, persistent file flags, SA attribute lookup macros, directory-entry locks, vnode/ZFS entry macros, timestamp helpers, and ZIL logging entry points for ZPL operations.

Key elements:
- Persistent pflags include readonly, hidden, system, archive, immutable, nounlink, append-only, nodump, opaque, antivirus, reparse, offline, sparse, project inheritance, and project ID.
- Internal flags include xattr, inheritable ACE, trivial ACL, object ACE, protected/defaulted/autoinherit ACL, scanstamp, and exec-deny state.
- SA macros map ZPL attributes through `zfsvfs_t->z_attr_table`.
- `zfs_dirlock_t` serializes per-directory name operations.
- `znode_t` stores filesystem/vnode pointers, object ID, locks, range lock, cached metadata, ACL cache, project ID, all-znode list linkage, SA handle, and native-SA flag.
- `ZFS_ENTER`, `ZFS_EXIT`, and `ZFS_VERIFY_ZP` guard vnode/vfs operation entry against teardown/unmount.

Main dependencies and interactions:
- Kernel includes VFS/ZPL state, SA, stats, rrwlock, and range locks.
- Declares core functions for filesystem init/create, zget/rezget/inactive/delete/free, sync, object-to-path/stats, timestamp update, freespace, block growth, upgrades, share dir creation, and page map/unmap.
- Declares ZIL log helpers for create/remove/link/symlink/rename/write/truncate/setattr/ACL.

Implementation notes:
- The range-lock rules are documented here and govern file size/read/write/truncate correctness.
- Project ID inheritance is inline: child objects inherit only when parent has `ZFS_PROJINHERIT`.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/zfs_znode.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/zil.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/zil.h

Defines the ZFS Intent Log public/on-disk record format, transaction type constants, log record structures, write-state categories, parser/replay callbacks, and ZIL lifecycle APIs.

Key elements:
- `zil_header_t` stores claim/replay sequencing, log chain block pointer, flags, and padding.
- `zil_chain_t` describes log block chaining and trailer checksum placement.
- Transaction types cover create, mkdir, xattr mkdir, symlink, remove, rmdir, link, rename, write, truncate, setattr, ACL formats, create/mkdir variants with ACL/attrs, and write2.
- `TX_CI` marks case-insensitive operation variants.
- `TX_OOO()` identifies record types that can be logged out of order.
- `lr_t` is the common log record header; specific `lr_*` structs define create, ACL create, remove, link, rename, write, truncate, setattr, and ACL records.
- `itx_t` is the in-memory intent transaction wrapper.

Main dependencies and interactions:
- Depends on SPA, ZIO, DMU, and ZIO crypto.
- Used by ZPL logging in `zfs_znode.h` and ZIL internals in `zil_impl.h`.
- Exposes parse, replay, claim, sync, suspend/resume, commit, destroy, and LWB block tracking APIs.

Implementation notes:
- Many structures are on-disk ABI and must stay cross-architecture aligned.
- Large dnode slot count is packed into high object-ID bits for log record compatibility.
- Write logging has three states: indirect block pointer, copied immediate data, or deferred copy.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/zil.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/zil_impl.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/zil_impl.h

Defines private ZIL implementation structures for log write blocks, commit waiters, intent transaction grouping, async transaction trees, vdev flush tracking, and the `zilog_t` state object.

Key elements:
- `lwb_state_t` models log write block lifecycle: closed, opened, issued, write done, flush done.
- `lwb_t` stores block pointer, buffer, write/root zios, allocation tx, max txg, waiter list, vdev flush tree, and timing.
- `zil_commit_waiter_t` coordinates `zil_commit()` completion with condition variable, lock, LWB pointer, done flag, and zio error.
- `itxs_t`, `itxg_t`, and `itx_async_node_t` organize sync and async intent transactions per txg.
- `zil_vdev_node_t` tracks vdevs requiring cache flush after log writes.
- `zilog_t` holds locks, pool/spa/objset pointers, sequencing, suspend/replay flags, issuer lock, logbias/sync policy, parse statistics, per-txg intent lists, LWB list, BP tree, dirty linkage, and previous block sizes.

Main dependencies and interactions:
- Includes `zil.h` and DMU objset internals.
- Private to ZIL implementation and sync/commit paths.

Implementation notes:
- Comments precisely define lock ownership: `zl_issuer_lock` protects pre-issue LWB transitions; `zl_lock` protects completion transitions.
- `ZIL_MAX_LOG_DATA`, `ZIL_MAX_WASTE_SPACE`, and `ZIL_MAX_COPIED_DATA` tune immediate vs deferred write logging behavior.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/zil_impl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/zio.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/zio.h

Defines the public ZIO interface, block checksumming structures, checksum/compression/encryption constants, I/O flags, bookmarks, child types, transform stack, `zio_t`, allocation helpers, I/O constructors, execution APIs, fault injection, checksum ereports, and bookmark comparison helpers.

Key elements:
- `zio_eck_t` is the embedded checksum trailer.
- `zio_gbh_phys_t` defines self-checksumming gang block headers.
- `enum zio_checksum` lists supported checksum algorithms and pseudo-values.
- Encryption data lengths are defined for objset MAC, data IV, salt, and MAC.
- `enum zio_flag` controls aggregation, repair, scrub/resilver, physical I/O, failure behavior, caching, retry, queueing, raw compression/encryption, gang/DDT child state, nopwrite, reexecution, and delegation.
- `zbookmark_phys_t` identifies blocks by objset/object/level/blkid and has special root/ZIL/dnode conventions.
- `zio_prop_t` carries checksum, compression, object type, level, copies, dedup/nopwrite, small block, encryption metadata, byteorder, salt/IV/MAC.
- `zio_t` stores core I/O identity, callback state, data ABDs, vdev state, timing, pipeline state, errors, child/parent counts, gang state, synchronization, FMA checksum report, and taskq dispatch state.

Main dependencies and interactions:
- Includes priority, context, SPA, TXG, AVL, ZFS public definitions, and `zio_impl.h`.
- Used across DMU, vdev, ZIL, spa sync, scrubs, resilver, fault injection, and ereporting.

Implementation notes:
- `ECKSUM` and `EFRAGS` reuse otherwise-unused errno values.
- Child flag macros define which flags propagate to DDT, gang, and vdev child I/Os.
- The `zio_t` structure is central pipeline state; lock and child counters are correctness-critical.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/zio.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/zio_checksum.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/zio_checksum.h

Defines checksum function signatures, checksum metadata flags, ABD checksum iteration hooks, checksum info table entries, bad-checksum reports, and checksum compute/verify APIs.

Key elements:
- `zio_checksum_t` computes a checksum over an ABD.
- Template init/free hooks support salted algorithms.
- Flags identify metadata-safe, embedded, dedup-safe, salted, and nopwrite-safe checksums.
- `zio_abd_checksum_func_t` provides init/fini/iter callbacks for ABD checksum traversal.
- `zio_checksum_info_t` records byteorder-specific functions, template hooks, flags, and name.
- `zio_bad_cksum_t` reports expected/actual checksum, algorithm name, byteswap, injection, and validity.

Main dependencies and interactions:
- Depends on `zio.h`, feature mapping, and Fletcher support.
- Declares SHA, Skein, Edon-R, and Fletcher checksum entry points.
- Exposes checksum equality, compute, error, dedup checksum selection, template cleanup, and feature mapping.

Implementation notes:
- Byteorder is explicit through `ZIO_CHECKSUM_NATIVE` and `ZIO_CHECKSUM_BYTESWAP`.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/zio_checksum.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/zio_compress.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/zio_compress.h

Defines ZIO compression algorithm IDs, compression/decompression function signatures, compression info table, algorithm entry points, and generic compression/decompression wrappers.

Key elements:
- `enum zio_compress` includes inherit, on, off, LZJB, empty, gzip levels 1-9, ZLE, LZ4, and functions sentinel.
- `zio_compress_func_t`, `zio_decompress_func_t`, and `zio_decompress_abd_func_t` define common algorithm signatures.
- `zio_compress_info_t` stores name, level, compress function, and decompress function.
- Declares LZJB, gzip, ZLE, and LZ4 routines.
- Generic wrappers operate on ABD input or raw buffers.

Main dependencies and interactions:
- Includes `sys/abd.h`.
- Used by ZIO write compression and read decompression pipelines.

Implementation notes:
- ABD-specific decompression signature exists to support compressed ARC plus scatter ABDs without requiring every algorithm to implement it.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/zio_compress.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/zio_crypt.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/zio_crypt.h

Defines ZIO encryption algorithm metadata, loaded-key representation, wrapping/unwrapping, IV/salt/MAC encoding helpers, indirect MAC checksums, HMAC helpers, and data/ABD encryption-decryption entry points.

Key elements:
- Constants define wrapping key/IV/MAC lengths, master key maximum, HMAC key length, and key format version.
- `zio_crypt_type_t` distinguishes none, CCM, and GCM.
- `zio_crypt_info_t` maps crypto mechanism name, mode type, key length, and human-readable name.
- `zio_crypt_key_t` stores encryption algorithm, version, GUID, master/HMAC/current key data, salt, salt use count, illumos crypto keys/templates, and salt lock.
- Prototypes cover key init/destroy, salt retrieval, key wrap/unwrap, IV generation, dedup IV/salt generation, block pointer parameter/MAC encode/decode, ZIL MAC encode/decode, dnode bonus copying, indirect MAC checksum, HMACs, objset HMACs, and data/ABD crypt.

Main dependencies and interactions:
- Depends on DMU, refcount, illumos crypto API, nvpair, AVL, and ZIO.
- Used by encrypted ZIO pipeline stages, raw send/receive metadata, and encrypted ZIL/objectset handling.

Implementation notes:
- Encryption routines expose both linear-buffer and ABD variants.
- Dedup encryption requires deterministic IV/salt generation from plaintext.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/zio_crypt.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/zio_impl.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/zio_impl.h

Defines private ZIO pipeline stage bits and precomposed pipeline masks for read, write, free, claim, ioctl, trim, DDT, gang, and vdev child I/O.

Key elements:
- `enum zio_stage` covers open, BP init, async issue, compression, encryption, checksum generate/verify, nopwrite, DDT read/write/free, gang assemble/issue, DVA throttle/allocate/free/claim, ready, vdev I/O start/done/assess, and done.
- Pipeline masks include interlock, vdev child, read physical, read logical, DDT read, write physical, rewrite, write, DDT child write, DDT write, free, DDT free, claim, ioctl, trim, and blocking stages.
- Declares `zio_inject_init()` and `zio_inject_fini()`.

Main dependencies and interactions:
- Included by `zio.h`.
- Used internally by ZIO executor to advance I/O through staged behavior.

Implementation notes:
- The header comment documents compression, dedup, nopwrite, and encryption transformations.
- Nopwrite is explicitly mutually exclusive with encryption except encrypted dedup has special deterministic handling.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/zio_impl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/zio_priority.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/zio_priority.h

Defines queue priority classes for ZIO scheduling.

Key elements:
- `zio_priority_t` includes sync read, sync write/ZIL, async read/prefetch, async write/spa_sync, scrub/resilver, vdev removal, initializing, trim, queueable sentinel, and now/non-queued I/O.
- Comment requires `ZIO_PRIORITY_NUM_QUEUEABLE` to match the public `ZIO_PRIORITY_N_QUEUEABLE` value in `uts/common/sys/fs/zfs.h`.

Main dependencies and interactions:
- Included by `zio.h`.
- Consumed by vdev queueing and ZIO creation APIs.

Implementation notes:
- Ordering is a scheduler contract. Changes must be mirrored in public ZFS definitions.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/zio_priority.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/zrlock.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/zrlock.h

Defines a small reference-style lock with wait-for-zero behavior and optional debug owner tracking.

Key elements:
- `zrlock_t` contains mutex, volatile refcount, condition variable, padding, and debug owner/caller fields under `ZFS_DEBUG`.
- Declares init/destroy, add/remove, tryenter/exit, zero check, locked check, and debug owner accessor.
- `zrl_add()` macro passes `__func__` to `zrl_add_impl()`.

Main dependencies and interactions:
- Includes `zfs_context.h`.
- Used where subsystems need to prevent teardown until reference count reaches zero.

Implementation notes:
- The debug caller capture helps identify the ref holder in diagnostics.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/zrlock.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/zthr.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/zthr.h

Declares the ZFS helper-thread abstraction.

Key elements:
- Opaque `zthr_t`.
- `zthr_func_t` is the worker callback signature.
- `zthr_checkfunc_t` decides whether work should run.
- Creation APIs support normal and timer-based helper threads.
- Declares destroy, wakeup, cancel, resume, and cancellation query.

Main dependencies and interactions:
- Used by background ZFS services that need a cancellable/resumable loop.
- The header relies on surrounding includes for `boolean_t` and `hrtime_t`.

Implementation notes:
- The API separates readiness checking from execution callback.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/zthr.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/zvol.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/zvol.h

Declares ZFS volume constants and kernel block-device entry points.

Key elements:
- `ZVOL_OBJ` and `ZVOL_ZAP_OBJ` identify volume object slots.
- Declares volume size/blocksize validation, stats, creation callback, minor create/remove, volume resize, and busy/init/fini.
- Declares device operations: open, close, dump, strategy, read/write, async read/write, ioctl.
- Declares helper accessors for volume params, size, write-cache-enable setting, and minor-based ZIL write logging.

Main dependencies and interactions:
- Includes `zfs_context.h`.
- Integrates ZFS objsets with illumos block device interfaces and ZIL logging.

Implementation notes:
- The params accessor returns opaque handles for minor, objset, ZIL, range lock, and bonus state.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/zvol.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/txg.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/txg.c

Implements ZFS transaction group lifecycle management: initialization, sync/quiesce thread control, open/quiesce/sync transitions, commit callback dispatch, wait/kick/delay helpers, active-txg verification, and per-txg intrusive lists.

Key elements:
- Top comment explains the txg state machine: open accepts mutations, quiescing waits for in-flight transactions, syncing writes stable state and executes synctasks.
- `txg_init()` allocates per-CPU txg state, initializes locks, condition variables, callback lists, and starting open txg.
- `txg_fini()` tears down locks/CVs/taskq/per-CPU storage after threads are stopped.
- `txg_sync_start()` starts quiesce and sync kernel threads.
- `txg_sync_stop()` waits through deferred txgs, signals exit, and waits for both threads.
- `txg_hold_open()`, `txg_rele_to_quiesce()`, `txg_register_callbacks()`, and `txg_rele_to_sync()` manage transaction holds and per-txg callback lists.
- `txg_quiesce()` advances the open txg and waits for all per-CPU hold counts to drain.
- `txg_sync_thread()` waits for timeout, scan activity, waiters, dirty threshold, or quiesced txg; then calls `spa_sync()` and dispatches callbacks.
- `txg_quiesce_thread()` waits for a requested future txg, quiesces the current open txg, and hands it to sync.
- `txg_delay()` rate-limits open txg writers when syncing/quiescing backlog exists.
- `txg_wait_synced()`, `txg_wait_synced_sig()`, `txg_wait_open()`, and `txg_kick()` provide external coordination.
- `txg_list_*()` implements per-txg intrusive linked lists over objects embedding `txg_node_t`.

Main dependencies and interactions:
- Depends on txg internals, DMU transaction internals, DSL pool/scan, ZIL, and CPR callbacks.
- Calls `spa_sync()` for actual pool sync.
- Uses `dsl_scan_active()`, dirty-data thresholds, `dmu_tx_do_callbacks()`, taskqs, DTrace probes, and condition variables.

Implementation notes:
- Per-CPU `tc_open_lock` lets most transactions enter the open txg with low contention; quiesce temporarily grabs all such locks to advance the open txg.
- Commit callbacks are moved out of per-CPU lists after sync and dispatched asynchronously on a lazily created taskq.
- `txg_verify()` asserts non-initial txgs are within the active window unless using `ZILTEST_TXG`.
- `txg_all_lists_empty()` is intentionally racy and documented as such.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/txg.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/uberblock.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/uberblock.c

Implements basic uberblock verification and update logic.

Key elements:
- `uberblock_verify()` byteswaps the whole uberblock if the magic matches byteswapped `UBERBLOCK_MAGIC`, then validates the magic.
- `uberblock_update()` asserts txg monotonicity, fills magic, txg, root vdev guid sum, timestamp, software version, MMP magic/config fields, clears checkpoint txg, and reports whether the root block was born in this txg.

Main dependencies and interactions:
- Includes ZFS context, uberblock internals, vdev internals, and MMP.
- Reads root vdev `vdev_guid_sum` and pool multihost setting.
- Uses `zfs_multihost_interval` and `zfs_multihost_fail_intervals` for MMP config.

Implementation notes:
- It intentionally does not update `ub_version`, preserving older uberblock version behavior.
- MMP fields are zeroed when multihost is disabled.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/uberblock.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/unique.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/unique.c

Implements a process-wide unique 64-bit value allocator backed by an AVL tree and random generation.

Key elements:
- Static `unique_avl` tracks allocated values.
- Static `unique_mtx` serializes tree access.
- `unique_t` stores AVL linkage and value.
- `UNIQUE_MASK` limits generated values to `UNIQUE_BITS`.
- `unique_init()` creates the AVL tree and mutex.
- `unique_fini()` destroys them.
- `unique_create()` obtains a unique value through `unique_insert(0)` and immediately removes it, returning a currently-unused random value.
- `unique_insert()` accepts a requested value or generates random values until nonzero, within mask, and absent from the AVL tree.
- `unique_remove()` removes a value if present.

Main dependencies and interactions:
- Includes ZFS context, AVL, and `sys/unique.h`.
- Uses `TREE_CMP()` from `zfs_context.h` and `random_get_pseudo_bytes()`.

Implementation notes:
- `unique_insert()` drops the mutex while generating random bytes, then reacquires and retries validation.
- Values are tracked only while inserted; `unique_create()` returns an unreserved value by design.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/unique.c -->