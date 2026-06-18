# sources/distributed-fs/ceph-client/drivers/media/pci/mantis/mantis_dma.h

- Purpose: Public declaration header for the Mantis DMA lifecycle and bottom-half transfer routine.
- Important APIs/types/functions: `mantis_dma_init`, `mantis_dma_exit`, `mantis_dma_start`, `mantis_dma_stop`, and `mantis_dma_xfer`.
- Control flow: Included by probe/DVB code: probe allocates buffers, DVB feed callbacks start/stop hardware, and workqueue setup uses `mantis_dma_xfer`.
- State and persistence: No state; it exposes functions operating on `struct mantis_pci` fields defined in `mantis_common.h`.
- Dependencies and integration points: Depends on `struct mantis_pci` and `struct work_struct` being visible through including compilation units.
- Risks: Prototype drift would break DMA/DVB integration. It intentionally exposes start/stop separately from allocation, so callers must preserve lifecycle order.
- Test signals: Compile and link coverage plus stream start/stop tests in `mantis_dvb.c`.
