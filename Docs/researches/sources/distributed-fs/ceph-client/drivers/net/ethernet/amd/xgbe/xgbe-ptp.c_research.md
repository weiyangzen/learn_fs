# sources/distributed-fs/ceph-client/drivers/net/ethernet/amd/xgbe/xgbe-ptp.c

## Purpose
`xgbe-ptp.c` registers and implements the Linux PTP hardware clock interface for AMD XGBE. It provides PHC frequency adjustment, time adjustment, time get/set, and per-output PPS enablement.

## Important APIs, Types, And Functions
- `xgbe_adjfine` adjusts the timestamp addend using `adjust_by_scaled_ppm`.
- `xgbe_adjtime` applies positive or negative time deltas through timestamp update registers.
- `xgbe_gettimex` reads the hardware time with system timestamp bracketing.
- `xgbe_settime` initializes the hardware time.
- `xgbe_enable` handles `PTP_CLK_REQ_PEROUT` by calling `xgbe_pps_config`.
- `xgbe_ptp_register` fills `struct ptp_clock_info`, registers the PHC, disables timestamping by default, and initializes hwtstamp config to off.
- `xgbe_ptp_unregister` unregisters the PHC.

## Control Flow
`xgbe_config_netdev` calls `xgbe_ptp_register` when PTP support is reachable. PTP core operations call the registered callbacks, which recover `pdata` from the embedded `ptp_clock_info`, take `tstamp_lock` for register operations, and delegate low-level timestamp programming to `xgbe-hwtstamp.c`. Perout requests are copied into `pdata->pps[index]` and applied through `xgbe_pps_config`.

## State And Persistence
PTP state lives in `pdata->ptp_clock_info`, `pdata->ptp_clock`, `pdata->tstamp_addend`, `pdata->tstamp_config`, and `pdata->pps[]`. Hardware time and addend live in MAC registers. `tstamp_lock` serializes PHC operations with timestamp code.

## Dependencies And Integration Points
This file depends on Linux PTP clock APIs, timestamp helpers from `xgbe-hwtstamp.c`, PPS programming from `xgbe-pps.c`, and hardware feature counts for `n_per_out` and `n_ext_ts`. ethtool timestamp reporting references the registered PHC index.

## Risks
Perout indexing is taken from the PTP request; correctness depends on PTP core bounds relative to `n_per_out`. Negative `adjtime` handling writes sign and adjusted nanoseconds in MAC-specific format and must match `TSCTRLSSR`. `max_adj` is set to `ptpclk_rate`, so incorrect clock discovery affects user-visible adjustment limits. Unregister does not clear `pdata->ptp_clock` after unregistering.

## Test Signals
Use `ptp4l`, `phc2sys`, `phc_ctl`, and `testptp` to validate get/set, fine adjustment, negative and positive adjustments, PHC index reporting via `ethtool -T`, and PPS perout behavior. Re-test after interface restart and driver unload.
