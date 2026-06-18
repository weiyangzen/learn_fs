# sources/distributed-fs/ceph-client/drivers/ata/pata_hpt3x3.c

`pata_hpt3x3.c` is the libata driver for HighPoint HPT343/HPT363 controllers. These older chips use a nonstandard BAR4 taskfile layout and have DMA/freeze errata. The driver always provides PIO timing setup and conditionally includes DMA support under `CONFIG_PATA_HPT3X3_DMA`.

`hpt3x3_set_piomode()` writes PCI config registers `0x44` and `0x48`, encoding a three-bit PIO timing per device and clearing DMA bits. With DMA enabled, `hpt3x3_set_dmamode()` writes the mode value and marks MWDMA or UDMA in `0x48`. `hpt3x3_freeze()` stops DMA before SFF freeze to avoid hangs, `hpt3x3_bmdma_setup()` clears BMDMA interrupt/error bits before generic setup, and `hpt3x3_atapi_dma()` rejects ATAPI DMA.

`hpt3x3_init_one()` initializes chipset registers, allocates a two-port host, enables PCI, maps BAR4, sets DMA mask, manually assigns taskfile/control/BMDMA addresses from BAR4 offsets, enables bus mastering, and activates with `ata_bmdma_interrupt()`. Resume reruns chipset initialization after generic PCI resume.

There is no heap private state; hardware state is PCI config and BAR4 registers. Dependencies are PCI managed mapping, DMA mask setup, libata BMDMA/SFF, and optional PM. Risks include wrong BAR4 offsets, compile-time DMA behavior divergence, and DMA hangs if freeze/setup ordering changes. Tests should cover both HPT343/HPT363 latency paths, PIO master/slave timing, optional DMA, ATAPI PIO fallback, resume, and forced freeze while DMA is active.
