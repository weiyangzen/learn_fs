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
