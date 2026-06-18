# sources/distributed-fs/ceph-client/drivers/media/v4l2-core/Kconfig

## Purpose
This Kconfig fragment defines V4L2 core feature symbols and helper module symbols used by media drivers. It controls optional subdevice APIs, advanced debug behavior, old fixed minor allocation, tuner support, codec/helper modules, mem2mem support, flash LED integration, fwnode/async support, CCI register helpers, and ISP support.

## Important symbols
`VIDEO_V4L2_I2C` is an internal bool enabled by default when both I2C and VIDEO_DEV are available. `VIDEO_V4L2_SUBDEV_API` exposes the pad-level subdevice userspace API and depends on media controller support. `VIDEO_ADV_DEBUG` and `VIDEO_FIXED_MINOR_RANGES` are user-visible toggles. `VIDEO_TUNER`, `V4L2_JPEG_HELPER`, `V4L2_H264`, `V4L2_VP9`, `V4L2_MEM2MEM_DEV`, `V4L2_FLASH_LED_CLASS`, `V4L2_FWNODE`, `V4L2_ASYNC`, `V4L2_CCI`, `V4L2_CCI_I2C`, and `V4L2_ISP` determine which helper objects or modules are built.

## Control flow
Kconfig has declarative dependency flow. Selecting `V4L2_FLASH_LED_CLASS` pulls in media controller, async, and subdev API support. Selecting `V4L2_FWNODE` pulls in async support. Selecting `V4L2_CCI_I2C` depends on I2C and selects both regmap I2C support and the base CCI helper. `V4L2_MEM2MEM_DEV` and `V4L2_ISP` depend on videobuf2 core.

## State and persistence behavior
The file persists build-time configuration, not runtime state. The resulting `.config` choices decide which V4L2 objects, exported symbols, and APIs are available to drivers. User-visible bools can affect compatibility with legacy userspace or debugging workflows.

## Dependencies and integration points
This fragment is paired with `drivers/media/v4l2-core/Makefile`. Symbols here gate compilation of files such as `tuner-core.c`, `v4l2-async.c`, `v4l2-cci.c`, `v4l2-fwnode.c`, codec helpers, and mem2mem helpers. Driver Kconfigs outside this directory select or depend on these symbols.

## Risks and edge cases
Incorrect dependencies can cause link failures, hidden APIs, or invalid user-visible configurations. Overusing `select` can silently enable dependencies without their prerequisites; underusing it can make helper symbols unavailable to drivers. Legacy `VIDEO_FIXED_MINOR_RANGES` should remain opt-in because it conflicts with modern udev-based allocation expectations.

## Test signals
Build matrix tests should cover VIDEO_DEV with and without I2C, MEDIA_CONTROLLER, LED flash class, V4L2_FWNODE, CCI over I2C, mem2mem, and helper modules as built-in and module. `make oldconfig`/`savedefconfig` diffs are useful signals for accidental prompt or default changes.
