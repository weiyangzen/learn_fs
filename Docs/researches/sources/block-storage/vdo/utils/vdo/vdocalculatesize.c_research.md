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
