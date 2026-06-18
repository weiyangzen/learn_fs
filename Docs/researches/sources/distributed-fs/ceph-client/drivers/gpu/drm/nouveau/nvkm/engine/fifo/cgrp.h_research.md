<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/fifo/cgrp.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/fifo/cgrp.h

## Purpose

`cgrp.h` defines FIFO channel-group, engine-context, and VMM-context data structures plus group helper prototypes.

## Important APIs, Types, And Functions

`struct nvkm_vctx` tracks a VMM-specific subcontext, instance GPU object, VMA, and ectx reference. `struct nvkm_ectx` tracks an engine-level group context and backing object. `struct nvkm_cgrp` stores function table, name, runlist, VMM, hardware group flag, id, kref, channel list/count, lookup lock, context lists, mutex, recovery state, and runlist list node. The header declares group creation/ref/unref, vctx get/put, IRQ lock put, channel iteration macros, and logging macros.

## Control Flow

Channel creation and engine bind paths use these structures to share contexts across channels. Recovery and preemption paths consult the group function table and `rc` state.

## State And Persistence Behavior

The header defines all persistent group state. `rc` tracks none/pending/running recovery states. `chans`, `ectxs`, and `vctxs` are lifetime-managed lists.

## Dependencies And Integration Points

It includes core OS helpers and is used by FIFO channel, runlist, generation backends, and user channel-group code.

## Risks And Edge Cases

The `lock` protects IRQ handler channel/group lookup, while `mutex` protects context lists; mixing them incorrectly risks deadlock or stale lookups. Group `id` may be a CGID or fall back to a channel id depending on hardware.

## Test Signals

Build integration plus runtime context reuse, group preemption, recovery state transitions, and correct logs with group ids validate this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/fifo/cgrp.h -->
