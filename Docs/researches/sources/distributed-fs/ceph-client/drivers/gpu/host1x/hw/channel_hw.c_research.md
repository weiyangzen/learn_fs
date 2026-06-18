<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/hw/channel_hw.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/host1x/hw/channel_hw.c

## Purpose

`hw/channel_hw.c` is the generation-specialized host1x channel submission engine. It converts pinned `host1x_job` command descriptors into pushbuffer opcodes, handles waits/gathers/setclass, programs stream IDs and MLOCK sequences on HW6+, creates completion fences, and starts CDMA.

## Important APIs, Types, And Functions

- `submit_wait()`, `submit_setclass()`, and `submit_gathers()` emit host1x opcodes for waits, stream-ID-aware class switches, and gather DMA.
- `synchronize_syncpt_base()` supports relative waits on older hardware with wait bases.
- `host1x_channel_set_streamid()` and `host1x_enable_gather_filter()` program stream ID/filtering for secure gather handling.
- `channel_program_cdma()` builds the full command sequence, with older-HW serialization/base handling and HW6+ MLOCK/stream-ID/idle-fence wrapping.
- `channel_submit()` is the operation-table submit callback, handling submit lock, CDMA begin/end, fence creation, and tracepoints.
- `host1x_channel_init()` computes each channel's MMIO base.

## Control Flow

Submission locks `submitlock`, sets channel stream ID, enables gather filtering, assigns the syncpoint to the channel, begins CDMA, and emits opcodes. On HW6+, absolute pre-fence waits are emitted with an invalid stream ID, engine MLOCK is acquired, an idle fence is inserted before switching to the real stream ID, work gathers are submitted, another idle fence is inserted, and MLOCK is released. Older hardware optionally serializes against the syncpoint's current max, synchronizes wait base, emits setclass, increments syncpoint max, and submits gathers. A fence is created before `host1x_cdma_end()` flushes hardware so a fast completion is not missed.

## State And Persistence Behavior

The function mutates channel registers, CDMA pushbuffer, syncpoint max values, job `syncpt_end`, job fence/callback fields, and syncpoint channel assignment. Hardware-visible stream IDs and gather filter bits persist until changed by later submissions or reset.

## Dependencies And Integration Points

Depends on opcodes, generated register headers, `cdma.c`, `job.c`, `fence.c`, `syncpt.c`, tracepoints, and Tegra IOMMU stream-ID helpers. It is included into each generation build unit with `HOST1X_HW` controlling code shape.

## Risks And Test Signals

The HW6+ MLOCK/stream-ID sequence is security-sensitive; incorrect ordering can let an engine access buffers under the wrong stream ID. Fence creation errors are warned but submit still returns success. 64-bit gather addresses require `GATHER_W` support. Tests should include pre-fence waits, relative waits, wide gathers above 4 GiB, stream-ID isolation, MLOCK release after timeout, and submit-complete fence callbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/hw/channel_hw.c -->
