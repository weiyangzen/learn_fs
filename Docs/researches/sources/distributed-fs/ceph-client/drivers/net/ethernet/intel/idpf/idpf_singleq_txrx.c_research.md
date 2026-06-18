# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/idpf/idpf_singleq_txrx.c

## Purpose
`idpf_singleq_txrx.c` implements the single-queue IDPF TX/RX datapath. It builds base TX descriptors and context descriptors, maps skb data to DMA, handles checksum/TSO/tunnel offloads, cleans completed TX descriptors, allocates/refills RX buffers, decodes base and flex RX descriptors, runs XDP/libeth receive processing, updates stats, and provides the single-queue NAPI poll handler.

## Important APIs, types, and functions
- TX offload and mapping: `idpf_tx_singleq_csum()`, `idpf_tx_singleq_build_ctx_desc()`, `idpf_tx_singleq_map()`, `idpf_tx_singleq_dma_map_error()`, and public `idpf_tx_singleq_frame()`.
- TX completion: `idpf_tx_singleq_clean()` and `idpf_tx_singleq_clean_all()`.
- RX descriptor helpers: `idpf_rx_singleq_test_staterr()`, `idpf_rx_singleq_is_non_eop()`, base/flex checksum extractors, base/flex hash handlers, and base/flex field extractors.
- RX processing and refill: `idpf_rx_singleq_buf_hw_alloc_all()`, `idpf_rx_singleq_clean()`, and `idpf_rx_singleq_clean_all()`.
- XDP/libeth integration: `idpf_rx_singleq_process_skb_fields()`, `idpf_xdp_run_pass()`, `LIBETH_XDP_ONSTACK_BUFF`, and libeth RX/TX helpers.
- NAPI entry point: `idpf_vport_singleq_napi_poll()`.

## Control flow
TX starts in `idpf_tx_singleq_frame()`. It computes descriptor demand, stops the subqueue if available descriptors fall below the needed threshold, derives IPv4/IPv6 flags from the skb protocol, runs TSO setup, runs single-queue checksum setup, emits a context descriptor when TSO or tunnel metadata is needed, records the first TX buffer, calculates packet/byte accounting, maps the skb into one or more base descriptors, sets EOP/RS on the last descriptor, updates BQL, and rings the hardware tail unless xmit-more batching defers it.

Checksum setup handles outer and inner headers for encapsulated packets. It builds tunnel context fields for UDP/GRE/IP-in-IP/IPv6 tunnels, falls back to `skb_checksum_help()` when unsupported non-TSO offload is encountered, and rejects unsupported TSO combinations. It programs MAC/IP/L4 header length offsets and base descriptor command bits for IPv4, IPv6, TCP, UDP, and SCTP.

DMA mapping maps the linear skb first, then each fragment, splitting any segment larger than the hardware maximum descriptor data size. On mapping failure it increments DMA error stats, unmaps already mapped buffers through libeth completion helpers, clears a TSO context descriptor if one was consumed, and updates the hardware tail to keep queue state coherent.

TX clean walks from `next_to_clean`, skips context descriptors, checks the watched EOP descriptor's done dtype, completes the skb and all associated fragments through libeth, advances ring cursors with wrap handling, updates queue packet/byte stats, and wakes the netdev queue when descriptor availability exceeds the wake threshold and the vport/carrier are up.

RX clean loops until packet budget is exhausted or the next descriptor lacks DD. It uses a DMA read barrier before descriptor fields, extracts packet length and ptype from either base or flex descriptor format, attaches the buffer to an on-stack libeth XDP buffer, advances the ring, handles non-EOP aggregation and RX error descriptors, runs XDP/GRO processing with checksum/hash field population, saves partial XDP state, refills cleaned buffers, updates packet/byte stats, and returns packets processed.

The NAPI poll handler handles budget-zero netpoll by cleaning TX only. Otherwise it fairly divides budget across RX queues and TX queues on the q-vector. If work remains, it enables writeback-on-ITR and returns budget; if complete, it completes NAPI and reenables interrupts or leaves writeback-on-ITR for busy-polling.

## State and persistence behavior
TX state lives in descriptor rings (`base_tx`, `base_ctx`), `tx_buf` metadata, `next_to_use`, `next_to_clean`, watched `rs_idx`, BQL accounting, queue stats, and hardware tail registers. RX state lives in descriptor rings, `rx_buf` page-pool/netmem entries, XDP saved buffer state, `next_to_clean`, `next_to_alloc`, `next_to_use`, queue stats, ptype lookup table, page pool, and tail registers. State is volatile per queue and rebuilt on vport open/reset.

## Dependencies and integration points
The file depends on Linux skb, DMA mapping, NAPI, XDP, page pool, BQL, checksum/GSO metadata, and `net/libeth/xdp.h`. It consumes descriptor definitions from `idpf_lan_txrx.h` and virtchnl2 RX descriptor definitions, queue helpers/macros from `idpf.h`, TSO/drop/hardware-tail helpers from other IDPF files, and interrupt helpers from vport interrupt code. It is selected when the negotiated queue model is single queue.

## Risks and edge cases
- Descriptor cursor arithmetic is high risk; wrap handling must keep `tx_buf`, descriptor pointers, and negative `ntc` arithmetic synchronized.
- DMA mapping error unwind must free every mapped fragment and not unmap unmapped context descriptors.
- Checksum/tunnel parsing must reject unsupported TSO cases but safely software-checksum unsupported non-TSO packets.
- RX DD detection relies on overlapping descriptor fields being zero for unused descriptors; descriptor format changes can break this assumption.
- Non-EOP RX handling and saved XDP buffer state must handle multi-buffer packets without leaks.
- Budget division across many queues can under-service queues if packet and TX completion work are imbalanced.
- Queue wake decisions depend on vport up and carrier state; incorrect state can cause stuck TX queues.

## Test signals
Run single-queue traffic with checksum offload, TSO, SCTP, IPv6 extension headers, UDP/GRE tunnels, GSO partial, VLAN traffic, xmit-more batching, DMA mapping failure injection, TX queue stop/wake stress, RX base and flex descriptor modes, XDP pass/drop/redirect if supported, multi-buffer RX, RX checksum/hash validation, netpoll budget-zero calls, interrupt moderation/NAPI completion behavior, and reset/open/close while traffic is active.
