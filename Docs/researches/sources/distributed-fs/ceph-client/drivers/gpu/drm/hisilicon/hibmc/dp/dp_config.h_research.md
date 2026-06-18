
# sources/distributed-fs/ceph-client/drivers/gpu/drm/hisilicon/hibmc/dp/dp_config.h

## Purpose
`dp_config.h` centralizes fixed HIBMC DisplayPort configuration constants used by the DP hardware, link, and mode-validation code.

## Important APIs, Types, And Functions
The file defines constants for bits per pixel (`HIBMC_DP_BPP`), symbols per fclk, MSA register defaults, DP register offset, HDCP selector, interrupt/reset masks, clock enable mask, sync enable mask, link-rate calculation factor, sync delay based on lane count, interrupt enable mask, and `DP_MODE_VALI_CAL`.

## Control Flow
There is no executable flow. The only expression-like macro is `HIBMC_DP_SYNC_DELAY(lanes)`, which selects a delay value of 86 for two lanes and 46 otherwise.

## State And Persistence
The file owns no state. The constants are written into or compared against DP hardware configuration by other HIBMC DP files.

## Dependencies And Integration Points
It is part of the HIBMC DP support set and complements `dp_comm.h`, `dp_reg.h`, `dp_hw.c`, `dp_link.c`, and `hibmc_drm_dp.c`. The mode-validation calculation constant is tied to a comment that `HIBMC_DP_LINK_RATE_CAL * 10000 * 80% = 216000`.

## Risks
Hard-coded constants imply a specific HIBMC DP hardware profile: 24 bpp, maximum two-lane behavior, fixed masks, and fixed validation margin. New hardware revisions or different lane rates may require updates. `HIBMC_DP_SYNC_DELAY(lanes)` treats every non-2 lane count the same.

## Test Signals
Validate DP modes at expected bandwidth limits, one-lane and two-lane sync timing, reset/clock/interrupt bring-up, MSA programming, and regression tests for mode validation around the `DP_MODE_VALI_CAL` threshold.
