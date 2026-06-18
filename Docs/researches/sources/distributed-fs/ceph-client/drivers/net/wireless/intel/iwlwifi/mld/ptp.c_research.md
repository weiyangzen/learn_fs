# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/ptp.c

Purpose: provides a PTP hardware clock for the MLD device using the firmware/hardware GP2 timer, including adjusted time calculation, frequency/delta adjustments, wraparound tracking, cross-timestamp support, registration, and teardown.

Important APIs/functions: `iwl_mld_ptp_get_adj_time()`, `iwl_mld_ptp_init()`, and `iwl_mld_ptp_remove()` are exported. Static PTP callbacks implement gettime, unsupported settime, adjtime, adjfine, delayed wrap-check work, firmware cross timestamp read, and PHC cross timestamp conversion.

Control flow: gettime reads GP2, locks `ptp_data.lock`, converts GP2 microseconds to adjusted nanoseconds, and returns `timespec64`. adjtime accumulates `delta`. adjfine first snapshots adjusted time under the old scale, stores the new GP2 anchor, clears delta/wrap counter, and updates scaled frequency. A delayed work runs hourly to observe GP2 and detect wraps. Cross timestamp sends a firmware PTM read-both command under wiphy lock, validates response size, converts GP2 10 ns units to microseconds, then adjusts it through the same time-scale logic.

State and persistence: `struct ptp_data` holds `ptp_clock`, callback info, spinlock, delta, scale anchor GP2/adjusted ns, scaled frequency, last GP2, wrap counter, and delayed work. State is in memory and reset on removal.

Dependencies and integration: depends on Linux PTP clock APIs, timekeeping, direct PRPH GP2 register reads, firmware `WNM_PLATFORM_PTM_REQUEST_CMD`, host-command wrappers, and debug logging. `rx.c` can use `iwl_mld_ptp_get_adj_time()` for monitor-mode radiotap timestamps.

Risks and test signals: wrap detection distinguishes old reads from real wraps using a 5000 usec threshold; wrong thresholding affects long-running PHC accuracy. `settime` is intentionally unsupported. Tests should cover invalid GP2 sentinel, adjfine anchoring, wrap counter behavior, delayed work cancellation after unregister, response-size validation, and concurrent RX timestamp adjustment under the spinlock.
