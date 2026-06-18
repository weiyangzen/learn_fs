# Group Research: group_1806_vdo_sources_block_storage_vdo_utils_vdo_vdoStatsWriter_c_sources_bl_c7ef1ae17a39

Scope confirmed against `Docs/research_subset_a.md`: all files are under included source tree `sources/block-storage/vdo`. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/block-storage/vdo/utils/vdo/vdoStatsWriter.c -->
# File Research: sources/block-storage/vdo/utils/vdo/vdoStatsWriter.c

## Purpose

`vdoStatsWriter.c` formats an in-memory `struct vdo_statistics` into a verbose, aligned text report. It is the writer half used by `vdostats.c` when verbose/YAML-like output is requested after `read_vdo_stats()` has decoded the kernel/device-mapper stats message.

The top comment says new statistics must be kept in sync with:

- `../base/statistics.h`
- `../base/message-stats.c`
- `../base/pool-sysfs-stats.c`
- `./messageStatsReader.c`
- `../../../perl/Permabit/Statistics/Definitions.pm`

## Main Data Flow

The file keeps global output state:

- `fieldCount`: number of label/value rows currently populated.
- `maxLabelLength`: longest label for alignment.
- `labels[MAX_STATS][MAX_STAT_LENGTH]`
- `values[MAX_STATS][MAX_STAT_LENGTH]`

`vdo_write_stats(struct vdo_statistics *stats)` resets those globals, calls `write_vdo_statistics(" ", stats)`, then prints all collected rows as:

```text
<label><padding> : <value>
```

## Core Helpers

Primitive writers:

- `write_u8()`
- `write_u64()`
- `write_string()`
- `write_block_count_t()`
- `write_u32()`
- `write_double()`

Each writes a label string to `labels[fieldCount]`, updates `maxLabelLength`, writes the formatted value to `values[fieldCount]`, then increments `fieldCount`.

Nested statistics writers:

- `write_block_allocator_statistics()`
- `write_commit_statistics()`
- `write_recovery_journal_statistics()`
- `write_packer_statistics()`
- `write_slab_journal_statistics()`
- `write_slab_summary_statistics()`
- `write_ref_counts_statistics()`
- `write_block_map_statistics()`
- `write_hash_lock_statistics()`
- `write_error_statistics()`
- `write_bio_stats()`
- `write_memory_usage()`
- `write_index_statistics()`
- `write_vdo_statistics()`

These build labels with `asprintf()`, pass nested field values to primitive writers, free the temporary label, and propagate any non-`VDO_SUCCESS` result.

## Important Calculations

`write_vdo_statistics()` derives several user-facing values:

- `one_k_blocks = physical_blocks * block_size / 1024`
- `one_k_blocks_used = (data_blocks_used + overhead_blocks_used) * block_size / 1024`
- `one_k_blocks_available = (physical_blocks - data_blocks_used - overhead_blocks_used) * block_size / 1024`
- `used_percent` rounded to nearest integer.
- `saving_percent`, based on logical blocks used versus physical data blocks used.
- `512 byte emulation` string based on `logical_block_size == 512`.
- `write_amplification_ratio` from `(bios_meta.write + bios_out.write) / bios_in.write`, rounded with `roundf()` and later printed with two decimals.

Several capacity and savings fields are emitted as `"N/A"` when the VDO is in recovery mode or when `stats->mode` is `"read-only"`.

## Dependencies

Includes:

- Generic C: `stdio.h`, `stdlib.h`, `string.h`
- Utility headers: `numeric.h`, `string-utils.h`
- VDO/base headers: `math.h`, `statistics.h`, `status-codes.h`, `types.h`, `vdoStats.h`

The file depends heavily on the layout of `struct vdo_statistics` and its nested structs.

## Notable Behaviors and Risks

- `MAX_STATS` is fixed at `239`. If the stats schema grows without updating this constant, the primitive writers can write past `labels`/`values`.
- `MAX_STAT_LENGTH` is fixed at `80`, but labels are written with `sprintf()` rather than bounded `snprintf()`. Current labels appear intended to fit, but this is a schema-coupled safety assumption.
- All label construction uses `asprintf()` and frees correctly after use.
- `write_double()` prints with `%.2f`, but `write_amplification_ratio` is already rounded to an integer-valued float via `roundf()`, so the display loses fractional ratio precision.
- The leading prefix passed from `vdo_write_stats()` is `" "`, so all labels intentionally begin with a leading space.
<!-- END FILE RESEARCH: sources/block-storage/vdo/utils/vdo/vdoStatsWriter.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/vdo/utils/vdo/vdoVolumeUtils.c -->
# File Research: sources/block-storage/vdo/utils/vdo/vdoVolumeUtils.c

## Purpose

`vdoVolumeUtils.c` provides common helper routines for loading and freeing a `UserVDO` from a file or block device. Many utilities in this directory use these wrappers instead of directly constructing a `PhysicalLayer` and loading VDO metadata.

## Main API

Public functions:

- `makeVDOFromFile(const char *filename, bool readOnly, UserVDO **vdoPtr)`
- `readVDOWithoutValidation(const char *filename, UserVDO **vdoPtr)`
- `freeVDOFromFile(UserVDO **vdoPtr)`

Internal helper:

- `loadVDOFromFile(const char *filename, bool readOnly, bool validateConfig, UserVDO **vdoPtr)`

## Behavior

`loadVDOFromFile()` enforces:

```c
validateConfig || readOnly
```

This prevents creating a writable VDO layer without validating config.

It then:

1. Builds either a read-only or writable `PhysicalLayer`:
   - `makeReadOnlyFileLayer(filename, &layer)`
   - `makeFileLayer(filename, 0, &layer)`
2. Calls `loadVDO(layer, validateConfig, &vdo)`.
3. On load failure, destroys the layer and reports the decoded VDO error with `warnx()`.
4. On success, returns the `UserVDO`.

`freeVDOFromFile()`:

1. Handles `NULL` input gracefully.
2. Saves `vdo->layer`.
3. Calls `freeUserVDO(&vdo)`.
4. Destroys the physical layer.
5. Clears the caller’s pointer.

## Dependencies

Includes:

- `vdoVolumeUtils.h`
- `err.h`
- `errors.h`
- `permassert.h`
- `status-codes.h`
- `fileLayer.h`
- `userVDO.h`

## Used By

This helper is used by VDO metadata and admin utilities including:

- `vdoaudit.c`
- `vdodumpblockmap.c`
- `vdodumpmetadata.c`
- `vdolistmetadata.c`
- `vdostats` indirectly does not load backing files, but other VDO tools use the pattern.
- `vdoreadonly.c` and `vdoforcerebuild.c` use lower-level file layer calls because they mutate metadata states directly.

## Notable Behaviors and Risks

- The static `errBuf` is shared inside this compilation unit only.
- The layer ownership contract is clear: on successful load, the returned `UserVDO` owns a layer that must be released through `freeVDOFromFile()`.
- `readVDOWithoutValidation()` is intentionally read-only and used for metadata inspection paths where config validation may fail or be unnecessary.
<!-- END FILE RESEARCH: sources/block-storage/vdo/utils/vdo/vdoVolumeUtils.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/vdo/utils/vdo/vdoVolumeUtils.h -->
# File Research: sources/block-storage/vdo/utils/vdo/vdoVolumeUtils.h

## Purpose

`vdoVolumeUtils.h` declares shared loading/freeing helpers for `UserVDO` instances backed by a file or block device.

## API

Declared functions:

- `makeVDOFromFile(const char *filename, bool readOnly, UserVDO **vdoPtr)`
- `readVDOWithoutValidation(const char *filename, UserVDO **vdoPtr)`
- `freeVDOFromFile(UserVDO **vdoPtr)`

The loader functions are annotated with `__must_check`, requiring callers to handle error status codes.

## Dependencies

Includes:

- `types.h`
- `userVDO.h`

## Design Notes

The header intentionally hides the internal `PhysicalLayer` construction details. Callers only need a filename, a read-only flag where applicable, and a `UserVDO **` result slot.

This file is the public boundary for `vdoVolumeUtils.c`.
<!-- END FILE RESEARCH: sources/block-storage/vdo/utils/vdo/vdoVolumeUtils.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/vdo/utils/vdo/vdoaudit.c -->
# File Research: sources/block-storage/vdo/utils/vdo/vdoaudit.c

## Purpose

`vdoaudit.c` implements `vdoAudit`, a consistency checker for an offline VDO backing device. It audits:

- Logical block count from block map entries versus saved recovery journal count.
- Block map entry validity.
- Physical block reference counts observed from the block map versus stored slab reference counts.
- Slab summary free-space hints versus actual free blocks.

It can print either summary output or verbose per-error diagnostics.

## Command-Line Interface

Usage:

```text
vdoAudit [ [--summary] | [--verbose] ] <filename>
```

Options:

- `--help`
- `--summary`
- `--verbose`
- `--version`

`--summary` is the default behavior.

## Key Data Structures

`SlabAudit` tracks audit state for each slab:

- `slabNumber`
- `slabOrigin`
- `refCounts`: audited reference counts derived from block map traversal.
- `badRefCounts`
- `deltaCounts`: histogram of stored minus audited reference deltas.
- `firstError`
- `lastError`

Global audit state includes:

- `vdo`
- `slabSummaryEntries`
- `slabDataBlocks`
- `hintShift`
- `lbnCount`
- `slabs[MAX_VDO_SLABS]`
- `badBlockMappings`
- `badRefCounts`
- `badSlabs`
- `badSummaryHints`

## Main Flow

`main()`:

1. Registers status codes.
2. Parses arguments.
3. Loads VDO read-only with `makeVDOFromFile()`.
4. Initializes one `SlabAudit` per slab and allocates each slab’s `refCounts`.
5. Calls `auditVDO()`.
6. Prints success message or summary.
7. Frees allocations and exits `0` on pass, `1` otherwise.

`auditVDO()`:

1. Rejects `VDO_NEW` as unauditable.
2. Warns if VDO state is not `VDO_CLEAN`.
3. Calls `examineBlockMapEntries(vdo, examineBlockMapEntry)` to validate mappings and populate audited refs.
4. Loads slab summary with `readSlabSummary()`.
5. Compares counted logical blocks with `vdo->states.recovery_journal.logical_blocks_used`.
6. Calls `verifyPBNRefCounts()`.
7. Returns success only if logical count, ref counts, and summary hints all match.

## Block Map Auditing

`examineBlockMapEntry()` validates each mapping:

- Unmapped entries must use `VDO_ZERO_BLOCK`.
- Compressed states must not point at `VDO_ZERO_BLOCK`.
- Leaf mappings increment `lbnCount`.
- PBNs must map to a valid slab and data block, not slab metadata.
- Interior tree page references are marked as `PROVISIONAL_REFERENCE_COUNT`.
- Duplicate interior tree page references, compressed tree pages, or refcount overflows are reported as mapping problems.

## Reference Count Auditing

`verifyPBNRefCounts()` allocates a buffer for slab reference count metadata and calls `verifySlab()` for each slab.

`verifySlab()`:

- For pristine slabs where `load_ref_counts` is false, expects all audited references to be zero and all slab data blocks to be free.
- For used slabs, reads reference count blocks from disk and compares them to audited references.

`verifyRefCountSector()` handles special provisional values:

- Tree pages may validly have stored reference count `1` or `MAXIMUM_REFERENCE_COUNT`.
- Empty audited refs with stored `PROVISIONAL_REFERENCE_COUNT` are tolerated.

`verifySummaryHint()` checks slab free block count against `fullness_hint << hintShift` with an allowed error of `1 << hintShift`.

## Output

Verbose mode uses `warnx()` for detailed mapping/refcount/summary issues.

Summary mode prints:

- Total block mapping errors.
- Total free-space hint errors.
- Total reference count errors.
- Total slabs containing errors.
- Per-slab error range and histogram.

## Dependencies

Includes:

- System: `err.h`, `getopt.h`, `linux/fs.h`, `stdio.h`, `stdlib.h`, `sys/ioctl.h`, `sys/stat.h`, `unistd.h`
- Utility: `errors.h`, `fileUtils.h`, `logger.h`, `memory-alloc.h`, `syscalls.h`
- VDO/base: `encodings.h`, `status-codes.h`, `types.h`
- VDO user helpers: `blockMapUtils.h`, `slabSummaryReader.h`, `userVDO.h`, `vdoVolumeUtils.h`

## Notable Behaviors and Risks

- `slabs` is statically sized to `MAX_VDO_SLABS`, matching VDO constraints.
- `freeAuditAllocations()` assumes `vdo` is non-null when iterating `vdo->slabCount`; current call sites satisfy this after VDO loading.
- Summary warnings for a clean logical block count are printed with `warnx()`, so success diagnostics go to stderr.
- The auditor can continue after some per-entry mapping problems, but hard errors from traversal or reads cause audit failure.
<!-- END FILE RESEARCH: sources/block-storage/vdo/utils/vdo/vdoaudit.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/vdo/utils/vdo/vdocalculatesize.c -->
# File Research: sources/block-storage/vdo/utils/vdo/vdocalculatesize.c

## Purpose

`vdocalculatesize.c` implements `vdoCalculateSize`, a planning utility that estimates VDO physical usable space, metadata overhead, dedupe window, and memory usage for supplied physical/logical sizes and format parameters.

## Command-Line Interface

Usage requires:

- `--physical-size=MB`
- `--logical-size=MB`

Optional arguments:

- `--block-map-cache-size=blocks`
- `--human-readable`
- `--index-memory-size=GB`
- `--slab-bits=bits`
- `--slab-size=MB`
- `--sparse-index`
- `--version`
- `--help`

Defaults:

- Block map cache size: `32768` blocks.
- Index memory: `"0.25"`.
- Slab bits: `19`, producing 2 GiB slabs.
- Sparse index: false.
- Human-readable: false.

## Main Data Structure

`struct vdoInfo` contains:

- Input parameters: index memory, logical size, physical size, sparse flag, slab bits/size.
- UDS info: index size and dedupe window.
- VDO block counts: physical, logical, user data, fixed system blocks.
- Slab info: block count, slab count, journal usage, reference count usage.
- Block map info: cache size, total pages/leaves, usable space, forest memory usage.
- Output formatting flag.

## Main Flow

`main()`:

1. Initializes `vdoInfo` with defaults.
2. Parses arguments with `parseArgs()`.
3. Validates argument combinations with `checkArgs()`.
4. Calculates all derived values through `calculateVDOInfo()`.
5. Checks limits with `checkVDOConfigError()`.
6. Prints grouped report sections with `printVDOInfo()`.

## Core Calculations

Block map pages:

- Leaf count uses `vdo_compute_block_map_page_count(logicalBlocks)`.
- Parent/interior pages are computed by repeatedly dividing by `VDO_BLOCK_MAP_ENTRIES_PER_PAGE` across tree height.

UDS index size:

- `getUDSIndexSize()` builds `UdsConfigStrings`, calls `parseIndexConfig()`, then `computeIndexBlocks()`.

Dedupe window:

- `0.25` GiB memory maps to 256 GiB dense window.
- `0.5` or `0.50` maps to 512 GiB.
- `0.75` maps to 768 GiB.
- Positive integer GiB maps to `memory * 1024 GiB`.
- Sparse index multiplies dedupe window by 10.

VDO block info:

- `totalSystemBlock = FIXED_METADATA_BLOCKS + udsIndexSize`
- `physicalBlocks = physicalSize / VDO_BLOCK_SIZE`
- `logicalBlocks = logicalSize / VDO_BLOCK_SIZE`
- `userDataBlocks = physicalBlocks - totalSystemBlock`

Slab info:

- `slabSizeInBlock = 1 << slabBits`
- `slabCount = userDataBlocks / slabSizeInBlock`
- `totalSlabJournal = slabCount * DEFAULT_VDO_SLAB_JOURNAL_SIZE`
- `totalReferenceCount = vdo_get_saved_reference_count_size(userDataBlocks)`

Usable space:

```c
(userDataBlocks
 - totalBlockMapPages
 - totalReferenceCount
 - totalSlabJournal) * VDO_BLOCK_SIZE
```

## Validation

`checkVDOConfigError()` rejects:

- Logical blocks beyond `MAXIMUM_VDO_LOGICAL_BLOCKS`.
- Physical blocks beyond `MAXIMUM_VDO_PHYSICAL_BLOCKS`.
- Physical size below calculated minimum VDO size.

Slab validation:

- Slab size must be between `MIN_VDO_SLAB_SIZE` and `MAX_VDO_SLAB_SIZE`.
- `--slab-size` must be a power-of-two number of 4 KiB blocks.
- `--slab-bits` and `--slab-size` are mutually exclusive.

## Dependencies

Includes:

- System: `ctype.h`, `err.h`, `getopt.h`, `math.h`, `stdio.h`, `stdlib.h`, `string.h`
- VDO/base: `constants.h`, `status-codes.h`, `types.h`, `vdoConfig.h`
- Utility: `blockMapUtils.h`, `parseUtils.h`, `printUtils.h`

## Notable Behaviors and Risks

- Sizes are parsed with `parseSize(optarg, true, ...)`, so command help says default unit is MB.
- The help text for `--slab-bits` says values between 4 and 23, but parsing enforces `MIN_SLAB_BITS = 13` through `MAX_SLAB_BITS = 23`.
- Some spelling/formatting issues exist in diagnostics, such as “minumum” and “maxmium”.
- Calculations are model estimates and depend on constants matching the formatter and on-disk layout.
<!-- END FILE RESEARCH: sources/block-storage/vdo/utils/vdo/vdocalculatesize.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/vdo/utils/vdo/vdodebugmetadata.c -->
# File Research: sources/block-storage/vdo/utils/vdo/vdodebugmetadata.c

## Purpose

`vdodebugmetadata.c` implements `vdoDebugMetadata`, a debugging utility for metadata dump files created by `vdodumpmetadata`. It loads selected metadata regions into process memory so a developer can inspect them under GDB, and can also search slab/recovery journals from the command line.

It explicitly does not decode or expose full block map pages.

## Command-Line Interface

Usage:

```text
vdoDebugMetadata [--pbn=<pbn>] [--searchLBN=<lbn>] <filename>
```

Options:

- `--help`
- `--pbn=<pbn>`: print slab journal entries for the given PBN.
- `--searchLBN=<lbn>`: print recovery journal entries for the given LBN.
- `--version`

The program is intended to be run under GDB with a breakpoint on `doNothing()`.

## Key Data Structures

`SlabState`:

- `slabJournalBlocks`
- `referenceBlocks`

`UnpackedJournalBlock`:

- `header`
- `sectors[VDO_SECTORS_PER_BLOCK]`

Global loaded metadata:

- `vdo`
- `slabSummary`
- `slabCount`
- `slabs`
- `recoveryJournal`
- `rawJournalBytes`
- `nextBlock`
- `slabConfig`
- arrays of requested `pbns` and `searchLBNs`

## Main Flow

`main()`:

1. Registers status codes.
2. Allocates arrays for requested PBNs and LBNs.
3. Parses options.
4. Calls `readVDOFromDump()` to construct a `UserVDO` from the dump file.
5. Calls `allocateMetadataSpace()`.
6. Calls `readMetadata()`.
7. Prints the VDO nonce.
8. Searches slab journals for requested PBNs.
9. Searches recovery journal for requested LBNs.
10. Calls `doNothing()` as a GDB breakpoint target.
11. Prints help if no searches were requested.
12. Frees metadata and destroys the layer.

## Dump Loading

`readVDOFromDump()`:

1. Creates a read-only file layer.
2. Loads volume geometry.
3. Creates `UserVDO`.
4. Adjusts geometry so `VDO_DATA_REGION` starts at block `1`, matching dump layout.
5. Loads the superblock.
6. Decodes component states.
7. Forces `states.layout.start = 2`.
8. Calls `setDerivedSlabParameters()`.

This adapts the dump-file layout back into enough `UserVDO` state to reason about metadata.

## Metadata Loading

`allocateMetadataSpace()` allocates:

- Per-slab reference count block buffers.
- Per-slab slab journal block buffers.
- A raw recovery journal buffer.
- Decoded `UnpackedJournalBlock` array.
- Slab summary block buffers.

`readMetadata()` computes how many non-block-map metadata blocks are at the end of the dump, then positions `nextBlock` there. It reads:

1. Per-slab reference count blocks.
2. Per-slab journal blocks.
3. Raw recovery journal.
4. Slab summary blocks.

Recovery journal headers and sectors are unpacked into `recoveryJournal`.

## Search Features

`findSlabJournalEntries(pbn)`:

- Verifies PBN is inside the slab depot.
- Computes slab number and slab offset.
- Iterates all slab journal blocks and entries for that slab.
- Prints matching operations.

`findRecoveryJournalEntries(lbn)`:

- Converts LBN to block map page/slot.
- Iterates all recovery journal blocks, sectors, and entries.
- Prints entries matching the desired slot, including:
  - PBN
  - operation
  - mapping state
  - journal block validity
  - sequence congruence
  - sector validity

## Dependencies

Includes:

- System: `err.h`, `getopt.h`, `stdio.h`, `stdlib.h`
- Utility: `errors.h`, `logger.h`, `memory-alloc.h`, `syscalls.h`
- VDO/base: `encodings.h`, `status-codes.h`, `types.h`
- VDO helpers: `fileLayer.h`, `parseUtils.h`, `userVDO.h`, `vdoVolumeUtils.h`

## Notable Behaviors and Risks

- `processArgs()` checks the `--searchLBN` limit using `pbnCount == MAX_SEARCH_LBNS` instead of `searchLBNCount == MAX_SEARCH_LBNS`; this can fail to enforce the intended LBN limit.
- The utility assumes the dump ordering emitted by `vdodumpmetadata`: optional block map content first, then per-slab metadata, recovery journal, slab summary.
- Error handling is intentionally fatal in many read/allocation paths because the tool is for debugging complete dump files.
<!-- END FILE RESEARCH: sources/block-storage/vdo/utils/vdo/vdodebugmetadata.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/vdo/utils/vdo/vdodumpblockmap.c -->
# File Research: sources/block-storage/vdo/utils/vdo/vdodumpblockmap.c

## Purpose

`vdodumpblockmap.c` implements `vdoDumpBlockMap`, a utility that prints VDO logical-to-physical mappings from a cleanly shut down VDO device.

It can dump either:

- A single LBN mapping via `--lba`.
- All non-empty mappings by traversing the block map.

## Command-Line Interface

Usage:

```text
vdoDumpBlockMap [--lba=<lba>] <filename>
```

Options:

- `--help`
- `--lba=<lba>`
- `--version`

## Main Flow

`main()`:

1. Registers status codes.
2. Parses arguments.
3. Loads VDO read-only with `makeVDOFromFile()`.
4. If `--lba` was provided, calls `dumpLBN()`.
5. Otherwise calls `examineBlockMapEntries(vdo, dumpBlockMapEntry)`.
6. Frees VDO and exits based on result.

## Single Mapping Output

`dumpLBN()`:

1. Calls `findLBNMapping(vdo, lbn, &pbn, &state)`.
2. Prints the LBN.
3. Prints one of:
   - `unmapped`
   - `mapped`
   - `compressed`, with compression slot derived from mapping state.

## Full Block Map Output

`dumpBlockMapEntry()` is a `MappingExaminer` callback. It prints any entry where:

- state is not `VDO_MAPPING_STATE_UNMAPPED`, or
- PBN is not `VDO_ZERO_BLOCK`.

The line includes:

- block map page PBN
- slot
- height
- target PBN
- compression state

## Dependencies

Includes:

- System: `err.h`, `getopt.h`, `stdio.h`, `stdlib.h`
- Utility: `errors.h`, `logger.h`
- VDO/base: `encodings.h`, `status-codes.h`, `types.h`
- VDO helpers: `blockMapUtils.h`, `vdoVolumeUtils.h`

## Notable Behaviors and Risks

- `--lba` parsing uses `strtoull()` and checks `ERANGE`, `EINVAL`, and empty input.
- The sentinel for “no LBN specified” is `0xFFFFFFFFFFFFFFFF`, so that exact LBN cannot be requested distinctly if it were otherwise meaningful.
- The help says the VDO should be cleanly shut down; the code relies on loader/traversal behavior rather than explicitly checking clean state.
<!-- END FILE RESEARCH: sources/block-storage/vdo/utils/vdo/vdodumpblockmap.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/vdo/utils/vdo/vdodumpmetadata.c -->
# File Research: sources/block-storage/vdo/utils/vdo/vdodumpmetadata.c

## Purpose

`vdodumpmetadata.c` implements `vdodumpmetadata`, a utility that copies VDO metadata regions from a backing device into an output file. The dump can later be inspected by `vdoDebugMetadata`.

It supports full metadata dumps, dumps without block map pages, or targeted block map page dumps for specified LBNs.

## Command-Line Interface

Usage:

```text
vdodumpmetadata [--no-block-map] [--lbn=<lbn>] <vdoBacking> <outputFile>
```

Options:

- `--help`
- `--lbn=<lbn>`: implies `--no-block-map`; can be supplied up to 255 times.
- `--no-block-map`
- `--version`

## Main Flow

`main()`:

1. Registers status codes.
2. Allocates the `lbns` array.
3. Parses arguments.
4. Loads input VDO read-only with `makeVDOFromFile()`.
5. Allocates a copy buffer of `STRIDE_LENGTH * VDO_BLOCK_SIZE`.
6. Opens the output file with `FU_CREATE_WRITE_ONLY`.
7. Dumps:
   - geometry block
   - superblock
   - block map content, unless suppressed
   - slab metadata
   - recovery journal
   - slab summary
8. Frees allocations and exits.

## Dump Ordering

The output file layout is:

1. Geometry block.
2. Superblock.
3. Either:
   - full block map root pages and referenced internal pages, or
   - selected LBN page blocks, or
   - no block map pages.
4. Per-slab reference count blocks and slab journal blocks.
5. Recovery journal.
6. Slab summary.

`vdoDebugMetadata` depends on this ordering by locating the fixed non-block-map metadata at the end of the dump.

## Block Copying

`copyBlocks(startBlock, count)` copies in strides of up to `STRIDE_LENGTH` blocks:

1. Reads from VDO layer.
2. Writes to output FD with `write_buffer()`.
3. Advances source and remaining count.

`zeroBlock()` writes one zeroed 4 KiB block, used when a requested LBN’s block map page is absent.

## Block Map Dumping

`dumpBlockMap()`:

- Full mode:
  - Copies root block map pages from `vdo->states.block_map`.
  - Traverses block map entries and calls `copyPage()` for referenced internal pages.
- Targeted mode:
  - Calls `findLBNPage()` for each requested LBN.
  - Copies that page or writes a zero page if missing.

`copyPage()` ignores:

- leaf height `0`
- invalid data blocks
- unmapped entries

Otherwise, it copies the referenced page.

## Dependencies

Includes:

- System: `err.h`, `getopt.h`
- Utility: `errors.h`, `fileUtils.h`, `memory-alloc.h`, `string-utils.h`, `syscalls.h`
- VDO/base: `encodings.h`, `status-codes.h`, `types.h`
- VDO helpers: `blockMapUtils.h`, `fileLayer.h`, `parseUtils.h`, `physicalLayer.h`, `userVDO.h`, `vdoVolumeUtils.h`

## Notable Behaviors and Risks

- Output size can be large; help estimates around 1.4 GB per TB of logical space for full metadata.
- The code does not unlink a partially written output file on failure.
- `freeAllocations()` syncs/closes output FD through `try_sync_and_close_file()`.
- `--lbn` count is bounded before incrementing because `lbnCount` is `uint8_t`.
<!-- END FILE RESEARCH: sources/block-storage/vdo/utils/vdo/vdodumpmetadata.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/vdo/utils/vdo/vdoforcerebuild.c -->
# File Research: sources/block-storage/vdo/utils/vdo/vdoforcerebuild.c

## Purpose

`vdoforcerebuild.c` implements `vdoforcerebuild`, a small metadata-mutating utility that marks an existing VDO device so it exits read-only mode and attempts metadata regeneration/rebuild.

## Command-Line Interface

Usage:

```text
vdoforcerebuild filename
```

Options documented:

- `--help`
- `--version`

## Main Flow

`main()`:

1. Registers VDO status codes.
2. Parses options.
3. Requires exactly one filename.
4. Creates a writable file layer with `makeFileLayer(filename, 0, &layer)`.
5. Calls `forceVDORebuild(layer)`.
6. Destroys the layer, syncing/closing the backing file.

## Dependencies

Includes:

- System: `err.h`, `getopt.h`, `stdio.h`, `stdlib.h`, `unistd.h`
- Utility: `errors.h`, `logger.h`
- VDO/base: `constants.h`, `status-codes.h`, `types.h`, `vdoConfig.h`
- VDO helper: `fileLayer.h`

## Notable Behaviors and Risks

- The `options` table includes `--version` mapped to `'V'`, but `optionString` is `"h"` and omits `V`. Long `--version` works through `getopt_long()`, but short `-V` is not accepted despite the handler.
- This tool writes metadata state. It does not use `makeVDOFromFile()` because it operates directly through the physical layer and `forceVDORebuild()`.
- Failure exits use status/result values through `errx()`.
<!-- END FILE RESEARCH: sources/block-storage/vdo/utils/vdo/vdoforcerebuild.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/vdo/utils/vdo/vdoformat.c -->
# File Research: sources/block-storage/vdo/utils/vdo/vdoformat.c

## Purpose

`vdoformat.c` implements `vdoformat`, the low-level formatter for VDO block devices. It validates the target block device, checks for existing signatures, prepares VDO and UDS index configuration, writes initial metadata through `formatVDO()`, verifies the formatted VDO, and prints capacity guidance.

## Command-Line Interface

Usage:

```text
vdoformat [options] filename
```

Options:

- `--force`
- `--help`
- `--logical-size=<size>`
- `--slab-bits=<bits>`
- `--uds-memory-size=<gigabytes>`
- `--uds-sparse`
- `--verbose`
- `--version`

Defaults:

- Logical size defaults inside formatting logic when `logicalSize == 0`.
- Slab bits default to `19`.

## Main Flow

`main()`:

1. Registers status codes.
2. Parses format parameters into `logicalSize`, `slabBits`, `UdsConfigStrings`, `verbose`, and `force`.
3. Requires exactly one target filename.
4. Stats the file and requires a block device.
5. Extracts major/minor and checks `/sys/dev/block/<major>:<minor>/holders` to ensure no active holders.
6. Opens the device read-write.
7. Uses `BLKGETSIZE64` to get physical byte size.
8. Rejects devices larger than `MAXIMUM_VDO_PHYSICAL_BLOCKS * VDO_BLOCK_SIZE`.
9. Closes the FD.
10. Builds `struct vdo_config`.
11. Validates logical size alignment and max logical block count.
12. Creates a `PhysicalLayer`.
13. Checks existing signatures using blkid, requiring `--force` if found.
14. Parses UDS index config.
15. Allocates a zero buffer and writes one block at block 1 to clear old UDS superblock state.
16. Calls `formatVDO(&config, &indexConfig, layer)`.
17. Handles common format errors with extra diagnostic help.
18. Loads the newly formatted VDO to verify it.
19. Prints capacity/growth information via `describeCapacity()`.
20. Frees VDO and destroys the layer.

## Existing Signature Detection

`checkForSignaturesUsingBlkid()`:

- Creates a blkid probe.
- Enables partition and superblock probing.
- Iterates detected signatures.
- Prints details using `printSignatureInfo()`.
- If signatures are found:
  - with `--force`: prints a warning and continues.
  - without `--force`: returns `EPERM`.

`printSignatureInfo()` reports offset, label, UUID, type, and usage where blkid exposes them.

## Device-In-Use Check

`checkDeviceInUse()` builds `/sys/dev/block/<major>:<minor>/holders` and counts entries using `countHolders()`.

It retries up to 25 times with 200 ms sleep, then fails if holders remain.

## Capacity Reporting

`describeCapacity()` prints:

- Whether logical blocks defaulted.
- Physical addressable size across current data slabs.
- Slab count and slab size.
- Maximum growable physical address space based on `MAX_VDO_SLABS`.
- Advice about choosing larger slabs when needed.

`printReadableSize()` handles human-ish B/KB/MB/GB/TB/PB display for these messages.

## Dependencies

Includes:

- System/library: `blkid/blkid.h`, `dirent.h`, `err.h`, `getopt.h`, `linux/fs.h`, `stdio.h`, `stdlib.h`, `unistd.h`, `sys/ioctl.h`, `sys/stat.h`, `sys/sysmacros.h`
- Utility: `errors.h`, `fileUtils.h`, `logger.h`, `string-utils.h`, `syscalls.h`, `time-utils.h`
- VDO/base: `constants.h`, `status-codes.h`, `types.h`, `vdoConfig.h`
- VDO helpers: `fileLayer.h`, `parseUtils.h`, `userVDO.h`, `vdoVolumeUtils.h`

## Notable Behaviors and Risks

- `optionString` includes an unused `i` option; there is no corresponding long option or switch case.
- `countHolders()` increments the caller’s holder count but does not reset it; `checkDeviceInUse()` calls it repeatedly with the same `holders` variable. If holders are present initially, this can accumulate counts across retries rather than observing a fresh count.
- The zero buffer allocated before clearing block 1 is not explicitly initialized in this file; correctness depends on the layer allocator returning zeroed memory or on external guarantees.
- The formatter only accepts block devices, not regular files.
- On `VDO_NO_SPACE`, it calculates and prints the minimum required VDO size.
<!-- END FILE RESEARCH: sources/block-storage/vdo/utils/vdo/vdoformat.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/vdo/utils/vdo/vdolistmetadata.c -->
# File Research: sources/block-storage/vdo/utils/vdo/vdolistmetadata.c

## Purpose

`vdolistmetadata.c` implements `vdoListMetadata`, a read-only utility that prints the ranges of VDO metadata regions on a backing device.

Each range is printed as:

```text
startBlock .. endBlock: label
```

The endpoints are inclusive 4 KiB VDO metadata block indexes.

## Command-Line Interface

Usage:

```text
vdoListMetadata <vdoBackingDevice>
```

Options:

- `--help`
- `--version`

## Main Flow

`main()`:

1. Registers status codes.
2. Parses arguments.
3. Loads the VDO without config validation using `readVDOWithoutValidation()`.
4. Lists:
   - geometry block
   - index
   - superblock
   - block map roots
   - per-slab reference blocks and journals
   - recovery journal
   - slab summary
5. Frees VDO and exits.

## Region Listing Functions

- `listGeometryBlock()`: block `0`, count `1`.
- `listIndex()`: blocks `1` through before data region start.
- `listSuperBlock()`: first block of data region.
- `listBlockMap()`: block map tree roots if `root_count > 0`.
- `listSlabs()`: for each slab, lists reference count blocks and slab journal blocks.
- `listRecoveryJournal()`: partition `VDO_RECOVERY_JOURNAL_PARTITION`.
- `listSlabSummary()`: partition `VDO_SLAB_SUMMARY_PARTITION`.

## Dependencies

Includes:

- System: `err.h`, `getopt.h`, `stdlib.h`
- Utility: `errors.h`, `string-utils.h`, `syscalls.h`
- VDO/base: `encodings.h`, `status-codes.h`, `types.h`
- VDO helpers: `userVDO.h`, `vdoVolumeUtils.h`

## Notable Behaviors and Risks

- Uses `readVDOWithoutValidation()`, so it can list metadata even if full config validation is undesirable.
- `listBlocks()` prints `physical_block_number_t` and `block_count_t` with `%ld`; this assumes those typedefs are compatible with `long` on the target platform.
- Per-slab label buffer is 64 bytes, sufficient for current labels and slab numbers.
<!-- END FILE RESEARCH: sources/block-storage/vdo/utils/vdo/vdolistmetadata.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/vdo/utils/vdo/vdoreadonly.c -->
# File Research: sources/block-storage/vdo/utils/vdo/vdoreadonly.c

## Purpose

`vdoreadonly.c` implements `vdoreadonly`, a small metadata-mutating utility that forces an existing VDO device into read-only mode.

## Command-Line Interface

Usage:

```text
vdoreadonly filename
```

Options documented:

- `--help`
- `--version`

## Main Flow

`main()`:

1. Registers status codes.
2. Parses options.
3. Requires exactly one filename.
4. Opens a writable file layer with `makeFileLayer(filename, 0, &layer)`.
5. Calls `setVDOReadOnlyMode(layer)`.
6. Destroys the layer to close and sync.

## Dependencies

Includes:

- System: `err.h`, `getopt.h`, `linux/fs.h`, `stdlib.h`, `sys/ioctl.h`
- Utility: `errors.h`, `fileUtils.h`, `logger.h`, `string-utils.h`
- VDO/base: `constants.h`, `status-codes.h`
- VDO helpers: `fileLayer.h`, `physicalLayer.h`, `vdoConfig.h`, `vdoVolumeUtils.h`

## Notable Behaviors and Risks

- As with `vdoforcerebuild.c`, the options table includes `--version`, but `optionString` is `"h"` and omits short `V`; long `--version` works, short `-V` likely does not.
- Several included headers are not directly used by this file but may reflect shared utility template usage.
- This tool intentionally writes metadata and should only be run against the intended backing device.
<!-- END FILE RESEARCH: sources/block-storage/vdo/utils/vdo/vdoreadonly.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/vdo/utils/vdo/vdorecover -->
# File Research: sources/block-storage/vdo/utils/vdo/vdorecover

## Purpose

`vdorecover` is a Bash recovery helper for running space reclamation against a VDO device that is full or otherwise needs controlled cleanup. It builds device-mapper snapshots under and above the VDO target, runs `fstrim` or prompts for manual deletion, then merges snapshot changes back.

## Command-Line Interface

Usage:

```text
./vdo_recover {path to vdo device}
```

It accepts `--help` or `-h`.

The script requires root (`EUID == 0`) and a running device-mapper target of type `vdo`.

## Main Flow

Top-level flow:

1. Read `VDO_DEVICE=$1`.
2. Validate argument and root privileges.
3. Iterate `dmsetup ls --target vdo`.
4. Match basename of supplied device path to VDO volume name.
5. Refuse to run if the VDO device appears mounted directly.
6. Install `_cleanup` trap.
7. Save original VDO dm table.
8. Run `_recoveryProcess`.
9. Clear trap and exit.

`_recoveryProcess()`:

1. Initializes `LOOPBACK_DIR`, defaulting to a temp dir.
2. Calls `_insertSnapUnderVDO`.
3. Calls `_addSnapAboveVDO`.
4. Calls `_repointUpperDevicesOrMountVDO`.
5. Merges data snapshot.
6. Merges backing snapshot.
7. Prints completion with final used percentage.

## Snapshot Operations

`_insertSnapUnderVDO()`:

- Extracts VDO backing device from VDO table.
- Replaces active VDO target temporarily with an error target.
- Creates a snapshot under the VDO backing.
- Reloads VDO to point at the under-VDO snapshot.

`_addSnapAboveVDO()`:

- Creates a snapshot over the VDO device itself.

`_snap()`:

- Creates `<device>-origin` as `snapshot-origin`.
- Creates a loopback COW file through `_mkloop()`.
- Creates `<device>-snap` as a `snapshot` target.

`_mergeSnapshot()`:

- Converts a snapshot table to `snapshot-merge`.
- Waits for merge to complete.
- Removes merge and snap devices.

## Reclaim and Manual Cleanup

`_fstrim()`:

- Checks snapshot status capacity.
- Runs `_fstrimAndPrompt()` when there is room in the snapshot.

`_fstrimAndPrompt()`:

- Runs `fstrim` if a mount point is provided.
- Reads VDO usage from `vdostats $VDO_VOLUME_NAME`.
- If usage remains `100`, prompts the user to delete files and continue.

`_repointUpperDevicesOrMountVDO()`:

- Detects devices depending on the VDO.
- If a dependent device exists:
  - Saves its original table.
  - Reloads it to point at the VDO snapshot.
  - Prompts/attempts trim through the dependent mount.
  - Restores the original table.
- Otherwise:
  - Mounts the VDO snapshot in a temp directory.
  - Runs fstrim.
  - Unmounts it.

## Cleanup

`_cleanup()` attempts to:

- Unmount temporary mount point.
- Restore dependent device table.
- Remove dm snapshot/merge/origin devices.
- Detach loop devices.
- Remove temporary loopback files.
- Disable then restore original VDO table if needed.

## Dependencies

External commands used include:

- `dmsetup`
- `blockdev`
- `losetup`
- `truncate`
- `df`
- `mktemp`
- `mount`
- `umount`
- `rmdir`
- `fstrim`
- `vdostats`
- `awk`, `grep`, `sed`, `cut`, `basename`, `rm`, `sleep`

## Notable Behaviors and Risks

- The script uses `set -e`, but many cleanup commands are guarded with `|| true`.
- There is a likely test bug in `_mkloop()`:
  ```bash
  if [[ TMPFS -lt LO_DEV_SIZE ]]; then
  ```
  This compares literal strings/empty variables rather than `$TMPFS` and `$LO_DEV_SIZE`.
- Temporary file size uses `truncate -s ${LO_DEV_SIZE}M`, while `LO_DEV_SIZE` is derived from sectors unless `TMPFILESZ` is supplied; units may be confusing.
- Parsing `dmsetup` output with whitespace-sensitive shell pipelines can be brittle for unusual names.
- The script is destructive if pointed at the wrong VDO target; it manipulates live dm tables and snapshots.
<!-- END FILE RESEARCH: sources/block-storage/vdo/utils/vdo/vdorecover -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/vdo/utils/vdo/vdostats.bash -->
# File Research: sources/block-storage/vdo/utils/vdo/vdostats.bash

## Purpose

`vdostats.bash` provides Bash completion for the `vdostats` command.

## Behavior

It defines `_vdostats()`:

1. Calls `_init_completion`.
2. Clears `COMPREPLY`.
3. Defines possible options:
   - `--help`
   - `--all`
   - `--human-readable`
   - `--si`
   - `--verbose`
   - `--version`
4. Uses `compgen -W` against the current word to populate completions.

It registers completion with:

```bash
complete -F _vdostats vdostats
```

## Dependencies

This completion assumes the standard Bash completion environment where `_init_completion` is available.

## Notable Behaviors and Risks

- The TODO notes that device-name completion is not implemented.
- Only long options are completed, even though `vdostats` also supports short options.
<!-- END FILE RESEARCH: sources/block-storage/vdo/utils/vdo/vdostats.bash -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/vdo/utils/vdo/vdostats.c -->
# File Research: sources/block-storage/vdo/utils/vdo/vdostats.c

## Purpose

`vdostats.c` implements `vdostats`, a command-line utility that queries running VDO device-mapper targets and displays configuration/statistics information.

It supports default `df`-style output and verbose aligned output through `vdo_write_stats()`.

## Command-Line Interface

Usage:

```text
vdostats [--help] [--version] [options...] [device [device ...]]
```

Options:

- `-h`, `--help`
- `-a`, `--all`: compatibility alias for verbose.
- `--human-readable`
- `--si`: SI units, implies human-readable.
- `-v`, `--verbose`
- `-V`, `--version`

If no devices are supplied, all running VDO devices are queried.

## Output Styles

`enum style`:

- `STYLE_DF`: default concise table.
- `STYLE_YAML`: verbose output.

Verbose is enabled by `-a` or `-v`, and causes each selected device to be printed as:

```text
<device> :
 <aligned verbose stats from vdo_write_stats()>
```

## Main Flow

`main()`:

1. Registers status codes.
2. Parses arguments.
3. Sets verbose style if requested.
4. Calls `enumerate_devices()` to list running VDO dm targets.
5. If no device arguments:
   - Calculates max display name length from all VDO target names.
   - Processes every VDO target.
6. If device arguments are present:
   - Calculates max display name length from argument basenames.
   - Resolves each argument through `transformDevice()`.
   - Processes matching devices.
7. Frees path array.

## Device Enumeration

`enumerate_devices()`:

1. Runs `dmsetup ls --target vdo` once to count lines.
2. Allocates `vdoPaths`.
3. Runs `dmsetup ls --target vdo` again.
4. Parses each line as:
   ```text
   name (major, minor)
   ```
5. Stores:
   - `name`
   - `resolvedName = dm-<minor>`
   - `resolvedPath = /dev/dm-<minor>`

## Device Resolution

`transformDevice()` matches user input against known VDO paths by:

- exact dmsetup target name
- resolved `dm-N` name
- `realpath()` result compared to `/dev/dm-N`

This allows callers to pass either target names or device paths.

## Stats Query

`process_device(original, name)`:

1. Builds command:
   ```c
   dmsetup message <name> 0 stats
   ```
2. Runs it with `popen()`.
3. Reads one stats line into `statsBuf[8192]`.
4. Calls `read_vdo_stats(statsBuf, &stats)`.
5. Displays according to current style:
   - `displayDFStyle()`
   - `vdo_write_stats()`
6. Checks `pclose()` status and fails if dmsetup returned nonzero.

## DF-Style Calculations

`getDFStats()` computes:

- `size = physical_blocks`
- `used = data_blocks_used + overhead_blocks_used`
- `available = size - used`
- `usedPercent = rounded used / size`
- `savingPercent = (logicalUsed - dataUsed) / logicalUsed`, or zero if no logical usage.

`displayDFStyle()` prints a header once, then rows with:

- Device
- Size or 1K-blocks
- Used
- Available
- Use%
- Space saving%

If `stats->in_recovery_mode`, used/available/percent/savings fields are printed as `N/A`.

Human-readable display uses `printSizeAsHumanReadable()`, with divisor `1024` by default or `1000` under `--si`.

## Dependencies

Includes:

- System: `linux/limits.h`, `err.h`, `errno.h`, `fcntl.h`, `getopt.h`, `libgen.h`, `stdio.h`, `stdlib.h`, `string.h`, `sys/stat.h`, `unistd.h`
- Utility/VDO: `errors.h`, `logger.h`, `memory-alloc.h`, `statistics.h`, `status-codes.h`, `vdoStats.h`

It depends on:

- `read_vdo_stats()` from the stats reader side.
- `vdo_write_stats()` from `vdoStatsWriter.c`.
- External `dmsetup`.

## Notable Behaviors and Risks

- `process_device()` builds a shell command with `sprintf(dmCommand, "dmsetup message %s 0 stats", name)`. Device names originate from `dmsetup` enumeration when valid, which mitigates but does not eliminate shell-command concerns.
- `statsBuf` is fixed at 8192 bytes; if the kernel stats message grows beyond one line or that size, parsing may truncate.
- `displayDFStyle()` uses `strdup(path)`, then `basename()`, and does not check `strdup()` failure.
- `enumerate_devices()` uses `getline()` but does not free `dmsetupLine`; process lifetime is short, but it is still a small leak.
- The output table width adapts to selected names through `maxDeviceNameLength`.
<!-- END FILE RESEARCH: sources/block-storage/vdo/utils/vdo/vdostats.c -->