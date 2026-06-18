# Group Research: group_1680_reactos_sources_windows_reactos_drivers_filesystems_ext2_src_memory_5cb6449e503c

Scope checked against `Docs/research_subset_a.md`: `sources/windows/reactos` is included in subset A. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/src/memory.c -->
# File Research: sources/windows/reactos/drivers/filesystems/ext2/src/memory.c

Core lifetime and memory-management implementation for the ReactOS-imported Ext2Fsd driver. It allocates, initializes, links, unlinks, reclaims, and destroys the driver’s main runtime objects: IRP contexts, FCBs, CCBs, inodes, Linux-style dentries, extent-chain nodes, MCB pathname/tree entries, and VCB volume state.

The early object-allocation paths are mostly lookaside-list wrappers with driver-specific initialization. `Ext2AllocateIrpContext` captures IRP stack state, major/minor codes, file/Fcb/Ccb pointers, real device, wait policy, top-level IRP state, and write-through/verify flags. FCB allocation initializes oplocks, file locks, `FSRTL_COMMON_FCB_HEADER`, file size/allocation size, section objects, resources, and inserts the FCB into the VCB list. CCBs optionally hold and reference symlink MCBs. MCB allocation builds short/full names, initializes `LargeMcb` maps, sets hidden attributes for dot-prefixed files, and stores ext2 inode/private links.

The file owns two levels of cached block mapping. VCB extent routines map raw volume offsets to `FsRtlLargeMcb` runs aligned to `IoUnitSize`, while MCB extent routines map file block offsets to disk block offsets using block-sized units. Higher-level helpers add, remove, and look up block extents, initialize an MCB zone by walking extent/indirect mappings, and build chained I/O extents for reads/writes. `Ext2BuildExtents` uses the MCB zone cache when possible, falls back to `Ext2BlockMap` for allocation or cache misses, coalesces adjacent physical ranges, and skips sparse blocks unless allocation was requested.

MCB tree management is another major responsibility. `Ext2SearchMcbWithoutLock` handles `.`, `..`, symlink targets, and case-insensitive child lookup. `Ext2InsertMcb` attaches children under a parent or symlink target and references the parent. `Ext2RemoveMcb`, `Ext2LinkTailMcb`, `Ext2LinkHeadMcb`, `Ext2UnlinkMcb`, and `Ext2FirstUnusedMcb` maintain both the directory tree and the reclaim queue, with special handling for root, deleted files, special files, symlinks, child pointers, and reference counts.

Mount initialization is concentrated in `Ext2InitializeVcb`. It validates feature flags and block size, sets read-only policy for unsupported `ro_compat` features, identifies ext3 journals, initializes resources/lists/notify state, binds VPB/device/stream-file state, initializes cache manager state, creates the Linux-style block device and buffer-head cache, fills `super_block`/`ext3_sb_info` fields, validates descriptor and inode geometry, computes maximum file/block limits, loads group descriptors, optionally recovers the journal, builds the root MCB/dentry/inode, checks metadata bitmap consistency when configured, references the target device, and applies per-volume registry settings. Its failure cleanup unwinds lookaside lists, group descriptors, cache maps, stream objects, notify state, and resources.

The file also includes metadata integrity and configuration helpers. `Ext2CheckSetBlock` and `Ext2CheckBitmapConsistency` verify and repair allocation bitmap bits for group block bitmaps, inode bitmaps, and inode tables. `Ext2QueryVolumeParams`, `Ext2ParseRegistryVolumeParams`, and `Ext2PerformRegistryVolumeParams` read per-volume registry settings keyed by UUID and apply readonly/write support, ext3 write forcing, bitmap checking, codepage, hidden prefix/suffix, mount point, and UID/GID options. ReactOS-specific conditionals fix assignment-vs-comparison bugs in hiding-prefix/suffix checks.

Shutdown and reclamation paths tear down cache maps, stream objects, VCB resources, MCBs, buffer heads, FCBs, VPBs, and device objects. Three reaper threads reclaim unused MCBs, buffer heads, and FCBs according to global pressure, object age, reference counts, and stop events. `Ext2StartReaper` and `Ext2StopReaper` wrap system-thread creation, startup synchronization, and shutdown signaling.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/src/memory.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/src/misc.c -->
# File Research: sources/windows/reactos/drivers/filesystems/ext2/src/misc.c

General utility code for the Ext2Fsd driver. It provides small arithmetic/time helpers, filename character-set conversion wrappers, sleep, Windows-to-Linux error translation, Linux-to-Windows status translation, and dot/dotdot name checks.

`Ext2Log2` returns the zero-based order of a positive value by shifting until zero. `Ext2NtTime` converts Unix seconds-since-1970 to NT time, while `Ext2LinuxTime` converts an NT `LARGE_INTEGER` back to Unix seconds and falls back to the current system time if conversion fails.

The filename conversion helpers bridge the driver’s optional Linux NLS tables with Windows RTL OEM conversion. `Ext2MbsToUnicode` and `Ext2UnicodeToMbs` first count output length by calling a selected `nls_table`’s `char2uni` or `uni2char`, then optionally fill the caller’s buffer after checking capacity. `Ext2OEMToUnicodeSize`, `Ext2OEMToUnicode`, `Ext2UnicodeToOEMSize`, and `Ext2UnicodeToOEM` prefer the configured VCB codepage table, then fall back to `RtlOemStringToCountedUnicodeSize`, `RtlOemStringToUnicodeString`, `RtlxUnicodeStringToOemSize`, or `RtlUnicodeStringToOemString`.

`Ext2Sleep` delays the current kernel thread for the requested milliseconds. `Ext2LinuxError` maps many `NTSTATUS` values to negative Linux `errno` values used by the Linux-derived ext2/ext3 code. `Ext2WinntError` maps common negative Linux errors back to Windows status codes. `Ext2IsDot` and `Ext2IsDotDot` recognize Unicode `"."` and `".."` directory names by exact byte length and character contents.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/src/misc.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/src/nls.c -->
# File Research: sources/windows/reactos/drivers/filesystems/ext2/src/nls.c

Driver-level NLS module loader/unloader. It declares init/exit entry points for many Linux-style `nls_table` modules and loads them into the global table registry used by filename conversion.

`Ext2LoadAllNls` clears the global `tables` list, initializes `nls_lock`, always loads UTF-8, then under `FULL_CODEPAGES_SUPPORT` loads Chinese GB2312/Big5 and a broad set of single-byte codepages: ASCII, Windows CP1250/1251/1255, DOS CP437/737/775/850/852/855/857/860/861/862/863/864/865/866/869/874/932/949, EUC-JP, ISO-8859 variants, and KOI8 variants. The code relies on `LOAD_NLS` macros to call each module’s initializer and track return state.

`Ext2UnloadAllNls` unloads the same built-in NLS modules in roughly reverse/dependency-safe order, ending with UTF-8. The file is glue code: actual registration logic is in `nls_base.c`, while conversion tables live in the individual `nls_*` files. One notable quirk is that the unload list uses `UNLOAD_NLS(init_nls_ascii)` and `UNLOAD_NLS(init_nls_cp1250)` for the first two entries while the remaining entries use `exit_nls_*` names.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/src/nls.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/src/nls/nls_ascii.c -->
# File Research: sources/windows/reactos/drivers/filesystems/ext2/src/nls/nls_ascii.c

Linux-derived ASCII NLS table module. It defines exact byte-to-Unicode mappings for the 7-bit ASCII range, reverse Unicode-to-byte page table for Unicode page `0x00`, and case-folding tables for ASCII uppercase/lowercase conversion.

`uni2char` accepts Unicode code points whose high byte indexes a populated page table and whose low byte maps to a nonzero byte; otherwise it returns `-EINVAL`, or `-ENAMETOOLONG` when no output space is available. `char2uni` maps one input byte through `charset2uni` and rejects NUL/zero mappings as invalid.

The exported `nls_table` is named `"ascii"` with no alias. Its init routine registers the table with `register_nls`, and its exit routine unregisters it. The module uses Linux `module_init`, `module_exit`, and dual BSD/GPL license declarations, as adapted for this driver’s Linux-compatibility layer.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/src/nls/nls_ascii.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/src/nls/nls_base.c -->
# File Research: sources/windows/reactos/drivers/filesystems/ext2/src/nls/nls_base.c

Shared Linux NLS support layer embedded in the Ext2Fsd driver. It provides the global `struct nls_table *tables` registry, `nls_lock`, UTF-8 conversion helpers, NLS table registration and lookup, and exported symbols consumed by individual codepage modules and driver filename conversion code.

The UTF-8 section uses a table-driven decoder/encoder for one- through six-byte sequences. `utf8_mbtowc` validates continuation bytes and overlong ranges, `utf8_mbstowcs` converts a byte string to wide characters while skipping invalid bytes, `utf8_wctomb` emits the shortest matching UTF-8 sequence within `maxlen`, and `utf8_wcstombs` converts wide strings to UTF-8 while skipping unencodable characters.

`register_nls` and `unregister_nls` maintain the global linked list under `spin_lock`, reject null, duplicate, busy, or missing tables, and update each table’s `next` pointer. `find_nls` matches by charset or alias and uses `try_module_get`; `load_nls` first checks built-ins and can request a module when `CONFIG_KMOD` is enabled; `unload_nls` releases the module owner.

The second half defines a simple identity-like single-byte default mapping table, including byte-to-Unicode, reverse page `0x00`, and ASCII case folding. The default-table loader is disabled under `#if 0 // Masked by Matt`, but export declarations still include `load_nls_default`. This file is the central contract used by the codepage modules listed in this group.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/src/nls/nls_base.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/src/nls/nls_cp1250.c -->
# File Research: sources/windows/reactos/drivers/filesystems/ext2/src/nls/nls_cp1250.c

Generated Linux NLS module for Windows codepage CP1250, covering Central European Latin characters. It defines a 256-entry `charset2uni` table, reverse Unicode-to-codepage tables for Unicode pages `00`, `01`, `02`, `20`, and `21`, plus CP1250-specific lowercase and uppercase byte maps.

The conversion functions follow the common single-byte NLS pattern used throughout this directory. `uni2char` indexes `page_uni2charset` by Unicode high byte and rejects unmapped entries or insufficient output space. `char2uni` maps one byte to Unicode and rejects zero mappings. Case tables preserve ASCII folding and add CP1250-specific folding for accented Central European letters.

The module registers an `nls_table` with charset `"cp1250"` and no alias. `init_nls_cp1250` calls `register_nls`, `exit_nls_cp1250` calls `unregister_nls`, and the file declares Linux-style module init/exit and dual BSD/GPL licensing.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/src/nls/nls_cp1250.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/src/nls/nls_cp1251.c -->
# File Research: sources/windows/reactos/drivers/filesystems/ext2/src/nls/nls_cp1251.c

Generated Linux NLS module for Windows codepage CP1251, primarily Cyrillic. Its `charset2uni` table maps CP1251 bytes to Unicode Cyrillic, punctuation, currency, and Latin/control code points. Reverse mappings are provided for Unicode pages `00`, `04`, `20`, and `21`, with byte case-folding tables for Cyrillic upper/lower pairs and ASCII.

`uni2char` and `char2uni` are the standard single-byte implementations used by these NLS modules: they perform exact mapping only, return `-ENAMETOOLONG` for no output space, return `-EINVAL` for unmapped characters, and consume or emit one byte per successful character.

The module’s `nls_table` is named `"cp1251"` with no alias. Init and exit functions register and unregister the table through the shared NLS registry, and the file uses Linux module metadata declarations.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/src/nls/nls_cp1251.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/src/nls/nls_cp1255.c -->
# File Research: sources/windows/reactos/drivers/filesystems/ext2/src/nls/nls_cp1255.c

Generated Linux NLS module for Windows codepage CP1255, Hebrew. The byte-to-Unicode table covers ASCII/control bytes, Windows punctuation, shekel sign, Hebrew vowel marks, punctuation, Hebrew letters, and selected undefined byte slots. Reverse Unicode mapping pages are `00`, `01`, `02`, `05`, `20`, and `21`.

The file uses the shared single-byte NLS conversion structure. `uni2char` looks up an exact reverse mapping from `page_uni2charset`; `char2uni` maps the input byte through `charset2uni`; both reject zero/unmapped values. The case tables mostly leave Hebrew bytes unchanged while preserving ASCII case conversion and the mappings present in the generated table.

The module registers charset `"cp1255"` and alias `"iso8859-8"`, and it declares `MODULE_ALIAS_NLS(iso8859-8)`. Init and exit functions register/unregister the table with the NLS base layer.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/src/nls/nls_cp1255.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/src/nls/nls_cp437.c -->
# File Research: sources/windows/reactos/drivers/filesystems/ext2/src/nls/nls_cp437.c

Generated Linux NLS module for DOS codepage CP437. It maps bytes to Unicode for ASCII, Western European accented letters, box-drawing characters, block elements, Greek/math symbols, and other original IBM PC glyphs. Reverse Unicode maps are provided for pages `00`, `01`, `03`, `20`, `22`, `23`, and `25`.

The conversion routines implement exact one-byte mapping only. `uni2char` uses the Unicode high byte to choose a reverse page table and the low byte to select a codepage byte; `char2uni` returns the corresponding wide character from `charset2uni`. Both use `-EINVAL` for missing mappings and `uni2char` also checks output length.

The table is registered under charset `"cp437"` with no alias. The lower/upper tables include ASCII folding and generated folding for CP437 accented Latin entries where a byte-level uppercase/lowercase counterpart exists.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/src/nls/nls_cp437.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/src/nls/nls_cp737.c -->
# File Research: sources/windows/reactos/drivers/filesystems/ext2/src/nls/nls_cp737.c

Generated Linux NLS module for DOS codepage CP737, a Greek codepage. Its byte-to-Unicode table maps ASCII/control bytes, Greek uppercase and lowercase letters, accented Greek letters, box-drawing/block glyphs, and selected math symbols. Reverse Unicode maps are present for pages `00`, `03`, `20`, `22`, and `25`.

`uni2char` and `char2uni` are the standard exact single-byte routines used by the surrounding NLS files. The case-folding tables include ASCII folding plus Greek byte-pair folding for the codepage’s uppercase/lowercase Greek range, while leaving drawing and symbol bytes stable.

The module registers charset `"cp737"` with no alias. `init_nls_cp737` and `exit_nls_cp737` connect it to the shared NLS registry, with Linux-style module declarations and dual BSD/GPL license metadata.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/src/nls/nls_cp737.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/src/nls/nls_cp775.c -->
# File Research: sources/windows/reactos/drivers/filesystems/ext2/src/nls/nls_cp775.c

Generated Linux NLS module for DOS codepage CP775, used for Baltic languages. The 256-entry forward table maps ASCII/control bytes, Baltic Latin letters, Western accented letters, punctuation, box-drawing/block characters, and symbols. Reverse mapping pages are `00`, `01`, `20`, `22`, and `25`.

The module follows the common NLS pattern: exact Unicode-to-byte lookup through `page_uni2charset`, exact byte-to-Unicode lookup through `charset2uni`, `-ENAMETOOLONG` on no output space, and `-EINVAL` on unmapped characters. Generated case tables encode ASCII and CP775-specific uppercase/lowercase byte equivalents.

The `nls_table` charset is `"cp775"` with no alias. Init and exit functions register and unregister the table through the shared NLS base code.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/src/nls/nls_cp775.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/src/nls/nls_cp850.c -->
# File Research: sources/windows/reactos/drivers/filesystems/ext2/src/nls/nls_cp850.c

Generated Linux NLS module for DOS codepage CP850, the multilingual Latin-1 DOS codepage. The forward table maps ASCII/control bytes, Western European accented letters, box-drawing characters, block glyphs, fractions, currency symbols, and punctuation. Reverse Unicode maps are supplied for pages `00`, `01`, `20`, and `25`.

Conversion is exact and single-byte. `uni2char` fails for unmapped Unicode values or zero output capacity, while `char2uni` maps one raw byte and rejects zero mappings. Lowercase and uppercase tables provide byte-level folding for ASCII and supported CP850 Latin pairs.

The file registers charset `"cp850"` with no alias via `init_nls_cp850` and unregisters via `exit_nls_cp850`. Like the other generated NLS modules, it depends on `nls_base.c` for registry and module-reference behavior.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/src/nls/nls_cp850.c -->