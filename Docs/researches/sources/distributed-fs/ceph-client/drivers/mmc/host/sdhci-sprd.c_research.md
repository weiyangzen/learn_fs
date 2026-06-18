# sources/distributed-fs/ceph-client/drivers/mmc/host/sdhci-sprd.c

## Purpose
This file supports Spreadtrum/Unisoc R11 SDHCI controllers. It implements non-standard register access rules, custom clock division and PHY DLL handling, PHY delay tuning from device tree, software queue integration, regulator/pinctrl voltage switching, HS400 enhanced strobe, SD high-speed command/data tuning, and runtime PM.

## Important APIs, Types, And Functions
`struct sdhci_sprd_host` stores version, three clocks, pinctrl states, base rate, a backup of host flags, and per-timing PHY delay values. `sdhci_sprd_ops` overrides read/write accessors, clock, power, min/max clock, UHS signaling, hardware reset, timeout count, read-only state, and request completion. Important helpers include `sdhci_sprd_calc_div()`, `_sdhci_sprd_set_clock()`, `sdhci_sprd_enable_phy_dll()`, `sdhci_sprd_set_uhs_signaling()`, `sdhci_sprd_voltage_switch()`, `sdhci_sprd_hs400_enhanced_strobe()`, `sdhci_sprd_tuning()`, and `sdhci_sprd_phy_param_parse()`.

## Control Flow
Probe allocates through `sdhci_pltfm_init()` with Spreadtrum quirks, sets a 64-bit DMA mask, overrides MMC host ops for request handling, HS400 ES, SD high-speed tuning, and voltage switch, parses MMC OF properties, sets atomic request handling for non-removable cards or deferred completion for removable cards, parses PHY delay properties, obtains optional pinctrl states, gets/enables `sdio`, `enable`, and optional `2x_enable` clocks, initializes DLL backup mode, enables runtime PM, enables SDHCI v4 mode, reads caps but clears UHS-I capability bits so DT controls exposure, gets regulators, performs `sdhci_setup_host()`, initializes `mmc_hsq`, adds the host, and arms autosuspend.

Clock programming computes the Spreadtrum divider, writes SDHCI clock control through `sdhci_enable_clk()`, toggles automatic inner/outer clock bits above 400 kHz, updates DLL inversion for low clock rates, and enables the PHY DLL above 52 MHz. UHS signaling writes non-standard HS200/HS400/HS400ES mode encodings and applies per-timing PHY delay. SD high-speed tuning sweeps 0..255 delay samples, records pass/fail, selects the middle of the longest passing range, and writes the resulting delay field.

## State And Persistence
Persistent state includes cached `base_rate`, `flags` backup used to restore auto CMD23 behavior per request, PHY delay table, pinctrl state, and runtime PM state. Hardware state includes DLL config/delay registers, debounce backup bits, busy-position auto-clock bits, non-standard software reset bit 3, and regulator state. Runtime suspend/resume gates clocks and `mmc_hsq`.

## Dependencies And Integration Points
The driver depends on `sdhci-pltfm`, `mmc_hsq`, pinctrl, regulators, OF properties `sprd,phy-delay-*`, runtime PM, and SDHCI v4 support. It registers for `sprd,sdhci-r11`.

## Risks
Register access is non-standard: max-current is synthetic, block-count writes are ignored, interrupt enables are masked, and reset bit 3 must be preserved except for explicit hardware reset. Generic SDHCI changes can break these assumptions. Tuning allocates a 256-byte result buffer and sends many status/switch commands, so failures can be timing/card dependent. Auto CMD23 is disabled per request when CMD23 stuff bits conflict with v4.10 ARGUMENT2 semantics.

## Test Signals
Validate removable and non-removable paths, HSQ request finalization, voltage switch pinctrl/regulator behavior, HS400 enhanced strobe delay, SD high-speed tuning range selection, DLL lock logs above 52 MHz, auto CMD23 disable for stuffed CMD23, runtime PM clock gating, and hardware reset behavior.
