# sources/distributed-fs/ceph-client/drivers/net/ethernet/samsung/sxgbe/sxgbe_platform.c

Purpose: Provides the platform-driver wrapper for SXGBE. It parses device-tree platform data, maps MMIO resources, invokes the common SXGBE probe/remove entry points, maps IRQs, and exposes PM callbacks.

Important APIs and flow: `sxgbe_probe_config_dt()` reads PHY interface mode, ethernet alias bus id, allocates MDIO bus data and DMA config, and reads Samsung PBL/burst-map properties. `sxgbe_platform_probe()` maps resource 0, allocates DT platform data, calls `sxgbe_drv_probe()`, parses common, TX queue, RX queue, and LPI IRQs from the DT node, reads the MAC address, stores the netdev in platform data, and returns. `sxgbe_platform_remove()` calls `sxgbe_drv_remove()`. PM wrappers call common suspend/resume/freeze/restore stubs. `sxgbe_register_platform()` and `sxgbe_unregister_platform()` are used by `sxgbe_main.c` module init/exit.

State and dependencies: Platform state is `struct sxgbe_plat_data` allocated with devm, a mapped `ioaddr`, IRQ mappings on each queue, and the netdev stored with `platform_set_drvdata()`. It depends on OF helpers, platform resource mapping, SXGBE common probe/remove functions, and compatible string `samsung,sxgbe-v2.0a`.

Risks and test signals: Probe calls the common driver before IRQ numbers are parsed, so error paths must be checked carefully because `platform_get_drvdata()` is still old/null until late success. IRQ mapping disposal on partial TX/RX loops is delicate. Tests should cover DT property variants, missing IRQs at every position, failed common probe, MAC address absent/present, remove after successful probe, and PM callback routing.
