# File Research: sources/block-storage/kvdo/vdo/vio-read.c

## Purpose
Implements the VDO read path and read-modify-write read phase for `data_vio` requests.

## Main Flow
- `launch_read_data_vio()` finds the block map slot for the LBN after the logical lock is acquired.
- `read_block_mapping()` requests the mapped block from the block map.
- `read_block()` handles zero mappings, compressed mappings, partial reads, read-modify-write reads, and full-block read cloning.
- `read_endio()` records completed bio stats and routes successful reads to the CPU queue.
- `complete_read()` decompresses if needed, performs partial copy-out, acknowledges the user bio, and completes the VIO.
- `cleanup_read_data_vio()` releases the logical lock on the logical-zone thread.

## Partial And RMW Behavior
- `modify_for_partial_write()` overlays discard zeroes or incoming bio data into the fetched block.
- It updates `is_zero_block`, switches the operation to write, clears the read error handler, and relaunches the write path.
- `complete_zero_read()` zero-fills a block buffer or user bio and can continue into partial-write modification.

## I/O Behavior
- Full 4 KiB uncompressed reads clone the user bio to avoid copying.
- Compressed and partial reads use the `data_block` or compression buffer.
- Only selected request flags are passed through: `REQ_PRIO`, `REQ_META`, `REQ_SYNC`, and `REQ_RAHEAD`.

## Important Invariants
- Mapping lookup and logical lock release happen on the logical zone.
- Decompression and bio copying happen on the CPU queue.
- Zero-block mappings avoid backing I/O.
