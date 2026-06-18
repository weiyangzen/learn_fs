# sources/distributed-fs/ceph-client/drivers/mmc/host/sdhci-omap.c

Purpose: this driver supports TI OMAP-family SDHCI/MMCHS controllers, including OMAP2/3/4/5, DRA7, K2G, AM335, and AM437 variants. It adapts offset differences, voltage/PBIAS handling, iodelay pinctrl, temperature-aware tuning, runtime PM context save/restore, wake IRQs, and special reset behavior to the SDHCI core.

Important APIs, types, and functions: `struct sdhci_omap_data` holds register offsets and flags per compatible. `struct sdhci_omap_host` stores base pointers, regulators, current timing/power/bus state, pinctrl states, wake IRQ, tuning flag, and context registers. Key functions include `sdhci_omap_start_signal_voltage_switch`, `sdhci_omap_execute_tuning`, `sdhci_omap_card_busy`, `sdhci_omap_set_ios`, `sdhci_omap_set_clock`, `sdhci_omap_enable_dma`, `sdhci_omap_reset`, `sdhci_omap_irq`, and runtime PM context save/restore.

Control flow: `sdhci_omap_probe()` gets match data, creates an SDHCI platform host, adjusts `host->ioaddr` and `mapbase` to the SDHCI register offset while preserving OMAP base access, parses OF/MMC properties, applies DRA7 ES1.x frequency limits, configures clocks and PBIAS, enables runtime PM before setup so the PM domain can initialize registers, derives voltage capabilities from regulators, installs MMC callbacks, chooses external DMA if needed, configures caps, sets up host, builds iodelay pinctrl state table, adds the host, and registers optional wake IRQ.

State and persistence: driver state tracks bus mode, power mode, timing, PBIAS enabled status, tuning-in-progress, and context register snapshots. Runtime suspend saves OMAP registers, selects idle pinctrl, may request retune, and runtime resume restores registers before resuming SDHCI. No durable state is written.

Dependencies and integration points: integrates with `sdhci-pltfm`, PM runtime/autosuspend, TI PM domains, regulators `pbias` and `vqmmc`, pinctrl named by timing modes, thermal zone `cpu_thermal`, wake IRQ named `wakeup`, GPIO card-detect/write-protect helpers, and OF compatibles under `ti,*-sdhci`.

Risks: tuning depends on CPU thermal readings and a two-stage DLL search; unavailable thermal zone fails tuning. During tuning, data reset is suppressed and IRQ filtering manually handles command errors, so race-prone interrupt behavior is possible. PBIAS/vqmmc voltage capability derivation and 3.0 V/3.3 V quirk handling must match board regulators. Context restore order is explicitly important for HCTL and can break after register changes.

Test signals: cover every compatible offset, voltage switching with PBIAS/vqmmc, DRA7 iodelay state selection, high-speed tuning across temperatures, runtime suspend/resume with retune, wake IRQ behavior, external DMA selection, card busy detection, erase timeout handling, and special reset timeout logging.
