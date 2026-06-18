# sources/distributed-fs/ceph-client/drivers/net/ethernet/google/gve/gve_rx.c

## Purpose

`gve_rx.c` implements the legacy GQI RX datapath. It allocates/free GQI RX rings, preposts packet buffers in raw-addressing or QPL mode, consumes RX descriptors in NAPI, assembles SKBs from fragments, runs XDP for eligible packets, handles copybreak and QPL copy-pool behavior, updates RX stats, and rings the legacy RX doorbell.

## Important APIs, types, and functions

- Allocation/lifecycle: `gve_rx_alloc_ring_gqi`, `gve_rx_alloc_rings_gqi`, `gve_rx_free_ring_gqi`, `gve_rx_free_rings_gqi`, `gve_rx_start_ring_gqi`, `gve_rx_stop_ring_gqi`.
- Buffer setup: `gve_rx_prefill_pages`, `gve_setup_rx_buffer`, `gve_rx_alloc_buffer`, `gve_rx_unfill_pages`, `gve_rx_free_buffer`.
- Packet assembly: `gve_rx_add_frags`, `gve_rx_skb`, `gve_rx_qpl`, `gve_rx_raw_addressing`, `gve_rx_copy_to_pool`.
- Recycling/refill: `gve_rx_can_recycle_buffer`, `gve_rx_flip_buff`, `gve_rx_refill_buffers`.
- XDP: `gve_xdp_redirect`, `gve_xsk_pool_redirect`, `gve_xdp_done`.
- Polling: `gve_rx_work_pending`, `gve_clean_rx_done`, `gve_rx_poll`.

## Control flow and state

Ring allocation creates a data ring, optional QPL, QPL copy pool, queue resources, and a descriptor ring. `fill_cnt` tracks posted buffers, `cnt` tracks consumed descriptors, and `desc.seqno` tracks the next expected 3-bit sequence number. In NAPI, `gve_clean_rx_done()` loops while descriptors have the expected sequence and budget allows, calls `gve_rx()` per fragment, advances counters/sequence, detects incomplete packet anomalies, flushes XDP TX/redirects when counters changed, refills raw-addressing buffers below threshold, and writes the doorbell.

Per-packet state lives in `rx->ctx`: head/tail SKB, total size, fragment count, and drop flag. QPL mode must return registered pages to the NIC quickly, so non-recyclable data is copied to a separate copy pool. Raw-addressing mode can replace a page if the stack still owns it. State is volatile and reset by ring stop/start.

## Dependencies and integration points

The file depends on legacy descriptors in `gve_desc.h`, common ring structs in `gve.h`, QPL/page allocation helpers from `gve_main.c`, XDP and AF_XDP kernel APIs, and `gve_tx.c` for GQI XDP TX flush/transmit. `gve_main.c` calls the alloc/start/stop/free APIs and uses `gve_rx_work_pending()` during interrupt completion.

## Risks and test signals

Risks include page-ref bias imbalance, RX sequence mismatch triggering reset, incomplete packet handling, QPL copy-pool exhaustion, buffer refills failing without timely repoll, XDP actions only supported for single-fragment packets, and copybreak accounting. Tests should cover GQI raw and QPL modes, fragmented packets, sequence wrap, RX checksum/hash propagation, XDP DROP/PASS/TX/REDIRECT, AF_XDP redirect path, small-packet copybreak, and forced allocation failures.
