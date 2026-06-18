# File Research: sources/block-storage/vdo/utils/vdo/vdoConfig.c

Implements VDO formatting, minimum-size calculation, geometry initialization, partition clearing, and offline state changes.

Key details:
- `initializeLayoutFromConfig()` creates the default layout with block-map roots, recovery journal, slab summary, and slab depot.
- `configureRecoveryJournal()` starts journal sequence at `1` with zero logical and block-map usage.
- `configureVDO()` initializes layout, slab config/depot, derived slab params, auto logical size when unset, block-map state, and `VDO_NEW` state.
- `calculateMinimumVDOFromConfig()` computes fixed metadata size plus one slab.
- `computeIndexBlocks()` asks UDS for index size and requires a multiple of VDO block size.
- `initializeVolumeGeometry()` places index region at block 1 and data region after the index.
- `formatVDOWithNonce()` registers status codes, validates config, creates `UserVDO`, configures metadata, clears block-map and recovery-journal partitions, and saves geometry/superblock.
- `forceVDORebuild()` and `setVDOReadOnlyMode()` update inactive superblock state.

Risk notes:
- `configureAndWriteVDO()` writes an allocated geometry block before encoding it later via `saveVDO()`, so the first write appears to be a placeholder/zeroing step.
- `clearPartition()` chooses a power-of-two buffer size based on partition size divisibility, up to 4096 blocks.
