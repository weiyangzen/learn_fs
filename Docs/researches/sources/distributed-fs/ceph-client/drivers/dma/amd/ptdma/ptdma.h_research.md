## sources/distributed-fs/ceph-client/drivers/dma/amd/ptdma/ptdma.h

### Purpose
`ptdma.h` defines AMD PassThru DMA register constants, descriptor formats, device/queue/channel state, and cross-file function prototypes. It is also consumed by AE4DMA because AE4 reuses the PTDMA dmaengine abstraction.

### Important APIs, Types, And Functions
Important constants include command queue register offsets, queue sizing macros, interrupt bits, PT engine identifiers, descriptor sizes, and block sizes. Key types are `struct pt_tasklet_data`, `struct pt_passthru_engine`, `struct pt_cmd`, `struct pt_dma_desc`, `struct pt_dma_chan`, `struct pt_cmd_queue`, `struct pt_device`, `struct ptdma_desc`, and `struct pt_dev_vdata`. Prototypes cover dmaengine registration, debugfs setup, core init/destroy, passthrough execution, status checking, queue start/stop, and inline interrupt enable/disable helpers.

### Control Flow, State, And Persistence
The header captures persistent driver state: the PT device owns PCI/device info, MMIO base, one hardware command queue, dmaengine channels, descriptor cache, counters, and callback tasklet data. Queue state tracks coherent ring memory, register base, cached control word, interrupt enable state, status/error snapshots, and total passthrough operations. Descriptor bitfields encode the 8-word hardware command format for passthrough copies.

### Dependencies, Integration Points, Risks, And Test Signals
Dependencies include dmaengine, PCI, dmapool, lists, waitqueues, spinlocks, mutexes, and `virt-dma`. Risks include register offset drift with hardware revisions, bitfield layout portability, macro precedence in pointer mask sizing, shared inline interrupt helpers being PTDMA-specific even though AE4 embeds PT structures, and ABI-like coupling between PTDMA and AE4DMA. Test signals include compile of PTDMA and AE4DMA users, descriptor size/layout checks, queue register programming validation, interrupt enable/disable register writes, and debugfs field access.
