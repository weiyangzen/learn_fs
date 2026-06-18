# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4vf/sge.c

## Purpose
Implements the Chelsio T4/T5/T6 SR-IOV VF Scatter Gather Engine data path: Ethernet TX submission, RX response processing, free-list refill, interrupt/NAPI handling, queue allocation/freeing, and SGE timer maintenance. It is the VF driver's high-throughput DMA ring owner and bridges Linux `sk_buff`/NAPI/netdev queues to Chelsio firmware work requests and hardware doorbells.

## Important APIs, Types, And Functions
Internal descriptor state is represented by `struct tx_sw_desc` for retained TX skbs/SGLs and `struct rx_sw_desc` for RX page, DMA address, and low-bit flags (`RX_LARGE_BUF`, `RX_UNMAPPED_BUF`). Helper APIs include `txq_avail()`, `fl_cap()`, `fl_starving()`, `map_skb()`, `unmap_sgl()`, `free_tx_desc()`, `refill_fl()`, `alloc_ring()`, `sgl_len()`, `flits_to_desc()`, `write_sgl()`, `ring_tx_db()`, and `ring_fl_db()`.

Exported driver entry points are `t4vf_eth_xmit()`, `t4vf_ethrx_handler()`, `t4vf_sge_intr_msix()`, `t4vf_intr_handler()`, `t4vf_sge_alloc_rxq()`, `t4vf_sge_alloc_eth_txq()`, `t4vf_free_sge_resources()`, `t4vf_sge_start()`, `t4vf_sge_stop()`, and `t4vf_sge_init()`. These are called by the surrounding cxgb4vf adapter setup, netdev operations, interrupt setup, and teardown paths.

## Control Flow
TX starts in `t4vf_eth_xmit()`: it validates packet size and MTU, chooses the queue from `skb_get_queue_mapping()`, inserts the VF VLAN tag if required, reclaims completed descriptors, computes firmware work-request flits, checks credits, maps the skb for DMA, builds `fw_eth_tx_pkt_vm_wr` plus LSO or normal `cpl_tx_pkt_core`, optionally adds checksum/VLAN controls, writes a DSGL, records the skb in the last descriptor, advances producer state, updates netdev TX timestamp, and rings the TX doorbell. Queue pressure stops the netdev subqueue and requests firmware egress queue updates.

RX flows through `napi_rx_handler()` into `process_responses()`. The response loop checks generation bits, distinguishes FL-buffer packet responses from CPL-only messages, constructs a `pkt_gl` gather list from free-list pages, syncs the final buffer for CPU access, calls the response queue handler, advances response descriptors, and refills the free list when enough space is available. `t4vf_ethrx_handler()` converts packet gather lists to skbs, chooses GRO for good TCP packets with RX checksum and GRO enabled, otherwise builds a normal skb, sets checksum/VLAN metadata, and hands it to `netif_receive_skb()`.

Interrupt flow is split between MSI-X and MSI. MSI-X schedules the target response queue NAPI directly. MSI uses `process_intrq()` to process forwarded interrupt messages from an interrupt queue, map ingress queue IDs back through `s->ingr_map`, and schedule NAPI on the real response queue.

Queue allocation uses firmware mailbox commands inline in this Linux-facing SGE layer. `t4vf_sge_alloc_rxq()` allocates coherent response/free-list rings, fills `FW_IQ_CMD`, registers NAPI, stores absolute/context IDs, initializes BAR2 doorbell addresses, and pre-fills FLs. `t4vf_sge_alloc_eth_txq()` allocates coherent TX rings and software descriptors, sends `FW_EQ_ETH_CMD`, then initializes TX counters and queue identifiers.

## State And Persistence
Persistent runtime state lives in `adapter->sge`, per-queue `pidx/cidx/in_use/gen/offset`, DMA coherent rings, software descriptor arrays, free-list page references, NAPI state, timers, and netdev queue stop/restart counters. The file does not persist across reboot; all state is reconstructed during device open/reset. DMA ownership is carefully tracked: TX skbs are retained until hardware completion; RX page ownership is transferred to skbs via page refs, unmapped from DMA before CPU use, and restored on handler backpressure.

Timers provide recovery state: `sge_rx_timer_cb()` tracks starving free lists via `starving_fl` bitmaps and schedules NAPI for refill, while `sge_tx_timer_cb()` periodically reclaims completed TX descriptors to avoid stalls when no new traffic arrives.

## Dependencies And Integration Points
The file depends on Linux networking/DMA/NAPI APIs, Chelsio firmware structures from `t4fw_api.h`, CPL messages from `t4_msg.h`, register/value definitions from the PF common headers, and cxgb4vf common helpers in `t4vf_common.h`/`t4vf_defs.h`. It calls `t4vf_wr_mbox()`, `t4vf_bar2_sge_qregs()`, `t4vf_fl_pkt_align()`, `t4vf_iq_free()`, and `t4vf_eth_eq_free()` from `t4vf_hw.c`. It integrates upward with netdev TX, RX handlers, MSI/MSI-X interrupt registration, adapter open/close, and ethtool/debug counters through queue stats.

## Risks
Ring wrap handling is complex in `write_sgl()`, `unmap_sgl()`, inline copy paths, and BAR2 write-combining doorbells; off-by-one errors can corrupt descriptors or leak DMA mappings. RX free-list low-bit encoding must remain compatible with hardware buffer-size bits. Firmware capability differences between T4/T5/T6 affect doorbell fields, burst sizes, status-page lengths, and packet alignment. Memory pressure paths rely on starving-bit recovery and NAPI rescheduling, so refill regressions can deadlock RX. TX reclaim policy intentionally delays skb destruction for performance, which makes the timer important for sparse traffic workloads.

## Test Signals
Useful signals include successful probe/open with SGE parameter validation, TX/RX traffic under TSO/checksum/VLAN/GRO, queue stop/restart counters, absence of DMA API warnings, NAPI budget behavior, pktgen or sparse UDP tests for TX timer reclaim, low-memory RX refill tests, MSI and MSI-X interrupt modes, T4/T5/T6 BAR2 fallback coverage, and firmware mailbox queue allocation/free error injection.
