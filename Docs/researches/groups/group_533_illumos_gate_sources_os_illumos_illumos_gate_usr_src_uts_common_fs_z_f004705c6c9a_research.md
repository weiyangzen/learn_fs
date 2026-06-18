# Group Research: group_533_illumos_gate_sources_os_illumos_illumos_gate_usr_src_uts_common_fs_z_f004705c6c9a

Scope: `Docs/research_subset_a.md`; source tree: `sources/os/illumos/illumos-gate`. All listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/zfs.conf -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/zfs.conf

Registers the ZFS kernel module as a pseudo-device with `name="zfs" parent="pseudo";`. This is the driver/module configuration stub used by illumos packaging and module loading, not filesystem behavior logic.

The file is otherwise license/header metadata. Its operational effect is limited to making the ZFS module appear under the pseudo device parent so the kernel can attach the ZFS subsystem through normal module configuration paths.

There are no tunables, functions, state machines, or cross-file logic in this file.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/zfs.conf -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/zfs_acl.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/zfs_acl.c

Implements ZFS ACL storage, conversion, inheritance, chmod rewriting, retrieval, setting, and access checks. It bridges illumos vnode/security APIs, ZFS znodes/SAs/DMU objects, NFSv4-style ACEs, legacy ZFS ACL layouts, and FUID/SID-aware identity handling.

The file supports two ACL layouts through `acl_ops_t`: legacy fixed `zfs_oldace_t` entries and FUID-aware variable-sized entries with compact owner/group/everyone ACEs plus optional object ACE data. `zfs_acl_alloc()`, `zfs_acl_node_alloc()`, `zfs_acl_node_read()`, and `zfs_aclset_common()` manage in-memory ACL lists, cached ACLs on znodes, SA-stored ACL attributes, embedded legacy ACLs, and external DMU ACL objects. Legacy ACLs may be transformed to FUID format by `zfs_acl_xform()` when the dataset version supports it.

ACL validation and translation are centralized in `zfs_acl_valid_ace_type()`, `zfs_ace_valid()`, `zfs_copy_ace_2_fuid()`, `zfs_copy_fuid_2_ace()`, `zfs_copy_ace_2_oldace()`, and `zfs_vsec_2_aclp()`. These functions validate ACE type/flag combinations, reject object ACEs for old ACL versions, convert POSIX IDs to ZFS FUIDs, map FUIDs back to uid/gid values, preserve object ACE GUID data, and track ACL-wide hints such as `ZFS_INHERIT_ACE`, `ZFS_ACL_OBJ_ACE`, `ZFS_ACL_PROTECTED`, `ZFS_ACL_DEFAULTED`, and `ZFS_ACL_AUTO_INHERIT`.

Mode synthesis and chmod behavior are handled by `zfs_mode_compute()` and `zfs_acl_chmod()`. `zfs_mode_compute()` walks ACEs in order to infer Unix mode bits and the `ZFS_NO_EXECS_DENIED` optimization flag. `zfs_acl_chmod()` rewrites owner/group/everyone ACEs from trivial access masks, optionally splits inheritable trivial ACEs into inherit-only copies, and applies the `aclmode=groupmask` trimming rule. `zfs_acl_chmod_setattr()` and `zfs_acl_chown_setattr()` are setattr helpers that read or rebuild ACLs and recompute mode.

Creation-time ACL construction happens in `zfs_acl_ids_create()`. It derives owner/group FUIDs from credentials or explicit vnode attributes, enforces setgid inheritance and privilege rules, optionally inherits ACEs from the parent via `zfs_acl_inherit()`, creates trivial ACLs when there is no inheritable parent ACL, and returns a `zfs_acl_ids_t` bundle used by node creation. `zfs_acl_ids_overquota()` checks user, group, and project quotas before creation, and `zfs_acl_ids_free()` releases associated ACL/FUID tracking data.

User-visible ACL operations are `zfs_getacl()` and `zfs_setacl()`. `zfs_getacl()` checks `ACE_READ_ACL`, uses the cached ACL when possible, filters object ACEs unless `VSA_ACE_ALLTYPES` is requested, and returns ACL-wide flags. `zfs_setacl()` checks immutability and `ACE_WRITE_ACL`, converts the supplied `vsecattr_t`, reserves DMU transaction holds for SA/FUID/external ACL updates, calls `zfs_aclset_common()`, updates the ACL cache, syncs dirty FUID tables, and writes a ZIL ACL log record.

Access enforcement is split across dataset checks, ACE checks, and privilege fallbacks. `zfs_zaccess_dataset_check()` rejects writes on read-only mounts, data writes to immutable files, deletes of nounlink files, and reads/executes of quarantined files. `zfs_zaccess_aces_check()` evaluates ACEs in order, removing satisfied access-of-interest bits so later ACEs cannot override earlier results. `zfs_zaccess_common()` adds replay/skip-ACL/read-only-DOS handling, while `zfs_zaccess()` maps ACE masks to vnode `VREAD/VWRITE/VEXEC` bits and invokes illumos `secpolicy_*` fallbacks for owner and privileged access.

Specialized access helpers include `zfs_fastaccesschk_execute()` for a hot execute-access path using mode bits and `ZFS_NO_EXECS_DENIED`, `zfs_zaccess_rwx()` and `zfs_zaccess_unix()` for Unix-mode callers, `zfs_has_access()` for “any access” checks, `zfs_zaccess_delete()` for Windows-like delete/delete-child semantics plus sticky-directory and compatibility handling, and `zfs_zaccess_rename()` for rename as delete plus add-file/add-directory permission.

Important invariants: ACL iteration uses per-call `zfs_acl_iter_t` state so multiple threads can iterate independently; ACL cache replacement is protected by `z_acl_lock`; SA-upgrade races are handled by retry/verification around `z_is_sa`; checksum errors reading external ACL objects are surfaced as `EIO`; object ACEs set persistent hints so later `getacl` calls know whether filtering is needed.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/zfs_acl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/zfs_byteswap.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/zfs_byteswap.c

Provides endian conversion routines for ZFS on-disk znode and ACL data. These are used when importing or reading metadata written with byte order different from the host.

`zfs_oldace_byteswap()` swaps arrays of old fixed-size `ace_t` entries. `zfs_oldacl_byteswap()` treats the whole supplied buffer as fixed old ACE slots because the old layout does not independently encode how many valid ACEs are present.

`zfs_ace_byteswap()` handles both POSIX `ace_t` layout and ZFS FUID ACL layout. It walks the supplied byte buffer, swaps ACE header fields, chooses the entry size based on special owner/group/everyone compact entries, normal FUID entries, and object ACE entries, and avoids overrunning partially filled embedded ACL blocks. For ZFS-layout entries it swaps `z_fuid` only when the full `zfs_ace_t` body is present.

`zfs_acl_byteswap()` is the public wrapper for modern ZFS ACL layout. `zfs_znode_byteswap()` swaps every fixed-width field in `znode_phys_t`, including timestamps, mode, size, parent, link count, xattr, rdev, flags, uid/gid/FUIDs, ZAP object, padding, and embedded ACL physical metadata. It then dispatches to modern or old ACL byteswapping based on the swapped ACL version.

The main safety concern addressed here is bounded parsing of variable-sized ACE records inside fixed-size znode bonus data; short trailing fragments are ignored rather than read past the buffer.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/zfs_byteswap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/zfs_ctldir.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/zfs_ctldir.c

Implements the virtual ZFS control directory `.zfs`, including `.zfs/snapshot` and `.zfs/shares`. These nodes are built with illumos GFS primitives and do not exist as normal on-disk directory entries. Snapshot entries under `.zfs/snapshot` are GFS mountpoints that trigger kernel automounts of snapshot datasets.

Initialization and lifecycle are handled by `zfsctl_init()`, `zfsctl_fini()`, `zfsctl_create()`, `zfsctl_destroy()`, `zfsctl_root()`, and `zfsctl_is_node()`. The root `.zfs` vnode is cached in `zfsvfs->z_ctldir`, has synthetic inode/time attributes, and exposes two entries: `snapshot` and `shares`. The control vnodes reject write opens/access and provide FIDs suitable for NFS exposure.

The `.zfs/snapshot` implementation maintains an AVL tree of currently known or mounted snapshot entries (`zfs_snapentry_t`) protected by `sd_lock`. `zfsctl_snapdir_lookup()` validates and resolves snapshot names, handles case-insensitive real-name lookup, creates a GFS snapshot vnode when needed, mounts the ZFS snapshot on that vnode via `domount()`, traverses to the mounted root, and then rewrites the mounted root vnode’s `v_vfsp` to the parent filesystem for NFS compatibility. If a cached snapshot vnode was unmounted behind its back, lookup remounts it.

Snapshot mutation operations are implemented as directory operations on `.zfs/snapshot`. `zfsctl_snapdir_mkdir()` creates a snapshot after permission checks. `zfsctl_snapdir_remove()` unmounts and destroys a snapshot. `zfsctl_snapdir_rename()` renames a snapshot after resolving case variants and checking permissions, then updates both the AVL entry and mounted VFS resource/mountpoint strings with `zfsctl_rename_snap()`.

Directory enumeration uses `zfsctl_snapdir_readdir_cb()` to list snapshots directly from DMU snapshot iteration, including case-conflict flags when requested. Attribute reporting for `.zfs/snapshot` uses the number of cached mounted entries for link/size and the dataset snapshot cmtime for timestamps.

The `.zfs/shares` directory is a virtual pass-through to `zfsvfs->z_shares_dir` when configured. `zfsctl_shares_lookup()`, `zfsctl_shares_readdir()`, `zfsctl_shares_getattr()`, and `zfsctl_shares_fid()` delegate to the real shares directory znode; absent shares support returns `ENOTSUP`.

Unmount and cleanup paths are explicit. `zfsctl_unmount_snap()` force/unmounts a snapshot vfs, releases the GFS vnode without recursing into the snapdir inactive path, and frees the AVL entry. `zfsctl_snapshot_inactive()` removes an unused snapshot mountpoint vnode from the AVL tree. `zfsctl_lookup_objset()` maps a mounted snapshot objset ID back to its `zfsvfs_t`, and `zfsctl_umount_snapshots()` unmounts all mounted snapshots for a filesystem during parent unmount.

Key invariants: `.zfs` rejects extended-attribute lookup; snapshot mountpoint vnodes are expected to be covered and have almost no operations; recursive lookup while holding `sd_lock` returns `ENOENT` to avoid mount recursion; mounted snapshot roots deliberately masquerade as part of the parent VFS for NFS behavior.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/zfs_ctldir.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/zfs_debug.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/zfs_debug.c

Implements a small global in-kernel ZFS debug message buffer. Messages are stored in `zfs_dbgmsgs`, protected by `zfs_dbgmsgs_lock`, with a byte-size limit controlled by `zfs_dbgmsg_maxsize` defaulting to 4 MiB.

`zfs_dbgmsg_init()` creates the list and initializes the mutex. `zfs_dbgmsg_fini()` drains all stored messages, frees their variable-sized allocations, destroys the mutex, and asserts that accounting returned to zero.

`zfs_dbgmsg()` formats a printf-style message into a variable-sized `zfs_dbgmsg_t`, records wall-clock and high-resolution timestamps, emits a DTrace probe, appends the record to the list, and trims oldest records until `zfs_dbgmsg_size` is below the configured limit.

`zfs_dbgmsg_print()` prints all currently buffered messages under the lock with a caller-supplied tag. The comments document inspection through MDB `::zfs_dbgmsg` and DTrace probes.

The design is intentionally lossy under pressure: newest messages are kept and oldest messages are freed once the byte cap is exceeded.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/zfs_debug.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/zfs_dir.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/zfs_dir.c

Implements ZFS directory name lookup/locking, link creation/destruction, unlinked-set cleanup, extended-attribute directory creation, and sticky-directory remove policy. It is the core glue between VFS name operations, ZAP directory objects, DNLC caching, znode link counts, and DMU transactions.

Name lookup begins with `zfs_match_find()` and `zfs_dirent_lock()`. `zfs_dirent_lock()` serializes operations on a specific directory name, rejecting `.`, `..`, and `.zfs`, selecting normalized/case-sensitive/case-insensitive matching based on dataset properties and lookup flags, optionally using DNLC, and taking either narrow or wide dirlocks to avoid races in mixed-case filesystems. It returns both a held target znode and a dirlock that protects the ZAP entry until `zfs_dirent_unlock()`.

`zfs_dirlook()` handles special names: empty/`.` returns the directory itself, `..` resolves via parent SA attribute with a special case for snapshots mounted under `.zfs`, and `.zfs` returns the synthetic control directory when present. Ordinary names use `zfs_dirent_lock()` with shared locking and optional case-insensitive lookup, then enable znode prefetch after successful lookup.

The unlinked set is the crash-safe delete queue. `zfs_unlinked_add()` inserts zero-link znodes into the filesystem unlinked ZAP. `zfs_unlinked_drain()` dispatches asynchronous cleanup, `zfs_unlinked_drain_stop_wait()` cancels/waits on it, and `zfs_unlinked_drain_task()` walks the unlinked set, rehydrates znodes, marks them unlinked, and lets inactive processing remove them. `zfs_rmnode()` performs final deletion: purges xattr directories when needed, frees file contents, unlinks xattr directories, frees external ACL objects, removes the znode from the unlinked set, and calls `zfs_znode_delete()` in a net-free transaction.

`zfs_link_create()` links a znode into a directory ZAP, increments child link count unless renaming, updates parent ID and flags on the child, updates directory size/link/timestamps, stores a dirent value that can include file type bits on newer ZPL versions, and updates DNLC. `zfs_link_destroy()` removes a directory entry, rejects mounted/non-empty targets, decrements link counts, marks last-link targets as unlinked, updates parent metadata, removes DNLC entries, and either returns the unlinked status to the caller or inserts the target into the unlinked set.

`zfs_dropname()` removes a ZAP name using normalized removal when required by the dataset’s normalization/case mode. The embedded comment table documents the exact match-type matrix for case-sensitive, case-insensitive, and mixed-case filesystems with or without Unicode normalization.

Extended attributes are represented as hidden xattr directories. `zfs_make_xattrdir()` checks `ACE_WRITE_NAMED_ATTRS`, builds ACL/identity state, reserves creation and FUID transaction holds, creates the xattr directory with `zfs_mknode()`, stores its object ID in the base file SA xattr attribute, and logs `TX_MKXATTR`. `zfs_get_xattrdir()` locks the xattr slot, returns an existing xattr directory, optionally creates one, and enforces read-only filesystem behavior.

`zfs_dirempty()` is a hint-style check that a directory has only `.` and `..` and no in-progress dirlocks. `zfs_sticky_remove_access()` enforces sticky-directory restrictions: removal is allowed for directory owner, file owner, writable regular file, or privileged caller.

Important invariants: dirlocks protect ZAP names rather than whole directories; shared dirlocks copy the name on second shared use to avoid dangling caller storage; unlinked entries are intentionally retried after remount if deletion runs out of space or is interrupted; directory size is maintained as entry count; directory link count tracks subdirectory `..` references.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/zfs_dir.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/zfs_fm.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/zfs_fm.c

Implements ZFS Fault Management Architecture event generation for pool, vdev, block, data, device, delay, and checksum errors, plus resource events such as removal, autoreplace, and state changes. Kernel-only sections build and post FMA nvlists; non-kernel builds retain validity wrappers and shared interfaces.

`zfs_ereport_start()` constructs the common ereport and detector payload. It validates whether the event should be emitted, serializes ENA generation under `spa_errlist_lock`, chooses a pool-wide ENA during load or a logical-ZIO ENA for related I/O failures, sets the FMA class, detector FMRI, pool metadata, failmode, vdev metadata, parent vdev metadata, ZIO error/offset/size, previous vdev state, and logical bookmark fields.

`zfs_ereport_is_valid()` suppresses misleading or redundant events: try-import and recovery loads, repeated failed opens, non-read/write ZIO failures, inaccessible vdevs already failing due to probes/removal, checksum reads from missing DTL regions, probe failures after removal, and bogus delay events from unqueued I/O.

Checksum reporting has a staged path. `zfs_ereport_start_checksum()` captures vdev-specific checksum report context and links a report onto the logical ZIO. `zfs_ereport_finish_checksum()` annotates and posts the saved report when good/bad data are available. `zfs_ereport_post_checksum()` is the immediate one-shot version. `zfs_ereport_send_interim_checksum()` posts a partial report, and `zfs_ereport_free_checksum()` frees report state.

`annotate_ecksum()` compares good and bad ABD buffers to enrich checksum ereports. It records expected/actual checksums and algorithm when supplied, tracks byte ranges that differ, compresses many ranges by increasing the minimum gap via `shrink_ranges()`, stores inline set/cleared bit arrays for small corruptions, or stores per-bit histograms for larger corruptions. It can drop an event when good and bad buffers are identical and the caller requested that behavior.

`zfs_ereport_post()` posts ordinary ereports and frees the associated nvlists. `zfs_post_common()` and wrappers `zfs_post_remove()`, `zfs_post_autoreplace()`, and `zfs_post_state_change()` emit resource events used by diagnosis/retire agents to interpret vdev removal, autoreplace behavior, and state recovery.

The file’s core design goal is correlation: events for one logical I/O share an ENA even if failures happen through mirrors, RAID-Z, gang blocks, retries, or delegated I/O, while purely physical/cache/aggregation noise is suppressed or isolated.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/zfs_fm.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/zfs_fuid.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/zfs_fuid.c

Implements ZFS FUID support: compact persistent encoding of POSIX IDs and SID-like domain/rid identities used for owners, groups, and ACL ACEs. It maintains per-filesystem domain tables, maps between FUIDs and illumos uid/gid values, records new FUID domains for logging, and supports replay.

On disk, the FUID table is a packed XDR nvlist containing an array of domain records with index, domain string, and offset. `zfs_fuid_table_load()` reads the table object, unpacks the nvlist, and builds two AVL trees keyed by index and domain. `zfs_fuid_sync()` serializes the current AVL contents back to a DMU object, creating `ZFS_FUID_TABLES` in the master node if needed, and stores the packed size in the object bonus buffer.

`zfs_fuid_avl_tree_create()`, `zfs_fuid_table_destroy()`, `zfs_fuid_idx_domain()`, `zfs_fuid_find_by_domain()`, and `zfs_fuid_find_by_idx()` manage the in-memory domain table. New domains are assigned monotonically increasing indexes and set `zfsvfs->z_fuid_dirty`, making callers responsible for reserving transaction space and syncing.

Mapping functions include `zfs_fuid_map_id()` and `zfs_fuid_map_ids()`, which convert FUIDs to uid/gid values through `kidmap` when the FUID index is nonzero. `zfs_fuid_create_cred()` creates owner/group FUIDs from credentials, preferring credential SIDs for ephemeral IDs and falling back to plain POSIX IDs or nobody when necessary. `zfs_fuid_create()` creates FUIDs for explicit chown/chgrp or ACL ACE IDs, querying idmap for domain/rid outside replay and consuming logged replay FUID state during replay.

`zfs_fuid_node_add()` builds a `zfs_fuid_info_t` side structure recording domains and FUIDs created during an operation. That structure is used by ZIL logging and replay to preserve the exact domain/rid mapping for owners, groups, and ACL ACEs. `zfs_fuid_info_alloc()` and `zfs_fuid_info_free()` manage its lists and optional replay domain table.

Credential membership helpers are optimized for hot ACL access checks. `zfs_fuid_is_cruser()` compares a FUID to the credential user, avoiding idmap calls when the credential already has a matching KSID. `zfs_user_in_cred()` checks the credential user and SID list for ACE user IDs. `zfs_groupmember()` checks primary group KSID, SID list, process groups, and finally POSIX group membership after FUID-to-gid mapping.

`zfs_fuid_txhold()` reserves the correct DMU transaction holds for syncing a dirty FUID table, handling both new-table creation and updates to an existing table object.

Key invariants: FUID index zero means a plain POSIX ID; empty domain maps to index zero/nobody-style fallback; domain AVL nodes are never removed while the filesystem is active; replay does not call idmap but consumes logged FUID information; callers that dirty domains must include FUID transaction holds and call `zfs_fuid_sync()`.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/zfs_fuid.c -->