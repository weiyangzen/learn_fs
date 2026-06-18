# sources/distributed-fs/ceph-client/drivers/scsi/scsi_lib_dma.c

Purpose: contains the DMA-dependent SCSI library helpers that map and unmap a command's data scatterlist for low-level drivers.

Important APIs/types/functions: `scsi_dma_map(struct scsi_cmnd *cmd)` checks `scsi_sg_count(cmd)`, maps `scsi_sglist(cmd)` against `cmd->device->host->dma_dev` with `cmd->sc_data_direction`, returns the mapped segment count, returns zero for no SG list, and returns `-ENOMEM` if `dma_map_sg()` returns zero. `scsi_dma_unmap(struct scsi_cmnd *cmd)` performs the matching `dma_unmap_sg()` when an SG list exists. Both are exported.

Control flow: drivers call `scsi_dma_map()` after the midlayer has built the command SG table and before programming hardware descriptors. On completion or error unwind they call `scsi_dma_unmap()` with the same command.

State and persistence: no local state is stored. The DMA API records mapping state in architecture/IOMMU internals, and the command's SG entries may be updated with DMA addresses by the mapping call.

Dependencies and integration: depends on `scsi_alloc_sgtables()` in `scsi_lib.c` having populated the SG list, on the host's `dma_dev`, and on the Linux DMA mapping API. Low-level SCSI drivers consume these helpers in their queue paths.

Risks: map/unmap balance is critical; leaking mappings or unmapping unmapped SG lists can corrupt IOMMU state. Direction must match the command. Returning zero for no data and negative for mapping failure means callers must distinguish no-transfer commands from failure.

Test signals: run read/write I/O with zero, one, and many SG segments under IOMMU debugging; inject `dma_map_sg()` failure; verify low-level driver unwind paths unmap exactly once; exercise DMA directions for read, write, and no-data commands.
