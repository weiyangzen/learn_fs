# Group Research: group_851_linux_sources_os_linux_linux_fs_ufs_namei_c_sources_os_linux_linux_f_342976a0d6ab

Scope verified against `Docs/research_subset_a.md`: all files are under `sources/os/linux/linux`. Every listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ufs/namei.c -->
# File Research: sources/os/linux/linux/fs/ufs/namei.c

## Purpose
Implements UFS directory inode operations for Linux VFS name lookup and namespace mutation: create, lookup, link, unlink, symlink, mkdir, rmdir, mknod, and rename.

## Main Contents
- `ufs_add_nondir()`: common helper that adds a directory entry for non-directories, instantiates the dentry on success, and discards the new inode on failure.
- `ufs_lookup()`: validates `UFS_MAXNAMLEN`, resolves inode numbers through `ufs_inode_by_name()`, and returns aliases via `d_splice_alias()`.
- Creation paths:
  - `ufs_create()` allocates a regular inode and attaches file inode/file/address-space ops.
  - `ufs_mknod()` validates old device encoding, initializes special inode metadata, and stores UFS-specific device data.
  - `ufs_symlink()` chooses slow page-cache symlinks or fast in-inode symlinks based on `s_maxsymlinklen`.
  - `ufs_mkdir()` handles parent/child link counts, initializes an empty directory, and links it into the parent.
- Removal and movement:
  - `ufs_unlink()` finds and deletes the directory entry, then drops the target link count.
  - `ufs_rmdir()` checks emptiness before unlinking and adjusts directory link counts.
  - `ufs_rename()` supports only `RENAME_NOREPLACE`, handles directory `..` updates, replacement targets, and link count adjustments.
- Exports `ufs_dir_inode_operations`.

## Important Design Points
- Closely follows ext2-style VFS namei patterns while relying on UFS directory helpers from `dir.c`.
- Directory rename has separate handling for moving directories across parents because `..` must be updated with `ufs_set_link()`.
- Fast symlinks store bytes in `UFS_I(inode)->i_u1.i_symlink`; slow symlinks use page-cache-backed symlink operations.
- Error paths are mostly link-count centered: newly allocated inodes are discarded, and parent directory link increments are undone.

## Cross-File Relationships
- Uses on-disk constants from `ufs_fs.h`, internal inode/super helpers from `ufs.h`, and device helpers from `util.h`.
- Calls directory helpers declared in `ufs.h`: `ufs_add_link()`, `ufs_find_entry()`, `ufs_delete_entry()`, `ufs_empty_dir()`, `ufs_make_empty()`, `ufs_dotdot()`, and `ufs_set_link()`.
- Uses inode allocation and loading APIs from other UFS files: `ufs_new_inode()` and `ufs_iget()`.
- File, directory, and address-space operation tables are declared in `ufs.h` and installed here for newly created inodes.

## Risks / Review Notes
- `ufs_symlink()` rejects links larger than one filesystem block before deciding fast versus slow symlink.
- Rename semantics are intentionally limited: unsupported flags other than `RENAME_NOREPLACE` return `-EINVAL`.
- Directory replacement paths must preserve link-count invariants; changes in `ufs_rename()` need careful audit against VFS rename locking assumptions.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ufs/namei.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ufs/super.c -->
# File Research: sources/os/linux/linux/fs/ufs/super.c

## Purpose
Implements UFS superblock, mount, remount, export, sync, statfs, inode-cache, and module registration logic for the Linux UFS filesystem driver.

## Main Contents
- NFS export support:
  - `ufs_nfs_get_inode()`, `ufs_fh_to_dentry()`, `ufs_fh_to_parent()`, `ufs_get_parent()`.
  - `ufs_export_ops` uses generic inode file handles with UFS inode lookup.
- Debug-only dump helpers for superblock and cylinder group state under `CONFIG_UFS_DEBUG`.
- Error reporting:
  - `ufs_error()` marks writable filesystems bad, schedules superblock dirtiness, and applies the configured `onerror` policy.
  - `ufs_panic()` marks bad and read-only while logging a panic-style message.
  - `ufs_warning()` logs nonfatal warnings.
- Mount option parsing:
  - `ufstype=` supports `old`, `sun`, `sunos`, `sunx86`, `44bsd`, `ufs2`/`5xbsd`, `hp`, `nextstep`, `nextstep-cd`, and `openstep`.
  - `onerror=` supports `panic`, `lock`, `umount`, and `repair`.
- Superblock loading:
  - `ufs_fill_super()` allocates `ufs_sb_info` and `ufs_sb_private_info`, selects geometry defaults by flavor, reads the on-disk superblock, probes byte order through magic values, validates fragment/block sizes, checks clean state, initializes derived geometry, loads root inode, and reads cylinder group structures for writable mounts.
- Cylinder summary handling:
  - `ufs_setup_cstotal()` normalizes variant-specific on-disk summary placement into in-memory `cs_total`.
  - `ufs_put_cstotal()` writes summary totals back to the correct UFS1/UFS2/44BSD locations.
  - `ufs_read_cylinder_structures()` reads cylinder summaries and cylinder group buffers, then prepares the small cylinder-group private-info cache.
  - `ufs_put_super_internal()` writes summaries and releases cylinder group resources.
- Sync and dirty scheduling:
  - `ufs_sync_fs()` updates timestamps/state and summary totals.
  - `ufs_mark_sb_dirty()` queues delayed sync work.
  - `delayed_sync_fs()` drains the delayed work item.
- Remount and visibility:
  - `ufs_reconfigure()` handles read-only/read-write transitions and updates `onerror`.
  - `ufs_show_options()` reports current `ufstype` and `onerror`.
  - `ufs_statfs()` reports block, inode, free-space, name-length, and fsid data.
- Inode cache and filesystem registration:
  - `ufs_alloc_inode()`, `ufs_free_in_core_inode()`, `init_inodecache()`, `destroy_inodecache()`.
  - `ufs_super_ops`, `ufs_context_ops`, `ufs_fs_type`, `init_ufs_fs()`, `exit_ufs_fs()`.

## Important Design Points
- The driver requires an explicit `ufstype` for safe operation, but defaults to `old` with a warning if omitted.
- Byte order is detected by trying little-endian first, then big-endian, using the superblock magic.
- Several flavors are forced read-only even if mounted read-write: old, NeXTstep, NeXTstep CD, OpenStep, and HP.
- Writable remounts are allowed only when write support is compiled and the flavor is one of Sun, SunOS, 44BSD, Sun x86, or UFS2.
- Clean-state checks can force a filesystem read-only if it is active, bad, unknown, or needs fsck.
- UFS2 expands timestamps and block pointers, so mount setup changes time granularity/ranges and `s_apbshift`.
- `ufs_max_bytes()` derives maximum file size from direct/single/double/triple indirect addressing and clamps to `MAX_LFS_FILESIZE`.

## Cross-File Relationships
- Uses on-disk structures and flags from `ufs_fs.h`.
- Uses endian helpers from `swab.h`.
- Uses buffer, bitmap, state, and superblock-offset helpers from `util.h`.
- Installs inode operations implemented in UFS inode/file/namei code via declarations in `ufs.h`.
- Calls cylinder APIs `ufs_put_cylinder()` and UFS inode APIs `ufs_iget()`, `ufs_write_inode()`, `ufs_evict_inode()`.

## Risks / Review Notes
- Wrong `ufstype` is explicitly warned as filesystem-corrupting; variant flags control directory encoding, UID encoding, state fields, cylinder-group format, and pointer width.
- `ufs_read_cylinder_structures()` returns boolean success rather than errno, so mount failures collapse to generic paths.
- Delayed sync scheduling depends on `dirty_writeback_interval`; superblock dirtiness is not written immediately in all paths.
- On write-capable mounts, summary and cylinder group writeback paths must preserve endian conversion and variant-specific placement.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ufs/super.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ufs/swab.h -->
# File Research: sources/os/linux/linux/fs/ufs/swab.h

## Purpose
Provides filesystem-endian conversion helpers for UFS on-disk 16-, 32-, and 64-bit fields.

## Main Contents
- Defines `BYTESEX_LE` and `BYTESEX_BE`.
- Conversion helpers:
  - `fs64_to_cpu()`, `cpu_to_fs64()`
  - `fs32_to_cpu()`, `cpu_to_fs32()`
  - `fs16_to_cpu()`, `cpu_to_fs16()`
- In-place arithmetic helpers:
  - `fs32_add()`, `fs32_sub()`
  - `fs16_add()`, `fs16_sub()`

## Important Design Points
- All conversions are controlled by `UFS_SB(sbp)->s_bytesex`, which is set during superblock magic probing.
- The file assumes UFS instances are either little-endian or big-endian; exotic mixed-endian formats are explicitly outside its design.
- Uses Linux endian helpers with `__force` casts for bitwise on-disk typedefs.

## Cross-File Relationships
- Included by `super.c`, `util.c`, and `util.h`.
- Requires `UFS_SB()` from `ufs.h`.
- Applies to on-disk typedefs declared in `ufs_fs.h`: `__fs16`, `__fs32`, and `__fs64`.

## Risks / Review Notes
- Any missed conversion at a caller can corrupt metadata on opposite-endian UFS images.
- In-place add/sub helpers cast typed pointers to endian-specific pointer types; callers must pass actual on-disk fields, not CPU-native temporary storage.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ufs/swab.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ufs/ufs.h -->
# File Research: sources/os/linux/linux/fs/ufs/ufs.h

## Purpose
Central internal UFS header for Linux. It defines in-memory superblock and inode-private structures, mount option flags, debug macros, cross-file prototypes, and common conversion helpers.

## Main Contents
- `struct ufs_sb_info`: per-mounted-filesystem state, including private superblock info, cylinder summaries, cylinder-group buffers/cache slots, byte order, flavor flags, error policy, delayed sync work, and mount lock.
- `struct ufs_inode_info`: UFS inode extension with UFS1/UFS2 block-pointer storage, fast symlink storage, flags, shadow fields, last fragment, metadata seqlock, truncate mutex, directory lookup hint, and embedded VFS inode.
- Mount flags:
  - Error policy: panic, lock, umount, repair.
  - UFS flavor: old, 44BSD, Sun, NeXTstep, NeXTstep CD, OpenStep, Sun x86, HP, UFS2, SunOS.
- `UFSD()` debug macro under `CONFIG_UFS_DEBUG`.
- Prototypes for UFS allocation, cylinder, directory, file, inode, and superblock code.
- Accessors:
  - `UFS_SB()` maps `super_block` to `ufs_sb_info`.
  - `UFS_I()` maps VFS inode to `ufs_inode_info`.
  - `ufs_dtog()` and `ufs_dtogd()` compute cylinder group number and offset for a filesystem block.

## Important Design Points
- This header is the internal dependency hub for the UFS driver.
- `ufs_inode_info.i_u1` supports both 32-bit UFS1 block pointers and 64-bit UFS2 pointers, plus fast symlink storage sized for the larger case.
- Delayed superblock sync state is embedded in `ufs_sb_info` and protected by `work_lock`.
- `s_lock` is the coarse superblock lock used around mount/remount/statfs/sync-sensitive state.

## Cross-File Relationships
- Included by most UFS implementation files.
- Depends on layout definitions from `ufs_fs.h`.
- Prototypes functions implemented in `balloc.c`, `cylinder.c`, `dir.c`, `file.c`, `ialloc.c`, `inode.c`, `namei.c`, and `super.c`.

## Risks / Review Notes
- Changes to `struct ufs_inode_info` affect slab cache construction in `super.c`, including usercopy whitelisting for fast symlink storage.
- Mount flavor flag values are also used as parser enum results in `super.c`; changing them affects option handling.
- `ufs_dtog()` and `ufs_dtogd()` mutate their local copy through `do_div`; callers are safe only because arguments are passed by value.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ufs/ufs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ufs/ufs_fs.h -->
# File Research: sources/os/linux/linux/fs/ufs/ufs_fs.h

## Purpose
Defines the UFS on-disk format, layout constants, compatibility flags, cylinder group structures, inode structures, and private derived geometry structures used by the Linux UFS driver.

## Main Contents
- On-disk endian typedefs: `__fs16`, `__fs32`, `__fs64`.
- Core constants:
  - Boot/superblock offsets and sizes.
  - UFS1/UFS2 and HP magic values.
  - block/fragment sizing, direct/indirect block counts, root inode, clean-state values, and maximum directory name/link limits.
- Variant flag masks:
  - Directory entry format: old versus 44BSD.
  - UID/GID format: old, 44BSD, EFT.
  - State encoding: old, 44BSD, Sun, SunOS, Sun x86.
  - Cylinder group encoding: old, Sun, 44BSD.
  - Filesystem type: UFS1 versus UFS2.
- Geometry macros:
  - filesystem-block to disk-block conversion.
  - cylinder group base/super/cg/inode/data locations.
  - inode number to cylinder group/block/offset.
  - fragment/block rounding and mask helpers.
- Directory and summary structures:
  - `struct ufs_dir_entry`
  - `struct ufs_csum`
  - `struct ufs2_csum_total`
  - `struct ufs_csum_core`
- Superblock layouts:
  - Historical full `struct ufs_super_block` is retained in `#if 0` as documentation.
  - Active split layouts: `ufs_super_block_first`, `ufs_super_block_second`, `ufs_super_block_third`.
- Cylinder group layouts:
  - `struct ufs_cylinder_group`
  - `struct ufs_old_cylinder_group`
  - magic and old-format access macros.
- Inode layouts:
  - `struct ufs_inode` for UFS1 variants.
  - `struct ufs2_inode` for UFS2 with 64-bit size/timestamps/block pointers.
  - BSD inode flag constants.
- In-memory support structures:
  - `struct ufs_buffer_head`
  - `struct ufs_cg_private_info`
  - `struct ufs_sb_private_info`

## Important Design Points
- This file is a compatibility boundary. It models multiple historical UFS dialects in one driver.
- The active superblock representation is split into 512-byte pieces because a full superblock may span several fragments/buffers.
- Many macros assume a local variable named `uspi`, and some also assume `sb`; callers must follow the established local naming convention.
- UFS2 uses 64-bit block pointers and summary values, while UFS1 variants mostly use 32-bit fields.
- `ufs_sb_private_info` stores normalized, CPU-native derived values so runtime code does not repeatedly decode every on-disk superblock field.

## Cross-File Relationships
- Included by all UFS C files and internal headers.
- `super.c` fills `ufs_sb_private_info` from the split superblock structures and uses variant flags defined here.
- `util.h` uses directory, inode, bitmap, and superblock field definitions to implement endian-aware accessors.
- `namei.c` uses `UFS_MAXNAMLEN`, symlink sizing, and inode constants.
- Allocation, inode, directory, and cylinder code rely on cylinder group and bitmap layout definitions.

## Risks / Review Notes
- On-disk structure edits can break compatibility with existing UFS images.
- Several comments document historical oddities, such as HP flag overlap and variant-specific field reuse.
- The `ufs_cbtorpos()` macro is complex and variant-sensitive; allocation code depending on rotational layout should be treated carefully.
- Bitwise typedefs help catch endian mistakes, but many accesses still depend on correct helper usage.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ufs/ufs_fs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ufs/util.c -->
# File Research: sources/os/linux/linux/fs/ufs/util.c

## Purpose
Implements UFS utility routines for reading multi-fragment metadata buffers, releasing/dirtying/syncing those buffers, encoding special-device inode data, and locking page-cache folios.

## Main Contents
- Metadata buffer helpers:
  - `_ubh_bread_()` allocates a `ufs_buffer_head` and reads up to `UFS_MAXFRAG` fragments.
  - `ubh_bread_uspi()` reuses the `ufs_sb_private_info` embedded superblock buffer.
  - `ubh_brelse()` and `ubh_brelse_uspi()` release buffer references.
  - `ubh_mark_buffer_dirty()`, `ubh_sync_block()`, `ubh_bforget()`, and `ubh_buffer_dirty()`.
- Device encoding helpers:
  - `ufs_get_inode_dev()` decodes special inode device numbers with Sun/Sun x86 special handling.
  - `ufs_set_inode_dev()` stores device numbers using SysV or old device encoding depending on UFS state flavor.
- Page-cache helper:
  - `ufs_get_locked_folio()` locks an existing folio or reads one, handles truncate races, and ensures buffers exist.

## Important Design Points
- UFS metadata can span several fragment-sized buffer_heads; `ufs_buffer_head` abstracts that group.
- Size validation requires fragment alignment and caps count at `UFS_MAXFRAG`.
- Sun and Sun x86 device fields differ: Sun x86 uses `i_data[1]`, most others use `i_data[0]`.
- `ufs_get_locked_folio()` creates empty buffers sized by `inode->i_blkbits` if the folio lacks buffers.

## Cross-File Relationships
- Declared by `util.h`.
- Uses `ufs_sb_private_info`, `ufs_buffer_head`, and UFS variant flags from `ufs_fs.h`/`ufs.h`.
- Device helpers are used by inode read/write and `namei.c` mknod paths.
- Folio helper supports block mapping/truncation paths elsewhere in UFS.

## Risks / Review Notes
- `_ubh_bread_()` allows `count == 0` if size is zero; `ubh_bread_uspi()` rejects it. Callers should not pass zero-size metadata reads.
- `ubh_bread_uspi()` failure releases buffers read so far but does not clear all slots after failure.
- `ufs_get_locked_folio()` returns `NULL` for truncate races and `ERR_PTR()` for read failures; callers must distinguish both.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ufs/util.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ufs/util.h -->
# File Research: sources/os/linux/linux/fs/ufs/util.h

## Purpose
Provides inline helpers and macros for endian-aware UFS field access, superblock/cylinder buffer addressing, directory entry manipulation, UID/GID conversion, bitmap operations, fragment accounting, UFS1/UFS2 block pointer handling, and timestamp generation.

## Main Contents
- Buffer-head accessors:
  - `UCPI_UBH()`, `USPI_UBH()`, `get_usb_offset()`
  - `ubh_get_usb_first()`, `ubh_get_usb_second()`, `ubh_get_usb_third()`
  - `ubh_get_ucg()`
- Variant-specific superblock access:
  - `ufs_get_fs_state()`, `ufs_set_fs_state()`
  - `ufs_get_fs_npsect()`
  - `ufs_get_fs_qbmask()`, `ufs_get_fs_qfmask()`
- Directory entry helpers:
  - `ufs_get_de_namlen()`, `ufs_set_de_namlen()`
  - `ufs_set_de_type()`
- UID/GID helpers:
  - `ufs_get_inode_uid()`, `ufs_set_inode_uid()`
  - `ufs_get_inode_gid()`, `ufs_set_inode_gid()`
- Function declarations for buffer utilities, device helpers, `ufs_prepare_chunk()`, and folio helpers.
- Byte/word access macros across multi-fragment metadata buffers:
  - `ubh_get_addr8/16/32/64()`
  - `ubh_get_data_ptr()`
  - `ubh_blkmap()`
- Free-space helpers:
  - `ufs_freefrags()`
  - cylinder-group array access macros.
  - bitmap set/clear/test/find helpers.
  - block-level bitmap helpers: `ubh_isblockset()`, `ubh_clrblock()`, `ubh_setblock()`.
  - `ufs_fragacct()` updates fragment summary accounting.
- UFS1/UFS2 data pointer helpers:
  - `ufs_get_direct_data_ptr()`
  - `ufs_data_ptr_to_cpu()`
  - `ufs_cpu_to_data_ptr()`
  - `ufs_data_ptr_clear()`
  - `ufs_is_data_ptr_zero()`
- `ufs_get_seconds()` returns filesystem-endian low 32 bits of current real time.

## Important Design Points
- Many macros rely on a caller-local `uspi` variable; this is a strong convention in UFS code.
- Directory entry length/type and UID/GID layouts are variant-specific and selected through `UFS_SB(sb)->s_flags`.
- UFS1 and UFS2 block pointers differ in width; pointer helper functions centralize that distinction.
- Bitmap search helpers work across fragmented `buffer_head` arrays rather than contiguous memory.
- `ufs_get_seconds()` intentionally wraps to 32 bits for superblock/cylinder-group timestamps so dirty-state detection remains compatible with UFS1-style fields.

## Cross-File Relationships
- Included by UFS implementation files for common low-level access.
- Depends on endian helpers from `swab.h` and structure definitions from `ufs_fs.h`.
- Used by `super.c` for superblock state, mask, summary, and time updates.
- Used by allocation/cylinder/inode/directory code for bitmap and pointer manipulation.

## Risks / Review Notes
- Comments on 44BSD directory name length say `XXX this seems wrong`; this is a known caution around raw byte versus endian-converted fields.
- Some address macros appear fragile and depend on correct shifts, fragment size fields, and local variable names.
- `find_last_zero_bit()` manually scans bytes and must be kept consistent with bitmap end/start semantics.
- `ufs_fragacct()` assumes fragment list indexing matches UFS fragment counts; accounting bugs here affect free-space summaries.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ufs/util.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/unicode/Kconfig -->
# File Research: sources/os/linux/linux/fs/unicode/Kconfig

## Purpose
Defines kernel configuration options for filesystem UTF-8 normalization/casefolding support and its KUnit tests.

## Main Contents
- `UNICODE`: tristate option for UTF-8 NFD normalization and NFD+casefold support.
- Help text explains that when built as a module, the large casefolding table is requested only when a filesystem needs it.
- `UNICODE_NORMALIZATION_KUNIT_TEST`: tristate KUnit test option depending on `UNICODE && KUNIT`, defaulting to `KUNIT_ALL_TESTS`.

## Important Design Points
- Unicode support can be built-in, modular, or disabled.
- Tests are independently selectable but require both Unicode support and KUnit.

## Cross-File Relationships
- `Makefile` builds `unicode.o`, `utf8data.o`, and KUnit test objects based on these symbols.
- Filesystems using `linux/unicode.h` depend on `CONFIG_UNICODE`.

## Risks / Review Notes
- If `UNICODE=m`, runtime users depend on symbol/module availability for `utf8_data_table`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/unicode/Kconfig -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/unicode/Makefile -->
# File Research: sources/os/linux/linux/fs/unicode/Makefile

## Purpose
Builds the kernel Unicode normalization objects and optionally regenerates the generated UTF-8 data table from Unicode Character Database text files.

## Main Contents
- Builds `unicode.o` from `utf8-norm.o` and `utf8-core.o` when `CONFIG_UNICODE` is set.
- Builds `utf8data.o` when `CONFIG_UNICODE` is enabled.
- Builds `tests/utf8_kunit.o` when `CONFIG_UNICODE_NORMALIZATION_KUNIT_TEST` is enabled.
- Declares `mkutf8data` as a host program.
- Default path copies `utf8data.c_shipped` into generated `utf8data.c`.
- `REGENERATE_UTF8DATA=1` path runs `mkutf8data` with UCD inputs:
  - `DerivedAge.txt`
  - `DerivedCombiningClass.txt`
  - `DerivedCoreProperties.txt`
  - `UnicodeData.txt`
  - `CaseFolding.txt`
  - `NormalizationCorrections.txt`
  - `NormalizationTest.txt`

## Important Design Points
- Normal kernel builds use checked-in generated data instead of requiring UCD files.
- Regeneration is explicit and depends on placing UCD text files in the source directory.
- `targets += utf8data.c` marks the generated data file as a kbuild target.

## Cross-File Relationships
- Host generator is implemented by `mkutf8data.c`.
- Generated `utf8data.c` includes `utf8n.h` and exports `utf8_data_table`.
- Runtime code in `utf8-core.c` loads the generated table via symbol lookup.

## Risks / Review Notes
- Regeneration depends on exact UCD file names and parser expectations in `mkutf8data.c`.
- Generated output must stay compatible with trie reader logic in `utf8-norm.c`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/unicode/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/unicode/mkutf8data.c -->
# File Research: sources/os/linux/linux/fs/unicode/mkutf8data.c

## Purpose
Host-side generator that reads Unicode Character Database files and emits `utf8data.c`, a compact trie table used by the kernel UTF-8 normalization and casefolding runtime.

## Main Contents
- Command-line configurable inputs and output:
  - Age, combining class, core properties, UnicodeData, case folding, normalization corrections, normalization tests, and output C file.
- Unicode version handling:
  - Packs major/minor/revision into integer ages.
  - Builds `ages[]` and generation indexes used by trie leaves.
- UTF-8 helpers:
  - `utf8encode()`, `utf8decode()`, `utf32valid()`.
  - Valid Unicode range is limited to `0x0..0x10ffff`, with surrogates removed later.
- Compact trie builder:
  - `struct tree` and `struct node`.
  - `insert()` builds bitwise UTF-8 tries and collapses fully populated identical leaves.
  - `prune()` removes redundant singleton paths.
  - `mark_nodes()`, `index_nodes()`, `size_nodes()`, and `emit()` compute and serialize compact trie nodes/leaves.
- Unicode data model:
  - `struct unicode_data` stores code point, combining class, generation, correction age, UTF-32 and UTF-8 decompositions.
  - Global `unicode_data[0x110000]` covers all Unicode scalar slots.
  - `corrections` stores normalization corrections by version.
- Parsers:
  - `age_init()` reads `DerivedAge.txt` and marks defined code point generations.
  - `ccc_init()` reads canonical combining classes.
  - `nfdi_init()` reads canonical decompositions from `UnicodeData.txt`, ignoring compatibility decompositions.
  - `nfdicf_init()` reads common/full case folding from `CaseFolding.txt`.
  - `ignore_init()` maps `Default_Ignorable_Code_Point` entries to empty decompositions.
  - `corrections_init()` reads normalization corrections.
- Decomposition expansion:
  - `hangul_decompose()` prepares Hangul decompositions but marks them with a cookie so runtime handles them algorithmically.
  - `nfdi_decompose()` recursively expands canonical decompositions and seeds NFDICF when no casefold exists.
  - `nfdicf_decompose()` recursively expands casefolding decompositions.
  - `utf8_init()` converts UTF-32 decomposition arrays to UTF-8 strings.
- Generator self-check runtime:
  - Contains local trie lookup, age, length, cursor, and `utf8byte()` implementations mirroring kernel runtime behavior.
  - `trees_verify()` checks trie contents against source data.
  - `normalization_test()` validates generated NFDI behavior against `NormalizationTest.txt`.
- `write_file()` emits:
  - `utf8agetab`
  - `utf8nfdicfdata`
  - `utf8nfdidata`
  - packed `utf8data[]`
  - exported `utf8_data_table`
- `main()` orchestrates parse, decompose, build, verify, test, and output.

## Important Design Points
- Two normalization forms are generated:
  - `nfdi`: NFD plus removal of default ignorables.
  - `nfdicf`: NFD plus removal of default ignorables plus full casefolding.
- Leaves encode generation, canonical combining class, and optional decomposition string.
- Combining class reordering is not pre-expanded into every string; runtime cursors sort by CCC while scanning.
- Hangul syllable decompositions are represented with a marker and synthesized algorithmically at runtime to save table space.
- Trees are generated for correction/version boundaries so older Unicode versions can be supported from one data blob.
- The emitted trie format must match the constants and traversal code duplicated in `utf8-norm.c`.

## Cross-File Relationships
- Built as a host tool by `fs/unicode/Makefile`.
- Emits C code included in kernel builds as `utf8data.c`.
- Generated output defines `utf8_data_table`, consumed by `utf8-core.c` and interpreted by `utf8-norm.c`.
- Shares structure and trie format assumptions with `utf8n.h`.

## Risks / Review Notes
- Parsers use fixed-size line buffers and fixed-size decomposition arrays based on Unicode assumptions; new UCD formats or longer mappings can break generation.
- Memory allocation failures are generally not checked; this is a host build tool but still a robustness limitation.
- Runtime trie lookup code is duplicated between generator and kernel runtime; format changes must update both.
- Normalization correctness depends on UCD file consistency and successful `normalization_test()`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/unicode/mkutf8data.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/unicode/tests/utf8_kunit.c -->
# File Research: sources/os/linux/linux/fs/unicode/tests/utf8_kunit.c

## Purpose
KUnit tests for Linux filesystem UTF-8 normalization, casefolding, comparisons, and supported Unicode versions.

## Main Contents
- Test vectors:
  - `nfdi_test_data[]` covers identity normalization, canonical decomposition, non-canonical compatibility exclusions, Greek mapping, and canonical combining class ordering.
  - `nfdicf_test_data[]` covers ASCII folding, sharp-s expansion, decomposed casefolding, Cherokee, Old Hungarian, Osage, Latin small-capital, and Georgian cases.
- Local wrappers:
  - `utf8len()` calls `utf8nlen()` with NUL-terminated length.
  - `utf8cursor()` calls `utf8ncursor()` with NUL-terminated length.
- Test cases:
  - `check_utf8_nfdi()`: verifies normalized length and byte stream for NFDI.
  - `check_utf8_nfdicf()`: verifies normalized length and byte stream for NFDICF.
  - `check_utf8_comparisons()`: verifies `utf8_strncmp()` and `utf8_strncasecmp()` equivalence behavior.
  - `check_supported_versions()`: verifies expected supported and unsupported Unicode versions.
- KUnit suite setup:
  - `init_test_ucd()` loads `UTF8_LATEST`.
  - `exit_test_ucd()` unloads it.
  - `unicode_normalization_test_suite` registers four tests.

## Important Design Points
- Tests exercise both length calculation and cursor byte emission.
- Comparison tests validate higher-level exported API behavior, not only internal normalization.
- Tests require the generated table to be loadable via `utf8_load()`.

## Cross-File Relationships
- Includes `../utf8n.h` for internal cursor APIs.
- Calls exported APIs from `utf8-core.c` and internal/test-exported APIs from `utf8-norm.c`.
- Built only when `CONFIG_UNICODE_NORMALIZATION_KUNIT_TEST` is enabled.

## Risks / Review Notes
- Some `qstr.len` values use `sizeof()` on fixed-size arrays, so they include trailing zero padding; this intentionally exercises length-bounded handling but differs from ordinary filename lengths.
- `init_test_ucd()` records an expectation if `utf8_load()` fails but still returns 0; subsequent tests depend on `test->priv` being valid.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/unicode/tests/utf8_kunit.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/unicode/utf8-core.c -->
# File Research: sources/os/linux/linux/fs/unicode/utf8-core.c

## Purpose
Provides exported kernel Unicode APIs for UTF-8 validation, normalized comparison, casefolding, hashing, normalization, table loading/unloading, and version parsing.

## Main Contents
- Validation and comparisons:
  - `utf8_validate()` checks whether a `qstr` is valid under NFDI traversal.
  - `utf8_strncmp()` compares two strings after NFDI normalization.
  - `utf8_strncasecmp()` compares two strings after NFDICF normalization.
  - `utf8_strncasecmp_folded()` compares a pre-folded string against the NFDICF form of another string.
- Transformation helpers:
  - `utf8_casefold()` writes NFDICF output into a destination buffer.
  - `utf8_normalize()` writes NFDI output into a destination buffer.
  - `utf8_casefold_hash()` hashes the NFDICF byte stream using Linux name-hash helpers.
- Table/version handling:
  - `find_table_version()` selects the table entry matching a requested Unicode version.
  - `utf8_load()` allocates `struct unicode_map`, requests `utf8_data_table`, checks version support, and sets NFDI/NFDICF table pointers.
  - `utf8_unload()` releases the data-table symbol and map.
  - `utf8_parse_version()` parses `MAJ.MIN.REV` into `UNICODE_AGE()` format.
- Exports all public functions with `EXPORT_SYMBOL`.

## Important Design Points
- API comparison returns `0` for equal, `1` for unequal, and `-EINVAL` for invalid UTF-8 or cursor errors.
- Transform functions require enough destination space for the terminating NUL; otherwise they return `-EINVAL`.
- `utf8_casefold_hash()` hashes normalized bytes without materializing a separate folded string.
- `utf8_load()` uses `symbol_request(utf8_data_table)` so the large table can be modular.

## Cross-File Relationships
- Includes `utf8n.h`.
- Calls cursor and normalization length functions implemented in `utf8-norm.c`.
- Consumes generated `utf8_data_table` from `utf8data.c`.
- Uses public `struct unicode_map` and normalization enum from `linux/unicode.h`.

## Risks / Review Notes
- `utf8_strncasecmp_folded()` assumes `cf` is already valid UTF-8 casefolded data and indexes it until the normalized cursor ends; caller must ensure `cf` is NUL-terminated/long enough.
- `find_table_version()` starts at the last entry and decrements while `version < maxage`; malformed empty tables would underflow, though generated tables are expected valid.
- `utf8_parse_version()` returns `int` even though `UNICODE_AGE()` is unsigned-style packed; invalid negative parser inputs are rejected by `match_int()` failure or packing behavior checks elsewhere.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/unicode/utf8-core.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/unicode/utf8-norm.c -->
# File Research: sources/os/linux/linux/fs/unicode/utf8-norm.c

## Purpose
Implements the runtime UTF-8 trie interpreter and normalization cursor used by Linux filesystem Unicode validation, NFDI normalization, and NFDICF casefolding.

## Main Contents
- `utf8version_is_supported()`: checks whether a requested packed Unicode version appears in the generated age table.
- UTF-8 helpers:
  - `utf8clen()` returns sequence byte length from a valid leading byte.
  - `utf8decode3()` and `utf8encode3()` support Hangul decomposition.
- Trie format definitions:
  - Internal node bit flags: `BITNUM`, `NEXTBYTE`, `OFFLEN`, `RIGHTPATH`, `TRIENODE`, `RIGHTNODE`, `LEFTNODE`.
  - Leaf accessors: generation, canonical combining class, decomposition string.
- Hangul support:
  - Constants for Unicode Hangul decomposition.
  - `utf8hangul()` synthesizes a decomposition leaf for Hangul syllables.
- Trie lookup:
  - `utf8nlookup()` traverses the generated compact trie with a byte limit and returns a leaf only for valid UTF-8 Unicode sequences.
  - `utf8lookup()` is the unbounded wrapper.
- Length and cursor APIs:
  - `utf8nlen()` returns normalized byte length or `-1` for invalid UTF-8.
  - `utf8ncursor()` initializes a bounded normalization cursor.
  - `utf8byte()` emits one byte at a time from the normalized stream, handling decomposition, default-ignorable empty mappings, version gating, and canonical combining class order.
- KUnit module exports are enabled when normalization tests are modular.

## Important Design Points
- Trie lookup doubles as validation: failure to find a leaf means invalid/non-Unicode UTF-8 input.
- Code points newer than the selected Unicode version are treated as undecomposed stoppers.
- Decomposition strings are emitted through cursor state without decrementing the original input length.
- Canonical combining class ordering is implemented by repeated scans between stoppers, emitting classes in ascending order.
- Empty decompositions are used for default-ignorable code points and can reduce normalized length to zero.
- Hangul decompositions are generated at runtime from a compact marker rather than stored fully in the table.

## Cross-File Relationships
- Includes `utf8n.h` for cursor/table declarations.
- Consumes generated trie data from `utf8_data_table`.
- Called by public APIs in `utf8-core.c`.
- Shares trie layout constants and assumptions with `mkutf8data.c`.

## Risks / Review Notes
- `utf8byte()` is stateful and subtle; cursor fields `s`, `p`, `ss`, `sp`, `ccc`, and `nccc` must remain consistent.
- The lookup code assumes generated trie offsets and markers are valid; corrupt generated data would cause bad traversal.
- Bounded cursors reject strings starting with continuation bytes but rely on trie lookup for deeper UTF-8 validation.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/unicode/utf8-norm.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/unicode/utf8n.h -->
# File Research: sources/os/linux/linux/fs/unicode/utf8n.h

## Purpose
Internal header for Linux filesystem UTF-8 normalization, exposing cursor APIs and generated table structures shared by runtime code, tests, and generated data.

## Main Contents
- Includes Linux types, export, string, module, and public Unicode headers.
- Declares `utf8version_is_supported()`.
- Declares `utf8nlen()` for normalized length calculation.
- Defines `UTF8HANGULLEAF`.
- Defines `struct utf8cursor`, storing:
  - map and normalization form.
  - source/decomposition scan pointers.
  - bounded lengths.
  - current and next canonical combining classes.
  - synthesized Hangul leaf buffer.
- Declares `utf8ncursor()` and `utf8byte()`.
- Defines generated table metadata:
  - `struct utf8data`
  - `struct utf8data_table`
- Declares exported `utf8_data_table`.

## Important Design Points
- This is an internal ABI between generated `utf8data.c`, normalization runtime, and tests.
- `struct utf8cursor` exposes normalization state directly to runtime code; callers initialize it with `utf8ncursor()` and consume with `utf8byte()`.
- `utf8data_table` separates age/version tables, NFDICF table metadata, NFDI table metadata, and packed trie bytes.

## Cross-File Relationships
- Included by `utf8-core.c`, `utf8-norm.c`, `mkutf8data.c` generated output, and `tests/utf8_kunit.c`.
- Depends on public `struct unicode_map` and `enum utf8_normalization` from `linux/unicode.h`.

## Risks / Review Notes
- Layout changes to `struct utf8data_table` require coordinated updates to generator output and runtime consumers.
- `UTF8HANGULLEAF` must remain large enough for the synthesized Hangul leaf used by both generator-side and runtime normalization logic.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/unicode/utf8n.h -->