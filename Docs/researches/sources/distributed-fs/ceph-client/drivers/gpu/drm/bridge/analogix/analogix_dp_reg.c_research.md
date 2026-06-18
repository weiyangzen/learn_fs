# sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/analogix/analogix_dp_reg.c

Purpose: MMIO register access layer for Analogix DP controllers. It implements reset, power, interrupt, HPD, AUX, link-training, video, scrambling, and PSR packet helper operations used by `analogix_dp_core.c`.

Important APIs/types/functions: Major functions include `analogix_dp_reset`, `analogix_dp_init_analog_param`, `analogix_dp_init_interrupt`, `analogix_dp_set_analog_power_down`, `analogix_dp_init_analog_func`, `analogix_dp_init_aux`, `analogix_dp_transfer`, `analogix_dp_set_link_bandwidth`, `analogix_dp_set_lane_count`, `analogix_dp_set_lane_link_training`, `analogix_dp_set_training_pattern`, `analogix_dp_config_video_slave_mode`, `analogix_dp_is_video_stream_on`, and `analogix_dp_send_psr_spd`.

Control flow: Initialization resets video and function blocks, writes analog tuning, clears/masks interrupts, initializes HPD/AUX, powers analog blocks, and enables software/AUX functions. Link training helpers set bandwidth/lane registers, call optional PHY configuration, program lane voltage/pre-emphasis, training pattern, macro reset, and enhanced mode. AUX transfer clears the buffer, encodes request type and MOT, writes address/payload, starts hardware, polls for completion and reply, decodes defer/ACK, and resets AUX on error. Video helpers program color/timing, detect input clock/stream, and start output. PSR writes VSC SDP/header/payload registers and optionally polls sink PSR status.

State and persistence: The layer stores no independent software state; it mutates `dp->reg_base` registers and reads `dp->plat_data`, `video_info`, and `link_train`. Optional PHY state is configured through `phy_configure`.

Dependencies and integration: Depends on Linux MMIO `readl/writel`, `readx_poll_timeout`, PHY API, GPIO for HPD, DRM DP helper constants, and `analogix_dp_reg.h` bit definitions. It has Rockchip-specific branches selected by platform `dev_type`.

Risks: AUX request length macro computes `(x - 1)` and is used even for zero-size messages before `ADDR_ONLY`; hardware tolerance matters. Some helpers return after logging PHY configuration failures without propagating them. Rockchip and non-Rockchip power masks differ, so platform type errors can power down the wrong blocks. Polling timeouts can cause modeset latency.

Test signals: MMIO trace comparison, AUX native/I2C read/write/defer/error tests, PHY configure parameter assertions, link training on 1/2/4 lanes, video stream detection, HPD GPIO versus register mode, PSR enter/exit, and Rockchip/non-Rockchip reset paths.
