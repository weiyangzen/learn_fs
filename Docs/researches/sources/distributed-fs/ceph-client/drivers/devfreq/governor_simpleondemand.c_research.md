<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/devfreq/governor_simpleondemand.c -->
# sources/distributed-fs/ceph-client/drivers/devfreq/governor_simpleondemand.c

Purpose: implements the common polling governor that scales frequency from device busy/total time samples.

Important APIs and control flow: `devfreq_simple_ondemand_func()` calls `devfreq_update_stats()`, reads `df->last_status`, applies default or driver-provided thresholds (`upthreshold`, `downdifferential`), requests max frequency when total time is zero, when busy exceeds the up-threshold, or when current frequency is unknown, keeps current frequency in the hysteresis band, otherwise computes a proportional target from busy ratio and current frequency. `devfreq_simple_ondemand_handler()` starts/stops/suspends/resumes devfreq monitoring and applies interval updates through core helper functions.

State and persistence behavior: no private allocation. Per-device tuning is read from `struct devfreq_simple_ondemand_data` passed as `df->data`; polling state is owned by the devfreq core.

Dependencies and integration points: depends on profile `get_dev_status`, devfreq monitor helpers, and optional sysfs governor attrs `polling_interval` and `timer`. Used by Exynos bus, RK3399 DMC, Allwinner MBUS, and as a generic fallback for many other drivers.

Risks and test signals: threshold validation rejects `upthreshold > 100` or `upthreshold < downdifferential`, but a zero effective denominator can still occur if both are badly chosen around integer precedence in the target calculation. Busy/total values are shifted down only when either exceeds 24 bits, which changes precision. Test signals include zero-total max behavior, hysteresis band behavior, proportional downscaling, custom threshold rejection, polling interval zero/nonzero transitions, suspend/resume monitor state, and overflow-prone large counter samples.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/devfreq/governor_simpleondemand.c -->
