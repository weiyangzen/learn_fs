# File Research: sources/block-storage/vdo/utils/vdo/encodings.h

Defines VDO’s userspace-visible on-disk structures and inline packing/unpacking helpers.

Key details:
- Declares versioned headers, geometry blocks, volume regions, index config, block-map entries/pages, recovery journal formats, reference count sectors, slab journal blocks, slab summary entries, layout partitions, VDO config, VDO component state, and aggregate component states.
- Block-map entries are five-byte packed records containing a 36-bit PBN and four-bit mapping state.
- Recovery journal entries encode a block-map slot plus mapping/unmapping locations.
- Slab journal supports compact data-only entries and fuller entries with block-map increment type bitmap.
- Provides endian-safe inline helpers for versions, headers, block-map entries, recovery headers, journal points, slab journal entries, and geometry region starts.
- Declares all major encode/decode/validate functions implemented by `encodings.c`.

Research relevance:
- This is the central format contract for VDO userspace tools; persisted enum values and packed structures must stay stable.
