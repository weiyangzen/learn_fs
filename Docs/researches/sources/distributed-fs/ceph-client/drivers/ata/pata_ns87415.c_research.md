# sources/distributed-fs/ceph-client/drivers/ata/pata_ns87415.c

`pata_ns87415.c` supports National Semiconductor NS87415 controllers and, with `CONFIG_SUPERIO`, the PARISC SuperIO 87560 cell. It is a BMDMA-capable PATA driver with errata requiring timing reloads on PIO/DMA transitions and nonstandard DMA command/status handling.

`ns87415_set_mode()` computes PCI-clock PIO timing, writes per-device timing words at `0x44 + 2 * unit`, waits for write buffers to clear via status `0x43`, and updates config byte `0x42` for IORDY/DMA behavior. DMA callbacks switch timings around transfers: `ns87415_bmdma_start()` applies DMA mode before generic start, and `ns87415_bmdma_stop()` restores PIO after generic stop. `ns87415_bmdma_setup()` manually writes the PRD address and writes interrupt/error bits to the DMA command register due to an erratum. `ns87415_irq_clear()` uses the same command-register clear path, and `ns87415_check_atapi_dma()` disables ATAPI DMA.

`ns87415_fixup()` sets 512-byte sectors and PIO0 8-bit clocking during probe and resume. SuperIO-specific ops retry buggy zero reads for status/taskfile/BMDMA status. Probe enables PCI, applies fixups, selects normal or SuperIO ops, and delegates to `ata_pci_bmdma_init_one()`.

State is in PCI config and BMDMA registers. Dependencies are PCI, libata BMDMA/SFF, ATA timing helpers, and optional PARISC SuperIO support. Risks include erratum handling, timing flips on every DMA transfer, ATAPI DMA rejection, and SuperIO retry behavior. Tests should cover PIO/MWDMA timing, DMA setup bits, interrupt clear, write-buffer wait loop, ATAPI fallback, resume fixups, and SuperIO zero-read workarounds.
