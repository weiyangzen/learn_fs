# File Research: sources/block-storage/kvdo/vdo/volume-index005.h

## Purpose
Declares the constructor and save-size API for the dense volume index 005 implementation.

## Public API
- `make_volume_index005(const struct configuration *config, uint64_t volume_nonce, struct volume_index **volume_index)`: creates a concrete 005 volume index.
- `compute_volume_index_save_bytes005(const struct configuration *config, size_t *num_bytes)`: computes persisted byte size for a 005 index under the supplied configuration.

## Dependencies
Includes `volume-index-ops.h`, so callers see the abstract `struct volume_index` API and related types.

## Notes
This header exposes version-specific creation/sizing only. Runtime operations are performed through the common vtable interface in `volume-index-ops.h`.
