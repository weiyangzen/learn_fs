# sources/distributed-fs/ceph-client/drivers/media/test-drivers/vimc/vimc-common.c

## Purpose
`vimc-common.c` provides shared pixel-format mapping, source detection, link validation, and subdevice registration helpers for all VIMC entities.

## Important APIs, Types, and Functions
The central static table `vimc_pix_map_list[]` maps media-bus codes to V4L2 fourcc formats, bytes per pixel, and Bayer/non-Bayer classification. Exported lookup helpers are `vimc_pix_map_by_index()`, `vimc_mbus_code_by_index()`, `vimc_pix_map_by_code()`, and `vimc_pix_map_by_pixelformat()`. `vimc_is_source()` detects entities with no sink pads. `vimc_vdev_link_validate()` compares source and sink formats. `vimc_ent_sd_register()` initializes and registers a V4L2 subdevice entity with pads, ops, optional active-state initialization, and devnode exposure.

## Control Flow
Link validation retrieves a source and sink `v4l2_pix_format` either through subdev `get_fmt` or a video-device `vdev_get_format` callback, logs both formats, enforces matching width, height, pixelformat, compatible field order, and compatible colorimetry. Subdevice registration fills `vimc_ent_device`, initializes the subdev, assigns entity function and ops, sets flags for devnode/events, initializes pads, finalizes active state if supported, and registers with the parent V4L2 device.

## State and Persistence
The format map is static read-only state. The helper functions do not own long-lived resources except during successful subdevice registration. `vimc_ent_sd_register()` transfers initialized media entity/subdev state to V4L2 core and cleans it up on failure.

## Dependencies and Integration Points
The file depends on media entity helpers, V4L2 subdev and video-device APIs, V4L2 controls, and `vimc-common.h`. All entity implementations depend on these helpers for consistent format negotiation and registration.

## Risks and Edge Cases
`vimc_get_pix_format()` assumes `vimc_pix_map_by_code()` succeeds after subdev `get_fmt`; a missing map would lead to a null dereference. Link validation intentionally skips detailed colorimetry comparison if either side uses default colorspace. The format table ordering matters because the scaler's enumeration expects non-Bayer formats first.

## Test Signals
Tests should enumerate all bus codes and pixel formats, validate links with matching and mismatching dimensions/pixelformats/colorimetry, and run subdevice registration failure injection to verify cleanup.
