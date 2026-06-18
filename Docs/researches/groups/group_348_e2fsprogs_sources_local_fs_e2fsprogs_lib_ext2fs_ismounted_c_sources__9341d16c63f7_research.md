# Group Research: group_348_e2fsprogs_sources_local_fs_e2fsprogs_lib_ext2fs_ismounted_c_sources__9341d16c63f7

Scope checked against `Docs/research_subset_a.md`. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/ismounted.c -->
# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/ismounted.c

Implements libext2fs mount/busy detection. The public entry points are `ext2fs_check_mount_point()` and `ext2fs_check_if_mounted()`, returning `EXT2_MF_MOUNTED`, `EXT2_MF_ISROOT`, `EXT2_MF_READONLY`, `EXT2_MF_SWAP`, `EXT2_MF_BUSY`, and `EXT2_MF_EXTFS`.

On Linux it first probes block devices with `open(O_RDONLY | O_EXCL)` to cheaply determine whether the device is busy. It then checks `/proc/swaps`, `/proc/mounts`, and configured mtab paths via `getmntent`, with extra handling for loop-mounted regular files by comparing loop backing inode/device metadata.

The root filesystem path receives special treatment because mount tables may report `/dev/root`; the code compares the candidate device number against `stat("/")` and probes writability by creating `/.ismount-test-file`.

Important behaviors: environment variables can force pretend mounted states for tests, missing mtab can be ignored via `EXT2FS_NO_MTAB_OK`, and non-Linux platforms use `getmntinfo` when available. String copies to `mtpt` use `strncpy` with caller-supplied length and may not NUL-terminate if the mount path exactly fills the buffer.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/ismounted.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/jfs_compat.h -->
# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/jfs_compat.h

Provides userspace compatibility definitions so JBD/JBD2-derived journal code can compile inside e2fsprogs. It maps kernel-style endian helpers, allocation flags, logging macros, CRC helpers, spinlocks, and buffer-head conventions onto libext2fs equivalents or no-op stubs.

Defines the userspace `journal_s` structure used by journal replay/creation code, including superblock pointers, block ranges, transaction sequence fields, revoke tables, checksum seed, and fast-commit replay callback.

This header is intentionally not a full kernel emulation layer. Many kernel concepts are reduced to constants or no-ops, so code using it must not assume real locking, GFP behavior, or kernel logging semantics.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/jfs_compat.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/kernel-jbd.h -->
# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/kernel-jbd.h

Defines JBD2 on-disk journal metadata used by e2fsprogs: journal headers, commit headers, block tags, revoke headers, journal superblocks, checksum fields, feature bits, and transaction id helpers.

Key constants include `JBD2_MAGIC_NUMBER`, block type IDs, checksum feature bits, 64-bit and fast-commit incompat features, minimum/default journal sizing, and tag flags such as `JBD2_FLAG_ESCAPE`, `SAME_UUID`, and `LAST_TAG`.

Inline helpers generate feature predicates and setters/clearers for checksum, revoke, 64-bit, async commit, checksum v2/v3, and fast commit. `journal_tag_bytes()` adjusts descriptor tag size based on checksum and 64-bit features.

This is a structural compatibility header, not journal execution logic. Its main risk surface is format drift: these definitions must stay aligned with kernel JBD2 layout because journal replay and mkjournal depend on byte-exact on-disk structures.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/kernel-jbd.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/kernel-list.h -->
# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/kernel-list.h

Small Linux-style doubly linked list implementation. It defines `struct list_head`, initialization macros, insertion at head/tail, deletion, emptiness check, splice, and `list_entry()` via `container_of`.

The implementation is minimal and assumes callers maintain object lifetime and avoid double deletion. It is used as compatibility infrastructure by kernel-derived userspace code.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/kernel-list.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/link.c -->
# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/link.c

Implements directory entry creation via `ext2fs_link()` plus htree-indexed directory support. It handles both linear directories and indexed ext4 htree directories.

The linear path uses `link_proc()` over directory iteration, absorbing adjacent empty entries, splitting oversized entries, writing inode/name/type fields, and honoring metadata checksum tail space. It can append only to the last block when `EXT2FS_LINK_APPEND` is set.

The indexed path performs htree lookup, directory hash calculation with casefold support, leaf insertion, leaf splitting, internal node splitting, tree-depth growth, and conversion of a one-block directory into an indexed directory when the filesystem supports dir_index.

Important symbols: `dx_lookup`, `dx_split_leaf`, `dx_grow_tree`, `try_make_indexed_dir`, `ext2fs_dir_is_dx`, `ext2fs_inc_nlink`, `ext2fs_dec_nlink`, `ext2fs_dir_link_max`, and `ext2fs_dir_link_empty`.

Key invariants: directory block checksum tails reduce usable entry space; htree hash version must be supported; uninitialized mapped blocks are treated as corruption; directory nlink overflow can be represented as `i_links_count == 1` for indexed directories when the feature permits it.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/link.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/llseek.c -->
# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/llseek.c

Portable large-file seek wrapper exported as `ext2fs_llseek()`. On Linux it chooses between native `lseek`, `lseek64`, `llseek`, or the `_llseek` syscall depending on configure results.

If the kernel lacks llseek support, it falls back to regular `lseek` only when the requested offset fits in `off_t`; otherwise it returns `EINVAL`. Non-Linux platforms use `lseek64` when available or perform the same range check.

This file is foundational for raw image/device code that needs offsets beyond 2 GiB on older systems.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/llseek.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/lookup.c -->
# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/lookup.c

Implements `ext2fs_lookup()`, a simple directory name lookup over `ext2fs_dir_iterate()`. The callback compares requested name length and bytes against each dirent and aborts iteration on match.

Returns the found inode through the caller pointer, or `EXT2_ET_FILE_NOT_FOUND` when no entry matches. This is a low-level exact-byte lookup; higher-level casefold or path traversal behavior is handled elsewhere.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/lookup.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/mkdir.c -->
# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/mkdir.c

Implements `ext2fs_mkdir2()` and compatibility wrapper `ext2fs_mkdir()`. It allocates a directory inode and either a real data block or inline directory data depending on filesystem features and inode number.

The function builds a new directory template, initializes mode, size, extents/inline-data flags, link count, timestamps via `ext2fs_write_new_inode`, and then links the directory into its parent with `ext2fs_link()` after checking for name collisions.

It updates block/inode allocation accounting and increments the parent directory link count. Cleanup paths drop allocation stats if linking or inode writing fails after allocation, but they do not perform a full semantic rollback of all possible on-disk writes.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/mkdir.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/mkjournal.c -->
# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/mkjournal.c

Creates journal superblocks, journal files, journal inodes, and external journal links. Main public functions include `ext2fs_create_journal_superblock2`, `ext2fs_zero_blocks2`, `ext2fs_get_journal_params`, `ext2fs_add_journal_device`, and `ext2fs_add_journal_inode3`.

Journal superblocks are initialized with JBD2 magic, block size, max length including fast-commit blocks, UUID, sequence, and external-journal offsets when needed. Journal sizing uses filesystem block count with bounds and splits fast-commit space when enabled.

Mounted filesystems use POSIX `.journal` file creation and disable lazy initialization because writes allocate blocks. Unmounted filesystems allocate `EXT2_JOURNAL_INO` directly with `ext2fs_fallocate`, write the journal superblock, and back up journal block mapping in the superblock.

Risk points: mounted journal creation relies on mount detection, file flags/ioctls, and host filesystem behavior; `ext2fs_zero_blocks2` uses a static reusable zero buffer; external journal setup validates block device type, JBD2 superblock magic/type, block size, and user UUID slots.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/mkjournal.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/mmp.c -->
# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/mmp.c

Implements ext4 multiple mount protection helpers. When `CONFIG_MMP` is enabled, it reads and writes the MMP block, initializes it, starts/stops ownership, and periodically updates the fsck sequence.

Reads use a separate file descriptor and `O_DIRECT` when suitable to avoid stale cached MMP data. Checks include block range validation, checksum verification unless ignored, magic validation, endian swapping, and aligned buffer allocation based on direct I/O requirements.

`ext2fs_mmp_start()` performs the protection handshake: read current sequence, wait if another sequence is active, verify it did not change, write a fresh random sequence, wait again, verify ownership, then write `EXT4_MMP_SEQ_FSCK`.

`ext2fs_mmp_stop()` and `ext2fs_mmp_update2()` compare the saved buffer with freshly read disk state before writing. A mismatch returns `EXT2_ET_MMP_CHANGE_ABORT`, signaling that pending filesystem modifications should be abandoned.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/mmp.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/namei.c -->
# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/namei.c

Implements pathname traversal for libext2fs. Public entry points are `ext2fs_namei()`, `ext2fs_namei_follow()`, and `ext2fs_follow_link()`.

`dir_namei()` walks path components relative to a root and cwd, resetting to root on absolute paths. It uses `ext2fs_lookup()` for each component and can follow symlinks between components.

`follow_link()` supports fast symlinks stored in `i_block`, inline-data symlinks, and block-backed symlinks. It enforces `EXT2FS_MAX_NESTED_LINKS` to prevent symlink loops.

The implementation uses caller-sized block buffers for lookup and raw symlink block reads. It does not implement Unix permission checks; it resolves ext filesystem metadata paths only.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/namei.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/native.c -->
# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/native.c

Tiny endianness helper file. It exports `ext2fs_native_flag()` returning `EXT2_FLAG_SWAP_BYTES` on big-endian builds and `0` on little-endian builds.

Callers can use this to determine whether on-disk ext metadata needs byte swapping relative to the host.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/native.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/newdir.c -->
# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/newdir.c

Builds new directory data templates. `ext2fs_new_dir_block()` allocates and initializes a full directory block containing `.` and `..` entries when a directory inode is supplied.

It reserves metadata checksum tail space when enabled and initializes the dirent tail. Filetype fields are set only when the filesystem has the filetype feature.

`ext2fs_new_dir_inline_data()` initializes inline directory data by storing the parent inode in the inline dotdot area and creating the remaining empty dirent record, with big-endian output swabbing when required.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/newdir.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/nls_utf8.c -->
# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/nls_utf8.c

Userspace UTF-8 normalization and casefold support adapted from Linux so ext4 casefold hashes and comparisons match kernel behavior. It includes generated Unicode trie data via `utf8data.h`.

The code validates UTF-8, looks up code point metadata through a compact trie, performs canonical decomposition, removes default-ignorable code points, handles Hangul syllable decomposition algorithmically, and emits normalized bytes ordered by canonical combining class.

Public-facing helpers load the UTF-8 12.1 table with `ext2fs_load_nls_table()`, validate names through `ext2fs_check_encoded_name()`, and compare casefolded names through `ext2fs_casefold_cmp()`.

Invalid sequences return validation errors, casefold output can fail with `-ENAMETOOLONG`, and only `EXT4_ENC_UTF8_12_1` is supported by this table.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/nls_utf8.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/nt_io.c -->
# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/nt_io.c

Implements a Windows NT-native libext2fs I/O manager. It exposes `nt_io_manager()` and supplies open, close, set block size, read block, write block, and flush operations.

The file declares NT native APIs directly, maps NT/DOS errors to errno-style values, normalizes device names from drive letters and Unix-like names, opens devices with retry and read-only fallback, and supports lock, unlock, dismount, mounted check, flush, and partition type update operations.

I/O uses raw `NtReadFile`/`NtWriteFile` at block-derived offsets and enforces 512-byte alignment with assertions. The private channel maintains a one-block cache used for reads and updated by writes.

Caveats: `ext2fs_check_if_mounted()` appears to use `*mount_flags &= ...` after initializing to zero, which means it never sets `EXT2_MF_MOUNTED`; this may be intentional dead/legacy code or a latent bug. The implementation is highly Windows/NT-specific and relies on SEH constructs.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/nt_io.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/openfs.c -->
# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/openfs.c

Central filesystem-open path for libext2fs. `ext2fs_open()` delegates to `ext2fs_open2()`, which allocates the filesystem handle, opens the I/O channel, reads the superblock, validates features and geometry, reads group descriptors, starts MMP, and prepares optional support state.

Validation covers superblock magic, revision, checksum type and checksum retry, incompatible and readonly-compatible feature support, journal-device permission, block/cluster log constraints, bigalloc requirements, inode size, 64-bit descriptor size, group count, descriptor count, and inode count consistency.

Descriptor reading handles normal and `meta_bg` layouts, backup superblock recovery adjustments, big-endian descriptor swapping, image-file headers, and journal devices with no group descriptors.

Additional behavior: honors fake-time environment variables, parses `?` suffix I/O options from device names, initializes checksum seed, starts MMP for write/exclusive opens unless skipped, creates shared-block SHA map when requested, and loads UTF-8 NLS tables for casefold filesystems.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/openfs.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/orphan.c -->
# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/orphan.c

Implements ext4 orphan file creation, truncation, sizing, and checksum helpers. The orphan file is a bounded regular file containing orphan inode slots and per-block tails.

`ext2fs_create_orphan_file()` allocates or reuses the configured orphan inode, optionally truncates an existing non-empty orphan file, allocates up to `EXT4_MAX_ORPHAN_FILE_BLOCKS`, writes initialized blocks, sets timestamps/mode/link count/size, and sets the orphan_file feature.

Checksum helpers compute CRC32C over orphan inode number, generation, block number, and block payload. Metadata checksum mode writes and verifies the orphan block tail checksum.

`ext2fs_truncate_orphan_file()` punches all blocks from the orphan file, clears the inode, clears orphan-related superblock features, marks the superblock dirty, and clears `EXT2_FLAG_SUPER_ONLY` because descriptors/accounting may need updates.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/orphan.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/progress.c -->
# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/progress.c

Implements numeric progress callbacks through `ext2fs_numeric_progress_ops`. It prints `current/max` counters with backspaces so the display updates in place.

Progress output is gated by `EXT2_FLAG_PRINT_PROGRESS`. `E2FSPROGS_SKIP_PROGRESS` suppresses middle counter updates while still allowing start/end messages.

Updates are rate-limited to once per second by a static `last_update`, so multiple simultaneous progress streams would share timing state.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/progress.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/punch.c -->
# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/punch.c

Implements block deallocation for inode logical ranges through `ext2fs_punch()`. It supports inline data, extent-based files, and traditional direct/indirect block maps.

The indirect path recursively walks direct, indirect, double-indirect, and triple-indirect pointers, clears entries in the punched range, frees now-empty indirect blocks, and subtracts freed blocks from `i_blocks`.

The extent path opens the extent tree, edits extents around the punched range, splits extents when the punched range is in the middle, deletes empty extents, fixes parent indexes, and frees physical blocks. Bigalloc filesystems use cluster-aware checks before freeing boundary clusters.

Inline data punching clears inline payload and removes inline-data extended attributes only when the punch starts at logical block zero. The final inode is written after successful deallocation.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/punch.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/qcow2.c -->
# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/qcow2.c

Provides qcow2-to-raw image conversion helpers. `qcow2_read_header()` reads and validates qcow2 magic/version, and `qcow2_write_raw_image()` walks qcow2 metadata to copy allocated clusters to a raw output file.

The converter rejects encrypted images, compressed clusters, invalid cluster bit ranges, unaligned L1 table offsets, and oversized L1 tables. It reads the L1 table, then each referenced L2 table, then copies non-zero cluster entries to the corresponding raw offset.

The raw output is resized by seeking to `image_size - 1` and writing one zero byte. The implementation is intentionally limited: it does not implement qcow2 compression, snapshots, refcount validation, or writes back to qcow2.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/qcow2.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/qcow2.h -->
# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/qcow2.h

Defines qcow2 format constants and structures used by `qcow2.c`: header layout, L2 cache nodes, refcount bookkeeping, and the aggregate `ext2_qcow2_image` state.

Includes magic/version constants, copied/compressed flags, error codes for compressed/encrypted/corrupt images, and prototypes for `qcow2_read_header()` and `qcow2_write_raw_image()`.

Some structures such as L2 cache and refcount state are broader than the current converter’s read-only use, suggesting shared or historical support for qcow2 generation paths.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/qcow2.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/rbtree.c -->
# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/rbtree.c

Linux-derived red-black tree implementation namespaced with `ext2fs_`. It implements rotations, insertion rebalancing, deletion rebalancing, erase, first/last traversal, next/previous traversal, and node replacement.

`ext2fs_rb_insert_color()` assumes callers already linked the new node in binary-search order with `ext2fs_rb_link_node()`. `ext2fs_rb_erase()` handles zero, one, and two-child deletion cases, using successor replacement for two-child nodes.

The implementation packs parent pointer and color in `rb_parent_color`, so node alignment and correct use of helper macros are essential. It provides no ordering callbacks; users must implement their own search/insert comparisons.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/rbtree.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/rbtree.h -->
# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/rbtree.h

Header for the namespaced red-black tree support. It defines `struct rb_node`, `struct rb_root`, color constants, parent/color accessors, empty-node helpers, `RB_ROOT`, `ext2fs_rb_entry`, and function prototypes.

The parent pointer and color bits are packed into `uintptr_t rb_parent_color`; the struct is aligned to `sizeof(long)` to preserve low bits for flags.

The header emphasizes that callers provide search and ordered insertion logic themselves, then call `ext2fs_rb_insert_color()` for balancing.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/rbtree.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/read_bb.c -->
# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/read_bb.c

Reads bad blocks from the filesystem’s bad block inode (`EXT2_BAD_INO`). `ext2fs_read_bb_inode()` creates a badblocks list if needed, sizes it from inode block count with clamps, and iterates the inode’s blocks read-only.

The callback ignores metadata/indirect entries (`blockcnt < 0`) and out-of-filesystem block numbers, adding only valid blocks to the badblocks list.

This function converts on-disk bad block inode mappings into libext2fs badblocks-list form for tools such as fsck and mkfs workflows.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/read_bb.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/read_bb_file.c -->
# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/read_bb_file.c

Parses textual bad block lists from a `FILE *`. `ext2fs_read_bb_FILE2()` reads each line, scans an unsigned block number, rejects values beyond 32 bits with `EOVERFLOW`, validates against filesystem bounds when an fs is provided, and adds valid values to the list.

Invalid in-range parsing lines are skipped; out-of-filesystem block numbers trigger an optional callback with the original bad string.

`ext2fs_read_bb_FILE()` is a compatibility wrapper adapting the older invalid callback signature to the newer `priv_data` form.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/read_bb_file.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/res_gdt.c -->
# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/res_gdt.c

Supports reserved group descriptor table blocks for online resizing. `ext2fs_list_backups()` enumerates backup-super/GDT groups for sparse_super, sparse_super2, and non-sparse filesystems.

`ext2fs_create_resize_inode()` creates or repairs the resize inode’s double-indirect mapping so reserved primary and backup GDT blocks are represented. It allocates the double-indirect block if missing, verifies expected primary/backup GDT block locations, writes dirty indirect blocks, updates inode size/block counts, and writes the resize inode.

The code explicitly does not handle extents for this inode and relies on reserved blocks already being marked in-use during filesystem initialization.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/res_gdt.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/rw_bitmaps.c -->
# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/rw_bitmaps.c

Reads and writes block and inode bitmaps. Public helpers include `ext2fs_read_inode_bitmap`, `ext2fs_read_block_bitmap`, `ext2fs_read_bitmaps`, `ext2fs_write_inode_bitmap`, `ext2fs_write_block_bitmap`, and `ext2fs_write_bitmaps`.

Write paths serialize in-memory bitmaps to per-group bitmap blocks, force padding bits in the final block group, compute bitmap checksums, update group descriptor checksums, skip uninitialized groups when descriptor checksums permit, and clear dirty flags.

Read paths allocate bitmap structures, support e2image bitmap sources, verify bitmap checksums unless ignored, record bitmap tail padding problems, synthesize reserved metadata blocks for uninitialized block groups, and optionally use pthreads to read group ranges in parallel when the I/O channel supports threading.

External journal devices are rejected for bitmap operations. Threaded reads temporarily disable I/O caching and protect shared bitmap updates with a mutex.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/rw_bitmaps.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/sha256.c -->
# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/sha256.c

Self-contained SHA-256 implementation copied from libtomcrypt and relicensed for e2fsprogs. The public function is `ext2fs_sha256()`.

The implementation defines SHA-256 constants, rotate/choice/majority/sigma macros, big-endian load/store helpers, compression, init, process, and final padding/output routines.

A `UNITTEST` block contains known-answer tests for empty string, `"abc"`, and a longer standard vector. The code is simple and dependency-light, suitable for internal hashing needs without linking an external crypto library.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/lib/ext2fs/sha256.c -->