# sources/distributed-fs/ceph-client/drivers/net/ethernet/samsung/sxgbe/sxgbe_reg.h

Purpose: Central register map and bitfield definition header for the Samsung SXGBE MAC, MDIO/SMA, MMC counters, L3/L4/RSS/PTP/PPS blocks, MTL queues, DMA global state, DMA channels, speed control, feature discovery, and interrupt status/enable masks.

Important APIs and types: Defines register offsets such as core TX/RX config, packet filters, EEE LPI, VLAN, flow control, interrupt status, hardware feature registers, MDIO command/data, MAC address slots, MMC counters, RSS, timestamping, MTL global/queue registers, DMA global/channel registers, and descriptor pointer/tail registers. It also defines feature extraction macros for capability registers 0..2, queue register address macros, speed encodings, RX/TX enable bits, VLAN controls, checksum/jumbo bits, DMA interrupt masks, and channel status bits.

State and dependencies: The header carries no state; it is the shared symbolic ABI between register-access implementation files and the SXGBE hardware. `sxgbe_main.c`, `sxgbe_mdio.c`, `sxgbe_mtl.c`, and lower-level core/DMA/descriptor modules depend on these names remaining stable.

Risks and test signals: Register offsets and bitfield masks are hardware-critical and failures can appear as silent nonfunctional TX/RX, bad stats, broken MDIO, or wrong offload reporting. The typo-like macro `SXGBE_HW_FEAT_PMT_TEMOTE_WOP` is used by the driver and should not be renamed casually. Tests should include compile coverage of every consumer plus hardware or emulated register validation for feature extraction, interrupt mask composition, MMC stats offsets, MTL queue address calculations, and DMA channel address calculations.
