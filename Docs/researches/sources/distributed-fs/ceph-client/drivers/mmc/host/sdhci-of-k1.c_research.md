# sources/distributed-fs/ceph-client/drivers/mmc/host/sdhci-of-k1.c

Purpose: this is the SpacemiT K1/K3 SDHCI platform driver. It adds SoC-specific PHY, DLL, clock, reset, HS200/HS400, and enhanced-strobe handling around the generic SDHCI platform layer.

Important APIs, types, and functions: `struct spacemit_sdhci_host` holds `core` and `io` clocks, with `pltfm_host->clk` assigned to the IO clock. Helper functions `spacemit_sdhci_setbits`, `clrbits`, and `clrsetbits` perform read-modify-write on vendor registers. Key callbacks are `spacemit_sdhci_reset`, `spacemit_sdhci_set_uhs_signaling`, `spacemit_sdhci_set_clock`, `spacemit_sdhci_phy_dll_init`, HS400 transition callbacks, and `spacemit_sdhci_hs400_enhanced_strobe`.

Control flow: `spacemit_sdhci_probe()` selects K1 or K3 platform data from OF, initializes SDHCI private storage, parses MMC properties, applies SDHCI OF properties, installs HS400 callbacks when MMC is present, marks `MMC_CAP_NEED_RSP_BUSY`, enables required clocks and optional resets, then calls `sdhci_add_host()`. During reset-all, the PHY is enabled, pad drive and RX bias are configured, and MMC card mode is set when applicable. Clock changes select internal TX clock for slower SDR modes and normal TX path for faster modes.

State and persistence: state is volatile: enabled clocks, deasserted resets, vendor register bits for HS200/HS400/enhanced strobe, DLL lock state, and MMC caps. No persistent data is written. DLL configuration is reinitialized on HS400 transitions and enhanced-strobe enable.

Dependencies and integration points: the driver uses OF match data for `spacemit,k1-sdhci` and `spacemit,k3-sdhci`, clock names `core` and `io`, reset names `axi` and `sdh`, MMC HS400 callbacks, `sdhci-pltfm`, and standard SDHCI ops.

Risks: K1 marks broken 64-bit DMA while K3 does not; applying the wrong compatible can corrupt DMA. DLL lock waits only 100 us and warns on timeout but continues, so high-speed instability can be deferred to data errors. HS400 downgrade toggles PHY and mode bits with fixed delays, so ordering is important.

Test signals: probe with both compatibles, clock/reset failure paths, SDR/HS200/HS400 transitions, HS400 enhanced strobe on/off, eMMC and SDIO capability masking, DMA under K1 32-bit constraints, and warnings for failed DLL lock are key signals.
