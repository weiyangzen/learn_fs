# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/engine/fifo.h

## Purpose

This header defines FIFO/channel scheduling state for Nouveau: channel objects, run queues/lists, USERD memory, RAMFC/cache/engine contexts, non-stall events, fault handling, and per-generation FIFO constructors.

## Important APIs, Types, and Functions

Key contracts are `struct nvkm_chan`, `struct nvkm_fifo`, `nvkm_chan_get_chid`, `nvkm_chan_get_inst`, `nvkm_chan_put`, `nvkm_uchan_chan`, `nvkm_fifo_fault`, `nvkm_fifo_pause`, `nvkm_fifo_start`, and `nvkm_fifo_ctxsw_in_progress`, plus constructors from `nv04_fifo_new` through `ga102_fifo_new`.

## Control Flow

Channel lookup pins a channel under FIFO locking by CHID or instance address. FIFO pause/start bracket fault recovery, runlist manipulation, or context-switch sensitive operations. Fault paths receive `nvkm_fault_data`, identify the channel/engine, and coordinate with non-stall event delivery and channel error/block state.

## State and Persistence Behavior

Channels persist GPU object references for instance memory, push buffer, RAMFC, RAMHT, cache and engine contexts, VMM, USERD memory/base, GSP RM objects, scheduler IDs, blocked/errored atomics, and context lists. FIFO state tracks CHID/CGID allocators, run queues, runlists, USERD BAR1 mapping, RM method buffer size, and locks.

## Dependencies and Integration Points

It integrates NVKM engine/object/event infrastructure, GSP RM channel objects, fault subdevices, graphics/video/copy engines, and DRM channel allocation through NVIF.

## Risks

Stale channel references during interrupts or fault handling can use freed context memory. Pause/start imbalance can deadlock scheduling. USERD or RAMFC programming mistakes break pushbuffer submission and recovery.

## Test Signals

Exercise channel allocation/free, runlist scheduling, GPU fault injection, non-stall event delivery, context-switch pause/resume, GSP-backed channels, and concurrent channel lookup during teardown.
