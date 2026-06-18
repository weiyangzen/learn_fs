# sources/distributed-fs/ceph-client/drivers/net/ethernet/amd/xgbe/xgbe-pps.c

## Purpose
`xgbe-pps.c` configures MAC Pulse Per Second/per-out outputs for the PTP clock. It programs start time, interval, pulse width, command, and target mode registers for a selected PPS output.

## Important APIs, Types, And Functions
- `get_pps_mask`, `get_pps_cmd`, and `get_target_mode_sel` compute per-output bitfields in `MAC_PPSCR`.
- `xgbe_pps_config` is the exported configuration routine used by `xgbe-ptp.c` for `PTP_CLK_REQ_PEROUT`.

## Control Flow
`xgbe_enable` in `xgbe-ptp.c` copies a PTP perout request into `pdata->pps[index]`, takes `tstamp_lock`, and calls `xgbe_pps_config`. The PPS routine checks whether the target time register is busy. For disable, it writes a stop command. For enable, it writes target start seconds/nanoseconds, converts requested period to hardware units using `XGBE_V2_TSTAMP_SSINC`, validates a minimum period, writes interval and 50 percent duty-cycle width, then writes a start pulse-train command.

## State And Persistence
Configuration values are cached in `pdata->pps[index]` by the caller and programmed into MAC PPS registers. State is runtime and tied to the PHC/netdev lifetime.

## Dependencies And Integration Points
This file depends on MAC PPS register definitions from `xgbe-common.h`, timestamp increment constants from `xgbe.h`, and PTP request plumbing in `xgbe-ptp.c`. Locking is provided by the caller.

## Risks
The conversion always uses `XGBE_V2_TSTAMP_SSINC`; this assumes the PPS hardware mode matches that increment. The caller must validate `index` against `ptp_clock_info.n_per_out`; this function itself does not bounds-check. Busy target registers return `-EBUSY`, and too-small periods return `-EINVAL`. Duty cycle is fixed at 50 percent.

## Test Signals
Use `testptp` or equivalent PHC perout tooling to enable/disable outputs at supported indices and periods. Check `-EBUSY` handling, minimum period validation, output frequency/duty cycle on hardware, and behavior after PHC or netdev restart.
