# File Research: sources/block-storage/kvdo/vdo/header.h

## Purpose
Defines version-number and generic component-header formats used by VDO on-disk data.

## Main Contents
- `struct version_number`: native major/minor version.
- `struct packed_version_number`: little-endian on-disk version.
- Component IDs for super block, fixed layout, recovery journal, slab depot, block map, and geometry block.
- `struct header`: component id, version, and data size.
- `VDO_ENCODED_HEADER_SIZE`.

## API and Inline Helpers
- Version equality/upgradability predicates.
- Header/version encode/decode/validate declarations.
- `vdo_pack_version_number()` and `vdo_unpack_version_number()` convert between native and little-endian packed form.

## Integration
Used by persistent metadata components to identify format, size, and version compatibility.
