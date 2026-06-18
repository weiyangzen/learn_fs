## sources/distributed-fs/ceph-client/drivers/dma/amd/ptdma/ptdma-dmaengine.c

### Purpose
`ptdma-dmaengine.c` adapts PTDMA and AE4DMA hardware queues to the Linux dmaengine API. It provides virtual-channel backed memcpy and interrupt descriptors, status/pause/resume/terminate callbacks, descriptor allocation/freeing, and AE4-specific multi-queue command flow.

### Important APIs, Types, And Functions
Exported functions are `ae4_check_status_error()`, `pt_dmaengine_register()`, and `pt_dmaengine_unregister()`. Key internals include `pt_create_desc()`, `pt_prep_dma_memcpy()`, `pt_prep_dma_interrupt()`, `pt_issue_pending()`, `pt_dma_start_desc()`, `pt_handle_active_desc()`, `pt_cmd_callback()`, `pt_cmd_callback_work()`, `pt_tx_status()`, `pt_pause()`, `pt_resume()`, and `pt_terminate_all()`. AE4 helpers include `ae4_core_execute_cmd()`, `pt_core_perform_passthru_ae4()`, and `ae4_core_queue_full()`.

### Control Flow, State, And Persistence
Registration allocates one channel for PTDMA or one channel per AE4 queue, creates a descriptor cache, advertises `DMA_MEMCPY`, `DMA_INTERRUPT`, and `DMA_PRIVATE`, initializes `virt-dma` channels, and registers the dmaengine device. Prep allocates a `pt_dma_desc`, fills passthrough source/destination/length, installs callbacks, and for AE4 adds the command to the per-queue software list. `issue_pending` moves virt-dma descriptors to the issued list and starts processing if the engine is idle. PTDMA completion marks descriptors complete synchronously in the callback path; AE4 completion is driven by AE4 workqueue callbacks that use `pt_cmd_callback_work()`. Status checks poll hardware status/error fields before reporting cookie state.

### Dependencies, Integration Points, Risks, And Test Signals
Dependencies include `virt-dma`, dmaengine cookies, PTDMA core queue operations, AE4 queue structures, kmem_cache descriptors, and DMA descriptor unmapping. Risks include divergent PTDMA versus AE4 completion paths, AE4 queue-full wait timing, descriptor status races under `vc.lock`, missing residue accounting beyond descriptor granularity, terminate freeing descriptors while AE4 command lists may still contain command entries, and AE4 high/low address field ordering. Test signals include dmaengine memcpy through PTDMA and AE4, multiple AE4 channels submitting concurrently, queue-full timeout behavior, pause/resume/terminate with active and queued descriptors, cookie status before/after completion, interrupt-only descriptor prep, and error propagation from hardware status.
