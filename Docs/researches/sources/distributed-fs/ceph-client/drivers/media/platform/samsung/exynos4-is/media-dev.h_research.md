# sources/distributed-fs/ceph-client/drivers/media/platform/samsung/exynos4-is/media-dev.h

## Purpose
Defines the top-level FIMC media-device data structures, entity names, limits, pipeline indices, clock-provider structures, and helper accessors used across the Samsung camera media graph.

## Important APIs, Types, and Functions
Key types are `struct fimc_pipeline`, `struct fimc_sensor_info`, `struct cam_clk`, and `struct fimc_md`. Helper functions/macros include `to_fimc_pipeline()`, `source_to_sensor_info()`, `entity_to_fimc_mdev()`, `notifier_to_fimc_md()`, graph lock/unlock helpers, `fimc_md_is_isp_available()`, and `__fimc_md_get_subdev()`.

## Control Flow
The pipeline index enum defines ordered positions for sensor, CSIS, FIMC-LITE, FIMC-IS ISP, and FIMC capture subdevices. Media-device code fills these slots during graph walks and then uses them for power and stream sequencing.

## State and Persistence
`struct fimc_md` is the persistent runtime container for one media-device instance: registered entities, sensor descriptors, clocks, notifier, media/v4l2 devices, mode flags, spinlock, pipelines, and graph walk object. It is allocated at probe and released at remove.

## Dependencies and Integration Points
Includes media controller, V4L2 subdev/device, clk provider, OF, and all local entity headers. It is the shared contract between the top-level media device and subdrivers.

## Risks and Edge Cases
The helper `entity_to_fimc_mdev()` assumes any associated media device is embedded in `struct fimc_md`; using it on foreign media entities would miscast. `fimc_md_is_isp_available()` only checks for an available child node named `fimc-is`, so unusual DT layouts are invisible.

## Test Signals
Compile with and without OF, test graph helpers on all registered entity types, validate pipeline slot population from several graph shapes, and verify clock arrays are initialized before cleanup paths.
