# sources/distributed-fs/ceph-client/drivers/md/dm-cache-block-types.h

## Purpose
`dm-cache-block-types.h` creates sparse-distinct integer types for cache metadata block domains: origin blocks, cache blocks, and discard-bitset blocks. This prevents accidental mixing of indexes that have different meanings.

## Important APIs, Types, and Functions
The header typedefs `dm_oblock_t`, `dm_cblock_t`, and `dm_dblock_t` as `__bitwise` wrappers over `dm_block_t` or `uint32_t`. Conversion helpers are `to_oblock()`, `from_oblock()`, `to_cblock()`, `from_cblock()`, `to_dblock()`, and `from_dblock()`.

## Control Flow
There is no runtime control flow beyond inline casts. Callers explicitly convert at API boundaries, arithmetic sites, and persistent encoding/decoding points.

## State and Persistence
No state is stored here. The type choices affect persistence because metadata packing stores origin blocks, cache blocks, and discard blocks using the correct converted integer widths.

## Dependencies and Integration Points
It includes the persistent-data block manager for `dm_block_t`. It is included by cache metadata and policy headers, making the typed block aliases part of the cache target's internal ABI.

## Risks and Edge Cases
`dm_cblock_t` is backed by `uint32_t`, so cache block counts and indexes must fit that width. The `__force` conversions are intentionally explicit; overusing them can bypass sparse's protection and hide domain errors.

## Test Signals
Sparse builds should catch accidental assignment between block domains. Functional signals include correct mapping load/insert/remove behavior when origin, cache, and discard indexes differ substantially.
