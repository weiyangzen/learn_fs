# Group Research: group_1670_reactos_sources_windows_reactos_drivers_filesystems_btrfs_zstd_zstd_98c580e8958c

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/btrfs/zstd/zstd_fast.c -->
# File Research: sources/windows/reactos/drivers/filesystems/btrfs/zstd/zstd_fast.c

## Scope And Purpose

`zstd_fast.c` implements Zstd's fast block parser for the ReactOS Btrfs bundled Zstd library. It maintains hash tables, finds short prefix/dictionary matches, emits sequences into `seqStore_t`, and updates repeated offsets for later blocks.

Complete file read: 496 lines.

## Main Components

- `ZSTD_fillHashTable` preloads the match-state hash table from `ms->nextToUpdate` to an end pointer, either sparsely for fast dictionary-table load or more fully when requested.
- `ZSTD_compressBlock_fast_generic` is the core no-dictionary fast parser. It checks two adjacent candidates per loop, handles immediate repcode matches, stores regular match sequences, and skips faster through incompressible input.
- `ZSTD_compressBlock_fast` dispatches the generic parser by `minMatch` length.
- `ZSTD_compressBlock_fast_dictMatchState_generic` adds lookup against an attached dictionary match state and bridges matches spanning dictionary and prefix memory.
- `ZSTD_compressBlock_fast_dictMatchState` dispatches the dictionary-match-state variant by `minMatch`.
- `ZSTD_compressBlock_fast_extDict_generic` handles external dictionary windows through two-segment match counting and falls back to the normal fast parser if the external dictionary has been invalidated.
- `ZSTD_compressBlock_fast_extDict` dispatches the external-dictionary variant by `minMatch`.

## Integration Points

This file is selected by `ZSTD_selectBlockCompressor()` in `zstd_compress.c` for `ZSTD_fast` strategy and its dictionary modes. It depends on `ZSTD_matchState_t`, `ZSTD_hashPtr`, `ZSTD_count`, `ZSTD_count_2segments`, `ZSTD_storeSeq`, repeated-offset constants, and window helpers from `zstd_compress_internal.h`.

## Notes

- Match search is intentionally shallow and biased toward speed.
- Repcode invalidation is handled by zeroing offsets outside the valid prefix window.
- Dictionary handling is pointer-arithmetic heavy; correctness depends on `dictLimit`, `lowLimit`, `dictIndexDelta`, and prefix/dictionary boundaries being maintained by the caller.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/btrfs/zstd/zstd_fast.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/btrfs/zstd/zstd_fast.h -->
# File Research: sources/windows/reactos/drivers/filesystems/btrfs/zstd/zstd_fast.h

## Scope And Purpose

`zstd_fast.h` declares the fast Zstd block-compression strategy entry points used by the shared compressor dispatcher.

Complete file read: 37 lines.

## Public Interface

- `ZSTD_fillHashTable` fills a `ZSTD_matchState_t` hash table up to a supplied end pointer using a selected dictionary-table load method.
- `ZSTD_compressBlock_fast` compresses one block with the fast parser and no attached dictionary match state.
- `ZSTD_compressBlock_fast_dictMatchState` compresses with a separate dictionary match state.
- `ZSTD_compressBlock_fast_extDict` compresses with an external dictionary window.

## Integration Points

The header includes `mem.h` for fixed-width Zstd types and `zstd_compress_internal.h` for match-state, sequence-store, repcode, and dictionary-mode definitions. It uses `extern "C"` guards for C++ compatibility.

## Notes

This header is purely declarative and has no local logic. Its declarations are consumed by `zstd_compress.c`, `zstd_ldm.c`, and other strategy-selection code.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/btrfs/zstd/zstd_fast.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/btrfs/zstd/zstd_internal.h -->
# File Research: sources/windows/reactos/drivers/filesystems/btrfs/zstd/zstd_internal.h

## Scope And Purpose

`zstd_internal.h` is the shared internal contract for Zstd compression, decompression, and dictionary-building code. It defines constants, error-return macros, entropy defaults, sequence storage structures, block metadata, hot copy helpers, and internal declarations that must stay consistent across modules.

Complete file read: 447 lines.

## Main Components

- Dependency setup enables static-linking-only APIs for Zstd, FSE, HUF, and xxhash internals.
- Error helpers `RETURN_ERROR_IF`, `RETURN_ERROR`, and `FORWARD_IF_ERROR` return encoded Zstd errors and add debug logging when enabled.
- Shared constants define frame/block header sizes, repcode counts, minimum match length, literal/match/offset symbol limits, FSE log limits, and default normalized distributions.
- `ZSTD_copy8`, `ZSTD_copy16`, `COPY8`, `COPY16`, and `ZSTD_wildcopy` provide optimized copy primitives that may intentionally over-read/write within documented overlength bounds.
- `ZSTD_limitCopy` copies up to destination capacity.
- `seqDef`, `seqStore_t`, and `ZSTD_sequenceLength` define the internal sequence stream emitted by match finders.
- `ZSTD_getSequenceLength` expands long literal or match lengths tracked out of band.
- `ZSTD_frameSizeInfo` and `blockProperties_t` describe compressed/decompressed frame and block metadata.
- Internal declarations expose sequence-store access, sequence-code conversion, custom memory allocation, repcode invalidation, compressed-block size parsing, and sequence-header decoding.
- `ZSTD_highbit32` provides compiler-specific or fallback high-bit calculation used throughout compression cost and offset coding.

## Integration Points

This header is included by the Zstd compression and decompression implementation files. Its constants and table definitions must match the bitstream format and the decoder's expectations.

## Notes

- `ZSTD_wildcopy` is performance-critical and deliberately permits bounded overrun behavior; callers must provide adequate buffer slack.
- The default normalized tables and symbol bit tables are format-sensitive.
- The error macros depend on encoded `ERROR(...)` values from `error_private.h`.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/btrfs/zstd/zstd_internal.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/btrfs/zstd/zstd_lazy.c -->
# File Research: sources/windows/reactos/drivers/filesystems/btrfs/zstd/zstd_lazy.c

## Scope And Purpose

`zstd_lazy.c` implements Zstd greedy, lazy, lazy2, and btlazy2 block compression strategies. It provides both hash-chain and binary-tree match finders and supports normal prefix compression, dictionary-match-state compression, and external-dictionary compression.

Complete file read: 1138 lines.

## Main Components

- Binary-tree logic:
  - `ZSTD_updateDUBT` inserts unsorted positions into a deferred-update binary tree.
  - `ZSTD_insertDUBT1` sorts one pending candidate.
  - `ZSTD_DUBT_findBestMatch` and `ZSTD_DUBT_findBetterDictMatch` search sorted candidates and optional dictionary match state for the best match.
  - `ZSTD_BtFindBestMatch*` wrappers dispatch by `minMatch` and dictionary mode.
- Hash-chain logic:
  - `ZSTD_insertAndFindFirstIndex_internal` updates the hash chain to the current input.
  - `ZSTD_insertAndFindFirstIndex` exposes that helper for other modules.
  - `ZSTD_HcFindBestMatch_generic` searches hash-chain candidates and optional dictionary chains.
- Lazy parser:
  - `ZSTD_compressBlock_lazy_generic` is the shared normal/dictionary-match-state parser. It checks repcodes, asks the selected match finder for candidates, optionally probes one or two bytes ahead, stores chosen sequences, and updates repcodes.
  - `ZSTD_compressBlock_lazy_extDict_generic` mirrors the parser for external dictionary windows with two-segment matching.
- Public wrappers select parser depth and match finder:
  - Greedy: depth 0, hash chain.
  - Lazy: depth 1, hash chain.
  - Lazy2: depth 2, hash chain.
  - Btlazy2: depth 2, binary tree.
  - Each has no-dictionary, dictionary-match-state, and external-dictionary variants where applicable.

## Integration Points

The file is called through the compressor strategy table in `zstd_compress.c`. It depends on `ZSTD_storeSeq`, window bounds, repcode rules, `ZSTD_count`, `ZSTD_count_2segments`, hash helpers, and compression parameters from `zstd_compress_internal.h`.

## Notes

- The deferred binary tree trades delayed sorting work for faster insertion.
- Pointer and index arithmetic intentionally uses unsigned overflow patterns in several boundary checks.
- Compression ratio and CPU cost are controlled mainly by `searchLog`, `chainLog`, `targetLength`, parser depth, and whether the binary tree is used.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/btrfs/zstd/zstd_lazy.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/btrfs/zstd/zstd_lazy.h -->
# File Research: sources/windows/reactos/drivers/filesystems/btrfs/zstd/zstd_lazy.h

## Scope And Purpose

`zstd_lazy.h` declares the lazy-family Zstd block-compressor entry points and one hash-chain helper.

Complete file read: 67 lines.

## Public Interface

- `ZSTD_insertAndFindFirstIndex` updates the match-state hash chain and returns the first candidate index.
- `ZSTD_preserveUnsortedMark` is declared for index-reduction handling of deferred binary-tree unsorted markers.
- Normal block compressors:
  - `ZSTD_compressBlock_btlazy2`
  - `ZSTD_compressBlock_lazy2`
  - `ZSTD_compressBlock_lazy`
  - `ZSTD_compressBlock_greedy`
- Dictionary-match-state variants:
  - `ZSTD_compressBlock_btlazy2_dictMatchState`
  - `ZSTD_compressBlock_lazy2_dictMatchState`
  - `ZSTD_compressBlock_lazy_dictMatchState`
  - `ZSTD_compressBlock_greedy_dictMatchState`
- External-dictionary variants:
  - `ZSTD_compressBlock_greedy_extDict`
  - `ZSTD_compressBlock_lazy_extDict`
  - `ZSTD_compressBlock_lazy2_extDict`
  - `ZSTD_compressBlock_btlazy2_extDict`

## Integration Points

The header includes `zstd_compress_internal.h` and is consumed by `zstd_compress.c` strategy dispatch plus modules that need hash-chain insertion.

## Notes

This header exposes strategy variants only; parser implementation and match-finder behavior live in `zstd_lazy.c`.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/btrfs/zstd/zstd_lazy.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/btrfs/zstd/zstd_ldm.c -->
# File Research: sources/windows/reactos/drivers/filesystems/btrfs/zstd/zstd_ldm.c

## Scope And Purpose

`zstd_ldm.c` implements Zstd long-distance matching. It finds large repeated regions beyond normal block match-finder reach, stores them as raw sequences, and then interleaves those predefined sequences with the selected normal block compressor.

Complete file read: 619 lines.

## Main Components

- Parameter sizing:
  - `ZSTD_ldm_adjustParameters` fills defaults for window, bucket size, minimum match length, hash log, and sampling rate.
  - `ZSTD_ldm_getTableSize` estimates hash/bucket workspace size.
  - `ZSTD_ldm_getMaxNbSeq` estimates raw sequence capacity.
- Hashing and buckets:
  - `ZSTD_ldm_getSmallHash`, `ZSTD_ldm_getChecksum`, and `ZSTD_ldm_getTag` split a rolling hash into bucket index, checksum, and sampling tag.
  - `ZSTD_ldm_getBucket`, `ZSTD_ldm_insertEntry`, and `ZSTD_ldm_makeEntryAndInsertByTag` manage circular bucket entries.
  - `ZSTD_ldm_fillHashTable` preloads the LDM table over a range.
- Sequence generation:
  - `ZSTD_ldm_generateSequences_internal` rolls through input, samples tagged positions, scans candidate buckets, extends matches forward and backward, emits `rawSeq` records, and fills the table after accepted matches.
  - `ZSTD_ldm_generateSequences` chunks large input, performs overflow correction, enforces maximum distance, and carries leftover literals between chunks.
  - `ZSTD_ldm_reduceTable` adjusts table offsets after overflow correction.
- Sequence consumption:
  - `ZSTD_ldm_skipSequences` advances a raw sequence store when data is skipped.
  - `maybeSplitSequence` splits long raw sequences across block boundaries.
  - `ZSTD_ldm_blockCompress` compresses literal gaps with the normal block compressor and injects LDM matches into `seqStore_t`.

## Integration Points

This file is called by `zstd_compress.c` when LDM is enabled. It uses rolling-hash helpers, Zstd window maintenance, `ZSTD_selectBlockCompressor`, `ZSTD_storeSeq`, fast-table preload helpers, and normal strategy compressors.

## Notes

- LDM is disabled by returning zero workspace/sequence capacity when `enableLdm` is false.
- The implementation is careful about dictionary invalidation on overflow correction.
- Raw sequence offsets must remain valid at the end of split sequences, so max-distance enforcement is done before sequence generation.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/btrfs/zstd/zstd_ldm.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/btrfs/zstd/zstd_ldm.h -->
# File Research: sources/windows/reactos/drivers/filesystems/btrfs/zstd/zstd_ldm.h

## Scope And Purpose

`zstd_ldm.h` declares the long-distance matching API used by Zstd compression.

Complete file read: 110 lines.

## Public Interface

- `ZSTD_LDM_DEFAULT_WINDOW_LOG` aliases the default window-log limit.
- `ZSTD_ldm_fillHashTable` preloads LDM entries for a byte range.
- `ZSTD_ldm_generateSequences` produces long-distance `rawSeq` matches for a source range.
- `ZSTD_ldm_blockCompress` compresses a block while consuming predefined raw LDM sequences and a normal secondary block compressor.
- `ZSTD_ldm_skipSequences` advances raw sequences for data not passed to block compression.
- `ZSTD_ldm_getTableSize` estimates LDM table workspace.
- `ZSTD_ldm_getMaxNbSeq` estimates the maximum number of raw sequences.
- `ZSTD_ldm_adjustParameters` normalizes LDM parameters against regular compression parameters.

## Integration Points

The header includes `zstd_compress_internal.h` for LDM state and sequence types and `zstd.h` for public compression parameter types. It is consumed primarily by `zstd_compress.c`.

## Notes

The comments document important caller contracts: the Zstd window must be updated before sequence generation, the raw sequence store must be large enough, and predefined sequences can span block boundaries.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/btrfs/zstd/zstd_ldm.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/btrfs/zstd/zstd_opt.c -->
# File Research: sources/windows/reactos/drivers/filesystems/btrfs/zstd/zstd_opt.c

## Scope And Purpose

`zstd_opt.c` implements Zstd's optimal parser strategies: `btopt`, `btultra`, and `btultra2`. It builds a binary-tree match finder, prices literals/matches from adaptive statistics, computes a shortest path through candidate sequences, and emits the chosen parse.

Complete file read: 1200 lines.

## Main Components

- Price model:
  - `ZSTD_bitWeight`, `ZSTD_fracWeight`, and `WEIGHT` convert symbol frequencies to bit-cost estimates.
  - `ZSTD_rescaleFreqs` initializes or decays literal, literal-length, match-length, and offset-code statistics, optionally from dictionary entropy tables.
  - `ZSTD_rawLiteralsCost`, `ZSTD_litLengthPrice`, and `ZSTD_getMatchPrice` score candidate sequences.
  - `ZSTD_updateStats` updates adaptive statistics after emitting a sequence.
- Match insertion and collection:
  - `ZSTD_insertAndFindFirstIndexHash3` maintains the special 3-byte hash table.
  - `ZSTD_insertBt1` inserts positions into the binary tree.
  - `ZSTD_updateTree_internal` and exported `ZSTD_updateTree` advance the tree for dictionary loading.
  - `ZSTD_insertBtAndGetAllMatches` collects repcode, hash3, binary-tree, external-dictionary, and dictionary-match-state candidates.
  - `ZSTD_BtGetAllMatches` dispatches match collection by `minMatch`.
- Optimal parsing:
  - `ZSTD_compressBlock_opt_generic` initializes costs, explores candidate parses in `priceTable`, updates per-position repcodes, backtracks the lowest-cost path, emits sequences, and returns last-literal length.
- Public wrappers:
  - `ZSTD_compressBlock_btopt`
  - `ZSTD_compressBlock_btultra`
  - `ZSTD_compressBlock_btultra2`
  - Dictionary-match-state and external-dictionary variants for btopt/btultra.
- Two-pass ultra mode:
  - `ZSTD_initStats_ultra` performs a first pass on the first block to seed statistics, then resets match history before the real parse.
  - `ZSTD_upscaleStats` reinforces first-pass statistics.

## Integration Points

The file is selected by `zstd_compress.c` for high compression strategies. It depends on `hist.h`, FSE/HUF symbol-cost state, `ZSTD_storeSeq`, repcode update helpers, binary-tree tables in `ZSTD_matchState_t`, and the shared constants in `zstd_internal.h`.

## Notes

- `btultra2` is intentionally first-block/no-dictionary/no-LDM only.
- The parser uses bounded tables sized by `ZSTD_OPT_NUM`; large matches can trigger immediate encoding.
- Cost model changes directly affect compression ratio, speed, and decompression locality.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/btrfs/zstd/zstd_opt.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/btrfs/zstd/zstd_opt.h -->
# File Research: sources/windows/reactos/drivers/filesystems/btrfs/zstd/zstd_opt.h

## Scope And Purpose

`zstd_opt.h` declares the optimal-parser Zstd strategy entry points and the binary-tree update helper used during dictionary loading.

Complete file read: 56 lines.

## Public Interface

- `ZSTD_updateTree` updates the binary tree for dictionary content loading.
- No-dictionary optimal compressors:
  - `ZSTD_compressBlock_btopt`
  - `ZSTD_compressBlock_btultra`
  - `ZSTD_compressBlock_btultra2`
- Dictionary-match-state variants:
  - `ZSTD_compressBlock_btopt_dictMatchState`
  - `ZSTD_compressBlock_btultra_dictMatchState`
- External-dictionary variants:
  - `ZSTD_compressBlock_btopt_extDict`
  - `ZSTD_compressBlock_btultra_extDict`

## Integration Points

The header includes `zstd_compress_internal.h` for match-state and sequence-store types. It is consumed by the compressor strategy dispatcher and dictionary-loading paths.

## Notes

The header explicitly notes that `btultra2` has no dictionary or external-dictionary variant because it is intended only for the first block without prefix/dictionary history.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/btrfs/zstd/zstd_opt.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/cdfs/CMakeLists.txt -->
# File Research: sources/windows/reactos/drivers/filesystems/cdfs/CMakeLists.txt

## Scope And Purpose

`CMakeLists.txt` defines the ReactOS CDFS kernel-mode filesystem driver build.

Complete file read: 41 lines.

## Build Behavior

- Adds ReactOS driver include directories.
- Defines the CDFS source list, including allocation, cache, initialization, create/cleanup/close, directory, file info, fsctl, read/write, PnP, resource, verification, volume info, and work queue modules.
- Builds `cdfs` as a module library with `cdfs.rc`.
- Marks the target as a kernel-mode driver with `set_module_type(cdfs kernelmodedriver)`.
- Links against `${PSEH_LIB}` and `memcmp`.
- Imports `ntoskrnl` and `hal`.
- Installs the driver under `reactos/system32/drivers`.
- Registers `cdfs_reg.inf`.

## Integration Points

This file is the build entry for `sources/windows/reactos/drivers/filesystems/cdfs`. It wires the CDFS driver into the ReactOS build, driver packaging, and registry INF installation.

## Notes

The source list is explicit; adding a CDFS module requires updating this file unless another build file includes it indirectly.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/cdfs/CMakeLists.txt -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/cdfs/allocsup.c -->
# File Research: sources/windows/reactos/drivers/filesystems/cdfs/allocsup.c

## Scope And Purpose

`allocsup.c` implements CDFS allocation mapping through `CD_MCB`. It maps file offsets to logical CD disk offsets, lazily loads allocation extents from directory entries, supports multi-extent and interleaved files, and manages MCB storage lifetime.

Complete file read: 935 lines.

## Main Components

- `CdLookupAllocation` is the main lookup path. It returns the logical disk offset and byte count for a file offset. If the MCB lacks the mapping, it walks the parent directory's dirents, adds all allocation extents for the file, and retries.
- `CdAddAllocationFromDirent` grows the MCB array when needed and adds one extent from a `DIRENT`, converting block offsets and interleave sizes to bytes.
- `CdAddInitialAllocation` initializes the single aligned MCB entry used for directory/path-table style streams.
- `CdTruncateAllocation` truncates the MCB at the entry containing a starting file offset.
- `CdInitializeMcb` initializes an FCB's MCB to use the embedded single entry.
- `CdUninitializeMcb` frees an expanded MCB array.
- `CdFindMcbEntry` linearly finds the entry containing a file offset or the insertion point for a missing entry.
- `CdDiskOffsetFromMcbEntry` converts a file offset within an MCB entry to a disk offset and contiguous byte count, including interleave data/skip handling.

## Integration Points

This file depends on `cdprocs.h`, FCB locking, parent directory acquisition, dirent enumeration helpers, block-size conversion macros, CDFS pool allocation, and CDFS exception raising. It is used by read and stream code that need logical on-disc locations.

## Notes

- DASD I/O bypasses normal MCB lookup and maps file offset directly to disk offset.
- MCBs are not sparse; adding entry `N` makes it the current last entry.
- Interleaved files may return only the current data-block fragment as contiguous.
- Corrupt multi-extent chains raise `STATUS_DISK_CORRUPT_ERROR`.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/cdfs/allocsup.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/cdfs/cachesup.c -->
# File Research: sources/windows/reactos/drivers/filesystems/cdfs/cachesup.c

## Scope And Purpose

`cachesup.c` implements CDFS cache-manager support for internal stream files, MDL-read completion, and volume cache purging.

Complete file read: 671 lines.

## Main Components

- `CdCreateInternalStream` creates a stream file object for directory or path-table FCBs with `IoCreateStreamFileObjectLite`, initializes cache mapping with `CcInitializeCacheMap`, attaches the stream to the FCB, and gives the stream a borrowed name for profiling.
- During first stream initialization, `CdCreateInternalStream` reads the directory self entry, validates it, updates file/allocation/valid-data sizes, rebuilds initial allocation when needed, maps hidden attributes, converts CD time to NT time, and marks the FCB initialized.
- Error cleanup dereferences partially created stream objects, releases temporary dirent context, decrements the extra FCB reference, and unlocks the FCB.
- `CdDeleteInternalStream` detaches an internal stream from an FCB, uninitializes its cache map, clears the borrowed name pointer, and dereferences the file object.
- `CdCompleteMdl` completes MDL reads by calling `CcMdlReadComplete`, clearing `Irp->MdlAddress`, and completing the IRP.
- `CdPurgeVolume` closes delayed FCBs, acquires all files, walks the FCB table, flushes image sections, purges data sections, optionally deletes internal streams during dismount, and handles path-table and volume-DASD FCBs.

## Integration Points

This file is tied to Windows cache manager APIs (`CcInitializeCacheMap`, `CcUninitializeCacheMap`, `CcPurgeCacheSection`, `CcMdlReadComplete`), memory-manager image-section flushing, CDFS FCB/VCB locking, reference counting, dirent lookup, allocation helpers, and teardown logic.

## Notes

- Stream file names are borrowed from FCB-owned buffers and explicitly nulled before object dereference.
- `CdPurgeVolume` returns the first `STATUS_UNABLE_TO_DELETE_SECTION` if purge fails because a section remains active.
- The create path carefully keeps an extra FCB reference to survive error-path close/teardown behavior.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/cdfs/cachesup.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/cdfs/cd.h -->
# File Research: sources/windows/reactos/drivers/filesystems/cdfs/cd.h

## Scope And Purpose

`cd.h` defines CDFS on-disc structures and constants for ISO 9660, HSG, Joliet, directory records, path-table records, CD time conversion, and XA system-use data.

Complete file read: 534 lines.

## Main Components

- Sector constants define 2048-byte logical sectors, 2352-byte raw/XA sectors, sector masks, and sector shifts.
- Volume descriptor constants define descriptor sector, descriptor types, version, standard IDs, volume ID size, root directory-entry length, and TOC data-track flags.
- `RAW_ISO_VD`, `RAW_HSG_VD`, and `RAW_JOLIET_VD` describe primary/secondary volume descriptor layouts.
- `CdRvd*` macros abstract field access across ISO and HSG volume descriptors.
- `RAW_DIRENT` overlays ISO/HSG directory records, including extent location, data length, record time, flags, interleave fields, volume sequence number, and file ID.
- Directory attribute constants define hidden, directory, associated-file, and multi-extent flags.
- `CdRawDirentFlags` selects the correct HSG or ISO flag field.
- `CdConvertCdTimeToNtTime` converts 7-byte CD timestamps into NT time and applies ISO GMT offset when valid.
- `RAW_PATH_ISO` and `RAW_PATH_HSG` describe path-table entry variants.
- `CdRawPathIdLen`, `CdRawPathXar`, and `CdRawPathLoc` abstract path-table field access across ISO/HSG layouts.
- `SYSTEM_USE_XA` and `XA_EXTENT_TYPE` define XA extension metadata and extent categories.

## Integration Points

This header is included through CDFS internals wherever raw disc structures are parsed. It relies on broader driver definitions such as `VCB_STATE_HSG`, `FlagOn`, `Add2Ptr`, `RtlTimeFieldsToTime`, and CDFS VCB/IRP context types.

## Notes

- Structures intentionally mirror unaligned on-disc layouts; helper macros avoid unsafe direct interpretation in some cases.
- CD time conversion applies GMT offsets only for ISO media and only for the valid `[-48, 52]` quarter-hour range.
- The raw directory record supports file IDs up to 255 bytes, beyond strict short-name assumptions.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/cdfs/cd.h -->