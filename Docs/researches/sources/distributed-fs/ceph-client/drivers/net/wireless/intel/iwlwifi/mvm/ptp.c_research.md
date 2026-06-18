<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mvm/ptp.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mvm/ptp.c

## Purpose
Registers an iwlwifi PTP hardware clock (PHC) backed by the device GP2 timer, translates/wraps/scales GP2 timestamps into adjusted nanoseconds, supports frequency/time adjustment, and provides system-device cross timestamps either through firmware synced-time command or host loop sampling.

## Important APIs, Types, And Functions
Public APIs are `iwl_mvm_ptp_init`, `iwl_mvm_ptp_remove`, and `iwl_mvm_ptp_get_adj_time`. PTP callbacks are `iwl_mvm_phc_get_crosstimestamp`, `iwl_mvm_ptp_gettime`, `iwl_mvm_ptp_settime`, `iwl_mvm_ptp_adjtime`, and `iwl_mvm_ptp_adjfine`. Static helpers include `iwl_mvm_ptp_update_new_read`, `iwl_mvm_get_crosstimestamp_fw`, `iwl_mvm_phc_get_crosstimestamp_loop`, and delayed `iwl_mvm_ptp_work`.

## Control Flow
Initialization fills `ptp_clock_info`, sets callback pointers, initializes scaled frequency to `SCALE_FACTOR`, names the clock, initializes delayed wrap-tracking work, and registers the PHC. Reads take `mvm->mutex`, read GP2 from firmware/hardware, call `iwl_mvm_ptp_get_adj_time`, and return nanoseconds as a timespec or cross timestamp. Cross timestamping uses firmware `WNM_PLATFORM_PTM_REQUEST_CMD` when synced-time capability exists; otherwise it samples host sync time five times and chooses the smallest system-vs-GP2 delta. `adjtime` accumulates delta. `adjfine` snapshots current adjusted time before changing scale, resets wrap/delta origin, and applies the scaled ppm offset. Periodic delayed work reads GP2 before expected wrap to keep wrap tracking current.

## State And Persistence
Uses `mvm->ptp_data`: registered clock pointer, clock info, delayed work, `last_gp2`, `wrap_counter`, scale update GP2/time, `scaled_freq`, and `delta`. State is runtime-only and reset on remove. Firmware GP2 is a 32-bit microsecond counter, so wrap accounting is essential for continuity.

## Dependencies And Integration Points
Depends on Linux PTP clock framework, timekeeping, math64 helpers, `iwl_mvm_get_systime`, `iwl_mvm_get_sync_time`, firmware synced-time capability, `iwl_mvm_send_cmd`, and lifecycle hooks from `ops.c` (`iwl_mvm_ptp_remove` during stop). Consumers may request RX timestamps in PTP clock time through `mvm->rx_ts_ptp`.

## Risks And Edge Cases
Old GP2 reads can look like wraparound; the 5 ms threshold filters small backwards reads. Missing periodic work around the one-hour wrap can break monotonic conversion. `iwl_mvm_get_crosstimestamp_fw` does not free the response on the success path in the code as read, which is a leak risk unless ownership is handled elsewhere. `settime` is unsupported. Frequency adjustment resets delta and wrap origin, so callers expecting independent phase/frequency control need coverage.

## Test Signals
Verify PHC registration/unregistration, unavailable PTP module behavior, gettime monotonicity across GP2 wrap, old-read filtering, adjtime delta accumulation, adjfine scaling before and after reads, firmware synced-time and fallback loop cross timestamps, invalid firmware response length, delayed work cancellation on remove, and repeated init/remove without stale clock state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mvm/ptp.c -->
