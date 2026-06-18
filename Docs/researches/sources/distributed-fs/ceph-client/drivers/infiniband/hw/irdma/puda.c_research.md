# sources/distributed-fs/ceph-client/drivers/infiniband/hw/irdma/puda.c

## Purpose
This file implements the Intel IRDMA privileged UDA helper queues used for iWARP/RoCE exception traffic: ILQ and IEQ. It owns PUDA resource creation/destruction, buffer-pool management, send and receive posting, CQ polling, and IEQ-specific reassembly of partial MPA FPDUs before sending completed data back through a loopback UDA send.

## Important APIs, Types, And Functions
- Public PUDA lifecycle and I/O APIs: `irdma_puda_create_rsrc()`, `irdma_puda_dele_rsrc()`, `irdma_puda_poll_cmpl()`, `irdma_puda_get_bufpool()`, `irdma_puda_ret_bufpool()`, `irdma_puda_send()`, and `irdma_puda_send_buf()`.
- Resource helpers allocate coherent CQ/QP memory, initialize `struct irdma_sc_cq` and `struct irdma_sc_qp`, issue CQP create/destroy commands, register PUDA CQs in `dev->ilq_cq`/`dev->ieq_cq`, and allocate `struct irdma_puda_buf` DMA buffers.
- Receive-path helpers include `irdma_puda_poll_info()`, `irdma_puda_post_recvbuf()`, `irdma_puda_replenish_rq()`, and `irdma_ilq_putback_rcvbuf()`.
- IEQ partial-FPDU handling is in `irdma_ieq_process_fpdus()`, `irdma_ieq_process_buf()`, `irdma_ieq_handle_partial()`, `irdma_ieq_get_fpdu_len()`, `irdma_ieq_compl_pfpdu()`, `irdma_ieq_handle_exception()`, `irdma_ieq_receive()`, and `irdma_ieq_cleanup_qp()`.
- The code depends on helpers declared elsewhere for TCP/IP parsing, AH creation/free, CRC checks, QP lookup, AE generation, and IEQ ACKs.

## Control Flow
`irdma_puda_create_rsrc()` allocates one resource per VSI, wires SQ/RQ tracking arrays after the resource object, initializes the PD, creates the CQ, creates the UDA QP, allocates `tx_buf_cnt + rq_size` DMA buffers, posts the initial receive queue, enables CRC checking for IEQ, and arms the CQ. Error paths call `irdma_puda_dele_rsrc()` to unwind by the `rsrc->cmpl` milestone.

Receive completions flow through `irdma_puda_poll_cmpl()`. It decodes a CQE with `irdma_puda_poll_info()`, validates the completion context and QP id, synchronizes the DMA buffer for CPU access, parses TCP/IP metadata, dispatches to the ILQ or IEQ receive callback, and either puts the ILQ receive buffer back in place or replenishes IEQ RQ entries. Send completions recover the buffer from SQ tracking, call the transmit completion callback, advance SQ availability, and drain `txpend` if queued buffers exist.

`irdma_puda_send_buf()` serializes SQ availability with `bufpool_lock`. If no send WQE is available or earlier buffers are pending, it queues the buffer on `txpend`; otherwise it builds `irdma_puda_send_info`, synchronizes the buffer, and calls `irdma_puda_send()` to write the UDA SEND WQE and ring the doorbell.

IEQ receives identify the real QP with `irdma_ieq_get_qp()` and then process exception traffic under `qp->pfpdu.lock`. The first buffer for a partial mode initializes `pfpdu->rcv_nxt`, `fps`, `max_fpdu_data`, and `rxlist`. Buffers are appended only when sequence and receive-window checks pass. GEN2+ may first create an AH from the received packet, then `irdma_ieq_process_fpdus()` walks ordered buffers, validates MPA markers and CRC, copies complete or reassembled FPDUs into transmit buffers, updates TCP/IP header fields, marks loopback, and sends them through the PUDA SQ.

## State And Persistence
State is in memory and hardware queues only. Persistent per-resource state includes the CQ, QP, PD, DMA memory blocks, SQ/RQ tracking arrays, receive indexes, invalid receive count, transmit availability, buffer pool, pending transmit list, allocation list, stats counters, and IEQ CRC/partial counters. Per-QP IEQ state lives in `struct irdma_pfpdu`: ordered receive list, next sequence state, first partial sequence, marker length, AH pointer, CRC/error flags, and counters. Memory barriers (`dma_wmb()`, `dma_rmb()`) and DMA sync calls protect device/CPU ownership transitions.

## Dependencies And Integration Points
The file integrates with the lower UK queue helpers in `uk.c`, SC object definitions in `type.h`, UDA hardware field macros in `uda_d.h`, CQP command helpers, work scheduler/QoS hooks, device/VSI state, TCP/IP parser helpers, AH management, and hardware generation checks. It publishes PUDA CQs through `struct irdma_sc_dev` so interrupt/CEQ paths can find the correct CQ.

## Risks And Edge Cases
The main risks are queue accounting errors, wrong polarity/valid-bit ordering, DMA ownership mistakes, and partial-FPDU list lifetime bugs. `avail_buf_count` is incremented outside the spinlock in `irdma_puda_ret_bufpool()`, so it is a snapshot rather than a strictly locked counter. IEQ partial handling must return all buffers to the pool on CRC, sequence, AH creation, or no-buffer failures. GEN1 and GEN2 WQE layouts diverge in several paths, increasing regression risk. Destruction skips CQP destroy on reset but still frees host memory, so callers must guarantee hardware is quiesced.

## Test Signals
Useful signals include module builds with both GEN1 and GEN2+ paths, PUDA resource create/destroy under injected CQP and allocation failures, CQ poll tests for RQ/SQ/error/extended CQEs, KASAN/KCSAN/leak checks on IEQ error cleanup, packet tests with IPv4/IPv6/VLAN/source-MAC extended CQEs, MPA marker and CRC fault injection, out-of-order IEQ sequence tests, and runtime counters for `stats_buf_alloc_fail`, `stats_rcvd_pkt_err`, `crc_err`, `bad_seq_num`, `partials_handled`, and `stats_sent_pkt_q`.
