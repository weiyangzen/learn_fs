# File Research: sources/block-storage/kvdo/vdo/volume-geometry.h

## Purpose
Defines VDO geometry structures and helpers for locating index/data regions.

## Key Types
- `struct index_config`: UDS memory setting, unused field, and sparse flag.
- `enum volume_region_id`: index region and data region IDs.
- `struct volume_region`: region ID plus absolute start block.
- `struct volume_geometry`: release version, nonce, UUID, bio offset, regions, and index config.
- `struct volume_geometry_4_0`: legacy sizing-only geometry without bio offset.

## Public API
- `vdo_get_index_region_start()`
- `vdo_get_data_region_start()`
- `vdo_get_index_region_size()`
- `vdo_read_geometry_block()`

## Important Constant
- `VDO_GEOMETRY_BLOCK_LOCATION = 0`
