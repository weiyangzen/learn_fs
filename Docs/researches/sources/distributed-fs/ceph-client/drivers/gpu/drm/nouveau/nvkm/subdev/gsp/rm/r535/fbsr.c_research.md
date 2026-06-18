<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r535/fbsr.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r535/fbsr.c

## Purpose
Implements R535 framebuffer save/restore support and an RM-aware instmem wrapper for suspend/resume.

## Important APIs, Types, And Functions
Defines `struct fbsr_item`, `struct fbsr`, `r535_fbsr_memlist`, `fbsr_init`, `fbsr_send`, `r535_fbsr_suspend`, `r535_fbsr_resume`, `r535_fbsr`, `r535_instmem_new`, and its destructor.

## Control Flow
Suspend builds a list of VRAM regions to preserve from instmem preserved objects, boot objects, and the GSP non-WPR heap. It totals region sizes, adds reserved framebuffer and VGA workspace sizes, allocates a scatter-gather sysmem buffer, creates a temporary RM client/device, registers sysmem with RM, then sends each VRAM region as a memory-list object and control command. Resume frees the sysmem buffer because RM has restored VRAM. `r535_fbsr_memlist` builds RM memory-list RPCs for host or framebuffer memory.

## State And Persistence
During suspend it persists `gsp->sr.fbsr` sysmem backup until resume. Temporary RM client/device/memory-list objects are freed after setup. Instmem wrapper disables zeroing while preserving hardware hooks.

## Dependencies And Integration Points
Depends on instmem lists, GSP SG allocation, RM device/client APIs, RM control commands, memory target/address helpers, and NV50 instmem construction.

## Risks And Edge Cases
Missing preserved regions can lose VRAM state across suspend. Memory-list page counts assume GSP page size alignment. Failure after sysmem allocation must free backup storage.

## Test Signals
Successful suspend with FBSR debug region logs, successful resume without VRAM corruption, and no SG memory leaks on failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r535/fbsr.c -->
