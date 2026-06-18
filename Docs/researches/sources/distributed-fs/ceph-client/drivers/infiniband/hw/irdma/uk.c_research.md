# sources/distributed-fs/ceph-client/drivers/infiniband/hw/irdma/uk.c

## Purpose
This file implements the IRDMA user/kernel shared queue mechanics: SQ/RQ/SRQ WQE construction, CQ polling, ring advancement, inline-data packing, generation-specific WQE helpers, queue depth/shift calculation, and QP/CQ/SRQ UK initialization.

## Important APIs, Types, And Functions
- WQE allocation/posting helpers: `irdma_qp_get_next_send_wqe()`, `irdma_qp_get_next_recv_wqe()`, `irdma_srq_get_next_recv_wqe()`, `irdma_uk_qp_post_wr()`, `irdma_nop()`, and internal `irdma_nop_1()`.
- Send operations: `irdma_uk_rdma_write()`, `irdma_uk_rdma_read()`, `irdma_uk_send()`, `irdma_uk_inline_rdma_write()`, `irdma_uk_inline_send()`, `irdma_uk_atomic_fetch_add()`, `irdma_uk_atomic_compare_swap()`, and `irdma_uk_stag_local_invalidate()`.
- Receive operations: `irdma_uk_post_receive()` and `irdma_uk_srq_post_receive()`.
- Completion operations: `irdma_uk_cq_poll_cmpl()`, `irdma_uk_cq_empty()`, `irdma_uk_cq_request_notification()`, `irdma_uk_cq_resize()`, `irdma_uk_cq_set_resized_cnt()`, and `irdma_uk_clean_cq()`.
- Init/sizing helpers: `irdma_get_wqe_shift()`, `irdma_get_sqdepth()`, `irdma_get_rqdepth()`, `irdma_get_srqdepth()`, `irdma_uk_qp_init()`, `irdma_uk_cq_init()`, `irdma_uk_srq_init()`, `irdma_uk_calc_shift_wq()`, and depth/fragment conversion helpers.
- `iw_wqe_uk_ops` and `iw_wqe_uk_ops_gen_1` select generation-specific fragment, inline, and memory-window writers.

## Control Flow
SQ posting starts by validating SGE counts and inline sizes, calculating total transfer length and required WQE quanta, then calling `irdma_qp_get_next_send_wqe()`. That allocator ensures the WQE does not cross an unsupported hardware chunk boundary by padding with NOPs when needed, advances the SQ head by quanta, toggles polarity on wrap, and records WR tracking. Operation-specific code writes fragments, remote addresses, immediate data, AH/QKey/QPN fields, fences, opcode, completion-signaling, and valid bit after `dma_wmb()`. Optional `post_sq` rings the doorbell.

RQ and SRQ posting atomically advance the receive ring head, write fragment descriptors, store WR ids, publish the valid bit after a DMA barrier, and update SRQ shadow state. CQ polling validates polarity, handles extended CQEs, decodes immediate data, UD VLAN/source MAC, QP context, status, operation, WQE index, payload length, invalidated STag, and solicited events. It advances SQ/RQ/SRQ tails and CQ head/tail, but during flush it can park the CQ head and synthesize additional software completions for remaining WQEs on older hardware.

Initialization functions install ring bases, doorbells, shadow areas, queue sizes, fragment limits, WQE-size multipliers, polarity defaults, generation-specific ops, and connection-reserved WQE handling.

## State And Persistence
The persistent state is the UK portions of QPs, CQs, and SRQs: ring head/tail, base pointers, doorbells, shadow areas, WR tracking arrays, receive WR id arrays, polarity bits, flush flags, max fragment/inline limits, WQE operation table, and queue sizes. WQEs and CQEs are hardware-visible memory, so valid-bit ordering and DMA barriers are part of state correctness.

## Dependencies And Integration Points
The file depends on `user.h` for operation structures and status enums, `irdma.h`/`defs.h` for bit masks and ring macros, Linux RDMA `ib_sge`, MMIO `writel()`, and memory barriers. It is used by both kernel and user-mapped queue paths and by higher SC/PUDA code that embeds `struct irdma_qp_uk` and `struct irdma_cq_uk`.

## Risks And Edge Cases
High-risk areas are WQE quanta calculation, chunk padding, valid-bit polarity on wrap, GEN1 versus GEN2+ layout differences, inline-data packing, flush CQE synthesis, and keeping SQ/RQ tails synchronized with hardware CQEs. Unsigned ring arithmetic and untrusted SGE counts are guarded, but regressions can produce memory corruption or stuck queues. CQ polling treats non-signaled SQ completions as unexpected except in flush paths, so caller expectations must match signaled tracking.

## Test Signals
Test RDMA write/read/send, inline variants, immediate data, atomics, local invalidate, RQ and SRQ receives, CQ notification, CQ resize, clean CQ, flush completions, queue wrap, chunk-boundary padding, maximum SGE limits, max inline limits, GEN1 and GEN2+ descriptor layouts, and doorbell/ring state under stress. KASAN/KCSAN and hardware CQE dumps are valuable for this file.
