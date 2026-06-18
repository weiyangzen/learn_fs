# File Research: sources/block-storage/kvdo/vdo/volume-geometry.c

## Purpose
Reads, decodes, validates, and checksums the on-disk VDO geometry block at block 0.

## On-Disk Format
- Magic number: `dmvdo001`.
- Header ID: `VDO_GEOMETRY_BLOCK`.
- Supported geometry block versions:
  - 4.0: no `bio_offset` in `volume_geometry`.
  - 5.0: includes `bio_offset`.
- Payload includes release version, nonce, UUID, volume regions, and index config.
- CRC32 covers all decoded bytes before the checksum field.

## Key Functions
- `is_loadable_release_version()` accepts current release plus compatible Magnesium and Aluminum releases.
- `decode_index_config()` decodes UDS index memory size and sparse flag, skipping an unused field.
- `decode_volume_region()` decodes region ID and start block.
- `decode_volume_geometry()` decodes version-dependent geometry fields.
- `decode_geometry_block()` checks magic, decodes and validates header, decodes geometry, and asserts position before checksum.
- `vdo_parse_geometry_block()` verifies checksum and release compatibility.
- `vdo_read_geometry_block()` synchronously reads block 0 from a block device and parses it.

## Important Behavior
- Version 4 geometries default `bio_offset` to zero.
- Header `size` is unusual: it includes the geometry block header and payload, not just payload.
- Synchronous read errors are logged and returned as `-EIO`.
- Unsupported release versions return `VDO_UNSUPPORTED_VERSION`.
- Checksum mismatch returns `VDO_CHECKSUM_MISMATCH`.
