# sources/distributed-fs/ceph-client/drivers/gpu/drm/hisilicon/hibmc/dp/dp_serdes.c

Purpose: programs the DP SERDES physical layer for HIBMC link training and link-rate changes.

Important APIs/functions: `hibmc_dp_serdes_init()` sets the SERDES base, initializes both lane TX de-emphasis registers to level 0/pre-emphasis 0, and switches to the highest SERDES rate. `hibmc_dp_serdes_rate_switch()` writes the same rate to both lane rate registers and waits for lane status. `hibmc_dp_serdes_set_tx_cfg()` translates DP training-set voltage/pre-emphasis bits into per-lane de-emphasis values and writes PMA lane registers.

Control flow: link training calls rate switch before training loops and TX config whenever the sink requests new training settings. Each programming sequence waits 300 to 500 us, then requires `HIBMC_DP_LANE_STATUS_OFFSET` to equal `DP_SERDES_DONE`.

State and persistence: `dp->serdes_base` is derived from the DP base. Hardware lane PMA and rate registers retain their programmed values until subsequent writes or reset. There is no software cache other than the caller's `train_set`.

Dependencies and integration points: depends on DP register macros, DP training bit masks, `FIELD_GET/PREP`, and DRM debug logging. It is tightly coupled to `dp_link.c`.

Risks: the static `serdes_tx_cfg[4][4]` table is sparse and invalid voltage/pre-emphasis combinations return `-EINVAL`, which can stop training. The function loops over `HIBMC_DP_LANE_NUM_MAX` instead of active lane count, so both lanes are programmed even when training falls back to one lane. SERDES status equality check is strict.

Test signals: training at each voltage/pre-emphasis combination, one-lane fallback, rate changes across 1.62/2.7/5.4/8.1 classes, and injected lane status failures validate behavior.
