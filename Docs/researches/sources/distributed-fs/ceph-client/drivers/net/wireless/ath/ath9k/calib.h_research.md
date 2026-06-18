# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/calib.h

Purpose: Declares ath9k calibration data structures, INI table helpers, calibration list macros, NF history limits, PA calibration state, and common calibration entry points.

Important APIs/types: `struct ar5416IniArray` wraps register initialization tables with rows/columns and access macros. `INIT_CAL()` and `INSERT_CAL()` build a circular list of `struct ath9k_cal_list`. `enum ath9k_cal_state` defines inactive, waiting, running, and done states. `struct ath9k_percal_data` supplies hardware calibration callbacks and sample counts. `struct ath9k_nfcal_hist` stores five NF readings, current index, private median NF, and invalid warmup count. `struct ath9k_pacal_info` tracks PA calibration offset and skip counters.

Control flow: Hardware-specific init code declares per-calibration objects, initializes them with these macros, starts/reset calibrations through `ath9k_hw_reset_calibration()`, and manages NF through the exported functions implemented in `calib.c`.

State/persistence: The header defines persistent per-device/per-channel calibration containers but does not allocate them. NF history length, invalid warmup length, min/max sample constants, and PA skip limits are compile-time behavioral constants.

Dependencies/integration: Includes `hw.h` and is used by hardware calibration, reset, debugfs NF dumps, and channel change paths.

Risks: The circular list macro assumes callers initialize `cal_list_last` correctly. INI macros cast table storage to `u32 *` and rely on rectangular arrays. `NUM_NF_READINGS` is six, representing control and extension chains, so callers must gate extension readings on HT40.

Test signals: Compile coverage for all hardware families, calibration list insertion order, NF history initialization, NF dump formatting, and channel-width-specific NF register access.
