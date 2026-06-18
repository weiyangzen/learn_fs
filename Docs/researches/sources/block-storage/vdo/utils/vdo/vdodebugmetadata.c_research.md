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
