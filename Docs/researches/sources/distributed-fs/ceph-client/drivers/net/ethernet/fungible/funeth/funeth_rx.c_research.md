# sources/distributed-fs/ceph-client/drivers/net/ethernet/fungible/funeth/funeth_rx.c

## Purpose
Implements the funeth receive data path, Rx buffer/page management, CQE processing, XDP receive actions, GRO delivery, Rx queue allocation, and Rx device resource creation/destruction.

## Important APIs and Functions
Externally used functions are `fun_rxq_napi_poll()`, `fun_rxq_set_bpf()`, `funeth_rxq_create()`, `fun_rxq_create_dev()`, and `funeth_rxq_free()`. Internal helpers manage page cache reuse (`cache_offer()`, `cache_get()`, `refresh_refs()`), page allocation/freeing, packet gathering (`get_buf()`, `fun_gather_pkt()`), XDP execution (`fun_run_xdp()`), CQ phase handling, and packet handoff (`fun_handle_cqe_pkt()`).

## Control Flow
NAPI polling calls `fun_process_cqes()`, which checks CQ phase tags, uses `dma_rmb()` before reading descriptors, handles packets up to budget, then flushes pending XDP TX or redirect operations. Packet handling advances the CQ, gathers one or more page fragments from the RQ, optionally runs XDP when configured headroom matches, builds either a linear skb with `napi_build_skb()` or a frags skb with `napi_get_frags()`, sets hash/checksum/timestamp metadata, traces, and submits to GRO. RQ doorbells are written when enough buffers have been consumed.

## State and Persistence
`struct funeth_rxq` tracks CQ/RQ rings, DMA addresses, current buffer and offset, spare buffer, cached reusable buffers, headroom, XDP program, stats, phase, NAPI pointer, and hardware ids. The page reuse model takes a large batch of page references to avoid frequent refcount writes and only reuses pages when reference counts prove the stack no longer owns them.

## Dependencies and Integration Points
Depends on DMA mapping APIs, XDP, BPF, NAPI/GRO, hardware CQ/RQ structures, and queue creation helpers from `fun_queue`. It integrates with `funeth_main.c` for queue publication, IRQ/NAPI ownership, XDP program installation, and hardware timestamp configuration.

## Risks and Test Signals
Risks include page reference accounting errors, DMA sync direction mistakes, packet split/gather boundary bugs, PF_MEMALLOC handling, CQ phase races, XDP action fallback when page refs are not safe, and RQ doorbell starvation. Test with multi-fragment jumbo packets, GRO and checksum/hash metadata validation, XDP_PASS/DROP/TX/REDIRECT, low-memory allocation failures, timestamp-enabled receive, NAPI budget exhaustion, and queue teardown under traffic.
