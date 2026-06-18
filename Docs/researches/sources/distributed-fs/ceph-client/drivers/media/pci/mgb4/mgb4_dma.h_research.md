# sources/distributed-fs/ceph-client/drivers/media/pci/mgb4/mgb4_dma.h

- Purpose: Public MGB4 DMA channel lifecycle and transfer declarations.
- Important APIs/types/functions: `mgb4_dma_channel_init`, `mgb4_dma_channel_free`, and `mgb4_dma_transfer`.
- Control flow: Core initializes/frees channels; vin/vout call transfer from workqueues.
- State and persistence: No state; operates on `struct mgb4_dev` DMA channel arrays.
- Dependencies and integration points: Depends on `mgb4_core.h` and scatter-gather table types from kernel headers.
- Risks: Prototype changes affect core and both video directions.
- Test signals: Compile/link plus vin/vout streaming tests.
