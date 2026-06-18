# sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/stmmac_libpci.c

Purpose: Provides reusable PCI power-management helpers for stmmac platform glue drivers.

Important APIs and flow: `stmmac_pci_plat_suspend()` saves PCI state, disables the device, and enables wake from D3. `stmmac_pci_plat_resume()` restores PCI state, powers the device to D0, enables it, and restores bus mastering. Both are exported GPL symbols.

Control flow and state: Persistent state is PCI config/device state managed by the PCI core. The `bsp_priv` argument is accepted for platform-helper compatibility but unused.

Dependencies and integration: Depends on Linux device and PCI APIs plus `stmmac_libpci.h`. PCI-based stmmac drivers can use these helpers in PM callbacks before or after common stmmac suspend/resume logic.

Risks and test signals: Ordering with common netdev suspend/resume matters: device disable before DMA quiesce would be unsafe if called in the wrong layer. Test suspend/resume on PCI devices, wake from D3, `pci_enable_device()` failure recovery, bus mastering restored after resume, and interaction with runtime PM.
