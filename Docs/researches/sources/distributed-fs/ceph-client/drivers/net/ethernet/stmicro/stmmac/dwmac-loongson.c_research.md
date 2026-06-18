<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac-loongson.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac-loongson.c

## Purpose
`dwmac-loongson.c` is a PCI glue driver for Loongson GMAC/GNET controllers built around Synopsys GMAC cores with Loongson-specific DMA interrupt layout, reset behavior, PCI/OF/ACPI configuration, and optional multi-channel MSI routing.

## Important APIs, Types, and Functions
- `struct loongson_data` records the custom Loongson core ID, multi-channel capability, and device pointer.
- `loongson_default_data()`, `loongson_gmac_data()`, and `loongson_gnet_data()` initialize stmmac platform defaults for GMAC and integrated-GNET variants.
- `loongson_dwmac_dma_init_channel()` and `loongson_dwmac_dma_interrupt()` override DMA ops for Loongson multi-channel cores.
- `loongson_dwmac_setup()` patches `synopsys_id`, installs custom DMA ops, and fills `mac_device_info` link/MII capabilities.
- `loongson_dwmac_msi_config()` maps common, RX, and TX vectors for multi-MSI mode.
- `loongson_dwmac_dt_config()` and `loongson_dwmac_acpi_config()` choose IRQ, MDIO, bus id, and PHY mode depending on firmware interface.

## Control Flow
PCI probe allocates platform data, enables the PCI function, maps BAR0, records the Loongson core version from `GMAC_VERSION`, runs per-device setup from `driver_data`, computes FIFO sizes, then parses either DT or ACPI resources. Multi-channel devices try to allocate per-channel MSI vectors but continue with the common MAC IRQ if allocation fails. Finally `stmmac_dvr_probe()` owns the netdev. Remove reverses stmmac registration, DT MDIO node references, MSI allocation, and PCI enablement.

## State and Persistence
Driver state is per-PCI-device and held in devm allocations plus `plat->bsp_priv`. Hardware state includes DMA bus mode, interrupt masks/status, PCI MSI vectors, and PHY autonegotiation. No persistent storage is used.

## Dependencies and Integration Points
The file depends on PCI, OF IRQ, ACPI fallback through normal PCI IRQs, `stmmac_libpci`, `dwmac1000` DMA ops, GMAC register definitions, and phylib. It integrates with stmmac by providing custom `mac_setup`, `fix_soc_reset`, suspend/resume callbacks, and optional multi-MSI resource arrays.

## Risks and Edge Cases
- Loongson custom IDs `0x10` and `0x12` must be detected before stmmac core setup or the wrong DMA model is selected.
- Multi-channel V1 disables TX checksum offload on channels 1..7 because only channel 0 supports it.
- MSI allocation failures are tolerated but can reduce interrupt isolation and performance.
- The DMA reset can take up to two seconds; missing PHY clock is reported when reset is already stuck.
- GNET speed-up to 1000 Mbps restarts autonegotiation as a hardware workaround.

## Test Signals
Test coverage should include PCI probe/remove for GMAC1, GMAC2, and GNET IDs; DT and ACPI boot paths; multi-channel TX/RX interrupt accounting; MSI fallback; DMA soft reset timeout behavior; and GNET 10/100 to 1000 Mbps renegotiation. `ethtool -S` interrupt counters and traffic across all enabled queues are strong runtime signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac-loongson.c -->
