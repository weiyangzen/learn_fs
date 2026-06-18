# sources/distributed-fs/ceph-client/drivers/mmc/host/sdhci-pic32.c

## Purpose
This file is the Microchip PIC32 platform SDHCI driver. It wraps `sdhci-pltfm` allocation with PIC32-specific clocks, bus-width handling, shared-bus selection, write-protect behavior, platform DMA setup, and OF matching for `microchip,pic32mzda-sdhci`.

## Important APIs, Types, And Functions
`struct pic32_sdhci_priv` stores the platform device and two clocks: `sys_clk` and `base_clk`. `pic32_sdhci_get_max_clock()` reports `base_clk` rate. `pic32_sdhci_set_bus_width()` updates SDHCI host-control width bits and always applies the PIC32 card-detect errata settings `SDHCI_CTRL_CDSSEL` and not `SDHCI_CTRL_CDTLVL`. `pic32_sdhci_get_ro()` always returns writable because hardware write-protect is unstable. `pic32_sdhci_probe()`, `pic32_sdhci_remove()`, and `pic32_sdhci_driver` implement the platform lifecycle.

## Control Flow
Probe calls `sdhci_pltfm_init()` with `sdhci_pic32_pdata`, obtains the `sdhci_pltfm_host` and private PIC32 data, optionally calls board `setup_dma()` with ADMA FIFO thresholds, gets/enables `sys_clk`, gets/enables `base_clk`, parses OF MMC properties, checks slot type from capabilities, configures shared-bus clock/IRQ pin selection if needed, then registers the host with `sdhci_add_host()`. Remove checks whether the controller appears dead by reading all-ones interrupt status, removes the host, and disables both clocks.

## State And Persistence
Persistent software state is limited to the two prepared clocks in private data. Hardware state includes shared-bus pin-selection bits and host-control card-detect select/test bits. Quirks are fixed through `sdhci_pic32_pdata`: no HISPD bit and no 1.8 V signaling.

## Dependencies And Integration Points
The driver depends on `sdhci-pltfm`, common SDHCI helpers, Microchip platform data for optional DMA setup, two named clocks, and MMC OF parsing. Integration is through the platform driver and OF compatible table.

## Risks
The error path disables `base_clk` in `err_base_clk` even when failures can occur before it is enabled, so clock pointer validity depends on branch ordering. The private pointer in remove is cast with `sdhci_priv(host)` even though probe accessed PIC32 data through `sdhci_pltfm_priv()`, which is a pattern worth reviewing because `sdhci_priv()` returns the platform wrapper, not the private tail. Hardware write-protect is intentionally ignored, so media WP tests cannot rely on this driver.

## Test Signals
Probe should show successful host registration, correct `base_clk` max frequency, shared-bus slot operation, stable card detect despite errata bits, DMA setup callback execution on platform-data systems, and clean clock disable on removal.
