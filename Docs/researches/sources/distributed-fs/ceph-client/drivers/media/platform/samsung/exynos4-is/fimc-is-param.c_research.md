# sources/distributed-fs/ceph-client/drivers/media/platform/samsung/exynos4-is/fimc-is-param.c

## Purpose
`fimc-is-param.c` maintains the host-side FIMC-IS pipeline parameter cache and copies dirty parameter blocks into the DMA-shared firmware region before `HIC_SET_PARAMETER`. It also provides helpers to initialize and mutate ISP, sensor, DRC, and face-detection parameters.

## Important APIs, Types, and Functions
Low-level update helpers are `__fimc_is_hw_update_param()`, `__get_pending_param_count()`, and `__is_hw_update_params()`. Configuration helpers include `__is_set_frame_size()`, `fimc_is_hw_get_sensor_max_framerate()`, `__is_set_sensor()`, `__is_set_isp_flash()`, `__is_set_isp_awb()`, `__is_set_isp_effect()`, `__is_set_isp_iso()`, `__is_set_isp_adjust()`, `__is_set_isp_metering()`, `__is_set_isp_afc()`, `__is_set_drc_control()`, `__is_set_fd_control()`, the `__is_set_fd_config_*()` family, and `fimc_is_set_initial_params()`.

## Control Flow
Callers update fields in `is->config[is->config_index]` and mark parameter bits with `fimc_is_set_param_bit()`. Before sending parameters, `__is_hw_update_params()` walks the dirty bitmaps, copies selected 64-byte parameter blocks into `is->is_p_region->parameter`, and leaves the firmware command layer to write the mailbox and wait for completion. Initialization fills defaults for all four scenarios, enabling ISP/DRC/FD OTF paths, disabling unused DMA inputs/outputs, configuring default 3A, flash, AWB, ISO, metering, AFC, and FD options.

## State and Persistence
The primary state is `struct chain_config config[IS_SC_MAX]`, per-scenario dirty bitmaps `p_region_index[0..1]`, and the shared DMA parameter region pointed to by `is->is_p_region`. Updates are volatile and synchronized partly by `is->slock` for pending-count reads; memory barriers are used by the command layer before firmware consumption.

## Dependencies and Integration Points
The file depends on FIMC-IS core structures, command/error constants, register command helpers, V4L2 media bus frame formats, bit operations, and sensor metadata. `fimc-is.c` calls `fimc_is_set_initial_params()` during hardware initialization, while ISP controls call the individual setters and then `fimc_is_itf_s_param()`.

## Risks and Edge Cases
Only a subset of the parameter ABI is copied by `__fimc_is_hw_update_param()`; dirty bits for unsupported blocks would return `-EINVAL` or be ignored by loop ranges. FD parameter bits live above bit 31, and helpers manually inspect `p_region_index[1]` with `PARAM_FD_CONFIG - 32`, so bit-index mistakes are likely. Some defaults set duplicate `width` fields in DMA input structures and rely on packed ABI layout. Sensor framerate defaults depend on only the first `is->sensor` entry.

## Test Signals
Validate initial parameter upload for all scenarios, dirty bit counts matching copied blocks, frame-size updates marking ISP/DRC/FD OTF bits, sensor framerate zero and explicit FPS behavior, ISP controls setting combined command masks, FD config command accumulation across multiple setters, set-parameter timeout recovery, and firmware rejection logs for invalid parameter values.
