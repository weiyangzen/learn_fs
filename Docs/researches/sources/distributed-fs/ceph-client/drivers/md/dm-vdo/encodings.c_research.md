# sources/distributed-fs/ceph-client/drivers/md/dm-vdo/encodings.c

## Purpose
Implements VDO's machine-independent on-disk metadata encoders, decoders, validators, and initializers. It covers geometry blocks, super block headers and component payloads, layout partitions, block-map state and pages, recovery-journal state and journal entries, slab-depot state and slab sizing, and volume geometry initialization. The file is the compatibility boundary between in-memory VDO structures and persistent metadata.

## Important APIs, Types, And Functions
Version and header constants define the accepted formats: geometry block versions 4.0 and 5.0, block-map header 2.0, recovery-journal header 7.0, slab-depot header 2.0, layout header 3.0, VDO component data 41.0, volume version 67.0, and super block header 12.0. `VDO_GEOMETRY_MAGIC_NUMBER` is `"dmvdo001"`.

Geometry APIs are `vdo_initialize_volume_geometry()`, `vdo_encode_volume_geometry()`, and `vdo_parse_geometry_block()`. Super block/component APIs are `vdo_initialize_component_states()`, `vdo_encode_super_block()`, `vdo_decode_super_block()`, `vdo_decode_component_states()`, `vdo_validate_component_states()`, `vdo_validate_config()`, and `vdo_destroy_component_states()`.

Layout APIs are `vdo_initialize_layout()`, `vdo_uninitialize_layout()`, `vdo_get_partition()`, and `vdo_get_known_partition()`. Slab APIs are `vdo_configure_slab()`, `vdo_configure_slab_depot()`, and `vdo_decode_slab_journal_entry()`. Block-map APIs are `vdo_format_block_map_page()`, `vdo_validate_block_map_page()`, and `vdo_compute_new_forest_pages()`. `vdo_get_journal_operation_name()` names recovery-journal operation codes.

The low-level helpers use packed structs and explicit little-endian encode/decode functions to avoid host-endian or alignment-dependent disk formats.

## Control Flow
Formatting starts with `vdo_initialize_volume_geometry()`, which asks UDS for the index size, places the index region at block 1, places the data region after the index, copies UUID/index settings, and sets the nonce. `vdo_initialize_component_states()` initializes the VDO config, volume version, recovery journal start, layout beginning one block after the data region start, slab depot state, block map root state, and `VDO_NEW` state.

Writing metadata calls `vdo_encode_volume_geometry()` for geometry and `vdo_encode_super_block()` for super block data. Geometry writes magic, header, fields, region table, index config, and CRC. Super block writes header, fixed component data in a strict order, and CRC, with an assertion that the whole encoding fits in one sector to reduce torn-write exposure.

Loading first calls `vdo_parse_geometry_block()` to validate magic, versioned header, and checksum. `vdo_decode_super_block()` validates the super block header and checksum without decoding all component content. Then `vdo_decode_component_states()` starts at `VDO_COMPONENT_DATA_OFFSET`, validates volume version, and decodes VDO component, layout, recovery journal, slab depot, and block map state. `vdo_validate_component_states()` checks the geometry/superblock nonce match and delegates config validation.

Layout creation carves block-map space from the beginning, slab summary and recovery journal from the end, and gives all remaining middle space to the slab depot. Layout decoding validates partition count and required partition presence, then checks partition coverage.

## State And Persistence
Everything this file encodes is persistent metadata. Geometry stores nonce, UUID, bio offset, index/data region starts, and index memory/sparse settings. The super block stores volume version, VDO state/config, layout, recovery-journal state, slab-depot state, and block-map state. CRCs protect geometry and super block payloads. Version checks reject unsupported incompatible formats rather than attempting partial interpretation.

The file also defines derived persistent layout decisions: slab journal thresholds, reference count block counts, depot first/last blocks, root origin/count, and recovery journal initial sequence.

## Dependencies And Integration Points
It depends on Linux CRC, UUID, log2 helpers, VDO constants/types/numeric packing helpers, logger, memory allocation, assertions, and UDS index-size computation. It integrates with `dm-vdo-target.c` during format/load/grow, with block map code for page formatting/validation and forest growth, with recovery journal code for persisted journal state and entry decoding, with slab depot code for depot configuration, and with UDS for index region sizing.

## Risks
On-disk compatibility is the main risk. Any size, version, field order, endian conversion, or packed-struct change can make existing VDO volumes unloadable or silently misdecoded. `vdo_validate_header()` allows minimum-size validation for variable layouts and exact-size validation for fixed components; using the wrong mode can reject valid metadata or accept malformed data.

Layout validation is subtle. Decoding currently sums required partition counts from `start` and expects that to equal `size`; this assumes exactly the required partitions cover the layout. Duplicate partition IDs, overlapping partitions, or inconsistent free ranges are areas to scrutinize when changing the decoder.

The super block checksum verification skips component decoding until later, so callers must always follow `vdo_decode_super_block()` with `vdo_decode_component_states()` and validation before trusting state. Geometry version 4 compatibility omits `bio_offset`, so mixed-version behavior depends on defaulting that field to zero.

## Test Signals
Tests should round-trip geometry and super block encodings on little- and big-endian builds if possible, inject bad magic/version/size/checksum/nonce values, load version 4 and version 5 geometry blocks, validate boundary slab sizes and journal sizes, verify layout partition coverage and missing/extra partitions, and compare block-map page validity for wrong nonce, uninitialized page, and wrong PBN. Growth tests should verify `vdo_compute_new_forest_pages()` and layout initialization with small and maximum physical sizes.
