# sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/stmmac_platform.c

Purpose: platform and device-tree glue for STMMAC. It parses OF properties into `plat_stmmacenet_data`, gathers MMIO/IRQ resources, exposes devres probe helpers, and manages platform clocks during runtime and system PM.

Important APIs and functions: `stmmac_probe_config_dt()` parses MAC address, PHY mode, legacy `mac-mode`, `phy-handle`, max speed, bus alias, CSR clock, deprecated PHY address, FIFO sizes, DMA settings, core-compatible capabilities, AXI, MTL queues, clocks, PTP ref clock, and resets. `stmmac_mtl_setup()` parses RX/TX queue count, scheduling, DCB/AVB modes, priorities, routes, DMA channel mapping, weights, and CBS parameters. `stmmac_mdio_setup()` decides whether to allocate/register MDIO data. `stmmac_get_platform_resources()` gathers named IRQs, optional per-queue IRQs, and MMIO. Probe/remove helpers bridge platform wrappers to `stmmac_dvr_probe/remove()`. `stmmac_pltfr_pm_ops` binds common sleep and runtime PM.

Control flow: wrapper drivers typically call DT config, resource gathering, and then `stmmac_pltfr_probe()` or its devm variant. DT parsing allocates platform data, fills bus/PHY/MDIO/core/DMA/AXI/MTL fields, enables clocks, resolves PTP reference rate, and obtains resets. Error paths release OF refs and clocks. Runtime suspend/resume toggles bus clocks. Noirq suspend/resume disables/restores PTP ref clock when running without WoL.

State and persistence: persistent settings live in `plat_stmmacenet_data`: queue configs, DMA modes, filter sizes, PTP clock rate, MDIO nodes, clocks, resets, wrapper callbacks, and BSP private data. Static `bus_id` generates fallback Ethernet IDs. Devres actions clean clocks and OF nodes.

Dependencies and integration: platform, OF, MDIO, clocks, resets, PM runtime, net address APIs, common STMMAC probe/remove/suspend/resume, and wrapper-provided `init/exit/clks_config` hooks.

Risks and test signals: DT compatibility handling is broad; property precedence and cleanup are common failure points. MTL setup requires child-node counts to match queue counts. Clock behavior differs for `snps,dwc-qos-ethernet-4.10`. Test with probe deferral, MDIO modes, multi-queue DTs, PTP clock selection, suspend/resume with and without WoL, and wrapper devres removal.
