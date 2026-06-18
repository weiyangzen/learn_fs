# sources/distributed-fs/ceph-client/arch/sh/drivers/dma/dma-api.c



Source read size: 274 lines, 6103 bytes.



Purpose: legacy SuperH DMA management API that registers DMAC providers, exposes virtual channels, handles request/free/configure/transfer/wait, and publishes `/proc/dma`.

Important APIs/types/functions: `register_dmac()`, `unregister_dmac()`, `request_dma()`, `free_dma()`, `dma_xfer()`, `dma_wait_for_completion()`, `get_dma_info()`, `get_dma_channel()`, `get_dma_residue()`, `dma_configure_channel()`, `registered_dmac_list`, and `dma_spin_lock`.

Control flow: DMAC drivers register `struct dma_info`; registration allocates or accepts channel tables, assigns virtual channel numbers, initializes waitqueues/sysfs entries, and adds the controller to a global list. Clients request a channel atomically, configure optional CHCR flags, start a transfer through provider ops, then wait by TEI waitqueue or polling residue.

State and persistence: in-memory global list of controllers, per-channel busy flags, device IDs, waitqueues, mode/address/count fields, proc and sysfs exposure. No disk persistence.

Dependencies and integration points: integrates SH on-chip, Dreamcast G2/PVR2, and DMABRG-era DMA users with platform devices, procfs, sysfs, waitqueues, and provider-specific MMIO drivers.

Risks and test signals: callers assume valid channels before dereferencing; global list traversal is not visibly locked; sysfs `dev_id` store uses `strcpy`; legacy API conflicts with DMAengine if both are enabled. Test request/free races, invalid channels, TEI wakeups, proc/sysfs output, and module unload of registered DMACs.
