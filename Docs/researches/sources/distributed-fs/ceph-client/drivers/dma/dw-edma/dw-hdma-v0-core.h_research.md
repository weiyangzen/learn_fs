## sources/distributed-fs/ceph-client/drivers/dma/dw-edma/dw-hdma-v0-core.h

Purpose: Minimal declaration header for the native HDMA v0 register back end.

Important APIs/types/functions: declares `dw_hdma_v0_core_register(struct dw_edma *dw)`, which installs HDMA v0 operations into the common eDMA core.

Control flow: common probe calls this when the map format is `EDMA_MF_HDMA_NATIVE`.

State and persistence: no standalone state; registration changes `dw->core`.

Dependencies and integration: includes `linux/dma/edma.h`; consumed by `dw-edma-core.c`.

Risks and test signals: prototype drift breaks builds or probe selection. Test with native HDMA-capable configs and PCI IDs that select HDMA.
