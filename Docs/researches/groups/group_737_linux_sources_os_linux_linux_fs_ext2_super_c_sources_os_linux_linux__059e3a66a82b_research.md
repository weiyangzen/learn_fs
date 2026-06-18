# Group Research: group_737_linux_sources_os_linux_linux_fs_ext2_super_c_sources_os_linux_linux__059e3a66a82b

Scope verified against `Docs/research_subset_a.md`. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ext2/super.c -->
# File Research: sources/os/linux/linux/fs/ext2/super.c

## Purpose
Implements ext2 filesystem registration, mount/remount, superblock validation, superblock lifecycle, statfs, sync/freeze handling, NFS export hooks, quota hooks, mount-option parsing, inode slab setup, and module init/exit.

## Main Responsibilities
- `ext2_fill_super()` is the central mount path: allocates `ext2_sb_info`, reads the on-disk superblock, validates magic/features/block size/inode size/group geometry/device size, loads group descriptors, initializes reservation windows, counters, xattr cache, quota ops, super ops, export ops, and root inode.
- `ext2_parse_param()` and `ext2_set_options()` implement the fs_context mount API and merge parsed options with on-disk defaults.
- `ext2_reconfigure()` handles remount transitions, including read-only/read-write state changes, quota suspend/resume, POSIX ACL flag updates, and refusal to change DAX while busy.
- `ext2_sync_super()`, `ext2_sync_fs()`, `ext2_write_super()`, `ext2_freeze()`, and `ext2_unfreeze()` maintain on-disk superblock counters and validity/error state.
- `ext2_error()` marks the filesystem errored, syncs the superblock, and applies `errors=continue|panic|remount-ro`.

## Integration Points
Registers `ext2_fs_type` through `register_filesystem()`, uses VFS `super_operations`, fs_context parsing, buffer-head block IO, quota APIs, DAX device discovery, xattr/ACL hooks, and generic NFS file-handle helpers.

## Important Behaviors
The mount path rejects unsupported incompatible features, rejects read-write mounts with unsupported read-only-compatible features, verifies group descriptors, validates root inode shape, and warns on unchecked/error/check-interval/max-mount-count states. DAX support is accepted only when the block device supports it and the block size equals page size; the driver logs a deprecation warning for ext2 DAX.

## Risks and Edge Cases
Most failure paths funnel through carefully ordered cleanup labels; future edits must preserve partial-initialization ordering. Remount state changes mix spinlock-protected superblock fields with quota and IO operations, so lock ordering matters. `statfs` caches overhead based on block count and updates free counters in the on-disk superblock image.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ext2/super.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ext2/symlink.c -->
# File Research: sources/os/linux/linux/fs/ext2/symlink.c

## Purpose
Defines inode operations for ext2 symlinks.

## Main Responsibilities
- `ext2_symlink_inode_operations` uses `page_get_link` for regular symlinks stored through page/cache-backed data.
- `ext2_fast_symlink_inode_operations` uses `simple_get_link` for fast symlinks stored directly in inode data.
- Both operation tables expose ext2 `getattr`, `setattr`, and `listxattr`.

## Integration Points
Used by inode creation/loading code to attach the right symlink behavior depending on whether the symlink is fast or block-backed. Integrates with ext2 xattr listing so symlinks can expose extended attributes.

## Risks and Edge Cases
This file is intentionally minimal; correctness depends on inode code selecting the matching operations table for fast versus non-fast symlinks.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ext2/symlink.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ext2/trace.c -->
# File Research: sources/os/linux/linux/fs/ext2/trace.c

## Purpose
Materializes ext2 tracepoint definitions.

## Main Responsibilities
Defines `CREATE_TRACE_POINTS` before including `trace.h`, causing the tracepoint storage and registration code for ext2 direct-IO trace events to be generated in exactly one translation unit.

## Integration Points
Includes `ext2.h`, `linux/uio.h`, and local `trace.h`. The trace events are consumed by ext2 IO paths that include `trace.h` without `CREATE_TRACE_POINTS`.

## Risks and Edge Cases
This file must remain the single tracepoint definition unit. Duplicating `CREATE_TRACE_POINTS` elsewhere would cause link conflicts.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ext2/trace.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ext2/trace.h -->
# File Research: sources/os/linux/linux/fs/ext2/trace.h

## Purpose
Declares ext2 tracepoints for direct IO read/write activity.

## Main Responsibilities
- Defines `TRACE_SYSTEM ext2`.
- Declares reusable `ext2_dio_class` with device, inode, inode size, IO position, byte count, kiocb flags, sync/async status, and return value.
- Instantiates events for direct IO write begin/end/buffered fallback end and read begin/end.
- Declares `ext2_dio_write_endio` with completed size and endio return status.

## Integration Points
Uses Linux tracepoint infrastructure and `TRACE_IOCB_STRINGS` for flag rendering. The header sets `TRACE_INCLUDE_PATH .` and `TRACE_INCLUDE_FILE trace` for kernel trace generation.

## Risks and Edge Cases
Event fields dereference `iocb->ki_filp` and its inode, so callers must pass valid IO control blocks. Output semantics depend on callers passing the correct `ret` or `size` at each IO phase.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ext2/trace.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ext2/xattr.c -->
# File Research: sources/os/linux/linux/fs/ext2/xattr.c

## Purpose
Implements ext2 extended attribute storage, lookup, listing, mutation, sharing, hashing, cache management, and inode cleanup.

## Main Responsibilities
- Stores xattrs in a single external EA block referenced by `EXT2_I(inode)->i_file_acl`.
- `ext2_xattr_get()` validates the EA block and entries, finds the sorted name/index entry, and copies or sizes the value.
- `ext2_xattr_list()` validates the block, filters namespace visibility through handlers, and emits prefixed names.
- `ext2_xattr_set()` creates, replaces, or removes attributes, preserving sorted entries and compact value layout.
- `ext2_xattr_set2()` updates inode state, reuses identical cached blocks, allocates new EA blocks, releases old blocks, updates quotas, and marks metadata dirty.
- `ext2_xattr_delete_inode()` releases the inode’s EA block on inode deletion.
- Hash and mbcache helpers enable sharing identical EA blocks by content hash and refcount.

## Integration Points
Uses ext2 block allocation/freeing, quota initialization/accounting, buffer-head IO, superblock feature updates, `mb_cache`, namespace handlers from user/trusted/security/ACL code, and inode xattr semaphores.

## Important Behaviors
EA blocks are copy-on-write unless exclusively owned and not being reused. The code validates magic, block count, entry boundaries, value offsets, and unsupported external value blocks. Setting the first xattr upgrades the superblock to dynamic revision and sets `EXT2_FEATURE_COMPAT_EXT_ATTR`.

## Risks and Edge Cases
Locking is delicate: inode `xattr_sem` protects `i_file_acl`, buffer locks serialize shared block refcount/content changes, and mbcache races are handled with delete-or-get/wait paths. Corrupt xattr blocks trigger `ext2_error()`. Attribute size is limited by filesystem block size.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ext2/xattr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ext2/xattr.h -->
# File Research: sources/os/linux/linux/fs/ext2/xattr.h

## Purpose
Defines ext2 on-disk extended attribute format, alignment helpers, namespace indexes, and xattr API declarations or stubs.

## Main Responsibilities
- Declares `ext2_xattr_header` and `ext2_xattr_entry`.
- Defines namespace indexes for user, POSIX ACL access/default, trusted, Lustre, and security attributes.
- Provides alignment/size macros: `EXT2_XATTR_LEN`, `EXT2_XATTR_NEXT`, and `EXT2_XATTR_SIZE`.
- Exposes get/set/list/delete/cache APIs when `CONFIG_EXT2_FS_XATTR` is enabled.
- Provides `-EOPNOTSUPP` stubs and null handlers when xattr support is disabled.
- Declares or stubs `ext2_init_security()` based on `CONFIG_EXT2_FS_SECURITY`.

## Integration Points
Included by ext2 inode, symlink, ACL, security, and xattr implementation files. It bridges VFS xattr handlers with ext2’s disk layout.

## Risks and Edge Cases
The layout macros define the parser/writer contract for `xattr.c`; changing padding or entry sizing would alter disk compatibility.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ext2/xattr.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ext2/xattr_security.c -->
# File Research: sources/os/linux/linux/fs/ext2/xattr_security.c

## Purpose
Implements ext2 `security.*` extended attribute support for Linux security modules.

## Main Responsibilities
- Defines get/set handler wrappers around `ext2_xattr_get()` and `ext2_xattr_set()` using `EXT2_XATTR_INDEX_SECURITY`.
- Implements `ext2_initxattrs()` to write all security xattrs supplied during inode initialization.
- `ext2_init_security()` delegates to `security_inode_init_security()`.

## Integration Points
Connects ext2 inode creation to LSM-provided labels such as SELinux contexts. Exposes `ext2_xattr_security_handler` with `XATTR_SECURITY_PREFIX`.

## Risks and Edge Cases
Initialization stops on the first failed xattr write. Security labeling depends on ext2 xattr support and available EA block space.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ext2/xattr_security.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ext2/xattr_trusted.c -->
# File Research: sources/os/linux/linux/fs/ext2/xattr_trusted.c

## Purpose
Implements ext2 `trusted.*` extended attribute namespace handling.

## Main Responsibilities
- Lists trusted attributes only for callers with `CAP_SYS_ADMIN`.
- Routes get/set operations to `ext2_xattr_get()` and `ext2_xattr_set()` with `EXT2_XATTR_INDEX_TRUSTED`.
- Registers `ext2_xattr_trusted_handler` under `XATTR_TRUSTED_PREFIX`.

## Integration Points
Used by the ext2 xattr handler table and VFS xattr dispatch.

## Risks and Edge Cases
Visibility is capability-gated for listing, while actual get/set permission checks are also governed by VFS xattr policy. Storage limitations and corruption behavior are inherited from `xattr.c`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ext2/xattr_trusted.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ext2/xattr_user.c -->
# File Research: sources/os/linux/linux/fs/ext2/xattr_user.c

## Purpose
Implements ext2 `user.*` extended attribute namespace handling.

## Main Responsibilities
- Lists user attributes only when the `XATTR_USER` mount option is enabled.
- Rejects get/set with `-EOPNOTSUPP` when `XATTR_USER` is disabled.
- Routes enabled get/set operations to `ext2_xattr_get()` and `ext2_xattr_set()` using `EXT2_XATTR_INDEX_USER`.
- Registers `ext2_xattr_user_handler` under `XATTR_USER_PREFIX`.

## Integration Points
Driven by mount options parsed in `super.c` and used by VFS xattr dispatch.

## Risks and Edge Cases
User xattrs can be present on disk but hidden/inaccessible if the mount option is disabled.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ext2/xattr_user.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ext4/Kconfig -->
# File Research: sources/os/linux/linux/fs/ext4/Kconfig

## Purpose
Defines kernel configuration options for building ext4 and optional ext4 features.

## Main Responsibilities
- `EXT4_FS` selects required infrastructure: buffer heads, JBD2, CRC helpers, iomap, and encryption algorithms when fs encryption is enabled.
- `EXT4_USE_FOR_EXT2` allows ext4 to mount ext2 filesystems when ext2 is not built.
- `EXT4_FS_POSIX_ACL` enables POSIX ACL support and selects `FS_POSIX_ACL`.
- `EXT4_FS_SECURITY` enables security label xattr support.
- `EXT4_DEBUG` enables runtime debug messages.
- `EXT4_KUNIT_TESTS` builds ext4 KUnit tests.

## Integration Points
Controls which objects are compiled by the ext4 Makefile and which VFS/security/fscrypt features are available.

## Risks and Edge Cases
`EXT4_USE_FOR_EXT2` changes which driver services ext2 mounts. Optional ACL/security/encryption support affects on-disk feature usability and mount/runtime behavior.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ext4/Kconfig -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ext4/Makefile -->
# File Research: sources/os/linux/linux/fs/ext4/Makefile

## Purpose
Defines ext4 object composition for the kernel build.

## Main Responsibilities
- Builds `ext4.o` when `CONFIG_EXT4_FS` is enabled.
- Lists core ext4 objects covering allocation, bitmap validation, directory handling, journaling glue, extents, inode/file operations, resize, superblock, symlink, sysfs, xattrs, fast commits, and orphan handling.
- Conditionally adds ACL, security xattr, verity, encryption, and KUnit test objects.

## Integration Points
Consumes Kconfig symbols from `fs/ext4/Kconfig` and feeds kbuild.

## Risks and Edge Cases
Feature object inclusion must match declarations used in headers; missing conditional objects would produce unresolved symbols or disabled feature stubs.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ext4/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ext4/acl.c -->
# File Research: sources/os/linux/linux/fs/ext4/acl.c

## Purpose
Implements ext4 POSIX ACL conversion, retrieval, setting, and new-inode ACL initialization.

## Main Responsibilities
- `ext4_acl_from_disk()` validates and converts ext4 xattr ACL bytes into `struct posix_acl`.
- `ext4_acl_to_disk()` serializes in-memory ACLs to ext4 ACL xattr format.
- `ext4_get_acl()` fetches access/default ACL xattrs and converts them.
- `ext4_set_acl()` starts a journal transaction, updates mode for access ACLs via `posix_acl_update_mode()`, writes the xattr, marks inode dirty when needed, and retries allocation on ENOSPC.
- `ext4_init_acl()` derives ACLs from the parent directory during inode creation and writes default/access ACL xattrs with `XATTR_CREATE`.

## Integration Points
Uses ext4 xattr APIs, JBD2 handles, quota initialization, inode dirtying, POSIX ACL core helpers, and idmapped mount information for mode updates.

## Risks and Edge Cases
Default ACLs are valid only on directories. ACL xattr sizing affects journal credit calculation. Disk parsing rejects malformed entry counts, unknown tags, truncated entries, and trailing bytes.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ext4/acl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ext4/acl.h -->
# File Research: sources/os/linux/linux/fs/ext4/acl.h

## Purpose
Defines ext4 POSIX ACL disk structures, sizing helpers, and ACL API declarations/stubs.

## Main Responsibilities
- Defines `EXT4_ACL_VERSION`, ACL header, full entry, and short entry formats.
- `ext4_acl_size()` computes serialized ACL xattr size.
- `ext4_acl_count()` validates a serialized size and returns the number of ACL entries.
- Declares `ext4_get_acl()`, `ext4_set_acl()`, and `ext4_init_acl()` when ACL support is enabled.
- Provides null/stub behavior when `CONFIG_EXT4_FS_POSIX_ACL` is disabled.

## Integration Points
Used by `acl.c`, inode creation, and inode operation tables.

## Risks and Edge Cases
The first four ACL entries are encoded in short form unless user/group IDs are needed; sizing/count logic must stay compatible with `acl.c` parsing.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ext4/acl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ext4/balloc.c -->
# File Research: sources/os/linux/linux/fs/ext4/balloc.c

## Purpose
Implements ext4 block-group arithmetic, block bitmap initialization/validation/loading, free-cluster accounting, allocation retry policy, metadata block allocation wrapper, and metadata overhead calculations.

## Main Responsibilities
- `ext4_get_group_number()` and `ext4_get_group_no_and_offset()` map filesystem block numbers to groups and bitmap offsets.
- `ext4_num_overhead_clusters()` and related helpers compute per-group metadata overhead, including superblocks, group descriptors, bitmaps, and inode tables.
- `ext4_init_block_bitmap()` initializes uninitialized group block bitmaps and marks metadata/padding bits.
- `ext4_get_group_desc()` retrieves group descriptors from the RCU-managed descriptor buffer array.
- `ext4_read_block_bitmap_nowait()`, `ext4_wait_block_bitmap()`, and `ext4_read_block_bitmap()` load and verify block bitmaps.
- `ext4_validate_block_bitmap()` verifies checksums, required metadata bits, and padding bits, then marks corrupt group bitmaps.
- `ext4_has_free_clusters()` and `ext4_claim_free_clusters()` enforce reserved-block, dirty-cluster, root-reserved, and allocation-reserved accounting.
- `ext4_should_retry_alloc()` decides whether ENOSPC paths should wait for journal commits or discard work and retry.
- `ext4_new_meta_blocks()` wraps multiblock allocation for metadata and accounts quota for delayed-allocation reservations.
- `ext4_bg_has_super()`, `ext4_bg_num_gdb()`, and `ext4_num_base_meta_blocks()` compute backup super/GDT placement.

## Integration Points
Uses ext4 group descriptors, block/inode bitmap checksum helpers, mballoc, JBD2, quota accounting, mount options, flex_bg/meta_bg/sparse_super features, KUnit static stubs, and tracepoints.

## Risks and Edge Cases
Bitmap validation is central corruption defense; failures mark group bitmaps corrupt and can remount/error the filesystem. Bigalloc cluster math, flex_bg layouts, meta_bg layouts, and last-group sizing make off-by-one errors high risk. Allocation retry is intentionally bounded to avoid infinite ENOSPC loops.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ext4/balloc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ext4/bitmap.c -->
# File Research: sources/os/linux/linux/fs/ext4/bitmap.c

## Purpose
Provides ext4 bitmap utility and metadata checksum helpers.

## Main Responsibilities
- `ext4_count_free()` counts unset bits in a bitmap using `memweight()`.
- `ext4_inode_bitmap_csum_verify()` and `_set()` verify/store inode bitmap checksums in group descriptors.
- `ext4_block_bitmap_csum_verify()` and `_set()` verify/store block bitmap checksums in group descriptors.

## Integration Points
Used by block/inode allocation and bitmap validation paths. Relies on `metadata_csum`, ext4 checksum seed, descriptor size, and low/high checksum fields.

## Risks and Edge Cases
Checksum byte length differs for inode and block bitmaps. High checksum fields are present only with sufficiently large group descriptors; otherwise calculated checksums are truncated to 16 bits.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ext4/bitmap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ext4/block_validity.c -->
# File Research: sources/os/linux/linux/fs/ext4/block_validity.c

## Purpose
Tracks filesystem metadata block ranges so ext4 can reject file mappings that overlap protected system zones.

## Main Responsibilities
- Maintains an RCU-protected red-black tree of `ext4_system_zone` ranges.
- `ext4_setup_system_zone()` builds the tree from each group’s base metadata, block bitmap, inode bitmap, inode table, and internal journal inode blocks when present.
- `add_system_zone()` inserts non-overlapping ranges and merges adjacent ranges belonging to the same inode marker.
- `ext4_release_system_zone()` swaps out the tree and frees it after an RCU grace period.
- `ext4_sb_block_valid()` checks a block range against filesystem bounds and system-zone overlap.
- `ext4_inode_block_valid()` applies the check for an inode.
- `ext4_check_blockref()` validates arrays of block references and reports corrupt references.

## Integration Points
Uses ext4 group metadata helpers, inode block mapping, journal inode awareness, RCU, rbtrees, slab cache lifecycle, and ext4 error reporting.

## Risks and Edge Cases
Overlap while building the system zone is treated as corruption. RCU is required because block validation can run concurrently with remount changes that enable/disable block validity. Journal inode blocks are allowed for the journal inode itself but protected from regular file mappings.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ext4/block_validity.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ext4/crypto.c -->
# File Research: sources/os/linux/linux/fs/ext4/crypto.c

## Purpose
Implements ext4 integration with fscrypt filename handling, encryption policy/context storage, password salt ioctl, and fscrypt operation registration.

## Main Responsibilities
- Converts `fscrypt_name` into `ext4_filename` through `ext4_fname_from_fscrypt_name()`.
- `ext4_fname_setup_filename()` and `ext4_fname_prepare_lookup()` prepare encrypted and casefold-aware names for create/lookup paths.
- `ext4_fname_free_filename()` releases fscrypt and casefold buffers.
- `ext4_ioctl_get_encryption_pwsalt()` returns or lazily generates the filesystem encryption password salt in the superblock under a journal transaction.
- `ext4_get_context()` reads encryption context xattrs.
- `ext4_set_context()` writes encryption context xattrs, handles new-inode versus existing-inode transaction modes, rejects root-directory encryption, rejects DAX conflicts, converts inline data, sets inode encryption flags, and retries ENOSPC where appropriate.
- Registers `ext4_cryptops` for fscrypt.

## Integration Points
Uses fscrypt, ext4 xattrs, JBD2, quota initialization, inline-data conversion, inode flag synchronization, superblock checksums, random UUID generation, and mount write access.

## Risks and Edge Cases
Root directory encryption is forbidden because `lost+found` expectations would break. Existing nonempty DAX inodes and DAX-flagged inodes cannot receive encryption context. Salt generation mutates the superblock and must update checksum and journal metadata.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ext4/crypto.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ext4/dir.c -->
# File Research: sources/os/linux/linux/fs/ext4/dir.c

## Purpose
Implements ext4 directory file operations, directory entry validation, linear and htree readdir, htree seek-position mapping, encrypted-name emission, and per-open directory iteration state.

## Main Responsibilities
- `is_dx_dir()` detects htree-indexed or potentially indexed directories.
- `__ext4_check_dir_entry()` validates rec_len, alignment, name length, block bounds, checksum-tail placement, inode range, and invalid terminal `"."` entries.
- `ext4_readdir()` handles fscrypt preparation, htree fallback, inline directories, linear block mapping, readahead, checksum verification, i_version rescan safety, encrypted filename conversion, and `dir_emit()`.
- Hash/position helpers convert htree major/minor hashes to 32-bit or 64-bit directory offsets.
- `ext4_dir_llseek()` seeks by htree hash space for indexed directories and resets cached iteration state.
- `ext4_htree_store_dirent()` stores htree entries in a red-black tree ordered by hash/minor hash, with linked-list collision chains.
- `ext4_dx_readdir()` fills and drains the htree-sorted rb tree, preserving state across calls and handling hash-collision leftovers.
- `ext4_check_all_de()` validates all entries in a directory buffer.
- `ext4_dir_open()` allocates per-file private iteration state; `ext4_release_dir()` frees it.
- Exports `ext4_dir_operations`.

## Integration Points
Uses ext4 block mapping/bread, htree fill logic from other ext4 directory code, fscrypt, casefold hash metadata, metadata checksums, file readahead, inode i_version, VFS dir context, ioctl/fsync hooks, and generic lease handling.

## Risks and Edge Cases
Directory corruption handling skips bad blocks/entries and reports ext4 errors. Htree offsets are hash-derived, so 32-bit compatibility affects seek cookies. Encrypted and casefolded directories require hash/minor-hash preservation for stable userspace names. The per-open rb tree must be invalidated when directory i_version changes.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ext4/dir.c -->