# sources/distributed-fs/ceph-client/drivers/ptp/ptp_mock.c

Purpose: provides an exported helper for virtual network devices to create a mock PTP hardware clock backed by `CLOCK_MONOTONIC_RAW`. It behaves like an adjustable PHC without hardware, useful for tests and virtual drivers that need a PHC index.

Important APIs/types/functions: `struct mock_phc` stores `ptp_clock_info`, registered clock, `timecounter`, `cyclecounter`, and a spinlock. `mock_phc_create()` allocates the object, initializes a cyclecounter whose `read` returns `ktime_get_raw_ns()`, registers the PTP clock, and schedules periodic worker refresh. `mock_phc_destroy()` unregisters and frees it. `mock_phc_index()` returns `ptp_clock_index()`. Clock operations include `mock_phc_adjfine()`, `mock_phc_adjtime()`, `mock_phc_settime64()`, `mock_phc_gettime64()`, and `mock_phc_refresh()`.

Control flow: callers create a mock PHC with a parent device. Reads call `timecounter_read()` under lock. Frequency adjustments first read the counter to preserve continuity, then update `cc.mult` using the scaled-ppm conversion. Time adjustments use `timecounter_adjtime()`, and settime reinitializes the timecounter origin. The aux worker periodically reads the clock so the timecounter is refreshed before overflow-sensitive deltas become too large.

State and persistence: time and frequency offset exist only in the in-memory timecounter/cyclecounter. No settings persist after destroy or reboot. The spinlock serializes all timecounter and multiplier changes.

Dependencies and integration: exports GPL symbols through `linux/ptp_mock.h`, uses the PTP class, `linux/timecounter.h`, and raw monotonic kernel time. It is intended as a library-style module rather than an enumerated platform or PCI driver.

Risks and test signals: the refresh interval is chosen to avoid 64-bit multiplication overflow in `timecounter_read_delta()` under the maximum allowed frequency adjustment; changing max adjustment, shift, or refresh interval must be reviewed together. Test by creating/destroying from a virtual net driver, reading `/dev/ptpN`, applying positive and negative `adjfine`, settime/adjtime continuity, and ensuring worker scheduling stops at unregister.
