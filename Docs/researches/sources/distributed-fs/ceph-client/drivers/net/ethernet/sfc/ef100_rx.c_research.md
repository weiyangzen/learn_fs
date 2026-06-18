# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/ef100_rx.c

Purpose: Implements EF100 receive event handling, RX descriptor doorbells, packet prefix decoding, checksum extraction, FCS/drop accounting, and MAE representor steering for packets received on non-base mports.

Important APIs and functions: `ef100_rx_buf_hash_valid()` reads the EF100 RX prefix RSS validity bit. `efx_ef100_ev_rx()` consumes RX completion events and advances `removed_count`. `ef100_rx_write()` writes DMA buffer addresses into RX descriptors and rings `ER_GZ_RX_RING_DOORBELL`. `__ef100_rx_packet()` is the packet finalizer reached through `efx_rx_flush_packet()`. Static helpers decode prefix fields and detect FCS errors.

Control flow: RX events report a packet count. For each packet, the code syncs the DMA buffer, skips the EF100 prefix by advancing `page_offset`, recycles page ownership, flushes any previous packet, then records one fragment in the channel. Finalization reads the prefix before the Ethernet header, optionally lets raw channel handlers consume the packet, drops FCS errors unless `NETIF_F_RXALL` is enabled, validates minimum Ethernet length, handles ingress mport routing, populates checksum state, updates queue byte/packet counters, and passes the skb through GRO.

State and persistence: It mutates per-channel counters such as `n_rx_eth_crc_err`, `n_rx_frm_trunc`, `n_rx_mport_bad`, `n_rx_merge_events`, and `irq_mod_score`; per-queue counters such as `removed_count`, `notified_count`, `rx_packets`, and `rx_bytes`; and RX buffer fields `len` and `page_offset`. No durable persistence exists, but queue indices must remain consistent across interrupt/NAPI processing.

Dependencies and integration points: Depends on EF100 register layout macros from `ef100_regs.h`, queue helpers from `rx_common.h`, NIC data from `ef100_nic.h`, generic flush path from `efx.h`, MCDI common definitions, and optional `CONFIG_SFC_SRIOV` representor functions. It integrates with `efx_channels.c` NAPI polling, RX refill, GRO, netdev feature flags, and MAE mport identity.

Risks: Prefix field decoding is bit-offset sensitive. Bad `removed_count` or descriptor mask handling can desynchronize completions. Mport handling drops unrecognized traffic and representor copies depend on RCU protection. Memory barriers in `ef100_rx_write()` are required before doorbells and before grant-credit work. RXALL changes security/error visibility by accepting FCS-bad frames.

Test signals: Exercise single and merged RX events, short frames, FCS-bad frames with and without RXALL, checksum valid/error paths, representor RX by mport, unknown mport drops, RX refill/doorbell updates, and GRO delivery under NAPI budget.
