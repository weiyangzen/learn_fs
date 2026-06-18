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
