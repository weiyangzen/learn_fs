# sources/distributed-fs/ceph-client/drivers/mmc/host/sdhci-of-hlwd.c

Purpose: this is a compact OF platform driver for the Nintendo Wii Hollywood SDHCI controller. It reuses the big-endian 32-bit byte-swapped SDHCI accessors and adds a small post-write delay required by the hardware.

Important APIs, types, and functions: the file defines `sdhci_hlwd_writel`, `sdhci_hlwd_writew`, and `sdhci_hlwd_writeb`, each delegating to `sdhci_be32bs_*` and then calling `udelay(SDHCI_HLWD_WRITE_DELAY)`. `sdhci_hlwd_ops` supplies the SDHCI core callbacks, while `sdhci_hlwd_pdata` declares 32-bit DMA address and size quirks.

Control flow: `sdhci_hlwd_probe()` simply calls `sdhci_pltfm_init_and_add_host()` with the local platform data. Once registered, generic SDHCI handles clock, bus width, reset, and UHS signaling. Remove and PM use the shared `sdhci_pltfm_remove` and `sdhci_pltfm_pmops`.

State and persistence: the driver owns no private data and persists nothing. Runtime state is the generic SDHCI host plus hardware registers. The only behavioral state is the enforced delay after every write callback.

Dependencies and integration points: it integrates through compatible string `nintendo,hollywood-sdhci`, `sdhci-pltfm`, MMC core, and the platform bus. It depends on the existing big-endian byte-swapped accessor helpers.

Risks: the critical risk is write-posting or bus timing sensitivity; removing or shortening the delay can corrupt controller operation. The driver assumes generic SDHCI reset/clock/UHS handling is sufficient and does not parse custom OF properties. DMA behavior depends on the two 32-bit quirks matching the hardware.

Test signals: successful probe on Wii hardware or an accurate emulator, stable card detect/enumeration, PIO/DMA read/write tests, suspend/resume through platform PM, and absence of intermittent errors after register writes are the main signals.
