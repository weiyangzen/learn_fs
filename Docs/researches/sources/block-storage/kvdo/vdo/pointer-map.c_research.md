# File Research: sources/block-storage/kvdo/vdo/pointer-map.c

## Purpose
Implements a generic pointer-key to pointer-value hash map using Hopscotch hashing without the algorithm’s concurrency features.

## Data Model
- `struct bucket`: packed `first_hop`, `next_hop`, key, and value.
- `struct pointer_map`: size, capacity, bucket count, bucket array, comparator, and hasher.
- Neighborhood size is 255; hop offsets are biased by one so zero means NULL.

## Key Operations
- `make_pointer_map`: allocates map and bucket array sized by requested capacity/load.
- `free_pointer_map`: frees map storage but not keys/values.
- `pointer_map_size`
- `pointer_map_get`
- `pointer_map_put`
- `pointer_map_remove`

## Hashing / Placement
`select_bucket` scales a 32-bit hash into `[0, capacity)` with `(hash * capacity) >> 32`, avoiding modulo division. Entries that hash to a bucket must live within that bucket’s 255-entry neighborhood.

## Collision Resolution
- `find_empty_bucket` linearly probes for a vacancy.
- `move_empty_bucket` relocates entries from enclosing neighborhoods to move a hole closer.
- `find_or_make_vacancy` repeats relocation until the hole is within the target neighborhood.
- If this fails, `resize_buckets` grows capacity by 1.5x and rehashes all entries.

## Update / Removal
`pointer_map_put` rejects NULL values. Existing mappings can be returned and optionally updated. Removal clears the bucket and splices it out of the hop list.

## Integration Notes
The map does not own keys or values. The header explicitly assumes keys are either part of values, unmanaged, or safe to forget when replaced.
