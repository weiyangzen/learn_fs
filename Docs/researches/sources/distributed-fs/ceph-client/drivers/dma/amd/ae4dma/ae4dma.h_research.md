## sources/distributed-fs/ceph-client/drivers/dma/amd/ae4dma/ae4dma.h

### Purpose
`ae4dma.h` defines AE4DMA register offsets, descriptor formats, queue state, device state, and core function prototypes. It is the contract between AE4 PCI/core code and the shared PTDMA dmaengine implementation.

### Important APIs, Types, And Functions
Important constants include `MAX_AE4_HW_QUEUES`, AE4 queue register offsets, `AE4_DMA_VERSION`, `CMD_AE4_DESC_DW0_VAL`, and `AE4_TIME_OUT`. Types include `struct ae4_msix`, `struct ae4_cmd_queue`, `union dwou`, `struct dword1`, `struct ae4dma_desc`, and `struct ae4_device`. Declared functions are `ae4_core_init()`, `ae4_destroy_work()`, and `ae4_check_status_error()`.

### Control Flow, State, And Persistence
The header embeds a `struct pt_device` inside `struct ae4_device`, making AE4 appear as a PTDMA-compatible device with version `AE4_DMA_VERSION`. Each AE4 queue embeds a `struct pt_cmd_queue`, a command list, workqueue, completion, counters, and hardware index tracking used by both AE4 core and `ptdma-dmaengine.c`.

### Dependencies, Integration Points, Risks, And Test Signals
Dependencies include `ptdma.h`, `virt-dma.h`, PCI/device/dmaengine headers, workqueues, waitqueues, and completions. Risks include descriptor field ordering/endian assumptions, high/low address naming inconsistencies relative to PTDMA descriptors, queue array bounds, and cross-directory header coupling. Test signals include compile coverage with PTDMA enabled, descriptor size/register programming validation, multi-queue channel registration, and AE4 error status decoding.
