
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_fence.c

## Purpose
Implements Nouveau's common `dma_fence` wrapper and channel fence tracking. It provides fence creation, emission, signaling, waiting, synchronization against BO reservations, uevent-assisted callbacks, context teardown, and killed-channel cleanup for multiple hardware-specific fence backends.

## Important APIs, Types, and Functions
External functions include `nouveau_fence_create()`, `nouveau_fence_new()`, `nouveau_fence_emit()`, `nouveau_fence_done()`, `nouveau_fence_wait()`, `nouveau_fence_sync()`, `nouveau_fence_unref()`, `nouveau_fence_context_new()`, `nouveau_fence_context_del()`, `nouveau_fence_context_free()`, and `nouveau_fence_context_kill()`. Internal helpers include `nouveau_fence_signal()`, `nouveau_fence_update()`, `nouveau_fence_wait_legacy()`, `nouveau_fence_wait_busy()`, `nouveau_fence_is_signaled()`, and uevent callback/work handlers. The file defines legacy and uevent `dma_fence_ops`.

## Control Flow
Each channel owns a `nouveau_fence_chan` with a pending list, sequence counter, backend callbacks, lock, and optional NVIF non-stall interrupt event. `nouveau_fence_emit()` initializes the dma_fence, increments the context sequence, calls the backend emit method, then under lock updates already-completed fences and appends the new fence to pending. Signaling walks pending fences in sequence order based on the backend `read()` callback. Uevent mode allows NVIF events to schedule work that updates pending fences; legacy mode relies on polling/wait hooks. `nouveau_fence_sync()` iterates reservation fences, tries local GPU-side sync via backend `sync()`, and falls back to CPU waits when needed.

## State and Persistence
Per-channel state persists in `struct nouveau_fence_chan`: pending/flip lists, lock, kref, backend callbacks, sequence/context IDs, name, event, notify count, dead flag, and killed flag. Per-fence state includes the embedded `dma_fence`, pending-list node, RCU channel pointer, and timeout.

## Dependencies and Integration Points
The file depends on Linux dma-fence/dma-resv APIs, NVIF channel events, trace/fence infrastructure, Nouveau channel objects, and hardware-specific fence backend constructors declared in the header. GEM validation, EXEC, DMEM migration, display flips, and BO lifetime management all consume these fences.

## Risks and Test Signals
Risks include list lifetime under `dma_fence` callbacks, RCU channel pointer use after channel teardown, missed uevent blocking/unblocking, sequence wrap comparisons, and deadlock/performance regressions in `nouveau_fence_sync()`. Test signals include cross-channel BO sharing, external reservation fences, interrupt-driven and polling fence completion, channel kill with error propagation, fence callbacks after channel free, timeout waits, and lockdep with reservation locks.
