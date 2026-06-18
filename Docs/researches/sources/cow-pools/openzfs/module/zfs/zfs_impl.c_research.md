# File Research: sources/cow-pools/openzfs/module/zfs/zfs_impl.c

## Summary
Provides a small registry for checksum/hash implementation backends.

## Main Responsibilities
- Defines the available implementation backend operation tables.
- Returns backend operations by algorithm name.

## Key APIs
- `zfs_impl_get_ops()`

## Important Behavior
The registry currently contains BLAKE3, SHA-256, and SHA-512 operation tables. Passing a null or empty algorithm name returns the first registered backend. Otherwise, lookup compares against each backend’s `name`.

## Risks
The function asserts on lookup assumptions and returns the matched pointer, or the terminating entry if the name is unknown. Callers are expected to request known algorithm names.
