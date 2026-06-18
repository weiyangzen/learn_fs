# Research Report: subset-b-005775

This grouped report covers the assigned UFS and Unicode source files. Each section preserves the source path in its title and is delimited for reconciliation into the final source-tree-aligned per-file documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ufs/namei.c -->
# sources/distributed-fs/ceph-client/fs/ufs/namei.c

## Purpose
`namei.c` implements UFS VFS namespace operations: lookup, create, mknod, symlink, hard link, mkdir, unlink, rmdir, and rename. It is the bridge between VFS dentries/inodes and lower UFS directory primitives from `dir.c`, inode allocation from `ialloc.c`, and inode setup from `inode.c`/`file.c`.

## Important APIs, Types, And Functions
The exported integration point is `ufs_dir_inode_operations`. `ufs_lookup()` validates `UFS_MAXNAMLEN`, resolves inode numbers via `ufs_inode_by_name()`, and materializes aliases with `ufs_iget()` and `d_splice_alias()`. `ufs_create()`, `ufs_mknod()`, and `ufs_symlink()` allocate new inodes with `ufs_new_inode()`, install inode/file/address-space operations, and call `ufs_add_nondir()`. `ufs_mkdir()` sets up directory operations, link counts, and `.`/`..` via `ufs_make_empty()`. `ufs_rename()` handles `RENAME_NOREPLACE`, replacement, directory `..` updates, and link count transitions.

## Control Flow
Most create-like paths allocate first, initialize mode-specific state, mark the inode dirty, then insert a directory entry. On add failure, `ufs_add_nondir()` decrements the link count and discards the new inode. Rename first finds the old entry, optionally finds the old directory's `..`, replaces or adds the destination entry, updates ctime, deletes the old entry, then adjusts parent link counts and `..` if a directory moved across parents.

## State And Persistence
Persistent state changes are directory entries, inode link counts, inode ctime/size, special-device encoded data, fast symlink payloads in `UFS_I(inode)->i_u1.i_symlink`, and dirty inode metadata. Folio-backed directory entries are released with `folio_release_kmap()` after modification.

## Dependencies And Integration Points
The file depends on UFS directory helpers (`ufs_add_link`, `ufs_find_entry`, `ufs_delete_entry`, `ufs_set_link`, `ufs_empty_dir`, `ufs_dotdot`), allocation (`ufs_new_inode`), inode loading (`ufs_iget`), file/page symlink operations, `ufs_aops`, and VFS dentry/link-count APIs.

## Risks And Test Signals
Risk concentrates around link-count rollback, directory rename corner cases, and fast-vs-slow symlink length handling. Useful tests are VFS namespace suites over UFS images: create/link/unlink/rmdir/rename replacement, cross-directory directory rename, long names, fast and slow symlinks, special files, and forced error injection in directory insertion/deletion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ufs/namei.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ufs/super.c -->
# sources/distributed-fs/ceph-client/fs/ufs/super.c

## Purpose
`super.c` owns UFS filesystem registration, mount/reconfigure/unmount, superblock parsing, export support, inode cache setup, statfs, error policy, and delayed superblock syncing. It translates user mount options and on-disk superblock variants into `struct ufs_sb_info` and `struct ufs_sb_private_info`.

## Important APIs, Types, And Functions
External-facing entry points are the `file_system_type` named `ufs`, `ufs_context_ops`, `ufs_super_ops`, and `ufs_export_ops`. `ufs_parse_param()` handles `ufstype=` and `onerror=`. `ufs_fill_super()` is the central mount path. `ufs_setup_cstotal()`, `ufs_put_cstotal()`, `ufs_read_cylinder_structures()`, and `ufs_put_super_internal()` load/store summary and cylinder-group state. `ufs_sync_fs()` and `ufs_mark_sb_dirty()` update superblock timestamps and schedule delayed sync work. `ufs_reconfigure()` handles ro/rw transitions. `ufs_statfs()` reports free space and inode counts.

## Control Flow
Mount allocates `ufs_sb_info`, initializes locks/work, chooses a flavour-specific expected block size, superblock size, flags, and read-only constraints, then reads the superblock with `ubh_bread_uspi()`. It retries when on-disk fragment/superblock sizes differ from the initial assumption and tries alternate NeXTstep offsets. After byte-order/magic validation it checks clean state, fills derived geometry, computes allocation thresholds and `s_maxbytes`, loads root inode, copies total summaries, and for writable mounts reads cylinder groups.

## State And Persistence
Persistent metadata includes `fs_clean`, `fs_time`, fs_state checksums for Sun variants, cylinder summaries, and loaded cylinder groups. Errors mark writable filesystems bad, dirty the superblock buffer, queue delayed sync, and force `SB_RDONLY` according to `onerror`. Unmount/remount-ro writes summary state back before releasing buffers.

## Dependencies And Integration Points
This file integrates with the VFS fs_context API, block-device mounting, NFS export helpers, UFS inode operations (`ufs_iget`, `ufs_write_inode`, `ufs_evict_inode`), cylinder cache (`ufs_put_cylinder`), buffer helpers from `util.c`, byte swapping from `swab.h`, and on-disk layout declarations from `ufs_fs.h`.

## Risks And Test Signals
Risk areas are flavour detection, endian switching, clean-state logic, retry paths, writable-vs-read-only gating, cylinder summary I/O, delayed work lifetime, and reconfigure failure cleanup. Test signals include mounting representative old/sun/sunos/sunx86/44bsd/ufs2/nextstep/openstep/hp images, remount ro/rw, statfs consistency, NFS file-handle lookup, dirty superblock sync, and fault injection in superblock/cylinder reads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ufs/super.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ufs/swab.h -->
# sources/distributed-fs/ceph-client/fs/ufs/swab.h

## Purpose
`swab.h` centralizes endian conversion for UFS on-disk integer types. UFS images may be little-endian or big-endian, and runtime conversion is selected by `UFS_SB(sb)->s_bytesex`.

## Important APIs, Types, And Functions
The file defines `BYTESEX_LE` and `BYTESEX_BE`, plus inline converters for `__fs64`, `__fs32`, and `__fs16`: `fs64_to_cpu()`, `cpu_to_fs64()`, `fs32_to_cpu()`, `cpu_to_fs32()`, `fs16_to_cpu()`, and `cpu_to_fs16()`. It also provides in-place arithmetic helpers `fs32_add()`, `fs32_sub()`, `fs16_add()`, and `fs16_sub()`.

## Control Flow
Each helper checks the mounted filesystem byte sex and dispatches to Linux endian primitives such as `le32_to_cpu`, `be32_to_cpu`, `cpu_to_le64`, or `be16_add_cpu`. No persistent state is held here; state is read from the superblock info established by `super.c` after magic-number probing.

## State And Persistence
The helpers directly affect persistence when callers write superblocks, cylinder groups, inode fields, directory entry lengths, and free-space counters. Correctness depends on all accesses to `__fs*` fields using these wrappers rather than raw casts.

## Dependencies And Integration Points
`swab.h` depends on `UFS_SB()` from `ufs.h` and Linux endian helpers. It is included by UFS superblock, utility, allocation, inode, and directory code that touches on-disk fields.

## Risks And Test Signals
The stated design assumes only big-endian and little-endian UFS variants. Risks include missing conversions, arithmetic on sparse bitwise types, or using a helper before `s_bytesex` is initialized. Test signals are successful mount/read/write/statfs on both endian image variants and fsck-compatible on-disk metadata after mutations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ufs/swab.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ufs/ufs.h -->
# sources/distributed-fs/ceph-client/fs/ufs/ufs.h

## Purpose
`ufs.h` is the in-kernel UFS private interface. It defines in-core superblock and inode state, mount option bits, debug macros, cross-file function declarations, and helper accessors used across the UFS implementation.

## Important APIs, Types, And Functions
`struct ufs_sb_info` stores the parsed private superblock pointer, cylinder summary cache, byte sex, flavour flags, cylinder group buffers, error policy, delayed sync work, and locks. `struct ufs_inode_info` embeds UFS block pointers/fast symlink storage, flags, truncation and metadata synchronization state, and the VFS inode. `UFS_SB()` and `UFS_I()` convert VFS objects to UFS private structures. The file declares UFS allocation, directory, file, inode, and superblock functions. `ufs_dtog()` and `ufs_dtogd()` map filesystem blocks to cylinder groups.

## Control Flow
There is little executable flow here beyond inline conversion helpers. The header establishes contracts followed by `super.c` during mount, `namei.c` during namespace changes, allocation code during block/inode allocation, and inode/file code during read/write/truncate.

## State And Persistence
The in-core structures mirror persistent UFS state but also maintain transient caches and synchronization. `s_lock`, `work_lock`, `sync_work`, `s_cg_loaded`, and `s_cgno[]` protect lifecycle and caching. `i_u1` stores either on-disk block pointers or fast symlink bytes that later get written to disk.

## Dependencies And Integration Points
It depends on `ufs_fs.h` for on-disk types and Linux VFS primitives. It is included by almost every UFS implementation file and is the main internal ABI among superblock, inode, directory, allocation, and utility code.

## Risks And Test Signals
Risks include layout assumptions in `container_of`, stale or inconsistent cylinder group cache state, and mismatched mount flags across modules. Compile coverage across all UFS configs and mount/runtime testing that exercises delayed sync, truncation, allocation, and namespace operations are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ufs/ufs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ufs/ufs_fs.h -->
# sources/distributed-fs/ceph-client/fs/ufs/ufs_fs.h

## Purpose
`ufs_fs.h` describes UFS on-disk format constants, bitwise filesystem integer types, geometry macros, directory entries, cylinder groups, UFS1/UFS2 inodes, split superblock structures, and private parsed superblock/cylinder-group structures.

## Important APIs, Types, And Functions
Important declarations include `__fs64`, `__fs32`, `__fs16`, magic values for UFS/UFS2/HP variants, mount flag masks (`UFS_DE_*`, `UFS_UID_*`, `UFS_ST_*`, `UFS_CG_*`, `UFS_TYPE_*`), geometry macros (`ufs_cgstart`, `ufs_inotofsba`, `ufs_blkroundup`, etc.), `struct ufs_dir_entry`, `struct ufs_csum_core`, `struct ufs_cylinder_group`, `struct ufs_inode`, `struct ufs2_inode`, `struct ufs_buffer_head`, `struct ufs_cg_private_info`, `struct ufs_sb_private_info`, and the three split superblock structs.

## Control Flow
The file is declarative, but its macros drive runtime address calculations for superblock parsing, cylinder-group loading, inode lookup, block allocation, directory record sizing, and statfs. Macros intentionally refer to local variables such as `uspi` or `sb`, so callers must provide the expected context.

## State And Persistence
This is the authoritative map for persistent UFS metadata: superblock fields, fs state/clean flags, cylinder-group free maps and summaries, inode ownership/timestamps/block pointers, directory record layout, and UFS2 64-bit extensions. `ufs_sb_private_info` caches parsed and derived values such as masks, shifts, total counts, allocation thresholds, and maximum fast symlink length.

## Dependencies And Integration Points
It integrates with endian helpers in `swab.h`, accessors in `util.h`, and all UFS implementation files. The structs must match disk layout, including packed UFS2 superblock portions and fixed-size split superblock chunks.

## Risks And Test Signals
Risks are high because a wrong field, shift, mask, or struct alignment corrupts all downstream parsing. Test signals are mounting validated UFS1/UFS2 images from multiple producers, comparing kernel-derived statfs/inode geometry against fsck or dump tools, and exercising allocation/free paths that rely on cylinder-group offsets and bitmaps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ufs/ufs_fs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ufs/util.c -->
# sources/distributed-fs/ceph-client/fs/ufs/util.c

## Purpose
`util.c` implements shared UFS buffer, device-number, and folio helpers. These routines support superblock/cylinder-group multi-fragment I/O, metadata dirtying/syncing, special inode device encoding, and directory/pagecache access.

## Important APIs, Types, And Functions
`_ubh_bread_()` allocates a `struct ufs_buffer_head` and reads a contiguous fragment range. `ubh_bread_uspi()` reuses the embedded superblock buffer in `ufs_sb_private_info`. `ubh_brelse()`, `ubh_brelse_uspi()`, `ubh_mark_buffer_dirty()`, `ubh_sync_block()`, `ubh_bforget()`, and `ubh_buffer_dirty()` manage buffer lifetime and state. `ufs_get_inode_dev()` and `ufs_set_inode_dev()` translate special-device encodings, including Sun/Sunx86 sysv-style devices. `ufs_get_locked_folio()` locates or reads and locks pagecache folios and ensures buffer_heads exist.

## Control Flow
Read helpers validate fragment-aligned sizes and `UFS_MAXFRAG`, then loop over `sb_bread()` calls with failure unwind. Device helpers branch on `UFS_ST_MASK`. `ufs_get_locked_folio()` first tries `filemap_lock_folio()`, falls back to `read_mapping_folio()`, locks the folio, handles truncate races, and creates empty buffers using the inode block size.

## State And Persistence
Buffer helpers pin metadata blocks, propagate dirty state, force synchronous writes, or forget buffers. Device helpers persist encoded `dev_t` values into inode block-pointer storage. Folio helper state is transient but important for directory/block modification paths.

## Dependencies And Integration Points
The file uses Linux buffer-head and folio APIs, `old_encode_dev`/`sysv_encode_dev`, UFS endian conversion, and UFS private structures. It is consumed by mount, directory, allocation, inode, and write paths.

## Risks And Test Signals
Risks include partial-read unwinds, embedded `USPI_UBH` reuse, fragment-size validation, folio truncate races, and device encoding compatibility. Tests should inject read failures, mount/write UFS images with varied fragment sizes, create device nodes on Sun and non-Sun variants, and exercise directory operations under memory pressure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ufs/util.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ufs/util.h -->
# sources/distributed-fs/ceph-client/fs/ufs/util.h

## Purpose
`util.h` provides inline helpers and macros for UFS variant-specific field access, bitmap manipulation across fragmented buffer_heads, free-fragment accounting, data pointer access for UFS1/UFS2, and timestamp conversion.

## Important APIs, Types, And Functions
It defines `UCPI_UBH()` and `USPI_UBH()`, superblock state helpers (`ufs_get_fs_state`, `ufs_set_fs_state`, `ufs_get_fs_npsect`, `ufs_get_fs_qbmask`, `ufs_get_fs_qfmask`), directory entry helpers (`ufs_get_de_namlen`, `ufs_set_de_namlen`, `ufs_set_de_type`), UID/GID helpers, declarations for `util.c`, and `ubh_get_usb_*()` split-superblock accessors. Bitmap helpers include `ubh_get_addr*`, `ubh_find_next_zero_bit`, `ubh_find_last_zero_bit`, `ubh_isblockset`, `ubh_clrblock`, `ubh_setblock`, and `ufs_fragacct()`. Data-pointer helpers abstract 32-bit UFS1 vs 64-bit UFS2 block pointers.

## Control Flow
Most functions dispatch on `UFS_ST_MASK`, `UFS_UID_MASK`, `UFS_DE_MASK`, or `uspi->fs_magic`. Bitmap search walks per-fragment buffers using derived bit-per-fragment shifts; block helpers select masks based on fragments per block.

## State And Persistence
The header reads and writes persistent superblock state, directory names/types, inode owner IDs, cylinder-group free maps, fragment summary counters, and inode data pointers. `ufs_get_seconds()` wraps real time into a filesystem 32-bit timestamp for superblock/group metadata.

## Dependencies And Integration Points
It depends on `ufs_fs.h`, `ufs.h`, `swab.h`, Linux buffer-head/pagecache APIs, and bitops. Its macros assume in-scope `uspi` in several call sites, matching older UFS code style.

## Risks And Test Signals
Risks include variant-specific field confusion, the noted comments that 44BSD directory name length assignment "seems wrong", pointer arithmetic across fragmented buffers, and 2038/2106 timestamp behavior. Tests should cover old/44BSD/Sun/Sunx86/UFS2 image operations, bitmap allocation/free invariants, UID/GID round trips, and fast symlink/block pointer writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ufs/util.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/unicode/Kconfig -->
# sources/distributed-fs/ceph-client/fs/unicode/Kconfig

## Purpose
This Kconfig fragment exposes kernel configuration switches for UTF-8 normalization and casefolding support used by filesystems, plus KUnit coverage for that support.

## Important APIs, Types, And Functions
`config UNICODE` is a tristate option titled "UTF-8 normalization and casefolding support". Its help text explains that enabling it provides UTF-8 NFD normalization and NFD+CF casefolding, and as a module the large casefolding table is loadable on demand. `config UNICODE_NORMALIZATION_KUNIT_TEST` is a tristate test option depending on `UNICODE && KUNIT` and defaults to `KUNIT_ALL_TESTS`.

## Control Flow
Build-time selection controls whether the Unicode runtime object and generated data table are compiled in or loadable. The test option pulls in `tests/utf8_kunit.o` when KUnit is enabled.

## State And Persistence
No runtime state is defined here. The persistent effect is kernel build configuration: whether filesystems can call the exported Unicode normalization APIs and whether tests are available.

## Dependencies And Integration Points
`UNICODE` feeds the Unicode `Makefile`, producing `unicode.o` and `utf8data.o`. Filesystems such as ext4/f2fs can depend on this normalization support for case-insensitive directory handling. The test symbol integrates with KUnit.

## Risks And Test Signals
Risks are mainly configuration coverage: module vs built-in linkage and test availability. Test signals are successful allmodconfig/built-in/module builds and KUnit execution under `CONFIG_UNICODE_NORMALIZATION_KUNIT_TEST`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/unicode/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/unicode/Makefile -->
# sources/distributed-fs/ceph-client/fs/unicode/Makefile

## Purpose
The Unicode Makefile builds the UTF-8 normalization runtime, generated data table, optional KUnit tests, and the host-side `mkutf8data` generator used to refresh the checked-in data table from Unicode Character Database text files.

## Important APIs, Types, And Functions
When `CONFIG_UNICODE` is set, `unicode.o` is built from `utf8-norm.o` and `utf8-core.o`, and `utf8data.o` is included. `CONFIG_UNICODE_NORMALIZATION_KUNIT_TEST` adds `tests/utf8_kunit.o`. The target `$(obj)/utf8data.c` either copies `utf8data.c_shipped` or, under `REGENERATE_UTF8DATA=1`, invokes `mkutf8data` with `DerivedAge.txt`, `DerivedCombiningClass.txt`, `DerivedCoreProperties.txt`, `UnicodeData.txt`, `CaseFolding.txt`, `NormalizationCorrections.txt`, and `NormalizationTest.txt`.

## Control Flow
Normal builds avoid regeneration and copy the shipped generated file. Regeneration is opt-in and depends on UCD input files being present in the source directory. `targets += utf8data.c` registers generated output, while `hostprogs += mkutf8data` builds the host generator.

## State And Persistence
The Makefile materializes `utf8data.c` in the object tree. That generated C file persists normalization tables exported by `utf8_data_table` in the final kernel/module.

## Dependencies And Integration Points
It integrates with Kbuild object syntax, host program rules, and the runtime files `utf8-norm.c`, `utf8-core.c`, and `utf8n.h`.

## Risks And Test Signals
Risks include target spelling consistency, stale shipped data, missing UCD inputs during regeneration, and module/built-in dependency ordering. Signals are clean incremental builds with and without `REGENERATE_UTF8DATA=1`, plus KUnit tests against the resulting table.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/unicode/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/unicode/mkutf8data.c -->
# sources/distributed-fs/ceph-client/fs/unicode/mkutf8data.c

## Purpose
`mkutf8data.c` is a host generator that reads Unicode Character Database files and emits compact C trie data for kernel UTF-8 NFDI and NFDICF normalization. Its output is `utf8data.c`, consumed by the runtime Unicode module.

## Important APIs, Types, And Functions
Global inputs default to UCD filenames and are overridden by `-a`, `-c`, `-d`, `-f`, `-n`, `-p`, `-t`, and `-o`. `struct unicode_data` tracks code point, canonical combining class, age generation, corrections, and UTF-32/UTF-8 decompositions. `struct tree`/`struct node` build compact tries. Parsing and data setup is handled by `age_init()`, `ccc_init()`, `nfdi_init()`, `nfdicf_init()`, `ignore_init()`, and `corrections_init()`. Decomposition and table generation use `hangul_decompose()`, `nfdi_decompose()`, `nfdicf_decompose()`, `utf8_init()`, `trees_init()`, `trees_populate()`, `trees_reduce()`, `trees_verify()`, `normalization_test()`, and `write_file()`.

## Control Flow
`main()` initializes every code point, parses UCD data, expands canonical/casefold/ignorable/correction mappings, synthesizes Hangul decomposition cookies, converts mappings to UTF-8, builds versioned NFDI/NFDICF tries, prunes and indexes trie nodes until offset sizes stabilize, verifies lookups for all Unicode scalar values, runs normalization tests from `NormalizationTest.txt`, then writes C arrays and `utf8_data_table`.

## State And Persistence
All state is in host-process globals and heap allocations. Persistent output is generated C containing age tables, per-version trie offsets, packed trie bytes, and exported module metadata. It intentionally does not store full Hangul decompositions; runtime expands them algorithmically.

## Dependencies And Integration Points
The generator depends on libc, UCD file formats, Kbuild host tooling, and an implementation of the same trie/cursor logic used by `utf8-norm.c` for self-verification. Its output format must match `struct utf8data_table` in `utf8n.h`.

## Risks And Test Signals
Risks include fixed `LINESIZE`, fixed decomposition array sizes, parser assumptions about UCD format, correction-version tree logic, offset-size convergence, and emitted-table ABI drift. Signals are successful regeneration, zero `normalization_test()` failures, deterministic diffs against expected shipped data, and runtime KUnit success with regenerated tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/unicode/mkutf8data.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/unicode/tests/utf8_kunit.c -->
# sources/distributed-fs/ceph-client/fs/unicode/tests/utf8_kunit.c

## Purpose
`utf8_kunit.c` provides KUnit tests for the kernel Unicode normalization runtime. It validates supported Unicode versions, NFDI normalization, NFDICF casefolding, and comparison helpers.

## Important APIs, Types, And Functions
The test vectors `nfdi_test_data` and `nfdicf_test_data` encode representative UTF-8 input and expected normalized/casefolded byte strings. `check_utf8_nfdi()` validates `utf8nlen()`, `utf8ncursor()`, and `utf8byte()` for canonical decomposition and combining-class ordering. `check_utf8_nfdicf()` validates folding cases across Unicode versions. `check_utf8_comparisons()` checks `utf8_strncmp()` and `utf8_strncasecmp()`. `check_supported_versions()` checks `utf8version_is_supported()`. Suite init loads `UTF8_LATEST` via `utf8_load()` and exit calls `utf8_unload()`.

## Control Flow
KUnit creates a `unicode_map`, stores it in `test->priv`, then each case iterates static test vectors. Cursor tests stream normalized bytes and compare each byte to expected output; comparison tests use `struct qstr` wrappers.

## State And Persistence
The only runtime state is the loaded Unicode map and cursor-local iteration state. There is no persistent data mutation; the test observes the generated normalization table.

## Dependencies And Integration Points
It depends on `CONFIG_UNICODE`, KUnit, `<linux/unicode.h>`, and internal `utf8n.h` declarations. When built as a module, `utf8-norm.c` exports selected internals for the test.

## Risks And Test Signals
The vectors cover important cases but are not exhaustive for invalid UTF-8, truncation, zero-length buffers, or all Unicode versions. Passing this suite signals that table loading, core normalization, folding, comparison, and version checks are functional.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/unicode/tests/utf8_kunit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/unicode/utf8-core.c -->
# sources/distributed-fs/ceph-client/fs/unicode/utf8-core.c

## Purpose
`utf8-core.c` exports filesystem-facing UTF-8 validation, normalized comparison, casefolding, hashing, normalization, Unicode table loading/unloading, and version parsing.

## Important APIs, Types, And Functions
Exported functions are `utf8_validate()`, `utf8_strncmp()`, `utf8_strncasecmp()`, `utf8_strncasecmp_folded()`, `utf8_casefold()`, `utf8_casefold_hash()`, `utf8_normalize()`, `utf8_load()`, `utf8_unload()`, and `utf8_parse_version()`. `find_table_version()` selects an exact `struct utf8data` entry by encoded Unicode age.

## Control Flow
Validation calls `utf8nlen()` in NFDI mode and reports invalid input on negative return. Comparison initializes two cursors and streams normalized bytes until a mismatch, error, or terminator. Casefold/normalize write byte-by-byte into caller buffers and return `-EINVAL` if the destination is too short or input is invalid. Hashing streams NFDICF bytes through the VFS name hash. `utf8_load()` allocates a `unicode_map`, requests `utf8_data_table` dynamically, verifies the requested version, selects NFDI/NFDICF tables, and unwinds symbol references on failure.

## State And Persistence
`unicode_map` is heap state owned by callers. It holds the requested version, the shared generated table symbol, and selected normalization table pointers. No persistent storage is modified.

## Dependencies And Integration Points
The file depends on `utf8-norm.c` cursor routines, generated `utf8_data_table`, Linux module symbol request/put, parser helpers, qstr/stringhash APIs, and filesystems that consume exported Unicode helpers.

## Risks And Test Signals
Risks include exact-version matching in `find_table_version()`, buffer termination semantics, comparing against pre-folded strings without length checks in `utf8_strncasecmp_folded()`, and module reference lifetime. Signals are KUnit normalization tests, filesystem casefold lookup/hash tests, invalid UTF-8 tests, and module unload/load reference checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/unicode/utf8-core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/unicode/utf8-norm.c -->
# sources/distributed-fs/ceph-client/fs/unicode/utf8-norm.c

## Purpose
`utf8-norm.c` implements the runtime trie decoder and normalization cursor used by Unicode-aware filesystems. It validates UTF-8 against generated tables, filters by Unicode version, expands decompositions, performs algorithmic Hangul decomposition, and emits bytes in canonical combining class order.

## Important APIs, Types, And Functions
Public functions are `utf8version_is_supported()`, `utf8nlen()`, `utf8ncursor()`, and `utf8byte()`. Internal helpers include `utf8clen()`, `utf8decode3()`, `utf8encode3()`, `utf8hangul()`, `utf8nlookup()`, and `utf8lookup()`. The packed trie format is described by `BITNUM`, `NEXTBYTE`, `OFFLEN`, `RIGHTPATH`, `TRIENODE`, `RIGHTNODE`, and `LEFTNODE`; leaf interpretation uses `LEAF_GEN`, `LEAF_CCC`, and `LEAF_STR`.

## Control Flow
`utf8nlookup()` walks the generated trie from the selected normalization table offset, consuming input bytes only through valid UTF-8 paths. Hangul leaves are expanded into a small cursor-local synthetic leaf. `utf8nlen()` scans the input and sums either original byte length, decomposition length, or zero for empty decompositions. `utf8ncursor()` initializes bounded cursor state and rejects initial continuation bytes. `utf8byte()` repeatedly scans between stopper characters to emit CCC 0 bytes first, then nonzero combining classes in ascending order.

## State And Persistence
State lives in `struct utf8cursor`: source pointers, decomposition pointers, saved scan positions, remaining length, current/next CCC, and Hangul scratch storage. It reads immutable generated tables from the loaded `unicode_map`.

## Dependencies And Integration Points
It depends on `utf8n.h`, generated `utf8_data_table`, Linux module exports, and `utf8-core.c` callers. Test-only exports are enabled when the KUnit test is a module.

## Risks And Test Signals
Risks include malformed/truncated UTF-8 handling, length underflow around decompositions, combining-class rescan complexity, Hangul synthetic leaf correctness, and behavior for characters newer than the selected Unicode version. Signals are KUnit tests, generator self-tests, invalid/truncated input tests, and filesystem name-lookup equivalence tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/unicode/utf8-norm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/unicode/utf8n.h -->
# sources/distributed-fs/ceph-client/fs/unicode/utf8n.h

## Purpose
`utf8n.h` is the internal header for the Unicode normalization implementation. It declares cursor APIs, table structures, and the generated data table contract shared by `utf8-core.c`, `utf8-norm.c`, generated `utf8data.c`, and KUnit tests.

## Important APIs, Types, And Functions
It declares `utf8version_is_supported()`, `utf8nlen()`, `utf8ncursor()`, and `utf8byte()`. `struct utf8cursor` stores the normalization map, normalization mode, active and saved source/decomposition pointers, bounded lengths, current and next canonical combining class, and Hangul scratch bytes. `struct utf8data` pairs a maximum Unicode age with a trie offset. `struct utf8data_table` points to age tables, NFDICF and NFDI table arrays, their sizes, and the packed trie data. `utf8_data_table` is the exported generated table symbol.

## Control Flow
The header is declarative. Runtime flow is defined by implementations: callers initialize a cursor with `utf8ncursor()`, then repeatedly call `utf8byte()` until it returns 0 or an error.

## State And Persistence
The cursor is caller-owned transient state. `utf8data_table` is immutable generated module data that persists for the life of the Unicode data module.

## Dependencies And Integration Points
It includes Linux types, export, string, module, and unicode headers. It exposes internals needed by `utf8-core.c`, `utf8-norm.c`, generated table code, and `tests/utf8_kunit.c`.

## Risks And Test Signals
Risks include ABI drift between the generator output and `struct utf8data_table`, cursor field assumptions across implementation changes, and normalization enum mismatches. Signals are compile-time type compatibility, successful symbol resolution of `utf8_data_table`, and KUnit/runtime normalization tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/unicode/utf8n.h -->
