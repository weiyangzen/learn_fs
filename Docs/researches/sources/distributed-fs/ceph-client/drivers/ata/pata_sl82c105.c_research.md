# sources/distributed-fs/ceph-client/drivers/ata/pata_sl82c105.c

## Purpose
`pata_sl82c105.c` drives the Winbond/SL82C105 PATA controller. It handles shared PIO/DMA timing registers by switching timings at DMA start and stop, and it resets the DMA engine around every DMA transfer per errata.

## Important APIs, Types, and Functions
Important callbacks and helpers are `sl82c105_pre_reset()`, `sl82c105_configure_piomode()`, `sl82c105_set_piomode()`, `sl82c105_configure_dmamode()`, `sl82c105_reset_engine()`, `sl82c105_bmdma_start()`, `sl82c105_bmdma_stop()`, `sl82c105_qc_defer()`, `sl82c105_sff_irq_check()`, `sl82c105_bridge_revision()`, `sl82c105_fixup()`, and `sl82c105_init_one()`. Control bits live in PCI config register `0x40`.

## Control Flow, State, and Persistence
Probe enables PCI, locates function 0 to determine the Winbond 553 bridge revision, disables DMA on missing or early bridge revisions, applies controller enable/fifo fixup bits, and registers through `ata_pci_bmdma_init_one()`. Reset suppresses absent secondary ports by checking config enable bits. PIO mode writes the shared timing word at `0x44 + 8*port + 4*dev`. DMA start delays, resets the DMA engine through register `0x7e`, writes DMA timing, then starts BMDMA. DMA stop stops BMDMA, resets the engine, delays, and restores PIO timing for the device.

## Dependencies and Integration Points
The driver uses libata BMDMA callbacks, config-space IRQ status checking, PCI slot lookup for bridge revision, 40-wire cable policy, and host-wide command serialization through `qc_defer` to avoid the reset bug across channels.

## Risks and Test Signals
Risks include DMA enablement on unsafe bridge revisions, missed timing restoration after abnormal completion, host-wide serialization assumptions, config-space IRQ status mistakes, and secondary-port enable handling. Tests should include early and later bridge revisions, DMA and PIO fallback profiles, timeout/error-handler DMA stop paths, alternating PIO/DMA commands, simultaneous channel attempts, suspend/resume fixup replay, and stress tests with ATAPI and disk DMA.
