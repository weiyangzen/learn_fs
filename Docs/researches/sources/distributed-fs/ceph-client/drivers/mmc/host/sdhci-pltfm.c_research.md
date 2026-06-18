# sources/distributed-fs/ceph-client/drivers/mmc/host/sdhci-pltfm.c

## Purpose
This file is the reusable platform/OF helper layer for SDHCI host drivers. It allocates and initializes `struct sdhci_host` for memory-mapped platform devices, applies common properties and compatibility quirks, registers/removes hosts, and provides shared system-sleep PM operations.

## Important APIs, Types, And Functions
Exported APIs include `sdhci_pltfm_clk_get_max_clock()`, `sdhci_get_property()`, `sdhci_pltfm_init()`, `sdhci_pltfm_init_and_add_host()`, `sdhci_pltfm_remove()`, `sdhci_pltfm_suspend()`, `sdhci_pltfm_resume()`, and `sdhci_pltfm_pmops`. Static helpers include `sdhci_wp_inverted()` and `sdhci_get_compatibility()`. The default ops table uses generic clock, bus-width, reset, and UHS signaling callbacks.

## Control Flow
`sdhci_pltfm_init()` maps MMIO resource 0, obtains IRQ 0, allocates an SDHCI host with room for `struct sdhci_pltfm_host` plus caller private data, assigns IO address, IRQ, hardware name, ops, and quirks, and stores the host in platform drvdata. `sdhci_get_property()` reads generic properties: auto CMD12, 1-bit-only/bus-width, inverted write protect, broken card detect, no 1.8 V, Freescale compatibility quirks, and optional clock-frequency into `pltfm_host->clock`. `sdhci_pltfm_init_and_add_host()` combines init, property parsing, and `sdhci_add_host()`.

## State And Persistence
The helper initializes persistent platform state in `struct sdhci_pltfm_host`, especially `clk`, `clock`, and `xfer_mode_shadow` for BE byte-swapper users. It persists device properties as SDHCI quirks and quirks2. PM suspend marks retune needed unless tuning mode 3, suspends the host, and disables `pltfm_host->clk`; resume reenables the clock and resumes the host.

## Dependencies And Integration Points
It is used by many platform drivers in the same directory. It depends on Linux device properties, platform resource APIs, optional PowerPC machine checks for legacy WP inversion, clock framework, and SDHCI core APIs.

## Risks
Callers must initialize `pltfm_host->clk` before using shared PM ops, otherwise suspend/resume will operate on a null or invalid clock. Property parsing mutates quirks before host setup, so duplicate or conflicting board-specific parsing can change behavior. Legacy Freescale compatibility quirks are applied by string matching and can affect timeout/DMA behavior globally for those compatibles.

## Test Signals
Coverage should include successful platform probe through `sdhci_pltfm_init_and_add_host()`, property-to-quirk mapping, dead-host removal when interrupt status is all ones, suspend/resume retune marking, and clock disable/enable ordering with drivers that use `sdhci_pltfm_pmops`.
