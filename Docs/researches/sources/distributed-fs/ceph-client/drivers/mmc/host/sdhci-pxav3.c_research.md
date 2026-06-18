# sources/distributed-fs/ceph-client/drivers/mmc/host/sdhci-pxav3.c

## Purpose
This file supports Marvell PXA v3 and Armada 38x SDHCI platform controllers. It extends `sdhci-pltfm` with MBUS window setup, Armada-specific capability corrections, UHS signaling clock feedback workarounds, pinctrl switching for high-speed modes, regulator-aware power control, runtime PM, and 74-clock initialization generation.

## Important APIs, Types, And Functions
`struct sdhci_pxa` stores core/IO clocks, prior power mode, optional Armada SDIO3 config MMIO, and pinctrl states. `mv_conf_mbus_windows()` programs MBUS DRAM windows from `mv_mbus_dram_info()`. `armada_38x_quirks()` reads capabilities early, maps optional `conf-sdio3`, and adjusts 1.8/3.3 V and SDR/DDR support for Armada errata. `pxav3_reset()`, `pxav3_gen_init_74_clocks()`, `pxav3_set_uhs_signaling()`, `pxav3_set_power()`, and `pxav3_set_clock()` implement the custom SDHCI ops.

## Control Flow
Probe initializes a host with `sdhci_pxav3_pdata`, enables IO and optional core clocks, sets MMC busy-response and 1.8 V DDR capabilities, applies Armada 38x quirks and MBUS windows when compatible, parses OF or platform data, applies caps/quirks, obtains optional pinctrl states, enables runtime PM with autosuspend, adds the host, enables wakeup for SDIO IRQ if requested, and drops the runtime PM reference.

Clock changes choose default pins below 100 MHz and UHS pins at higher rates, then call generic `sdhci_set_clock()`. UHS signaling updates host-control2 mode bits and, when `conf-sdio3` exists, applies Armada FE-2946959 feedback-clock/inversion settings for SDR50/DDR50 versus other modes. Power changes use `sdhci_set_power_noreg()` and then update `vmmc` regulator OCR. The 74-clock hook generates initial clocks when moving from power-up to power-on and warns if the hardware interrupt bit does not clear.

## State And Persistence
Persistent state includes prepared clocks, current `power_mode`, optional mapped SDIO3 config register, pinctrl state pointers, runtime PM active/suspended state, and MBUS window registers. Platform data derived from OF is stored in `pdev->dev.platform_data` for reset-time delay replay.

## Dependencies And Integration Points
The driver depends on `sdhci-pltfm`, PXA platform data, OF matching for `mrvl,pxav3-mmc` and `marvell,armada-380-sdhci`, `linux/mbus.h`, pinctrl, regulators via MMC core, and runtime PM. It registers as `sdhci-pxav3`.

## Risks
Armada capability correction is tightly tied to DT resources; missing `conf-sdio3` disables SDR50/DDR50 to avoid errata. MBUS setup maps a second resource manually and must match SoC memory topology. Runtime suspend disables clocks and marks retune, so missed resume ordering can break high-speed modes. Pinctrl at the 100 MHz threshold can affect signal integrity.

## Test Signals
Use DT variants for PXA v3 and Armada 38x, verify MBUS windows, confirm UHS capability filtering with and without `conf-sdio3`, check pinctrl transitions around 100 MHz, regulator OCR changes, 74-clock generation, runtime autosuspend/resume, and SDIO wakeup.
