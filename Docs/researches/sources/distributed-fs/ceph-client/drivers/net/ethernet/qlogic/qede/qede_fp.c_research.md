# sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qede/qede_fp.c

## Purpose
This file implements the qede fast path: Tx descriptor construction and completion, Rx buffer provisioning and CQE processing, NAPI polling, MSI-X fastpath interrupt entry, XDP transmit/redirect support, checksum/GRO metadata, tunnel offload filtering, and PTP timestamp handoff from packets to `qede_ptp`.

## Important APIs, Types, and Functions
The central queue types are `struct qede_fastpath`, `struct qede_rx_queue`, `struct qede_tx_queue`, `struct sw_rx_data`, `struct qede_agg_info`, qede software Tx rings, and qed chain objects used for FW descriptor rings.

Public driver entry points include `qede_alloc_rx_buffer()`, `qede_free_tx_pkt()`, `qede_txq_has_work()`, `qede_has_rx_work()`, `qede_recycle_rx_bd_ring()`, `qede_update_rx_prod()`, `qede_poll()`, `qede_msix_fp_int()`, `qede_start_xmit()`, `qede_select_queue()`, `qede_features_check()`, and `qede_xdp_transmit()`.

Important internal helpers include `qede_xmit_type()`, `qede_update_tx_producer()`, `qede_tx_int()`, `qede_xdp_tx_int()`, `qede_rx_process_cqe()`, `qede_rx_xdp()`, `qede_rx_build_skb()`, `qede_rx_build_jumbo()`, the TPA/GRO helpers `qede_tpa_start()`, `qede_tpa_cont()`, `qede_tpa_end()`, and checksum classifiers `qede_check_csum()`, `qede_check_tunn_csum()`, and `qede_check_notunn_csum()`.

## Control Flow
Transmit starts in `qede_start_xmit()`. The code chooses an offload type from skb checksum/GSO/encapsulation state, optionally linearizes skb fragments, produces FW Tx BDs, maps linear and fragmented skb data for DMA, fills VLAN, L4 checksum, tunnel, IPv6 extension, and LSO fields, stores the skb in the software ring, advances `sw_tx_prod`, and rings the doorbell through `qede_update_tx_producer()`. Tx completion is driven by NAPI through `qede_tx_int()`, which compares FW status-block consumer indices against qed chain indices, calls `qede_free_tx_pkt()` to unmap and free skb data, updates netdev byte/packet completion accounting, and wakes stopped queues when descriptor space returns.

Receive setup allocates order-0 pages in `qede_alloc_rx_buffer()`, maps full pages for DMA, and places page segments into Rx BDs. NAPI calls `qede_rx_int()`, which processes completion CQEs until budget or hardware consumer exhaustion. Regular CQEs can run XDP first. `XDP_PASS` continues into skb construction; `XDP_TX` and `XDP_REDIRECT` allocate replacement buffers before consuming the current BD; drop/abort paths recycle BDs. Non-XDP packets build skb data from page segments, handle jumbo packets spanning multiple BDs, set protocol/hash/checksum/Rx queue metadata, record PTP Rx timestamps when CQE flags indicate a timestamped timesync packet, and pass packets through GRO.

TPA/GRO CQEs are handled as a small state machine. TPA start builds the initial skb and records aggregation state, continuation appends page frags, and end verifies lengths and BD counts, finalizes protocol/checksum/GSO metadata, and submits the aggregated skb. `qede_poll()` also handles XDP Tx completions, flushes redirects, completes NAPI when no more status-block work exists, acknowledges interrupts, and flushes pending XDP Tx doorbells.

## State and Persistence Behavior
The file maintains volatile queue state: software producer/consumer indices, filled Rx buffer counts, page offsets within reused Rx pages, DMA mappings, skb pointers, XDP frame/page ownership, TPA aggregation state, per-queue statistics, and hardware doorbell producer values. It persists nothing beyond in-memory driver state and netdev statistics. DMA mappings and page references are lifetime-sensitive and move between device ownership, driver rings, XDP, and the networking stack.

## Dependencies and Integration Points
It depends on qed chain/status-block and doorbell APIs, `struct eth_*_bd`/CQE formats from the qed firmware interface, Linux netdev/NAPI/skbuff/GRO APIs, DMA mapping APIs, XDP/BPF helpers, tunnel and checksum helpers, VLAN helpers, and `qede_ptp_record_rx_ts()`/`qede_ptp_tx_ts()` from the PTP layer. `qede_main.c` allocates and starts the queues consumed here and wires `qede_start_xmit`, `qede_poll`, IRQ handlers, and XDP hooks into netdev operations.

## Risks
The highest risks are descriptor/accounting mismatches and DMA lifetime errors. Tx failure cleanup must return qed chain producers to the pre-packet position and unmap exactly the segments that were mapped. Rx page reuse depends on correct `page_offset`, refcount, and DMA unmap behavior, especially with XDP because pages are mapped bidirectionally. Memory barriers around status-block reads and doorbell writes are essential to avoid missed completions or firmware reading stale descriptors. TPA error paths can leak or double-use pages if aggregation state and `tpa_start_fail` handling drift. Hardware checksum classification must not mark bad packets as `CHECKSUM_UNNECESSARY`, especially for tunneled traffic. Only one PTP Tx timestamp can be outstanding, so timestamp requests may be skipped under load.

## Test Signals
Useful signals include sustained TCP/UDP transmit and receive, high-fragment skb transmit, TSO/TSO6, VLAN insertion/receive, VXLAN/Geneve/GRE offloads, IPIP offload suppression, jumbo receive, GRO/TPA aggregation, XDP pass/drop/tx/redirect, queue stop/wake stress, Tx timeout diagnostics, and PTP hardware timestamping. Kernel debug signals include DMA API debugging, page refcount debugging, NAPI budget behavior under netpoll budget zero, no stuck netdev queues, stable `rx_alloc_errors` under memory pressure, and no missed interrupts after status-block acknowledgement.
