# sources/distributed-fs/ceph-client/drivers/media/platform/samsung/exynos4-is/common.h

## Purpose
`common.h` declares the shared Exynos4 camera helper functions implemented in `common.c`.

## Important APIs, Types, and Functions
It declares `fimc_find_remote_sensor(struct media_entity *entity)` and `__fimc_vidioc_querycap(struct device *dev, struct v4l2_capability *cap)`.

## Control Flow
There is no executable control flow.

## State and Persistence
The header stores no state and only exposes helper prototypes.

## Dependencies and Integration Points
It includes Linux device and videodev2 definitions plus media entity and V4L2 subdev headers so FIMC, FIMC-IS, and shared capture code can use common helper declarations.

## Risks and Edge Cases
The header intentionally has a small API surface. Any signature changes must be coordinated with exported symbol users and module builds.

## Test Signals
Compile coverage of FIMC capture and any other users verifies declarations and exported definitions remain aligned.
