# sources/distributed-fs/ceph-client/drivers/mmc/host/sdhci-of-sparx5.c

Purpose: this is the Microchip Sparx5 SDHCI OF driver. It configures Sparx5-specific CPU syscon registers, eMMC mode/reset bits, optional card clock delay, DMA cache attributes, and ADMA descriptor splitting for 128 MiB boundaries.

Important APIs, types, and functions: `struct sdhci_sparx5_data` stores the host, CPU control regmap, and `delay_clock`. `sdhci_sparx5_adma_write_desc` mirrors other DWC-derived boundary splitting logic. `sparx5_set_cacheable` programs ACP cache attributes, `sparx5_set_delay` programs `MSHC_DLY_CC`, `sdhci_sparx5_set_emmc` maintains the `IS_EMMC` bit, and `sdhci_sparx5_reset_emmc` toggles eMMC reset with conservative delays.

Control flow: `sdhci_sparx5_probe()` initializes SDHCI platform data and private storage, increases ADMA descriptor capacity, enables the `core` clock, reads optional `microchip,clock-delay`, parses SDHCI/MMC properties, obtains a syscon regmap by compatible string, applies clock delay, performs eMMC reset and capability masking for non-removable media, adds the host, and optionally forces un-cached ACP access for DMA when coherent memory declaration is enabled.

State and persistence: all state is volatile hardware state plus devm-managed private data. Reset callbacks reapply `IS_EMMC` after generic SDHCI reset. The driver does not persist data outside registers.

Dependencies and integration points: uses `sdhci-pltfm`, OF compatible `microchip,dw-sparx5-sdhci`, syscon compatible `microchip,sparx5-cpu-syscon`, `devm_clk_get_enabled("core")`, DMA mask inspection, and MMC removable-card helpers.

Risks: the syscon lookup by global compatible rather than a phandle can be fragile if multiple system controllers exist. Delay-clock values outside 1..15 are silently ignored, and `delay_clock` is not explicitly initialized before the conditional test. Non-removable detection drives eMMC reset and SD/SDIO capability removal, so board descriptions must be accurate. DMA cache forcing is conditional on both DMA flags and `CONFIG_DMA_DECLARE_COHERENT`.

Test signals: verify non-removable eMMC reset and mode bit persistence, removable SD path without eMMC masking, `microchip,clock-delay` programming, DMA crossing 128 MiB boundaries, coherent-DMA cache setting, syscon lookup failure, reset behavior, and debug version/type register logs.
