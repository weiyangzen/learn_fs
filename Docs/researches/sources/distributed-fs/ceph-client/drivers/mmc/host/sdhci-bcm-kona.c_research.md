# sources/distributed-fs/ceph-client/drivers/mmc/host/sdhci-bcm-kona.c

## Purpose

`sdhci-bcm-kona.c` is the SDHCI platform driver for Broadcom Kona controllers. It wraps the generic SDHCI platform layer with Kona-specific top-level reset/init registers, GPIO-driven card-detect emulation, core clock setup, and quirks required by the Kona SD host integration.

## Important APIs, Types, And Functions

- `struct sdhci_bcm_kona_dev` contains `write_lock`, used to serialize delay-sensitive writes to card-detect emulation registers.
- `sdhci_bcm_kona_sd_reset()` asserts and deasserts `KONA_SDHOST_RESET` with polling and mandatory write spacing.
- `sdhci_bcm_kona_sd_init()` enables core interrupt propagation and AHB clock gating.
- `sdhci_bcm_kona_sd_card_emulate()` updates `KONA_SDHOST_CORESTAT` to synthesize controller card-detect and write-protect state from MMC GPIOs.
- `sdhci_bcm_kona_card_event()` mirrors GPIO card detect into controller status.
- `sdhci_bcm_kona_probe()` performs platform init, DT parsing, clock rate/enable, reset/init, `sdhci_add_host()`, and initial card insertion emulation.

## Control Flow

Probe calls `sdhci_pltfm_init()`, parses DT/MMC properties, requires `f_max`, obtains the core clock, sets the clock rate to `f_max`, enables it, marks non-removable cards as broken-card-detect, resets and initializes the top-level controller, and registers the SDHCI host. For non-removable cards it immediately emulates insertion; for removable cards it samples the GPIO after host registration and emulates insertion when present. Remove delegates SDHCI platform removal and disables the clock.

## State And Persistence Behavior

Runtime state is minimal: the platform private write mutex and enabled clock. Card-detect state is represented in hardware `CORESTAT`, not in long-lived driver state. There is no persistent storage.

## Dependencies And Integration Points

The file depends on `sdhci-pltfm.h`, generic SDHCI ops, DT/MMC parsing, common SDHCI platform PM ops, Linux clock framework, and MMC slot GPIO helpers. Device matching is through `"brcm,kona-sdhci"` and deprecated `"bcm,kona-sdhci"`.

## Risks And Edge Cases

- Back-to-back register writes require deliberate delays.
- `f_max` is mandatory; missing `max-frequency` in DT causes probe failure.
- Card detect is GPIO-driven but must be mirrored into controller status to generate SDHCI events.
- Non-removable devices force broken-card-detection and synthetic insertion.

## Test Signals

Signals include DT match/probe, required `max-frequency`, clock rate setting, reset timeout logging, card insertion/removal through GPIO, write-protect propagation, non-removable synthetic insertion, basic `mmc_test`, suspend/resume through `sdhci_pltfm_pmops`, and remove clock cleanup.
