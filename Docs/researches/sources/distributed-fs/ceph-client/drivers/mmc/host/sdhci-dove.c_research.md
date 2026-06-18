# sources/distributed-fs/ceph-client/drivers/mmc/host/sdhci-dove.c

## Purpose

`sdhci-dove.c` is the compact SDHCI platform driver for Marvell Dove SoC SDHCI controllers. It supplies a few register-read overrides and quirks around missing registers, voltage capabilities, timeout behavior, and DMA, then delegates most behavior to the generic SDHCI platform core.

## Important APIs, Types, And Functions

- `sdhci_dove_readw()` returns zero for missing `SDHCI_HOST_VERSION` and `SDHCI_SLOT_INT_STATUS` registers and otherwise performs a normal 16-bit read.
- `sdhci_dove_readl()` masks `SDHCI_CAN_VDD_300` from the capabilities register.
- `sdhci_dove_ops` wires read overrides plus generic clock, bus-width, reset, and UHS signaling functions.
- `sdhci_dove_pdata` declares quirks for non-simultaneous VDD/power, no busy IRQ, broken timeout, forced DMA, and no HISPD bit.
- `sdhci_dove_probe()` initializes the platform host, enables the clock, parses DT/MMC properties, and adds the host.

## Control Flow

Probe creates an SDHCI platform host with `sdhci_dove_pdata`, obtains an enabled clock with `devm_clk_get_enabled()`, parses MMC DT properties, and calls `sdhci_add_host()`. Remove and PM are generic `sdhci_pltfm_remove` and `sdhci_pltfm_pmops`.

## State And Persistence Behavior

This driver has no custom private state. State is in the generic SDHCI host and platform clock pointer. No persistence exists.

## Dependencies And Integration Points

It integrates with DT compatible `"marvell,dove-sdhci"`, Linux clocks, `mmc_of_parse()`, `sdhci-pltfm`, and the generic SDHCI core. It relies on SDHCI platform PM and removal helpers.

## Risks And Edge Cases

- Returning zero for absent version/slot interrupt registers is a compatibility shim; generic SDHCI code must not require real values from those registers.
- Capability masking removes 3.0 V support; board voltage declarations and regulators must agree.
- Forced DMA and broken timeout/no busy IRQ quirks mean timeout and data error behavior should be tested on real hardware.

## Test Signals

Build and DT match coverage, clock enable, capability dump showing no 3.0 V, basic read/write I/O, timeout behavior, busy-command behavior, suspend/resume through platform PM, and remove cleanup.
