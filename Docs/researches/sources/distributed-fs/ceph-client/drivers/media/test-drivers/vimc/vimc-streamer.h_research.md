# sources/distributed-fs/ceph-client/drivers/media/test-drivers/vimc/vimc-streamer.h

## Purpose
`vimc-streamer.h` declares the streaming engine state and the start/stop API used by VIMC capture nodes.

## Important APIs, Types, and Functions
`VIMC_STREAMER_PIPELINE_MAX_SIZE` limits a runtime pipeline to 16 entities. `struct vimc_stream` contains a `media_pipeline`, ordered `ved_pipeline` array, `pipe_size`, and `task_struct *kthread`. `vimc_streamer_s_stream()` starts or stops streaming for a capture-anchored pipeline.

## Control Flow
Capture entities embed `struct vimc_stream` and pass it plus their `vimc_ent_device` to `vimc_streamer_s_stream()` from vb2 start/stop callbacks. The implementation fills the array and manages the thread.

## State and Persistence
The struct is per capture stream and transient. It does not persist beyond active streaming and is reset by the implementation on stop.

## Dependencies and Integration Points
The header includes media-device APIs and `vimc-common.h`. It is consumed by `vimc-capture.c` and implemented by `vimc-streamer.c`.

## Risks and Edge Cases
The fixed-size array means topology expansion must also revisit the max size. Callers must pass a valid capture-side entity and must not concurrently start/stop the same stream without the capture/vb2 locks.

## Test Signals
Compile tests catch API drift. Runtime tests should verify no stale `kthread` pointer remains after stop and that pipeline sizes fit the hard-coded topology.
