# sources/distributed-fs/ceph-client/drivers/scsi/aic7xxx/aic7xxx_pci.c

Purpose: product-specific PCI identification and hardware initialization for AIC7xxx-family controllers. It maps device/subsystem IDs to setup routines, configures chip features/bugs, initializes PCI/chip registers, reads SEEPROM or BIOS scratch settings, controls termination, probes external SCB RAM, handles PCI errors, and restores PCI-side state after reset/resume.

Important APIs and functions: public entry points include `ahc_find_pci_device()`, `ahc_pci_config()`, `ahc_pci_test_register_access()`, `ahc_acquire_seeprom()`, `ahc_release_seeprom()`, and `ahc_pci_resume()`. Internal functions include `check_extport()`, `ahc_parse_pci_eeprom()`, `configure_termination()`, cable-detect helpers, board-control read/write helpers, `ahc_pci_intr()`, `ahc_pci_chip_init()`, SCB RAM probe/config helpers, and many `ahc_*_setup()` routines.

Control flow: bus glue locates an identity via `ahc_find_pci_device()`, which composes a 64-bit ID and matches masks while rejecting unsupported or unconnected functions. `ahc_pci_config()` runs the selected setup, powers D0, maps registers, disables interrupts, enables bus mastering and optional DAC, initializes the softc, records BIOS/default state, resets the chip, configures DT/CRC and DMA/cache settings, checks SEEPROM/external port data, applies defaults if needed, probes external SCB RAM, snapshots PCI/chip registers, calls `ahc_init()`, and maps interrupts.

State and persistence: runtime state includes `ahc->chip`, `features`, `bugs`, `flags`, channel, instruction RAM size, SCSI IDs, termination flags, SEEPROM copy, PCI cache size, parity counters, and `bus_softc.pci_softc` snapshots. It reads SEEPROM and may later support writes through proc code; this file itself primarily reads and configures hardware registers.

Dependencies and integration: depends on local register definitions, inline accessors, 93cx6 SEEPROM helpers, PCI config wrappers from OS glue, and core initialization/reset functions. It feeds the SCSI-facing layer with hardware capabilities and saved state.

Risks: broad hardware matrix with many revision-specific bug flags; ID mask mistakes can bind unsupported RAID/SISL devices; termination and cable detection directly affect bus electrical stability; SEEPROM checksum/default fallback can alter negotiation and reset behavior; external SCB RAM probing intentionally toggles parity/error registers; PCI parity storm handling disables checking after a threshold.

Test signals: adapter/revision matrix probing, unknown generic ID handling, SEEPROM checksum success/failure, BIOS scratch fallback, Ultra/Ultra2/Ultra160 negotiation defaults, cable/termination combinations, external SRAM presence/absence, register-access validation, PCI parity interrupt path, reset/resume restoration, and unsupported RAID ID rejection.
