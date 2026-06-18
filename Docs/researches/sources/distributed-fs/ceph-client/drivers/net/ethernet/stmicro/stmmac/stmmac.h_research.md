# sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/stmmac.h

Purpose: Defines central private data structures, resource declarations, queue state, feature state, and cross-file prototypes for the stmmac driver.

Important APIs and types: Key structures include `stmmac_resources`, TX/RX queue and buffer types, XDP wrappers, FPE config, TC/RFS/filter entries, RSS config, DMA queue arrays, EST schedule state, MSI interrupt names, and `stmmac_priv`. It declares probe/remove/suspend/resume, MDIO, PCS, PTP, XDP, ethtool, queue reinit, queue enable/disable, AF_XDP wakeup, and TAS basetime helpers.

Control flow and state: `stmmac_priv` is the persistent driver instance tying together MMIO bases, netdev/device, selected hardware callbacks, platform data, phylink, DMA rings, NAPI channels, statistics, EST/FPE/PTP/MMC state, EEE/WOL, descriptor mode, VLAN bitmap, TC/RFS flow tables, RSS table, XDP program, workqueue state, and devlink.

Dependencies and integration: Includes Linux networking, phylink, PCI, PTP, reset, page pool, XDP, BPF, and driver `common.h`. It is included by nearly every file in this subset.

Risks and test signals: Layout changes affect hot-path cache behavior and many subsystems. Test probe/remove, suspend/resume, queue reconfiguration, XDP/AF_XDP, PTP registration, EST/FPE, ethtool stats, MSI naming, VLAN restore, and selftest build configurations.
