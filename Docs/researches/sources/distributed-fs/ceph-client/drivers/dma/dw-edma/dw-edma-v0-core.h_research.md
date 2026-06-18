## sources/distributed-fs/ceph-client/drivers/dma/dw-edma/dw-edma-v0-core.h

Purpose: Minimal declaration header for the eDMA v0 register back end.

Important APIs/types/functions: declares `dw_edma_v0_core_register(struct dw_edma *dw)`, which installs the eDMA v0 `dw_edma_core_ops` table into the common core object.

Control flow: common probe calls this function unless the chip map format selects native HDMA.

State and persistence: no standalone state; registration mutates `dw->core`.

Dependencies and integration: includes `linux/dma/edma.h` for the forward-visible eDMA types. Used by `dw-edma-core.c`.

Risks and test signals: low-risk header, but prototype drift breaks linkage. Test with normal `CONFIG_DW_EDMA` builds and probe paths selecting eDMA v0.
