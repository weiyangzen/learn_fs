<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfd3/xsk.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfd3/xsk.c

## Purpose
`xsk.c` implements the NFD3 AF_XDP polling path. It receives packets into XSK buffers, parses NFP metadata, runs XDP programs, converts selected packets to SKBs, handles XDP_TX and XDP_REDIRECT, transmits user-space XSK TX descriptors, and completes XDP/XSK TX buffers.

## Important APIs, Types, And Functions
The public functions are `nfp_nfd3_xsk_poll()` and `nfp_nfd3_xsk_tx_free()`. Internal helpers include `nfp_nfd3_xsk_tx_xdp()`, `nfp_nfd3_xsk_rx_skb()`, `nfp_nfd3_xsk_rx()`, `nfp_nfd3_xsk_complete()`, and `nfp_nfd3_xsk_tx()`.

## Control Flow
`nfp_nfd3_xsk_rx()` polls RX descriptors, detects buffer starvation, validates metadata length, updates stats, adjusts XDP buffer pointers for dynamic metadata, parses chained metadata, routes representor/control-port packets to SKB/control paths before BPF, runs the XDP program for host packets, and handles PASS/TX/REDIRECT/DROP/ABORTED. PASS allocates an skb and copies data from the XSK buffer, then frees the XSK RX buffer. XDP_TX builds an NFD3 TX descriptor using the RX XDP buffer and marks it as `is_xsk_tx` so completion frees it. REDIRECT calls `xdp_do_redirect()` and flushes at the end.

`nfp_nfd3_xsk_complete()` reads TX completion pointers, updates stats, frees RX-buffer-backed XDP_TX buffers, and reports user-space TX completions for descriptors not reused from RX. `nfp_nfd3_xsk_tx()` batches `xsk_tx_peek_desc()` descriptors while ring space is available, syncs DMA for device, fills descriptors, releases the XSK producer batch, and writes the hardware TX pointer with a barrier.

## State And Persistence
State lives in RX `xsk_rxbufs`, XDP/TX ring `txbufs`, XSK pool producer/consumer rings, TX descriptor pointers, and per-vector stats. Buffers are transferred among RX pool ownership, XDP program ownership, TX descriptor ownership, and userspace completion ownership.

## Dependencies And Integration Points
The file integrates with NFP metadata parsing/checksum/VLAN helpers from `dp.c`, NFP app representor/control dispatch, AF_XDP pool APIs, XDP redirect APIs, NAPI, NFD3 descriptor format, and XSK setup/wakeup support in `nfp_net_xsk.c`.

## Risks
Ownership is the main risk: XDP_TX buffers must be unstashed and freed exactly once on completion, while normal XSK TX descriptors must be completed back to userspace. The path supports only dynamic metadata layout. SKB conversion copies packet data, so it is slower than zero-copy and can fail under memory pressure. The NAPI completion uses `skbs` rather than all polled packets for `napi_complete_done()`, which is intentional but easy to misread when changing budgeting.

## Test Signals
Test AF_XDP RX with XDP PASS/TX/REDIRECT/DROP/ABORTED, metadata-present representor and control-port packets, RX buffer starvation, invalid metadata, XSK userspace TX batching, TX completion accounting with reused and non-reused buffers, xdp_do_flush behavior, and NAPI budget interactions with normal TX completion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfd3/xsk.c -->
