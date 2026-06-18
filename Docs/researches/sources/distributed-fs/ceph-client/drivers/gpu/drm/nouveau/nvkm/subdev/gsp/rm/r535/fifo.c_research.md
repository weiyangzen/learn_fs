<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r535/fifo.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r535/fifo.c

## Purpose
Implements R535 RM-backed FIFO, runlist, channel allocation, engine discovery, channel error recovery, and constructed Falcon context sizing.

## Important APIs, Types, And Functions
Defines channel callbacks, `r535_chan_alloc`, `r535_chan_ramfc_write/clear`, engine functions for CE/GR/Falcon engines, `r535_fifo_rc_chid`, `r535_fifo_rc_triggered`, `r535_fifo_xlat_rm_engine_type`, `r535_fifo_ectx_size`, `r535_fifo_runl_ctor`, `r535_fifo_new`, and exports `r535_fifo`.

## Control Flow
Runlist construction allocates CHID/CGID spaces, queries RM's device info table, creates runlists, translates RM engine IDs to NVKM types/instances, skips unsupported SW engines and lone GRCEs, creates RM-backed engines, adds them to runlists, stores engine descriptors, queries CE fault method buffer size, and fetches constructed Falcon context sizes. Channel RAMFC write allocates a coherent method buffer, calls RM channel allocation with instance/userd/ramfc/method/gpfifo data, binds the engine, and schedules the GPFIFO. RC notifications log RM exception data and mark the channel in error.

## State And Persistence
Persists FIFO function table, runlists, engines, CHID allocators, channel RM objects, method buffers, GR context refs, engine RM descriptors/sizes, and nonstall interrupt state.

## Dependencies And Integration Points
Depends on NVKM FIFO/runlist/channel frameworks, GSP internal RM controls, RM GPU class/callback data, GR context constructors, DMA coherent allocation, and GSP interrupt lookup.

## Risks And Edge Cases
RM engine translation must be complete. Method buffer allocation cleanup depends on `ramfc_clear`. GR contexts take extra refs until channel deletion. Device info table changes can expose unsupported engine types.

## Test Signals
Successful runlist construction, channel creation/scheduling, workload execution, RC error reporting, and clean channel teardown without memory leaks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/rm/r535/fifo.c -->
