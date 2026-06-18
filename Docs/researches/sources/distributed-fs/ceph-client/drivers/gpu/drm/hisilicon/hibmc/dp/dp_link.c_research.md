# sources/distributed-fs/ceph-client/drivers/gpu/drm/hisilicon/hibmc/dp/dp_link.c

Purpose: implements DisplayPort link training for HIBMC, including DPCD capability discovery, local transmitter/SERDES setup, clock recovery, channel equalization, and fallback to lower link rates or fewer lanes.

Important APIs/functions: `hibmc_dp_link_training()` is the exported entry point. Internal helpers map DP link rates to SERDES codes, program lane count and enhanced framing, set training patterns, initialize voltage/pre-emphasis, read and interpret lane status, apply sink adjust requests, downgrade rate/lane count, and update caps from DPCD.

Control flow: training starts by reading DPCD caps, clamping link rate to at most `DP_LINK_BW_8_1` and lanes to `HIBMC_DP_LANE_NUM_MAX`, programming SERDES rate, then looping. Each loop performs CR preparation, clock recovery with up to 80 tries and five same-voltage retries, then channel equalization with five retries. Failed CR reduces rate first, then lane count; failed EQ prefers lane reduction after CR succeeded, then rate reduction. On hard error, the training pattern is disabled before returning.

State and persistence: updates `dp->link.cap.link_rate`, `dp->link.cap.lanes`, `dp->link.train_set`, and `dp->link.status.clock_recovered/channel_equalized`. These are in-memory link state and feed later mode validation and TU calculation. The sink state is mutated through AUX writes to `DP_LINK_BW_SET`, `DP_DOWNSPREAD_CTRL`, `DP_TRAINING_PATTERN_SET`, and lane training set registers.

Dependencies and integration points: depends on DRM DP helper routines for DPCD IO, training delays, lane status parsing, and adjust requests. It calls HIBMC SERDES programming functions and DP register-field helpers. It is invoked from `hibmc_dp_mode_set()` when a stream needs an equalized link.

Risks: `drm_dp_read_dpcd_caps()` errors are logged but not returned before caps update, so stale or zero DPCD contents can influence fallback behavior. Training can spin through multiple fallback attempts and is sensitive to AUX reliability. Training pattern disable errors are ignored in some paths. Lane/rate downgrade reaches `-EIO` at the minimum capability.

Test signals: verify DPCD capability parsing, CR and EQ success/failure paths, sink adjust-request propagation to SERDES, fallback from HBR3 to lower rates and from 2 lanes to 1 lane, and cleanup of training pattern on errors.
