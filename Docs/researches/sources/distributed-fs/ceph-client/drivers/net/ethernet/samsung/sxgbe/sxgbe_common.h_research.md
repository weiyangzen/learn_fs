# sources/distributed-fs/ceph-client/drivers/net/ethernet/samsung/sxgbe/sxgbe_common.h

Purpose: central shared contract for the Samsung SXGBE driver. It defines driver constants, hardware capability flags, statistics layout, operation tables, queue state, private device state, and cross-file prototypes.

Important APIs and types: `struct sxgbe_extra_stats` is the ethtool-visible extended counter set updated by descriptor and DMA paths. `struct sxgbe_core_ops`, `struct sxgbe_ops`, `struct sxgbe_dma_ops`, `struct sxgbe_desc_ops`, and `struct sxgbe_mtl_ops` form the hardware abstraction tables. `struct sxgbe_tx_queue` and `struct sxgbe_rx_queue` hold descriptor rings, DMA addresses, skb arrays, queue indices, IRQs, and coalescing state. `struct sxgbe_hw_features` stores decoded hardware capabilities. `struct sxgbe_priv_data` is the main netdev private state and holds queues, sizes, NAPI, mapped registers, hardware ops, PHY/MDIO state, pause/EEE/PTP fields, clock, capabilities, stats, and platform data.

Control flow: platform/main probe code fills `sxgbe_priv_data`, obtains ops via `sxgbe_get_core_ops()`, `sxgbe_get_desc_ops()`, `sxgbe_get_dma_ops()`, and `sxgbe_get_mtl_ops()`, allocates rings according to queue constants, then netdev, DMA, ethtool, MDIO, and PM code share this structure.

State and persistence: all runtime state is in `sxgbe_priv_data` and nested queue/stat structures. It is volatile and tied to net_device lifetime. Persistent externally visible state includes ethtool stats, link settings delegated to PHY, coalesce settings, EEE state, and hardware feature reporting.

Dependencies and integration: relies on Linux net_device, PHY, MII, PTP, clock, timer, and platform data types. It bridges the split source files into one driver by declaring all exported helpers.

Risks: many constants hard-code queue counts, FIFO sizes, register dump sizes, and MTU limits. `NETIF_F_HW_VLAN_ALL` is locally defined and may collide with kernel feature naming over time. Stats use `unsigned long` but ethtool extraction handles only u64 vs u32, so width assumptions matter. Hardware descriptor bitfield layout in related headers is compiler/endianness sensitive.

Test signals: compile with PTP enabled/disabled, probe feature decoding, queue allocation for max TX/RX queues, ethtool stats string/count consistency, EEE state transitions, RX checksum and VLAN feature toggles, and PM suspend/resume declarations under `CONFIG_PM`.
