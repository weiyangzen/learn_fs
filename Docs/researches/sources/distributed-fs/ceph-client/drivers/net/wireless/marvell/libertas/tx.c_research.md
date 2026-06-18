# sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/libertas/tx.c

## Purpose
Builds Libertas firmware TX descriptors from netdev skbs, queues one pending data frame for the main thread to send through the active transport, and handles monitor-mode TX feedback.

## Important APIs And Functions
`lbs_hard_start_xmit()` is the netdev transmit entry point for station and mesh devices. `lbs_send_tx_feedback()` is exported to transports/event paths to echo monitor-mode TX packets back with retry status. `convert_radiotap_rate_to_mv()` maps radiotap rates into firmware TX-control format.

## Control Flow And State
TX holds `driver_lock`, rejects surprise removal and invalid sizes, stops both station and mesh queues, and enforces a single `priv->tx_pending_len` slot. It fills `struct txpd` in `priv->tx_pending_buf`, copies destination address from Ethernet or 802.11 header, applies mesh descriptor markings, copies payload after the descriptor, updates stats, and wakes `lbs_thread()`. Monitor mode keeps `currenttxskb` until an event calls `lbs_send_tx_feedback()`, which sets retry count and injects the skb back through `netif_rx()`.

## Dependencies And Integration
Used by `main.c` netdev ops and `mesh.c` mesh netdev ops. Depends on `host.h`, `radiotap.h`, mesh helpers, `lbs_thread()` draining `tx_pending_buf`, and transport `hw_host_to_card`.

## Risks And Test Signals
Risks include contention between station and mesh hard-start paths, queue wake rules when waiting for monitor feedback, invalid radiotap header assumptions, and descriptor length mismatch. Test signals include ordinary TX, mesh TX descriptor marking, oversize/zero-length drops, queue stop/wake behavior, transport send failures, and monitor TX feedback injection.
