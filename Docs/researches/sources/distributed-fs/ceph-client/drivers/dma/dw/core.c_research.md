## sources/distributed-fs/ceph-client/drivers/dma/dw/core.c

Purpose: Shared DMAengine core for classic Synopsys DesignWare AHB DMA variants. It manages descriptors, queues, interrupt/tasklet completion, transfer preparation, pause/resume/terminate, resource allocation, hardware parameter probing, and DMAengine registration.

Important APIs/types/functions: `do_dma_probe()`, `do_dma_remove()`, `do_dw_dma_on/off()`, `do_dw_dma_enable/disable()`, `dw_dma_filter()`, prep callbacks `dwc_prep_dma_memcpy()` and `dwc_prep_slave_sg()`, status/config callbacks, interrupt handler `dw_dma_interrupt()`, tasklet `dw_dma_tasklet()`, and descriptor helpers `dwc_desc_get()`, `dwc_dostart()`, `dwc_scan_descriptors()`, `dwc_descriptor_complete()`.

Control flow: variant probe installs operation callbacks and calls `do_dma_probe()`. The core obtains platform data or auto-configures from hardware registers, allocates channels, creates a DMA pool for hardware descriptors, requests IRQ, registers DMAengine capabilities, and exposes DMA callbacks. Transfer prep builds linked descriptor chains; submit queues them; issue-pending starts the first queued chain using hardware LLP or software LLP emulation. IRQ disables masks and schedules a tasklet; tasklet scans transfer/error bits, completes descriptors, advances queued work, or handles bad descriptors.

State and persistence: `struct dw_dma` owns device state, channel array, descriptor pool, tasklet, all-channel mask, and in-use mask. Each channel owns active/queued descriptor lists, lock, direction, slave config, flags for paused/soft-LLP/cyclic, residue, and hardware capability data. All state is volatile and register/DMA-pool backed.

Dependencies and integration: used by `dw.c` and `idma32.c` variants plus platform/PCI glue. Depends on DMAengine, DMA pools, IRQ/tasklet, runtime PM, and register definitions from `regs.h`.

Risks and test signals: descriptor list manipulation, soft LLP fallback, residue accounting, pause drain behavior, bad descriptor recovery, and auto-configuration parsing are high-risk. Test with dmatest memcpy and slave SG, channels with and without LLP, pause/resume/terminate, shared IRQ behavior, runtime PM probe/remove, and invalid DMA address error paths.
