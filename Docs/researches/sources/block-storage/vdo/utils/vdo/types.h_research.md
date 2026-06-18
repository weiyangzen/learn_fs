# File Research: sources/block-storage/vdo/utils/vdo/types.h

Defines core scalar aliases and persisted enums for VDO userspace metadata handling.

Key details:
- Provides aliases for block counts, block sizes, logical/physical block numbers, nonces, pages, roots, slabs, slots, threads, zones, and sequence numbers.
- Defines persisted `enum vdo_state` and helpers for read-only rebuild and recovery-required states.
- Defines persisted journal operation, partition ID, metadata type, block-map slot, and block-mapping-state values.
- Defines `struct data_location` and packed `struct slab_config`.

Research relevance:
- Many enum values are persisted on disk, so compatibility depends on preserving numeric values and packing.
