<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r535/gr.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r535/gr.c

## Purpose
Implements R535 graphics context buffer discovery, golden context initialization, per-channel context promotion, and GR teardown.

## Important APIs, Types, And Functions
Defines `r535_gr_promote_ctx`, `r535_gr_chan_new`, `r535_gr_units`, `r535_gr_get_ctxbuf_info`, `r535_gr_get_ctxbufs_and_zcull_info`, `r535_gr_oneinit`, `r535_gr_dtor`, and exports `r535_gr`.

## Control Flow
Oneinit allocates a golden instance object and VMM, creates an RM VA space and privileged channel, queries RM for context buffer sizes, allocates/promotes golden context buffers, allocates a 3D object to trigger RM golden-context initialization, then frees temporary objects while retaining global context buffers. Per-channel creation references the channel VMM and calls `r535_gr_promote_ctx` to allocate or reuse context buffers, map them into the VMM, and send `GPU_PROMOTE_CTX` entries to RM. Destructor frees per-channel mappings and global context memory.

## State And Persistence
`r535_gr` stores context buffer descriptors and global context buffer memory. Each `r535_gr_chan` stores VMM refs, memory refs, and VMA mappings until channel object destruction. `r535_gr_units` reports GPC/TPC state from GSP.

## Dependencies And Integration Points
Depends on RM internal static GR context queries, RM FIFO channel allocation, RM VMM VA-space creation, NVKM memory/VMM APIs, and graphics class allocation.

## Risks And Edge Cases
Context buffer arrays are bounded by `R515_GR_MAX_CTXBUFS`. Memory/VMM mapping failures during promotion can leave partially allocated resources handled by object teardown. RM context metadata must match expected buffer ID mapping.

## Test Signals
Successful golden context initialization, graphics channel creation, no context buffer warnings, correct GPC/TPC unit reporting, and clean context memory unrefs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r535/gr.c -->
