# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvc0_fence.c

## Purpose
This file adapts the NV84 fence backend to Fermi/NVC0 semaphore method encodings.

## Important APIs, Types, and Functions
Main entry point is `nvc0_fence_create`. Internal helpers `nvc0_fence_emit32`, `nvc0_fence_sync32`, and `nvc0_fence_context_new` override the NV84 per-channel emit/sync function pointers.

## Control Flow
Creation delegates to `nv84_fence_create`, then replaces the global context-new hook. Context creation delegates to `nv84_fence_context_new` and swaps the per-context `emit32` and `sync32` methods. Emit programs NV906F release with WFI and 16-byte release size; sync programs NV906F acquire greater-or-equal with acquire switch enabled.

## State and Persistence Behavior
State is inherited from NV84: shared fence BO, per-channel slots, VMA refs, and suspend data. This file only changes method encodings.

## Dependencies and Integration Points
It depends on NV906F push methods, NV84 fence structures/functions, and generic Nouveau fence infrastructure.

## Risks
Incorrect method flags can cause fences to signal before work is complete or fail to wait. Since state is inherited, NV84 BO and VMA lifecycle bugs affect NVC0 too.

## Test Signals
Signals include NVC0 fence release/acquire ordering, non-stall interrupt behavior, cross-channel synchronization, and regression tests shared with NV84.
