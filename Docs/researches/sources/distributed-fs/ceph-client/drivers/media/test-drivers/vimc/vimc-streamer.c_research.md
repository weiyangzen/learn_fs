# sources/distributed-fs/ceph-client/drivers/media/test-drivers/vimc/vimc-streamer.c

## Purpose
`vimc-streamer.c` runs the active VIMC media pipeline. It walks upstream from a capture node, enables subdevices, creates an ordered pipeline list, and starts a kernel thread that repeatedly pulls a frame from the source and pushes it through each entity to the capture sink.

## Important APIs, Types, and Functions
The exported API is `vimc_streamer_s_stream(struct vimc_stream *stream, struct vimc_ent_device *ved, int enable)`. Internal helpers include `vimc_get_source_entity()`, `vimc_streamer_pipeline_init()`, `vimc_streamer_pipeline_terminate()`, `vimc_streamer_get_sensor()`, and `vimc_streamer_thread()`. `struct vimc_stream` is declared in `vimc-streamer.h`.

## Control Flow
On enable, `vimc_streamer_s_stream()` returns if a thread already exists, otherwise initializes the pipeline. Pipeline initialization starts with the capture entity, stores each `vimc_ent_device`, enables subdev streaming where applicable, follows the first linked sink pad upstream, and stops when it reaches an entity with no upstream source, which must be source-only. It then starts `vimc-streamer thread`. The thread loops until stopped, reads FPS jiffies from the first sensor in the pipeline or defaults to 30 FPS, then iterates from source to sink calling each entity's `process_frame()` with the previous frame pointer. On disable, it stops the thread and terminates the pipeline in reverse order.

## State and Persistence
The stream object stores the media pipeline, up to 16 entity pointers, pipeline size, and kthread pointer. This state exists only while capture streaming is active and is cleared during termination.

## Dependencies and Integration Points
The streamer depends on media graph helpers, V4L2 subdev streaming state, kernel freezer/kthread APIs, and VIMC entity callbacks. Capture nodes call it from vb2 start/stop streaming; sensor/debayer/scaler/capture implementations provide the frame-processing callbacks it invokes.

## Risks and Edge Cases
Only the first sink pad is followed, so more complex fan-in topologies are not represented. Pipeline length is capped at 16. If any `process_frame()` returns null or error, remaining downstream entities are skipped for that frame. The streamer reads sensor internals to get frame cadence, coupling it to `struct vimc_sensor_device`.

## Test Signals
Tests should start and stop streaming repeatedly, validate pipeline order for each enabled link path, test immediate streamoff after streamon, confirm subdev `s_stream` calls balance on failures, and exercise no-buffer capture behavior where processing returns `-EAGAIN`.
