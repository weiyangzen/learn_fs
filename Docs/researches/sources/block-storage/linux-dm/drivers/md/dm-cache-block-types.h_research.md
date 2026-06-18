# File Research: sources/block-storage/linux-dm/drivers/md/dm-cache-block-types.h

Defines sparse-distinct block identifier types for cache code: `dm_oblock_t` for origin blocks, `dm_cblock_t` for cache blocks, and `dm_dblock_t` for discard bitset blocks.

The inline conversion helpers use `__force` casts to move between raw integer/block types and the annotated types. This lets sparse catch accidental mixing of origin, cache, and discard indexes.

The file depends on persistent-data `dm_block_t` and keeps the type layer small and header-only.
