# sources/control-plane/mayastor/io-engine/src/core/partition.rs

## Purpose
Calculates fixed partition layout offsets for reserving GPT and io-engine metadata space before the user data partition.

## Important APIs, Types, and Functions
- `GPT_TABLE_SIZE`, `METADATA_RESERVATION_OFFSET`, `METADATA_RESERVATION_SIZE`, and `DATA_PARTITION_OFFSET` define layout constants.
- `calc_data_partition(req_size, num_blocks, block_size)` returns `(data_start, data_end, req_blocks)` in blocks.
- `bytes_to_alinged_blocks(size, block_size)` rounds byte sizes up to block counts.

## Control Flow and State
`calc_data_partition` computes GPT table blocks, metadata start, last usable block before backup GPT, metadata blocks, and data start. If the device cannot fit metadata reservation before the usable end, it returns `None`. It then rounds requested size to blocks and caps the data end at the last usable block.

There is no state or persistence here; the returned offsets are consumed by bdev/pool layout code.

## Dependencies and Integration Points
Used by nexus/bdev layout paths that create or expose data partitions while reserving metadata space.

## Risks and Test Signals
The function assumes `num_blocks` is large enough for `gpt_blocks + 2`; otherwise unsigned subtraction can underflow in debug builds and wrap in release if not optimized with checks. `block_size` must be nonzero. The helper name contains a typo (`alinged`). Tests should cover tiny devices, non-divisible block sizes, exact metadata fit, oversized requested data, and zero block-size rejection by callers.
