# sources/distributed-fs/ceph-client/drivers/ata/pata_triflex.c

## Purpose
`pata_triflex.c` supports the Compaq TriFlex IDE controller used in older Compaq workstations. It programs per-device timing words and reloads timing on DMA start/stop because PIO and DMA timing requirements do not share a stable register setup.

## Important APIs, Types, and Functions
Important functions are `triflex_prereset()`, `triflex_load_timing()`, `triflex_set_piomode()`, `triflex_bmdma_start()`, `triflex_bmdma_stop()`, `triflex_init_one()`, and the suspend-specific `triflex_ata_pci_device_suspend()`. The port ops inherit `ata_bmdma_port_ops`, override BMDMA start/stop and prereset, and force 40-wire cable detection.

## Control Flow, State, and Persistence
Probe registers a single PIO4/MWDMA2/slave-capable profile through `ata_pci_bmdma_init_one()`. Prereset checks per-channel enable bits in PCI config register `0x80`. `triflex_load_timing()` maps PIO, SWDMA, and MWDMA modes to 16-bit timing values and writes the master or slave half of config dword `0x70` or `0x74`. PIO setup loads initial PIO timing; DMA start switches to DMA timing before `ata_bmdma_start()`; DMA stop stops BMDMA and restores PIO timing.

## Dependencies and Integration Points
The file integrates with libata BMDMA/SFF reset helpers, PCI config timing registers, and generic PCI remove/resume. Its suspend path deliberately saves PCI state without powering down or disabling the device because legacy APM BIOS code may require IDE access.

## Risks and Test Signals
Risks include unsupported or unexpected transfer mode reaching `BUG()`, timing not restored after DMA error recovery, legacy suspend behavior conflicting with modern PM expectations, and hardcoded 40-wire policy limiting performance. Tests should cover enable-bit absent ports, all PIO and MWDMA modes, DMA timeout/error paths, master/slave timing independence, suspend/resume on affected platforms, and dmesg checks for libata fallback when DMA is unavailable.
