## sources/distributed-fs/ceph-client/drivers/dma/amd/ptdma/ptdma-dev.c

### Purpose
`ptdma-dev.c` initializes and drives the original AMD PassThru DMA hardware queue. It programs queue registers, submits 32-byte passthrough descriptors, handles queue interrupts and errors, registers dmaengine support, and tears hardware down.

### Important APIs, Types, And Functions
Important functions are `pt_start_queue()`, `pt_stop_queue()`, `pt_core_execute_cmd()`, exported `pt_core_perform_passthru()`, `pt_check_status_trans()`, `pt_core_irq_handler()`, `pt_core_init()`, and `pt_core_destroy()`. State is held in `struct pt_device`, `struct pt_cmd_queue`, `struct pt_cmd`, `struct pt_passthru_engine`, and hardware descriptor `struct ptdma_desc`.

### Control Flow, State, And Persistence
Core init creates a DMA pool, writes global PTDMA configuration registers, allocates a coherent ring, disables queue interrupts, sets queue base/tail/head and size bits, requests an IRQ, enables interrupts, registers the dmaengine device, and installs debugfs. A passthrough request fills source/destination/length descriptor fields, toggles interrupt enable based on the queued dmaengine descriptor flags, copies the descriptor to the ring under `q_lock`, advances the ring index, performs a memory barrier, writes the tail register, and starts the queue. IRQ handling disables interrupts, reads/acknowledges status, records first command error, may advance the head pointer on error, invokes the current command callback, and reenables interrupts.

### Dependencies, Integration Points, Risks, And Test Signals
Dependencies include coherent DMA allocation, DMA pools, PCI-provided MMIO/IRQ, bitfield helpers, shared dmaengine registration, and debugfs setup. Risks include only one global `tdata.cmd` for in-flight callback state, ring-full handling mostly delegated to higher layers, error-code array indexing without bounds checks, interrupt disable/reenable races, and destroy flushing `pt->cmd` even though normal PT submission primarily uses virt-dma descriptors. Test signals include PTDMA device probe, memcpy submission/completion with and without interrupt flag, hardware error injection/status handling, IRQ storm avoidance, dmaengine unregister on remove, and cleanup after `pt_core_init()` failures.
