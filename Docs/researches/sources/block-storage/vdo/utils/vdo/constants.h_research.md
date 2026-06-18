# File Research: sources/block-storage/vdo/utils/vdo/constants.h

Central constant set for userspace VDO metadata and configuration limits.

Key details:
- Defines block geometry: `VDO_BLOCK_SIZE = 4096`, `VDO_SECTOR_SIZE = 512`, `VDO_SECTORS_PER_BLOCK = 8`, and `VDO_ZERO_BLOCK = 0`.
- Defines block-map shape: `VDO_BLOCK_MAP_ENTRIES_PER_PAGE = 812`, tree height `5`, flat origin `1`, and default root count `60`.
- Defines journal defaults: recovery journal `32 * 1024` blocks, slab journal `224` blocks, minimum slab journal `2` blocks.
- Defines maximums for zones, slab bits, slabs, simultaneous restoration reads, threads, and user VIOs.

Research relevance:
- These constants anchor almost every format calculation in `encodings.c`, `vdoConfig.c`, and block-map traversal.
