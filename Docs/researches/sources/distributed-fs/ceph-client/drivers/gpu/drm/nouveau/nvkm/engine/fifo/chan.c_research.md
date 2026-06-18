<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/fifo/chan.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/fifo/chan.c

## Purpose

`chan.c` implements FIFO channel lifetime, context binding, preemption, runlist insertion/removal, error/block/allow state, channel lookup by instance or CHID, USERD setup, RAMFC setup, and resource teardown.

## Important APIs, Types, And Functions

`nvkm_chan_cctx_get()/put()` manage per-channel context references to group vctxs. `nvkm_chan_cctx_bind()` blocks scheduling, preempts, updates engine binding, and resumes scheduling. `nvkm_chan_preempt()` and `_locked()` call generation preempt hooks and optionally wait. `nvkm_chan_insert()` and `nvkm_chan_remove()` maintain runlist/channel-group lists and trigger runlist updates. `nvkm_chan_error()` marks a channel errored, blocks it, optionally preempts, and notifies CHID events. `nvkm_chan_allow()` and `nvkm_chan_block()` maintain a block refcount. `nvkm_chan_get_inst()` and `nvkm_chan_get_chid()` locate channels for IRQ handlers. `nvkm_chan_new_()` validates arguments, creates or joins a group, allocates instance memory, joins VMM, binds push DMA objects, allocates CHID/USERD, clears USERD, and writes RAMFC.

## Control Flow

User channel creation calls a generation wrapper that ends in `nvkm_chan_new_()`. The channel starts blocked until inserted and allowed. When inserted, runlist state is updated under the runlist mutex. Engine context binding safely removes the channel or group from scheduling, preempts, updates context pointers, and allows scheduling. Errors from runqueue/runlist interrupts mark the channel disabled and notify clients.

## State And Persistence Behavior

`struct nvkm_chan` persists function table, name, runqueue, CHID, block/error atomics, context list, group reference, instance object, optional VMM reference, push object, RAMFC/cache/eng/pgd/RAMHT objects, USERD memory/base, and runlist membership. USERD may be caller-supplied or FIFO-managed.

## Dependencies And Integration Points

It depends on channel-group context management, CHID allocators, runlist update/preempt helpers, DMA object binding, MMU/VMM join/part, GPU object and RAMHT helpers, NVIF channel ABI, and generation `nvkm_chan_func` tables.

## Risks And Edge Cases

Argument validation is dense and generation-dependent. Partial creation failures rely on caller cleanup through `nvkm_chan_del()`. USERD bounds checks must prevent mapping past supplied memory. Blocking uses a refcount, so unmatched allow/block calls can leave channels stopped or running too early. Error notification requires holding the right lookup locks.

## Test Signals

Signals include successful channel creation for private and grouped channels, correct CHID allocation/release, USERD writes visible to clients, runlist updates after insert/remove, preemption wait success, channel error events on injected faults, and no leaked VMM joins or GPU objects after destroy.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/fifo/chan.c -->
