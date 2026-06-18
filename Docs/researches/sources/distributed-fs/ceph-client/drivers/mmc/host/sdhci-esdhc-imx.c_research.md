# sources/distributed-fs/ceph-client/drivers/mmc/host/sdhci-esdhc-imx.c

## Purpose

`sdhci-esdhc-imx.c` is the large Freescale/NXP i.MX and S32 eSDHC/uSDHC platform driver. It adapts non-standard eSDHC/uSDHC register layout and behavior to the SDHCI core, covers many SoC generations, implements manual and standard tuning, HS200/HS400/HS400ES, CQHCI, pinctrl speed states, card-detect/write-protect policy, clock and power management, and numerous errata workarounds.

## Important APIs, Types, And Functions

- `struct esdhc_soc_data` maps compatibles to flags and quirks such as USDHC, manual/standard tuning, CAP1 availability, HS200/HS400/HS400ES, CQHCI, PM QoS, lost-state PM, broken Auto CMD23, and errata flags.
- `struct esdhc_platform_data` stores board-level WP/CD type, delay-line/tuning/strobe settings, and saved tuning values.
- `struct pltfm_imx_data` stores SoC data, board data, clocks, pinctrl states, actual clock, card type, multiblock workaround state, DDR state, and PM QoS request.
- Register accessors translate between SDHCI expectations and eSDHC/uSDHC registers: `esdhc_readl_le()`, `esdhc_writel_le()`, `esdhc_readw_le()`, `esdhc_writew_le()`, `esdhc_readb_le()`, and `esdhc_writeb_le()`.
- `usdhc_execute_tuning()`, `esdhc_reset_tuning()`, `esdhc_prepare_tuning()`, `esdhc_executing_tuning()`, and `usdhc_auto_tuning_mode_sel_and_en()` implement tuning.
- `esdhc_set_uhs_signaling()`, `esdhc_set_strobe_dll()`, and `esdhc_hs400_enhanced_strobe()` implement high-speed timing modes.
- `esdhc_cqe_enable()` and `esdhc_cqhci_ops` integrate command queueing.

## Control Flow

Probe initializes an SDHCI platform host with i.MX pdata, reads match data, applies SoC quirks and PM QoS, gets and enables `per`, `ipg`, and `ahb` clocks, records the base clock, obtains pinctrl speed states, configures USDHC-specific caps and tuning hooks, applies SoC flags for ADMA errata, HS modes, broken Auto CMD23, HS400ES, and optional CQHCI. It then parses DT board properties and generic MMC/SDHCI properties, initializes hardware registers through `sdhci_esdhc_imx_hwinit()`, adds the host, configures wake capability, and enables runtime PM autosuspend.

The accessor layer rewrites present-state bits, capabilities, current limits, interrupt status bits, transfer mode, command writes, clock control, host control, reset behavior, and watermark levels. For older eSDHC it shadows transfer mode and combines it with command writes; for USDHC it uses `MIX_CTRL` and maps Auto CMD23 bits.

Manual tuning scans delay-cell windows, programs the center of the largest passing window, and sets auto-tuning margins. Standard tuning configures controller tuning registers and handles reset/restore paths. High-speed signaling toggles DDR/HS400/feedback clock bits, selects pinctrl states, and configures strobe DLL for HS400.

PM paths save tuning for powered SDIO wake devices, enable/disable IRQ wake, select pinctrl sleep/default states, suspend/resume SDHCI and CQHCI, gate clocks at runtime suspend, restore clock rate when lost, reinitialize hardware after low-power state, and replay saved tuning.

## State And Persistence Behavior

All state is runtime memory. `pltfm_imx_data` persists SoC flags, board properties, tuning save values, clock handles/rates, current DDR and multiblock workaround state, and PM QoS request. `boarddata.saved_tuning_delay_cell` survives suspend within driver memory and is restored for SDIO keep-power cases. `actual_clock` is saved across runtime suspend to restore the clock. Hardware state can be lost in low-power modes and is reinitialized from driver state.

## Dependencies And Integration Points

The driver integrates DT compatible data, `mmc_of_parse()`, `sdhci_get_property()`, GPIO CD/WP helpers, pinctrl speed states, three clocks, runtime/system PM, CPU latency QoS, CQHCI, SDHCI platform helpers, generic MMC tuning helpers, and eMMC reset/HS400 host callbacks. It includes `sdhci-cqhci.h` so full resets deactivate CQHCI safely.

## Risks And Edge Cases

- The shared static `sdhci_esdhc_ops.platform_execute_tuning` is assigned during probe when a manual-tuning SoC is seen; mixed SoC instances with different tuning flags deserve scrutiny.
- The accessors contain many register translations and side effects; regressions can appear as generic SDHCI failures.
- Errata flags strongly affect ADMA, Auto CMD23, 1.8 V maximum clocks, and low-power state loss.
- Tuning and saved tuning are timing-sensitive and differ for SD, eMMC, and SDIO.
- Runtime suspend gates all clocks and may remove PM QoS; resume error paths must re-enable clocks in the right order and remove PM QoS on failure.
- CQHCI enable must drain pending buffer data and clear HALT after runtime resume to avoid queue hangs.

## Test Signals

Coverage should include all major compatible families, DT parsing of tuning/pinctrl/strobe properties, SD/eMMC/SDIO card types, GPIO and controller WP/CD, PIO and DMA transfers, Auto CMD23 and RPMB reliable write behavior, manual and standard tuning, SDR50/SDR104/HS200/HS400/HS400ES, CQE I/O and reset, suspend/resume with SDIO wake, runtime PM autosuspend, low-power state loss, and errata-limited 1.8 V clocks.
