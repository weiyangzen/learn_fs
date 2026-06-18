# sources/distributed-fs/ceph-client/drivers/crypto/cavium/nitrox/nitrox_reqmgr.c

## Purpose

`nitrox_reqmgr.c` turns a prepared `se_crypto_request` into DMA mappings, Nitrox SG components, packet input instructions, command-queue entries, and asynchronous completions. It also enforces queue length, backlogs eligible requests, processes response lists from solicited packet completions, and handles timeout/error propagation.

## Important APIs, Types, And Functions

- `incr_index()` wraps command queue ring indices.
- `softreq_unmap_sgbufs()` and `softreq_destroy()` undo DMA mappings, free SG component arrays, and release the soft request.
- `create_sg_component()` converts DMA-mapped Linux SG entries into Nitrox four-entry `nitrox_sgcomp` arrays and maps that component array for device access.
- `dma_map_inbufs()`/`dma_map_outbufs()` map request SG lists and create component lists.
- `backlog_list_add()`, `response_list_add()`, `response_list_del()`, and `get_first_response_entry()` maintain command queue lists.
- `cmdq_full()` atomically reserves pending slots and rolls back if over `ndev->qlen`.
- `post_se_instr()` copies a 64-byte instruction to the packet input ring, adds the request to the response list, records a timestamp, executes `dma_wmb()`, and rings the doorbell.
- `post_backlog_cmds()` drains queued backlog entries while space exists.
- `nitrox_enqueue_request()` posts immediately or backlogs/drops based on `CRYPTO_TFM_REQ_MAY_BACKLOG`.
- `nitrox_process_se_request()` is the exported submission entry point used by algorithm code.
- `sr_completed()`, `process_response_list()`, and `pkt_slc_resp_tasklet()` detect hardware completions and invoke request callbacks.
- `backlog_qflush_work()` retries backlog posting from workqueue context.

## Control Flow

`nitrox_process_se_request()` rejects non-ready devices, allocates `nitrox_softreq`, records callback state and response marker pointers, maps input and output SGs, extracts a DMA context handle if a crypto context is present, picks `smp_processor_id() % ndev->nr_queues`, and fills the packet instruction. The instruction points `dptr0` at input SG components, sets gather and scatter counts, sets front-data size, total length, destination solicit port, context length/pointer, opcode/arg, output SG component pointer, and GP header front data.

Submission calls `nitrox_enqueue_request()`, which first tries to flush old backlog requests, then uses `cmdq_full()` to decide whether to post, backlog, or reject. Posted requests are copied into `cmdq->base[write_idx]`, added to the response list, published with `dma_wmb()`, and submitted by writing `1` to the queue doorbell.

Completions arrive through `pkt_slc_resp_tasklet()`. It reads completion counts, asks `process_response_list()` to walk up to the current pending budget, checks ORH/completion markers, handles timeout if markers remain pending past `ndev->timeout`, decrements pending counts, removes completed requests, maps the low ORH byte to an error status, destroys request DMA resources, and calls the algorithm callback. The tasklet then clears/resends the interrupt and schedules backlog flush work if needed.

## State And Persistence Behavior

State is per-device command queue state: pending counts, backlog counts/list, response list, write index, MMIO doorbell/completion addresses, and stats counters (`posted`, `completed`, `dropped`). Per-request state persists from submission until callback and contains DMA mappings, SG component arrays, timestamp, callback, and response markers. Hardware-visible command descriptors and SG components persist in DMA memory until unmapped.

## Dependencies And Integration Points

This file depends on Nitrox common/device/CSR headers, Linux DMA mapping, workqueues, spinlocks, atomics, jiffies, and Crypto API request flags. It integrates with `nitrox_skcipher.c` and AEAD providers through `nitrox_process_se_request()`, with ISR setup through `pkt_slc_resp_tasklet()`, and with common queue allocation structures from `nitrox_dev.h`.

## Risks And Edge Cases

- `cmdq_full()` increments `pending_count` as a reservation; every failure/completion path must balance it.
- `post_backlog_cmds()` holds `backlog_qlock` while calling `post_se_instr()`, which takes `cmd_qlock` and response lock; lock ordering must remain consistent.
- `sr_completed()` waits up to about 1 ms for completion bytes after ORH status appears; slow memory visibility can produce false incomplete reports.
- Timeout handling still calls callbacks with the low ORH byte, which may remain `0xff` from `PENDING_SIG`, causing generic error mapping upstream.
- DMA maps both source and destination as bidirectional; this is conservative but can hide direction-specific cache bugs.
- `smp_processor_id()` queue selection assumes stable CPU context and can be skewed under softirq/preemption behavior.

## Test Signals

Signals include Crypto API async success, backlog behavior under full queues, dropped counters when backlog is disallowed, timeout logging, DMA mapping error handling, SG fragmentation coverage, stats increments, response-list ordering, and interrupt resend behavior when completion count remains over threshold.
