# File Research: sources/block-storage/kvdo/vdo/volume-index006.h

## Purpose
Declares the constructor and save-size API for the sparse+dense volume index 006 implementation.

## Public API
- `make_volume_index006(const struct configuration *config, uint64_t volume_nonce, struct volume_index **volume_index)`: creates a 006 wrapper index.
- `compute_volume_index_save_bytes006(const struct configuration *config, size_t *num_bytes)`: computes persisted byte size for a 006 index.

## Dependencies
Includes `volume-index-ops.h`, exposing the common abstract volume-index interface.

## Notes
The 006 implementation is version-specific at construction time but presents the same `struct volume_index` vtable interface to callers.
