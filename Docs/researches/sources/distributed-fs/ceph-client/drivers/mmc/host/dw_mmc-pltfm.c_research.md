# sources/distributed-fs/ceph-client/drivers/mmc/host/dw_mmc-pltfm.c

Purpose: provides the common platform-device wrapper for the shared DesignWare MMC core and includes a small Intel/Altera SoCFPGA timing initialization hook.

Important APIs and functions: exported `dw_mci_pltfm_register` allocates, maps, and probes a `dw_mci` host for platform drivers. Exported `dw_mci_pltfm_remove` calls shared removal. `dw_mci_socfpga_priv_init` programs SoCFPGA clock phase through an Altera system-manager regmap. `dw_mci_pltfm_probe` selects optional drv_data from OF match data.

Control flow: platform registration obtains IRQ 0, stores variant drv_data, maps MMIO resource 0, records the physical register base for external DMA, stores host in platform drvdata, and calls `dw_mci_probe`. Generic compatibles use no drv_data; SoCFPGA uses an init hook that reads `clk-phase-sd-hs` from the phase map, looks up `altr,sysmgr-syscon`, converts phase degrees to 45-degree steps, and writes sysmgr timing fields.

State and persistence: no wrapper-private state beyond the allocated `dw_mci`. SoCFPGA phase programming persists in system-manager registers while the platform is powered.

Dependencies and integration points: depends on platform devices, OF matching, `dw_mmc.h`, `dw_mmc-pltfm.h`, Altera sysmgr lookup, regmap, shared PM ops, and the shared DW core.

Risks: `dw_mci_pltfm_probe` assumes `of_match_node` returns a match when an OF node exists. SoCFPGA sysmgr phase setup logs warnings and continues if regmap lookup fails, so requested clock phase may be silently absent. Phase values are integer-divided by 45 degrees.

Test signals: generic `snps,dw-mshc`, SoCFPGA, and Pistachio DT probes; IRQ/resource mapping failures; external DMA physical address use; sysmgr phase register updates; and shared DW transfer/PM tests.
