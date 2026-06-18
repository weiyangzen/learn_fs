# File Research: sources/block-storage/vdo/utils/vdo/userVDO.c

Implements lifecycle, loading, saving, and slab-address helpers for user-space VDO objects.

Key details:
- `makeUserVDO()` wraps a `PhysicalLayer` in a heap-allocated `UserVDO`.
- `freeUserVDO()` destroys decoded component state allocations and frees the wrapper.
- `loadVolumeGeometry()` reads block 0 and parses geometry.
- `loadVDOWithGeometry()` reads the superblock at the geometry data-region start, decodes component states, optionally validates config/nonce/size, then computes derived slab fields.
- `writeVolumeGeometryWithVersion()` encodes magic, geometry, checksum, and writes block 0.
- `saveSuperBlock()` and `saveVDO()` write encoded superblock and optional geometry.
- `getSlabNumber()`, `getSlabBlockNumber()`, and `isValidDataBlock()` validate PBNs against slab depot boundaries and data-block area.

Risk notes:
- `getPartition()` calls `errx(1, ...)` on missing partition, so callers using it opt into process exit rather than recoverable error handling.
