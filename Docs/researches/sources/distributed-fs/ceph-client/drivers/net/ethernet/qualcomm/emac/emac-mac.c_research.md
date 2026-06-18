# sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/emac/emac-mac.c

### Purpose
`emac-mac.c` implements Qualcomm EMAC MAC and DMA operation: multicast filtering, register programming, descriptor ring allocation, device start/stop, PHY link adjustment, receive completion, transmit completion, and packet transmit descriptor construction.

### Important APIs, Types, And Functions
Public functions include `emac_mac_up()`, `emac_mac_down()`, `emac_mac_reset()`, `emac_mac_stop()`, `emac_mac_mode_config()`, `emac_mac_rx_process()`, `emac_mac_tx_process()`, `emac_mac_rx_tx_ring_init_all()`, `emac_mac_rx_tx_rings_alloc_all()`, `emac_mac_rx_tx_rings_free_all()`, `emac_mac_tx_buf_send()`, and multicast hash helpers. Internal helpers configure MAC/DMA/RX/TX registers, allocate/free TX/RX rings, refill RFDs, parse RRDs, prepare TSO/checksum offloads, and fill TPD descriptors.

### Control Flow
Bringup resets ring indices, programs MAC/DMA/ring registers, refills RX buffers, connects the PHY in SGMII mode, enables interrupts, starts PHY polling, enables NAPI, and starts the netdev queue. Link changes start or stop MAC datapath and notify SGMII. RX processing consumes hardware RRDs up to budget, maps RFD buffers to SKBs, drops error packets, sets checksum/VLAN metadata, submits SKBs to GRO, updates process indices, and refills buffers. TX maps head/frags into TPDs, programs checksum/TSO/VLAN fields, marks the last descriptor after a write barrier, advances the hardware producer index, and later unmaps/frees completed buffers.

### State, Persistence, And Dependencies
State is in `emac_adapter`, one RX queue, one TX queue, descriptor ring memory from a coherent DMA allocation, per-descriptor SKB/DMA bookkeeping, netdev queue state, NAPI state, PHY state, and hardware mailbox/descriptor registers. Dependencies include Linux DMA mapping, SKB/GSO/checksum helpers, PHYLIB, CRC32 multicast hashing, SGMII helpers, and EMAC register definitions from `emac.h`.

### Integration Points
The core platform driver calls these routines from netdev open/stop/start_xmit, interrupt/NAPI paths, multicast mode updates, and reinit flows. Etthtool ring/pause/private-flag changes feed into this file via adapter fields and reinitialization.

### Risks
Descriptor accounting is the main risk: mapping failures must unwind produced descriptors correctly, TX queue stop/wake thresholds must leave room for worst-case SKBs, and RX refill must preserve one blank buffer slot. The driver logs but does not support multi-RFD receive packets. Hardware checksum quirks require ignoring L4F in the drop mask. Start/stop ordering must avoid PHY adjust-link races, which is why interrupts are disabled before `phy_disconnect()`.

### Test Signals
Exercise open/close, link up/down, MTU changes including jumbo, VLAN RX/TX, RX checksum on/off, TCPv4/v6 TSO, fragmented SKBs, DMA mapping failure injection, low RX buffer refill, TX queue stop/wake, multicast/promiscuous/allmulti modes, NAPI budget limits, and repeated ethtool-triggered reinitialization.
