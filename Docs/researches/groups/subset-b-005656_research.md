# subset-b-005656 research

Grouped research for the ext4 xattr files and f2fs build, ACL, checkpoint, and compression files listed in work item `subset-b-005656`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ext4/xattr.c -->
# sources/distributed-fs/ceph-client/fs/ext4/xattr.c

## Purpose

`fs/ext4/xattr.c` is the core ext4 extended attribute implementation. It stores, lists, updates, shares, validates, and deletes xattrs held in three possible places: the inode body, one external EA block referenced by `EXT4_I(inode)->i_file_acl`, and, when the `ea_inode` feature is enabled, separate EA inodes for large values. The file also owns the mbcache-backed deduplication path for shared EA blocks and shared EA inodes, journal credit estimation for xattr mutations, and cleanup of EA references during inode deletion.

## Important APIs, Types, and Functions

The public entry points are `ext4_xattr_get()`, `ext4_listxattr()`, `ext4_xattr_set()`, `ext4_xattr_set_handle()`, `ext4_xattr_set_credits()`, `__ext4_xattr_set_credits()`, `ext4_xattr_ibody_find()`, `ext4_xattr_ibody_set()`, `ext4_xattr_ibody_get()`, `ext4_expand_extra_isize_ea()`, `ext4_xattr_delete_inode()`, `ext4_xattr_inode_array_free()`, `ext4_evict_ea_inode()`, `ext4_xattr_create_cache()`, `ext4_xattr_destroy_cache()`, and `ext4_get_inode_usage()`.

`ext4_xattr_handler_map` maps on-disk name indexes to VFS xattr handlers for `user`, POSIX ACLs, `trusted`, `security`, and `hurd`; `ext4_xattr_handlers` is the handler list exported to VFS inode operations. The implementation uses the on-disk structs and macros from `xattr.h`, plus `ext4_xattr_info`, `ext4_xattr_search`, `ext4_xattr_ibody_find`, and the local `ext4_xattr_block_find`.

Validation is centered on `check_xattrs()`, `ext4_xattr_check_block()`, and `__xattr_check_inode()`. Search and enumeration are handled by `xattr_find_entry()`, `ext4_xattr_list_entries()`, `ext4_xattr_ibody_list()`, and `ext4_xattr_block_list()`. Large-value EA inode support uses `ext4_xattr_inode_iget()`, `ext4_xattr_inode_get()`, `ext4_xattr_inode_lookup_create()`, `ext4_xattr_inode_create()`, `ext4_xattr_inode_write()`, `ext4_xattr_inode_update_ref()`, and `ext4_xattr_inode_dec_ref_all()`. Block sharing uses `ext4_xattr_block_cache_insert()`, `ext4_xattr_block_cache_find()`, `ext4_xattr_cmp()`, `ext4_xattr_release_block()`, `ext4_xattr_hash_entry()`, and `ext4_xattr_rehash()`.

## Control Flow

Reads take `EXT4_I(inode)->xattr_sem` for read in `ext4_xattr_get()`. They search the inode-body xattr area first via `ext4_xattr_ibody_get()` and then fall back to the external EA block via `ext4_xattr_block_get()`. Both paths validate bounds and on-disk invariants before copying data. If an entry has `e_value_inum`, the value is loaded through `ext4_xattr_inode_get()`, which igets the EA inode, checks size, reads all value blocks, validates the crc32c-derived value hash, and may insert the EA inode into the cache.

Listing follows the same two-storage order in `ext4_listxattr()`, but each entry is filtered through `ext4_xattr_prefix()` and `xattr_handler_can_list()`, so namespace-specific visibility rules apply before names are copied to the user buffer.

Writes normally enter through `ext4_xattr_set()`, which initializes quotas, computes credits, starts an `EXT4_HT_XATTR` journal handle, and calls `ext4_xattr_set_handle()`. `ext4_xattr_set_handle()` takes the xattr write lock, verifies available journal credits, reserves the raw inode for modification, finds the target entry in the inode and block areas, enforces `XATTR_CREATE`/`XATTR_REPLACE`, skips unchanged inline values, and tries to store the new value first in the inode body. On `-ENOSPC`, it tries or creates an EA block. If the value is too large and `ea_inode` is available, it retries with `i.in_inode = 1`. Successful mutation updates the superblock xattr compat feature, ctime, inode version, raw inode metadata, and marks fast commit ineligible for xattr changes.

`ext4_xattr_set_entry()` is the shared in-memory editor. It calculates old and new padded value sizes, compacts old values, inserts or removes the name entry, stores either inline value bytes or an EA inode number, updates entry hashes, and rehashes an EA block when needed. It deliberately performs failure-prone EA inode iget/refcount work before modifying the xattr entry region.

External block updates in `ext4_xattr_block_set()` choose among in-place mutation of an exclusive block, cloning a shared block, reusing an identical cached block by incrementing its refcount, or allocating a new metadata block. Replacement of a previous block releases the old block through `ext4_xattr_release_block()`, which decrements the block refcount or frees the block and decrements all referenced EA inodes.

Deletion during inode eviction is handled by `ext4_xattr_delete_inode()`. It decrements EA inode references found in the inode body, releases the external EA block, clears `i_file_acl`, marks the inode dirty, and returns any deferred EA inodes to `ext4_xattr_inode_array_free()` for `iput()`.

## State and Persistence Behavior

On disk, inode-body xattrs start at `IHDR()` after `i_extra_isize`; block xattrs start with an `ext4_xattr_header` at `i_file_acl`. Block xattr headers include magic, refcount, hash, checksum, and block count. Entry descriptors grow upward while value bytes are packed from the end of the storage region downward. EA blocks are sorted; inode-body entries are not.

Shared EA blocks persist through `h_refcount`, `h_hash`, and the inode's `i_file_acl`. Metadata checksums cover the block number and header/data with `h_checksum` zeroed for calculation. Large EA values persist in hidden regular EA inodes whose refcount is encoded in ctime plus raw i_version, whose value hash is stored in atime seconds, and whose parent/backpointer compatibility is recognized for old Lustre-style EA inodes. Quota is charged to the parent inode even when the large EA value is shared.

All persistent mutations are journaled through jbd2 handles, buffer write access calls, dirty metadata calls, inode dirtying, and metadata block allocation/free. The file takes care to handle journal restarts while decrementing EA inode refs and to zero block tails and value padding before writeback.

## Dependencies and Integration Points

This file integrates with VFS xattr handlers, POSIX ACL handler constants, jbd2/ext4 journaling, ext4 inode allocation and block mapping, quota operations, mbcache, metadata checksums, inline data, fast commit eligibility, ext4 error reporting, and lockdep. It depends on the namespace wrappers in `xattr_user.c`, `xattr_trusted.c`, `xattr_security.c`, and `xattr_hurd.c`, and on `xattr.h` for all storage layout definitions.

## Risks and Edge Cases

The highest-risk areas are corruption validation, refcount transitions, and ENOSPC paths. `check_xattrs()` defends against out-of-bounds names, overlapping values, unsupported EA inode references, invalid EA inode numbers, oversized values, and invalid checksums. Shared block races require buffer locking plus mbcache delete-or-get semantics so a block is not modified while another thread is trying to reuse it. EA inode refcounts can wrap, so `ext4_xattr_inode_update_ref()` explicitly checks zero and `U64_MAX`. Journal credit underestimation is guarded by preflight credit checks and retry-on-ENOSPC in `ext4_xattr_set()`. Hash compatibility for old signed-char name hashing is supported but warned once.

Inline data and inode expansion interact with xattr layout. `EXT4_STATE_NO_EXPAND` is set while holding the xattr write lock to avoid recursive expansion, and `ext4_expand_extra_isize_ea()` may move selected xattrs from inode body to EA block to make room for larger inode extra fields.

## Test Signals

Useful tests exercise get/list/set/remove across all namespaces, long names, create/replace flags, values that fit inode body, values that spill to EA blocks, values large enough for EA inodes, identical xattr block sharing, identical EA inode sharing, quota failures, journal credit exhaustion, nojournal mode, inline-data inodes, inode extra-isize expansion, deletion of inodes with shared EA blocks and EA inodes, and corruption injection for bad magic, bad checksum, bad value offsets, invalid `e_value_inum`, hash mismatch, and read I/O failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ext4/xattr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ext4/xattr.h -->
# sources/distributed-fs/ceph-client/fs/ext4/xattr.h

## Purpose

`fs/ext4/xattr.h` defines the ext4 extended attribute on-disk format, namespace indexes, storage layout helpers, in-memory helper structs, lock helpers, and exported function prototypes used by ext4 xattr, ACL, security, and inode-management code.

## Important APIs, Types, and Functions

The key on-disk constants are `EXT4_XATTR_MAGIC`, `EXT4_XATTR_REFCOUNT_MAX`, and the namespace indexes for user, POSIX ACL access/default, trusted, Lustre, security, system, richacl, encryption, and Hurd xattrs. `struct ext4_xattr_header` is the external block header with magic, refcount, block count, block hash, checksum, and reserved fields. `struct ext4_xattr_ibody_header` marks in-inode xattr storage. `struct ext4_xattr_entry` stores the name length/index, value offset, optional EA inode number, value size, entry hash, and inline name.

The layout macros `EXT4_XATTR_LEN()`, `EXT4_XATTR_NEXT()`, and `EXT4_XATTR_SIZE()` implement 4-byte padding. `IHDR()`, `ITAIL()`, and `IFIRST()` locate the inode-body xattr area from a raw ext4 inode. `BHDR()`, `BFIRST()`, `ENTRY()`, and `IS_LAST_ENTRY()` do the same for external xattr blocks. `EXT4_INODE_HAS_XATTR_SPACE()` checks whether the inode has enough extra-inode room for an ibody xattr header, one entry, padding, and data.

The in-memory control structs are `ext4_xattr_info`, `ext4_xattr_search`, `ext4_xattr_ibody_find`, and `ext4_xattr_inode_array`. Exported APIs include get/list/set paths, journal credit estimation, inode deletion cleanup, extra-isize expansion, EA inode eviction, ibody find/get/set, mbcache creation/destruction, inode xattr validation, optional security initialization, optional lockdep class setup, and quota usage accounting.

## Control Flow

This header does not implement full control flow, but it defines how callers traverse storage: start with a header, use `IFIRST()` or `BFIRST()` to obtain the first entry, iterate with `EXT4_XATTR_NEXT()`, and stop when `IS_LAST_ENTRY()` sees the null terminator. Writers use `ext4_write_lock_xattr()`, `ext4_write_trylock_xattr()`, and `ext4_write_unlock_xattr()` to protect xattr mutation and to set `EXT4_STATE_NO_EXPAND` while the xattr semaphore is held.

## State and Persistence Behavior

The structs in this file are the persistent ABI for ext4 xattrs. Entry value bytes may be inline in the inode or external block, or may be referenced by `e_value_inum` when large EA inode storage is enabled. `EXT4_XATTR_SIZE_MAX` is intentionally larger than the current user-visible xattr size limit to support consistency checks without overflow-prone `INT_MAX` arithmetic. `EXT4_XATTR_MIN_LARGE_EA_SIZE()` defines when using an external inode can be worthwhile by reserving room in an EA block for at least one entry and terminator.

## Dependencies and Integration Points

The header includes `<linux/xattr.h>` and is consumed by ext4 xattr namespace handlers, ext4 ACL code, security initialization, inode expansion code, and eviction paths. Its locking helpers depend on `EXT4_I(inode)->xattr_sem` and inode state flags from `ext4.h`. Security initialization is compiled to `ext4_init_security()` only when `CONFIG_EXT4_FS_SECURITY` is enabled; otherwise it is an inline no-op.

## Risks and Edge Cases

The layout macros are pointer-arithmetic heavy and assume validated input. Callers must validate entry bounds before trusting `EXT4_XATTR_NEXT()` or value offsets. `EXT4_STATE_NO_EXPAND` is intentionally overloaded: it can mean inline xattrs/data are too full to expand, or that xattr write locking is preventing recursive expansion. Callers using the lock helpers must preserve and restore the prior state flag correctly.

## Test Signals

Tests should cover xattr layout iteration, padding, maximum name and value boundaries, in-inode capacity checks for different inode sizes and `i_extra_isize`, conditional compilation of security and lockdep paths, and correct save/restore behavior of `EXT4_STATE_NO_EXPAND` around xattr writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ext4/xattr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ext4/xattr_hurd.c -->
# sources/distributed-fs/ceph-client/fs/ext4/xattr_hurd.c

## Purpose

`fs/ext4/xattr_hurd.c` implements the ext4 VFS xattr handler for GNU Hurd-prefixed attributes. It is a thin namespace adapter that maps the VFS `XATTR_HURD_PREFIX` namespace to ext4's on-disk `EXT4_XATTR_INDEX_HURD` namespace.

## Important APIs, Types, and Functions

The file defines `ext4_xattr_hurd_list()`, `ext4_xattr_hurd_get()`, `ext4_xattr_hurd_set()`, and exports `ext4_xattr_hurd_handler`. The handler's `.prefix` is `XATTR_HURD_PREFIX`; `.list`, `.get`, and `.set` point to the local wrapper functions.

## Control Flow

Listing and access are gated by the ext4 mount option `XATTR_USER`. `ext4_xattr_hurd_list()` returns true only when that option is set on the dentry superblock. `ext4_xattr_hurd_get()` and `ext4_xattr_hurd_set()` return `-EOPNOTSUPP` if `XATTR_USER` is not enabled; otherwise they call `ext4_xattr_get()` or `ext4_xattr_set()` with `EXT4_XATTR_INDEX_HURD`.

## State and Persistence Behavior

This file does not manage storage itself. It persists values through the common ext4 xattr engine, which may store the attribute in the inode body, external EA block, or EA inode depending on size and feature flags. The only persistent discriminator introduced here is the `EXT4_XATTR_INDEX_HURD` name index on each xattr entry.

## Dependencies and Integration Points

It depends on ext4 mount-option helpers from `ext4.h`, the common xattr API from `xattr.h`, and VFS xattr handler dispatch. The handler is included in `ext4_xattr_handler_map` and `ext4_xattr_handlers` from `xattr.c`, which makes it visible to ext4 inode operations and xattr listing.

## Risks and Edge Cases

The main behavioral risk is policy coupling to `XATTR_USER`: disabling user xattrs also disables Hurd xattrs. The get/set wrappers ignore the `mnt_idmap` argument, which is expected for raw xattr storage but should remain consistent with VFS handler signatures. All corruption, journaling, quota, and size risks are delegated to `xattr.c`.

## Test Signals

Mount ext4 with and without `user_xattr` and verify Hurd-prefixed xattrs list, get, set, replace, and remove only when the option permits them. Also verify that entries persist with the Hurd name index and that errors from the common ext4 xattr engine propagate unchanged.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ext4/xattr_hurd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ext4/xattr_security.c -->
# sources/distributed-fs/ceph-client/fs/ext4/xattr_security.c

## Purpose

`fs/ext4/xattr_security.c` implements the ext4 VFS xattr handler for `security.*` labels and provides the inode-creation hook that initializes security xattrs from Linux Security Modules.

## Important APIs, Types, and Functions

The file defines `ext4_xattr_security_get()`, `ext4_xattr_security_set()`, `ext4_initxattrs()`, `ext4_init_security()`, and exports `ext4_xattr_security_handler`. The handler uses `XATTR_SECURITY_PREFIX` and delegates storage to `EXT4_XATTR_INDEX_SECURITY`.

## Control Flow

Normal get/set calls are direct wrappers around `ext4_xattr_get()` and `ext4_xattr_set()` with the security namespace index. During inode creation, `ext4_init_security()` calls `security_inode_init_security()` and passes `ext4_initxattrs()` as the callback. The callback iterates the LSM-provided `struct xattr` array and writes each label into the new inode using `ext4_xattr_set_handle()` with the caller's existing journal handle and `XATTR_CREATE`. Iteration stops on the first negative error.

## State and Persistence Behavior

Security labels persist as ext4 xattrs with `EXT4_XATTR_INDEX_SECURITY`. Because initialization uses the transaction handle supplied by the creator, initial labels are committed atomically with inode creation metadata. Storage location and large-value behavior are delegated to the common xattr layer.

## Dependencies and Integration Points

This file depends on `<linux/security.h>` and LSM xattr initialization semantics. It integrates with ext4 inode creation through the `ext4_init_security()` prototype in `xattr.h`, which compiles only under `CONFIG_EXT4_FS_SECURITY`. It also integrates with the common xattr engine, jbd2 handles, and VFS xattr dispatch.

## Risks and Edge Cases

Failure to set any one initial label aborts the callback and returns the error to inode creation. Journal credit sizing must account for all security xattrs that can be emitted by active LSMs. Because `ext4_initxattrs()` uses `XATTR_CREATE`, pre-existing labels on a reused or unexpected inode state should fail rather than replace. Runtime security get/set authorization is expected to be enforced above or around VFS xattr dispatch; this wrapper only selects storage.

## Test Signals

Tests should create files under SELinux, Smack, AppArmor, or another label-producing LSM and verify that labels are initialized and journaled with the inode. Exercise `security.*` get/set/remove through VFS APIs, forced ENOSPC or journal-credit failures during label creation, and propagation of errors from `ext4_xattr_set_handle()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ext4/xattr_security.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ext4/xattr_trusted.c -->
# sources/distributed-fs/ceph-client/fs/ext4/xattr_trusted.c

## Purpose

`fs/ext4/xattr_trusted.c` implements the ext4 VFS xattr handler for the `trusted.*` namespace. It maps trusted xattrs to `EXT4_XATTR_INDEX_TRUSTED` and restricts listing to administrators.

## Important APIs, Types, and Functions

The file defines `ext4_xattr_trusted_list()`, `ext4_xattr_trusted_get()`, `ext4_xattr_trusted_set()`, and exports `ext4_xattr_trusted_handler`. The handler uses `XATTR_TRUSTED_PREFIX`.

## Control Flow

`ext4_xattr_trusted_list()` returns `capable(CAP_SYS_ADMIN)`, so unprivileged callers do not see trusted names in listxattr output. Get and set calls are thin wrappers around `ext4_xattr_get()` and `ext4_xattr_set()` using `EXT4_XATTR_INDEX_TRUSTED`. The wrapper does not perform its own capability checks for get/set; VFS and xattr core policy are expected to gate access.

## State and Persistence Behavior

Trusted values persist through common ext4 xattr storage under the trusted name index. The file itself maintains no independent state.

## Dependencies and Integration Points

It depends on Linux capability checks, VFS xattr handler dispatch, and the common ext4 xattr implementation. The exported handler is wired into the handler map and list in `xattr.c`.

## Risks and Edge Cases

The namespace's security property depends on correct VFS/core checks for get and set, because only list filtering happens locally. Any change in capability semantics or namespace policy should be checked against this wrapper. Storage corruption, ENOSPC, quota, and journaling risks are delegated to `xattr.c`.

## Test Signals

Test listxattr as privileged and unprivileged callers, verify get/set/remove of trusted xattrs with appropriate privileges, and ensure common ext4 xattr errors propagate. Also verify that trusted entries are not exposed in list output without `CAP_SYS_ADMIN`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ext4/xattr_trusted.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ext4/xattr_user.c -->
# sources/distributed-fs/ceph-client/fs/ext4/xattr_user.c

## Purpose

`fs/ext4/xattr_user.c` implements the ext4 VFS xattr handler for the `user.*` namespace. It gates user xattrs on the ext4 `XATTR_USER` mount option and maps them to `EXT4_XATTR_INDEX_USER`.

## Important APIs, Types, and Functions

The file defines `ext4_xattr_user_list()`, `ext4_xattr_user_get()`, `ext4_xattr_user_set()`, and exports `ext4_xattr_user_handler`. The handler uses `XATTR_USER_PREFIX`.

## Control Flow

All operations first check the mount option. Listing returns true only when `test_opt(dentry->d_sb, XATTR_USER)` succeeds. Get and set return `-EOPNOTSUPP` when the option is disabled; otherwise they call `ext4_xattr_get()` or `ext4_xattr_set()` with the user namespace index.

## State and Persistence Behavior

User xattrs persist under the ext4 user name index and are stored by the common xattr engine in inode body, EA block, or EA inode form. This wrapper keeps no additional state.

## Dependencies and Integration Points

The file depends on ext4 mount-option handling, VFS xattr dispatch, and the common ext4 xattr implementation. Its exported handler is part of `ext4_xattr_handlers` and `ext4_xattr_handler_map`, affecting both VFS operations and list filtering.

## Risks and Edge Cases

The main risk is mount-option policy: user xattrs must not be accessible when `XATTR_USER` is disabled. The wrapper ignores idmap details, which is normal for raw xattr data but should stay aligned with VFS expectations. Size, quota, corruption, and journal behavior are delegated to `xattr.c`.

## Test Signals

Mount with and without user xattrs enabled. Verify `user.*` list/get/set/remove behavior, `-EOPNOTSUPP` propagation when disabled, correct persistence across remount, and fallback behavior for inode-body, EA block, and large-value storage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ext4/xattr_user.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/f2fs/Kconfig -->
# sources/distributed-fs/ceph-client/fs/f2fs/Kconfig

## Purpose

`fs/f2fs/Kconfig` defines the kernel configuration surface for F2FS. It controls whether F2FS is built, which optional features are compiled, and which compression, encryption, ACL, xattr, debug, fault-injection, iostat, and locking dependencies are selected.

## Important Config Symbols

`F2FS_FS` is the root tristate and depends on `BLOCK`. It selects buffer heads, NLS, CRC32, iomap support, encryption xattr support when needed, encryption algorithms, and compression library symbols according to selected algorithms. `F2FS_STAT_FS` enables debugfs status reporting. `F2FS_FS_XATTR` enables xattrs. `F2FS_FS_POSIX_ACL` depends on xattrs and selects `FS_POSIX_ACL`. `F2FS_FS_SECURITY` depends on xattrs and enables security labels. `F2FS_CHECK_FS` adds runtime consistency checking. `F2FS_FAULT_INJECTION` enables injected failures. `F2FS_FS_COMPRESSION` enables file compression. `F2FS_FS_LZO`, `F2FS_FS_LZORLE`, `F2FS_FS_LZ4`, `F2FS_FS_LZ4HC`, and `F2FS_FS_ZSTD` select algorithm support. `F2FS_IOSTAT` enables I/O statistics, and `F2FS_UNFAIR_RWSEM` enables unfair rwsem behavior when block cgroups are present.

## Control Flow

Kconfig dependency flow starts at `F2FS_FS`. ACL and security features are unavailable unless xattrs are enabled. Compression algorithms are unavailable unless `F2FS_FS_COMPRESSION` is enabled, and their selected library dependencies feed directly into `compress.c` compile-time branches. The default choices lean toward common F2FS functionality: status, xattrs, ACLs, and compression algorithms default to enabled once their parent feature is enabled.

## State and Persistence Behavior

This file does not persist filesystem runtime state, but it determines which on-disk features can be mounted or used by a built kernel. Enabling xattr, ACL, security, and compression changes which metadata features the filesystem can create or interpret. Compression algorithm selections influence whether existing compressed files using a given algorithm can be read.

## Dependencies and Integration Points

The symbols map directly to object inclusion in `Makefile` and to `#ifdef CONFIG_F2FS_*` blocks in F2FS source files such as `acl.c`, `xattr.c`, `compress.c`, `debug.c`, and `iostat.c`. Compression selections integrate with kernel LZO, LZ4, LZ4HC, and ZSTD libraries.

## Risks and Edge Cases

Configuration mismatches can produce kernels unable to access expected F2FS features. Disabling xattrs disables ACL and security labels. Disabling a compression algorithm can make files compressed with that algorithm unreadable by this build. Runtime checking and fault injection are useful for development but may affect performance or failure behavior if enabled unexpectedly.

## Test Signals

Build matrix tests should cover F2FS without xattrs, with xattrs but no ACL/security, with compression disabled, and with each compression algorithm combination. Kconfig dependency tests should verify that selected libraries and object files match enabled symbols and that invalid symbol combinations are not offered.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/f2fs/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/f2fs/Makefile -->
# sources/distributed-fs/ceph-client/fs/f2fs/Makefile

## Purpose

`fs/f2fs/Makefile` defines how the F2FS kernel object is assembled from mandatory and optional source files.

## Important Build Rules

`obj-$(CONFIG_F2FS_FS) += f2fs.o` builds the aggregate F2FS object when the root filesystem symbol is enabled. The base `f2fs-y` list includes directory, file, inode, name, hash, superblock, inline-data, checkpoint, garbage collection, data, node, segment, recovery, shrinker, extent cache, and sysfs code. Conditional additions include `debug.o` for `CONFIG_F2FS_STAT_FS`, `xattr.o` for `CONFIG_F2FS_FS_XATTR`, `acl.o` for `CONFIG_F2FS_FS_POSIX_ACL`, `verity.o` for `CONFIG_FS_VERITY`, `compress.o` for `CONFIG_F2FS_FS_COMPRESSION`, and `iostat.o` for `CONFIG_F2FS_IOSTAT`.

## Control Flow

The Makefile mirrors Kconfig feature selection. Core mount and filesystem operation code is always part of `f2fs.o` when F2FS is enabled. Optional feature objects are linked only when their config symbols are enabled, which means callers must use conditional declarations or stubs, as seen in `acl.h`.

## State and Persistence Behavior

This file has no runtime state, but it controls which code can interpret or produce feature-specific persistent metadata. Including or excluding `compress.o`, `acl.o`, or `xattr.o` changes support for compressed clusters, POSIX ACL xattrs, and generic xattrs in the built filesystem.

## Dependencies and Integration Points

It integrates with the kernel kbuild system and symbols defined in `Kconfig`. It is the bridge between configuration and implementation for files researched in this subset: `checkpoint.o` is mandatory, `acl.o` is conditional on POSIX ACL support, and `compress.o` is conditional on compression support.

## Risks and Edge Cases

Build breakage can occur if optional code is referenced without a stub when the object is not linked. Feature combinations must stay aligned with Kconfig dependencies. Because `checkpoint.o` is mandatory, checkpoint regressions affect every F2FS build.

## Test Signals

Compile F2FS with minimal config, full config, xattr-only, ACL-enabled, compression-enabled, fs-verity-enabled, and iostat-enabled variants. Verify object inclusion with `make V=1` or generated build artifacts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/f2fs/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/f2fs/acl.c -->
# sources/distributed-fs/ceph-client/fs/f2fs/acl.c

## Purpose

`fs/f2fs/acl.c` implements POSIX ACL support for F2FS on top of F2FS xattrs. It converts between the F2FS on-disk ACL xattr format and in-memory `struct posix_acl`, handles get/set operations for access and default ACLs, applies ACL inheritance and umask behavior during inode creation, and keeps inode mode bits synchronized with equivalent access ACLs.

## Important APIs, Types, and Functions

Public entry points are `f2fs_get_acl()`, `f2fs_set_acl()`, and `f2fs_init_acl()`. Internal format helpers are `f2fs_acl_size()`, `f2fs_acl_count()`, `f2fs_acl_from_disk()`, and `f2fs_acl_to_disk()`. ACL mutation helpers include `__f2fs_get_acl()`, `f2fs_acl_update_mode()`, `__f2fs_set_acl()`, `f2fs_acl_clone()`, `f2fs_acl_create_masq()`, and `f2fs_acl_create()`.

The on-disk structs and `F2FS_ACL_VERSION` come from `acl.h`; xattr indexes come from `xattr.h`. Values are stored in the empty-name POSIX ACL xattr entries `F2FS_XATTR_INDEX_POSIX_ACL_ACCESS` and `F2FS_XATTR_INDEX_POSIX_ACL_DEFAULT`.

## Control Flow

`f2fs_get_acl()` rejects RCU lookup with `-ECHILD` and calls `__f2fs_get_acl()`. The internal getter selects access or default ACL index, first probes `f2fs_getxattr()` for the value size, allocates a zeroed buffer if present, fetches the value, and parses it with `f2fs_acl_from_disk()`. `-ENODATA` becomes a NULL ACL, while other errors become `ERR_PTR()`.

`f2fs_set_acl()` checks for checkpoint error and then calls `__f2fs_set_acl()`. For access ACLs, `f2fs_acl_update_mode()` uses `posix_acl_equiv_mode()` to update the inode mode and drop an ACL that is equivalent to mode bits; it also clears setgid if the caller lacks group ownership/capability. Default ACLs are allowed only on directories. Non-NULL ACLs are serialized with `f2fs_acl_to_disk()` and stored through `f2fs_setxattr()`. On success, the VFS ACL cache is updated.

`f2fs_init_acl()` is called during inode creation. It obtains the parent directory default ACL, applies umask when no default ACL exists, clones and masks the inherited ACL against the new mode, installs a default ACL for new directories, installs an access ACL when the inherited ACL is not mode-equivalent, and marks the inode dirty synchronously after mode changes.

## State and Persistence Behavior

The persistent ACL xattr starts with `struct f2fs_acl_header` and version `F2FS_ACL_VERSION`. The first four ACL classes use compact `f2fs_acl_entry_short` records without an ID; named user and group entries use full `f2fs_acl_entry` records with little-endian UID/GID values in the initial user namespace. Access ACL changes may update `inode->i_mode`, `F2FS_I(inode)->i_acl_mode`, and cached ACL pointers. ACL xattrs are persisted by the common F2FS xattr layer and therefore participate in checkpointing and node/page writeback indirectly.

## Dependencies and Integration Points

This file depends on Linux POSIX ACL helpers, F2FS xattr APIs, F2FS inode dirtying, checkpoint error state, idmapped mount permission helpers, and `init_user_ns` UID/GID conversion. It is linked only when `CONFIG_F2FS_FS_POSIX_ACL` is enabled.

## Risks and Edge Cases

Parser risks include malformed length, wrong version, unexpected trailing bytes, unknown tags, and invalid short/full entry transitions. Setter risks include clearing `FI_ACL_MODE` correctly on serialization failure, default ACL rejection on non-directories, mode/ACL equivalence handling, and setgid stripping under idmapped mounts. Creation-time inheritance must release all ACL references on every error path.

## Test Signals

Tests should cover malformed ACL xattrs, empty ACLs, all POSIX ACL tag types, access ACLs equivalent and non-equivalent to mode bits, default ACL inheritance by files and directories, symlink creation, idmapped mount setgid behavior, checkpoint error returning `-EIO`, and ACL cache updates after set/remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/f2fs/acl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/f2fs/acl.h -->
# sources/distributed-fs/ceph-client/fs/f2fs/acl.h

## Purpose

`fs/f2fs/acl.h` defines the F2FS on-disk POSIX ACL xattr format and exposes ACL entry points or stubs depending on `CONFIG_F2FS_FS_POSIX_ACL`.

## Important APIs, Types, and Functions

The persistent format version is `F2FS_ACL_VERSION`. `struct f2fs_acl_header` stores the little-endian version. `struct f2fs_acl_entry_short` stores tag and permissions for ACL entries that do not need an ID. `struct f2fs_acl_entry` extends that with a little-endian UID/GID ID for named user and group entries.

When POSIX ACL support is enabled, the header declares `f2fs_get_acl()`, `f2fs_set_acl()`, and `f2fs_init_acl()`. When disabled, `f2fs_get_acl` and `f2fs_set_acl` are NULL macros and `f2fs_init_acl()` is an inline no-op returning zero.

## Control Flow

The header's conditional declarations let common F2FS inode and creation code call ACL hooks without linking `acl.o` when ACL support is disabled. With ACL enabled, calls are dispatched to `acl.c`; without ACL, creation proceeds without ACL initialization.

## State and Persistence Behavior

The structs define the byte layout stored as F2FS POSIX ACL xattr values. All numeric fields are little-endian. The short-entry optimization means the serialized size depends on tag order and count; parsing code in `acl.c` must agree exactly with these definitions.

## Dependencies and Integration Points

The header includes `<linux/posix_acl_xattr.h>` for POSIX ACL constants and types. It is consumed by F2FS inode creation, xattr, and ACL implementation code. Kconfig and the F2FS Makefile determine whether the real implementation is linked.

## Risks and Edge Cases

Any ABI change to these structs would affect existing on-disk ACL xattrs. The disabled-config stubs must remain consistent with callers' expectations; for example, creation must not fail just because ACL support is compiled out.

## Test Signals

Build tests should cover ACL enabled and disabled. Format tests should verify serialized sizes, version checks, little-endian conversion, and compatibility between `acl.h` layout and `acl.c` parser/serializer.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/f2fs/acl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/f2fs/checkpoint.c -->
# sources/distributed-fs/ceph-client/fs/f2fs/checkpoint.c

## Purpose

`fs/f2fs/checkpoint.c` implements F2FS checkpointing and related metadata orchestration. It manages checkpoint locks and priority uplift, metadata folio I/O, block-address validation, dirty inode tracking, orphan inode recovery and persistence, checkpoint pack validation and selection at mount, freezing filesystem operations for checkpoint, writing checkpoint packs, and the optional merged checkpoint request thread.

## Important APIs, Types, and Functions

Lock tracing and priority helpers include `f2fs_down_read_trace()`, `f2fs_down_read_trylock_trace()`, `f2fs_up_read_trace()`, `f2fs_down_write_trace()`, `f2fs_down_write_trylock_trace()`, `f2fs_up_write_trace()`, `f2fs_lock_op()`, `f2fs_trylock_op()`, and `f2fs_unlock_op()`.

Metadata folio APIs include `f2fs_grab_meta_folio()`, `f2fs_get_meta_folio()`, `f2fs_get_meta_folio_retry()`, `f2fs_get_tmp_folio()`, `f2fs_ra_meta_pages()`, `f2fs_ra_meta_pages_cond()`, `f2fs_sync_meta_pages()`, and `f2fs_meta_aops`. Address validation is exposed by `f2fs_is_valid_blkaddr()` and `f2fs_is_valid_blkaddr_raw()`.

Inode tracking APIs include `f2fs_add_ino_entry()`, `f2fs_remove_ino_entry()`, `f2fs_exist_written_data()`, `f2fs_release_ino_entry()`, `f2fs_set_dirty_device()`, `f2fs_is_dirty_device()`, `f2fs_acquire_orphan_inode()`, `f2fs_release_orphan_inode()`, `f2fs_add_orphan_inode()`, and `f2fs_remove_orphan_inode()`. Recovery and checkpoint APIs include `f2fs_recover_orphan_inodes()`, `f2fs_get_valid_checkpoint()`, `f2fs_sync_dirty_inodes()`, `f2fs_wait_on_all_pages()`, `f2fs_write_checkpoint()`, `f2fs_issue_checkpoint()`, `f2fs_start_ckpt_thread()`, `f2fs_stop_ckpt_thread()`, `f2fs_flush_ckpt_thread()`, and init/destroy helpers for checkpoint caches and request control.

## Control Flow

Mount-time checkpoint selection begins in `f2fs_get_valid_checkpoint()`. It reads both checkpoint packs, validates the first and last checkpoint block of each pack through checksum and version checks, chooses the newer valid version, copies the checkpoint payload into `sbi->ckpt`, records `cur_cp_pack`, and performs sanity checking before reading any additional payload blocks.

Runtime checkpointing enters through `f2fs_write_checkpoint()` or `f2fs_issue_checkpoint()`. `f2fs_issue_checkpoint()` may write synchronously or enqueue a request to the checkpoint thread when merge-checkpoint mode is active. The synchronous path takes `gc_lock`, then `f2fs_write_checkpoint()` takes `cp_global_sem` except during resize, skips clean checkpoints for selected reasons, rejects read-only or checkpoint-error states, and calls `block_operations()`.

`block_operations()` freezes mutating filesystem activity by taking `cp_rwsem`, flushing quota when needed, writing dirty dentries, taking `node_change`, syncing dirty inode metadata, taking `node_write`, syncing dirty node pages, and preparing the checkpoint block counters. `unblock_operations()` releases `node_write` and `cp_rwsem`.

After operations are blocked, `f2fs_write_checkpoint()` flushes merged writes, advances the checkpoint version, flushes NAT and SIT entries, saves in-memory current segment state, and calls `do_checkpoint()`. `do_checkpoint()` writes dirty metadata, fills checkpoint counters and current segment fields, updates flags, copies NAT/SIT bitmaps, computes the checkpoint checksum, writes NAT bits, checkpoint payload, orphan blocks, data summaries, node summaries when needed, flushes metadata and device cache, and finally writes the second checkpoint block through `commit_checkpoint()` with `META_FLUSH`. It then invalidates temporary meta mapping pages for encrypted/verity/compressed files, releases inode tracking entries, resets dirty/checkpoint flags, switches to the next checkpoint pack, and reports `-EIO` if checkpoint error state appeared.

Orphan recovery is handled separately by `f2fs_recover_orphan_inodes()`, which reads orphan blocks from the current checkpoint pack, igets each orphan inode, clears nlink, drops it through `iput()` to trigger truncation, and sets `SBI_NEED_FSCK` if cleanup cannot prove the node block was removed.

## State and Persistence Behavior

The central persistent object is `struct f2fs_checkpoint` plus checkpoint payload blocks, orphan inode blocks, segment summaries, NAT/SIT bitmaps, optional NAT bits, and two alternating checkpoint packs. `checkpoint_ver` determines the newer pack. Checkpoint flags persist mount/recovery state such as orphan presence, umount, fastboot, trimmed, fsck-needed, resize, checkpoint-disabled, quick-disabled, quota-needs-fsck, and CRC recovery mode.

In memory, the file maintains metadata folios in `META_MAPPING(sbi)`, dirty page counters, inode-management radix trees and lists for orphan/append/update/flush tracking, checkpoint timing stats, and merged checkpoint request queues. It also maintains slab caches for `ino_entry` and `inode_entry`.

## Dependencies and Integration Points

This file is deeply integrated with F2FS node, segment, data, quota, discard, GC, recovery, iostat, tracepoint, fault-injection, and mount-option code. It uses Linux folio/pagecache APIs, writeback controls, bio submission, blk plugs, wait queues, kthreads, delay accounting, ioprio, and block-device statistics. It provides synchronization used by write paths, GC, quota writes, compression writes, and recovery.

## Risks and Edge Cases

Risks concentrate around ordering and failure handling. Checkpoint correctness depends on freezing the right operations, flushing NAT/SIT/meta/data in order, writing the final checkpoint block only after prior metadata is durable, and switching packs only after success. Address validation must distinguish metadata, recovery, and data contexts and set `SBI_NEED_FSCK` or checkpoint error state appropriately. Orphan recovery on read-only hardware is skipped, which preserves media but leaves cleanup to later writable mounts. Quota flushing can retry and eventually set quota repair flags. The merged checkpoint thread must complete queued requests even when the thread stops or a request was already dispatched.

## Test Signals

High-value tests include mount with one valid checkpoint pack, both valid packs with different versions, invalid checksum, invalid payload count, orphan recovery success/failure, readonly orphan skip, dirty dentry/node/imeta flushing, quota flush retries, checkpoint disabled and pause behavior, discard-only checkpoints with no candidates, NAT/SIT flush errors, device flush errors, cp_error propagation, merged checkpoint queue latency and shutdown, fault injection for locks/block addresses/orphans, and fsck-needed flag setting after validation failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/f2fs/checkpoint.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/f2fs/compress.c -->
# sources/distributed-fs/ceph-client/fs/f2fs/compress.c

## Purpose

`fs/f2fs/compress.c` implements F2FS filesystem-level compression. It manages compression context allocation, algorithm backends, compression and decompression I/O contexts, compressed-cluster read/write paths, overwrite and truncate behavior for compressed clusters, compressed-page caching, and global/per-mount memory caches used by compression.

## Important APIs, Types, and Functions

The backend abstraction is `struct f2fs_compress_ops`, with optional init/destroy hooks and required compression/decompression hooks. Backends are compiled for LZO, LZ4/LZ4HC, ZSTD, and LZO-RLE depending on Kconfig. Public helpers include `f2fs_is_compressed_page()`, `f2fs_compress_control_folio()`, `f2fs_init_compress_ctx()`, `f2fs_destroy_compress_ctx()`, `f2fs_compress_ctx_add_page()`, `f2fs_is_compress_backend_ready()`, `f2fs_is_compress_level_valid()`, `f2fs_decompress_cluster()`, `f2fs_end_read_compressed_page()`, `f2fs_cluster_is_empty()`, `f2fs_cluster_can_merge_page()`, `f2fs_all_cluster_page_ready()`, `f2fs_sanity_check_cluster()`, `f2fs_is_compressed_cluster()`, `f2fs_is_sparse_cluster()`, `f2fs_prepare_compress_overwrite()`, `f2fs_compress_write_end()`, `f2fs_truncate_partial_cluster()`, `f2fs_write_multi_pages()`, `f2fs_compress_write_end_io()`, `f2fs_alloc_dic()`, `f2fs_decompress_end_io()`, `f2fs_put_folio_dic()`, `f2fs_cluster_blocks_are_contiguous()`, `COMPRESS_MAPPING()`, cache invalidation/load helpers, and init/destroy helpers for mempools and slabs.

## Control Flow

Writeback batches pages into a `compress_ctx`. `f2fs_write_multi_pages()` checks `cluster_may_compress()`: the file must need compression, not be atomic, the cluster must be full, checkpoint must be healthy, and all pages must be within EOF. It then calls `f2fs_compress_pages()`, which initializes the backend, allocates compressed pages from a mempool, vmaps raw and compressed page arrays, invokes the selected backend, writes the F2FS compression header (`clen`, optional checksum, reserved fields), zero-fills the tail, frees unused compressed pages, and records the valid compressed page count. If compression is ineffective or impossible, the cluster falls back to `f2fs_write_raw_pages()`.

`f2fs_write_compressed_pages()` converts a compressed cluster into on-disk blocks. It obtains the dnode, validates that each cluster slot has a block address, allocates a `compress_io_ctx`, marks compressed pages with private context, optionally encrypts them, sets writeback on raw pages, stores `COMPRESS_ADDR` in the cluster header slot, invalidates or rewrites old blocks, submits out-of-place writes for compressed payload pages, updates compressed block accounting, unlocks raw pages, and frees context arrays after submission. Completion runs through `f2fs_compress_write_end_io()`, which frees compressed pages, waits until all pending compressed pages finish, ends writeback on raw pages, releases arrays, and decrements writeback counters last.

Read completion uses `f2fs_alloc_dic()` to create a `decompress_io_ctx`, allocate compressed pages, optionally preallocate decompression buffers, and attach the context to compressed folios. `f2fs_end_read_compressed_page()` decrements read counters, marks failure, optionally caches the compressed page, and calls `f2fs_decompress_cluster()` after the last page. Decompression maps buffers, validates compressed length, calls the backend, verifies optional checksums, marks fsck-needed on checksum mismatch, and completes through `f2fs_decompress_end_io()`. If fs-verity is enabled for the inode, decompressed folios are verified on the verity workqueue before unlocking.

Overwrite and truncate paths call `f2fs_prepare_compress_overwrite()` and `prepare_compress_overwrite()` to lock and read the entire compressed cluster into page cache before partial updates. `f2fs_truncate_partial_cluster()` zeroes the partial cluster tail, writes it back, truncates page cache, and truncates blocks after the rounded page boundary.

## State and Persistence Behavior

On disk, a compressed cluster starts with `COMPRESS_ADDR` in the first logical block slot, followed by compressed data blocks in the remaining slots and holes/new addresses for unused tail slots. The compressed byte stream begins with an F2FS compression header containing compressed length, checksum, and reserved fields. In-memory state includes `compress_ctx` raw and compressed page arrays, `compress_io_ctx` for writeback completion, `decompress_io_ctx` for read completion, compressed block counters in the inode, private folio markers using `F2FS_COMPRESSED_PAGE_MAGIC`, and an optional compressed-page cache backed by `sbi->compress_inode` mapping physical block addresses to cached compressed folios.

## Dependencies and Integration Points

This file depends on F2FS node and segment mapping, dnode updates, out-of-place data writeback, fscrypt, fsverity, tracepoints, iostat/page counters, low-memory policy, mount options such as `COMPRESS_CACHE`, slab and mempool allocation, and kernel compression libraries. Kconfig selects which algorithm backends exist; `f2fs_is_compress_backend_ready()` prevents use of unavailable backends for compressed files.

## Risks and Edge Cases

Major risks include partial-cluster updates, fallback correctness when compression expands data, writeback cancellation after partial submission, checkpoint races for quota files, compressed cluster corruption, checksum mismatch handling, memory allocation under low-memory mode, fscrypt bounce-page cleanup, fsverity verification ordering, and use-after-free around `sbi` during writeback completion. The code deliberately decrements page counters last in completion paths and can defer `decompress_io_ctx` freeing to `post_read_wq` outside task context.

## Test Signals

Tests should cover all enabled algorithms and compression levels, compression fallback for incompressible data, encrypted compressed files, verity compressed files, checksum success and mismatch, read I/O failure, partial overwrite of compressed clusters, truncate inside compressed clusters, sparse cluster detection, GC/writeback interaction, quota inode compressed writes, compressed-page cache hit/miss/invalidation, low-memory decompression mode, and Kconfig builds with each backend disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/f2fs/compress.c -->
