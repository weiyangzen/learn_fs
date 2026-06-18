# sources/distributed-fs/ceph-client/drivers/md/dm-vdo/encodings.h

## Purpose
`encodings.h` is the shared contract for VDO's persistent metadata formats and the inline helpers that translate between native in-memory structures and packed, little-endian, on-disk representations. It covers volume geometry, block-map entries and pages, recovery journal blocks and entries, slab journal/reference-count formats, slab summary entries, layout/superblock component state, and CRC helpers.

## Important APIs, Types, And Functions
- Versioning and component headers: `struct version_number`, `struct packed_version_number`, `struct header`, `struct packed_header`, `vdo_pack_version_number()`, `vdo_unpack_version_number()`, `vdo_pack_header()`, and `vdo_unpack_header()`. Component IDs include `VDO_SUPER_BLOCK`, `VDO_LAYOUT`, `VDO_RECOVERY_JOURNAL`, `VDO_SLAB_DEPOT`, `VDO_BLOCK_MAP`, and `VDO_GEOMETRY_BLOCK`.
- Geometry: `struct volume_geometry`, `struct volume_region`, `struct index_config`, `vdo_initialize_volume_geometry()`, `vdo_encode_volume_geometry()`, `vdo_parse_geometry_block()`, `vdo_get_index_region_start()`, `vdo_get_data_region_start()`, and `vdo_get_index_region_size()`.
- Block map: `struct block_map_entry`, `struct block_map_page`, `vdo_pack_block_map_entry()`, `vdo_unpack_block_map_entry()`, `vdo_is_valid_location()`, `vdo_format_block_map_page()`, `vdo_validate_block_map_page()`, `vdo_compute_block_map_page_count()`, and `vdo_compute_new_forest_pages()`.
- Recovery journal: `struct recovery_journal_entry`, `struct packed_recovery_journal_entry`, v1 compatibility entry structures, `struct recovery_block_header`, `struct packed_journal_header`, `struct packed_journal_sector`, `vdo_pack_recovery_journal_entry()`, `vdo_unpack_recovery_journal_entry()`, `vdo_pack_recovery_block_header()`, `vdo_unpack_recovery_block_header()`, `vdo_is_valid_recovery_journal_sector()`, and `vdo_compute_recovery_journal_block_number()`.
- Slab/refcount metadata: `vdo_refcount_t`, `struct packed_reference_sector`, `struct packed_reference_block`, `struct slab_depot_state_2_0`, `struct slab_journal_entry`, `packed_slab_journal_entry`, `struct packed_slab_journal_block`, `vdo_pack_slab_journal_entry()`, `vdo_unpack_slab_journal_entry()`, `vdo_decode_slab_journal_entry()`, `vdo_get_saved_reference_count_size()`, and `vdo_get_slab_journal_start_block()`.
- Layout and superblock: `struct layout`, `struct partition`, `struct vdo_config`, `struct vdo_component`, `struct vdo_component_states`, `vdo_initialize_layout()`, `vdo_validate_config()`, `vdo_decode_component_states()`, `vdo_validate_component_states()`, `vdo_encode_super_block()`, `vdo_decode_super_block()`, and `vdo_initialize_component_states()`.

## Control Flow And Data Flow
Most helpers are one-step pack/unpack routines. Callers construct native metadata state, invoke a pack helper to produce a packed structure or block, then write it through the VDO I/O path. Reads reverse that path: packed bytes are validated, converted to native values, and then passed to higher-level block map, slab depot, journal, or superblock logic. Journal helpers preserve sequence/entry ordering through `struct journal_point`, with `vdo_advance_journal_point()` and `vdo_before_journal_point()` used by recovery and slab journal code.

Bitfield-heavy structures encode constrained fields into compact records. A block-map entry stores 36 PBN bits plus a 4-bit mapping state in five bytes. Recovery journal entries combine a block-map slot, operation, mapping, and unmapping. Slab journal entries use a 23-bit slab-block offset and a one-bit increment flag, with an alternate payload layout when block-map increments are present.

## State And Persistence Behavior
This file defines persistent VDO compatibility. Packed structures use fixed-width little-endian fields and `__packed` layout so metadata remains machine independent. The declared version constants and encoded-size constants act as hard gates for decoding old formats and laying out superblock component data. Compatibility-sensitive fields such as `volume_geometry_4_0`, recovery journal v1 entries, layout 3.0 structures, and `packed_vdo_component_41_0` preserve older on-disk formats.

Persistent risk centers on exact field sizes. The 36-bit PBN encodings cap physical addressability, `packed_journal_point` assumes the top 16 sequence bits are zero, and many size constants are derived from VDO block/sector sizes. Any change here changes on-disk metadata and must be paired with versioning and upgrade logic.

## Dependencies And Integration Points
The header depends on Linux endian/CRC/UUID/block types plus VDO `constants.h`, `types.h`, and `numeric.h`. Implementations live mainly in `encodings.c`, while callers are spread across `vdo.c`, `dm-vdo-target.c`, `block-map.c`, `slab-depot.c`, and recovery journal code. Index geometry stored inside `struct volume_geometry` connects the VDO metadata area to the UDS indexer.

## Risks
- Bitfields depend on explicit byte-order branches; build coverage must include supported endian assumptions.
- The journal and block-map encodings rely on masked values fitting in narrow fields; missing validation before packing can silently truncate.
- Persistent size constants are cross-component contracts; accidental structure padding or enum-size assumptions would corrupt metadata.
- `vdo_is_valid_location()` treats zero-block mappings specially, so compression-state validation must stay aligned with block-map semantics.

## Test Signals
Useful tests include pack/unpack round trips for every packed structure, block-map entry tests around PBN values near 32-bit and 36-bit boundaries, recovery journal sector validation for v1/v2 metadata, superblock decode/encode compatibility fixtures, and CRC/geometry-block corruption tests. Kernel integration signals are successful VDO creation, load, suspend/resume, recovery replay, and metadata validation on existing volumes.
