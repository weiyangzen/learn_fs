# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/engine/gr.h

## Purpose

This header defines the graphics engine wrapper, Z-cull information exposed to legacy userspace, context-switch controls, TLB flush support, and per-generation graphics constructors.

## Important APIs, Types, and Functions

Core items are `struct nvkm_gr_zcull_info`, `struct nvkm_gr`, `nvkm_gr_units`, `nvkm_gr_tlb_flush`, `nvkm_gr_ctxsw_pause`, `nvkm_gr_ctxsw_resume`, `nvkm_gr_ctxsw_inst`, and generation constructors from NV04 through GA102.

## Control Flow

Graphics constructors build a generation-specific engine and optionally populate Z-cull geometry/context-switch metadata. Runtime helpers report active units, flush graphics TLBs after VMM changes, and pause/resume context switching around sensitive register or memory operations.

## State and Persistence Behavior

Persistent driver state is the engine object plus cached Z-cull fields and `has_zcull_info`. Hardware context-switch state changes when pause/resume helpers execute and must be restored after protected operations.

## Dependencies and Integration Points

It is used by ABI16 getparam/Z-cull ioctls, MMU invalidation paths, channel context management, and all chip-specific GR implementations.

## Risks

Wrong Z-cull metadata breaks userspace tiling assumptions. Missing TLB flushes can cause GPU faults after remapping. Context-switch pause imbalance can hang graphics channels.

## Test Signals

Run graphics channel creation, Z-cull info ioctls, TLB flush after buffer remap, context-switch pause/resume fault injection, and generation selection build coverage.
