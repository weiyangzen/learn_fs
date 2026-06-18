# sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb-v2/mxl111sf-tuner.c

Purpose: DVB tuner implementation for the MxL111SF CMOS tuner block. It provides tuner ops for RF tuning across DVB-T, ATSC, ATSC-MH, and US cable modes, tracks tuned frequency/bandwidth, reports lock/RF power, and exposes IF frequency selection.

Important APIs/types/functions: `struct mxl111sf_tuner_state` stores shared chip state, config callbacks, IF enum, cached frequency, and bandwidth. `mxl111sf_calc_phy_tune_regs()` computes bandwidth and RF channel register values. `mxl1x1sf_tune_rf()` stops tuning, checks device mode, programs RF registers, optionally toggles top master and IF output, starts tuning, and runs `ant_hunt`. `mxl111sf_tuner_set_params()`, `mxl111sf_tuner_get_status()`, `mxl111sf_get_rf_strength()`, and getter/release functions populate `dvb_tuner_ops`. `mxl111sf_tuner_attach()` is exported.

Control flow: the main bridge attaches this tuner to each created frontend after demod attachment. Tune requests select a bandwidth code by delivery system, call RF tune, and cache the selected frequency/bandwidth. In tuner mode, IF output frequency is configured before `START_TUNE_REG` is asserted. RF strength temporarily switches to register page 2, reads digital RF power LSB/MSB, and restores page 0.

State and persistence: per-frontend tuner state is allocated and freed by tuner ops release. Hardware tune state persists in RF tune registers, IF selection/bypass registers, start-tune bit, page register, and top-master state. Cached frequency/bandwidth are software-only and are returned by getter ops.

Dependencies and integration: depends on shared MxL111SF register callbacks, PHY `top_master_ctrl`, and optional antenna hunt callback supplied by `mxl111sf.c`. It integrates with DVB frontend tuning via `fe->ops.tuner_ops`.

Risks: `mxl_phy_tune_rf` is a static mutable register array shared across all tuner instances, so concurrent tunes could race if multiple frontends tune simultaneously. Unsupported bandwidth or delivery system returns `-EINVAL`. RF strength page restoration happens even after errors, but the final restore result overwrites the earlier error. IF frequency calculations are mostly disabled and use hard-coded bypass values.

Test signals: attach tuner to all frontends; tune ATSC, ATSC-MH, DVB-C Annex B, and DVB-T 6/7/8 MHz paths; validate RF lock bits; confirm RF strength reads restore page 0; exercise antenna hunting; concurrent multi-frontend tune testing on multi-profile devices.
