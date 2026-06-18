## sources/distributed-fs/ceph-client/drivers/dma/amd/ae4dma/ae4dma-dev.c

### Purpose
`ae4dma-dev.c` initializes and services AMD AE4DMA hardware queues, then registers them through the shared PTDMA dmaengine layer. It handles per-queue coherent descriptor rings, IRQs, completion workqueues, and debugfs setup.

### Important APIs, Types, And Functions
The module parameter `max_hw_q` controls how many hardware queues to initialize. Key functions are `ae4_pending_work()`, `ae4_core_irq_handler()`, `ae4_destroy_work()`, and `ae4_core_init()`. It uses `struct ae4_device`, `struct ae4_cmd_queue`, `struct pt_cmd_queue`, AE4 register offsets, and shared functions `ae4_check_status_error()`, `pt_dmaengine_register()`, and `ptdma_debugfs_setup()`.

### Control Flow, State, And Persistence
Initialization writes the requested queue count to the device, loops over queues allocating IRQs and coherent rings, programs max index and base address registers, initializes command lists/waitqueues/completions, starts an ordered workqueue per hardware queue, and registers dmaengine channels. IRQs increment per-queue interrupt counters, clear status bits, and wake the pending worker. The worker waits until interrupt count exceeds done count, then under `cmd_lock` drains completed descriptors from the software command list based on hardware read index, checks descriptor errors, invokes callbacks, decrements queue count, advances read index, and completes waiters.

### Dependencies, Integration Points, Risks, And Test Signals
Dependencies include PCI-provided IRQ numbers and BAR mapping, AE4 descriptor layout, coherent DMA allocation, ordered workqueues, waitqueues, shared PTDMA dmaengine code, and debugfs. Risks include unbounded `max_hw_q` relative to `MAX_AE4_HW_QUEUES`, delayed work that loops forever and relies on cancellation, interrupt/counter races, completion wakeups under queue-full conditions, queue count/list mismatch, and lack of explicit dmaengine unregister in AE4 remove path. Test signals include probing with one and many queues, MSI-X vector mapping, descriptor completion and error logging, queue-full timeout path, workqueue cancellation during remove, and dmaengine channel count matching initialized queues.
