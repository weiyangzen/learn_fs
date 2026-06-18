# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/fifo/runq.c

Purpose: implements minimal allocation and destruction for FIFO runqueues/PBDMAs.

Important APIs and data: `nvkm_runq_new()` allocates a zeroed `struct nvkm_runq`, assigns `fifo->func->runq`, stores FIFO pointer and PBDMA id, and appends it to `fifo->runqs`. `nvkm_runq_del()` removes the list entry and frees it.

Control flow: common FIFO construction creates one runqueue per hardware PBDMA using this helper. Chip-specific runqueue callbacks then initialize registers, handle interrupts, and report idle state.

State and persistence: state is an in-memory list node, callback pointer, FIFO pointer, and PBDMA id. No hardware programming is done here and no state persists across driver lifetime.

Dependencies and integration: depends on `runq.h` and `priv.h`, and is consumed by the common FIFO constructor and chip-specific runlist constructors that associate runqueues with runlists.

Risks: allocation failure returns NULL rather than encoded error; callers must handle it. Deleting a runqueue assumes it is linked and no longer referenced by a runlist.

Test signals: runqueue count equals chip-specific `runq_nr`, PBDMA ids match interrupt/register offsets, clean teardown removes all list entries, and build coverage for FIFO construction.
