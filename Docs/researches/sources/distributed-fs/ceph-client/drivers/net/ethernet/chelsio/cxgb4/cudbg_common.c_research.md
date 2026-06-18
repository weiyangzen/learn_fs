# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4/cudbg_common.c

## Purpose
This file provides common CUDBG buffer management helpers used by all cxgb4 debug-dump collectors. It abstracts whether entity collectors write directly into the ethtool/vmcore output buffer or into a reusable compression input buffer.

## Important APIs, Types, And Functions
- `cudbg_get_buff()` reserves a collector input buffer of a requested size. With no compression it points into the main output at the current offset; with compression it points to `pdbg_init->compress_buff`.
- `cudbg_put_buff()` releases/reset the temporary input buffer and clears the reusable compression buffer.
- `cudbg_update_buff()` advances the output buffer offset after an uncompressed direct write.

## Control Flow
Collectors call `cudbg_get_buff()` before filling entity data. The helper validates output capacity, then either returns an output slice or the compression scratch buffer. After collection, `cudbg_lib.c` calls `cudbg_write_and_release_buff()`, which either invokes `cudbg_update_buff()` or compresses and then calls `cudbg_put_buff()`.

## State And Persistence
State is transient in `struct cudbg_buffer` offsets and `struct cudbg_init` compression fields. No persistent state is stored. Under compression, the scratch buffer is zeroed after each entity/chunk so it can be reused.

## Dependencies And Integration Points
It depends on `cxgb4.h`, `cudbg_if.h`, and `cudbg_lib_common.h`. The helpers are used by `cudbg_lib.c` collectors and indirectly by `cxgb4_cudbg.c` when collecting ethtool/vmcore dumps.

## Risks
Size checks use `offset + size`, which assumes no integer overflow in practical dump sizes. Compression mode rejects entity chunks larger than `compress_buff_size`, so callers must chunk large data. `cudbg_update_buff()` trusts `pin_buff->size`; if a collector writes less than reserved size without adjusting it, the output will include stale/zero padding.

## Test Signals
Test no-compression and compression modes, exact-fit buffers, too-small buffers returning `CUDBG_STATUS_NO_MEM`, chunked large entities, and repeated collector calls reusing the compression buffer.
