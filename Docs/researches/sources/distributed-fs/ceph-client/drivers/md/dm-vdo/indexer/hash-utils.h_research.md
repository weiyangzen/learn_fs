# sources/distributed-fs/ceph-client/drivers/md/dm-vdo/indexer/hash-utils.h

## Purpose
`hash-utils.h` provides inline helpers that partition a 16-byte UDS record name into fields used by the volume index, chapter index, and sparse sampling logic.

## Important APIs, Types, And Functions
- Byte layout constants divide the name into volume-index bytes `[0..7]`, chapter-index bytes `[8..13]`, and sampling bytes `[14..15]`.
- `uds_extract_chapter_index_bytes()` reads six bytes as a 48-bit big-endian value.
- `uds_extract_volume_index_bytes()` reads eight big-endian bytes for volume-index addressing.
- `uds_extract_sampling_bytes()` reads two big-endian bytes for sampling.
- `uds_hash_to_chapter_delta_list()` computes the chapter delta-list number from high address bits.
- `uds_hash_to_chapter_delta_address()` computes the chapter-list address from low address bits.
- `uds_name_to_hash_slot()` maps chapter-index bytes modulo a caller-provided slot count.

## Control Flow And Data Flow
Record names are treated as already-hashed names. Callers extract deterministic slices for different index structures. Chapter-index insertion/search uses geometry-derived `chapter_address_bits` and `chapter_delta_list_bits` so each name maps to one list and one address within that list.

## State And Persistence Behavior
The header has no mutable state. Its byte partitioning is a persistent compatibility contract because it determines how record names are placed in saved volume and chapter indexes.

## Dependencies And Integration Points
It depends on unaligned numeric access, `geometry.h`, and `indexer.h`. It is used by chapter-index, volume-index, sparse-cache, and other index lookup paths.

## Risks
- Any change to byte offsets/counts breaks lookup compatibility with existing indexes.
- Big-endian extraction is intentional even though many on-disk structures are little-endian; changing it would remap every record name.
- Geometry bit counts must keep masks within valid shift widths.
- `uds_name_to_hash_slot()` assumes `slot_count` is nonzero.

## Test Signals
Tests should use fixed 16-byte names to verify extracted volume/chapter/sample values, list/address mapping for several geometries, modulo slot mapping, and sparse-sampling decisions in callers.
