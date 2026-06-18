<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/lima/lima_devfreq.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/lima/lima_devfreq.c

## Purpose
Implements optional devfreq and thermal cooling support for Lima GPU clock scaling using OPP tables and busy/idle accounting.

## Important APIs, types, and functions
Public functions are `lima_devfreq_init()`, `lima_devfreq_fini()`, `lima_devfreq_record_busy()`, `lima_devfreq_record_idle()`, `lima_devfreq_resume()`, and `lima_devfreq_suspend()`. Internal helpers are `lima_devfreq_update_utilization()`, `lima_devfreq_target()`, `lima_devfreq_reset()`, and `lima_devfreq_get_dev_status()`.

## Control flow
Init exits quietly when no `operating-points-v2` property exists. Otherwise it sets the `core` clock name, optional `mali` regulator, loads OPPs, chooses an initial frequency, configures simple_ondemand thresholds, registers devfreq, and optionally registers cooling. Busy/idle calls update utilization under a spinlock and maintain a busy counter. Devfreq polling reads current GPU rate, rolls elapsed time into busy or idle buckets, returns status, and resets counters. Suspend/resume wrap the devfreq device and reset accounting on resume.

## State and persistence
`struct lima_devfreq` stores devfreq and cooling handles, governor data, busy/idle ktime counters, last update time, busy count, and spinlock. State persists for the device lifetime after init.

## Dependencies and integration points
Uses the clk, devfreq, OPP, thermal cooling, property, and regulator frameworks. Scheduler power-management paths record busy/idle transitions while tasks run.

## Risks
Busy count underflow is only `WARN_ON`, so mismatched record calls can corrupt utilization. Debug percentage divides by `total_time / 100`, which can be zero for tiny intervals. Optional regulator handling must align with OPP voltage requirements.

## Test signals
Validate devices with and without OPP tables, frequency transitions under render load, cooling device registration, suspend/resume accounting reset, and balanced busy/idle calls during GP/PP jobs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/lima/lima_devfreq.c -->
