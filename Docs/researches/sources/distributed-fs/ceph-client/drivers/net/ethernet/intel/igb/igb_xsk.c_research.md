# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/igb/igb_xsk.c

## Purpose
`igb_xsk.c` implements AF_XDP zero-copy support for `igb`. It binds and unbinds `xsk_buff_pool` instances to queue IDs, switches RX ring software metadata between skb buffers and zero-copy XDP buffers, processes zero-copy RX descriptors through XDP programs, transmits AF_XDP descriptors, and provides the netdev XSK wakeup hook.

## Important APIs, Types, And Functions
External entry points include `igb_xsk_pool()`, `igb_xsk_pool_setup()`, `igb_alloc_rx_buffers_zc()`, `igb_clean_rx_ring_zc()`, `igb_clean_rx_irq_zc()`, `igb_xmit_zc()`, and `igb_xsk_wakeup()`. Internal helpers perform ring quiesce/restart (`igb_txrx_ring_disable()`, `igb_txrx_ring_enable()`), metadata reallocation (`igb_realloc_rx_buffer_info()`), descriptor filling (`igb_fill_rx_descs()`), skb construction for XDP_PASS (`igb_construct_skb_zc()`), and XDP execution (`igb_run_xdp_zc()`).

## Control Flow
Pool setup validates the queue, DMA maps the AF_XDP pool, disables the queue pair if the interface is running with XDP enabled, reallocates RX buffer metadata to zero-copy format, re-enables rings, and wakes RX NAPI. Disable reverses the process and DMA unmaps the pool. During RX cleaning, each completed descriptor supplies an `xdp_buff`; optional inline PTP timestamp headers are stripped, the XDP program is run, and results are either redirected, transmitted back, consumed, or converted into an skb for the normal stack. TX reads AF_XDP TX descriptors with `xsk_tx_peek_release_desc_batch()`, DMA syncs each payload, builds advanced TX descriptors, and updates the hardware tail.

## State And Persistence
State is per ring: `rx_buffer_info_zc`, `rx_buffer_info`, `xsk_pool`, descriptor indices, ring flags, XDP program pointer, and queue stats. Pool DMA mappings are persistent until pool disable. Need-wakeup state is maintained through `xsk_set_rx_need_wakeup()` and `xsk_clear_rx_need_wakeup()` when the pool requests that mode.

## Dependencies And Integration Points
This file depends on AF_XDP pool APIs, generic XDP redirect/TX APIs, BPF tracing, NAPI, DMA synchronization, and existing `igb` ring configuration and timestamp helpers. It integrates with `igb_ptp_rx_pktstamp()` for inline RX hardware timestamps, `igb_finalize_xdp()` for XDP TX/redirect finalization, and interrupt generation through EICS/ICS writes in `igb_xsk_wakeup()`.

## Risks
The pool switch path temporarily disables live queues and must restore both descriptor state and NAPI state on failures. RX zero-copy paths must not leak XDP buffers across PASS, DROP, REDIRECT, and TX outcomes. The code relies on descriptor length zeroing and DMA barriers to avoid stale descriptor consumption. `igb_xmit_zc()` currently sets report status on every descriptor, which is explicitly noted as a possible performance optimization. Need-wakeup handling must avoid leaving user space asleep when buffers or TX work remain.

## Test Signals
Run AF_XDP zero-copy bind/unbind tests, XDP_PASS/DROP/TX/REDIRECT programs, `xdpsock` RX/TX need-wakeup modes, queue restart while link is up, and pool setup failure injection. Counters for RX allocation failures, XDP exceptions, TX completions, and packet delivery through NAPI/GRO are useful signals.
