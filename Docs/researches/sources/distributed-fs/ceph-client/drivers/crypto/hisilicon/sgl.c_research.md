# sources/distributed-fs/ceph-client/drivers/crypto/hisilicon/sgl.c

## Purpose
This file provides a shared HiSilicon accelerator helper for converting Linux scatterlists into hardware SGL descriptors stored in preallocated coherent DMA pools. SEC and ZIP use it to avoid allocating descriptor memory per request and to hand hardware a compact DMA address for a list of source or destination buffers.

## Important APIs, Types, And Functions
Exported APIs are `hisi_acc_create_sgl_pool()`, `hisi_acc_free_sgl_pool()`, `hisi_acc_sg_buf_map_to_hw_sgl()`, and `hisi_acc_sg_buf_unmap()`. The hardware layout is `struct hisi_acc_hw_sgl`, with header fields for next pointer and entry counts followed by flexible `struct acc_hw_sge` entries. `struct hisi_acc_sgl_pool` stores up to five coherent memory blocks, count, SGE capacity, and descriptor size.

## Control Flow
Pool creation validates device, count, and SGE count, computes an aligned descriptor size, chooses block sizes up to `PAGE_SIZE << MAX_PAGE_ORDER` capped at 2^31, allocates full blocks plus a remainder block, and stores pool geometry. Mapping first DMA maps the Linux scatterlist, rejects inputs with more mapped entries than the pool SGE count, obtains the indexed hardware SGL from the pool, fills SGE DMA addresses/lengths/page controls, and returns both virtual and DMA addresses. Unmap reverses the scatterlist DMA mapping and clears descriptor fields.

## State And Persistence
State is coherent DMA memory owned by the pool and reused by callers according to a caller-provided index. The helper itself does not track allocations or concurrency; it assumes the caller assigns unique indices and releases mappings. Descriptor contents are cleared on unmap but pool memory persists until `hisi_acc_free_sgl_pool()`.

## Dependencies And Integration Points
The file depends on DMA mapping, scatterlist APIs, and `linux/hisi_acc_qm.h` for public declarations. SEC uses one input and one output pool per QP. ZIP uses a pool sized at twice the queue depth so each request gets separate source and destination hardware SGLs.

## Risks
Because the pool does not internally lock or allocate entries, callers must not reuse the same index concurrently. `entry_sum_in_chain` is set to the pool capacity rather than actual mapped entries, matching hardware expectations but easy to misinterpret. Failure during remainder allocation frees only previously allocated full blocks; this is correct for the current loop but sensitive to future changes. `page_ctrl` stores `sg_virt()` and must not be consumed by hardware as a DMA pointer.

## Test Signals
Exercise pool creation for min/max SGE counts, boundary block counts, invalid counts, scatterlists with too many mapped entries, in-place/unmap paths in SEC and ZIP, and repeated reuse of the same index. DMA debug and KASAN can catch stale mapping and descriptor overrun bugs.
