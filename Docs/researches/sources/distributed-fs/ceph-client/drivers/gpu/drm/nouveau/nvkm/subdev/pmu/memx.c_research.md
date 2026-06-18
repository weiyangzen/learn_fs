# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/pmu/memx.c

## Purpose
Builds and optionally executes PMU MEMX scripts used for memory register programming, waits, delays, vblank synchronization, and training.

## Important APIs, Types, And Functions
`struct nvkm_memx` caches batched method/data words. Public helpers include `nvkm_memx_init()`, `nvkm_memx_fini()`, `nvkm_memx_wr32()`, `nvkm_memx_wait()`, `nvkm_memx_nsec()`, `nvkm_memx_wait_vblank()`, `nvkm_memx_train()`, `nvkm_memx_train_result()`, `nvkm_memx_block()`, and `nvkm_memx_unblock()`.

## Control Flow
Init asks the PMU MEMX process for data buffer base/size, locks PMU data access, and positions writes. Commands are coalesced when method-compatible, flushed when full or incompatible, and finally released; optional execution sends `MEMX_MSG_EXEC` and logs execution timing.

## State, Persistence, And Dependencies
State lives in the heap `nvkm_memx` script builder, PMU data segment, cached command buffer, and PMU training result area. No filesystem persistence exists.

## Integration Points
Depends on working PMU mailbox send/receive, MEMX FUC process IDs, display head registers for vblank selection, and memory training callers.

## Risks
The file trusts PMU-reported buffer bounds and has hardware-specific vblank heuristics. WAIT/DELAY/VBLANK are force-flushed because firmware cannot handle multiple combined operations.

## Test Signals
Signals include successful script execution replies, expected register traces, memory training result reads of the expected size, and no PMU data-access lock hangs.
