<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/gr.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/gr.h

## Purpose
Declares R535 graphics-engine private state used by generic RM GR and R535 GR implementation files.

## Important APIs, Types, And Functions
Defines `R515_GR_MAX_CTXBUFS`, `struct r535_gr_chan`, `struct r535_gr`, and `r535_gr_get_ctxbuf_info`.

## Control Flow
No runtime flow. Structures describe per-channel context buffers, global context buffers, and scrubber objects.

## State And Persistence
`r535_gr` stores context buffer descriptors, shared global context memory, and scrubber channel/object state. `r535_gr_chan` stores VMM references and per-channel context memory/VMA arrays.

## Dependencies And Integration Points
Included by generic RM GR and R535 GR files; depends on NVKM memory, VMM, object, and GR types.

## Risks And Edge Cases
`R515_GR_MAX_CTXBUFS` bounds all context buffer arrays; overflow is guarded by implementation `WARN_ON`s. Lifetime of VMM mappings must match channel destruction.

## Test Signals
No context buffer overflow warnings, clean VMM/memory unrefs, and successful graphics context creation/destruction.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/gr.h -->
