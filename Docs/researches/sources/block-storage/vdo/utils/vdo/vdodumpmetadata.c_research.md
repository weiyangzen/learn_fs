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
