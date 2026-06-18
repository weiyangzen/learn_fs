# Group Research: group_1427_openzfs_sources_cow_pools_openzfs_module_os_linux_zfs_vdev_disk_c_s_8196c6e529e3

Scope checked against `Docs/research_subset_a.md`: all files are under `sources/cow-pools/openzfs`, which is included in subset A. Every listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/os/linux/zfs/vdev_disk.c -->
# File Research: sources/cow-pools/openzfs/module/os/linux/zfs/vdev_disk.c

## Purpose

Linux block-device implementation for the OpenZFS leaf disk vdev. It opens and closes Linux block devices, translates ZFS `zio_t` read/write/flush/TRIM requests into Linux BIO operations, reports capacity and ashift data, handles block-layer compatibility across kernel versions, and registers `vdev_disk_ops`.

## Main Structures And Tunables

- `zfs_bdev_handle_t` abstracts kernel-version differences between `struct bdev_handle`, `struct file`, and older raw `struct block_device *` handles.
- `vdev_disk_t` stores the current block-device handle plus `vd_lock`, a reader/writer lock protecting concurrent I/O versus close/reopen.
- `zfs_vdev_disk_max_segs` limits BIO segment count when nonzero, clamped against the device queue and a minimum of 4.
- `zfs_vdev_open_timeout_ms` controls retry time for transient udev path disappearance or zvol `ERESTARTSYS`.
- `zfs_vdev_failfast_mask` maps the vdev failfast property into Linux BIO failfast flags.

## Open/Close And Capacity

- `vdev_bdev_mode()` converts SPA read/write mode into Linux block open flags and always requests exclusive access.
- `bdev_capacity()` and `bdev_max_capacity()` calculate current usable bytes and potential expansion bytes. Whole-disk expansion accounts for EFI reserved space, `NEW_START_BLOCK`, and partition end alignment.
- `vdev_disk_open()` validates absolute `vdev_path`, handles reopen by dropping the old handle under writer lock, optionally rereads partition tables during expansion, retries opens for transient `ENOENT` and zvol `ERESTARTSYS`, then records block size, write-cache, TRIM, secure TRIM, rotational, capacity, and ashift properties.
- `vdev_disk_close()` skips close during `vdev_reopening`; otherwise it takes writer lock, releases the block device, clears `vdev_tsd`, destroys the lock, and frees `vdev_disk_t`.

## BIO Compatibility And Submission

The file contains compatibility code for Linux block API changes, including `bio_alloc()` signatures, `bio_set_dev()`, cgroup `blkg_tryget()`, and GPL-only symbol avoidance. `vdev_submit_bio()` temporarily clears `current->bio_list` around `submit_bio()` to avoid unwanted bio recursion/plugging effects.

`vdev_bio_max_segs()` combines device queue limits, kernel limits, and the tunable. `vdev_bio_max_bytes()` uses queue max sectors.

## Read/Write Data Path

- `vbio_t` is a ZFS-side wrapper for one ZIO translated into one or more chained BIOs.
- `vbio_alloc()` captures the parent ZIO, target block device, max segments/bytes, logical block-size mask, starting offset, current BIO, optional bounce ABD, and flags.
- `vbio_add_page()` allocates BIOs, sets sector/op/flags, adds page segments respecting logical-block-size alignment and max BIO byte constraints, chains and submits full BIOs, and advances offsets.
- `vbio_submit()` starts a block plug, iterates ABD pages via `abd_iterate_page_func()`, sets the final BIO completion callback/private pointer, submits the chain, and finishes the plug.
- `vbio_completion()` converts BIO status to `zio->io_error`, logs errors via `vdev_disk_error()`, releases the BIO, stashes `vbio` in `zio->io_bio`, and uses `zio_delay_interrupt()` so cleanup happens outside interrupt context.

Before submission, `vdev_disk_io_rw()` rejects accesses beyond `bdev_capacity()`, resolves inherited/default failfast policy, applies failfast flags unless retrying/tryhard, and checks whether the ABD page layout can be submitted directly. If the ABD has data that would force unsafe LBS/page-boundary splits, it allocates an aligned ABD bounce buffer, copies write data into it, verifies alignment, and saves it on the `vbio`.

`vdev_disk_io_done()` frees the `vbio`, copies read data back from a bounce ABD if needed, frees the bounce ABD, and on `EIO` revalidates disk status. Failed media checks invalidate the block device, mark removal wanted, and request `SPA_ASYNC_REMOVE`.

## Flush And TRIM

- `vdev_disk_io_flush()` allocates an empty BIO, installs `vdev_disk_io_flush_completion()`, sets flush operation attributes, submits, and invalidates the block device cache.
- Flush start logic respects `vdev_readable()`, `zfs_nocacheflush`, and `vdev_nowritecache`, returning `ENXIO`, success, or `ENOTSUP` without issuing a BIO when appropriate.
- `vdev_bdev_issue_secure_erase()` and `vdev_bdev_issue_discard()` wrap kernel-version-specific secure discard and discard APIs.
- `vdev_disk_io_trim()` chooses secure erase versus discard, maps ZIO offset/size to sectors, handles sync success by interrupting the ZIO immediately, or installs `vdev_disk_discard_end_io()` for async completion.

## Vdev Ops And Parameters

`vdev_disk_io_start()` dispatches ZIO types under `vd_lock`: flush, TRIM, read/write, and a defensive `ENOTSUP` default. `vdev_disk_ops` wires disk vdev behavior into the core vdev layer, including open, close, I/O start/done, hold/release stubs, default sizing/xlate helpers, and `vdev_disk_kobj_evt_post()`.

The file also defines setters for min/max auto ashift that validate against `ASHIFT_MIN`, `ASHIFT_MAX`, and the counterpart tunable before delegating to `param_set_uint()`.

## Notable Edges

- Uses retry windows to mask transient udev path churn.
- Uses writer/read locks to prevent I/O against a closing or failed reopen device handle.
- Uses bounce ABDs only when Linux page/LBS splitting constraints require them.
- Errors in completion paths are logged with pool/vdev/type/offset/size context via `printk()`, because some completions may run in interrupt context.

<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/os/linux/zfs/vdev_disk.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/os/linux/zfs/vdev_label_os.c -->
# File Research: sources/cow-pools/openzfs/module/os/linux/zfs/vdev_label_os.c

## Purpose

Linux OS hook for checking whether the reserved boot area on a vdev is in use.

## Behavior

`vdev_check_boot_reserve(spa_t *spa, vdev_t *childvd)` ignores both arguments and returns `0`. The comment explains that Linux has no known external consumers of the reserved boot area, so the check always reports no conflict.

## Integration

This is a tiny platform-specific implementation used by common vdev label code. Other platforms may perform real boot-reserve checks; Linux intentionally does not.

<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/os/linux/zfs/vdev_label_os.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/os/linux/zfs/vdev_raidz.c -->
# File Research: sources/cow-pools/openzfs/module/os/linux/zfs/vdev_raidz.c

## Purpose

Linux kernel-parameter glue for selecting/reporting the active RAIDZ implementation.

## Behavior

- `param_get_raidz_impl()` writes the current RAIDZ implementation name/details into the supplied buffer by calling `vdev_raidz_impl_get(buf, PAGE_SIZE)`.
- `param_set_raidz_impl()` passes the requested value to `vdev_raidz_impl_set()` and returns its error code.

## Integration

The actual RAIDZ implementation selection logic is elsewhere. This file only adapts it to the Linux `zfs_kernel_param_t` get/set interface.

<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/os/linux/zfs/vdev_raidz.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/os/linux/zfs/zfs_acl.c -->
# File Research: sources/cow-pools/openzfs/module/os/linux/zfs/zfs_acl.c

## Purpose

Core Linux ZFS ACL implementation. It handles ZFS/NFSv4 ACL storage formats, old-to-new ACL conversion, FUID mapping, ACL inheritance and chmod behavior, POSIX-mode derivation, ACL get/set operations, and permission checks for access, delete, and rename.

## ACL Formats And Operations

The file defines two `acl_ops_t` implementations:

- `zfs_acl_v0_ops` for old fixed `zfs_oldace_t` entries.
- `zfs_acl_fuid_ops` for newer FUID-aware ACEs, including compact owner/group/everyone ACEs and larger object ACEs.

The ops table abstracts get/set of type, flags, mask, who, entry size, abstract size, mask offset, and optional object ACE data. This allows generic ACL walking and transformation code to work over both on-disk formats.

`zfs_external_acl()`, `zfs_acl_znode_info()`, and `zfs_znode_acl_version()` handle legacy external ACL objects and races with SA upgrades. `zfs_acl_version()` maps ZPL version to initial versus FUID ACL format.

## Allocation, Walking, And Conversion

- `zfs_acl_alloc()`, `zfs_acl_node_alloc()`, `zfs_acl_node_free()`, `zfs_acl_release_nodes()`, and `zfs_acl_free()` manage ACL containers and list nodes.
- `zfs_acl_valid_ace_type()` and `zfs_ace_valid()` validate ACE type, owner/group/everyone flags, object ACE eligibility, and inheritance flag combinations while updating ACL hints.
- `zfs_acl_next_ace()` walks ACL nodes safely, validating per-entry bounds using the active ops table.
- `zfs_copy_ace_2_fuid()` converts user ACE buffers to ZFS FUID ACL entries and creates FUIDs for named users/groups.
- `zfs_copy_fuid_2_ace()` maps ZFS FUID ACLs back to exported `ace_t`/`ace_object_t` buffers.
- `zfs_copy_ace_2_oldace()` converts user ACE buffers to legacy format.
- `zfs_acl_xform()` transforms an old ACL into FUID format, allocating a new node, converting entries, replacing old nodes, and updating version/count/byte totals.

## Mode And Trivial ACL Logic

`zfs_unix_to_v4()` and `zfs_v4_to_unix()` translate between Unix mode bits and NFSv4-style ACE masks. `zfs_mode_compute()` derives inode mode bits from ACL entries and updates `ZFS_NO_EXECS_DENIED` depending on whether execute was denied or absent.

`acl_trivial_access_masks()` builds canonical owner/group/everyone masks for a Unix mode. `ace_trivial_common()` detects ACLs that are representable as trivial mode-derived ACLs by rejecting named users/groups, inheritance flags, read-attribute denies, delete permission, malformed delete-child grants, and non-owner administrative allows.

## ACL Storage Updates

`zfs_acl_node_read()` reads a znode ACL under `z_acl_lock`, using cached ACLs when possible unless modification is requested. It reads SA-stored ACLs directly or legacy ACL data from embedded `z_ace_data` / external DMU objects. Checksum errors are translated to `EIO`.

`zfs_aclset_common()` is the shared writer used by chmod, creation, and explicit setacl paths. It recomputes mode/pflags, clears cached ACLs, upgrades old ACLs when needed, writes SA ACL attributes or legacy embedded/external ACL objects, updates ACL-wide pflags and trivial hints, updates ctime, and commits via `sa_bulk_update()`.

`zfs_acl_chmod()` rewrites ACLs to match a new mode while respecting `aclmode`: it may split inheritable owner/group/everyone ACEs into inherit-only entries, trim allows to group permissions, preserve audit/object/inherit-only entries, add canonical mode ACEs, and rebuild count/byte totals.

`zfs_acl_chmod_setattr()` obtains or creates the ACL for chmod according to `z_acl_mode`, applies `zfs_acl_chmod()`, and returns the modified ACL to the caller.

## Inheritance And Creation

`zfs_ace_can_use()` decides whether an ACE should inherit to the new object. `zfs_acl_inherit()` builds a child ACL according to `aclinherit`, object type, requested mode, and parent ACE flags. It handles `discard`, symlink exclusion, `noallow`, `passthrough`, `passthrough-x`, `restricted`, no-propagate, inherit-only conversion, and hint updates.

`zfs_acl_ids_create()` builds initial ACL IDs for new znodes. It converts explicit ACLs when provided, creates owner/group FUIDs, applies setgid inheritance and setgid clearing policy, inherits parent ACLs when appropriate, falls back to trivial ACLs, applies chmod-style mode ACLs when needed, computes resulting mode, and marks trivial ACLs. `zfs_acl_ids_free()` releases ACL/FUID data, and `zfs_acl_ids_overquota()` checks user/group/project quota before create.

## Get/Set ACL Interfaces

- `zfs_getacl()` checks `ACE_READ_ACL`, reads/caches the ACL, counts or filters object ACEs depending on `VSA_ACE_ALLTYPES`, allocates the output ACE buffer, converts entries to user-visible layout, and returns ACL flags.
- `zfs_vsec_2_aclp()` validates user ACL count, allocates a ZFS ACL, converts old/FUID entries, installs ACL-wide flags, and returns the internal ACL.
- `zfs_setacl()` checks immutable state and `ACE_WRITE_ACL`, converts the user ACL, preserves existing wide flags when not explicitly provided, creates a DMU transaction with holds for SA/FUID/external ACL changes, retries on `ERESTART`, writes via `zfs_aclset_common()`, caches the new ACL, syncs FUIDs, logs the ACL change, and commits.

## Access Checks

`zfs_zaccess_dataset_check()` rejects writes on readonly datasets, writes to immutable files, delete/unlink on nounlink files, and read/execute on quarantined files.

`zfs_zaccess_aces_check()` is the main non-trivial ACL evaluator. It walks ACEs in order, skips inherit-only directory ACEs, matches owner/group/everyone/named-user entries against credentials and idmaps, removes covered bits from the working mask, accumulates deny bits, supports "any access" short-circuit mode, and returns `EACCES`, `0`, or `-1` for unresolved requested bits.

`zfs_zaccess_trivial()` delegates mode-like checks to Linux `generic_permission()` for trivial ACLs while rejecting unmappable special permissions such as write-owner/write-ACL/delete.

`zfs_zaccess_common()` combines empty/replay short-circuits, dataset checks, skip-ACL handling, DOS readonly handling, trivial ACL path, and ACE evaluator path.

`zfs_zaccess()` is the public fine-grained permission check. It remaps xattr directory access to base-file named-attribute permissions, maps requested ACE bits to Unix mode bits for privilege checks, invokes ACL checks, handles append fallback, and consults Linux/SPL secpolicy helpers for owner, DAC, chown, remove, and residual special bits.

`zfs_fastaccesschk_execute()` provides a fast execute check for common non-xattr cases using mode bits and `ZFS_NO_EXECS_DENIED`, falling back to full `zfs_zaccess()`.

`zfs_has_access()`, `zfs_zaccess_rwx()`, and `zfs_zaccess_unix()` are wrappers for "any access" and Unix mode-derived requests.

## Delete And Rename

`zfs_zaccess_delete()` implements Windows-like delete semantics: target `ACE_DELETE` is checked first, target denies win, otherwise parent `ACE_DELETE_CHILD` or optionally `ACE_WRITE_DATA` can grant deletion, privilege fallbacks are attempted, and sticky-bit restrictions are enforced via `zfs_sticky_remove_access()`.

`zfs_zaccess_rename()` requires delete permission on the source, delete permission on an overwritten target if any, and add-file/add-subdirectory permission on the target directory. It also rejects quarantined source znodes.

<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/os/linux/zfs/zfs_acl.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/os/linux/zfs/zfs_ctldir.c -->
# File Research: sources/cow-pools/openzfs/module/os/linux/zfs/zfs_ctldir.c

## Purpose

Linux implementation of the virtual ZFS control directory, `.zfs`. It dynamically exposes `.zfs/snapshot` and `.zfs/shares`, automounts snapshots on lookup, supports optional snapshot create/remove/rename from the snapdir, handles NFS file handles for control nodes, and tracks automounted snapshots for delayed expiration.

## Snapshot Tracking

The file maintains two AVL trees:

- `zfs_snapshots_by_name`, keyed by full dataset snapshot name.
- `zfs_snapshots_by_objsetid`, keyed by `(spa, objsetid)`.

`zfs_snapentry_t` records snapshot name, mount path, spa, objset id, root dentry, delayed unmount task id, AVL nodes, refcount, mount-progress condition state, and last mount error.

Key helpers allocate/free entries, hold/release refcounts, add/remove entries to AVL trees, fill pending entries after a successful mount, find by name or objset id, and rename entries after snapshot rename. Pending entries have `se_spa == NULL` while a mount is in progress and are present only in the name tree until filled.

## Expiration And Unmount

`snapentry_expire()` is a delayed task that attempts an expire unmount, clears the task id, releases the dispatch hold, and reschedules expiration if the snapshot remained mounted. `zfsctl_snapshot_unmount_cancel()` cancels delayed unmounts and drops the held reference if cancellation wins. `zfsctl_snapshot_unmount_delay()` finds an active snapshot by objset id, cancels any previous deadline, and schedules a new one.

`zfsctl_snapshot_unmount()` waits for in-progress automounts, calls `/usr/bin/env umount -t zfs -n` with optional force, retries after `exportfs -f` on failure to clear NFS export references, maps helper failure to `EBUSY`, and releases the snapentry.

## Control Inodes

`zfsctl_inode_alloc()` creates synthetic control-directory znodes/inodes with root ownership, directory mode, control flags, no SA handle, selected inode/file ops, stable timestamps, and insertion into `z_all_znodes`. `zfsctl_inode_lookup()` first tries `ilookup()`, optionally discovers snapshot creation time from dataset metadata, and allocates on demand.

`zfsctl_create()` creates and caches the `.zfs` root inode in `zfsvfs->z_ctldir`. `zfsctl_destroy()` either removes a snapshot's snapentry on snapshot unmount or releases the cached `.zfs` root inode on filesystem unmount.

`zfsctl_root()` returns a held reference to the cached `.zfs` inode. `zfsctl_is_node()` and `zfsctl_is_snapdir()` classify synthetic control nodes.

## FID And NFS Handling

`zfsctl_fid()` generates short FIDs for `.zfs` nodes and delegates snapshot directories to `zfsctl_snapdir_fid()`. Snapshot dir FIDs are long and encode objset id plus a generation bit indicating whether the snapdir was mounted. This lets NFS `fh_to_dentry` force automount/revalidation behavior when needed.

`zfsctl_snapdir_vget()` reconstructs a snapdir inode from objset id and generation. It tries the AVL cache first, falls back to scanning snapshots for a path, triggers automount with `kern_path(... LOOKUP_FOLLOW|LOOKUP_DIRECTORY ...)`, looks up the snapdir inode, and validates the encoded mountpoint generation.

## Lookup And Snapdir Operations

`zfsctl_root_lookup()` handles lookups below `.zfs`: `..` returns the filesystem root, `snapshot` returns the snapdir inode, `shares` returns the shares inode, and disabled snapdir returns `ENOENT`.

`zfsctl_snapdir_lookup()` looks up a snapshot name in the DMU snapshot list and returns a synthetic snapdir inode keyed as `ZFSCTL_INO_SNAPDIRS - objsetid`.

When `zfs_admin_snapshot` is enabled:

- `zfsctl_snapdir_mkdir()` validates a snapshot component name, checks snapshot permission, creates a single snapshot via `dmu_objset_snapshot_one()`, then looks it up.
- `zfsctl_snapdir_remove()` resolves real case-insensitive names when needed, checks destroy permission, forcibly unmounts any active snapshot mount, then destroys the snapshot.
- `zfsctl_snapdir_rename()` validates admin mode, resolves source case when needed, builds old/new full names, checks rename policy, rejects moving across directories, renames the snapshot through DSL, and updates the snapentry name tree.

`zfsctl_shares_lookup()` delegates names below `.zfs/shares` to the configured on-disk shares directory when present.

## Automount Path

`zfsctl_snapshot_mount()` is the automount trigger. It builds full snapshot dataset name and mount path, updates the cached mountpoint when not chrooted, releases `z_teardown_lock` before blocking usermode-helper operations to avoid a documented namespace/mountinfo deadlock, coordinates concurrent mounts with a pending snapentry and condition variable, calls `/usr/bin/env mount -i -t zfs -n -o suid|nosuid`, handles busy and failure cases, follows into the mounted snapshot, marks it shrinkable, fills the snapentry with spa/objset/root dentry, schedules delayed unmount, wakes waiters, and frees local buffers.

## Initialization And Tunables

`zfsctl_init()` creates AVL trees and initializes `zfs_snapshot_lock`; `zfsctl_fini()` destroys them. Module parameters expose:

- `zfs_admin_snapshot`: allow mkdir/rmdir/mv in `.zfs/snapshot`.
- `zfs_expire_snapshot`: seconds before automatic snapshot expiration.
- `zfs_snapshot_no_setuid`: mount automounted snapshots with `nosuid`.

<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/os/linux/zfs/zfs_ctldir.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/os/linux/zfs/zfs_debug.c -->
# File Research: sources/cow-pools/openzfs/module/os/linux/zfs/zfs_debug.c

## Purpose

Implements the in-kernel ZFS debug message buffer exposed through procfs/kstat and DTrace-style tracepoints.

## Data Model

`zfs_dbgmsg_t` is a variable-sized list node containing timestamp, allocation size, and message bytes. A global `procfs_list_t zfs_dbgmsgs` holds entries, with `zfs_dbgmsg_size` tracking total bytes and `zfs_dbgmsg_maxsize` defaulting to 4 MiB.

`zfs_dbgmsg_enable` controls whether callers should emit internal debug messages; the file registers it as a module parameter.

## Procfs Lifecycle

`zfs_dbgmsg_init()` installs `/proc/spl/kstat/zfs/dbgmsg` with show/header/clear callbacks. `zfs_dbgmsg_fini()` uninstalls it, purges all messages, and destroys the list. `zfs_dbgmsg_clear()` purges under the list lock.

`zfs_dbgmsg_show_header()` and `zfs_dbgmsg_show()` render `timestamp` and message columns through `seq_file`.

## Message Emission

`__set_error()` conditionally emits error diagnostics when `ZFS_DEBUG_SET_ERROR` is enabled in `zfs_flags`.

`__dprintf()` builds a bounded 1024-byte message containing current thread pointer, optional `dprintf:` prefix, basename, line, function, and formatted payload. It trims trailing newline for dprintf logs, fires `DTRACE_PROBE1(zfs__dprintf, ...)`, stores the message with `__zfs_dbgmsg()`, and frees the temporary buffer.

`__zfs_dbgmsg()` allocates a variable-sized message, timestamps it with `gethrestime_sec()`, adds it to the procfs list, updates total size, and purges oldest messages until under `zfs_dbgmsg_maxsize`.

<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/os/linux/zfs/zfs_debug.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/os/linux/zfs/zfs_dir.c -->
# File Research: sources/cow-pools/openzfs/module/os/linux/zfs/zfs_dir.c

## Purpose

Directory-entry, lookup, unlink-drain, link-count, xattr-directory, and sticky-directory helper implementation for Linux ZFS. It bridges ZFS ZAP directories, znodes, SA updates, normalization/case-folding semantics, unlinked-set recovery, and Linux permission helpers.

## Dirent Lookup And Locking

`zfs_match_find()` performs ZAP lookup for a name. It uses `zap_lookup_norm()` when normalization is active, optionally returns the real matched name and case-conflict flags, tolerates `EOVERFLOW` for entries where the first integer remains the object id, and strips dirent type bits with `ZFS_DIRENT_OBJ()`.

`zfs_dirent_lock()` serializes access to a directory name using per-directory `z_dirlocks` under `z_lock`, plus `z_name_lock` unless `ZHAVELOCK` is supplied. It rejects `.`, `..`, and `.zfs`, determines normalized/case-sensitive match type, decides when DNLC-style updates are safe, chooses wide versus narrow locks for case-folding/rename situations, supports shared locks, checks unlinked directories, performs lookup or xattr lookup, enforces `ZNEW`/`ZEXISTS`, and returns a held target znode if found.

`zfs_dirent_unlock()` releases the name lock if owned, decrements shared count or removes the dirlock from the list, wakes waiters, frees copied names, destroys the condition variable, and frees the dirlock.

## Directory Lookup

`zfs_dirlook()` handles special names:

- Empty string or `.` returns the directory itself.
- `..` returns parent, with a special path for snapshots mounted under `.zfs`.
- `.zfs` returns the control directory unless snapdir is disabled.
- Other names use `zfs_dirent_lock()` with `ZEXISTS | ZSHARED` and optional case-insensitive lookup.

It enables prefetching on successful ordinary lookup and fills the real pathname buffer for ignore-case special cases.

## Unlinked Set And Removal

`zfs_unlinked_add()` inserts an unlinked znode id into the filesystem unlinked object and updates kstats.

`zfs_unlinked_drain_task()` iterates the unlinked set after crash/force-unmount recovery, checks object type, gets each znode, marks it unlinked, and releases it so inactive cleanup can free it. `zfs_unlinked_drain()` dispatches this asynchronously on the pool unlinked-drain taskq or falls back to synchronous execution. `zfs_unlinked_drain_stop_wait()` cancels/waits for the drain task during unmount.

`zfs_purgedir()` deletes all regular-file/symlink entries in an inactive xattr directory using synthetic dirlocks and transactions, returning a skipped count so the parent can remain in the unlinked set if cleanup failed.

`zfs_rmnode()` is final znode deletion for link-count-zero inactive znodes. It purges xattr directory contents, frees regular file data, finds and unlinks xattr directories, frees external ACL objects, removes the znode from the unlinked set, broadcasts when the unlinked set becomes empty, updates kstats, calls `zfs_znode_delete()`, and commits. If space/transaction/freeing problems occur, it leaves the object in the unlinked set for later drain.

## Link Create/Destroy

`zfs_dirent()` packs object id with file type bits when supported by the ZPL version.

`zfs_link_create()` links a znode into a directory ZAP entry. It rejects new links to unlinked znodes, increments link count for non-new/non-rename links, writes the ZAP entry, activates the longname feature for long names, updates parent/flags/ctime on the child, increments directory size and parent link count for subdirectories, updates parent timestamps/pflags/link count, and persists all via SA bulk updates.

`zfs_dropname()` removes a directory ZAP entry, using normalized removal when needed and choosing match-case rules according to filesystem case mode and lookup flags.

`zfs_drop_nlink_locked()` validates directory emptiness, recovers impossible link counts, drops one link, marks the znode unlinked and clears nlink when it reaches the directory terminal count, updates links/ctime/flags, and optionally adds it to the unlinked set.

`zfs_drop_nlink()` wraps the locked helper. `zfs_link_destroy()` removes the name from the parent, drops the target link unless this is a rename-only removal, updates parent size/link count/timestamps, and either reports or enqueues final unlink state.

`zfs_dirempty()` checks that no dirlocks are active and the ZAP count is zero. It is exact only when the caller holds the right locks; otherwise it is a hint.

## Extended Attribute Directories

`zfs_make_xattrdir()` creates an xattr directory znode with ACL IDs, quota checks, SA/ZAP/FUID transaction holds, parent pointer verification in debug builds, parent `SA_ZPL_XATTR` update, optional intent log entry, and returns the held xattr znode.

`zfs_get_xattrdir()` locks the xattr pseudo-entry, returns an existing xattr directory if present, optionally creates it when `CREATE_XATTR_DIR` is set, rejects creation on readonly datasets, sets sticky world-writable directory attributes, maps ids, handles `ERESTART`, and returns `ENOENT` when not creating.

## Sticky Directory Removal

`zfs_sticky_remove_access()` enforces sticky-bit removal restrictions: replay bypasses checks, non-sticky directories allow removal, otherwise the caller must own the directory, own the target, have write access to the target, or pass `secpolicy_vnode_remove()`.

<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/os/linux/zfs/zfs_dir.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/os/linux/zfs/zfs_file_os.c -->
# File Research: sources/cow-pools/openzfs/module/os/linux/zfs/zfs_file_os.c

## Purpose

Linux kernel implementation of the portable `zfs_file_*` abstraction used by OpenZFS code that needs file operations from kernel context.

## File Lifecycle And References

- `zfs_file_open()` maps ZFS open requests to `filp_open()`. For non-create write-only opens it adds `O_EXCL`; for create it temporarily clears current umask so the requested mode is honored.
- `zfs_file_close()` calls `filp_close()`.
- `zfs_file_get()` obtains a `struct file *` from a file descriptor using `fget()`.
- `zfs_file_put()` releases it using `fput()`.
- `zfs_file_private()` returns `fp->private_data`.

## I/O Helpers

- `zfs_file_write()` and `zfs_file_read()` are stateful operations using and updating `fp->f_pos`.
- `zfs_file_pwrite()` and `zfs_file_pread()` perform positioned I/O without changing `fp->f_pos`.
- All read/write helpers return positive errno values, optionally report residual bytes, and treat short I/O without a residual pointer as `EIO`.
- `zfs_file_seek()` wraps `vfs_llseek()`, rejecting negative input offsets and returning `ESPIPE`-style errors from the kernel as positive errno.

## Attributes, Sync, And Allocation

- `zfs_file_getattr()` calls `vfs_getattr()` and returns size and mode in `zfs_file_attr_t`.
- `zfs_file_fsync()` maps `O_DSYNC` into the datasync flag for `vfs_fsync()`.
- `zfs_file_deallocate()` uses the file operation `fallocate()` with `FALLOC_FL_PUNCH_HOLE | FALLOC_FL_KEEP_SIZE` when available; otherwise it returns `EOPNOTSUPP`.
- `zfs_file_off()` returns the current file offset.
- `zfs_file_unlink()` is optional and intentionally unsupported on Linux, returning `EOPNOTSUPP`.

<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/os/linux/zfs/zfs_file_os.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/os/linux/zfs/zfs_ioctl_os.c -->
# File Research: sources/cow-pools/openzfs/module/os/linux/zfs/zfs_ioctl_os.c

## Purpose

Linux OS layer for the ZFS ioctl device and module initialization/teardown. It connects the common ZFS ioctl implementation to `/dev/zfs`, registers Linux-specific ioctls, initializes sysfs, and provides the kernel module entry points.

## VFS And Device State Helpers

- `zfs_vfs_held()` checks whether a `zfsvfs_t` has an attached superblock.
- `zfs_vfs_ref()` safely increments `s_active` with `atomic_inc_not_zero()` and returns `ESRCH` if the filesystem is gone.
- `zfs_vfs_rele()` releases the superblock with `deactivate_super()`.
- `zfsdev_private_set_state()` and `zfsdev_private_get_state()` store/retrieve `zfsdev_state_t` through `struct file.private_data`.

## /dev/zfs Operations

`zfsdev_open()` initializes per-open ZFS device state under `zfsdev_state_lock`. `zfsdev_release()` destroys that state.

`zfsdev_ioctl()` maps ioctl command to a vector number, allocates a `zfs_cmd_t`, copies it from userspace, calls `zfsdev_ioctl_common()`, copies results back, frees the command, and returns Linux negative errno values. `zfsdev_compat_ioctl()` delegates to the same function when compat ioctls are enabled.

`zfsdev_fops` wires open, release, unlocked ioctl, compat ioctl, and owner. `zfsdev_attach()` registers a misc device using static `ZFS_DEVICE_MINOR`, falling back to `MISC_DYNAMIC_MINOR` on `EBUSY`. `zfsdev_detach()` deregisters it.

## Linux-Specific Ioctls And Limits

`zfs_ioc_userns_attach()` and `zfs_ioc_userns_detach()` attach/detach datasets to Linux user namespaces through zone helpers, translating SPL `ENOTTY`/`ENXIO` into ZFS-specific user-namespace errors. `zfs_ioctl_init_os()` registers both dataset no-log ioctls with config security policy and no pool check.

`zfs_max_nvlist_src_size_os()` returns the configured max nvlist source size if set, otherwise the smaller of one quarter of RAM and 128 MiB. `zfs_ioctl_update_mount_cache()` is a no-op on Linux.

## Module Initialization

`openzfs_init_os()` calls `zfs_kmod_init()`, initializes ZFS sysfs, logs module/pool/filesystem versions and selected warnings, and stores `zfs_init_idmap`.

`openzfs_fini_os()` finalizes sysfs and the common kernel module state, then logs unload.

`openzfs_init()` initializes `zcommon`, ICP, zstd, and OS ZFS state in order, unwinding on failure. `openzfs_fini()` tears them down in reverse. Module metadata declares aliases for component modules, description, author, multiple license annotations, and version.

<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/os/linux/zfs/zfs_ioctl_os.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/os/linux/zfs/zfs_racct.c -->
# File Research: sources/cow-pools/openzfs/module/os/linux/zfs/zfs_racct.c

## Purpose

Linux resource-accounting adapter for ZFS read/write I/O accounting.

## Kernel Behavior

When `_KERNEL` is defined:

- `zfs_racct_read()` calls `task_io_account_read(size)` and updates SPA read I/O stats with `spa_iostats_read_add(spa, size, iops, flags)`.
- `zfs_racct_write()` calls `task_io_account_write(size)` and updates SPA write I/O stats with `spa_iostats_write_add(spa, size, iops, flags)`.

## Non-Kernel Behavior

Outside kernel builds, both functions are no-ops that explicitly consume their arguments.

<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/os/linux/zfs/zfs_racct.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/os/linux/zfs/zfs_sysfs.c -->
# File Research: sources/cow-pools/openzfs/module/os/linux/zfs/zfs_sysfs.c

## Purpose

Builds the ZFS sysfs interface under `/sys/module/zfs` so userland can discover supported kernel features, pool features, dataset properties, vdev properties, and pool properties from the loaded module.

## Kobject Framework

`zfs_mod_kobj_t` wraps a Linux `kobject`, `kobj_type`, `sysfs_ops`, allocated attributes, default group, child object table, and child count.

Core helpers:

- `zfs_kobj_init()` allocates attribute tables/default groups/children, wires show and release ops, and supports both `default_groups` and older `default_attrs` kernels.
- `zfs_kobj_add_attr()` initializes one read-only attribute and places it in the default group.
- `zfs_kobj_add()` initializes and adds a kobject under a parent.
- `zfs_kobj_fini()` recursively finalizes children, deletes the kobject, and drops the reference.
- `zfs_kobj_release()` frees allocated attributes, default group arrays, children, and resets counts.

## Property Sysfs

The common property attributes are `type`, `readonly`, `setonce`, `visible`, `values`, `default`, and for dataset properties `datasets`.

`zprop_sysfs_show()` renders one property attribute: property type, booleans, values string, numeric/string/index default, or applicable dataset types. `dataset_property_show()`, `vdev_property_show()`, and `pool_property_show()` map kobject names to property descriptors and call the common renderer.

`zprop_to_kobj()` creates one child kobject per property and attaches the appropriate attributes. `zfs_sysfs_properties_init()` creates one top-level property directory for pool, vdev, or dataset properties and populates children using `zprop_iter_common()`.

## Feature Sysfs

Kernel features are hard-coded as:

- `com.delphix:vdev_initialize`
- `org.zfsonlinux:vdev_trim`
- `org.openzfs:l2arc_persistent`

Each has a `supported` attribute that returns `yes`.

Pool features use `spa_feature_table` and expose `description`, `guid`, `uname`, `readonly_compatible`, `required_for_mos`, `activate_on_enable`, and `per_dataset`. `pool_feature_show()` looks up features by GUID and renders strings or flag-derived booleans.

`zfs_kernel_features_init()` and `zfs_pool_features_init()` create top-level feature directories and child kobjects.

## Initialization And Cleanup

`zfs_sysfs_init()` chooses the parent kobject depending on built-in versus module build, then initializes kernel features, pool features, pool properties, vdev properties, and dataset properties. On failure it finalizes previously created top-level kobjects.

`zfs_sysfs_fini()` finalizes all top-level kobjects and their children.

<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/os/linux/zfs/zfs_sysfs.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/os/linux/zfs/zfs_uio.c -->
# File Research: sources/cow-pools/openzfs/module/os/linux/zfs/zfs_uio.c

## Purpose

Linux kernel implementation of OpenZFS `zfs_uio_t` data movement helpers. It copies data between ZFS buffers and kernel iovecs, bio vectors, block requests, or Linux `iov_iter`s, supports prefaulting, supports non-consuming copies/skips/alignment checks, and manages direct-I/O page pinning.

## Copy Paths

- `zfs_uiomove_iov()` handles `UIO_SYSSPACE` iovecs using `memcpy()`, updating skip, iov pointer/count, resid, and logical offset.
- `zfs_uiomove_bvec_impl()` handles `UIO_BVEC` arrays by mapping each page with `zfs_kmap_local()`, copying into or out of the page window, unmapping, and updating progress.
- `zfs_copy_bvec()` is the single-bio-vec copy helper.
- `zfs_uiomove_bvec_rq()` handles `struct request`-backed UIOs by iterating request segments, finding segments intersecting `uio_loffset`, copying only needed ranges, updating resid/loffset, and setting resid to zero when no segment matched.
- `zfs_uiomove_bvec()` chooses request-backed or plain bvec copying.
- `zfs_uiomove_iter()` uses `copy_to_iter()` / `copy_from_iter()`, returns `EFAULT` on zero-byte pipe progress, optionally reverts the iterator for copy-only mode, and treats partial move copies as `EFAULT`.
- `zfs_uiomove()` dispatches by `uio_segflg` and is exported.

## Prefault, Copy, Skip, Alignment

`zfs_uio_prefaultpages()` does nothing for kernel-space, bvec, or direct-I/O pages, but uses `iov_iter_fault_in_readable()` for user iterators.

`zfs_uiocopy()` copies without consuming the original UIO by cloning the struct and, for iterators, reverting consumed bytes. It returns copied byte count.

`zfs_uioskip()` advances over `n` bytes in bvec, iterator, or sysspace iovec forms, updating skip/pointer/count/offset/resid.

`zfs_uio_page_aligned()` verifies page-aligned base and length for sysspace iovecs, uses `iov_iter_alignment()` for iterators, and currently returns false for other segment types.

## Direct I/O Page Handling

For kernels where `ZERO_PAGE()` is unavailable or unsuitable, marker macros collapse to no-ops. Otherwise ZFS marks replacement pages with a private value (`ZFSPAGE`) so it can later identify and free them.

`zfs_uio_dio_check_for_zero_page()` scans direct-I/O pages for the kernel zero page on writes. When found, it drops the zero page and allocates a private zero-filled page so user mappings cannot change data while a direct-I/O write is in flight.

`zfs_uio_free_dio_pages()` releases direct-I/O pages. It unpins pages when GUP pinning was used, otherwise it unmarks/frees ZFS replacement pages or `put_page()`s normal pages, then frees the page pointer array.

When `pin_user_pages_unlocked()` is available, `zfs_uio_pin_user_pages()` pins user-backed iterator pages for direct I/O, handling `ITER_UBUF` separately when supported and otherwise walking iovecs. It uses `FOLL_WRITE` for reads into userspace and reports partial pinning as `EFAULT`.

`zfs_uio_get_dio_pages_iov_iter()` uses `iov_iter_get_pages2()` or `iov_iter_get_pages()` to collect pages, manually advancing/reverting when required, asserting page alignment, and leaving the original iterator unchanged.

`zfs_uio_get_dio_pages_alloc()` allocates the direct-I/O page vector, chooses pinning or iterator page extraction for `UIO_ITER`, cleans up on errors, verifies expected page count, substitutes zero pages for non-pinned direct write pages, and marks the UIO with `UIO_DIRECT`.

<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/os/linux/zfs/zfs_uio.c -->