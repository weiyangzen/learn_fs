## sources/distributed-fs/ceph-client/drivers/dma/dw-edma/dw-edma-core.c

Purpose: Common DMAengine core for Synopsys DesignWare eDMA/HDMA controllers. It owns channel setup, descriptor/chunk/burst allocation, DMAengine callbacks, IRQ routing, transfer progression, and exported probe/remove entry points for bus glue.

Important APIs/types/functions: exports `dw_edma_probe()` and `dw_edma_remove()`. Key functions include `dw_edma_device_transfer()`, prep callbacks for slave SG/cyclic/interleaved, `dw_edma_device_config()`, `dw_edma_device_issue_pending()`, `dw_edma_start_transfer()`, done/abort interrupt handlers, IRQ allocation helpers, `dw_edma_channel_setup()`, and emulated interrupt helpers. It dispatches register work through `struct dw_edma_core_ops`.

Control flow: bus glue fills `struct dw_edma_chip`, then `dw_edma_probe()` chooses eDMA v0 or HDMA v0 ops, clamps hardware channel counts to linked-list region counts, requests IRQs, allocates optional emulated doorbell IRQ, initializes channels, registers DMAengine callbacks, and enables debugfs. Transfer prep validates direction against local/remote topology, creates chunks and bursts from SG/cyclic/interleaved input, and queues a virt-dma descriptor. Issue starts the first chunk; each done IRQ frees the completed chunk, starts the next chunk, pauses, stops, or completes the cookie.

State and persistence: volatile state lives in `struct dw_edma`, `struct dw_edma_chan`, `struct dw_edma_desc`, `struct dw_edma_chunk`, and `struct dw_edma_burst`. Channel status/request/configured flags gate operations. Linked-list memory regions are supplied by the platform and used as hardware-visible state; no file persistence.

Dependencies and integration: depends on DMAengine, virt-dma, MSI, IRQ descriptors, `linux/dma/edma.h`, and versioned core files. Bus glue must provide IRQ vector, optional PCI address translation, register base, LL/data regions, and map format.

Risks and test signals: direction inversion for local versus remote eDMA is easy to misuse; chunk accounting drives residue and completion; non-LL HDMA only supports one burst per chunk. Test with SG, cyclic, interleaved DMA, pause/resume/terminate, abort IRQs, single and multiple MSI vectors, callback-result residue, and local/remote address translation.
