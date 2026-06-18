# Group Research: group_1093_linux_stable_sources_os_linux_linux_stable_fs_ufs_namei_c_sources_o_a8f2c8ec8fbb

Scope: `Docs/research_subset_a.md`; all listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ufs/namei.c -->
# File Research: sources/os/linux/linux-stable/fs/ufs/namei.c

## Summary
Implements UFS directory inode operations for VFS name lookup and namespace mutation: create, lookup, link, unlink, symlink, mkdir, rmdir, mknod, and rename.

## Key APIs
- `ufs_lookup()`
- `ufs_create()`
- `ufs_mknod()`
- `ufs_symlink()`
- `ufs_link()`
- `ufs_mkdir()`
- `ufs_unlink()`
- `ufs_rmdir()`
- `ufs_rename()`
- `ufs_dir_inode_operations`

## Important Behavior
Creation allocates a UFS inode with `ufs_new_inode()`, assigns file or special inode operations, marks it dirty, and inserts a directory entry through `ufs_add_link()`. `ufs_add_nondir()` centralizes successful dentry instantiation and failure cleanup for non-directories.

Lookup rejects names longer than `UFS_MAXNAMLEN`, resolves directory entries with `ufs_inode_by_name()`, and uses `d_splice_alias()` for VFS alias handling.

Symlink creation supports fast symlinks stored in `ufs_inode_info.i_u1.i_symlink` when the link fits `s_maxsymlinklen`; longer symlinks use page-cache symlink storage and `ufs_aops`.

Directory creation increments the parent link count before allocation, initializes `.` and `..` with `ufs_make_empty()`, then inserts the new entry. Failure paths carefully undo both new-directory and parent link counts.

Unlink and rmdir locate entries with `ufs_find_entry()`, remove them using `ufs_delete_entry()`, update ctime/link counts, and release mapped folios. `ufs_rmdir()` only proceeds when `ufs_empty_dir()` succeeds.

Rename handles only default rename and `RENAME_NOREPLACE`; other flags return `-EINVAL`. Directory renames update the child `..` entry through `ufs_dotdot()`/`ufs_set_link()`, adjust parent link counts, and replace or add the target entry before deleting the old entry.

## Dependencies
Relies on UFS directory helpers from `dir.c`, allocation from `ialloc.c`, inode loading/writing from `inode.c`, page-cache folio mapping, VFS dentry/inode helpers, and metadata helpers from `ufs.h`/`util.h`.

## Risks
Rename correctness depends on preserving ordering across target replacement, source deletion, and `..` updates. Link-count rollback paths are important for failed create/mkdir/symlink operations. Fast symlink bounds depend on mount-time `s_maxsymlinklen` validation.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ufs/namei.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ufs/super.c -->
# File Research: sources/os/linux/linux-stable/fs/ufs/super.c

## Summary
Implements UFS superblock handling: mount option parsing, filesystem flavor setup, superblock probing and validation, cylinder-group summary loading, sync/remount/statfs, export operations, inode cache setup, and module registration.

## Key APIs
- Mount/export: `ufs_fill_super()`, `ufs_get_tree()`, `ufs_reconfigure()`, `ufs_show_options()`, `ufs_statfs()`.
- Diagnostics/error policy: `ufs_error()`, `ufs_panic()`, `ufs_warning()`.
- Sync/lifetime: `ufs_sync_fs()`, `ufs_mark_sb_dirty()`, `ufs_put_super()`.
- NFS export helpers: `ufs_nfs_get_inode()`, `ufs_fh_to_dentry()`, `ufs_fh_to_parent()`, `ufs_get_parent()`.
- Module setup: `init_ufs_fs()`, `exit_ufs_fs()`.

## Important Behavior
Mount parameters support `ufstype=` and `onerror=` through the fs-context parser. `ufstype` is fixed at mount and cannot be changed during remount; `onerror` may be updated.

`ufs_fill_super()` initializes `ufs_sb_info`, chooses flavor-specific defaults for old UFS, Sun, SunOS, Sun x86, 44BSD, UFS2, HP, NeXTstep, NeXTstep CD, and OpenStep, then reads the on-disk superblock. Unsupported write modes are forced read-only for older/flavor-limited variants.

The superblock probe detects little-endian or big-endian media by trying known UFS magic values. NeXT/OpenStep probing can retry shifted `s_sbbase` locations. Fragment and block sizes must be powers of two and within accepted ranges before blocksize is finalized.

Clean-state handling marks unclean, active, bad, or fsck-needed filesystems read-only. For Sun-style state encodings, clean state is checked through `ufs_get_fs_state()` against `UFS_FSOK - fs_time`.

After validation, the file copies on-disk geometry into `ufs_sb_private_info`, computes derived masks/shifts, inode/addressing parameters, free-space reserve thresholds, max fast symlink length, max file size, root inode, and cylinder-group summaries for read-write mounts.

`ufs_read_cylinder_structures()` loads cylinder summary blocks and validates all cylinder-group headers. `ufs_put_super_internal()` writes summary state and releases loaded cylinder-group resources.

Sync updates `fs_time`, Sun-style fs state, and cylinder summary totals. Dirty superblocks are synced lazily through delayed work. Remount read-only writes summaries and clean state; remount read-write reloads cylinder structures and is allowed only for supported writable flavors.

## Dependencies
Uses buffer-head I/O, UFS endian helpers, UFS on-disk structures, cylinder helpers, inode operations, Linux fs-context/parser APIs, exportfs helpers, delayed work, slab caches, and VFS block-device mounting.

## Risks
A wrong `ufstype` can corrupt media; the code warns when defaulting to `old`. Mount correctness depends on exact flavor flags for directory entry format, UID format, clean-state format, cylinder-group layout, and UFS1/UFS2 address width. Error paths must release partially read superblock/cylinder resources. Delayed superblock sync must be canceled during unmount after internal writeback.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ufs/super.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ufs/swab.h -->
# File Research: sources/os/linux/linux-stable/fs/ufs/swab.h

## Summary
Defines filesystem-endian conversion helpers for UFS media that may be little-endian or big-endian.

## Main Contents
- Byte-order selector enum: `BYTESEX_LE`, `BYTESEX_BE`.
- Conversion helpers: `fs64_to_cpu()`, `cpu_to_fs64()`, `fs32_to_cpu()`, `cpu_to_fs32()`, `fs16_to_cpu()`, `cpu_to_fs16()`.
- In-place arithmetic helpers: `fs32_add()`, `fs32_sub()`, `fs16_add()`, `fs16_sub()`.

## Important Behavior
All helpers branch on `UFS_SB(sb)->s_bytesex`, which is set during superblock probing. The file assumes UFS media are either little-endian or big-endian, not mixed or unusual byte orders.

## Dependencies
Requires `UFS_SB()` from UFS in-core state and Linux endian conversion primitives.

## Risks
Every on-disk numeric access depends on `s_bytesex` being detected before use. Incorrect byte sex causes geometry, counters, inode fields, and bitmaps to be interpreted incorrectly.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ufs/swab.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ufs/ufs.h -->
# File Research: sources/os/linux/linux-stable/fs/ufs/ufs.h

## Summary
Defines UFS in-core superblock/inode state, mount option constants, debug macros, cross-file function prototypes, and helper accessors.

## Main Contents
- `struct ufs_sb_info`: per-mount state, flavor/byte-order flags, cylinder-group caches, delayed sync work, and mount lock.
- `struct ufs_inode_info`: UFS private inode data, direct/indirect block storage, fast symlink buffer, metadata lock, truncate mutex, and embedded VFS inode.
- Mount option constants for error policy and UFS flavor.
- Debug macro `UFSD()`.
- Prototypes for allocation, cylinder, directory, file, inode, namei, and superblock helpers.
- Accessors `UFS_SB()`, `UFS_I()`.
- Geometry helpers `ufs_dtog()` and `ufs_dtogd()`.

## Important Behavior
`ufs_sb_info` is the central in-memory mount object and stores both user-selected flavor and derived flags from `ufs_fs.h`. `ufs_inode_info.i_u1` abstracts UFS1 32-bit block pointers, UFS2 64-bit block pointers, and fast symlink storage in the same space.

## Dependencies
Included throughout UFS code. Depends on Linux inode/superblock types, workqueues, buffer heads, seqlocks, and UFS on-disk definitions.

## Risks
The shared union in `ufs_inode_info` must be interpreted consistently with UFS1/UFS2 magic and inode type. The header exposes many cross-file contracts, so layout or prototype drift affects the entire UFS implementation.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ufs/ufs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ufs/ufs_fs.h -->
# File Research: sources/os/linux/linux-stable/fs/ufs/ufs_fs.h

## Summary
Defines UFS on-disk format constants, superblock/cylinder/inode structures, filesystem flavor flags, and geometry macros used by the Linux UFS driver.

## Main Contents
- UFS/UFS2 magic values, superblock offsets, block/fragment constants, inode block indexes, root inode constants.
- Clean-state constants and flavor flags for directory entry, UID, state, cylinder-group, and UFS1/UFS2 encodings.
- Addressing macros for block/device conversion, cylinder group location, inode-to-block mapping, block/fragment rounding, and bitmap layout.
- Directory entry and cylinder summary structures.
- UFS1 and UFS2 inode structures.
- Cylinder group structures for modern and historic formats.
- `struct ufs_buffer_head`, `struct ufs_cg_private_info`, `struct ufs_sb_private_info`.
- Split superblock structures: `ufs_super_block_first`, `ufs_super_block_second`, `ufs_super_block_third`.

## Important Behavior
The header captures multiple UFS dialects in one set of structures. It separates the superblock into first/second/third chunks because the complete historical superblock can exceed a single 512-byte sector and is read through a multi-fragment `ufs_buffer_head`.

`ufs_sb_private_info` stores normalized, CPU-endian geometry and counters copied from disk at mount. Most runtime macros assume local variables named `uspi` and sometimes `sb`, so call sites must follow established UFS style.

UFS1 and UFS2 differ in block pointer width, superblock fields, timestamp width, cylinder summary placement, and maximum fast symlink storage. The header encodes these differences through unions and flavor flags.

## Dependencies
Used by all UFS files plus `swab.h`/`util.h`. Relies on Linux integer, stat, fs, workqueue, and division helpers.

## Risks
Structure definitions must match disk layout exactly. Several macros depend on caller-local variable names and derived mount geometry. UFS dialect flags must be set correctly during mount before interpreting directory entries, UID fields, state fields, and cylinder-group data.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ufs/ufs_fs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ufs/util.c -->
# File Research: sources/os/linux/linux-stable/fs/ufs/util.c

## Summary
Provides non-inline UFS utility routines for multi-fragment buffer-head handling, device number encoding/decoding, and page-cache folio acquisition.

## Key APIs
- `_ubh_bread_()`
- `ubh_bread_uspi()`
- `ubh_brelse()`
- `ubh_brelse_uspi()`
- `ubh_mark_buffer_dirty()`
- `ubh_sync_block()`
- `ubh_bforget()`
- `ubh_buffer_dirty()`
- `ufs_get_inode_dev()`
- `ufs_set_inode_dev()`
- `ufs_get_locked_folio()`

## Important Behavior
`_ubh_bread_()` allocates a `ufs_buffer_head` and reads a contiguous set of filesystem fragments; `ubh_bread_uspi()` performs the same read into the embedded superblock buffer in `ufs_sb_private_info`. Both require the requested size to align to fragment size and fit within `UFS_MAXFRAG`.

Buffer helpers release, mark dirty, synchronously write, forget, or test all buffer heads contained in a `ufs_buffer_head`.

Device encoding differs for Sun/Sun x86 variants. Sun-style special files may use SysV major/minor encoding, while other variants use old Linux device encoding. Sun x86 stores the device value in `i_data[1]`; other variants use `i_data[0]`.

`ufs_get_locked_folio()` locks an existing folio or reads it from disk, handles truncation races, and ensures buffer heads exist for the folio before returning it.

## Dependencies
Uses Linux buffer-head/page-cache APIs, UFS endian helpers, mount flavor flags, and UFS private inode structures.

## Risks
Partial read failures must release already-acquired buffers. Device encoding must match the filesystem flavor or special files will decode incorrectly. `ufs_get_locked_folio()` can return `NULL` for truncation races or an error pointer for read failures, so callers must distinguish both.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ufs/util.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ufs/util.h -->
# File Research: sources/os/linux/linux-stable/fs/ufs/util.h

## Summary
Defines inline UFS helpers for superblock field access, directory entry encoding, UID/GID conversion, buffer-head address arithmetic, bitmap operations, fragment accounting, block-pointer access, and timestamp conversion.

## Main Contents
- Buffer accessors: `UCPI_UBH()`, `USPI_UBH()`, `get_usb_offset()`, `ubh_get_usb_first/second/third()`, `ubh_get_ucg()`.
- Superblock state helpers: `ufs_get_fs_state()`, `ufs_set_fs_state()`, `ufs_get_fs_npsect()`, `ufs_get_fs_qbmask()`, `ufs_get_fs_qfmask()`.
- Directory entry helpers: `ufs_get_de_namlen()`, `ufs_set_de_namlen()`, `ufs_set_de_type()`.
- UID/GID helpers: `ufs_get_inode_uid()`, `ufs_set_inode_uid()`, `ufs_get_inode_gid()`, `ufs_set_inode_gid()`.
- Multi-fragment buffer declarations and address macros.
- Bitmap helpers: bit set/clear/test, next/last zero-bit search, full-block set/clear/test.
- Fragment accounting: `ufs_fragacct()`.
- Data pointer helpers for UFS1/UFS2: `ufs_get_direct_data_ptr()`, `ufs_data_ptr_to_cpu()`, `ufs_cpu_to_data_ptr()`, `ufs_data_ptr_clear()`, `ufs_is_data_ptr_zero()`.
- Time helper: `ufs_get_seconds()`.

## Important Behavior
State, qmask, npsect, directory name length, and UID/GID fields are layout-dependent and switch on flags set in `UFS_SB(sb)->s_flags`.

Bitmap helpers operate across fragmented `ufs_buffer_head` storage instead of one contiguous bitmap. Full-block helpers set or clear bit groups according to fragments-per-block values of 1, 2, 4, or 8.

UFS1 and UFS2 block pointers are abstracted through helpers that read/write either 32-bit or 64-bit on-disk fields depending on `fs_magic`.

`ufs_get_seconds()` intentionally wraps 32-bit superblock/cylinder timestamps instead of clamping, preserving UFS dirty-state logic through unsigned 32-bit time behavior.

## Dependencies
Uses UFS endian helpers, Linux bitmap helpers, UFS private geometry, and buffer-head/page-cache types.

## Risks
Many macros rely on an in-scope `uspi` variable. The comments mark 44BSD directory name length handling as suspicious. Bitmap address macros must stay synchronized with fragment size and buffer layout. Data pointer helpers must only be used after UFS1/UFS2 magic is known.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ufs/util.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/unicode/Kconfig -->
# File Research: sources/os/linux/linux-stable/fs/unicode/Kconfig

## Summary
Adds Kconfig options for kernel UTF-8 normalization/casefolding support and its KUnit tests.

## Main Contents
- `CONFIG_UNICODE`: tristate UTF-8 NFD normalization and NFD+CF casefolding support.
- `CONFIG_UNICODE_NORMALIZATION_KUNIT_TEST`: tristate KUnit test module depending on `UNICODE && KUNIT`, defaulting with `KUNIT_ALL_TESTS`.

## Important Behavior
`UNICODE` can be built-in or modular. When modular, the large UTF-8 data table can be a separate loadable module requested only by filesystems that need it.

## Dependencies
Uses Kconfig tristate and KUnit dependency mechanisms.

## Risks
Filesystems using Unicode normalization need `CONFIG_UNICODE`; tests require both Unicode support and KUnit.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/unicode/Kconfig -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/unicode/Makefile -->
# File Research: sources/os/linux/linux-stable/fs/unicode/Makefile

## Summary
Builds the Unicode normalization implementation, generated data table, KUnit tests, and optional host-side data generator.

## Main Contents
- Builds `unicode.o` from `utf8-norm.o` and `utf8-core.o`.
- Builds `utf8data.o` when `CONFIG_UNICODE` is enabled.
- Builds `tests/utf8_kunit.o` for normalization tests.
- Defines generation of `utf8data.c` either by copying `utf8data.c_shipped` or regenerating from Unicode Character Database text files.
- Registers host program `mkutf8data`.

## Important Behavior
Normal builds copy the checked-in generated data file. Passing `REGENERATE_UTF8DATA=1` invokes `mkutf8data` with DerivedAge, DerivedCombiningClass, DerivedCoreProperties, UnicodeData, CaseFolding, NormalizationCorrections, and NormalizationTest inputs.

## Dependencies
Uses Linux kbuild object, host program, target, and `if_changed` rules.

## Risks
Regeneration depends on all expected UCD files being present in the directory and matching the parser assumptions in `mkutf8data.c`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/unicode/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/unicode/mkutf8data.c -->
# File Research: sources/os/linux/linux-stable/fs/unicode/mkutf8data.c

## Summary
Host-side generator that parses Unicode Character Database files, builds compact versioned UTF-8 normalization tries for NFDI and NFDICF, verifies them, runs normalization tests, and emits `utf8data.c`.

## Key Components
- UCD input parsing: `age_init()`, `ccc_init()`, `nfdi_init()`, `nfdicf_init()`, `ignore_init()`, `corrections_init()`.
- Decomposition processing: `hangul_decompose()`, `nfdi_decompose()`, `nfdicf_decompose()`, `utf8_init()`.
- Trie operations: `insert()`, `prune()`, `mark_nodes()`, `index_nodes()`, `size_nodes()`, `emit()`, `trees_populate()`, `trees_reduce()`.
- Verification/testing: `verify()`, `trees_verify()`, `normalization_test()`.
- Runtime-equivalent lookup/cursor helpers used for generator self-tests.
- Output: `write_file()`.
- Entry point: `main()`.

## Important Behavior
The generator supports two normalization forms tailored for filenames: `nfdi` applies canonical NFD and removes default ignorables; `nfdicf` also applies full casefolding using C+F mappings.

Unicode ages are packed with `UNICODE_AGE()` and compressed into generation numbers. Generated leaves store generation, canonical combining class, and optional decomposition strings. This allows runtime filtering by supported Unicode version.

The code builds a compact binary trie over valid UTF-8 byte sequences. Internal nodes encode bit tests, next-byte transitions, relative offsets, and node/leaf flags. Subtrees with identical leaves are collapsed, then pruned further when singleton chains make identical decisions.

Multiple trees are generated for normalization correction ages and for the latest NFDI/NFDICF tables. Older correction trees share or forward to later trees where possible.

The parser reads canonical decomposition mappings from `UnicodeData.txt`, ignores compatibility forms, applies full casefold mappings from `CaseFolding.txt`, removes `Default_Ignorable_Code_Point` entries from `DerivedCoreProperties.txt`, and applies normalization corrections from `NormalizationCorrections.txt`.

Hangul syllables are decomposed algorithmically. The generator marks Hangul leaves with a special `HANGUL` cookie instead of storing every decomposition string.

Generated trie data is aligned and emitted as a static byte array plus `utf8agetab`, `utf8nfdicfdata`, `utf8nfdidata`, and exported `utf8_data_table`.

## Dependencies
Runs as a host C program using libc file I/O, `getopt`, allocation, assertions, and string parsing. Its output is consumed by `utf8-core.c` and `utf8-norm.c`.

## Risks
The parser depends on UCD text file formats and fixed maximum decomposition mapping length assumptions. Trie correctness depends on offset sizing stabilizing through repeated indexing/sizing passes. The generated data must match the runtime trie decoder in `utf8-norm.c`; the file intentionally contains a runtime-equivalent decoder for verification.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/unicode/mkutf8data.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/unicode/tests/utf8_kunit.c -->
# File Research: sources/os/linux/linux-stable/fs/unicode/tests/utf8_kunit.c

## Summary
KUnit test suite for Linux UTF-8 normalization and casefolding support.

## Key Tests
- `check_supported_versions()`
- `check_utf8_comparisons()`
- `check_utf8_nfdicf()`
- `check_utf8_nfdi()`
- Suite setup/teardown: `init_test_ucd()`, `exit_test_ucd()`

## Important Behavior
The test data covers direct ASCII, canonical decomposition, canonical ordering, non-canonical compatibility cases that must not decompose under NFD, Greek normalization correction behavior, full casefolding, multi-character folds such as sharp-s, and codepoints introduced in newer Unicode versions.

Tests compare `utf8nlen()` lengths against expected normalized byte lengths, then iterate normalized bytes with `utf8byte()` and compare every output byte. Comparison tests ensure `utf8_strncmp()` and `utf8_strncasecmp()` report equality between original and expected normalized/casefolded forms.

Version tests assert support for Unicode 7.0.0, 9.0.0, and `UTF8_LATEST`, and reject unsupported future/zero/invalid ages.

## Dependencies
Uses KUnit, `linux/unicode.h`, internal `utf8n.h`, and `utf8_load()`/`utf8_unload()` to access generated Unicode tables.

## Risks
The test suite is focused on representative normalization/casefold examples, not exhaustive UCD coverage. Exhaustive validation is handled by `mkutf8data.c` during data generation.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/unicode/tests/utf8_kunit.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/unicode/utf8-core.c -->
# File Research: sources/os/linux/linux-stable/fs/unicode/utf8-core.c

## Summary
Provides exported kernel APIs for UTF-8 validation, normalized comparison, casefolding, normalized hashing, normalization output, Unicode table loading/unloading, and version parsing.

## Key APIs
- `utf8_validate()`
- `utf8_strncmp()`
- `utf8_strncasecmp()`
- `utf8_strncasecmp_folded()`
- `utf8_casefold()`
- `utf8_casefold_hash()`
- `utf8_normalize()`
- `utf8_load()`
- `utf8_unload()`
- `utf8_parse_version()`

## Important Behavior
Validation calls `utf8nlen()` in `UTF8_NFDI` mode and returns failure for invalid UTF-8.

Comparisons create `utf8cursor` instances and compare normalized byte streams. Case-insensitive comparisons use `UTF8_NFDICF`; case-sensitive normalized comparisons use `UTF8_NFDI`.

`utf8_casefold()` and `utf8_normalize()` stream normalized bytes into a caller buffer and return the output length excluding the terminating NUL. They return `-EINVAL` if the buffer is too small or input is invalid.

`utf8_casefold_hash()` hashes the NFDI+casefold byte stream with VFS name-hash helpers and writes `qstr.hash`.

`utf8_load()` allocates a `unicode_map`, requests the `utf8_data_table` symbol, validates requested Unicode version support, and selects the appropriate NFDI/NFDICF table entries. `utf8_unload()` releases the symbol and map.

`utf8_parse_version()` accepts strings of the form `major.minor.revision` and returns packed `UNICODE_AGE()` values.

## Dependencies
Uses generated `utf8_data_table`, trie/cursor functions from `utf8-norm.c`, kernel symbol request/put, string hash helpers, parser helpers, and `struct unicode_map`.

## Risks
Callers must load a supported Unicode version before using normalization APIs. Output functions require enough destination space for the normalized form plus NUL. `utf8_strncasecmp_folded()` assumes its first argument is already valid folded UTF-8.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/unicode/utf8-core.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/unicode/utf8-norm.c -->
# File Research: sources/os/linux/linux-stable/fs/unicode/utf8-norm.c

## Summary
Implements the UTF-8 trie decoder and normalization cursor used by kernel Unicode normalization and casefolding.

## Key APIs
- `utf8version_is_supported()`
- `utf8nlen()`
- `utf8ncursor()`
- `utf8byte()`

## Important Behavior
The file decodes a compact generated trie. Internal node bytes encode bit tests, optional next-byte advancement, relative right-node offsets, and node/leaf markers. Leaves contain Unicode generation, canonical combining class, and optional decomposition string.

`utf8nlookup()` validates UTF-8 by walking the trie and returns a leaf only for well-formed Unicode scalar values known to the generated table. Surrogates and invalid encodings are excluded by construction.

Hangul syllables are decomposed algorithmically when a leaf contains the special `HANGUL` marker. The synthesized leaf emits L, V, and optional T jamo sequences.

`utf8nlen()` computes the byte length of the normalized form without producing it. Characters newer than the selected table version pass through with their original byte length; decomposable characters use decomposition length.

`utf8ncursor()` initializes a normalization cursor and rejects NULL strings, length truncation overflow, and inputs beginning with a UTF-8 continuation byte.

`utf8byte()` streams one normalized byte at a time. It expands decomposition strings, skips empty decompositions for default ignorables, treats too-new characters as stoppers, and performs canonical combining class ordering by repeated scans between stopper characters.

## Dependencies
Consumes `struct unicode_map`, generated `utf8data` tables, `enum utf8_normalization`, and internal declarations from `utf8n.h`.

## Risks
Runtime trie decoding must stay byte-for-byte compatible with `mkutf8data.c` emission. The cursor intentionally rescans combining runs, so malformed trie data or invalid leaves would affect normalization ordering and validation. Callers must handle `-1` from `utf8byte()` as invalid input.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/unicode/utf8-norm.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/unicode/utf8n.h -->
# File Research: sources/os/linux/linux-stable/fs/unicode/utf8n.h

## Summary
Internal Unicode normalization header shared by UTF-8 core, normalizer, tests, and generated data.

## Main Contents
- Declaration: `utf8version_is_supported()`.
- Normalized length API: `utf8nlen()`.
- `UTF8HANGULLEAF` size constant.
- `struct utf8cursor` normalization cursor state.
- Cursor APIs: `utf8ncursor()`, `utf8byte()`.
- Generated table descriptors: `struct utf8data`, `struct utf8data_table`.
- Exported generated table symbol: `utf8_data_table`.

## Important Behavior
`struct utf8cursor` stores the selected `unicode_map`, normalization form, current source/decomposition pointers, saved scan positions, remaining lengths, current and next canonical combining classes, and a small buffer for algorithmic Hangul decomposition.

`struct utf8data_table` groups the generated age table, NFDICF table descriptors, NFDI table descriptors, and raw trie byte array.

## Dependencies
Includes Linux Unicode public types, export/module/string headers, and is consumed by both built code and KUnit tests.

## Risks
Cursor layout is coupled to `utf8-norm.c`. Generated table structure layout is coupled to `mkutf8data.c` output and `utf8-core.c` table loading.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/unicode/utf8n.h -->