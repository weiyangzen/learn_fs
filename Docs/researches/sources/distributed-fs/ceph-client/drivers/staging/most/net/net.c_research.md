# sources/distributed-fs/ceph-client/drivers/staging/most/net/net.c

## Purpose
Mostcore networking component that binds one async RX channel and one async TX channel from the same MOST interface into a Linux Ethernet netdev named `meth%d`. It encapsulates Ethernet frames into MOST Ethernet Packet (MEP) or MOST Asynchronous MAC (MAMAC/MDP) wire formats and decapsulates received MBOs back into skbs.

## Important APIs, Types, And Functions
`struct net_dev_context` owns the MOST interface, netdev, RX/TX channel ids, MAMAC mode flag, and global-list node. `struct net_dev_channel` tracks one linked channel. Key functions are `comp_probe_channel()`, `comp_disconnect_channel()`, `most_nd_open()`, `most_nd_stop()`, `most_nd_start_xmit()`, `comp_rx_data()`, `comp_resume_tx_channel()`, `skb_to_mamac()`, `skb_to_mep()`, `most_nd_set_mac_address()`, and `on_netinfo()`.

## Control Flow
Mostcore probes TX and RX async channels separately. The first channel allocates a netdev and the second registers it; open starts both MOST channels, wakes the net queue, and optionally requests HDM netinfo. Transmit gets an MBO from the TX channel, wraps the skb as MAMAC when the configured MAC begins with four zero bytes or as MEP otherwise, submits the MBO, updates stats, and frees the skb. RX completion validates MAMAC/MEP headers, allocates an skb, reconstructs Ethernet addressing for MAMAC, calls `eth_type_trans()`, and injects via `netif_rx()`.

## State And Persistence
State is in-memory only: linked channel flags, channel ids, `is_mamac`, netdev stats, queue/carrier state, and global `net_devices`. `probe_disc_mt` serializes probe/disconnect/open, while `list_lock` protects list membership and linked flags for refcounted lookups. No durable state is stored.

## Dependencies And Integration Points
Depends on Mostcore component/configfs APIs, `struct mbo`, Linux netdev/etherdevice helpers, skb allocation, and optional interface `request_netinfo`. It registers as Mostcore component `net`.

## Risks
The two-channel pairing is order-dependent and registration only happens on the second channel. MAMAC address synthesis uses protocol-specific offsets and assumes validated MDP headers. Disconnect relies on `unregister_netdev()` to drive `ndo_stop()` before channel stop. TX queue wake depends on Mostcore TX completion callbacks.

## Test Signals
Probe TX/RX in both orders, duplicate direction rejection, open/stop with netinfo callbacks, short/oversized skb drops, MEP and MAMAC packet round trips, invalid RX header rejection, TX MBO exhaustion queue stop/resume, MAC-address changes switching MTU/MAMAC mode, and disconnect while the netdev is up.
