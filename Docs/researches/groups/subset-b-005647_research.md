# subset-b-005647 research

Grouped research for ext2 superblock, symlink, tracing, and xattr files plus ext4 build, ACL, bitmap, block allocation, block-validity, crypto, and directory iteration files. Each section preserves the source path in its title and is delimited for deterministic splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ext2/super.c -->
# sources/distributed-fs/ceph-client/fs/ext2/super.c

## Purpose

`fs/ext2/super.c` is the ext2 VFS mount, superblock, quota, statistics, sync, freeze, remount, NFS export, inode-cache, and module-registration implementation. It turns an on-disk ext2 superblock and group descriptor table into an initialized `struct super_block`, validates core geometry and feature bits, wires ext2 operation tables into VFS, and persists mount-state transitions back to disk. It is the central integration point for ext2 block-device mounting in this source tree.

## Important APIs, types, and functions

- `ext2_error()`, `ext2_msg()`, and `ext2_msg_fc()` report filesystem and mount-context diagnostics. `ext2_error()` also marks the on-disk superblock with `EXT2_ERROR_FS`, syncs it, and optionally panics or remounts read-only according to `errors=`.
- `ext2_update_dynamic_rev()` upgrades revision-zero filesystems when newer compat features are enabled.
- `ext2_put_super()` releases quota state, xattr cache, group descriptor buffers, counters, DAX device references, and `struct ext2_sb_info`.
- `ext2_alloc_inode()`, `ext2_free_in_core_inode()`, `init_once()`, `init_inodecache()`, and `destroy_inodecache()` manage the `ext2_inode_cache` slab.
- `ext2_show_options()` reconstructs mount options for `/proc/mounts`.
- `ext2_sops` publishes VFS superblock callbacks: inode allocation/free, write/evict inode, put super, sync, freeze/unfreeze, statfs, show options, and optional quota IO.
- `ext2_export_ops`, `ext2_nfs_get_inode()`, `ext2_fh_to_dentry()`, and `ext2_fh_to_parent()` provide stable NFS file-handle lookup.
- `struct ext2_fs_context`, `ext2_param_spec`, and `ext2_parse_param()` implement the modern `fs_context` option parser for `sb=`, `errors=`, `dax`, `xip`, quotas, ACLs, user xattrs, reservation, grouping, uid/gid reservation, and legacy ignored options.
- `ext2_fill_super()` is the main mount routine. It allocates `ext2_sb_info`, reads the superblock, checks features and geometry, reads group descriptors, initializes counters/caches/reservation trees, reads the root inode, and installs VFS operations.
- `ext2_sync_super()`, `ext2_sync_fs()`, `ext2_freeze()`, `ext2_unfreeze()`, and `ext2_write_super()` keep superblock counters, timestamps, and validity state coherent on disk.
- `ext2_reconfigure()` implements remount option changes and read-only/read-write transitions.
- `ext2_statfs()` computes and caches metadata overhead and reports capacity/free inode data.
- Optional quota helpers `ext2_quota_read()`, `ext2_quota_write()`, `ext2_quota_on()`, and `ext2_quota_off()` expose quota file IO without pagecache locking assumptions.

## Control flow

Mount begins in `ext2_init_fs_context()`, which allocates parser state, seeds default reservation behavior for new mounts, or copies current options for reconfigure. `ext2_get_tree()` calls `get_tree_bdev()` with `ext2_fill_super()`. `ext2_fill_super()` then chooses an initial block size, reads the on-disk superblock at `ctx->s_sb_block`, verifies magic, applies parsed/default mount options, rejects unsupported incompat or read-write ro-compat features, handles DAX capability checks, rereads the superblock after block-size adjustment if needed, validates inode size, group sizes, block counts, inode counts, and descriptor placement, allocates descriptor arrays and free-count counters, creates the EA block cache, installs operation tables, reads and validates the root inode, warns for ext3 journal compat, updates mount counts/state, and writes the superblock.

Failure paths unwind in reverse order through labeled exits, releasing descriptor buffers, counters, xattr cache, superblock buffer, DAX references, and `sbi`. Unmount enters `ext2_put_super()`, which disables quotas, destroys the EA cache, restores `s_state` to the saved mount state for clean read-write unmount, syncs the superblock, and frees in-core structures.

Remount via `ext2_reconfigure()` first syncs the filesystem, builds a new option snapshot, refuses live DAX toggles, handles read-write to read-only by suspending quotas and restoring a valid on-disk state when appropriate, handles read-only to read-write by checking ro-compat features and rerunning setup, then commits option and POSIX ACL flag changes under `s_lock`.

## State and persistence behavior

Persistent state is centered on `struct ext2_super_block`: mount state, mount count, free block/inode counters, write time, feature bits, default mount options, reserved uid/gid, and UUID-backed fsid. Group descriptors persist bitmap and inode table locations and free counts maintained elsewhere. In-memory `ext2_sb_info` caches parsed options, descriptor buffers, group counts, overhead computations, reservation windows, percpu counters, xattr cache, DAX references, and lock state. `ext2_sync_fs()` intentionally clears `EXT2_VALID_FS` during normal mounted operation so an unclean shutdown is visible to fsck. `ext2_freeze()` restores the saved valid state only when there are no open unlinked files.

Quota persistence is through hidden quota files, with direct block IO through `ext2_get_block()` and explicit dirtying of quota file buffers and inode metadata. Xattr feature persistence is delegated to `xattr.c`, but this file creates and destroys the per-superblock mbcache and advertises `sb->s_xattr`.

## Dependencies and integration points

This file depends on Linux VFS superblock, inode, mount, `fs_context`, exportfs, quota, DAX, buffer-head, percpu-counter, seq_file, and block-device APIs. It integrates with ext2-specific inode/block helpers from `ext2.h`, xattr handlers from `xattr.h`, ACL mount options from `acl.h`, and NFS export parent lookup via `ext2_get_parent()`. It also surfaces module metadata through `file_system_type`, `module_init()`, and `module_exit()`.

## Risks and edge cases

The highest-risk paths are mount-time validation and remount transitions. Bad geometry, descriptor table locations, unsupported feature bits, invalid inode size, too-small groups, or device-size mismatches must fail before operation tables are exposed. `sb=` is ignored on remount by design, so tests must not expect it to move the superblock after initial mount. DAX is deprecated for ext2 and is disabled if the block device or block size is unsuitable. Error handling changes persistent state immediately, so `errors=panic`, `errors=remount-ro`, and failed superblock writes have visible operational consequences. Quota file IO bypasses normal pagecache expectations and depends on quota serialization.

## Test signals

Useful signals include mounting valid and deliberately malformed ext2 images; exercising rev0 images with feature bits; read-only and read-write mounts with unsupported ro-compat/incompat flags; DAX-capable and non-DAX devices; `errors=` behavior after injected metadata errors; freeze/unfreeze with and without unlinked open files; remount read-only/read-write with quota state; `statfs` overhead under sparse-super and non-sparse layouts; NFS file-handle stale generation checks; and quota read/write paths over holes, partial blocks, and sync inodes.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ext2/super.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ext2/symlink.c -->
# sources/distributed-fs/ceph-client/fs/ext2/symlink.c

## Purpose

`fs/ext2/symlink.c` declares the inode operation tables used for ext2 symlinks. Modern symlink body handling is generic; this file only selects the correct `get_link` strategy for page-backed symlinks versus ext2 fast symlinks whose target is stored inline in the inode block array.

## Important APIs, types, and functions

- `ext2_symlink_inode_operations` uses `page_get_link` for normal symlinks whose content is in pagecache-backed file data.
- `ext2_fast_symlink_inode_operations` uses `simple_get_link` for fast symlinks where the target is available directly from inode-private memory.
- Both operation tables share `ext2_getattr`, `ext2_setattr`, and `ext2_listxattr`, so attribute changes and xattr listing behavior are consistent across both symlink storage forms.

## Control flow

The inode instantiation path in other ext2 code chooses one of these tables based on whether a symlink is fast or normal. VFS link resolution calls `.get_link`; generic code either obtains a page-backed target or returns the inline target. VFS stat and chmod/chown/truncate-style metadata operations flow to `ext2_getattr()` and `ext2_setattr()`, and listxattr delegates to ext2 xattr handling when compiled in.

## State and persistence behavior

This file does not write persistent state directly. Persistence is determined by the inode format chosen elsewhere: normal symlink target data is stored in data blocks/pages, while fast symlink bytes are stored inside ext2 inode block fields. Attribute and xattr persistence is delegated to ext2 inode and xattr code.

## Dependencies and integration points

The file includes `ext2.h` for ext2 inode attribute helpers and `xattr.h` for `ext2_listxattr`. Its exported constants are consumed by inode setup code that assigns `inode->i_op`.

## Risks and edge cases

Correctness depends on assigning the matching operation table to the matching on-disk symlink format. A fast symlink routed through `page_get_link` or a normal symlink routed through `simple_get_link` would expose wrong or missing link targets. Optional xattr support changes whether `.listxattr` is a real function or `NULL` through `xattr.h`.

## Test signals

Create and read short fast symlinks and longer block-backed symlinks, run `lstat`, `readlink`, `chmod/chown` where allowed, list xattrs on symlinks with xattrs enabled/disabled, and verify targets survive unmount/remount.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ext2/symlink.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ext2/trace.c -->
# sources/distributed-fs/ceph-client/fs/ext2/trace.c

## Purpose

`fs/ext2/trace.c` is the tracepoint definition translation unit for ext2. It defines `CREATE_TRACE_POINTS` before including `trace.h`, causing the trace event declarations in the header to instantiate their storage and registration metadata exactly once.

## Important APIs, types, and functions

- `CREATE_TRACE_POINTS` selects tracepoint definition mode for Linux trace headers.
- `trace.h` provides the ext2 direct-I/O trace event classes and concrete events.
- `<linux/uio.h>` is included so trace prototypes involving `struct iov_iter` are visible.

## Control flow

There is no runtime control flow in this file. Build-time inclusion expands trace macros into generated tracepoint objects. Runtime calls from ext2 direct-I/O code invoke the tracepoints declared in `trace.h` and instantiated here.

## State and persistence behavior

Tracepoints are in-memory instrumentation hooks only. They do not alter filesystem state or persistence. They expose transient IO parameters and return values to ftrace/perf-style consumers when enabled.

## Dependencies and integration points

This file depends on the Linux tracepoint macro system and must be compiled into the ext2 object set whenever the matching trace declarations are referenced. Its include ordering and `TRACE_INCLUDE_*` settings in `trace.h` are important for generated trace code.

## Risks and edge cases

The main risk is ODR-like tracepoint misuse: defining `CREATE_TRACE_POINTS` in more than one translation unit would duplicate symbols, while omitting this file would leave tracepoint references unresolved. Prototype drift between trace callers and `trace.h` would be caught at compile time.

## Test signals

Build ext2 with tracing enabled, verify tracepoint symbols are present under tracing events, enable ext2 direct-I/O trace events, run direct reads/writes, and confirm event payload fields are populated.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ext2/trace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ext2/trace.h -->
# sources/distributed-fs/ceph-client/fs/ext2/trace.h

## Purpose

`fs/ext2/trace.h` declares ext2 tracepoints for direct-I/O read and write paths. It uses the Linux trace event macro language to record inode, device, file size, IO position, request length, kiocb flags, async/sync mode, and return status around direct-I/O operations.

## Important APIs, types, and functions

- `TRACE_SYSTEM ext2` names the trace subsystem.
- `DECLARE_EVENT_CLASS(ext2_dio_class, ...)` defines the common payload for most direct-I/O events using `struct kiocb`, `struct iov_iter`, and an `ssize_t ret`.
- `DEFINE_DIO_RW_EVENT()` instantiates `ext2_dio_write_begin`, `ext2_dio_write_end`, `ext2_dio_write_buff_end`, `ext2_dio_read_begin`, and `ext2_dio_read_end`.
- `TRACE_EVENT(ext2_dio_write_endio, ...)` adds an end-IO-specific event with completed size and integer return value.
- `TP_fast_assign` derives `dev`, `ino`, `isize`, `pos`, `count` or `size`, `ki_flags`, `aio`, and `ret`.
- `TP_printk` formats device major/minor, inode, size, position, length, IOCB flag strings, async status, and return value.

## Control flow

The header is normally included by trace callers in declaration mode and once by `trace.c` in definition mode. At runtime, ext2 direct-I/O paths call generated `trace_ext2_*` helpers. When disabled, tracepoints are low-overhead static keys; when enabled, the fast assignment code snapshots the current IO state and emits formatted records.

## State and persistence behavior

Trace payloads are transient diagnostic records. They do not persist to ext2 media and do not mutate ext2 state. They do expose live inode size and kiocb state at the time the tracepoint is hit, which is useful for debugging races and partial IO behavior.

## Dependencies and integration points

The header depends on `<linux/tracepoint.h>`, `TRACE_IOCB_STRINGS` from kernel tracing helpers, VFS `file_inode()`, kiocb state, and `iov_iter_count()`. `TRACE_INCLUDE_PATH .` and `TRACE_INCLUDE_FILE trace` make generated trace code locate this file from the ext2 build directory.

## Risks and edge cases

Tracepoint ABI names are externally visible to tracing scripts. Renaming events or fields can break diagnostics even though filesystem behavior is unchanged. Values such as `i_size` and `ki_pos` are sampled without locking beyond caller context, so consumers should treat them as observational data rather than synchronization. The class assumes `iocb->ki_filp` is valid.

## Test signals

Compile-test with tracing, enable each ext2 direct-I/O tracepoint, perform direct reads/writes including async and sync kiocb paths, verify IOCB flags print correctly, and check that error/short-IO return values appear in begin/end/endio event streams.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ext2/trace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ext2/xattr.c -->
# sources/distributed-fs/ceph-client/fs/ext2/xattr.c

## Purpose

`fs/ext2/xattr.c` implements ext2 extended attributes stored in external EA blocks referenced by `EXT2_I(inode)->i_file_acl`. It provides VFS xattr get/list/set/delete behavior, validates the ext2 EA block format, shares identical EA blocks across inodes through mbcache and on-disk refcounts, updates the ext2 compat feature bit, and frees EA blocks during inode deletion.

## Important APIs, types, and functions

- `ext2_xattr_handler_map` maps on-disk name indexes to Linux xattr handlers for `user`, POSIX ACL pseudo-handlers, `trusted`, and optional `security`.
- `ext2_xattr_handlers` is installed into `sb->s_xattr` by `super.c`.
- `ext2_xattr_get()` reads a named attribute, validates the header and each entry, searches sorted entries with `ext2_xattr_cmp_entry()`, inserts the block into mbcache, and copies or sizes the value.
- `ext2_listxattr()` and `ext2_xattr_list()` validate the block and emit visible names with prefixes only when `xattr_handler_can_list()` allows them.
- `ext2_xattr_set()` creates, replaces, or removes one attribute, using `XATTR_CREATE` and `XATTR_REPLACE` semantics, quota initialization, `xattr_sem`, sorted entry insertion/removal, value compaction, and copy-on-write when a shared block cannot be modified in place.
- `ext2_xattr_set2()` commits a prepared block by reusing an identical cached block, keeping an exclusive old block, allocating a new block, updating inode `i_file_acl`, dirtying metadata, and releasing the old block.
- `ext2_xattr_release_block()` decrements a shared block refcount or frees an exclusive EA block, synchronized against cache reuse.
- `ext2_xattr_delete_inode()` releases the inode's EA block during inode eviction after validating block range and header.
- `ext2_xattr_cache_insert()`, `ext2_xattr_cache_find()`, `ext2_xattr_cmp()`, `ext2_xattr_hash_entry()`, and `ext2_xattr_rehash()` implement deduplication by content hash plus full block comparison.
- `ext2_xattr_create_cache()` and `ext2_xattr_destroy_cache()` manage the per-superblock mbcache.

## Control flow

Get/list paths acquire `xattr_sem` for reading, read `i_file_acl` with `sb_bread()`, validate `EXT2_XATTR_MAGIC`, single-block layout, entry bounds, value offsets, and non-external values, then search or list entries. Set paths initialize quotas, acquire `xattr_sem` for writing, read the existing block if present, locate the insertion point in sorted order, compute available free space, enforce create/replace/remove rules, and either modify an exclusive uncached block under lock or clone/allocate a scratch block. The update phase rehashes the block unless empty, then `ext2_xattr_set2()` deduplicates or allocates the final block and points the inode at it.

When deleting an inode, the code uses `down_write_trylock()` because reclaim lockdep contexts are sensitive, reads the EA block if one exists, checks it is a valid data block, validates the header, releases/free-refcounts it, and clears `i_file_acl`.

## State and persistence behavior

Persistent EA state consists of an external block containing `struct ext2_xattr_header`, sorted `struct ext2_xattr_entry` records, value bytes packed from the block end, block-level hash, entry hashes, and refcount. The inode persists the EA block number in `i_file_acl`. The superblock compat feature `EXT2_FEATURE_COMPAT_EXT_ATTR` is set on first new EA block allocation through `ext2_xattr_update_super_block()`, which may upgrade the filesystem revision. In-memory state includes `xattr_sem`, mbcache entries keyed by hash/block number, and buffer-head verified/dirty state.

## Dependencies and integration points

The file integrates with ext2 block allocation/free (`ext2_new_blocks()`, `ext2_free_blocks()`), data block validation, inode dirtying, synchronous inode metadata writes, quota accounting, VFS xattr handlers, POSIX ACL handlers, security labels, mbcache, buffer-head IO, and superblock feature update helpers from `super.c`. Namespace-specific handlers in `xattr_user.c`, `xattr_trusted.c`, and `xattr_security.c` call into these generic routines.

## Risks and edge cases

EA block validation is security critical because offsets and lengths come from disk. Bad headers, value blocks, out-of-range offsets, and malformed entry chains must produce `-EIO` and mark errors rather than overrun memory. Shared-block refcounting is subtle: in-place modification is allowed only for exclusive blocks that are not concurrently being reused through mbcache. Cache hash collisions are handled by full block compare. Quota accounting must match refcount increments, decrements, allocations, and frees. Synchronous inodes require dirty buffer and inode metadata errors to be propagated carefully, including the special ENOSPC cleanup behavior.

## Test signals

Test get/list/set/remove for user/trusted/security/ACL namespaces; create vs replace flag errors; maximum name and value lengths; empty block removal; repeated identical xattr sets across many inodes to exercise shared blocks; mutation of one inode after sharing to verify copy-on-write; inode deletion freeing or decrementing EA blocks; corruption tests for header magic, refcount, offsets, padding, external value block, and bad `i_file_acl`; quota exhaustion; sync inode writeback errors; and superblock feature-bit updates on old revision filesystems.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ext2/xattr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ext2/xattr.h -->
# sources/distributed-fs/ceph-client/fs/ext2/xattr.h

## Purpose

`fs/ext2/xattr.h` defines the ext2 on-disk extended attribute block format, namespace indexes, alignment helpers, and public xattr API declarations or stubs. It is the contract shared by ext2 xattr storage, namespace handlers, ACL/security initialization, inode teardown, symlink xattr listing, and superblock setup.

## Important APIs, types, and constants

- `EXT2_XATTR_MAGIC` identifies valid EA blocks.
- `EXT2_XATTR_REFCOUNT_MAX` caps sharing of one identical EA block.
- `EXT2_XATTR_INDEX_USER`, `EXT2_XATTR_INDEX_POSIX_ACL_ACCESS`, `EXT2_XATTR_INDEX_POSIX_ACL_DEFAULT`, `EXT2_XATTR_INDEX_TRUSTED`, `EXT2_XATTR_INDEX_LUSTRE`, and `EXT2_XATTR_INDEX_SECURITY` define on-disk namespaces.
- `struct ext2_xattr_header` stores magic, refcount, block count, aggregate hash, and reserved fields.
- `struct ext2_xattr_entry` stores name length/index, value offset, external value block field, value size, entry hash, and inline flexible name.
- `EXT2_XATTR_LEN()`, `EXT2_XATTR_NEXT()`, and `EXT2_XATTR_SIZE()` encode 4-byte alignment for entries and values.
- When `CONFIG_EXT2_FS_XATTR` is enabled, the header declares handlers, `ext2_listxattr()`, `ext2_xattr_get()`, `ext2_xattr_set()`, `ext2_xattr_delete_inode()`, cache create/destroy helpers, and `ext2_xattr_handlers`.
- When disabled, inline stubs return `-EOPNOTSUPP`, do nothing for delete/cache destroy, and set operation pointers to `NULL`.
- `ext2_init_security()` is declared or stubbed depending on `CONFIG_EXT2_FS_SECURITY`.

## Control flow

The macros are used by `xattr.c` to iterate the variable-length entry table and calculate required free space. Build-time configuration controls whether callers link to real xattr routines or no-op stubs. Inode creation paths can call `ext2_init_security()` unconditionally because the header supplies a zero-return stub when security xattrs are unavailable.

## State and persistence behavior

This header defines persistent byte layout and alignment, so changes would affect disk compatibility. It intentionally represents only one-block EA storage: `h_blocks` must be one in validation code and `e_value_block` is not implemented for external value blocks. The function stubs affect in-memory feature availability but do not change on-disk existing xattr data.

## Dependencies and integration points

It includes Linux xattr declarations, depends on `struct inode`, `struct dentry`, `struct mb_cache`, and xattr handler types, and is included by ext2 superblock, symlink, ACL, security, trusted, user, and generic xattr code.

## Risks and edge cases

Alignment macros must remain consistent with on-disk parsing. Namespace index values are persistent and cannot be renumbered. The disabled-xattr stubs should match caller expectations, especially returning `-EOPNOTSUPP` rather than `-ENODATA`. The Lustre index is defined even though this subset does not provide a handler, so list/get behavior depends on handler-map coverage.

## Test signals

Compile with xattrs enabled and disabled, security enabled and disabled, and POSIX ACL enabled/disabled. Validate macro calculations for short and long names and values, ensure disabled builds produce no xattr handlers, and mount images with existing xattr blocks to confirm layout compatibility.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ext2/xattr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ext2/xattr_security.c -->
# sources/distributed-fs/ceph-client/fs/ext2/xattr_security.c

## Purpose

`fs/ext2/xattr_security.c` implements the `security.*` xattr namespace for ext2 and integrates inode creation with Linux Security Module label initialization. It is compiled when ext2 security xattrs are enabled.

## Important APIs, types, and functions

- `ext2_xattr_security_get()` calls `ext2_xattr_get()` with `EXT2_XATTR_INDEX_SECURITY`.
- `ext2_xattr_security_set()` calls `ext2_xattr_set()` with the security namespace index.
- `ext2_initxattrs()` iterates an LSM-provided `struct xattr` array and writes each label into ext2 xattrs.
- `ext2_init_security()` calls `security_inode_init_security()` with `ext2_initxattrs()` as the filesystem writer callback.
- `ext2_xattr_security_handler` publishes the `XATTR_SECURITY_PREFIX`, get, and set callbacks to VFS xattr dispatch.

## Control flow

VFS xattr operations on `security.*` dispatch through the handler into generic ext2 xattr storage. Inode creation paths call `ext2_init_security()`, which asks the LSM to compute initial labels for the new inode and parent/name context; the callback then writes each returned label with normal ext2 xattr set semantics.

## State and persistence behavior

Security labels persist in the same external EA blocks managed by `xattr.c`, under namespace index `EXT2_XATTR_INDEX_SECURITY`. This file does not add separate state. LSM-provided labels are persisted before or during inode creation depending on the caller path.

## Dependencies and integration points

The file depends on Linux security hooks, VFS xattr handler registration, and ext2 generic xattr storage. It is referenced by `xattr.h` and included in ext2 handler arrays only under the relevant configuration.

## Risks and edge cases

Partial initialization is possible if an LSM returns multiple xattrs and a later write fails; callers must handle the returned error. Security namespace availability is build-time controlled, so images with security labels mounted on a kernel without this option cannot expose them through handlers. The handler does not perform additional permission checks itself; it relies on VFS/LSM xattr policy.

## Test signals

Create files on SELinux or another security-module-enabled system, verify labels are set at creation, get/set `security.*` labels, inject ENOSPC during label writes, and compile/mount with `CONFIG_EXT2_FS_SECURITY` disabled to confirm graceful absence.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ext2/xattr_security.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ext2/xattr_trusted.c -->
# sources/distributed-fs/ceph-client/fs/ext2/xattr_trusted.c

## Purpose

`fs/ext2/xattr_trusted.c` implements the ext2 `trusted.*` xattr namespace. Trusted attributes are intended for privileged kernel/user-space consumers and are visible in listxattr only to callers with `CAP_SYS_ADMIN`.

## Important APIs, types, and functions

- `ext2_xattr_trusted_list()` returns true only for `capable(CAP_SYS_ADMIN)`.
- `ext2_xattr_trusted_get()` and `ext2_xattr_trusted_set()` call the generic ext2 xattr engine with `EXT2_XATTR_INDEX_TRUSTED`.
- `ext2_xattr_trusted_handler` publishes `XATTR_TRUSTED_PREFIX`, list, get, and set callbacks.

## Control flow

VFS dispatch selects this handler for names under `trusted.`. Listing checks capability through the `.list` callback. Get and set operations delegate to `ext2_xattr_get()` and `ext2_xattr_set()`, which perform storage validation, locking, allocation, and persistence.

## State and persistence behavior

Trusted attributes persist in ext2 external EA blocks under the trusted namespace index. No independent state is stored in this file. Visibility during list operations is dynamic and depends on caller credentials, not on-disk bits.

## Dependencies and integration points

The file depends on Linux capabilities, VFS xattr handlers, `xattr.h` namespace definitions, and the generic ext2 xattr storage implementation. Its handler is included in `ext2_xattr_handlers` when ext2 xattrs are enabled.

## Risks and edge cases

Capability gating only affects listing here; get/set permission enforcement also involves VFS xattr policy. Tests must distinguish "not listed" from "not present." Storage errors and malformed EA blocks propagate from `xattr.c`.

## Test signals

List `trusted.*` attributes as privileged and unprivileged callers, get/set/remove trusted attributes, verify persistence after remount, and exercise malformed EA block handling through this namespace.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ext2/xattr_trusted.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ext2/xattr_user.c -->
# sources/distributed-fs/ceph-client/fs/ext2/xattr_user.c

## Purpose

`fs/ext2/xattr_user.c` implements ext2 `user.*` xattr namespace handling. It gates user attributes on the `XATTR_USER` mount option and delegates actual storage to the generic ext2 xattr block implementation.

## Important APIs, types, and functions

- `ext2_xattr_user_list()` returns whether `test_opt(dentry->d_sb, XATTR_USER)` is enabled.
- `ext2_xattr_user_get()` rejects access with `-EOPNOTSUPP` when the mount option is disabled, otherwise calls `ext2_xattr_get()` with `EXT2_XATTR_INDEX_USER`.
- `ext2_xattr_user_set()` applies the same mount-option gate before calling `ext2_xattr_set()`.
- `ext2_xattr_user_handler` publishes `XATTR_USER_PREFIX`, list, get, and set callbacks.

## Control flow

VFS dispatch for `user.*` names reaches this handler. The list/get/set paths check the current superblock mount option. If enabled, they pass through to generic xattr code, including create/replace/remove flag handling and EA block allocation.

## State and persistence behavior

User attributes persist in external EA blocks under `EXT2_XATTR_INDEX_USER`. The mount option only controls exposure and mutation; existing on-disk user attributes can remain present while inaccessible if the filesystem is mounted with `nouser_xattr`.

## Dependencies and integration points

This file depends on ext2 mount-option state from `super.c`, VFS xattr handler dispatch, and generic ext2 xattr storage. `ext2_show_options()` reports `user_xattr` or `nouser_xattr` based on defaults and parsed options.

## Risks and edge cases

Behavior differs between "attribute absent" and "namespace disabled." Callers should see `-EOPNOTSUPP` when the namespace is disabled, not `-ENODATA`. Remounting with option changes can alter accessibility without changing on-disk content.

## Test signals

Mount with `user_xattr` and `nouser_xattr`, verify set/get/list behavior and error codes, remount toggling the option with existing attributes, and combine user xattrs with quota and ENOSPC injection to cover delegated storage paths.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ext2/xattr_user.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ext4/Kconfig -->
# sources/distributed-fs/ceph-client/fs/ext4/Kconfig

## Purpose

`fs/ext4/Kconfig` declares build-time configuration options for the ext4 filesystem, optional use of ext4 as the ext2 driver, POSIX ACL support, security labels, runtime debug support, and ext4 KUnit tests.

## Important APIs, types, and functions

- `config EXT4_FS` is the main tristate and selects `BUFFER_HEAD`, `JBD2`, `CRC16`, `CRC32`, `FS_IOMAP`, and `FS_ENCRYPTION_ALGS` when fs encryption is enabled.
- `config EXT4_USE_FOR_EXT2` allows ext4 to mount ext2 filesystems when the standalone ext2 driver is disabled.
- `config EXT4_FS_POSIX_ACL` selects `FS_POSIX_ACL` and controls inclusion of `acl.o`.
- `config EXT4_FS_SECURITY` enables security-label xattr support.
- `config EXT4_DEBUG` enables dynamic-debug-friendly ext4 debug messages.
- `config EXT4_KUNIT_TESTS` builds ext4 KUnit objects when ext4 and KUnit are enabled or `KUNIT_ALL_TESTS` selects them.

## Control flow

Kconfig has no runtime control flow. During kernel configuration it constrains which symbols can be selected, which dependencies are pulled in, and which source files the Makefile compiles. The resulting `CONFIG_*` symbols control conditional compilation throughout ext4 headers and sources.

## State and persistence behavior

These options do not persist filesystem state directly, but they change runtime capabilities. For example, ACL/security support controls whether existing on-disk xattrs are surfaced through standard handlers, encryption support controls whether `crypto.o` is built, and `EXT4_USE_FOR_EXT2` changes which driver handles ext2 images.

## Dependencies and integration points

The file integrates with the kernel Kconfig system, ext4 `Makefile`, xattr/ACL/security/crypto sources, JBD2 journaling, iomap, buffer-head IO, CRC libraries, and KUnit. Its help text documents on-disk compatibility expectations for ext3/ext4 features.

## Risks and edge cases

Configuration combinations matter. `EXT4_USE_FOR_EXT2` depends on `EXT2_FS=n` to avoid driver conflicts. Disabling ACL or security support can make on-disk metadata inaccessible through normal interfaces even if bytes remain present. KUnit tests are gated away from production by default but can be selected globally.

## Test signals

Run config matrix builds for built-in, module, and disabled ext4; enable/disable ACL, security, encryption, verity, and KUnit; verify Makefile object inclusion follows the symbols; and boot/mount ext2/ext3/ext4 images with `EXT4_USE_FOR_EXT2` combinations.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ext4/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ext4/Makefile -->
# sources/distributed-fs/ceph-client/fs/ext4/Makefile

## Purpose

`fs/ext4/Makefile` defines how the ext4 kernel object is assembled from core source files and optional feature objects. It is the build-system map from `CONFIG_EXT4_*`, `CONFIG_FS_VERITY`, and `CONFIG_FS_ENCRYPTION` to compiled code.

## Important APIs, types, and functions

- `obj-$(CONFIG_EXT4_FS) += ext4.o` builds ext4 as built-in or module based on the main Kconfig symbol.
- `ext4-y` lists core objects, including block allocation, bitmap, block validity, directories, journaling glue, extents, file operations, fsmap, fsync, hash, inode allocation, indirect blocks, inline data, ioctl, mballoc, migration, MMP, move extent, namei, page IO, readpage, resize, superblock, symlink, sysfs, xattrs, fast commit, and orphan handling.
- `ext4-$(CONFIG_EXT4_FS_POSIX_ACL) += acl.o`.
- `ext4-$(CONFIG_EXT4_FS_SECURITY) += xattr_security.o`.
- `ext4-test-objs` and `obj-$(CONFIG_EXT4_KUNIT_TESTS)` build ext4 KUnit tests.
- `ext4-$(CONFIG_FS_VERITY) += verity.o` and `ext4-$(CONFIG_FS_ENCRYPTION) += crypto.o`.

## Control flow

There is no runtime control flow. Kbuild concatenates object lists according to config symbols and links them into `ext4.o` or `ext4.ko`. Optional files contribute symbols that core ext4 code references through conditional compilation.

## State and persistence behavior

The Makefile does not manage state directly, but object inclusion controls available runtime features and therefore how persistent ext4 metadata is interpreted. Encryption contexts need `crypto.o`; verity metadata needs `verity.o`; ACL/security xattrs need their handlers.

## Dependencies and integration points

The file is coupled to `Kconfig`, ext4 source file names, and Kbuild conventions for composite objects. It also lists KUnit test object composition separately from the production ext4 object.

## Risks and edge cases

Missing an object from `ext4-y` can produce link failures or silently remove feature support. Adding a config-gated source without matching Kconfig dependencies can leave unresolved symbols in some build matrices. Test object lists must not be linked into production ext4 unless KUnit is selected.

## Test signals

Build ext4 built-in and as a module across ACL/security/encryption/verity/KUnit combinations, verify expected symbols are present, and run `modinfo` or link-map checks for optional object inclusion.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ext4/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ext4/acl.c -->
# sources/distributed-fs/ceph-client/fs/ext4/acl.c

## Purpose

`fs/ext4/acl.c` implements POSIX ACL support for ext4 using xattrs as the persistent storage format. It converts between ext4's on-disk ACL encoding and Linux `struct posix_acl`, retrieves ACLs through ext4 xattr get, sets ACLs transactionally through ext4 xattr set, updates inode mode for access ACL changes, and initializes inherited ACLs for new inodes.

## Important APIs, types, and functions

- `ext4_acl_from_disk()` validates ACL header version, counts entries, allocates a `posix_acl`, converts little-endian tags/perms/ids, and rejects malformed sizes or tags.
- `ext4_acl_to_disk()` serializes a `posix_acl` into ext4 ACL header plus short/full entries.
- `ext4_get_acl()` implements inode `get_posix_acl`, rejects RCU mode with `-ECHILD`, maps access/default types to xattr indexes, fetches the xattr, and converts it.
- `__ext4_set_acl()` maps ACL type to xattr name index, rejects default ACLs on non-directories, serializes the ACL, calls `ext4_xattr_set_handle()`, and updates the inode ACL cache.
- `ext4_set_acl()` performs quota initialization, computes xattr journal credits, starts an `EXT4_HT_XATTR` transaction, optionally calls `posix_acl_update_mode()`, sets the ACL xattr, marks inode dirty if mode changed, stops the journal, and retries ENOSPC through `ext4_should_retry_alloc()`.
- `ext4_init_acl()` uses `posix_acl_create()` to inherit/default ACLs during new inode creation and stores them with `XATTR_CREATE`.

## Control flow

ACL reads perform a size query, allocate an exact buffer, read the xattr value, then parse it. ACL writes run inside a journal transaction. For access ACLs, VFS permission semantics can require inode mode changes; the code computes the new mode before setting the xattr and marks the inode dirty in the same transaction. New inode initialization is called while inode creation already owns an ext4 journal handle, so `__ext4_set_acl()` is used directly without starting a nested transaction.

## State and persistence behavior

Persistent ACLs are xattrs under `EXT4_XATTR_INDEX_POSIX_ACL_ACCESS` and `EXT4_XATTR_INDEX_POSIX_ACL_DEFAULT` with `EXT4_ACL_VERSION`. In-memory ACLs are cached in `inode->i_acl` and `inode->i_default_acl` via `set_cached_acl()` or explicit NULL assignment during initialization. Access ACL writes may persist both an xattr and an inode mode change atomically through JBD2.

## Dependencies and integration points

The file depends on POSIX ACL core helpers, ext4 xattr credit calculation and set/get APIs, JBD2 transaction handles, quota initialization, ext4 inode dirtying, idmapped mount mode update support through `mnt_idmap`, and allocation retry logic from `balloc.c`.

## Risks and edge cases

Malformed ACL xattrs must be rejected without reading beyond the buffer. UID/GID conversion uses `init_user_ns`, so id translation assumptions are explicit. Default ACLs on non-directories return `-EACCES` unless clearing. Journal credit calculation must cover serialized ACL size, and ENOSPC retry must not repeat non-ENOSPC errors. If xattr setting succeeds but mode dirtying fails, callers see an error after partial metadata changes in a journal context.

## Test signals

Test get/set/remove access and default ACLs, default ACL rejection on regular files, ACL inheritance during create, mode updates from access ACL changes, malformed ACL xattr sizes/tags/version, quota initialization failures, ENOSPC retry, idmapped chmod/ACL interactions, remount with ACL support disabled, and crash recovery around ACL plus mode updates.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ext4/acl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ext4/acl.h -->
# sources/distributed-fs/ceph-client/fs/ext4/acl.h

## Purpose

`fs/ext4/acl.h` defines ext4's on-disk POSIX ACL structures, version, size/count helpers, and conditional prototypes or stubs for ACL operations. It is the format contract used by `acl.c` and inode operation tables.

## Important APIs, types, and constants

- `EXT4_ACL_VERSION` is the on-disk ACL format version.
- `ext4_acl_entry` stores tag, permission, and uid/gid id for named user/group entries.
- `ext4_acl_entry_short` stores tag and permission for owner/group/mask/other entries that do not need an id.
- `ext4_acl_header` stores the little-endian version.
- `ext4_acl_size(count)` computes serialized size, using short entries for up to the first four entries and full entries thereafter.
- `ext4_acl_count(size)` validates a serialized size and returns the number of entries or `-1`.
- With `CONFIG_EXT4_FS_POSIX_ACL`, it declares `ext4_get_acl()`, `ext4_set_acl()`, and `ext4_init_acl()`. Without it, get/set pointers become `NULL` and `ext4_init_acl()` is a zero-return stub.

## Control flow

The inline helpers are used before allocating ACL buffers and while parsing xattr values. Conditional compilation lets ext4 code call `ext4_init_acl()` unconditionally during inode creation while operation tables only expose get/set ACL callbacks when support exists.

## State and persistence behavior

The header's structures define persistent ACL xattr bytes. The size/count helpers encode ext4's compact ACL layout, where the common first four ACL entries do not store ids unless the serialized entry type requires it. Disabled ACL builds do not remove on-disk data but do prevent standard ACL operations from interpreting it.

## Dependencies and integration points

The header includes `<linux/posix_acl_xattr.h>` and depends on ext4 transaction handle types through prototypes. It is included by ACL implementation, super/inode operation setup, and new inode creation paths.

## Risks and edge cases

`ext4_acl_count()` mutates an unsigned `size` after subtracting the header, so callers must only pass sizes already checked by parsing code. The "first four short entries" assumption is tied to POSIX ACL canonical ordering; malformed noncanonical ACLs are rejected later by tag validation and core ACL checks. Persistent struct layout cannot change without format impact.

## Test signals

Unit-test `ext4_acl_size()` and `ext4_acl_count()` for zero, one to four, and many entries; malformed byte counts; ACL-disabled builds; and parsing/serializing round trips through `acl.c`.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ext4/acl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ext4/balloc.c -->
# sources/distributed-fs/ceph-client/fs/ext4/balloc.c

## Purpose

`fs/ext4/balloc.c` provides ext4 block-group/block-allocation support routines used by mballoc, metadata allocation, mount accounting, bitmap validation, and filesystem statistics. In this subset it covers group/block mapping, overhead calculation, lazy bitmap initialization, group descriptor lookup, block bitmap read/verify/wait, free-cluster reservation checks, allocation retry policy, metadata block allocation, free cluster counting, sparse-super/GDT placement, and inode goal-block selection.

## Important APIs, types, and functions

- `ext4_get_group_number()` and `ext4_get_group_no_and_offset()` map physical blocks to block groups and cluster offsets.
- `ext4_free_clusters_after_init()` and `ext4_num_overhead_clusters()` calculate free clusters for uninitialized bitmaps by subtracting superblock/GDT, bitmap, and inode-table metadata.
- `ext4_init_block_bitmap()` materializes an uninitialized group bitmap and sets metadata/padding bits after descriptor checksum verification.
- `ext4_get_group_desc()` safely indexes the RCU-managed group descriptor buffer array and returns a descriptor pointer.
- `ext4_get_group_info()` returns in-memory mballoc group info.
- `ext4_read_block_bitmap_nowait()`, `ext4_wait_block_bitmap()`, and `ext4_read_block_bitmap()` fetch and validate a block bitmap, handling uninitialized bitmap groups, async reads, readahead, checksum verification, padding verification, and corruption marking.
- `ext4_validate_block_bitmap()` combines checksum, required metadata bit checks, and padding checks under group lock.
- `ext4_claim_free_clusters()` and `ext4_has_free_clusters()` reserve dirty clusters after accounting for free, dirty, root-reserved, and delayed-reserved pools.
- `ext4_should_retry_alloc()` decides whether ENOSPC allocation should retry after journal commit or discard work.
- `ext4_new_meta_blocks()` allocates metadata clusters through mballoc and accounts delayed-allocation reserved quota.
- `ext4_count_free_clusters()` sums descriptor free-cluster counts, skipping bitmap-corrupt groups.
- `ext4_bg_has_super()`, `ext4_bg_num_gdb()`, `ext4_num_base_meta_blocks()`, and helpers model sparse-super, sparse-super2, meta_bg, and reserved GDT placement.
- `ext4_inode_to_goal_block()` picks allocation locality from inode group, flex_bg policy, delayed allocation, and process-coloring.

## Control flow

Bitmap read starts with descriptor lookup and bitmap block range validation. If the buffer is locked and the caller is only prefetching, it returns `NULL`. If the buffer is already uptodate, validation runs immediately. Otherwise it locks the buffer, handles checksum-protected uninitialized groups by creating the bitmap in memory, or submits metadata IO with `ext4_read_bh_nowait()`. Synchronous callers then wait, check IO success, clear `buffer_new`, and validate.

Allocation admission reads percpu counters quickly, falls back to summed counters near watermark, and allows reserved block use for root/reserved users, explicit root-block flags, `CAP_SYS_RESOURCE`, or `EXT4_MB_USE_RESERVED`. ENOSPC retry is journaling-aware: without a journal it does not retry; with pending frees it forces a nested commit up to three times, and with no pending frees it may flush discard work and recheck free clusters.

## State and persistence behavior

Persistent state includes group descriptors, block bitmap blocks, inode bitmap/table locations, descriptor checksums, free-cluster counts, backup superblocks, and group descriptor table backups. In-memory state includes group descriptor buffer arrays, group info corruption flags, percpu free/dirty cluster counters, reservation counters, journal state, discard work state, and buffer flags such as uptodate/verified/new. Lazy block bitmap initialization changes buffer contents in memory and later persistence is coordinated by callers.

## Dependencies and integration points

The file depends on ext4 superblock/group descriptor layout, mballoc APIs, JBD2 journaling, buffer-head IO, block bitmap checksum helpers in `bitmap.c`, tracepoints from `<trace/events/ext4.h>`, KUnit static stubs, quota accounting, capability checks, flex_bg helpers, and simulated failure hooks. Many higher-level ext4 paths call these helpers indirectly through mballoc and metadata allocation.

## Risks and edge cases

Bitmap validation is critical because a missing metadata bit can allow allocation over filesystem metadata. Flex_bg intentionally skips local bitmap metadata checks because metadata can live outside the group, so corruption detection differs by feature. Last group sizes, bigalloc cluster conversion, meta_bg/sparse_super2 placement, and reserved GDT accounting are all geometry-sensitive. RCU descriptor access assumes buffer lifetime rules held by the broader superblock state. Free-space admission depends on approximate percpu counters and must account dirty clusters to avoid overcommit.

## Test signals

Test block-to-group mapping with standard and `STD_GROUP_SIZE` modes, last partial groups, bigalloc clusters, sparse_super/sparse_super2/meta_bg combinations, uninitialized bitmap creation, checksum failure injection, padding-bit corruption, invalid bitmap block numbers, ENOSPC retry with pending journal frees and discard work, reserved block access by root/group/capability, KUnit stubs for bitmap reads/descriptors, and goal block selection for directories, regular files, flex_bg, and delalloc.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ext4/balloc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ext4/bitmap.c -->
# sources/distributed-fs/ceph-client/fs/ext4/bitmap.c

## Purpose

`fs/ext4/bitmap.c` provides small helpers for counting free bits and verifying/updating inode and block bitmap checksums. These functions are used by allocation, inode allocation, group descriptor maintenance, and mount/debug accounting.

## Important APIs, types, and functions

- `ext4_count_free()` returns free bits in a bitmap buffer as total bits minus `memweight()`.
- `ext4_inode_bitmap_csum_verify()` and `ext4_inode_bitmap_csum_set()` verify or store inode bitmap checksums in group descriptor low/high fields.
- `ext4_block_bitmap_csum_verify()` and `ext4_block_bitmap_csum_set()` do the same for block bitmap checksums.

## Control flow

Checksum helpers no-op successfully when metadata checksums are not enabled. Otherwise they compute the checksum over the bitmap's active byte range using `s_csum_seed`, compare it with low 16-bit descriptor fields and optional high 16-bit fields when the descriptor size includes them, or write those fields during update.

## State and persistence behavior

The bitmap bytes are persistent metadata blocks. The checksum fields are persistent group descriptor fields. In-memory state is limited to `struct buffer_head` contents and ext4 superblock checksum seed/descriptor size. Setting a checksum mutates the group descriptor in memory; callers are responsible for journaling/dirtying descriptor metadata.

## Dependencies and integration points

The file depends on ext4 feature checks, group descriptor layout, `EXT4_INODES_PER_GROUP()`, `EXT4_CLUSTERS_PER_GROUP()`, `ext4_chksum()`, and `memweight()`. `balloc.c` uses block bitmap verification before trusting allocation maps; inode allocation code uses the inode bitmap counterparts.

## Risks and edge cases

The checksum byte length must match only valid bitmap bits, not necessarily the full block. Descriptor-size checks determine whether high checksum fields are meaningful; older descriptors compare only 16 bits. Bigalloc affects block bitmap length through clusters per group. Callers must pair checksum updates with descriptor journaling.

## Test signals

Verify checksum pass/fail with metadata_csum enabled and disabled, descriptor sizes with and without high fields, corrupted bitmap bytes, corrupted descriptor checksum fields, bigalloc cluster counts, and free-bit counts for all-zero, all-one, and mixed bitmaps.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ext4/bitmap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ext4/block_validity.c -->
# sources/distributed-fs/ceph-client/fs/ext4/block_validity.c

## Purpose

`fs/ext4/block_validity.c` builds and queries an RCU-protected red-black tree of ext4 filesystem metadata block ranges, called system zones, so file data block references cannot overlap superblocks, group descriptors, bitmaps, inode tables, or journal inode blocks. It is a defense against metadata overwrite caused by corrupted block maps or logic bugs.

## Important APIs, types, and functions

- `struct ext4_system_zone` stores one protected range: start block, count, and owning inode number for special reserved-inode ranges.
- `ext4_init_system_zone()` and `ext4_exit_system_zone()` manage the kmem cache.
- `add_system_zone()` inserts a non-overlapping range into an rb-tree and merges adjacent ranges with the same inode owner.
- `ext4_setup_system_zone()` builds a complete tree for a mounted superblock from every group's base metadata, block bitmap, inode bitmap, inode table, and optional journal inode blocks, then publishes it with `rcu_assign_pointer()`.
- `ext4_release_system_zone()` clears the published pointer and frees the old tree after an RCU grace period.
- `ext4_protect_reserved_inode()` maps a reserved inode such as the journal inode and adds its extents as allowed-only-for-that-inode zones.
- `ext4_sb_block_valid()` checks a block range against filesystem bounds and the system zone tree; if an inode is supplied, overlap is allowed only when the zone owner matches the inode number.
- `ext4_inode_block_valid()` wraps the superblock-level check for an inode.
- `ext4_check_blockref()` validates an array of 32-bit block references and reports corruption through `ext4_error_inode()`.

## Control flow

Mount or remount setup allocates a new `ext4_system_blocks`, iterates groups, and adds protected metadata ranges. Overlaps during construction are corruption unless they can be merged as contiguous same-owner ranges. Journal inode protection maps the journal file through `ext4_map_blocks()` and inserts each mapped extent tagged with the journal inode number. Only after successful construction is the tree published. Readers use `rcu_read_lock()`, walk the rb-tree by range comparisons, and return invalid on any overlap except permitted same-inode reserved zones.

## State and persistence behavior

The rb-tree is in-memory derived state; it is not persisted. Its inputs are persistent ext4 geometry and journal inode extents. The tree pointer in `ext4_sb_info->s_system_blks` is protected by `sb->s_umount` for updates and RCU for readers. Persistent corruption is reported but not repaired here.

## Dependencies and integration points

The file depends on ext4 geometry helpers from allocation code, group descriptor access, journal inode lookup, inode block mapping, rb-tree APIs, RCU, slab cache management, and ext4 error reporting. Indirect block and extent validation code can call `ext4_check_blockref()` or `ext4_inode_block_valid()` before trusting disk block references.

## Risks and edge cases

System-zone construction must cover all metadata placements, including sparse/meta_bg geometry and journal inode extents. Overlapping metadata ranges generally signal corruption and abort setup. RCU publication is essential: remount can disable block validity while readers still walk the old tree. The range check guards against start block before first data block, arithmetic wraparound, and ending beyond filesystem size.

## Test signals

Mount with block validity enabled/disabled, create images with overlapping bitmap/table/super ranges, corrupt indirect block references to metadata blocks, validate journal inode exceptions, test remount toggling under concurrent reads, run with sparse_super/meta_bg/bigalloc layouts, and inject allocation failures during tree construction.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ext4/block_validity.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ext4/crypto.c -->
# sources/distributed-fs/ceph-client/fs/ext4/crypto.c

## Purpose

`fs/ext4/crypto.c` adapts ext4 to the Linux fscrypt framework. It prepares encrypted and casefolded filenames, manages fscrypt filename buffers, exposes the legacy encryption password salt ioctl, stores and retrieves inode encryption contexts through ext4 xattrs, enforces ext4-specific encryption constraints, and publishes `ext4_cryptops`.

## Important APIs, types, and functions

- `ext4_fname_setup_filename()` wraps `fscrypt_setup_filename()`, copies the result into `struct ext4_filename`, and prepares case-insensitive lookup data with `ext4_fname_setup_ci_filename()`.
- `ext4_fname_prepare_lookup()` wraps `fscrypt_prepare_lookup()` for dentry lookup and also prepares casefold state.
- `ext4_fname_free_filename()` frees fscrypt and ext4 casefold filename buffers.
- `ext4_ioctl_get_encryption_pwsalt()` returns `s_encrypt_pw_salt`, generating and journaling a UUID salt in the superblock if it is still zero and encryption is supported.
- `ext4_get_context()` reads `EXT4_XATTR_NAME_ENCRYPTION_CONTEXT` from the encryption xattr namespace.
- `ext4_set_context()` writes the encryption context either using an existing new-inode journal handle or by starting its own `EXT4_HT_MISC` transaction, with quota initialization, credit calculation, ENOSPC retry, inline-data conversion, DAX/root-directory rejection, inode flag updates, and inode dirtying.
- `ext4_get_dummy_policy()` returns the mounted dummy encryption policy.
- `ext4_has_stable_inodes()` reports the stable-inodes feature to fscrypt.
- `ext4_cryptops` supplies fscrypt callbacks and capability flags, including bounce pages, 32-bit inode support, subblock data units, legacy key prefix, context get/set, empty-dir check, and stable inode query.

## Control flow

Filename setup starts in VFS namei paths before lookup/create. fscrypt prepares disk/user names and optional crypto buffers, then ext4 augments the structure with casefold hashes/buffers; cleanup must release both. The salt ioctl first checks encryption feature support, obtains write access when initialization is needed, starts a journal transaction, gets write access to the superblock buffer, generates the UUID, updates the superblock checksum, dirties metadata, stops the journal, drops write access, and copies 16 bytes to user space.

Encryption context set rejects the root inode, nonempty DAX states, and DAX-flagged inodes, converts inline data away, then stores the xattr. For new inodes it uses the caller's handle and `XATTR_CREATE`; for existing inodes it starts a transaction and retries ENOSPC if a journal commit might free space.

## State and persistence behavior

Persistent state includes the superblock encryption password salt, inode encryption context xattr, inode `EXT4_INODE_ENCRYPT` flag, and possibly cleared inline-data eligibility. In-memory state includes `ext4_filename` buffers, fscrypt crypto buffers, casefold lookup data, per-inode crypt info offset, and dummy policy. Updating encryption context can also alter VFS inode flags such as `S_ENCRYPTED` and DAX-related flags.

## Dependencies and integration points

The file depends on fscrypt, ext4 xattrs, ext4 journaling, superblock checksums, quota initialization, inline-data conversion, DAX checks, namei/casefold helpers, random UUID generation, and user-copy APIs. Directory iteration and lookup code consume the prepared filename structures and fscrypt hashes.

## Risks and edge cases

Root directory encryption is prohibited because e2fsck expects unencrypted `lost+found`. DAX and encryption are incompatible in the checked states. Inline data must be converted before context persistence. Salt generation must be journaled and checksum-updated exactly once even under races. Existing-inode context writes need sufficient xattr credits and correct ENOSPC retry. Cleanup must avoid leaking fscrypt or casefold buffers after partial setup failure.

## Test signals

Test encrypted directory/file creation, lookup, casefolded encrypted names, filename buffer cleanup on failures, password salt ioctl before and after salt generation, concurrent salt requests, root-directory encryption rejection, DAX rejection, inline-data conversion, context inheritance for new inodes, existing-inode policy set with ENOSPC retry, and fscrypt empty-dir checks.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ext4/crypto.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ext4/dir.c -->
# sources/distributed-fs/ceph-client/fs/ext4/dir.c

## Purpose

`fs/ext4/dir.c` implements ext4 directory file operations, including linear directory iteration, htree-indexed directory iteration, directory entry validation, encrypted/casefolded name presentation, directory llseek semantics, per-open directory private state, and directory release cleanup.

## Important APIs, types, and functions

- `is_dx_dir()` detects htree-indexed or potentially indexed directories using feature flags, inode index flag, one-block size, or inline data.
- `is_fake_dir_entry()` treats dot entries, dot-dot entries, and checksum tail entries specially for validation sizing.
- `__ext4_check_dir_entry()` validates record length, alignment, name length fit, block overrun, checksum-tail spacing, inode bounds, and invalid final `.` entries, reporting through file or inode error helpers.
- `ext4_readdir()` is the linear/dispatcher iterate path. It prepares fscrypt, tries htree iteration, falls back on bad dx directories when safe, handles inline-data directories, maps directory blocks, performs readahead, verifies dirblock checksums, rescans after inode version changes, decrypts names, and emits entries.
- `hash2pos()`, `pos2maj_hash()`, `pos2min_hash()`, and `ext4_get_htree_eof()` translate htree hashes to `f_pos` for 32-bit and 64-bit directory APIs.
- `ext4_dir_llseek()` chooses htree hash-space seeking or normal ext4 seeking and invalidates the directory private cookie.
- `struct fname` stores htree entries in an rb-tree keyed by major/minor hash with a linked list for exact hash collisions.
- `ext4_htree_store_dirent()` allocates and inserts decrypted or raw names into the rb-tree.
- `call_filldir()` emits one hash bucket/collision chain and stores continuation state if the caller buffer fills.
- `ext4_dx_readdir()` fills and drains htree sorted names using `ext4_htree_fill_tree()`, inode version cookies, next-hash continuation, and EOF sentinels.
- `ext4_check_all_de()` validates all directory entries in a supplied buffer.
- `ext4_dir_open()` allocates `struct dir_private_info`; `ext4_release_dir()` frees it.
- `ext4_dir_operations` exports open, llseek, generic read, iterate_shared, ioctl, fsync, release, lease, and compat ioctl callbacks.

## Control flow

Every directory open gets private iteration state. Readdir first calls `fscrypt_prepare_readdir()`. If the directory is indexed, it calls `ext4_dx_readdir()`; only `ERR_BAD_DX_DIR` falls back to linear scanning, and the index flag may be cleared when metadata checksums are not enabled. Inline-data directories are handled before block iteration. Linear scanning maps logical directory blocks, skips holes, reads buffers, verifies checksums once per buffer, and validates each dirent before `dir_emit()`. Encrypted names are converted with `fscrypt_fname_disk_to_usr()`, using stored hash/minor hash for casefolded encrypted directories.

Htree iteration treats `ctx->pos` as a hash position. It rebuilds the rb-tree when position changes or inode version changes, fills it from `ext4_htree_fill_tree()`, emits names in hash order, tracks leftover collision-chain entries in `extra_fname`, advances to `next_hash`, and sets an htree EOF sentinel when exhausted.

## State and persistence behavior

This file mostly reads persistent directory blocks. It does not create/delete dirents, but it can clear the in-memory inode index flag after a bad dx fallback when metadata checksums are disabled, without marking the inode dirty. Persistent inputs include ext4 dirent records, file types, inode numbers, checksum tail entries, htree hashes, inline data, encryption/casefold metadata, and inode version changes maintained by writers. Per-open transient state lives in `dir_private_info`, rb-tree `fname` nodes, `ctx->pos`, hash cursors, and inode version cookies.

## Dependencies and integration points

The file depends on ext4 block mapping/read helpers, dirblock checksum verification, htree fill logic from namei/hash code, inline-data directory reads, fscrypt, Unicode/casefold support, VFS `dir_context`, `dir_emit()`, file readahead, inode versioning, buffer-head IO, and ext4 ioctl/fsync implementations.

## Risks and edge cases

Directory validation protects against corrupt disk records causing loops or overreads. Htree `f_pos` hash semantics differ from byte offsets and must stay compatible with 32-bit APIs and NFS-like consumers using hash modes. Encrypted and casefolded directories require correct hash propagation to fscrypt name conversion. If a directory changes during iteration, the code rescans to a valid record boundary using inode versioning. Bad checksums skip the block rather than emitting untrusted names. Large hash-collision chains can consume memory through `struct fname` allocations.

## Test signals

Test linear and indexed readdir, inline directories, encrypted directories, casefolded encrypted directories, 32-bit and 64-bit htree seek positions, telldir/seekdir stability, concurrent create/unlink/rename during readdir, corrupt rec_len/name_len/inode/checksum-tail cases, bad dx fallback with and without metadata checksums, directory block checksum failures, hash collisions, and file buffer-full continuation through `extra_fname`.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ext4/dir.c -->
