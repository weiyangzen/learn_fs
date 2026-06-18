# sources/distributed-fs/ceph-client/drivers/mmc/host/sdhci-cadence.c

## Purpose

`sdhci-cadence.c` is the SDHCI platform driver for Cadence SD4HC-compatible SD/SDIO/eMMC controllers, including Socionext UniPhier, Pensando Elba, Mobileye EyeQ, and generic Cadence compatibles. It handles Cadence HRS registers, PHY delay programming from DT, software tuning, eMMC mode selection, HS400 enhanced strobe, optional eMMC reset, and Elba byte-lane write control.

## Important APIs, Types, And Functions

- `struct sdhci_cdns_priv` stores HRS and optional write-control MMIO bases, write lock, enhanced-strobe state, private write callback, optional reset control, and parsed PHY parameters.
- `sdhci_cdns_write_phy_reg()`, `sdhci_cdns_phy_param_parse()`, and `sdhci_cdns_phy_init()` parse and program Cadence PHY delay properties.
- `sdhci_cdns_set_tune_val()`, `sdhci_cdns_execute_tuning()`, and `sdhci_cdns_tune_blkgap()` implement software tuning.
- `sdhci_cdns_set_uhs_signaling()` maps MMC timings to Cadence eMMC modes in HRS06 and falls back to generic SDHCI signaling for SD mode.
- Elba-specific `elba_priv_writel()`, `elba_write_l()`, `elba_write_w()`, and `elba_write_b()` serialize byte-lane enables before writes.
- `sdhci_cdns_hs400_enhanced_strobe()` and `sdhci_cdns_mmc_hw_reset()` expose MMC host callbacks.

## Control Flow

Probe enables the controller clock, selects match-specific driver data, counts PHY properties, initializes an SDHCI platform host with enough private storage for parsed parameters, stores HRS base and shifts `host->ioaddr` to the SDHCI SRS base, installs the HS400ES callback, runs optional match init such as Elba write-control setup, enables SDHCI v4 mode, reads capabilities with a forced SDHCI 4.00 version, parses DT/MMC properties, parses and writes PHY delay parameters, optionally gets an eMMC reset control and wires `card_hw_reset`, then calls `sdhci_add_host()`.

Tuning scans up to 40 Cadence tune values, records the longest passing streak from `mmc_send_tuning()`, programs the center point, and for HS200 tries read block-gap coefficients using `mmc_read_tuning()`. Resume re-enables the clock, reprograms PHY parameters, and resumes the SDHCI host.

## State And Persistence Behavior

Parsed PHY parameters persist in flexible-array private storage for the device lifetime and are replayed on resume. `enhanced_strobe` mirrors current MMC IOS state. Elba write serialization state is just a spinlock plus write-control base.

## Dependencies And Integration Points

Dependencies include SDHCI platform support, DT properties for PHY delays and compatibles, Linux reset controls, clock framework, bitfield helpers, poll helpers, MMC tuning helpers, and generic SDHCI v4 capability handling. Match data controls quirks and Elba-specific accessors.

## Risks And Edge Cases

- PHY writes poll HRS ACK with very short timeouts; slow or wedged hardware causes probe/resume failure.
- Tuning assumes the usable tune register range is 0-39 despite a wider field.
- Elba byte-lane control requires strict write ordering under `wrlock`; direct writes that bypass it can corrupt partial-register writes.
- HS400 enhanced-strobe state must stay synchronized with HRS06 mode transitions.
- Resume replays PHY setup before `sdhci_resume_host()`.

## Test Signals

Test generic and SoC-specific compatibles, all DT PHY delay properties, SDR104 and HS200 tuning, HS200 block-gap tuning, HS400 and HS400ES transitions, optional eMMC reset pulse timing, Elba byte/word/long register writes, suspend/resume PHY replay, and build coverage with `CONFIG_MMC_SDHCI_CADENCE`.
