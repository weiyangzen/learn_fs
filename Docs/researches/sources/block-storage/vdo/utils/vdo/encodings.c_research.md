# File Research: sources/block-storage/vdo/utils/vdo/encodings.c

Implements VDO userspace on-disk encoding, decoding, validation, layout construction, slab configuration, and checksum handling.

Key details:
- Defines current format headers for geometry v5.0, legacy geometry v4.0, block map v2.0, recovery journal v7.0, slab depot v2.0, layout v3.0, superblock v12.0, component data v41.0, and volume version v67.0.
- `vdo_parse_geometry_block()` validates magic `dmvdo001`, header version/size, geometry fields, and CRC32 checksum.
- `vdo_validate_block_map_page()` checks block-map page version 4.1, initialized flag, nonce, and expected PBN.
- Provides block-map forest sizing through `vdo_compute_new_forest_pages()`.
- Encodes/decodes recovery journal, slab depot, layout, VDO component, and complete component state payloads.
- `vdo_initialize_layout()` creates the fixed VDO partition layout: block map at the beginning, slab summary and recovery journal at the end, and slab depot in remaining space.
- `vdo_validate_config()` enforces slab size power-of-two constraints, journal constraints, physical/logical limits, and expected physical/logical sizes.
- `vdo_encode_super_block()` writes component data and checksum while asserting it fits in one sector to reduce torn-write exposure.

Risk notes:
- Version validation is strict; unsupported minor/major versions are rejected rather than upgraded in place.
- `decode_layout()` checks required partitions and total coverage by summing partition counts, but partition linked-list order is allocation order and not necessarily disk order.
