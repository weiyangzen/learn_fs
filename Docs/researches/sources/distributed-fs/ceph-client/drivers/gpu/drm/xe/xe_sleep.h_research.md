<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sleep.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sleep.h

Purpose: provides common sleep helpers with relaxed millisecond timing and exponential backoff.

Important APIs: `xe_sleep_relaxed_ms()` uses `msleep()` for delays over 20 ms and `usleep_range()` with 0.5 ms slack for shorter delays. `xe_sleep_exponential_ms()` sleeps for the current period, doubles it up to a maximum, and returns the actual requested delay.

Risks and test signals: callers must initialize `*sleep_period_ms` to a nonzero value or the first sleep is skipped and remains zero. Tests should cover zero, sub-20 ms, over-20 ms, and capped exponential growth.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sleep.h -->
