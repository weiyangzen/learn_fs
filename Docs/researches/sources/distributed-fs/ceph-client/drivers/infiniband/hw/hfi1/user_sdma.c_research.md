# sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/user_sdma.c

## Purpose
`user_sdma.c` implements the userspace SDMA submission path. It allocates per-file packet and completion queues, validates user-provided packet templates and iovecs, constructs one or more SDMA tx requests, handles expected-receive TID offsets, uses AHG when available, submits descriptors to SDMA engines, and publishes completion-ring status.

## Important APIs and Functions
Public APIs are `hfi1_user_sdma_alloc_queues()`, `hfi1_user_sdma_free_queues()`, and `hfi1_user_sdma_process_request()`. Core internal functions are `defer_packet_queue()`, `activate_packet_queue()`, `flush_pq_iowait()`, `user_sdma_send_pkts()`, `compute_data_length()`, `user_sdma_txadd_ahg()`, `check_header_template()`, `set_pkt_bth_psn()`, `set_txreq_header()`, `set_txreq_header_ahg()`, `user_sdma_txreq_cb()`, `user_sdma_free_request()`, and `set_comp_state()`. Engine selection uses `dlid_to_selector()` and `sdma_select_user_engine()`.

## Control Flow
Queue allocation builds a packet queue, request array, in-use bitmap, txreq slab cache, completion queue mapped with `vmalloc_user()`, and system-pinning handler, then publishes `fd->pq` under RCU. Request processing copies `sdma_req_info`, validates completion index, iovec count, fragment size, opcode, SC/VL consistency, P_Key, no-GRH template constraint, and expected-request TID vector requirements. It claims a completion slot, initializes `struct user_sdma_request`, copies data iovecs and optional TID array, selects an SDMA engine, optionally allocates AHG, marks the completion `QUEUED`, then loops until all packets are submitted. `user_sdma_send_pkts()` allocates txreqs, computes per-packet lengths, updates header fields or AHG descriptors, pins/maps user pages through SDMA packet helpers, queues txreqs, and calls `sdma_send_txlist()`. If the engine is busy, the queue is deferred to `sde->dmawait` and the caller waits for activation. Completion callback frees txreqs, marks errors, frees request resources at the final sequence, and publishes `COMPLETE` or `ERROR`.

## State, Persistence, and Dependencies
Persistent per-file state includes `hfi1_user_sdma_pkt_q`, `hfi1_user_sdma_comp_q`, request array, bitmap, txreq slab, iowait state, MMU RB handler, pinned-page counts, and completion ring entries. Per-request state includes copied header template, SDMA info, SDE pointer, TID list, data length, iov progress, sequence counters, AHG index, KDETH offsets, and error flag. Dependencies include SDMA core, iowait, mmu_rb, pinning, expected receive TID definitions, rdmavt headers, and TX tracepoints.

## Integration Points
The file/device ioctl path passes user iovecs into `hfi1_user_sdma_process_request()`. Expected receive setup supplies TID values validated here. SDMA engine code owns descriptor submission and callbacks. Completion queues are consumed by userspace. Queue teardown synchronizes with SRCU to stop new requests, drains iowait, waits for active request count to reach zero, and frees pinning resources.

## Risks and Test Signals
Risks include trusting malformed user templates, completion-slot reuse races, AHG descriptor overflow, expected TID offset crossing errors, busy-engine waits timing out and needing wait-list cleanup, freeing queues while callbacks are outstanding, memory ordering for completion status/errcode, and mismatched SC/VL/P_Key validation. Test signals include invalid opcode/GRH/SC/VL/P_Key rejection, expected and eager SDMA multi-packet sends, AHG and non-AHG paths, engine busy deferral and activation, completion-ring state transitions, request abort/error callback paths, queue teardown under outstanding requests, and page-pinning leak checks.
