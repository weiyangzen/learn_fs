# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/siena/rx.c

## Purpose

`rx.c` is the Siena receive packet processing path. It consumes completed RX descriptors after event handling, validates packet lengths/fragments, DMA-syncs data, pipelines prefetch and delivery, runs XDP when attached, builds SKBs or GRO fragments, attaches hardware timestamps, handles loopback self-test packets, and updates RX error/XDP counters.

## Important APIs, Types, and Functions

`efx_siena_rx_packet()` is called by NIC-specific event code when a packet completion arrives. It records flags, validates length and fragment count, handles explicit discard, syncs DMA buffers, adjusts offsets past the RX prefix, syncs tail fragments, recycles pages, and stores a pending packet in `channel->rx_pkt_*` after flushing the previously pending packet.

`__efx_siena_rx_packet()` is the second-stage delivery function. It reads prefix length if needed, diverts loopback self-test packets, runs `efx_do_xdp()`, clears checksum flags if RX checksum offload is disabled, chooses GRO for TCP packets without a special channel receiver, or calls `efx_rx_deliver()` to allocate and submit an SKB.

Local helpers include `efx_rx_packet__check_len()`, `efx_rx_mk_skb()`, `efx_rx_deliver()`, and `efx_do_xdp()`.

## Control Flow

The RX path is deliberately pipelined. Completion of packet N first calls `efx_rx_flush_packet()` so packet N-1 is delivered after its header prefetch had time to complete. The newly completed packet is stored in channel fields for the next flush. Multi-fragment packets are validated against `EFX_RX_MAX_FRAGS`, `efx->rx_dma_len`, and `efx->rx_scatter`.

XDP runs only for single-fragment packets. On `XDP_PASS`, any data pointer offset is reflected in RX buffer offset/length and the saved RX prefix is restored before the shifted Ethernet header. `XDP_TX` converts the XDP buffer to a frame and submits through `efx_siena_xdp_tx_buffers()`. `XDP_REDIRECT` calls `xdp_do_redirect()`. Drop/abort/invalid actions free the RX buffer and update counters.

SKB delivery copies header bytes into a linear SKB area and appends remaining page fragments. It sets checksum state, RX queue index, NAPI ID, optional timestamp, and either hands the SKB to a channel-specific receiver such as PTP or to `netif_receive_skb()`. GRO uses `napi_get_frags()` and fills skb frags directly.

## State and Persistence Behavior

This file updates `rx_queue->rx_packets`, RX buffer flags/lengths/offsets/page ownership, per-channel pending packet fields, RX error counters, XDP counters, `efx->n_rx_noskb_drops`, and SKB timestamp/checksum/hash metadata. Page ownership transfers to SKB, XDP TX/redirect, recycle ring, or free paths depending on action.

## Dependencies and Integration Points

It depends on RX queue allocation/refill/recycle helpers from `rx_common.c`, XDP and BPF APIs, TX XDP helper declarations, PTP timestamp attachment from `ptp.h`, loopback self-test hooks, NAPI/GRO, Linux checksum/SKB helpers, and NIC type RX prefix layout fields in `struct efx_nic_type`.

## Risks and Test Signals

Risk areas include page ownership on every XDP outcome, prefix restoration after XDP data adjustment, multi-fragment validation, checksum flag consistency, GRO fragment accounting, and timestamp attachment only when sync events are valid. Tests should cover single and scattered RX, overlength completions, explicit discard completions, XDP PASS/DROP/ABORTED/TX/REDIRECT including failure injection, RX checksum toggling, PTP channel receive hook, loopback self-test, and memory leak checks around SKB allocation failure.
