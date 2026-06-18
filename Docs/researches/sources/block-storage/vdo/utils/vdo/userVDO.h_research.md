# File Research: sources/block-storage/vdo/utils/vdo/userVDO.h

Declares the `UserVDO` aggregate and its load/save/address helper API.

Key details:
- `UserVDO` contains the physical layer, volume geometry, one-block superblock buffer, decoded component states, and derived slab parameters.
- Declares construction/destruction, geometry loading, superblock loading, full VDO loading, geometry writing, superblock saving, full saving, slab parameter derivation, slab/PBN lookups, data-block validation, and partition lookup.
- Provides inline `writeVolumeGeometry()` using `VDO_DEFAULT_GEOMETRY_BLOCK_VERSION`.

Research relevance:
- This is the high-level object most VDO utilities use after opening a physical layer.
