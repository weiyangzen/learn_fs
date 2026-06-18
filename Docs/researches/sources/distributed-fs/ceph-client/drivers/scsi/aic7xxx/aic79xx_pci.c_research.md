# sources/distributed-fs/ceph-client/drivers/scsi/aic7xxx/aic79xx_pci.c

## Purpose

`aic79xx_pci.c` contains product-specific probe, setup, and PCI error handling for AIC7901/AIC7902 Ultra320 controllers. It maps PCI IDs to controller descriptions/setup functions, configures chip features and revision workarounds, validates register access, reads SEEPROM/VPD or fallback scratch settings, configures termination, and handles PCI/PCI-X error interrupts.

## Important APIs, Types, and Functions

- `ahd_pci_ident_table[]` maps full PCI/subsystem IDs to names and setup functions.
- `ahd_compose_id()` builds the 64-bit identity from device/vendor/subdevice/subvendor.
- `ahd_find_pci_device()` reads PCI config identity, masks HostRAID/IROC bits, and returns a matching identity table entry.
- `ahd_pci_config()` is the main attach sequence after Linux PCI enablement: setup entry, bus mode detection, power D0, register mapping, DAC enable, bus mastering, softc init, reset, SEEPROM/termination check, core init, and IRQ mapping.
- `ahd_pci_suspend()` and `ahd_pci_resume()` save/restore PCI config fields used after resets and power transitions.
- `ahd_pci_test_register_access()` verifies the selected register mapping by pausing, clearing PCI errors, writing/reading SRAM, and checking PCI error status.
- `ahd_check_extport()` reads VPD and SEEPROM, verifies checksum, falls back to BIOS scratch SCB settings, or applies defaults.
- `ahd_configure_termination()` programs termination and STPWLEVEL from adapter control bits and flexport state.
- `ahd_pci_intr()` and `ahd_pci_split_intr()` dump/clear PCI and PCI-X split completion errors.
- `ahd_aic7901_setup()`, `ahd_aic7901A_setup()`, `ahd_aic7902_setup()`, and `ahd_aic790X_setup()` set chip/features/bugs and revision-specific I/O cell defaults.

## Control Flow and State

Attach starts with `ahd_find_pci_device()` and then `ahd_pci_config()`. The selected identity names the adapter and supplies the setup function. Setup sets `ahd->chip`, feature bits, channel letter from PCI function, and revision-dependent bug/workaround flags. `ahd_pci_config()` then classifies PCI versus PCI-X bus mode from `DEVCONFIG`, powers the device to D0, maps registers through the Linux OSM, enables dual-address cycles for high DMA addressing, enables bus mastering, initializes the softc, resets the chip, caches PCI cacheline size, switches to SCSI mode, reads NVRAM/configuration, initializes the core, increments `init_level`, and maps the interrupt.

SEEPROM flow first tries external port acquisition. If present, it reads VPD for the current function, parses it, reads the function-specific `struct seeprom_config`, verifies checksum, and releases the SEEPROM. If unavailable, it looks for BIOS signatures in SCB scratch RAM and reconstructs config words. If neither path succeeds, it sets `AHD_USEDEFAULTS`, runs default config, frees `seep_config`, and configures auto-termination defaults.

PCI error flow enters through the core bus interrupt hook. Split interrupts read and clear per-mode DCH/SG split status registers plus PCI-X status. PCI errors read and clear per-source PCI status registers, dump card state, clear conventional PCI status, restore modes, clear `PCIINT`, and unpause.

## State and Persistence Behavior

The file sets long-lived hardware state in `ahd->chip`, `ahd->features`, `ahd->bugs`, `ahd->flags`, `ahd->bus_description`, `ahd->pci_cachesize`, `ahd->channel`, termination flags, and `ahd->seep_config`. SEEPROM reads are persistent hardware configuration; writes are handled in `aic79xx_proc.c`. Suspend state is saved in `ahd->suspend_state.pci_state`.

## Dependencies and Integration Points

It depends on platform register and PCI config wrappers from `aic79xx_osm.c`, ID macros from `aic79xx_pci.h`, core initialization/reset/config parsing functions, flexport/SEEPROM helpers, and register definitions. It is called by `aic79xx_osm_pci.c` during probe and by the core interrupt path for PCI-specific errors.

## Risks

- Identity matching masks HostRAID/IROC bits; incorrect masks could bind unsupported RAID-mode devices or miss supported OEM devices.
- Revision workaround flags are dense and hardware-specific; removing or misapplying one can cause data corruption, failed aborts, or broken packetized transfers.
- `ahd_pci_test_register_access()` deliberately writes SRAM and manipulates error status; changes here need real hardware validation.
- SEEPROM fallback to scratch RAM trusts legacy BIOS signatures and word layout; endian or offset mistakes would apply wrong target/termination policy.
- Termination programming affects physical bus stability; bad flexport detection can cause device discovery or data integrity failures.

## Test Signals

- Probe known AIC7901/AIC7902 revisions and confirm the correct features, bug flags, bus mode description, DMA addressing, and channel letter.
- Validate SEEPROM present, checksum-failure, and no-SEEPROM fallback cases.
- Exercise MMIO register access test and PIO fallback.
- Inject or observe PCI/PCI-X errors and confirm interrupts are logged, latched status bits are cleared, and normal interrupts resume.
