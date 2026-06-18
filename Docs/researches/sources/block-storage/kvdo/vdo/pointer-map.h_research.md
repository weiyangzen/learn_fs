# File Research: sources/block-storage/kvdo/vdo/pointer-map.h

## Purpose
Declares the opaque pointer map interface and key callback contracts.

## Callback Contracts
- `pointer_key_comparator`: determines equality of key referents.
- `pointer_key_hasher`: returns a stable, uniformly distributed 32-bit hash for a key while stored.

## API Surface
- `make_pointer_map`
- `free_pointer_map`
- `pointer_map_size`
- `pointer_map_get`
- `pointer_map_put`
- `pointer_map_remove`

## Ownership Model
The map retains key/value pointer values but does not own the referenced memory. NULL values are unsupported. NULL keys are allowed only if the caller’s comparator and hasher support them.

## Integration Notes
Designed for constant-time lookup/update/remove in common cases, with occasional expensive resize on insertion.
