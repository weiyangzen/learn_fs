# sources/distributed-fs/ceph-client/drivers/media/test-drivers/vimc/vimc-sensor.c

## Purpose
`vimc-sensor.c` implements VIMC source subdevices backed by the V4L2 test pattern generator. Sensors generate frames, overlay optional text, expose image and timing controls, and provide frame cadence information used by the streamer thread.

## Important APIs, Types, and Functions
The implementation uses `struct vimc_sensor_device` from `vimc-common.h`. Key callbacks are `vimc_sensor_init_state()`, bus-code/frame-size enumeration, `vimc_sensor_set_fmt()`, `vimc_sensor_s_stream()`, `vimc_sensor_process_frame()`, and `vimc_sensor_s_ctrl()`. Timing helpers include `vimc_calc_vblank()` and `vimc_sensor_update_frame_timing()`. Controls include test pattern, OSD mode, H/V flip, brightness, contrast, hue, saturation, read-only pixel rate, read-only hblank, and adjustable vblank.

## Control Flow
Subdev state initializes to 640x480 RGB888. Format setting clamps size, validates bus code, clamps colorimetry, blocks active changes while streaming, updates hardware size, recalculates default vblank based on resolution target FPS, and updates timing controls. Stream-on configures the TPG for active format, computes frame size, updates frame timing, allocates a frame buffer, and records stream start time. `process_frame()` fills the frame with TPG output and optionally overlays color order, control values, sensor size, and elapsed-time counters.

## State and Persistence
Runtime state includes active subdev format, TPG data, control handler values, allocated frame, and `hw` fields for size, OSD mode, stream timestamp, and `fps_jiffies`. It is volatile and reset on stream-off/release. `fps_jiffies` is read by `vimc-streamer.c` to schedule frames.

## Dependencies and Integration Points
The sensor depends on V4L2 subdev/control/event APIs, media-bus formats, vmalloc, V4L2 TPG, and common VIMC helpers. It is the source for raw capture, debayer, scaler through the RGB/YUV input placeholder, and ancillary lens links.

## Risks and Edge Cases
TPG allocation is sized to maximum width and must remain consistent with negotiated formats. Stream-off frees `frame` without checking whether it is already null, which is safe for `vfree()`. Timing is simulated through jiffies, so precision is coarse. The RGB/YUV input entity reuses sensor behavior, which may blur semantic distinctions in topology tests.

## Test Signals
Tests should stream all supported formats, exercise TPG controls, OSD modes, timing controls and resolution changes, verify frame cadence changes around the 30 FPS threshold, and ensure active format changes are rejected during streaming.
