# Group Research: group_1682_reactos_sources_windows_reactos_drivers_filesystems_ext2_src_nls_nl_42f8588d3310

Scope confirmed against `Docs/research_subset_a.md`: `sources/windows/reactos` is included. The requested internal group report file was not present, so this report is based on complete reads of every listed source file.

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/src/nls/nls_iso8859-15.c -->
# File Research: sources/windows/reactos/drivers/filesystems/ext2/src/nls/nls_iso8859-15.c

This is a Linux-style NLS module for ISO-8859-15, registering charset name `iso8859-15` with the ReactOS Ext2 driver's Linux compatibility NLS layer.

It defines full byte-to-Unicode, Unicode-page-to-byte, lowercase, and uppercase tables. ISO-8859-15 differs from ISO-8859-1 by adding characters such as the Euro sign, OE ligatures, S/Z caron, and Y diaeresis; these are handled through `page01` and `page20`.

`uni2char` validates `boundlen`, indexes `page_uni2charset` by Unicode high byte, and returns `-EINVAL` for unmapped code points. `char2uni` maps one byte through `charset2uni` and treats Unicode `0x0000` as invalid, so NUL is used as a sentinel rather than a translatable character.

The module lifecycle is only `register_nls(&table)` / `unregister_nls(&table)` through `module_init` and `module_exit`.

Research notes: table-driven and deterministic; main compatibility risk is that zero entries cannot represent valid U+0000 mappings because zero is also the unmapped sentinel.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/src/nls/nls_iso8859-15.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/src/nls/nls_iso8859-2.c -->
# File Research: sources/windows/reactos/drivers/filesystems/ext2/src/nls/nls_iso8859-2.c

This file registers ISO-8859-2 as `iso8859-2`, covering Central and Eastern European Latin characters.

The structure matches the other generated NLS files: `charset2uni[256]`, reverse lookup pages `page00`, `page01`, `page02`, case conversion tables, `uni2char`, `char2uni`, and a static `nls_table`.

The reverse mapping includes Latin Extended-A and modifier-letter entries used by ISO-8859-2. Exact mappings only are accepted; missing or ambiguous Unicode input returns `-EINVAL`.

Case folding is byte-table based, not Unicode algorithm based. It maps charset bytes to their single-byte lower/upper equivalents and leaves unsupported cases unchanged.

Research notes: no dynamic state and no filesystem-specific logic; correctness depends entirely on the static tables matching the intended code page.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/src/nls/nls_iso8859-2.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/src/nls/nls_iso8859-3.c -->
# File Research: sources/windows/reactos/drivers/filesystems/ext2/src/nls/nls_iso8859-3.c

This is the ISO-8859-3 NLS table module registered as `iso8859-3`, supporting Latin-3/South European mappings.

Several positions in `charset2uni` intentionally map to `0x0000`, representing undefined ISO-8859-3 byte slots. Those bytes are rejected by `char2uni`.

Reverse lookup uses `page00`, `page01`, and `page02`, with sparse entries for Latin Extended and modifier characters. Entries set to zero are treated as unmappable.

Lowercase and uppercase tables include ISO-8859-3-specific pairs, including dotted/dotless I handling by byte value rather than locale-aware Unicode behavior.

Research notes: this is a generated compatibility table; it performs no validation beyond buffer length and table presence.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/src/nls/nls_iso8859-3.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/src/nls/nls_iso8859-4.c -->
# File Research: sources/windows/reactos/drivers/filesystems/ext2/src/nls/nls_iso8859-4.c

This file implements the ISO-8859-4 NLS table registered as `iso8859-4`, covering Baltic/Nordic Latin mappings.

The byte-to-Unicode table maps ISO-8859-4-specific characters such as A/E/I/O/U macron, ogonek, cedilla, and Baltic letters into Unicode. Reverse lookup is provided through `page00`, `page01`, and `page02`.

`uni2char` is exact-only and rejects unmapped Unicode. `char2uni` rejects bytes whose table entry is zero, including NUL and undefined character positions.

The case conversion tables encode single-byte upper/lower mappings for the charset and are used through `nls_table.charset2lower` and `charset2upper`.

Research notes: no runtime allocation or state; behavior is stable and table-driven.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/src/nls/nls_iso8859-4.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/src/nls/nls_iso8859-5.c -->
# File Research: sources/windows/reactos/drivers/filesystems/ext2/src/nls/nls_iso8859-5.c

This module registers ISO-8859-5 as `iso8859-5`, providing Cyrillic charset conversion.

`charset2uni` maps the upper half of the byte range to Cyrillic U+0400/U+0410/U+0430 ranges plus symbols such as numero sign. Reverse mapping uses `page00`, `page04`, and `page21`.

The lower/upper tables encode Cyrillic case conversion in charset-byte space, including uppercase Cyrillic letters at `0xb0`-style positions and lowercase counterparts at `0xd0`/`0xe0`.

`uni2char` checks `boundlen <= 0`, then maps through page tables. `char2uni` rejects `0x0000` table results.

Research notes: table-driven; no special handling for locale-specific Cyrillic case behavior beyond the static ISO-8859-5 table.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/src/nls/nls_iso8859-5.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/src/nls/nls_iso8859-6.c -->
# File Research: sources/windows/reactos/drivers/filesystems/ext2/src/nls/nls_iso8859-6.c

This is the ISO-8859-6 Arabic NLS module registered as `iso8859-6`.

`charset2uni` contains Arabic punctuation and Arabic letters in the U+0600 range. Notably, byte values `0x30`-`0x39` map to Arabic-Indic digits U+0660-U+0669 in this table, while reverse `page06` maps those Unicode digits back to ASCII digit byte positions.

Many byte positions in the upper half are undefined and represented as zero, causing `char2uni` to reject them.

Case conversion tables are effectively identity or sparse because Arabic has no upper/lowercase transformation in this charset.

Research notes: the digit mapping is a notable behavioral detail for callers expecting ASCII `0`-`9` to round-trip as U+0030-U+0039.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/src/nls/nls_iso8859-6.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/src/nls/nls_iso8859-7.c -->
# File Research: sources/windows/reactos/drivers/filesystems/ext2/src/nls/nls_iso8859-7.c

This module registers ISO-8859-7 Greek as `iso8859-7`.

The byte-to-Unicode table maps Greek tonos, uppercase/lowercase Greek letters, final sigma, diaeresis variants, and selected punctuation. Reverse lookup uses `page00`, `page02`, `page03`, and `page20`.

Case tables include Greek-specific byte mappings, including uppercase/lowercase Greek letters and accented variants where representable in the charset.

The conversion functions are the same exact-table pattern as the other NLS modules: one output byte per accepted Unicode character, one Unicode character per input byte, and `-EINVAL` for unmapped/sentinel entries.

Research notes: static table implementation with no filesystem-specific control flow; undefined code points are rejected rather than substituted.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/src/nls/nls_iso8859-7.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/src/nls/nls_iso8859-9.c -->
# File Research: sources/windows/reactos/drivers/filesystems/ext2/src/nls/nls_iso8859-9.c

This file registers ISO-8859-9 as `iso8859-9`, the Turkish Latin-5 charset.

The mapping is mostly ISO-8859-1-like, with Turkish-specific entries for G-breve, dotted capital I, dotless small i, and S-cedilla. Reverse lookup uses `page00` and `page01`.

Case conversion tables include Turkish byte mappings, including `0xdd` to `0x69` and `0xfd` to `0x49` behavior for dotted/dotless I in this table's byte-level casing.

As with the other NLS modules, `uni2char` only emits exact one-byte mappings and `char2uni` rejects zero/sentinel mappings.

Research notes: callers relying on language-neutral case folding should be aware this table embeds charset-specific Turkish casing behavior.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/src/nls/nls_iso8859-9.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/src/nls/nls_koi8-r.c -->
# File Research: sources/windows/reactos/drivers/filesystems/ext2/src/nls/nls_koi8-r.c

This module registers KOI8-R as `koi8-r`, supporting Russian Cyrillic plus box-drawing symbols.

`charset2uni` maps `0x80`-`0xbf` heavily to line/box drawing and symbols, and `0xc0`-`0xff` to Russian Cyrillic in KOI8-R order. Reverse lookup uses pages `00`, `04`, `22`, `23`, and `25`.

Case conversion tables map KOI8-R Cyrillic lowercase and uppercase bytes while preserving line drawing and symbol bytes.

The public behavior is the standard NLS exact mapping API: `uni2char`, `char2uni`, lower/upper byte tables, and module registration.

Research notes: no locking or mutable state; useful as a base table for related KOI8 variants.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/src/nls/nls_koi8-r.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/src/nls/nls_koi8-ru.c -->
# File Research: sources/windows/reactos/drivers/filesystems/ext2/src/nls/nls_koi8-ru.c

This is a small wrapper module for `koi8-ru`, implemented by loading the `koi8-u` NLS table at init time and overriding the few mappings where KOI8-RU differs.

`init_nls_koi8_ru` calls `load_nls("koi8-u")`, copies the base table's case-conversion pointers, and registers a new table named `koi8-ru`. Exit unregisters the wrapper and unloads the base table.

`uni2char` special-cases U+040E/U+045E and selected box-drawing differences, otherwise delegates to `p_nls->uni2char`.

Research note: the `char2uni` branch condition appears inconsistent with the comment. It maps bytes when `((*rawstring & 0xef) != 0xae)`, which means most input bytes bypass the base table and become U+040E/U+045E. Given the comment that KOI8-RU and KOI8-U differ only on two characters, this looks like a likely inverted condition and a high-risk bug.

Dependency risk: if `koi8-u` is unavailable, registration fails with `-EINVAL`.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/src/nls/nls_koi8-ru.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/src/nls/nls_koi8-u.c -->
# File Research: sources/windows/reactos/drivers/filesystems/ext2/src/nls/nls_koi8-u.c

This module registers KOI8-U as `koi8-u`, supporting Ukrainian Cyrillic additions over KOI8-R.

The table includes KOI8 line-drawing symbols and Cyrillic mappings, plus Ukrainian characters such as IE, I, YI, and GHE with upturn. Reverse lookup uses the same broad pages as KOI8-R with additional U+0490/U+0491 coverage.

Case conversion tables account for the Ukrainian additions and standard Cyrillic byte-pair casing.

It exposes the standard NLS callbacks and is also a runtime dependency for `nls_koi8-ru.c`.

Research notes: static exact mapping table; no dynamic behavior after registration.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/src/nls/nls_koi8-u.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/src/nls/nls_utf8.c -->
# File Research: sources/windows/reactos/drivers/filesystems/ext2/src/nls/nls_utf8.c

This module registers UTF-8 as an NLS charset named `utf8`.

Unlike the single-byte table files, `uni2char` delegates to `utf8_wctomb` and `char2uni` delegates to `utf8_mbtowc`. Failed encoding writes `?` to the output byte and returns `-EINVAL`; failed decoding sets the Unicode output to U+003F and returns `-EINVAL`.

`identity[256]` is initialized at module load and used for both lower and upper case conversion, meaning UTF-8 NLS performs no case mapping at the byte-table layer.

Research notes: this module depends on the shared UTF-8 helper functions in the NLS layer and treats UTF-8 as variable-length only in conversion callbacks, not in case folding.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/src/nls/nls_utf8.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/src/pnp.c -->
# File Research: sources/windows/reactos/drivers/filesystems/ext2/src/pnp.c

This file handles Ext2 filesystem Plug and Play IRPs for Windows 2000+ builds.

`Ext2Pnp` validates the IRP context and VCB, forces wait behavior, dispatches minor functions, and forwards unhandled PnP IRPs to the lower storage device. Handled paths usually consume the IRP and set `IrpContext->Irp = NULL`.

`Ext2PnpQueryRemove` waits for lazy writer activity, flushes files and volume state, locks the VCB, purges cached volume state, sends the query down synchronously with a completion event, and calls `Ext2CheckDismount` on success.

`Ext2PnpRemove` and `Ext2PnpSurpriseRemove` lock the VCB, forward the IRP, purge volume cache, check dismount, and set `VCB_DEVICE_REMOVED`. `Ext2PnpCancelRemove` unlocks the VCB and forwards the cancel-remove IRP.

Research notes: PnP forwarding depends on careful ownership of `IrpContext->Irp`. Error paths after failed VCB validation still rely on `Vcb->TargetDeviceObject` in the final forwarding path, so corrupted/non-VCB device extensions are risky.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/src/pnp.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/src/rbtree.c -->
# File Research: sources/windows/reactos/drivers/filesystems/ext2/src/rbtree.c

This is a Linux red-black tree implementation ported into the ReactOS Ext2 source tree.

It provides rotation helpers, insertion rebalancing, erase rebalancing, ordered traversal (`rb_first`, `rb_last`, `rb_next`, `rb_prev`), replacement, and a convenience `rb_insert` that accepts a caller-provided comparator.

The tree stores parent and color through the Linux `rb_parent_color` convention and exports the main functions with `EXPORT_SYMBOL`.

`rb_insert` ignores duplicate keys by returning without inserting when the comparator returns zero. No memory allocation, key ownership, or synchronization is handled here.

Research notes: correctness depends on callers maintaining valid `rb_node` links and external locking. Erase balancing follows the classic Linux algorithm and assumes tree invariants; corrupted trees can lead to null sibling dereferences.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/src/rbtree.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/src/read.c -->
# File Research: sources/windows/reactos/drivers/filesystems/ext2/src/read.c

This file implements Ext2 read dispatch for volume objects, regular files, inode extent reads, and MDL read completion.

`Ext2ReadVolume` handles raw volume reads. Cached reads use `CcMdlRead` or `CcCopyRead` against `Vcb->Volume`; noncached reads align length to sector size, lock the user buffer, create a single `EXT2_EXTENT`, and call `Ext2ReadWriteBlocks`.

`Ext2ReadInode` is the lower-level inode read helper. It handles fast symlink data stored inside the inode, builds extent chains with `Ext2BuildExtents`, zero-fills sparse gaps, then either dispatches direct I/O through `Ext2ReadWriteBlocks` or uses `CcCopyRead` from the volume stream.

`Ext2ReadFile` validates file state, lock state, byte ranges, oplocks, cache maps, EOF/VDL behavior, and resource acquisition. Cached reads use Cache Manager APIs; noncached reads lock buffers and call `Ext2ReadInode`.

`Ext2ReadComplete` finalizes MDL reads with `CcMdlReadComplete`. `Ext2Read` is the top-level dispatcher choosing completion, volume read, or FCB read.

Research notes: direct file read buffer locking uses `IoReadAccess` before filling the caller buffer, while volume direct reads use `IoWriteAccess`; this difference is worth verifying against the driver's `Ext2LockUserBuffer` semantics.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/src/read.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/src/shutdown.c -->
# File Research: sources/windows/reactos/drivers/filesystems/ext2/src/shutdown.c

This file implements filesystem shutdown handling through `Ext2ShutDown`.

The function acquires the global Ext2 resource exclusively, iterates `Ext2Global->VcbList`, acquires each mounted VCB's main resource, updates and caps the superblock mount count, saves the superblock, flushes dirty file caches, flushes the volume stream, and sends shutdown to the underlying disk.

If the global resource cannot be acquired with the IRP context wait policy, it returns `STATUS_PENDING` and queues the request.

Failures during flush call `DbgBreak` except media write-protection on volume flush. Completion and cleanup are centralized in the SEH finally block.

Research notes: this is a global coordination path with strong locking; it assumes the VCB list remains stable under `Ext2Global->Resource`.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/src/shutdown.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/src/volinfo.c -->
# File Research: sources/windows/reactos/drivers/filesystems/ext2/src/volinfo.c

This file implements Ext2 volume information query and set IRPs.

`Ext2QueryVolumeInformation` rejects the filesystem control device, validates the mounted VCB, acquires `MainResource` shared, zeroes the caller buffer, and handles `FileFsVolumeInformation`, `FileFsSizeInformation`, `FileFsDeviceInformation`, `FileFsAttributeInformation`, and Windows 2000+ `FileFsFullSizeInformation`.

Size information reports total/free allocation units from ext superblock counters, sectors per allocation unit from block size and disk geometry, and bytes per sector from disk geometry. Attribute information reports hard links, case sensitivity, preserved names, reparse points, extended attributes, read-only state, component name length, and filesystem name `EXT2`, `EXT3`, or `EXT4`.

`Ext2SetVolumeInformation` supports `FileFsLabelInformation`, rejects read-only volumes, limits labels to 16 WCHARs, copies the label to the VPB, converts it to OEM into `s_volume_name`, and saves the superblock.

Research note: `FileFsAttributeInformation` sets `FileSystemNameLength = 8` but copies `L"EXT4\0"`/`EXT3`/`EXT2` with 10 bytes, which appears to over-copy by one WCHAR relative to the advertised required length.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/src/volinfo.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/src/write.c -->
# File Research: sources/windows/reactos/drivers/filesystems/ext2/src/write.c

This file implements Ext2 write dispatch for volumes, files, inode extents, MDL completion, deferred Cache Manager writes, and floppy delayed flushes.

`Ext2WriteVolume` handles raw volume writes. Cached writes use `CcPrepareMdlWrite` or `CcCopyWrite`; noncached writes lock caller buffers and write extents directly. Paging writes consult VCB dirty extent tracking to write only tracked dirty ranges and remove them after success.

`Ext2WriteInode` builds extent chains with allocation enabled for non-directory writes, then either dispatches direct block I/O through `Ext2ReadWriteBlocks` or writes buffered data with `Ext2SaveBuffer`.

`Ext2WriteFile` is the main file write path. It validates file type, deletion state, access, byte alignment, locks, oplocks, cacheability, paging I/O, and recursive write-through. It expands allocation and file size when needed, updates inode size, enables the ext large-file feature if required, zeroes gaps before writes beyond valid data length, updates VDL, reports notify changes, and marks file/FCB modified.

`Ext2WriteComplete` completes MDL writes with `CcMdlWriteComplete`. `Ext2Write` rejects writes to the filesystem device, read-only volumes, locked volumes by non-lock owners, and dismount-pending FCB writes before dispatching to volume or file write handlers.

Research notes: the file-size growth path uses a temporary `MajorFunction += IRP_MJ_MAXIMUM_FUNCTION` protocol to influence `Ext2ExpandFile`, which is fragile but intentionally reverted in the finally block. Several error paths call `DbgBreak`, so checked builds may break on operational failures.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/src/write.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/fastfat/CMakeLists.txt -->
# File Research: sources/windows/reactos/drivers/filesystems/fastfat/CMakeLists.txt

This CMake file defines the ReactOS `fastfat` filesystem driver build target.

It appends the FAT driver source list, including create/read/write, cache support, directory support, volume info, PnP, shutdown, locking, verification, work queue, and `fatprocs.h`.

It builds `fastfat` as a module with `fastfat.rc`, marks it as a `kernelmodedriver`, links `${PSEH_LIB}` and `memcmp`, imports `ntoskrnl` and `hal`, configures `fatprocs.h` as the precompiled header, and installs the driver to `reactos/system32/drivers`.

Research notes: this file contains build orchestration only; it has no runtime filesystem logic but controls which source files participate in the fastfat driver.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/fastfat/CMakeLists.txt -->