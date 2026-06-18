# sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx5/mem.c

## Purpose
`mem.c` contains focused memory helper routines for mlx5 RDMA memory registration paths. It converts pinned user memory into hardware physical address segments and computes page-size/page-offset encodings for mlx5 command mailboxes with quantized offset fields.

## Important APIs, Types, And Functions
`mlx5_ib_populate_pas()` fills a PAS array from an `ib_umem` using `rdma_umem_for_each_dma_block()`. `__mlx5_umem_find_best_quantized_pgoff()` selects an allowed page size and calculates a quantized page offset. The public macro wrappers for the quantized helper are declared in `mlx5_ib.h`.

## Control Flow
PAS population iterates DMA blocks at the requested page size, ORs each DMA address with access flags, converts to big endian, and advances the output pointer. Quantized page-offset selection first asks RDMA core for the largest compatible page size using `ib_umem_find_best_pgoff()`. It then repeatedly halves the page size until the DMA offset fits in the mailbox page-offset field after scaling. If the reduced page size is not permitted by the original bitmap or the final quantized offset exceeds the field mask, it returns zero.

## State And Persistence Behavior
The file owns no state. It writes only caller-provided PAS arrays and page-offset output variables. Results are derived from the DMA mapping state held by `ib_umem`.

## Dependencies And Integration Points
The helpers are used by MR, CQ, QP, WQ, and device-memory registration code that needs mlx5 mailbox-compatible memory layout. Dependencies are RDMA umem iteration APIs, DMA block iterators, endian helpers, and page-size bitmaps prepared by `mlx5_ib.h` macros.

## Risks
The quantized loop assumes halving will eventually make the offset representable; invalid scale or bitmap inputs can still lead to a zero result. PAS population trusts the caller-provided array is large enough for `ib_umem_num_dma_blocks()`. Access flags are ORed into physical addresses, so flag bit placement must match hardware PAS format.

## Test Signals
Test user MR registration with aligned and unaligned addresses, multiple supported page sizes, small mailbox page-offset fields, dma-buf/ODP-backed umems where applicable, and PAS contents for read/write access flag combinations.
