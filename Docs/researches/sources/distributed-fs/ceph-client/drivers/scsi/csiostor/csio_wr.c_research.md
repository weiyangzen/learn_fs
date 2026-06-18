# sources/distributed-fs/ceph-client/drivers/scsi/csiostor/csio_wr.c

## Purpose

This file implements the csiostor work-request module. It allocates DMA-backed ingress, egress, and freelist queues; creates/destroys firmware queue contexts via mailbox commands; reserves and issues egress WRs; processes ingress responses and freelist buffers; and initializes SGE host/interrupt/coalescing parameters.

## Important APIs, Types, And Functions

Externally used APIs are `csio_wr_alloc_q()`, `csio_wr_iq_create()`, `csio_wr_eq_create()`, `csio_wr_destroy_queues()`, `csio_wr_get()`, `csio_wr_copy_to_wrp()`, `csio_wr_issue()`, `csio_wr_process_iq()`, `csio_wr_process_iq_idx()`, `csio_wr_sge_init()`, `csio_wrm_init()`, and `csio_wrm_exit()`. Internal response handlers include `csio_wr_iq_create_rsp()`, `csio_wr_eq_cfg_rsp()`, `csio_wr_iq_destroy_rsp()`, and `csio_wr_eq_destroy_rsp()`. Fast-path helpers manage FL doorbells, queue credits, IQ generation bits, and queue wraparound.

## Control Flow

Initialization starts with `csio_wrm_init()`, which allocates the WR module queue-pointer array and per-queue metadata. `csio_wr_sge_init()` then reads or programs SGE registers depending on mastership, firmware init state, and soft-parameter use. Queue allocation reserves a queue slot, allocates DMA memory, calculates credits/wrap pointers, optionally recursively allocates a freelist for an ingress queue, allocates FL buffer metadata, fills FL buffers, and records INTx handlers.

Firmware context creation uses mailbox commands. `csio_wr_iq_create()` builds IQ parameters from interrupt mode, WR size, vector, port, async flag, and optional freelist; synchronous callers immediately parse the response and install IQ/FL ids and interrupt map entries. `csio_wr_eq_create()` creates offload egress queues attached to an IQ.

Transmit paths call `csio_wr_get()` to read EQ status-page `cidx`, compute free credits, return one or two memory spans for possible wraparound, advance `pidx`, and record `inc_idx`. `csio_wr_issue()` uses a write barrier and rings the SGE doorbell. Receive paths call `csio_wr_process_iq()`, which loops while the footer generation bit indicates a new entry, dispatches CPL, FLBUF, or forwarded interrupt responses, replenishes FL queues below low water, then writes GTS with consumed count and coalescing timer.

## State And Persistence

`struct csio_wrm` owns the queue array, firmware id bases, interrupt map, free queue cursor, and cached SGE registers. Each `struct csio_q` stores producer/consumer indices, increment count, DMA region, owner, context-specific IDs, and stats. State is volatile but synchronized with hardware through DMA queue memory, status pages, doorbells, GTS writes, SGE registers, and firmware mailbox contexts.

## Dependencies And Integration Points

The file depends on Chelsio register definitions in `t4_values.h`, hardware helpers in `csio_hw.h`, mailbox helpers in `csio_mb.h`, `t4fw_api.h`, and `t4fw_api_stor.h`. It integrates with PCI DMA allocation, SGE hardware registers, firmware IQ/EQ commands, interrupt dispatch, and upper csiostor modules that provide IQ handlers and consume WR queue slots.

## Risks

Queue wrap and credit arithmetic are correctness-critical; an off-by-one can overwrite unconsumed WRs or starve queues. Several error paths in `csio_wr_alloc_q()` return after partially allocated queues or FL buffers, relying on later WRM exit for cleanup. `csio_wr_process_iq()` indexes `intr_map[qid]` without an explicit bound check after subtracting `fw_iq_start`, so corrupt forwarded interrupt qids can be dangerous. FL buffer invalidation does not free DMA memory immediately, which is intentional but makes refill/accounting bugs harder to see. SGE programming differs across T5/T6 and master/non-master paths; wrong flags can misconfigure padding, status page size, or coalescing.

## Test Signals

Test by creating/destroying IQ/EQ/FL queues in all interrupt modes, exhausting queue slots, forcing mailbox failures, issuing WRs that wrap around EQ end, processing empty and stray IQ interrupts, handling CPL/FLBUF/INTR responses, exercising FL refill thresholds, unloading after partial allocation failures, and validating SGE coalescing values against module parameters.
