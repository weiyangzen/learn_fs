<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/fifo/chan.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/fifo/chan.h

## Purpose

`chan.h` defines FIFO channel and channel-context function-table contracts and helper prototypes.

## Important APIs, Types, And Functions

`struct nvkm_cctx` tracks a channel's reference to a group/VMM engine context. `struct nvkm_chan_func` describes generation-specific instance block, USERD, RAMFC, bind/unbind/start/stop/preempt, and doorbell behavior. Nested structs describe instance memory size/zero/VMM requirements, USERD BAR/base/size/clear hook, and RAMFC layout/write/clear/ctxdma/devm/priv requirements. The header declares channel creation/destruction, allow/block/error, insert/remove, preempt, context get/put/bind, and logging macros.

## Control Flow

Generation backends fill an `nvkm_chan_func`; user channel constructors pass it to `nvkm_chan_new_()`. Runtime scheduling, error, and context paths call the optional hooks according to this contract.

## State And Persistence Behavior

The header defines how persistent channel state is initialized and what hardware resources it owns: instance, USERD, RAMFC, optional push DMA, and context objects.

## Dependencies And Integration Points

It includes public FIFO engine definitions and is consumed by shared channel code, generation FIFO files, runlist code, and user channel wrappers.

## Risks And Edge Cases

Boolean requirements in `nvkm_chan_new_()` are driven by these nested fields; inconsistent generation tables reject valid channels or accept invalid ones. Optional `preempt` and `doorbell_handle` must be checked by callers.

## Test Signals

Build coverage and successful channel creation across generations validate the prototypes. Runtime tests should cover both ctxdma and non-ctxdma RAMFC paths, BAR1 and supplied USERD, and privileged channel rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/fifo/chan.h -->
