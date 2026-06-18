# Group Research: group_966_linux_stable_sources_os_linux_linux_stable_fs_ceph_inode_c_sources_o_10b67fc1ee09

Scope checked against `Docs/research_subset_a.md`: `sources/os/linux/linux-stable` is included. All listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ceph/inode.c -->
# File Research: sources/os/linux/linux-stable/fs/ceph/inode.c

## Role

`inode.c` is the main CephFS inode metadata integration layer. It allocates and tears down Ceph inodes, maps MDS reply metadata into VFS inode state, manages directory fragmentation/delegation caches, handles dentry lease updates, prepopulates lookup/readdir results, implements setattr/getattr/permission paths, and schedules deferred inode work such as page invalidation, writeback, snap flushing, capability checks, and VM truncation.

## Major Responsibilities

- Create, locate, initialize, and evict Ceph inodes keyed by `ceph_vino`.
- Maintain Ceph-specific inode state in `struct ceph_inode_info`, including caps, xattrs, frag tree, layouts, quotas, snap realms, truncation state, and fscrypt metadata.
- Assimilate MDS inode/dentry/readdir replies into the local dcache/icache.
- Update inode size/time/link/auth/xattr/layout fields only when capabilities and version sequencing permit.
- Implement VFS inode operations for regular files, symlinks, encrypted symlinks, permissions, getattr, and setattr.
- Coordinate local page cache truncation and invalidation after remote metadata changes.
- Track directory fragmentation and delegated/repeated dirfrag routing state.
- Support CephFS snapshots and virtual snapdir inodes.

## Inode Creation And Lookup

`ceph_set_ino_cb()` initializes a newly inserted inode’s Ceph vino, Linux `i_ino`, raw i_version, and increments `mdsc->metric.total_inodes`.

`ceph_get_inode()` is the central inode-cache lookup/insert helper. It rejects reserved vinos, uses `inode_insert5()` when a preallocated inode is supplied, otherwise `iget5_locked()`, and consumes `newino` when another inode wins the race.

`ceph_new_inode()` allocates an inode before create-like operations, sets `CEPH_FSCRYPT_BLOCK_SHIFT`, prepares inherited ACL/security context for non-symlinks, initializes security context, and prepares fscrypt context unless the parent is the virtual snapdir.

`ceph_get_snapdir()` constructs the virtual `.snap` directory inode for a directory. It mirrors mode/owner/timestamps from the parent, borrows fscrypt auth when encrypted, sets snapdir inode ops/file ops, and gives it `CEPH_CAP_PIN` so it can be opened.

## Allocation And Eviction

`ceph_alloc_inode()` allocates `struct ceph_inode_info` from `ceph_inode_cachep`, initializes netfs state, locks, counters, cap state, xattr bookkeeping, snap state, frag tree, truncation fields, max-size fields, mode reference counters, unsafe op lists, work item state, and fscrypt fields.

`ceph_free_inode()` frees symlink and fscrypt-auth buffers, releases fscrypt inode info, and returns the inode object to the slab cache.

`ceph_evict_inode()` waits for outstanding netfs I/O, truncates page cache, clears inode state, unregisters fscache, removes caps, adjusts quota realm accounting, drops snap realm/snapid references, frees all directory frag tree nodes, destroys xattrs, releases xattr blobs, and puts layout pool namespace strings.

## Directory Fragment Tree

CephFS directories can be split into fragments and delegated/replicated across MDS ranks. This file tracks that in `ci->i_fragtree`.

Key helpers:

- `__get_or_create_frag()` inserts a `ceph_inode_frag` into an RB tree keyed by frag id.
- `__ceph_find_frag()` searches the RB tree.
- `__ceph_choose_frag()` walks split nodes to choose the leaf containing a hash value and optionally returns delegation info.
- `ceph_choose_frag()` wraps selection with `i_fragtree_mutex`.
- `ceph_fill_dirfrag()` updates per-fragment auth/replica delegation info from an MDS reply.
- `ceph_fill_fragtree()` reconciles the local split tree with the MDS-provided `ceph_frag_tree_head`, including sorting split records and pruning stale nodes.

Concurrency is split between `i_fragtree_mutex` for frag tree topology and `i_ceph_lock` for cap/auth state reads needed to resolve parent-auth delegation.

## MDS Inode Reply Assimilation

`ceph_fill_inode()` is the largest and most important function in the file. It populates a new or existing inode from `ceph_mds_reply_info_in`.

Important behavior:

- Verifies that an existing inode does not change file type or special-device rdev.
- Preallocates caps, xattr blobs, pool namespace strings, and snapid maps before taking `i_ceph_lock`.
- Decides whether reply metadata is newer using Ceph’s projected/stable inode version semantics.
- Updates raw inode change attribute from `iinfo->change_attr`.
- Merges issued and dirty caps to decide what local state must not be overwritten.
- Updates quota and immutable subvolume id.
- Applies fscrypt auth on new or previously unauthenticated encrypted inodes.
- Updates auth metadata, birth time, snapshot birth time, link count, file times, file counts, layout, pool namespace, file size, max size, directory recursive stats, xattrs, and inode version according to cap ownership.
- Handles encrypted file size by comparing object-rounded size with fscrypt cleartext file length.
- Sets VFS inode operations/file operations by file type.
- Allocates/caches symlink targets, with separate encrypted symlink handling via base64 decode and fscrypt get-link support.
- Adds new caps via `ceph_add_cap()` or accumulates snap caps for snapshot inodes.
- Updates fmode tracking, registers fscache cookies, fills inline data, wakes cap waiters, queues VM truncation, updates frag tree and dirfrag delegation.

The function is careful to avoid overwriting locally authoritative fields when exclusive caps or dirty caps are held.

## Size, Time, Subvolume, And Fscrypt

`ceph_fill_file_size()` applies MDS size/truncate state. It updates `i_size`, `i_blocks`, fscache size, reported size, truncate sequence, and page-cache truncation target. It queues truncation when caps or mappings mean local cached pages may remain beyond the new size. Encrypted files track a separate page-cache truncate size because object size can be rounded to fscrypt block boundaries.

`ceph_fill_file_time()` updates ctime/mtime/atime using capability-sensitive rules. With write/excl caps, it only accepts newer or compatible MDS time data; without relevant caps, MDS timestamps are authoritative.

`ceph_inode_set_subvolume()` sets the inode’s immutable subvolume id once. A later change triggers `WARN_ON_ONCE()` and is ignored.

`fill_fscrypt_truncate()` supports encrypted truncation that cuts through the last encrypted block. It obtains read caps, writes back dirty buffered data if needed, reads the last block, zeroes the truncated tail, encrypts the block in place, and attaches a pagelist payload to the setattr MDS request.

## Dentry And Trace Filling

`ceph_get_reply_dir()` validates that the parent inode associated with a dentry reply matches the directory inode in the reply. If the request parent is stale, it warns once and looks up the correct inode by vino.

Dentry lease helpers:

- `__update_dentry_lease()` updates a dentry lease under session mutex and dentry lock, including primary-link flag, shared generation, TTL, renewal timing, sequence, and session reference.
- `update_dentry_lease()` wraps locking and releases any displaced session.
- `update_dentry_lease_careful()` validates dentry name, parent vino, and target vino before updating leases when the parent inode is not locked.

`splice_dentry()` attaches a dentry to an inode with `d_splice_alias()`. For directories it first prunes any existing alias to prevent stale readdir-cache references after alias movement.

`ceph_fill_trace()` incorporates MDS replies for lookups and mutations. It can fill a parent directory inode, target inode, dentry lease, rename movement, null dentry after unlink/negative lookup, snapped directory lookup, and careful lease-only updates when parent locking is unavailable. It also handles aborted requests and ensures extra parent references from `ceph_get_reply_dir()` are dropped.

## Readdir Prepopulation

`readdir_prepopulate_inodes_only()` fills inode cache entries from readdir replies without dentry manipulation when a request is aborted.

`ceph_readdir_prepopulate()` builds dentries and inodes from directory listing replies, handles hash-ordered offsets, updates dirfrag delegation, starts readdir cache population at the leftmost fragment, resolves stale positive dentries pointing at wrong inos, handles `DCACHE_NOKEY_NAME`, fills inodes, splices negative dentries, sets dentry offsets, updates leases, and records cache entries when ordered/release counts match.

`fill_readdir_cache()` stores dentry pointers in folios under the directory mapping. It disables cache population if directory release/order counters no longer match the request snapshot.

`ceph_readdir_cache_release()` releases the mapped folio used during cache population.

## Deferred Inode Work

`ceph_queue_inode_work()` sets a work bit, takes an inode reference, and queues `ci->i_work` on `fsc->inode_wq`.

`ceph_inode_work()` processes work bits:

- `CEPH_I_WORK_WRITEBACK`: `filemap_fdatawrite()`.
- `CEPH_I_WORK_INVALIDATE_PAGES`: `ceph_do_invalidate_pages()`.
- `CEPH_I_WORK_VMTRUNCATE`: `__ceph_do_pending_vmtruncate()`.
- `CEPH_I_WORK_CHECK_CAPS`: `ceph_check_caps()`.
- `CEPH_I_WORK_FLUSH_SNAPS`: `ceph_flush_snaps()`.

`ceph_do_invalidate_pages()` invalidates fscache and page cache while coordinating with read-cache revocation generation. Shutdown inodes get mapping error `-EIO` and full page-cache truncation.

`__ceph_do_pending_vmtruncate()` applies pending page-cache truncation, flushing dirty snapped pages first when required, resizing fscache, truncating page cache, clearing pending state, checking caps when no write-buffer refs remain, and waking cap waiters.

## Setattr Path

`ceph_setattr()` is the VFS entry point. It rejects snapshots as read-only, rejects shutdown inodes, runs fscrypt and VFS setattr preparation, checks max file size and quota, delegates to `__ceph_setattr()`, then runs `posix_acl_chmod()` after successful mode changes.

`__ceph_setattr()` decides whether requested changes can be applied locally under held exclusive/write caps or must be sent to the MDS. It handles fscrypt auth, uid, gid, mode, atime, mtime, size, ctime-only updates, dirty cap marking, cap release masks, remote setattr requests, encrypted truncate payloads, and retry on `-EAGAIN` for fscrypt RMW races.

Local changes dirty caps and increment raw inode version; remote changes populate `req->r_args.setattr` and drop relevant caps. Size changes that go remote trigger pending VM truncation after success.

## Getattr, Permission, And Virtual Xattrs

`ceph_try_to_choose_auth_mds()` chooses auth MDS instead of a random replica when exclusive caps or rstat/xattr semantics make replica answers expensive or potentially stale.

`__ceph_do_getattr()` checks whether needed caps are already held unless forced; otherwise sends `CEPH_MDS_OP_GETATTR`. With a locked page it validates inline-data reply semantics and returns inline length or `-ENODATA`.

`ceph_do_getvxattr()` sends `CEPH_MDS_OP_GETVXATTR` with `CEPHFS_FEATURE_OP_GETVXATTR`, copies the returned value if the caller buffer is large enough, and returns length or error.

`ceph_permission()` fetches auth-shared metadata before calling `generic_permission()`; nonblocking permission checks return `-ECHILD`.

`statx_to_caps()` maps requested statx fields to Ceph cap masks.

`ceph_getattr()` optionally refreshes metadata, fills generic stats, reports Ceph-present inode number, btime, change cookie, snapshot-specific device id, directory size semantics, snapdir size from snap realm, directory block/nlink adjustments, and statx attributes for monotonic change and encryption.

## Shutdown

`ceph_inode_shutdown()` marks the inode shutdown, purges all inode caps, queues page invalidation if needed, and drops any inode references returned by cap purge.

## Key Interactions

- Depends heavily on `mds_client.h` request/reply/cap machinery.
- Uses `cache.h` for dentry lease and directory cache helpers.
- Uses `crypto.h` and fscrypt APIs for encrypted filenames, symlinks, file sizes, and truncation payloads.
- Uses fscache and netfs helpers for cached data lifecycle.
- Exposes inode operations consumed by other CephFS VFS operation tables.

## Concurrency Notes

- `ci->i_ceph_lock` protects most Ceph inode metadata and cap state.
- `mdsc->snap_rwsem` must be held by `ceph_fill_inode()` callers.
- `i_fragtree_mutex` protects directory fragment tree structure.
- `i_truncate_mutex` serializes page invalidation and VM truncation.
- Dentry leases require `dentry->d_lock`, with session refs managed carefully when lease ownership changes.
- Workqueue operations hold inode refs while queued and release them after work completes.

## Edge Cases And Defensive Checks

- Reserved vinos return `-EREMOTEIO`.
- Existing inode type/rdev changes are treated as stale metadata.
- Directory nonzero file sizes are warned and coerced to zero.
- Subvolume id changes after first set warn and are ignored.
- Parent/directory reply mismatch warns and retries with the correct inode.
- Snapdir and snapshot inodes have special capability, device, and readonly handling.
- Encrypted file size/truncate logic accounts for object-rounded sizes and block RMW requirements.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ceph/inode.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ceph/io.c -->
# File Research: sources/os/linux/linux-stable/fs/ceph/io.c

## Role

`io.c` provides CephFS I/O mode serialization helpers. It coordinates buffered reads/writes with direct I/O by using `inode->i_rwsem` and the Ceph inode flag `CEPH_I_ODIRECT`.

The design is borrowed from NFS and lets same-mode operations run concurrently while forcing transitions between buffered and direct I/O to drain or flush the incompatible mode.

## Main Entry Points

- `ceph_start_io_read()`
- `ceph_end_io_read()`
- `ceph_start_io_write()`
- `ceph_end_io_write()`
- `ceph_start_io_direct()`
- `ceph_end_io_direct()`

All start functions are declared `__must_check` in `io.h`.

## Buffered I/O Path

`ceph_start_io_read()` takes `inode->i_rwsem` for read optimistically. If `CEPH_I_ODIRECT` is already clear, buffered reads can proceed in parallel. If direct I/O mode is active, it drops the read lock, takes the write lock, calls `ceph_block_o_direct()`, then downgrades to a read lock.

`ceph_start_io_write()` takes `inode->i_rwsem` for write and calls `ceph_block_o_direct()`.

`ceph_block_o_direct()` requires the write side of `i_rwsem`. It clears `CEPH_I_ODIRECT_BIT` under `ci->i_ceph_lock` with memory barriers and, if direct I/O was active, calls `inode_dio_wait()` after dropping the spinlock. This drains outstanding direct I/O before buffered operations proceed.

End functions release the corresponding lock: buffered reads call `up_read()`, buffered writes call `up_write()`.

## Direct I/O Path

`ceph_start_io_direct()` takes `i_rwsem` for read optimistically. If `CEPH_I_ODIRECT` is already set, concurrent direct I/O can proceed. Otherwise it upgrades through a write-lock slow path, calls `ceph_block_buffered()`, and downgrades to read lock.

`ceph_block_buffered()` requires the write side of `i_rwsem`. It sets `CEPH_I_ODIRECT_BIT` under `i_ceph_lock` with memory barriers and, when switching from buffered mode, calls `filemap_write_and_wait()` to flush buffered dirty pages before direct I/O proceeds.

`ceph_end_io_direct()` releases the shared read lock.

## Concurrency Model

- `inode->i_rwsem` is the coarse mode-transition lock.
- `ci->i_ceph_lock` protects the `CEPH_I_ODIRECT` flag.
- Memory barriers around atomic bit changes ensure flag state is visible consistently.
- Same-mode reads/direct I/O can share the read lock.
- Buffered writes and truncates use the write lock and serialize with all direct I/O and buffered reads.

## Important Behavior

- Direct I/O mode blocks buffered I/O until direct I/O is drained.
- Buffered mode blocks direct I/O until buffered writes are flushed.
- Killable lock acquisition propagates interruption errors from `down_read_killable()` or `down_write_killable()`.
- A FIXME notes possible future use of `unmap_mapping_range()` when blocking buffered I/O.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ceph/io.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ceph/io.h -->
# File Research: sources/os/linux/linux-stable/fs/ceph/io.h

## Role

`io.h` is the local CephFS header for I/O mode coordination helpers implemented in `io.c`.

## Contents

It has a standard include guard `_FS_CEPH_IO_H`, includes `<linux/compiler_attributes.h>`, and declares:

- `int __must_check ceph_start_io_read(struct inode *inode);`
- `void ceph_end_io_read(struct inode *inode);`
- `int __must_check ceph_start_io_write(struct inode *inode);`
- `void ceph_end_io_write(struct inode *inode);`
- `int __must_check ceph_start_io_direct(struct inode *inode);`
- `void ceph_end_io_direct(struct inode *inode);`

## Contract

Callers must check the start helpers because they may fail on killable lock acquisition. A successful start helper must be paired with the matching end helper to release `inode->i_rwsem`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ceph/io.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ceph/ioctl.c -->
# File Research: sources/os/linux/linux-stable/fs/ceph/ioctl.c

## Role

`ioctl.c` implements CephFS-specific ioctl handling plus fscrypt ioctl forwarding that requires CephFS/MDS feature checks. It maps user ABI structures from `ioctl.h` to Ceph layout metadata, MDS requests, OSD placement calculations, and file consistency flags.

## Layout Ioctls

`ceph_ioctl_get_layout()` refreshes layout metadata with `ceph_do_getattr(..., CEPH_STAT_CAP_LAYOUT, false)`, copies the current inode layout into `struct ceph_ioctl_layout`, sets obsolete `preferred_osd` to `-1`, and copies it to userspace.

`__validate_layout()` validates object size and stripe unit alignment to page size, validates `object_size % stripe_unit`, and checks that `data_pool` is present in the current MDS map data pools under `mdsc->mutex`.

`ceph_ioctl_set_layout()` copies user layout, fetches current layout, fills unspecified fields from current inode layout, validates the resulting layout, builds a `CEPH_MDS_OP_SETLAYOUT` request, drops file shared/excl caps, and sends it to the auth MDS.

`ceph_ioctl_set_layout_policy()` validates a directory layout policy and sends `CEPH_MDS_OP_SETDIRLAYOUT`, causing future descendants to inherit the policy unless overridden.

## Data Location Ioctl

`ceph_ioctl_get_dataloc()` maps a file offset to Ceph object and OSD placement details.

It:

- Copies `struct ceph_ioctl_dataloc` from userspace.
- Uses `ceph_calc_file_object_mapping()` to compute object number, object offset, object size, and stripe unit.
- Builds the object name as `<ino>.<object_no>`.
- Constructs a `ceph_object_locator` with pool id and pool namespace.
- Converts object locator to PG and then to acting primary OSD under `osdc->lock`.
- Copies the OSD network address if available.
- Copies the populated structure back to userspace.

## Lazy And Sync I/O Flags

`ceph_ioctl_lazyio()` marks a file descriptor as lazy via `CEPH_FILE_MODE_LAZY`, increments the per-inode lazy mode counter when first set, touches fmode state, and triggers `ceph_check_caps()` when the file newly becomes lazy.

`ceph_ioctl_syncio()` sets `CEPH_F_SYNC` in `struct ceph_file_info`, forcing sync/direct-like behavior for that file descriptor.

## Fscrypt Support

`vet_mds_for_fscrypt()` checks active MDS sessions for `CEPHFS_FEATURE_ALTERNATE_NAME`, returning `-EOPNOTSUPP` when the feature is unavailable.

`ceph_set_encryption_policy()` rejects encrypted policy setup on directories with striped layout (`stripe_count > 1`), verifies MDS fscrypt support, obtains `CEPH_CAP_FILE_SHARED` so empty-directory checks are reliable, calls `fscrypt_ioctl_set_policy()`, and releases cap refs.

The dispatch path also vets MDS feature support before fscrypt policy get, extended policy get, add key, and nonce retrieval. Key removal and key-status ioctls are passed through without the same feature gate in this file.

## Dispatch

`ceph_ioctl_cmd_name()` maps known commands to debug names.

`ceph_ioctl()` logs the command and dispatches:

- `CEPH_IOC_GET_LAYOUT`
- `CEPH_IOC_SET_LAYOUT`
- `CEPH_IOC_SET_LAYOUT_POLICY`
- `CEPH_IOC_GET_DATALOC`
- `CEPH_IOC_LAZYIO`
- `CEPH_IOC_SYNCIO`
- fscrypt policy/key/nonce ioctls

Unknown commands return `-ENOTTY`.

## Error Handling

- Bad userspace copies return `-EFAULT`.
- Invalid layout values or pools return `-EINVAL`.
- Missing fscrypt MDS support returns `-EOPNOTSUPP`.
- MDS request allocation errors propagate through `PTR_ERR()`.
- Dataloc placement conversion errors propagate from `ceph_object_locator_to_pg()`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ceph/ioctl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ceph/ioctl.h -->
# File Research: sources/os/linux/linux-stable/fs/ceph/ioctl.h

## Role

`ioctl.h` defines the CephFS userspace ioctl ABI consumed by `ioctl.c`.

## Constants

`CEPH_IOCTL_MAGIC` is `0x97`.

## Layout ABI

`struct ceph_ioctl_layout` contains:

- `stripe_unit`
- `stripe_count`
- `object_size`
- `data_pool`
- obsolete `preferred_osd`

All main fields use `__u64` for cross-architecture alignment. `preferred_osd` is obsolete; new values are ignored and returned as `-1`.

Defined layout commands:

- `CEPH_IOC_GET_LAYOUT`
- `CEPH_IOC_SET_LAYOUT`
- `CEPH_IOC_SET_LAYOUT_POLICY`

The comments document that file layouts control object striping and data pool selection; directory layout policy applies to future children, not retroactively.

## Data Location ABI

`struct ceph_ioctl_dataloc` is an in/out structure for mapping a file offset to object and OSD location data.

Fields include:

- input/output `file_offset`
- output object offset, object number, object size, object name
- output block offset and block size
- output OSD id
- output OSD address as `sockaddr_storage`

Defined command:

- `CEPH_IOC_GET_DATALOC`

## Consistency Control Ioctls

`CEPH_IOC_LAZYIO` relaxes consistency for a file descriptor so buffered I/O may be used when the application accepts weaker cross-client consistency.

`CEPH_IOC_SYNCIO` forces synchronous I/O behavior that bypasses page cache in cases similar to multi-client write sharing. The comment distinguishes it from `O_SYNC`/`O_DSYNC` and notes similarity to `O_DIRECT` without the same alignment and stable-page constraints.

## Notable ABI Detail

Both `CEPH_IOC_SET_LAYOUT_POLICY` and `CEPH_IOC_SYNCIO` use command number `5` with the same magic but different ioctl direction/argument encoding. This is existing ABI encoded through `_IOW` versus `_IO`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ceph/ioctl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ceph/locks.c -->
# File Research: sources/os/linux/linux-stable/fs/ceph/locks.c

## Role

`locks.c` implements CephFS POSIX byte-range locks and BSD flock locks by coordinating VFS local lock state with MDS-distributed lock state. It also serializes local locks into Ceph wire-format lock records for reconnect/reclaim style workflows.

## Lock Owner Encoding

A static `lock_secret` is initialized by `ceph_flock_init()` using `get_random_bytes()`.

`secure_addr()` xors the lock owner pointer with `lock_secret` and sets the high bit. The high bit tells the MDS that the encoded owner is sufficient to identify the lock owner, unlike older code that used owner plus pid.

## File Lock Lifetime Hooks

`ceph_fl_copy_lock()` installs private Ceph lock ownership tracking by incrementing `ci->i_filelock_ref` and storing an inode reference in `fl->fl_u.ceph.inode`.

`ceph_fl_release_lock()` releases that inode reference without using `fl_file`, which may already be gone. When the last file lock reference drops, it clears `CEPH_I_ERROR_FILELOCK` under `i_ceph_lock`.

`ceph_fl_lock_ops` wires these functions into VFS file lock lifecycle callbacks.

## MDS Lock Messaging

`ceph_lock_message()` builds and submits `CEPH_MDS_OP_SETFILELOCK` or `CEPH_MDS_OP_GETFILELOCK`.

It:

- Installs Ceph file lock ops and increments lock ref count for set-lock requests.
- Disables waiting for unlock and non-set operations.
- Creates an MDS request against the auth MDS.
- Converts VFS `[start,end]` to Ceph start/length, with length `0` representing through EOF.
- Encodes rule, type, owner, pid, start, length, and wait flag.
- Submits and waits for the request, optionally using an interrupt-aware wait helper.
- Decodes `GETFILELOCK` replies back into VFS `file_lock` fields, including negative pid convention.

## Interruptible Blocking Locks

`ceph_lock_wait_for_completion()` handles interrupted blocking lock acquisition.

If interrupted before result:

- Marks the original request aborted under `r_fill_mutex` to avoid concurrent fill paths that depend on caller-held locks.
- If the request was not yet sent, it treats the interruption as complete.
- Otherwise it sends a lock interrupt request using `CEPH_LOCK_FCNTL_INTR` or `CEPH_LOCK_FLOCK_INTR` with unlock type.
- Waits for safe completion so server-side state is settled.

This prevents orphaned distributed locks after local signal interruption.

## POSIX Lock Entry Point

`ceph_lock()` implements fcntl locking.

Behavior:

- Requires `FL_POSIX`, otherwise returns `-ENOLCK`.
- Rejects shutdown inodes with `-ESTALE`.
- Converts `GETLK`, `SETLK`, and `SETLKW` to MDS op/wait semantics.
- If `CEPH_I_ERROR_FILELOCK` is set, unlock still updates local lock state, but other operations return `-EIO`.
- Converts VFS lock type to Ceph shared/exclusive/unlock.
- For unlock, `try_unlock_file()` first checks/removes local lock state and avoids unnecessary MDS traffic when no local lock exists.
- Sends the distributed lock request.
- On successful non-unlock set-lock, installs the local POSIX lock via `posix_lock_file()`.
- If local lock installation fails, sends an MDS unlock to undo the distributed lock.

## Flock Entry Point

`ceph_flock()` is the BSD flock equivalent.

Behavior mirrors `ceph_lock()` but requires `FL_FLOCK`, uses `CEPH_LOCK_FLOCK`, always sends `CEPH_MDS_OP_SETFILELOCK`, and installs local locks with `locks_lock_file_wait()`.

On local installation failure after successful MDS lock acquisition, it sends a distributed unlock to roll back.

## Unlock Optimization

`try_unlock_file()` temporarily sets `FL_EXISTS` and calls `locks_lock_file_wait()`.

- If the VFS reports `-ENOENT` and the caller did not originally set `FL_EXISTS`, unlock is treated as success without MDS traffic.
- Otherwise a positive return tells the caller to send the MDS unlock.

## Lock Counting And Encoding

`ceph_count_locks()` counts current POSIX and flock locks from `locks_inode_context()` under `ctx->flc_lock`.

`lock_to_ceph_filelock()` converts a VFS `file_lock` to `struct ceph_filelock`, including start, length, pid, secure owner, and Ceph lock type.

`ceph_encode_locks_to_buffer()` serializes current locks into a caller-provided `struct ceph_filelock` array. It separately validates that observed fcntl/flock counts do not exceed expected counts and returns `-ENOSPC` if they do.

`ceph_locks_to_pagelist()` appends lock metadata to a `ceph_pagelist` in this order:

1. fcntl lock count
2. fcntl lock records
3. flock lock count
4. flock lock records

## Concurrency And State

- `ci->i_ceph_lock` protects `CEPH_I_ERROR_FILELOCK`.
- `i_filelock_ref` tracks active lock references and controls when filelock error state can be cleared.
- VFS lock context spinlock protects traversal of local lock lists.
- MDS request completion paths coordinate with `r_fill_mutex` on interruption to avoid racing reply-fill logic.

## Error Handling

- Nonmatching lock classes return `-ENOLCK`.
- Shutdown inodes return `-ESTALE`.
- Filelock error state returns `-EIO` except unlock still cleans local state.
- Local lock deadlock/failure after MDS success triggers best-effort MDS unlock rollback.
- Encoding unknown VFS lock types returns `-EINVAL`.
- Encoding more locks than expected returns `-ENOSPC`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ceph/locks.c -->