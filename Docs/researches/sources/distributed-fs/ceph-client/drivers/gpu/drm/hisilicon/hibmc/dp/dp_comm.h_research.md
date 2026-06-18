
# sources/distributed-fs/ceph-client/drivers/gpu/drm/hisilicon/hibmc/dp/dp_comm.h

## Purpose
`dp_comm.h` defines common DisplayPort data structures, limits, register-field helpers, and cross-file function prototypes for the HIBMC DP implementation.

## Important APIs, Types, And Functions
The file defines `HIBMC_DP_LANE_NUM_MAX` as 2, `struct hibmc_link_status`, `struct hibmc_link_cap`, `struct hibmc_dp_link`, and `struct hibmc_dp_dev`. `struct hibmc_dp_dev` stores the `drm_dp_aux`, DRM device, MMIO base, register mutex, link-training state, DPCD buffer, downstream port buffer, DP descriptor, branch-device flag, HPD status, and serdes base.

Macros include `dp_field_modify(reg_value, mask, val)` and `hibmc_dp_reg_write_field(dp, offset, mask, val)`, the latter performing a mutex-protected read/modify/write using `FIELD_PREP`. Prototypes expose `hibmc_dp_aux_init()`, `hibmc_dp_link_training()`, `hibmc_dp_serdes_init()`, `hibmc_dp_serdes_rate_switch()`, and `hibmc_dp_serdes_set_tx_cfg()`.

## Control Flow
The header itself has no executable flow, but `hibmc_dp_reg_write_field()` expands into a locked read/modify/write sequence. DP implementation files use the shared structures to coordinate AUX initialization, link training, serdes setup, rate changes, and TX configuration.

## State And Persistence
`struct hibmc_dp_dev` is the persistent DP hardware context. It caches DPCD capabilities, downstream port information, link capabilities, training set values, HPD status, MMIO bases, and the AUX pointer. The mutex protects concurrent register-field updates through the macro.

## Dependencies And Integration Points
It depends on Linux bitfield, mutex, MMIO, errno, and type headers, plus DRM DP helper definitions and `dp_hw.h`. It is included by `dp_aux.c` and the other DP implementation files in the HIBMC driver.

## Risks
The register write macro evaluates the `dp` expression once but assumes a valid initialized mutex and MMIO base. It only protects accesses made through the macro; direct `readl()`/`writel()` sequences elsewhere must handle ordering and concurrency separately. Lane count is hard-limited to 2, so higher-lane hardware would require structural changes.

## Test Signals
Build coverage across all DP files, lockdep-clean concurrent register updates, successful two-lane and one-lane link training, correct DPCD cache population, and serdes rate/voltage/pre-emphasis changes reflected in hardware are the main validation signals.
