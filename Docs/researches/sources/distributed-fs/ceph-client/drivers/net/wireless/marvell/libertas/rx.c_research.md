# sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/libertas/rx.c

## Purpose
Processes full-firmware Libertas RX packets delivered by transports. It strips firmware descriptors, converts firmware SNAP/802.2 framing to Ethernet II when appropriate, routes mesh frames to the mesh netdev, constructs radiotap headers in monitor mode, updates stats, and submits packets to the network stack.

## Important APIs And Functions
`lbs_process_rxed_packet()` is exported to transports. `process_rxed_802_11_packet()` handles monitor-mode RX. `convert_mv_rate_to_radiotap()` maps firmware rate indices to radiotap 500 Kb/s units. Local packed header structs model firmware 802.3/SNAP and 802.11 layouts.

## Control Flow And State
Normal RX reads `struct rxpd`, finds the payload via `pkt_ptr`, chooses `priv->dev` or `priv->mesh_dev` via `lbs_mesh_set_dev()`, validates length, optionally rewrites SNAP to Ethernet II, pulls descriptor/header bytes, updates `priv->cur_rate` and netdev stats, then calls `netif_rx()`. Monitor RX validates length, builds `struct rx_radiotap_hdr`, pulls `rxpd`, expands headroom if needed, prepends radiotap, and submits the skb.

## Dependencies And Integration
Called by SDIO/SPI/USB transports after they allocate/fill skb data. Uses `host.h` descriptors, `radiotap.h`, mesh helpers, cfg80211 iftype, and Linux skb/netdev APIs.

## Risks And Test Signals
Risks include trusting firmware `pkt_ptr`, insufficient length checks for malformed frames, radiotap headroom allocation failure, SNAP conversion pointer arithmetic, and stats on the selected device. Test signals include Ethernet RX, non-SNAP LLC RX, mesh RX routing, monitor-mode capture, invalid length drops, and rate reporting.
