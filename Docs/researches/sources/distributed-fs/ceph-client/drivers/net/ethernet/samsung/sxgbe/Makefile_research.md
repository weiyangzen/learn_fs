# sources/distributed-fs/ceph-client/drivers/net/ethernet/samsung/sxgbe/Makefile

Purpose: defines the object composition for the Samsung SXGBE Ethernet driver.

Important rules: `obj-$(CONFIG_SXGBE_ETH) += samsung-sxgbe.o` creates the final built-in object or module. `samsung-sxgbe-objs` aggregates platform probe, main netdev logic, descriptor ops, DMA ops, MAC core ops, MTL ops, MDIO ops, ethtool ops, and any conditional `samsung-sxgbe-y` additions.

Control flow: Kbuild links the listed objects into one driver image when enabled.

State and persistence: no runtime state; controls link composition and module contents.

Dependencies and integration: depends on source files in the same directory (`sxgbe_platform.o`, `sxgbe_main.o`, `sxgbe_desc.o`, `sxgbe_dma.o`, `sxgbe_core.o`, `sxgbe_mtl.o`, `sxgbe_mdio.o`, `sxgbe_ethtool.o`).

Risks: object order can matter for initcall/link symbol resolution in drivers. Conditional `samsung-sxgbe-y` is available but not populated here, so feature expansion must be kept coherent.

Test signals: module link includes all operation providers; missing-object failures catch filename drift.
