# sources/distributed-fs/ceph-client/drivers/media/platform/samsung/exynos4-is/common.c

## Purpose
`common.c` provides shared helper routines exported to Samsung Exynos camera subsystem drivers. It locates the remote sensor at the head of a media pipeline and fills common V4L2 capability strings.

## Important APIs, Types, and Functions
`fimc_find_remote_sensor()` walks upstream through media pads until it finds a V4L2 subdevice whose group id is `GRP_ID_FIMC_IS_SENSOR` or `GRP_ID_SENSOR`. `__fimc_vidioc_querycap()` copies the device driver name into the V4L2 `driver` and `card` fields. Both functions are exported with `EXPORT_SYMBOL()`.

## Control Flow
`fimc_find_remote_sensor()` starts at entity pad 0, follows remote source pads while the current pad is a sink, converts V4L2 subdev entities to `struct v4l2_subdev`, and stops on a matching sensor group id or a broken/non-subdev link. `__fimc_vidioc_querycap()` is a direct string-copy helper.

## State and Persistence
The helpers are stateless and derive results from the live media graph and device driver metadata.

## Dependencies and Integration Points
The file depends on media entity and V4L2 subdev helpers plus Exynos FIMC group ids from `media/drv-intf/exynos-fimc.h`. FIMC capture uses `fimc_find_remote_sensor()` when enabling links and inherits sensor controls, while capture video nodes use `__fimc_vidioc_querycap()`.

## Risks and Edge Cases
The graph walk assumes pad 0 is the sink on intermediate subdevices, matching this subsystem's convention. Broken links or non-subdev entities return `NULL`. Callers must hold the graph mutex or otherwise guarantee streaming graph stability, as documented in the comment.

## Test Signals
Validate sensor discovery through direct sensor-to-FIMC links, CSIS/FIMC-LITE intermediate links, FIMC-IS sensor group ids, disconnected links returning `NULL`, and querycap strings on all video nodes using the helper.
