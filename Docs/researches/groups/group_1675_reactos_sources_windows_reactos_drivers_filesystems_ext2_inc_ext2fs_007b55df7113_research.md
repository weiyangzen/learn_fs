# Group Research: group_1675_reactos_sources_windows_reactos_drivers_filesystems_ext2_inc_ext2fs_007b55df7113

Scope: `Docs/research_subset_a.md`, focused exactly on the listed ReactOS Ext2Fsd include files. Every listed source file was read completely, including zero-byte placeholders.

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/inc/ext2fs.h -->
# File Research: sources/windows/reactos/drivers/filesystems/ext2/inc/ext2fs.h

This is the central Ext2Fsd/ReactOS ext2 driver header. It pulls in NT kernel/WDK definitions plus Linux-derived ext2/ext3/ext4 format headers, defines driver-wide constants, object types, core control blocks, mount flags, memory accounting helpers, and nearly all cross-module function prototypes.

Major definitions:
- Driver identity and options: `EXT2FSD_VERSION`, `DRIVER_NAME`, device names, registry value names, unload/write/preallocation toggles.
- Filesystem layout aliases: `EXT2_SUPER_BLOCK`, `EXT2_INODE`, `EXT2_GROUP_DESC`, `EXT2_DIR_ENTRY`, block/inode/group size macros, and ext3/ext4 count helpers.
- POSIX mode bits and permission helpers used to translate ext inode modes into Windows access and attributes.
- Pool tags, bugcheck codes, debug levels, trace macros, and memory/IRP accounting hooks.

Core structures:
- `EXT2_GLOBAL`: global driver state, fast I/O/filter/cache callbacks, device objects, mounted VCB list, reaper threads, lookaside lists, codepage and hiding-pattern settings, registry path, and performance counters.
- `EXT2_VCB`: mounted volume state, resources, FCB/MCB lists, volume/device objects, geometry, superblock, block/inode sizing, Linux `block_device`/`super_block`/`ext3_sb_info` shims, and max-file-size limits.
- `EXT2_FCB`: per-open-file control state, cache manager header/resources, section objects, locks, oplock, inode pointer, VCB pointer, MCB pointer, and reference/open counters.
- `EXT2_MCB`: metadata/name tree node containing path names, attributes, timestamps, extents, cached inode, dentry pointer, parent/child/target relationships, and reference count.
- `EXT2_CCB`: per-handle context with search pattern, symlink context, Linux-style `struct file`, and EA iteration index.
- `EXT2_IRP_CONTEXT`: per-request dispatch context with IRP, major/minor function, device/file object, FCB/CCB, wait/defer flags, and exception state.
- `EXT2_EXTENT` and `EXT2_RW_CONTEXT`: block I/O extent chains and async read/write tracking.

Functional surface:
- Declares the full driver API for access checks, disk I/O, cleanup/close, cache callbacks, create/link/symlink lookup, debug/devctl/dirctl/dispatch, EA operations, exception handling, indirect/extents block mapping, superblock/group/inode/block load-save, allocation/freeing, htree directory logic, init/unload, Linux shim lifecycle, byte-range locks, memory/object lifecycle, MCB/VCB tree operations, bitmap consistency, NLS conversion, PnP, read/write, journal recovery, shutdown, and volume information.
- Provides inline ext3 64-bit superblock count accessors and prototypes for ext4 group descriptor helpers.
- Defines Windows-specific write gating through `CanIWrite`, with global ext3 force-write and VCB force-write/read-only flags.

Notable risks:
- This header is very broad and tightly couples nearly every module, so signature drift or macro changes have wide blast radius.
- Several portability branches distinguish ReactOS, GNU NTIFS, Win2K, MSVC, and clang-cl; build behavior can vary by compiler target.
- `CanExt2Wait(IRP)` expands to `IoIsOperationSynchronous(Irp)` and references `Irp` rather than the macro parameter name.
- `S_ISFIL` references `S_IFFIL`, which is not defined in this header.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/inc/ext2fs.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/inc/linux/atomic.h -->
# File Research: sources/windows/reactos/drivers/filesystems/ext2/inc/linux/atomic.h

This header implements a small Linux `atomic_t` compatibility layer on top of Windows interlocked primitives.

Key definitions:
- `atomic_t` wraps a volatile `LONG counter`.
- `ATOMIC_INIT`, `atomic_read`, and `atomic_set`.
- Arithmetic helpers: `atomic_add`, `atomic_sub`, `atomic_inc`, `atomic_dec`.
- Test helpers: `atomic_sub_and_test`, `atomic_dec_and_test`, `atomic_inc_and_test`, `atomic_add_negative`.

Implementation notes:
- Uses `InterlockedExchange`, `InterlockedExchangeAdd`, `InterlockedIncrement`, `InterlockedDecrement`, and `InterlockedCompareExchange`.
- `atomic_sub_and_test` loops with compare-exchange to return whether the post-subtract result is zero.

Notable risk:
- `atomic_add_negative` returns the arithmetic post-add value, not a strict boolean negative test, despite the Linux-style function name.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/inc/linux/atomic.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/inc/linux/bit_spinlock.h -->
# File Research: sources/windows/reactos/drivers/filesystems/ext2/inc/linux/bit_spinlock.h

This is a Linux bit-spinlock compatibility header.

Provided helpers:
- `bit_spin_lock`
- `bit_spin_trylock`
- `bit_spin_unlock`
- `__bit_spin_unlock`
- `bit_spin_is_locked`

Behavior:
- Mirrors Linux bit-lock semantics using `test_and_set_bit_lock`, `test_bit`, `clear_bit_unlock`, `__clear_bit_unlock`, `preempt_disable`, `preempt_enable`, `cpu_relax`, and lock annotation macros.
- Actual bit operations are compiled only under `CONFIG_SMP` or `CONFIG_DEBUG_SPINLOCK`; otherwise the functions largely become preemption/annotation stubs.

Dependency risk:
- This header assumes many Linux kernel macros exist elsewhere in the compatibility layer. If those macros are missing or stubbed too weakly, JBD buffer-state locking becomes semantic rather than real synchronization.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/inc/linux/bit_spinlock.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/inc/linux/bitops.h -->
# File Research: sources/windows/reactos/drivers/filesystems/ext2/inc/linux/bitops.h

This header provides generic Linux-style bit manipulation helpers.

Key definitions:
- Kernel-only bit geometry macros: `BIT`, `BIT_MASK`, `BIT_WORD`, `BITS_TO_LONGS`, `BITS_PER_BYTE`.
- Search helpers: `find_first_zero_bit`, external `find_next_zero_bit`, `__ffs`, `find_first_bit`, `ffz`, `ffs`, `fls`, `fls64`, `fls_long`.
- Iteration macro: `for_each_bit`.
- Order helpers: `get_bitmask_order`, `get_count_order`.
- Rotation helpers: `rol32`, `ror32`.
- Hamming weight helpers: `hweight32`, `hweight64`, `hweight_long`.

Role:
- Supports bitmap scanning, allocation logic, log2 calculations, ext group bitmap handling, and journal bit state helpers.

Notable constraints:
- `find_next_bit` is referenced by `for_each_bit` but not declared in this header.
- The implementation assumes `BITS_PER_LONG`, endian-sized integer typedefs, and some generic macros are supplied by included compatibility headers.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/inc/linux/bitops.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/inc/linux/buffer_head.h -->
# File Research: sources/windows/reactos/drivers/filesystems/ext2/inc/linux/buffer_head.h

This file is zero bytes.

Role:
- Acts as an include placeholder for Linux `buffer_head` compatibility.
- Actual `struct buffer_head` and buffer-state support must come from other headers or source files in the ReactOS Ext2Fsd compatibility layer.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/inc/linux/buffer_head.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/inc/linux/config.h -->
# File Research: sources/windows/reactos/drivers/filesystems/ext2/inc/linux/config.h

This small configuration header enables htree indexed-directory support.

Definitions:
- Include guard `LINUX_CONFIG_H`.
- `EXT2_HTREE_INDEX 1`.
- A commented-out alternative `#undef EXT2_HTREE_INDEX`.

Impact:
- Enables `is_dx(dir)` and related indexed-directory link-count behavior in `ext3_fs.h`.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/inc/linux/config.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/inc/linux/debugfs.h -->
# File Research: sources/windows/reactos/drivers/filesystems/ext2/inc/linux/debugfs.h

This file is zero bytes.

Role:
- Placeholder for Linux `debugfs` includes.
- No debugfs declarations are provided or required by this subset.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/inc/linux/debugfs.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/inc/linux/errno.h -->
# File Research: sources/windows/reactos/drivers/filesystems/ext2/inc/linux/errno.h

This header maps Linux errno values into the compatibility layer.

Behavior:
- Includes host `<errno.h>`.
- For non-ReactOS builds, defines the common Linux errno range from `EPERM` through many network/library errors.
- Some values are defined unconditionally even on ReactOS, including `ENODATA`, `EBADMSG`, `EMSGSIZE`, `EOPNOTSUPP`, network/socket errors from `EADDRINUSE` onward, quota/media errors, internal restart/ioctl codes, and NFSv3-related errors.

Role:
- Lets Linux-derived ext2/ext3/ext4/JBD code return expected negative errno values before conversion through `Ext2WinntError`/`Ext2LinuxError`.

Notable risk:
- Conditional definition avoids clashes with ReactOS for many values but still defines others unconditionally, so compatibility depends on existing system errno headers not defining conflicting macros.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/inc/linux/errno.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/inc/linux/ext2_fs.h -->
# File Research: sources/windows/reactos/drivers/filesystems/ext2/inc/linux/ext2_fs.h

This Linux-derived header defines ext2 on-disk constants, structures, feature masks, directory layout, and kernel prototypes.

Major content:
- ext2 version/debug/preallocation constants.
- Special inode numbers, magic number, link limit, block/fragment sizing macros, inode-size and first-inode macros.
- ACL header and entry structures.
- `struct ext2_group_desc`.
- Direct/indirect block index constants and inode flags, including extents and huge-file flags.
- ioctl command constants.
- `struct ext2_inode`, including OS-dependent Linux/Hurd/Masix fields and extended inode size padding.
- Filesystem state, mount options, error behavior, default reserved uid/gid.
- `struct ext2_super_block` with classic ext2 dynamic revision fields.
- Feature flags and supported/unsupported feature masks.
- `struct ext2_dir_entry`, `struct ext2_dir_entry_2`, file-type enum, and directory record length macro.

Kernel-only declarations:
- Prototypes for ext2 block allocation, directory operations, inode operations, ioctl, superblock operations, and Linux VFS operation tables.

Role in this driver:
- Provides the ext2 on-disk contract used by the master driver header and by compatibility code.
- Also shares feature constants with ext3/ext4 code paths in this ReactOS port.

Notable constraints:
- User-mode feature-test macros assume an `EXT2_SB(sb)->s_es` layout, so callers must pass the expected wrapper, not only a raw superblock.
- Old Linux-era fields and feature masks are retained even when newer ext3/ext4 headers are also included.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/inc/linux/ext2_fs.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/inc/linux/ext3_fs.h -->
# File Research: sources/windows/reactos/drivers/filesystems/ext2/inc/linux/ext3_fs.h

This is the main Linux-derived ext3/ext4 format header for the driver. It defines ext3 on-disk layout plus selected ext4 group descriptor, feature, inode, directory, htree, and MMP structures.

Major content:
- ext3 reservation constants, special inode numbers, link limit, block/fragment size macros.
- `struct ext3_group_desc` and extended `struct ext4_group_desc`.
- `struct flex_groups` and ext4 block group flags.
- ext3/ext4 descriptor sizing and block group macros.
- ext3 and ext4 inode flags, user-visible/modifiable masks, and dynamic inode state bits.
- online resize input/data structures and ioctl constants.
- mount option structure and mount-option bit definitions.
- `struct ext3_inode`, including high size/block/ACL fields and extra timestamp fields.
- `struct ext3_super_block`, extended with journal, htree, descriptor size, 64-bit block count, extra inode size, MMP, RAID, and flex-bg fields.
- `EXT3_SB`, `EXT3_I`, and `ext3_valid_inum` for kernel builds.
- ext3/ext4 feature-test, set, clear, supported-feature, and unsupported-feature constants.
- Directory entry structures, file type constants, Lustre dirent extension helpers, record-length conversion helpers, and htree hash constants.
- Kernel-only htree support structures, `ext3_iloc`, `dir_private_info`, group-first-block helper, MMP structure, xattr ctime flag, and `ext3_match`.

Role:
- Bridges ext3 and partial ext4 compatibility for Ext2Fsd, especially journal-aware metadata, indexed directories, extents flags, large/huge files, and group descriptor checksums.

Notable risks:
- `EXT4_HTREE_EOF_64BIT` appears to be missing a closing parenthesis in the macro definition.
- Many ext4 feature flags are declared, but supported masks only include a subset, so mount/write policy must reject or degrade unsupported volumes correctly.
- `ext3_match` uses `_strnicmp`, making name matching case-insensitive in this port.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/inc/linux/ext3_fs.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/inc/linux/ext3_fs_i.h -->
# File Research: sources/windows/reactos/drivers/filesystems/ext2/inc/linux/ext3_fs_i.h

This header defines ext3/ext4 block-number typedefs and the in-memory ext3 inode sidecar structure.

Key definitions:
- Block group and filesystem block typedefs: `ext3_grpblk_t`, `ext4_grpblk_t`, `ext3_fsblk_t`, `ext4_fsblk_t`, `ext3_lblk_t`, `ext4_lblk_t`, `ext3_group_t`, `ext4_group_t`.
- Reservation window structures: `ext3_reserve_window`, `ext3_reserve_window_node`.
- Block allocation tracking: `ext3_block_alloc_info`.

`struct ext3_inode_info` contains:
- Raw block pointer array, inode flags, ACL/dir/dtime fields, block group, dynamic state, reservation info, directory lookup hint, optional xattr/ACL fields, orphan-list entry, on-disk size tracking, extra inode size, and embedded `struct inode`.

Role:
- Supplies Linux ext3 allocator and inode state expected by borrowed ext3 code.
- In this ReactOS port, `EXT3_I(inode)` returns the inode directly, so only fields mirrored in the local `struct inode` are usable unless the sidecar is explicitly embedded elsewhere.

Notable detail:
- Comments preserve Linux truncate/recovery reasoning around `i_disksize`, but the truncate mutex block is disabled.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/inc/linux/ext3_fs_i.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/inc/linux/ext3_fs_sb.h -->
# File Research: sources/windows/reactos/drivers/filesystems/ext2/inc/linux/ext3_fs_sb.h

This header defines the in-memory ext3 superblock information used by the driver.

Key structures:
- `struct ext3_gd`: group descriptor cache entry with block number, `ext4_group_desc` pointer, and backing `buffer_head`.
- `struct ext3_sb_info`: group descriptor lock/cache, descriptor sizing, group/inode/block geometry, address/descriptor bit counts, raw superblock pointer, first inode, htree hash seed, and default hash version.

Role:
- Provides the `s_fs_info` payload behind `EXT3_SB(sb)` and `EXT4_SB(sb)`.
- Used by group descriptor lookup, inode/block bitmap initialization, htree hashing, and superblock feature checks.

Declared function:
- `ext3_release_dir(struct inode *inode, struct file *filp)`.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/inc/linux/ext3_fs_sb.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/inc/linux/ext3_jbd.h -->
# File Research: sources/windows/reactos/drivers/filesystems/ext2/inc/linux/ext3_jbd.h

This header connects ext3 metadata operations to the JBD journaling layer.

Major content:
- `EXT3_JOURNAL(inode)` accessor.
- Transaction credit constants for single data updates, xattrs, data operations, delete operations, max transaction data, reserve blocks, and htree index operations.
- Quota-aware transaction credit macros, with no-op definitions when quota is disabled.
- Prototypes for inode dirtying and inode write reservation.
- Wrapper prototypes and macros for JBD access: undo/write/create access, revoke, dirty metadata, forget, dirty data, start/stop, extend/restart, current handle, blocks per page, force commit.
- Data-mode decision helpers: `ext3_should_journal_data`, `ext3_should_order_data`, `ext3_should_writeback_data`.

Role:
- Preserves Linux ext3 journaling call structure while allowing ReactOS/Ext2Fsd wrapper functions to add diagnostics and status conversion.

Notable constraints:
- Several helpers rely on `test_opt`, `EXT3_I`, and JBD functions being present and semantically compatible.
- Non-regular files default to journaled data in `ext3_should_journal_data`.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/inc/linux/ext3_jbd.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/inc/linux/ext4.h -->
# File Research: sources/windows/reactos/drivers/filesystems/ext2/inc/linux/ext4.h

This header provides selected ext4 compatibility definitions and includes the ext4 journal and extent headers.

Major content:
- Includes JBD and ext3 format headers.
- Defines Windows-style fixed-width typedefs `uint16_t`, `uint32_t`, `uint64_t`, then ext4 logical and filesystem block typedefs.
- Defines `EXT4_GET_BLOCKS_*` flags for allocation, unwritten extent conversion, delayed allocation, direct I/O, metadata no-fail, fallocate, lock/cache behavior, and unwritten conversion.
- Defines extent lookup/cache flags `EXT4_EX_NOCACHE` and `EXT4_EX_FORCE_CACHE`.
- Defines `EXT4_FREE_BLOCKS_*` flags.
- Defines multiblock allocator hint flags.
- Aliases `ext4_sb_info` to `ext3_sb_info`, provides `EXT4_SB`, and defines `EXT4_I(i)` as identity.

Role:
- Adapts ext4 extent code to the ext3-based in-memory structures used by this driver.
- Does not define a full Linux ext4 VFS layer; it exposes only the pieces needed by Ext2Fsd extent and allocation code.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/inc/linux/ext4.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/inc/linux/ext4_ext.h -->
# File Research: sources/windows/reactos/drivers/filesystems/ext2/inc/linux/ext4_ext.h

This header defines ext4 extent on-disk structures and helper functions.

Key structures:
- `ext4_extent_tail`: extent block checksum tail.
- `EXT4_EXTENT`: leaf extent with logical start, length/unwritten bit, and 48-bit physical start.
- `EXT4_EXTENT_IDX`: internal index entry with logical start and 48-bit leaf pointer.
- `EXT4_EXTENT_HEADER`: extent tree header with magic, entries, max entries, depth, and generation.
- `struct ext4_ext_path`: traversal state for extent lookup, split, insert, and truncate operations.

Key macros/helpers:
- `EXT4_EXT_MAGIC`, `get_ext4_header`, extent tail offset/finder.
- Entry navigation macros for first/last/max extent or index.
- `ext_inode_hdr`, `ext_block_hdr`, and `ext_depth`.
- Initialized/unwritten length helpers using `EXT_INIT_MAX_LEN`.
- Physical block load/store helpers for extents and indexes.
- `INODE_HAS_EXTENT`, `ext_to_block`, `idx_to_block`.
- `ext4_ext_dirty` wrapper macro.

Declared APIs:
- `ext4_ext_get_blocks`
- `ext4_ext_tree_init`
- `ext4_ext_truncate`

Role:
- Enables ext4 extent-tree mapping and truncation paths within the Ext2Fsd driver.
- Uses packed on-disk structs and local endian assumptions through the included ext4/ext3 compatibility layer.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/inc/linux/ext4_ext.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/inc/linux/ext4_jbd2.h -->
# File Research: sources/windows/reactos/drivers/filesystems/ext2/inc/linux/ext4_jbd2.h

This header defines ext4-facing journal wrapper declarations over the JBD layer.

Major APIs:
- `ext4_journal_abort_handle`
- `__ext4_handle_dirty_super`
- `__ext4_journal_get_write_access`
- `__ext4_forget`
- `__ext4_journal_get_create_access`
- `__ext4_handle_dirty_metadata`
- `__ext4_journal_start_sb`
- `__ext4_journal_stop`

Macros:
- Wrap access/forget/dirty/start/stop calls while passing source line and an Ext2Fsd `icb` context.
- `ext4_journal_start` routes through `__ext4_journal_start`.
- `ext4_journal_extend` is a stub returning `0`.

Role:
- Lets ext4 extent/xattr code follow Linux call patterns while carrying ReactOS request context for error handling and metadata writes.

Notable constraint:
- `ext4_journal_extend` does not actually reserve more credits, so callers expecting Linux JBD2 extension semantics may not get real transaction growth.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/inc/linux/ext4_jbd2.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/inc/linux/ext4_xattr.h -->
# File Research: sources/windows/reactos/drivers/filesystems/ext2/inc/linux/ext4_xattr.h

This header defines ext4 extended attribute layout and the Ext2Fsd/lwext4-style xattr management API.

Major content:
- xattr magic, maximum refcount, and name-index constants for user, POSIX ACL, trusted, Lustre, security, system, richacl, and encryption namespaces.
- Packed on-disk structures: `ext4_xattr_header`, `ext4_xattr_ibody_header`, `ext4_xattr_entry`.
- Alignment and navigation macros for xattr entry length, value size, next entry, name pointer, inode-body header/first entry, block header/first entry, and last-entry detection.
- `EXT4_ZERO_XATTR_VALUE` sentinel.

Runtime structures:
- `struct ext4_xattr_item`: one attribute item, including storage choice, namespace/name/data, rb-tree node, and ordered-list node.
- `struct ext4_xattr_ref`: active xattr editing context with IRP context, backing block buffer, inode MCB, raw on-disk inode, dirty flags, remaining inode/block space, VCB pointer, iterator state, rb-tree, and ordered list.

Declared APIs:
- Acquire/release xattr reference: `ext4_fs_get_xattr_ref`, `ext4_fs_put_xattr_ref`.
- Set/remove/get xattr: `ext4_fs_set_xattr`, `ext4_fs_set_xattr_ordered`, `ext4_fs_remove_xattr`, `ext4_fs_get_xattr`.
- Iterate/reset iteration, parse full names, map namespace prefixes, and purge item lists.

Role:
- Supplies extended attribute support for the Windows ext2 driver while using ext4-compatible on-disk xattr formats.

Provenance note:
- This file carries a 2015 lwext4-style permissive license header, unlike the older GPL-derived Linux headers in this group.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/inc/linux/ext4_xattr.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/inc/linux/freezer.h -->
# File Research: sources/windows/reactos/drivers/filesystems/ext2/inc/linux/freezer.h

This file is zero bytes.

Role:
- Placeholder for Linux freezer infrastructure.
- No freeze/thaw task declarations are provided in this compatibility subset.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/inc/linux/freezer.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/inc/linux/fs.h -->
# File Research: sources/windows/reactos/drivers/filesystems/ext2/inc/linux/fs.h

This header defines a minimal Linux VFS compatibility layer.

Key content:
- Device helpers and macros: `kdev_t`, `NODEV`, `MINORBITS`, `MINORMASK`, `MAJOR`, `MINOR`, `MKDEV`, `kdev_t_to_nr`, `to_kdev_t`.
- `struct super_block`: magic, flags, block size/max size, dirt flag, ID, block device, private VCB pointer, root dentry, and filesystem info pointer.
- `struct inode`: inode number, size/timestamps/delete time, block count/pointers, mode, uid/gid, refcount, link count, generation/version/flags, superblock pointer, private MCB pointer, extra inode size, and file ACL.
- Inode dirty/state bit masks.
- `struct dentry`: refcount, name, inode, parent, filesystem data, and superblock.
- `struct file`: flags, mode, version, size, position, dentry, and private data.
- Linux directory type constants.
- Prototypes: `iget`, `iput`, `bmap`.

Role:
- Provides just enough Linux VFS shape for borrowed ext3, htree, JBD, and ext4 extent/xattr code to compile inside the Windows driver.

Notable constraints:
- Device conversion helpers are stubbed to return `0`.
- The structures are simplified and do not provide full Linux VFS semantics.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/inc/linux/fs.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/inc/linux/group.h -->
# File Research: sources/windows/reactos/drivers/filesystems/ext2/inc/linux/group.h

This header declares ext4 group descriptor checksum and bitmap initialization helpers.

Content:
- Prototypes for `ext4_group_desc_csum`, `ext4_group_desc_csum_verify`, `ext4_read_block_bitmap`, `ext4_init_block_bitmap`, `ext4_init_inode_bitmap`, and `mark_bitmap_end`.
- Macro `ext4_free_blocks_after_init` aliases to `ext4_init_block_bitmap`.

Role:
- Supports ext4 group descriptor validation and lazy bitmap initialization code paths.
- Complements the group descriptor definitions in `ext3_fs.h`.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/inc/linux/group.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/inc/linux/highmem.h -->
# File Research: sources/windows/reactos/drivers/filesystems/ext2/inc/linux/highmem.h

This file is zero bytes.

Role:
- Placeholder for Linux highmem mapping APIs.
- No highmem helpers are provided in this compatibility subset.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/inc/linux/highmem.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/inc/linux/init.h -->
# File Research: sources/windows/reactos/drivers/filesystems/ext2/inc/linux/init.h

This file is zero bytes.

Role:
- Placeholder for Linux init/exit annotation macros.
- No module-init annotations are defined here.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/inc/linux/init.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/inc/linux/jbd.h -->
# File Research: sources/windows/reactos/drivers/filesystems/ext2/inc/linux/jbd.h

This is the main Linux JBD journaling header adapted for ReactOS/Ext2Fsd.

Major content:
- JBD includes and compatibility hooks.
- `jbdlock_t` mapped to `FAST_MUTEX`, with init/lock/unlock/assert helpers.
- JBD debug, allocation, and free helpers.
- Opaque `handle_t` and `journal_t` typedefs.
- On-disk journal structures: descriptor types, `journal_header_t`, `journal_block_tag_t`, `journal_revoke_header_t`, `journal_superblock_t`.
- Journal feature-test macros and known feature masks.
- Buffer state bits for JBD integration, buffer flag helper macro invocations, and `jh2bh`/`bh2jh`.
- Bit-spinlock wrappers for buffer state and journal-head locking.
- Concrete `struct handle_s`, `struct transaction_s`, and `struct journal_s`.
- Journal flags such as `JFS_UNMOUNT`, `JFS_ABORT`, `JFS_ACK_ERR`, `JFS_FLUSHED`, `JFS_LOADED`, `JFS_BARRIER`.
- Prototypes for buffer filing, log buffer allocation, commit/checkpoint management, metadata buffer writeout, wait/lock operations, handle lifecycle, journal start/restart/extend/access/dirty/forget/stop/flush/recovery/destroy/abort/error handling, journal-head management, revoke support, log thread control, checkpointing, and tail cleanup.
- Transaction ID comparison helpers `tid_gt` and `tid_geq`.
- Journal buffer list type constants `BJ_*`.

Role:
- Supplies the journaling state machine API and structures needed by ext3 recovery and metadata journaling in the driver.

Notable ReactOS adaptation:
- `journal_current_handle()` is stubbed to return `NULL`.
- Locking uses Windows fast mutexes instead of Linux spinlocks/semaphores for many journal locks.
- `jbd_ENOSYS()` retains Linux-style sleep/schedule behavior and depends on task-state compatibility definitions.

Notable risk:
- This header describes rich Linux JBD semantics; any stubbed compatibility primitive can weaken transaction, checkpoint, or abort behavior if callers assume full Linux behavior.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/inc/linux/jbd.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/inc/linux/journal-head.h -->
# File Research: sources/windows/reactos/drivers/filesystems/ext2/inc/linux/journal-head.h

This header defines JBD per-buffer journal metadata.

Key definitions:
- `tid_t`: transaction ID type.
- `transaction_t`: forward declaration of compound transaction.
- `struct journal_head`: back-pointer to `buffer_head`, reference count, journal list type, modified flag, frozen and committed data copies, owning/current transactions, transaction-list links, checkpoint transaction, and checkpoint-list links.

Role:
- Extends buffer heads with journal ownership and checkpoint metadata.
- Used heavily by JBD transaction, commit, revoke, and checkpoint logic.

Locking notes:
- Comments document expected protection by `jbd_lock_bh_journal_head`, `jbd_lock_bh_state`, and journal list locks.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/inc/linux/journal-head.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/inc/linux/kernel.h -->
# File Research: sources/windows/reactos/drivers/filesystems/ext2/inc/linux/kernel.h

This file is zero bytes.

Role:
- Placeholder for Linux kernel utility macros/functions.
- Required kernel-style helpers are expected from other compatibility headers.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/inc/linux/kernel.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/inc/linux/kthread.h -->
# File Research: sources/windows/reactos/drivers/filesystems/ext2/inc/linux/kthread.h

This file is zero bytes.

Role:
- Placeholder for Linux kthread APIs.
- Threading in this port is handled through Windows thread/event primitives and Ext2Fsd reaper/journal code.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/inc/linux/kthread.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/inc/linux/list.h -->
# File Research: sources/windows/reactos/drivers/filesystems/ext2/inc/linux/list.h

This header implements the classic Linux intrusive doubly linked list API.

Provided elements:
- `struct list_head`
- `LIST_HEAD_INIT`, `LIST_HEAD`, `INIT_LIST_HEAD`
- Internal add/delete helpers: `__list_add`, `__list_del`, `__list_splice`
- Operations: `list_add`, `list_add_tail`, `list_del`, `list_del_init`, `list_move`, `list_move_tail`, `list_empty`, `list_empty_careful`, `list_splice`, `list_splice_init`
- Container/iteration macros: `list_entry`, `list_for_each`, `list_for_each_safe`, `list_for_each_prev`, `list_for_each_entry`, `list_for_each_entry_safe`
- `prefetch(a)` stub.

Role:
- Supports Linux-derived structures such as orphan lists, xattr ordered lists, and other compatibility containers.

Notable constraints:
- No debug poisoning, validation, or concurrency protection is provided.
- Iteration macros use the local `prefetch` no-op/stub.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/inc/linux/list.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/inc/linux/lockdep.h -->
# File Research: sources/windows/reactos/drivers/filesystems/ext2/inc/linux/lockdep.h

This file is zero bytes.

Role:
- Placeholder for Linux lock dependency tracking.
- Lockdep fields and annotations are either compiled out or supplied elsewhere.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/inc/linux/lockdep.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/inc/linux/log2.h -->
# File Research: sources/windows/reactos/drivers/filesystems/ext2/inc/linux/log2.h

This header provides Linux-style integer base-2 helpers.

Key content:
- Declaration for `____ilog2_NaN`.
- Inline `__ilog2_u32` and `__ilog2_u64`, unless architecture overrides are configured.
- `is_power_of_2`.
- Runtime `__roundup_pow_of_two` and `__rounddown_pow_of_two`.
- Macros `ilog2`, `roundup_pow_of_two`, `rounddown_pow_of_two`, and `order_base_2`.

Role:
- Used by allocation, extent, journal, and bitmap code that needs block/order sizing.
- Relies on `fls`, `fls64`, and `fls_long` from `bitops.h`.

Notable behavior:
- The constant `rounddown_pow_of_two(1)` branch returns `0`, matching the file’s current macro text even though callers may expect `1` from a mathematical round-down helper.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/inc/linux/log2.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/inc/linux/magic.h -->
# File Research: sources/windows/reactos/drivers/filesystems/ext2/inc/linux/magic.h

This file is zero bytes.

Role:
- Placeholder for Linux filesystem magic constants.
- ext2/ext3 magic values used by this subset are defined directly in the ext2/ext3 headers.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/inc/linux/magic.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/inc/linux/mm.h -->
# File Research: sources/windows/reactos/drivers/filesystems/ext2/inc/linux/mm.h

This file is zero bytes.

Role:
- Placeholder for Linux memory-management declarations.
- Memory allocation and cache behavior are provided through other Ext2Fsd and compatibility headers.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/inc/linux/mm.h -->