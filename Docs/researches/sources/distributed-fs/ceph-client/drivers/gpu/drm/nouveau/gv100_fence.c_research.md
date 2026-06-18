
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/gv100_fence.c

## Purpose
Provides GV100-era Nouveau fence emit and sync operations using NVC36F semaphore methods, extending the NV84 fence infrastructure.

## Important APIs, types, and functions
- `gv100_fence_emit32()` releases a 32-bit sequence to a memory semaphore, emits a system membar, triggers a non-stall interrupt, and kicks the channel.
- `gv100_fence_sync32()` waits with `ACQ_CIRC_GEQ` against a 32-bit memory semaphore and kicks the channel.
- `gv100_fence_context_new()` creates the base NV84 fence channel context and overrides `.emit32`/`.sync32`.
- `gv100_fence_create()` creates the base fence private object and overrides `.context_new`.

## Control flow
Driver initialization calls `gv100_fence_create()`, which delegates to `nv84_fence_create()` and installs a GV100 context factory. Each channel context is then created through NV84 code and patched with GV100 semaphore operations. Fence emission writes address and payload, executes a release with WFI and 32-bit payload size, performs a system memory barrier, emits a non-stall interrupt, and kicks. Sync writes address/payload and executes an acquire greater-or-equal operation with TSG switching enabled.

## State and persistence
Persistent state remains in the inherited `nv84_fence_priv` and per-channel `nv84_fence_chan`. This file changes function pointers and writes GPU semaphore state to the channel pushbuffer. Fence sequence values persist in memory until overwritten.

## Dependencies and integration points
Depends on `nouveau_drv.h`, `nouveau_dma.h`, `nouveau_fence.h`, `nv50_display.h`, `nvif/push906f.h`, and `clc36f.h`. It integrates with Nouveau channel scheduling, dma-fence signaling, and legacy NV84 fence management.

## Risks
Memory ordering is critical: removing or weakening the SYS_MEMBAR can make CPU/GPU synchronization observe stale data. Address splitting and payload size must match the allocated fence memory. Missing `NON_STALL_INTERRUPT` would delay fence completion notification.

## Test signals
GPU channel workloads should signal fences reliably under stress. Cross-channel sync tests should wait for sequence values without hangs. Useful failure signals include fence timeouts, missing interrupts, or data visibility races after fence completion.
