# File Research: sources/block-storage/kvdo/vdo/physical-zone.h

## Purpose
Declares physical-zone structures and operations.

## Key Structures
- `struct physical_zone`: zone number, callback thread id, PBN operation map, PBN lock pool, block allocator, and next-zone pointer.
- `struct physical_zones`: flexible array container.

## API Surface
Construction/destruction, lock lookup/acquire/release, zone allocation, and diagnostic dump functions.

## Integration Notes
Physical zones are the per-thread/per-allocator partition for physical block operations. The `next` pointer supports ring traversal during allocation retries.
