# subset-b-005634 grouped research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ceph/inode.c -->
# sources/distributed-fs/ceph-client/fs/ceph/inode.c

## Purpose
`inode.c` is the central CephFS inode metadata integration layer in the Linux client. It allocates and tears down Ceph-specific inode state, assimilates MDS reply metadata into the VFS inode cache, manages directory fragment delegation state, attaches dentries and leases after lookup/readdir replies, handles asynchronous inode work for writeback/invalidation/truncation/cap checks, and implements the inode operations for permission, getattr, setattr, symlink resolution, ACL/xattr integration, and shutdown.

## Important APIs, types, and functions
The file primarily operates on `struct ceph_inode_info`, the Ceph wrapper around the VFS/netfs inode. Important exported helpers include `ceph_new_inode`, `ceph_as_ctx_to_req`, `ceph_get_inode`, `ceph_get_snapdir`, `ceph_alloc_inode`, `ceph_free_inode`, `ceph_evict_inode`, `ceph_fill_file_size`, `ceph_inode_set_subvolume`, `ceph_fill_file_time`, `ceph_fill_inode`, `ceph_fill_trace`, `ceph_readdir_cache_release`, `ceph_readdir_prepopulate`, `ceph_inode_set_size`, `ceph_queue_inode_work`, `__ceph_do_pending_vmtruncate`, `__ceph_setattr`, `ceph_setattr`, `ceph_try_to_choose_auth_mds`, `__ceph_do_getattr`, `ceph_do_getvxattr`, `ceph_permission`, `ceph_getattr`, and `ceph_inode_shutdown`.

Core local helpers include `ceph_set_ino_cb`, `ceph_get_reply_dir`, `__get_or_create_frag`, `__ceph_find_frag`, `ceph_choose_frag`, `ceph_fill_dirfrag`, `ceph_fill_fragtree`, `decode_encrypted_symlink`, dentry lease helpers, `splice_dentry`, `readdir_prepopulate_inodes_only`, `fill_readdir_cache`, `ceph_do_invalidate_pages`, `ceph_inode_work`, and `fill_fscrypt_truncate`. Inode operation tables exported from this file are `ceph_file_iops`, `ceph_symlink_iops`, and `ceph_encrypted_symlink_iops`.

## Control flow
Inode identity starts in `ceph_get_inode`, which rejects reserved vnodes and uses `iget5_locked` or `inode_insert5` with `ceph_set_ino_cb` so `i_vino`, `i_ino`, `i_version`, and inode metrics are initialized exactly when a cache entry is created. `ceph_new_inode` prepares a speculative inode for create-like operations by initializing ACL/security context and fscrypt context before the MDS reply binds it to a real vino.

MDS reply ingestion centers on `ceph_fill_inode`. It validates immutable inode type and device number, preallocates cap/xattr/pool namespace objects before taking `i_ceph_lock`, computes whether the reply is newer than the cached version, updates caps/quota/subvolume/fscrypt state, and then conditionally updates auth, link, file, layout, xattr, directory rstat, symlink, and inline-data state according to issued caps and reply version. It installs VFS operation tables based on inode type, adds or records caps, wakes cap waiters, queues VM truncation if a remote truncate requires page-cache work, and updates directory fragment delegation data. The function is deliberately cap-aware: client-local dirty or exclusive state wins over stale MDS metadata, while authoritative or newer metadata updates the local inode.

`ceph_fill_trace` incorporates whole lookup/mutation replies. It may refresh the parent directory inode, create or recover the target dentry for encrypted/name-translated lookups, fill the target inode, handle rename dentry movement, splice negative dentries to target inodes, delete dentries on null replies, and update dentry leases only when parent locking, target identity, and lease validity checks line up. `ceph_readdir_prepopulate` performs the analogous batch path for readdir replies: it calculates stable fpos offsets, looks up or allocates dentries, fills each listed inode, splices negative dentries, installs leases, and optionally stores dentry pointers in the directory page-cache backed readdir cache while the directory release/order counters still match the request.

`ceph_setattr` is the VFS entry point for metadata changes. It rejects snapshots and shutdown inodes, runs fscrypt and generic setattr validation, enforces max-file-size and quota limits for size changes, then calls `__ceph_setattr`. `__ceph_setattr` first tries local dirtying under suitable exclusive/write caps and otherwise builds an MDS `CEPH_MDS_OP_SETATTR` request with a mask and cap-drop set. Encrypted shrinking truncates that are not fscrypt-block aligned go through `fill_fscrypt_truncate`, which reads, zeroes, encrypts, and sends the last block to the MDS for safe read-modify-write. Remote truncate requests may retry on `-EAGAIN` and successful size changes force pending page-cache truncation.

`__ceph_do_getattr` avoids the MDS when cached caps satisfy the requested mask; otherwise it sends `CEPH_MDS_OP_GETATTR`, choosing auth MDS when exclusive caps, rstat, or xattr consistency require it. `ceph_getattr` maps statx request bits to Ceph cap masks, fills generic attributes, adjusts directory size/link semantics, reports snapshot device numbers, btime, change-cookie, and encryption attributes. `ceph_permission` obtains current auth metadata before delegating to `generic_permission`.

Asynchronous work is funneled through `ceph_queue_inode_work` and `ceph_inode_work`. Work bits invoke data writeback, page invalidation for cap revocation, pending VM truncate, cap checks, and snap flushing while holding an inode reference. `ceph_inode_shutdown` marks the inode shutdown, purges caps, and queues invalidation if cap removal says cached pages are unsafe.

## State and persistence behavior
The file maintains extensive volatile client state: `i_vino`, `i_version`, raw inode change attribute, inline-data version, time-warp and truncate sequence numbers, Ceph capability trees and dirty/flushing lists, cap reference counters, file-mode reference counts, `i_rdcache_gen`/`i_rdcache_revoking`, directory fragment rbtrees, xattr blobs and rbtrees, readdir-cache offsets, snap realm references, fscrypt authentication data, symlink strings, subvolume id, quota/rstat fields, and async work bits. Persistent truth lives in the Ceph MDS and OSD cluster; this code updates local cache only when protected by caps or when newer authoritative replies arrive.

Truncation and invalidation are stateful. `ceph_fill_file_size` updates `i_size`, `i_blocks`, fscache, reported size, truncate sequence, and `i_truncate_pagecache_size`, then returns whether VM truncation must be queued. `__ceph_do_pending_vmtruncate` serializes with `i_truncate_mutex`, flushes dirty snapped pages before truncating, resizes fscache, truncates page cache, clears pending state only if no newer truncate raced, and wakes cap waiters. `ceph_do_invalidate_pages` invalidates fscache and page cache only when the revocation generation still matches.

Snapdir and snapshot inode behavior is special: `ceph_get_snapdir` synthesizes a virtual snapdir inode from its parent, borrows fscrypt auth for encrypted parents, and sets pin caps so it can be opened. Snapshot inodes keep `i_snapid_map` and `i_snap_caps`, while normal inodes receive live MDS caps.

## Dependencies and integration points
This file integrates with the VFS inode/dentry/page-cache APIs, the netfs library, fscache, Linux fscrypt, generic ACL/xattr/security helpers, statx, quota, the Ceph MDS request/cap/snap/session subsystems, Ceph file layout and string helpers, directory code, xattr/ACL code, crypto code, export/quota/caps callers, and the MDS reply parser. `mds_client.c` calls `ceph_fill_trace` and `ceph_readdir_prepopulate` when handling replies. `addr.c`, `file.c`, `quota.c`, `xattr.c`, `export.c`, `acl.c`, and `crypto.c` call the exported getattr/setattr/truncation helpers.

## Risks
The highest-risk areas are ordering between caps and metadata replay, stale parent/dentry identity after rename, encrypted size and symlink handling, truncation races against dirty snapped pages or newer truncate sequences, invalidation races during cache-cap revocation, directory fragment tree update consistency, and lifetime rules around new inodes, snap realms, xattr blobs, caps, and dentry lease sessions. Another subtle risk is selecting a replica MDS for metadata that is stale under exclusive caps or buggy xattr replication; `ceph_try_to_choose_auth_mds` mitigates this for selected masks.

## Test signals
Useful tests include create/lookup/readdir/rename/unlink flows under concurrent renames, MDS reply reordering with projected and stable versions, remote truncates while mmap/read/write references exist, encrypted symlink lookup and fscrypt unaligned shrink truncate, page-cache invalidation on cache-cap revoke, snapdir and snapshot getattr, directory rstat and RBYTES mount option behavior, dentry lease expiry/renewal, directory frag split/delegation updates, setattr under local exclusive caps versus remote MDS request, quota/max-size enforcement, shutdown-induced `-ESTALE`, and statx masks including btime/change-cookie/encryption.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ceph/inode.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ceph/io.c -->
# sources/distributed-fs/ceph-client/fs/ceph/io.c

## Purpose
`io.c` provides the CephFS client helpers that serialize buffered I/O and direct I/O against each other. It uses `inode->i_rwsem` and the Ceph inode `CEPH_I_ODIRECT` flag to switch an inode between buffered and direct I/O modes without allowing stale page-cache data or overlapping mode transitions.

## Important APIs, types, and functions
The exported API is `ceph_start_io_read`, `ceph_end_io_read`, `ceph_start_io_write`, `ceph_end_io_write`, `ceph_start_io_direct`, and `ceph_end_io_direct`. Internal helpers are `ceph_block_o_direct`, which clears direct-I/O mode and waits for outstanding direct I/O, and `ceph_block_buffered`, which sets direct-I/O mode and flushes buffered dirty data. State is held in `struct ceph_inode_info::i_ceph_flags`, specifically `CEPH_I_ODIRECT_BIT`, protected by `i_ceph_lock` and ordered with atomic memory barriers.

## Control flow
Buffered reads optimistically take `i_rwsem` for read and check whether direct mode is already clear. If direct mode is set, they drop the read lock, take the write lock, clear `CEPH_I_ODIRECT`, wait for in-flight DIO via `inode_dio_wait`, downgrade to a read lock, and proceed. Buffered writes take the write lock up front and force direct mode off.

Direct I/O mirrors the read path. `ceph_start_io_direct` optimistically takes the read lock and returns immediately if `CEPH_I_ODIRECT` is already set. If not, it upgrades through a write lock, sets direct mode, flushes dirty buffered pages with `filemap_write_and_wait`, downgrades to a read lock, and lets parallel direct I/O proceed. End helpers release the corresponding read or write lock.

## State and persistence behavior
The mode bit is purely in-memory and is not persisted to the MDS. It is a local coherency guard that allows multiple operations of the same mode to run concurrently under shared `i_rwsem` while serializing mode transitions under the write side. The helpers also synchronize with VFS direct I/O accounting and page-cache writeback state.

## Dependencies and integration points
The implementation depends on Linux inode rwsems, spinlocks, memory-barrier primitives, `inode_dio_wait`, and `filemap_write_and_wait`. Ceph file read/write paths call these helpers before buffered or direct read/write operations; `file.c` contains the main call sites around sync/direct read and write paths.

## Risks
The key risks are missed mode-bit ordering, failure to wait for outstanding direct I/O before buffered access, failure to flush buffered data before direct I/O, lock leaks on error paths at call sites, and starvation under frequent direct/buffered mode switching. The `FIXME` about `unmap_mapping_range` signals that mappings may need stronger handling if direct mode must exclude already-mapped cached pages.

## Test signals
Exercise mixed buffered and O_DIRECT reads/writes from multiple threads, signal interruption while acquiring `i_rwsem`, direct writes after dirty buffered writes, buffered reads after in-flight direct writes, mmap plus direct I/O workloads, and tracing that every successful start helper is matched by the right end helper.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ceph/io.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ceph/io.h -->
# sources/distributed-fs/ceph-client/fs/ceph/io.h

## Purpose
`io.h` is the small public header for CephFS I/O mode exclusion helpers. It lets Ceph file code bracket buffered read, buffered write, and direct I/O sections without exposing the internal flag and locking implementation in `io.c`.

## Important APIs, types, and functions
The header declares `ceph_start_io_read`, `ceph_end_io_read`, `ceph_start_io_write`, `ceph_end_io_write`, `ceph_start_io_direct`, and `ceph_end_io_direct`. The start functions are annotated `__must_check`, which forces callers to handle lock-acquisition failures such as killable waits interrupted by signals.

## Control flow
There is no runtime control flow in the header. Its role is to define the compile-time contract: callers call a checked `ceph_start_io_*` function before entering the corresponding data path and call the matching `ceph_end_io_*` after the protected operation.

## State and persistence behavior
The header owns no state. It abstracts the in-memory I/O mode state maintained by `io.c` on `struct ceph_inode_info` and `inode->i_rwsem`.

## Dependencies and integration points
It includes `linux/compiler_attributes.h` for `__must_check` and relies on users having `struct inode` visible through the surrounding Ceph/VFS includes. It is included by `io.c` and Ceph file data-path code.

## Risks
The main risks are API misuse: ignoring a failed start call, mismatching direct/read/write end helpers, or entering data paths without the bracket. Since this header does not encode ownership types, correctness depends on call-site discipline and review.

## Test signals
Build warnings for ignored `__must_check` returns, static analysis for paired start/end calls, and runtime stress tests covering interrupted lock acquisition and all read/write/direct call paths are the best signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ceph/io.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ceph/ioctl.c -->
# sources/distributed-fs/ceph-client/fs/ceph/ioctl.c

## Purpose
`ioctl.c` implements CephFS-specific file and directory ioctls plus forwarding for fscrypt ioctls. It exposes layout inspection/change, directory layout policy setting, file-offset-to-object-location mapping, lazy/sync I/O mode flags, and encryption policy/key operations through the VFS ioctl entry point.

## Important APIs, types, and functions
The public entry is `ceph_ioctl`. Important local handlers are `ceph_ioctl_get_layout`, `__validate_layout`, `ceph_ioctl_set_layout`, `ceph_ioctl_set_layout_policy`, `ceph_ioctl_get_dataloc`, `ceph_ioctl_lazyio`, `ceph_ioctl_syncio`, `vet_mds_for_fscrypt`, `ceph_set_encryption_policy`, and `ceph_ioctl_cmd_name`.

The file uses `struct ceph_ioctl_layout` and `struct ceph_ioctl_dataloc` from `ioctl.h`, `struct ceph_file_info` for per-open flags/mode, `struct ceph_inode_info` for layout and mode counters, MDS requests for layout mutation, and OSD map helpers for data location calculation.

## Control flow
`ceph_ioctl` logs the decoded command name and dispatches by command number. `CEPH_IOC_GET_LAYOUT` refreshes layout caps with `ceph_do_getattr`, then copies the current inode layout to userspace. `CEPH_IOC_SET_LAYOUT` copies user input, fetches the current layout, treats zero fields as "leave current value", validates the normalized layout, sends a `CEPH_MDS_OP_SETLAYOUT` request to the auth MDS, and drops shared/exclusive file caps so the reply can refresh layout state. `CEPH_IOC_SET_LAYOUT_POLICY` validates the supplied layout and sends `CEPH_MDS_OP_SETDIRLAYOUT` for the directory.

`CEPH_IOC_GET_DATALOC` copies a requested file offset from userspace, calculates the Ceph object number and object offset from the inode layout, builds the object name, maps the object locator through the current OSD map to a PG and primary OSD, optionally copies the OSD address, and returns the filled structure. `CEPH_IOC_LAZYIO` marks the open file mode lazy under `i_ceph_lock`, updates per-mode counts and MDS fmode touch state, then asks cap logic to re-evaluate. `CEPH_IOC_SYNCIO` sets a per-file sync flag.

For fscrypt ioctls, the dispatcher first verifies that an MDS session advertises `CEPHFS_FEATURE_ALTERNATE_NAME` for operations that depend on encrypted alternate names. Setting an encryption policy also rejects directories with striped layout, obtains shared file caps so empty-directory checks are reliable, delegates to `fscrypt_ioctl_set_policy`, and releases any cap refs.

## State and persistence behavior
Layout mutations persist in CephFS metadata through MDS requests. `GET_LAYOUT` and `GET_DATALOC` are read-only, but depend on current layout, MDS map data pool lists, and OSD map state. `LAZYIO` and `SYNCIO` are per-open client-side flags; lazy mode also updates `i_nr_by_mode` and cap desired-mode state in the inode, affecting consistency behavior while that file is open. Fscrypt policy and key ioctls persist or query fscrypt-managed metadata/key state, with Ceph-specific feature gating.

## Dependencies and integration points
The file integrates with VFS ioctl dispatch in Ceph file and dir operations, MDS client request creation/submission, MDS maps, OSD maps and striper object mapping, Ceph object locators, user-copy APIs, fscrypt ioctl helpers, cap acquisition/release, and Ceph debug logging. Layout validation depends on `mdsc->mdsmap->m_data_pg_pools`; data location depends on `osdc->osdmap` under `osdc->lock`.

## Risks
Risks include ABI compatibility of ioctl structs, accepting invalid striping or pool values, stale layout or OSD map data during dataloc queries, races between lazy/sync mode changes and cap revocation, per-file mode counter imbalance, feature detection that only checks the first non-null MDS session, and encryption-policy correctness when directory layout or rstats are stale. `CEPH_IOC_SET_LAYOUT_POLICY` and `CEPH_IOC_SYNCIO` both use ioctl number 5 with different direction encoding, which is ABI-sensitive and should not be changed casually.

## Test signals
Tests should cover layout get/set with zero/default fields, invalid unaligned stripe/object sizes, invalid data pools, directory layout policy inheritance, dataloc mapping across object boundaries and degraded/no-primary PGs, lazyio idempotence and cap checks, syncio path selection in reads/writes, fscrypt ioctls with and without MDS alternate-name support, striped directory encryption-policy rejection, and user-copy fault injection returning `-EFAULT`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ceph/ioctl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ceph/ioctl.h -->
# sources/distributed-fs/ceph-client/fs/ceph/ioctl.h

## Purpose
`ioctl.h` defines the CephFS user ABI for Ceph-specific ioctl commands. It documents and declares the layout and data-location structures used by `ioctl.c`, and assigns ioctl numbers under `CEPH_IOCTL_MAGIC`.

## Important APIs, types, and functions
The header defines `CEPH_IOCTL_MAGIC`, `struct ceph_ioctl_layout`, `struct ceph_ioctl_dataloc`, and command macros `CEPH_IOC_GET_LAYOUT`, `CEPH_IOC_SET_LAYOUT`, `CEPH_IOC_SET_LAYOUT_POLICY`, `CEPH_IOC_GET_DATALOC`, `CEPH_IOC_LAZYIO`, and `CEPH_IOC_SYNCIO`.

`struct ceph_ioctl_layout` uses 64-bit fields for stripe unit, stripe count, object size, data pool, and obsolete preferred OSD. `struct ceph_ioctl_dataloc` carries an in/out file offset plus object offset/number/size/name, stripe-block offset/size, primary OSD id, and OSD socket address.

## Control flow
There is no executable control flow. The macros encode direction and type information for VFS ioctl dispatch. Userspace fills the input fields and `ioctl.c` copies, validates, and completes the output fields.

## State and persistence behavior
The header has no state. It defines the ABI through which userspace can read or request persistent CephFS layout metadata, query volatile cluster placement, or change per-open I/O mode flags.

## Dependencies and integration points
It depends on Linux ioctl/type headers and is included by the CephFS ioctl implementation and userspace-facing builds that need these command definitions. It is tightly coupled to `ioctl.c` and the Ceph file layout model.

## Risks
This is ABI surface. Field size, layout, command number, direction, and magic changes can break existing tools. The obsolete `preferred_osd` field must remain compatible, and the reused numeric command value for layout policy and syncio is safe only because the encoded ioctl direction/type differs.

## Test signals
Compile-time ABI size checks in userspace tools, ioctl round trips on 32-bit and 64-bit architectures, old tool compatibility for `preferred_osd`, and command-dispatch tests for each macro are the most relevant signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ceph/ioctl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ceph/locks.c -->
# sources/distributed-fs/ceph-client/fs/ceph/locks.c

## Purpose
`locks.c` implements CephFS distributed POSIX byte-range locks and BSD flock locks. It translates Linux `struct file_lock` operations into MDS filelock requests, mirrors successful locks into the local VFS lock manager, handles interruptible blocking lock acquisition, and encodes local lock state for reconnect/session recovery.

## Important APIs, types, and functions
The externally used functions are `ceph_flock_init`, `ceph_lock`, `ceph_flock`, `ceph_count_locks`, `ceph_encode_locks_to_buffer`, and `ceph_locks_to_pagelist`. Internal helpers include `secure_addr`, `ceph_fl_copy_lock`, `ceph_fl_release_lock`, `ceph_lock_message`, `ceph_lock_wait_for_completion`, `try_unlock_file`, and `lock_to_ceph_filelock`.

Important state includes the boot-time random `lock_secret`, `struct file_lock_operations ceph_fl_lock_ops`, `ceph_inode_info::i_filelock_ref`, `CEPH_I_ERROR_FILELOCK`, local VFS lock contexts, MDS request filelock arguments, and encoded `struct ceph_filelock` arrays/pagelists.

## Control flow
`ceph_flock_init` seeds `lock_secret`. `secure_addr` XORs that secret with the Linux lock owner pointer and sets the high bit so the MDS can treat owner as sufficient identity. For set-lock operations, `ceph_lock_message` installs Ceph lock operations and takes an inode reference before request submission, builds a `CEPH_MDS_OP_SETFILELOCK` or `CEPH_MDS_OP_GETFILELOCK` request, converts Linux start/end to Ceph start/length, encodes owner/pid/type/wait, submits to the auth MDS, waits for completion, and decodes GETLK replies back into the caller's `file_lock`.

Blocking locks use `ceph_lock_wait_for_completion`. If the wait is interrupted before the original request completed, it marks the original request aborted under MDS client locking and, if the request had been sent, issues an interrupt-style unlock request (`CEPH_LOCK_FCNTL_INTR` or `CEPH_LOCK_FLOCK_INTR`). It then waits for the original safe completion so the MDS and client do not diverge.

`ceph_lock` handles POSIX locks. It rejects non-POSIX locks and shutdown inodes, converts GETLK/SETLKW semantics, checks sticky `CEPH_I_ERROR_FILELOCK`, short-circuits unlocks that do not exist locally, sends the MDS request, and only after MDS success installs the lock locally with `posix_lock_file`. If local deadlock detection fails after MDS success, it sends a compensating MDS unlock. `ceph_flock` follows the same pattern for flock locks using `locks_lock_file_wait`.

Reconnect encoding starts with `ceph_count_locks`, which counts POSIX and flock lists under the inode lock context spinlock. `ceph_encode_locks_to_buffer` converts each local lock into a contiguous `struct ceph_filelock` array and returns `-ENOSPC` if counts changed beyond the caller's allocation. `ceph_locks_to_pagelist` serializes counts and lock arrays into a Ceph pagelist in fcntl-then-flock order.

## State and persistence behavior
The authoritative distributed lock state lives in the MDS. The client mirrors successful locks in the local VFS lock lists so Linux semantics and conflict detection work locally. `i_filelock_ref` pins inode/cap state while locks exist and clears `CEPH_I_ERROR_FILELOCK` when all Ceph-backed locks are released. Lock owner values are process-local obfuscated identities derived from pointers and a random boot secret; they are stable enough for a client lifetime but not persistent across reboot.

## Dependencies and integration points
The file depends on Linux file-locking infrastructure, MDS client request APIs, Ceph pagelists, inode cap/error state, inode lifetime management, random bytes, and Ceph wire constants for filelock rules and commands. `super.h` exposes `ceph_lock` and `ceph_flock` to file operation tables, and reconnect/session recovery code can use the count/encode/pagelist helpers to replay lock state.

## Risks
The main risks are client/MDS divergence if a local lock install fails after MDS success, races during interrupted blocking locks, stale inode references from `fl_file` lifetime, lock count changes between count and encode, owner identity reuse after process/client lifetime changes, and sticky error handling that must not strand local locks. The code also relies on correct caller serialization where MDS reply handling can otherwise race with locks held by VFS callers.

## Test signals
Tests should include POSIX GETLK/SETLK/SETLKW and flock shared/exclusive/unlock across multiple clients, interrupted blocking locks, local deadlock failure forcing compensating unlock, nonexistent unlock behavior, MDS session reconnect with lock replay, error injection setting `CEPH_I_ERROR_FILELOCK`, inode release while locks remain, and lock count changes during encode returning `-ENOSPC`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ceph/locks.c -->
