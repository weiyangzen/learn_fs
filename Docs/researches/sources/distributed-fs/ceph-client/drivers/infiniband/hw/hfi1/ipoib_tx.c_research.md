# sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/ipoib_tx.c

## Purpose
`ipoib_tx.c` implements HFI1 accelerated IPoIB transmit over SDMA. It owns per-netdev TX queues, circular request rings, SDMA descriptor construction, IB 9B UD header construction, xmit-more batching, NAPI completion cleanup, SDMA descriptor starvation sleep/wakeup handling, queue stop/wake thresholds, and timeout diagnostics.

## Important APIs, types, and functions
- `struct ipoib_txparms` collects per-packet transmit context: HFI device, AH attributes, port, TX queue, flow tuple, destination QPN, header size, and entropy.
- Circular ring helpers `hfi1_txreq_from_idx()`, `hfi1_ipoib_used()`, `hfi1_ipoib_ring_hwat()`, and `hfi1_ipoib_ring_lwat()` manage `struct hfi1_ipoib_circ_buf`.
- Queue control helpers `hfi1_ipoib_stop_txq()`, `hfi1_ipoib_wake_txq()`, `hfi1_ipoib_check_queue_depth()`, and `hfi1_ipoib_check_queue_stopped()` coordinate netdev subqueue state with ring fullness and descriptor starvation counters.
- `hfi1_ipoib_build_ib_tx_headers()` creates LRH/GRH/BTH/DETH headers and PBC for UD SEND_ONLY packets, including P_Key, Q_Key, PSN, SL-to-SC mapping, VL mapping, entropy, and source QPN.
- `hfi1_ipoib_build_tx_desc()` and `hfi1_ipoib_build_ulp_payload()` initialize SDMA descriptors for PBC/header plus SKB linear and paged payload.
- `hfi1_ipoib_send_dma_single()` and `hfi1_ipoib_send_dma_list()` submit one TX request or batch a list for `netdev_xmit_more()`.
- `hfi1_ipoib_sdma_sleep()`, `hfi1_ipoib_sdma_wakeup()`, and `hfi1_ipoib_flush_txq()` integrate the TX queue with SDMA iowait.
- `hfi1_ipoib_txreq_init()`, `hfi1_ipoib_txreq_deinit()`, `hfi1_ipoib_napi_tx_enable()`, and `hfi1_ipoib_napi_tx_disable()` own lifetime.

## Control flow
The netdev send path enters `hfi1_ipoib_send()`, rejects packets larger than the RDMA netdev MTU plus IPoIB encapsulation, builds `ipoib_txparms` from the address handle and SKB queue mapping, derives the service channel from `ibp->sl_to_sc`, and chooses list or single submission based on `netdev_xmit_more()` and whether a batch is already pending.

Both submit paths call `hfi1_ipoib_send_dma_common()`. That routine reserves a ring slot, initializes an `ipoib_txreq`, builds headers, builds SDMA descriptors, and switches SDMA engine when the flow changes. The single path advances the ring tail and calls `sdma_send_txreq()`. The list path flushes any pending list before a flow change, appends the descriptor to `tx_list`, advances the ring, and flushes only when the networking stack stops batching.

SDMA completion calls `hfi1_ipoib_sdma_complete()`, stores status, marks the TX request complete with release semantics, and schedules TX NAPI. `hfi1_ipoib_poll_tx_ring()` consumes completed entries in order, frees SKBs, cleans SDMA descriptors, advances the ring head with release semantics, updates completion counters, and wakes stopped queues when below the low-water mark.

## State and persistence
Each `struct hfi1_ipoib_txq` stores a ring, pending SDMA list, iowait object, current flow, selected SDMA engine, NAPI object, queue index, and counters. Request lifetime is ring-based: SKBs and descriptors are attached at tail reservation, completed by SDMA callback, then freed by NAPI from head order. Atomic fields `stops`, `ring_full`, and `no_desc` allow independent stop reasons. There is no persistent state beyond runtime memory and hardware descriptor submission.

## Dependencies and integration points
The file depends on Linux netdev multiqueue/NAPI APIs, SKB fragment APIs, HFI1 SDMA APIs, rdmavt AH/QP structures, HFI1 header/PBC helpers, tracepoints, SL-to-SC and SC-to-VL mappings, and iowait scheduling. It is invoked through `struct rdma_netdev.send` installed by `ipoib_main.c`.

## Risks
- Ring correctness depends on paired release/acquire operations between SDMA completion, TX NAPI, and tail/head updates.
- Queue stop/wake uses multiple atomic stop reasons; missed balancing can leave a subqueue permanently stopped or prematurely woken.
- Flow changes force list flushes. Errors during flush drop the current SKB and may leave queued descriptors for later cleanup.
- SDMA `-EBUSY` and `-ECOMM` are treated as accepted/queued conditions; other errors mark the request complete and rely on NAPI cleanup.
- The local source contains duplicated declarations in `hfi1_ipoib_send_dma_common()` and `hfi1_ipoib_sdma_sleep()` (`u32 head;` and duplicate `container_of` assignment). If this exact tree is compiled, those are build-breaking C errors and should be caught by the build.

## Test signals
- Compile HFI1 IPoIB TX to catch API drift and the duplicated declarations noted above.
- Stress multiqueue transmit with varying `tx_queue_len`, `netdev_xmit_more()` batching, flow changes, and SDMA engine selection.
- Force SDMA descriptor starvation to validate `hfi1_ipoib_sdma_sleep()`, iowait queueing, flush work, and queue wakeup.
- Inject SDMA completion errors and verify SKB freeing, netdev stats, NAPI completion, and timeout diagnostics.
- Exercise GRH and non-GRH address handles, P_Key/Q_Key changes, SL-to-SC changes, and MTU oversize drops.
