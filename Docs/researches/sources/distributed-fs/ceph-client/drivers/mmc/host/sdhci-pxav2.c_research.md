# sources/distributed-fs/ceph-client/drivers/mmc/host/sdhci-pxav2.c

## Purpose
This file supports Marvell PXA v1/v2 SDHCI-compatible platform controllers. It adds PXA-specific reset configuration, clock-gating and delay setup, 8-bit bus-width programming, legacy PXA168 SDIO erratum handling using a dummy CMD0 and pinctrl, platform/OF data parsing, and shared `sdhci-pltfm` PM integration.

## Important APIs, Types, And Functions
`struct sdhci_pxav2_host` stores a deferred SDIO request and optional pinctrl states. `pxav2_reset()` replays clock delay and clock-gating settings after full reset. `pxav1_readw()` works around SDH2/SDH4 host-version access on PXA168. `pxav1_irq()` and `pxav1_request_done()` implement the SDIO workaround. `pxav2_mmc_set_bus_width()` writes both SDHCI host-control bits and PXA `SD_CE_ATA_2` MMC width/card bits. Variant data selects `pxav1_sdhci_ops` or `pxav2_sdhci_ops`.

## Control Flow
Probe allocates through `sdhci_pltfm_init()`, enables IO and optional core clocks, installs baseline quirks for broken ADMA, broken timeout, and broken clock-base capabilities, selects variant from OF match data, parses platform or OF data for non-removable, 8-bit, delay, host caps, and PM caps, configures optional pinctrl states for the PXA168 SDIO workaround, then calls `sdhci_add_host()`.

For PXA v1 SDIO requests, completion is intercepted. If an SDIO direct or extended command succeeded, the driver resets the data port, records the original request, optionally switches CMD pin to GPIO-high, issues a dummy CMD0 to restart the clock, and delays `mmc_request_done()` until `pxav1_irq()` observes the dummy command completion. IRQ then clears command status, restores pinctrl default, clears `sdio_mrq`, and completes the original request.

## State And Persistence
Persistent state includes the optional pending `sdio_mrq`, pinctrl handles, clocks in `sdhci_pltfm_host`, platform flags/caps applied to `host->mmc`, and hardware clock-gating/delay registers replayed after full reset. The driver does not define custom suspend/resume beyond `sdhci_pltfm_pmops`.

## Dependencies And Integration Points
It depends on `sdhci-pltfm`, Marvell PXA platform data, OF properties such as `non-removable`, `bus-width`, and `mrvl,clk-delay-cycles`, optional pinctrl states `state_cmd_gpio` and `default`, and MMC SDIO command definitions.

## Risks
The SDIO erratum path is stateful and can deadlock request completion if the dummy CMD0 interrupt is lost or pinctrl states are missing on affected hardware. Reset-time delay/clock-gating programming depends on platform data and may not run for OF-created data unless populated correctly. Broken ADMA/timeout quirks reduce performance but avoid known failures.

## Test Signals
Test PXA v1 and v2 compatibles, SDIO direct/extended commands, dummy CMD0 completion, pinctrl transitions, 8-bit MMC bus-width programming, clock-delay OF properties, and suspend/resume through shared platform PM.
