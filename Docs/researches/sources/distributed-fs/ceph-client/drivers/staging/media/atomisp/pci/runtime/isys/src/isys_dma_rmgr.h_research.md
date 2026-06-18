# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/runtime/isys/src/isys_dma_rmgr.h

Purpose: private state definition for ISYS DMA channel allocation.

Important type: `isys_dma_rsrc_t` contains a `u32 active_table` bitmap and `u16 num_active` counter.

Control flow/state: no functions; `isys_dma_rmgr.c` owns an array indexed by DMA ID.

Dependencies/integration: channel count comes from ISYS2401 DMA constants, with channels represented as bit positions in `active_table`.

Risks: bitmap width caps channels at 32. State has no owner metadata, making leak/double release detection difficult.

Test signals: bitmap/counter invariants after allocate/release, max-channel compatibility, and reset coverage for every DMA ID.
