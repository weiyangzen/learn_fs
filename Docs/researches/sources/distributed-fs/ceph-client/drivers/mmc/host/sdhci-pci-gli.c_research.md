# sources/distributed-fs/ceph-client/drivers/mmc/host/sdhci-pci-gli.c

## Purpose
This file contains Genesys Logic PCI SDHCI fixups for GL9750, GL9755, GL9763E, and GL9767 controllers. It layers vendor register programming, custom clocks, tuning, MSI setup, UHS-II/SD Express handling, CQHCI support for GL9763E eMMC, and power-management quirks onto the generic `sdhci-pci` framework.

## Important APIs, Types, And Functions
The exported fixup objects are `sdhci_gl9750`, `sdhci_gl9755`, `sdhci_gl9763e`, and `sdhci_gl9767`. Each supplies a `struct sdhci_ops` table and probe callbacks such as `gli_probe_slot_gl9750()`, `gli_probe_slot_gl9755()`, `gli_probe_slot_gl9763e()`, and `gli_probe_slot_gl9767()`. GL9750/9755 clock paths use `gl975*_set_ssc_pll_*()` and custom `set_clock` functions to program spread-spectrum PLL settings. GL9750 also has `gl9750_execute_tuning()` with a two-pass RX-invert tuning fallback. GL9767 adds UHS-II and SD Express support through `sdhci_pci_uhs2_add_host()`, `sdhci_gl9767_set_power()`, `sdhci_gl9767_reset()`, `gl9767_init_sd_express()`, and vendor PHY programming. GL9763E integrates command queueing through `gl9763e_add_host()`, `sdhci_gl9763e_cqhci_irq()`, and `sdhci_gl9763e_cqhci_ops`.

## Control Flow
Slot probe performs one-time vendor setup, enables MSI if possible, adjusts advertised MMC capabilities, and enables SDHCI v4 mode. GL9750/9755 probes disable SDIO, set ASPM/L1 delay values, mask PCIe AER replay timer timeout, and program vendor tuning/PLL defaults. GL9767 additionally marks SD Express support, installs `init_sd_express`, configures debounce and UHS-II PHY registers, and uses UHS-II-aware add/remove host callbacks. GL9763E configures eMMC-only capabilities, enables HS200/HS400/HS400ES and optional CQE/DCMD based on mailbox bits, then uses a custom add-host path: setup SDHCI, allocate/init CQHCI, add the host, and disable low-power negotiation.

During runtime operations, clock callbacks disable PLL/SSC, calculate SDHCI divisors, program vendor PLLs for selected high rates, then re-enable the SDHCI clock. Reset callbacks ensure an internal clock exists, handle UHS-II SD-trans reset when needed, and reapply vendor defaults. Voltage-switch callbacks add controller-specific delays. Power callbacks mask overcurrent interrupts around power toggles and manage VDD2/UHS-II bits.

## State And Persistence
Most state is held in hardware registers and PCI config space. The driver mutates `host->pwr`, `host->clock`, `host->mmc->caps/caps2`, `host->mmc_host_ops`, `host->irq`, and CQHCI private state. GL9763E PM paths persist low-power negotiation policy across runtime/system suspend and resume. PLL, SSC, ASPM delay, debounce, UHS-II PHY, and SD Express mode bits persist until reset or reprogramming, so resume callbacks replay MSI and host state.

## Dependencies And Integration Points
The file depends on PCI config access, Open Firmware properties for Apple ARM64 CD/WP inversion, SDHCI core helpers, `sdhci-pci` fixup plumbing, UHS-II helpers from `sdhci-uhs2.h`, CQHCI support, and MMC timing/capability definitions. It integrates through PCI IDs declared in `sdhci-pci.h` and selected by the generic PCI driver.

## Risks
The code has many timing-sensitive register sequences with fixed millisecond and microsecond waits. PLL programming, VHS read/write windows, UHS-II reset ordering, and overcurrent masking can regress card detection or power cycling if reordered. GL9750 tuning deliberately returns success while storing errors in `host->tuning_err`, so callers must respect SDHCI tuning semantics. GL9763E CQHCI setup crosses SDHCI and CQHCI ownership, making suspend/resume and IRQ routing high-risk. Apple-specific OF inversion settings affect removable media detection and write protect.

## Test Signals
Test with each supported PCI ID. Signals include successful MSI allocation or clean INTx fallback, stable enumeration after suspend/resume, GL9763E CQE traffic and DCMD operation, GL9767 UHS-II and SD Express mode transitions, SDR104 tuning success/fallback, no replay timer AER noise, correct CD/WP polarity on OF systems, and no overcurrent interrupt storm during power changes.
