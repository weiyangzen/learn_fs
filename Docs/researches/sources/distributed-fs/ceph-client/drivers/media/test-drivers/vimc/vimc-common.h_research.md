# sources/distributed-fs/ceph-client/drivers/media/test-drivers/vimc/vimc-common.h

## Purpose
`vimc-common.h` is the shared interface for the VIMC virtual media graph. It defines common constants, controls, entity abstractions, pixel-format maps, device structures, sensor state, and helper prototypes.

## Important APIs, Types, and Functions
Important definitions include frame size limits, fixed timing constants, custom controls `VIMC_CID_TEST_PATTERN`, `VIMC_CID_MEAN_WIN_SIZE`, and `VIMC_CID_OSD_TEXT_MODE`, allocator enum, source/sink pad macros, and `vimc_colorimetry_clamp()`. Core types are `struct vimc_pix_map`, `struct vimc_ent_device`, `struct vimc_device`, `struct vimc_ent_type`, `struct vimc_ent_config`, and `struct vimc_sensor_device`. It declares all entity type exports and common helpers for format lookup, subdev registration, source detection, and link validation.

## Control Flow
`vimc-core.c` consumes `vimc_ent_config` and `vimc_ent_type` callbacks to instantiate topology entities. Each entity embeds or references `vimc_ent_device` so the streamer can call `process_frame()` uniformly and link validation can query video-node formats through `vdev_get_format()`.

## State and Persistence
Most structures describe per-device or per-entity runtime state. `vimc_sensor_device` includes test-pattern generator state, controls, media pad, frame buffer, and virtual hardware timing/OSD configuration. `vimc_allocator` is a module parameter declared externally and used by capture queue setup.

## Dependencies and Integration Points
The header includes platform device, slab, media-device, V4L2 device, TPG, and V4L2 controls headers. It forms the internal ABI between all VIMC object files; changes here can impact core topology, streamer, capture, sensor, debayer, scaler, and lens.

## Risks and Edge Cases
The `VIMC_IS_SRC(pad)` and `VIMC_IS_SINK(pad)` macros assume pad 0 is sink and nonzero is source, which matches current two-pad entities but is not a general media-entity rule. `vimc_colorimetry_clamp()` uses upper-bound checks tied to current V4L2 enum ranges. Exposing `vimc_sensor_device` here allows streamer code to inspect sensor hardware timing, but also couples streamer to sensor internals.

## Test Signals
Build tests catch internal ABI drift. Runtime tests should exercise custom controls, allocator selection, frame size limits, colorimetry clamping, and pipeline traversal across all entity types.
