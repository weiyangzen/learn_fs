# sources/distributed-fs/ceph-client/drivers/mmc/host/sdhci-spear.c

## Purpose
This is a compact SDHCI platform driver for ST SPEAr SoCs. It manually allocates an SDHCI host, maps one MMIO resource, enables a single clock at 50 MHz, optionally requests GPIO card detect, applies a broken-ADMA quirk, and delegates normal SDHCI operation to generic ops.

## Important APIs, Types, And Functions
`struct spear_sdhci` stores the controller clock. The static `sdhci_pltfm_ops` table uses generic `sdhci_set_clock`, `sdhci_set_bus_width`, `sdhci_reset`, and `sdhci_set_uhs_signaling`. Lifecycle functions are `sdhci_probe()`, `sdhci_remove()`, `sdhci_suspend()`, and `sdhci_resume()`. The OF compatible is `st,spear300-sdhci`.

## Control Flow
Probe allocates `struct sdhci_host` with private clock storage, maps registers, sets hardware name and ops, obtains IRQ, applies `SDHCI_QUIRK_BROKEN_ADMA`, gets/enables the clock, tries to set it to 50 MHz, optionally requests card-detect GPIO through `mmc_gpiod_request_cd()`, registers the host, and stores drvdata. If card-detect GPIO probe defers or host add fails, it disables the clock.

Remove reads interrupt status to detect a dead controller, removes the host, and disables the clock. System suspend marks retune when needed, suspends the host, and disables the clock; resume enables the clock and resumes the host.

## State And Persistence
Software state is just the prepared clock in private data plus host quirks/caps initialized at probe. Hardware state is the SDHCI register block and clock rate. No runtime PM or custom tuning state exists.

## Dependencies And Integration Points
The driver depends on platform resources, clock framework, optional MMC slot GPIO card-detect descriptors, common SDHCI core, and OF platform binding. It does not use `sdhci-pltfm` allocation despite resembling it.

## Risks
The driver name is generic (`sdhci`) and local ops symbol is named `sdhci_pltfm_ops`, which can be confusing during maintenance. It sets the clock to 50 MHz but only logs failure at debug level. Broken ADMA disables a performance path. The suspend path uses `clk_disable()` rather than `clk_disable_unprepare()`, matching probe's prepared state but requiring balanced enable counts.

## Test Signals
Expected signals are successful OF probe, 50 MHz clock setup or acceptable debug warning, optional CD GPIO handling including `-EPROBE_DEFER`, clean dead-host removal, and system sleep/resume with retune.
