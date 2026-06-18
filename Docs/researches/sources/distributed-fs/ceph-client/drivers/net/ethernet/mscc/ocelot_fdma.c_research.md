# sources/distributed-fs/ceph-client/drivers/net/ethernet/mscc/ocelot_fdma.c

## Purpose
Provides the FDMA fast path for Ocelot frame extraction and injection using DMA descriptor rings, NAPI, page recycling, and interrupt-driven cleanup.

## Important APIs/types/functions
Public functions are `ocelot_fdma_init`, `ocelot_fdma_start`, `ocelot_fdma_deinit`, `ocelot_fdma_inject_frame`, `ocelot_fdma_netdev_init`, and `ocelot_fdma_netdev_deinit`. RX centers on `ocelot_fdma_rx_get`, `ocelot_fdma_get_skb`, `ocelot_fdma_receive_skb`, and `ocelot_fdma_rx_restart`. TX centers on `ocelot_fdma_prepare_skb`, `ocelot_fdma_send_skb`, and `ocelot_fdma_tx_cleanup`.

## Control flow, state, persistence
Init allocates the FDMA context, requests the IRQ, allocates coherent DCB memory, splits it into TX/RX rings, pre-fills RX buffers, and enables the static key. Start configures QS group 0 for DMA, enables interrupts and NAPI, then activates RX. IRQ acknowledges events, disables FDMA interrupts, and schedules NAPI. NAPI cleans TX, drains RX, replenishes descriptors, restarts RX if stopped at a NULL LLP, and reenables interrupts. State is in ring cursors, SKB/page ownership, DMA mappings, NAPI, and FDMA hardware registers.

## Dependencies and integration
Depends on `ocelot_fdma.h`, `ocelot_qs.h`, DMA/SKB/NAPI APIs, IFH helpers, PTP RX timestamping, and `ocelot_net.c` transmit selection.

## Risks and test signals
Risks include ring off-by-one errors, leaked mappings, stale NULL LLP handling, FDMA TX busy return being ignored by the netdev wrapper, and IRQ dev_id mismatch in one error path. Test sustained RX/TX, ring pressure, queue wake/stop, PTP frames, allocation failures, and unload cleanup.
