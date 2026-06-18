# sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/stmmac_libpci.h

Purpose: Declares the stmmac PCI platform suspend/resume helper functions.

Important APIs and data: Exposes `stmmac_pci_plat_suspend(struct device *dev, void *bsp_priv)` and `stmmac_pci_plat_resume(struct device *dev, void *bsp_priv)`.

Control flow and state: No state is defined here. The declarations allow PCI glue drivers to share PM helper behavior implemented in `stmmac_libpci.c`.

Dependencies and integration: Uses `struct device` declarations from included translation units; included by the PCI helper implementation and expected PCI glue users.

Risks and test signals: Header/API drift would break out-of-file PCI glue builds. Test module builds with PCI stmmac users and ensure suspend/resume callback signatures match platform glue expectations.
