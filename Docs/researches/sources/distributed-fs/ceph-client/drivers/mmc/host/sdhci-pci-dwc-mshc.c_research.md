# sources/distributed-fs/ceph-client/drivers/mmc/host/sdhci-pci-dwc-mshc.c

## Purpose
This file provides the Synopsys DWC_MSHC PCI-specific SDHCI fixup exported as `sdhci_snps`. It replaces the generic clock callback with a Synopsys MMCM-aware implementation while otherwise delegating DMA, bus-width, reset, and UHS signaling to the common SDHCI/PCI helpers.

## Important APIs, Types, And Functions
The key entry point is `sdhci_snps_set_clock()`, installed through `sdhci_snps_ops.set_clock`. The exported `const struct sdhci_pci_fixes sdhci_snps` is consumed by the generic `sdhci-pci` device table through `sdhci-pci.h`. Vendor registers are found by reading `SDHCI_VENDOR_PTR_R`, then adding that vendor pointer to `SDHC_GPIO_OUT` and `SDHC_AT_CTRL_R`. High-speed clock programming uses fixed MMCM DRP constants for 100 MHz and 200 MHz.

## Control Flow
Clock changes first disable Synopsys software-managed RX tuning by clearing `SDHC_SW_TUNE_EN`. Requests at or below 52 MHz fall through to `sdhci_set_clock()`. Faster requests assert the MMCM reset bit, write either the 100 MHz or 200 MHz divider/feedback settings, deassert reset, then directly enable programmable clock mode, internal clock, and card clock in `SDHCI_CLOCK_CONTROL`.

## State And Persistence
The file keeps no private host state. Persistent effects are hardware register state: MMCM divider/feedback programming, vendor AT control state, and the card/internal clock bits. The routine does not update a private cache beyond the common SDHCI state maintained by core helpers.

## Dependencies And Integration Points
It depends on `sdhci.h` for host register access and `sdhci-pci.h` for the `sdhci_pci_fixes` contract and `sdhci_pci_enable_dma()`. Integration happens when the PCI glue selects `sdhci_snps` for `PCI_DEVICE_ID_SYNOPSYS_DWC_MSHC`.

## Risks
The implementation assumes only 100 MHz and 200 MHz require explicit MMCM programming; any other rate above 52 MHz is coerced to the 200 MHz settings. The code writes MMCM registers without polling for lock, so clock instability would surface later as command/data failures. Register offsets are hard-coded and depend on the vendor pointer being valid.

## Test Signals
Useful signals are successful enumeration at legacy and high-speed rates, no tuning regressions after clearing software tuning, stable transfers at 100/200 MHz, and absence of command/data timeout logs after repeated clock switches.
