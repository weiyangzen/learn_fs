# sources/distributed-fs/ceph-client/drivers/ata/pata_serverworks.c

## Purpose
`pata_serverworks.c` drives ServerWorks/RCC OSB4, CSB5, CSB6, CSB6IDE2, and HT1000 PATA controllers. It handles chipset errata, revision-specific UDMA limits, OEM cable detection, and different BMDMA scatter-gather capabilities for OSB4 versus CSB-class controllers.

## Important APIs, Types, and Functions
Important mode and policy callbacks are `serverworks_cable_detect()`, `serverworks_osb4_filter()`, `serverworks_csb_filter()`, `serverworks_set_piomode()`, and `serverworks_set_dmamode()`. Probe/fixup helpers include `serverworks_fixup_osb4()`, `serverworks_fixup_csb()`, `serverworks_fixup_ht1000()`, `serverworks_fixup()`, `serverworks_init_one()`, and resume-only `serverworks_reinit_one()`. `csb_bad_ata100[]` lists Seagate models whose UDMA5 is disabled.

## Control Flow, State, and Persistence
Probe enables the PCI device, applies chipset fixups, selects one of four port-info profiles, and initializes BMDMA through libata. OSB4 fixup locates the companion bridge, disables a 600 ns interrupt mask, and enables UDMA/33 support or falls back to a no-UDMA profile if the bridge cannot be found. CSB fixup configures third-channel or RAID-function side registers, enables DMA in register `0x5a`, and returns a mode selector indicating whether UDMA5 is available. Timing callbacks write PIO bytes at `0x40+offset`, CSB PIO mode nibbles at `0x4a`, MWDMA bytes at `0x44+offset`, UDMA per-port nibbles at `0x56+port`, and UDMA enable bits in `0x54`.

## Dependencies and Integration Points
The driver depends on libata BMDMA and PCI helpers, PCI companion-device discovery via `pci_get_device()`, OEM subsystem IDs for Dell/Sun cable detection, and SCSI host templates that distinguish dumb OSB4 DMA from normal CSB DMA. It integrates with libata `mode_filter` to suppress unsafe OSB4 disk UDMA and model-specific CSB5 UDMA5.

## Risks and Test Signals
Risks include fragile NDA/errata-derived register programming, PCI companion bridge lookup failures, wrong cable detection on non-Dell/Sun OEM systems, model-string filtering that misses affected drives, and resume paths failing to replay fixups. Tests should cover each PCI device ID and revision class, UDMA4 versus UDMA5 selection, listed Seagate models, OSB4 fallback without bridge, CSB6 third-channel dummy-port handling, Dell/Sun subsystem cable bits, suspend/resume, and sustained DMA stress with error-handler recovery.
