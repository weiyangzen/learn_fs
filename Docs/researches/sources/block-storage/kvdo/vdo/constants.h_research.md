# File Research: sources/block-storage/kvdo/vdo/constants.h

## Purpose
Defines global VDO sizing, layout, queueing, journal, and block constants.

## Key Constants
- Block map:
  - `VDO_BLOCK_MAP_ENTRIES_PER_PAGE = 812`
  - `VDO_BLOCK_MAP_TREE_HEIGHT = 5`
  - `DEFAULT_VDO_BLOCK_MAP_TREE_ROOT_COUNT = 60`
- Bio submission:
  - `DEFAULT_VDO_BIO_SUBMIT_QUEUE_COUNT = 4`
  - `DEFAULT_VDO_BIO_SUBMIT_QUEUE_ROTATE_INTERVAL = 64`
  - `VDO_BIO_ROTATION_INTERVAL_LIMIT = 1024`
- Journals:
  - `DEFAULT_VDO_RECOVERY_JOURNAL_SIZE = 32 * 1024`
  - `DEFAULT_VDO_SLAB_JOURNAL_SIZE = 224`
  - `VDO_RECOVERY_JOURNAL_TAIL_BUFFER_SIZE = 64`
- Limits:
  - `MAX_VDO_LOGICAL_ZONES = 60`
  - `MAX_VDO_PHYSICAL_ZONES = 16`
  - `MAX_VDO_SLAB_BITS = 23`
  - `MAX_VDO_SLABS = 8192`
  - `MAXIMUM_VDO_THREADS = 100`
  - `MAXIMUM_VDO_USER_VIOS = 2048`
- Block geometry:
  - `VDO_BLOCK_SIZE = 4096`
  - `VDO_SECTORS_PER_BLOCK = VDO_BLOCK_SIZE >> SECTOR_SHIFT`
  - `VDO_SECTOR_SIZE = 512`
  - `VDO_ZERO_BLOCK = 0`

## External Constants
Declares logical/physical maximums and minimum slab journal blocks defined in `constants.c`.

## Research Notes
This file supplies shared assumptions used across pool sizing, hash lock capacity, block map layout, and I/O alignment.
