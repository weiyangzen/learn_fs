# sources/distributed-fs/ceph-client/drivers/gpu/drm/panfrost/panfrost_devfreq.c

## Purpose
This file implements dynamic frequency scaling for Panfrost GPUs using devfreq, OPP tables, optional speed-bin filtering, thermal cooling registration, and busy/idle accounting from job execution.

## Important APIs, Types, and Functions
Important functions are `panfrost_devfreq_init`, `panfrost_devfreq_fini`, `panfrost_devfreq_resume`, `panfrost_devfreq_suspend`, `panfrost_devfreq_record_busy`, `panfrost_devfreq_record_idle`, `panfrost_devfreq_target`, and `panfrost_devfreq_get_dev_status`. The devfreq profile uses `DEVFREQ_GOV_SIMPLE_ONDEMAND`.

## Control Flow
Initialization skips unsupported multi-supply platforms, reads an optional `speed-bin` nvmem cell, configures OPP regulators and tables, sets the recommended initial OPP, records the fastest rate, initializes simple_ondemand thresholds, registers devfreq, and optionally registers a cooling device. Runtime status snapshots lock the counters, fold time since the last update into busy or idle buckets, publish total/busy time, and reset the interval. Job submission and completion call busy/idle recorders to maintain `busy_count`.

## State and Persistence Behavior
`struct panfrost_devfreq` stores current and fast frequencies, devfreq/cooling pointers, governor data, OPP table presence, time buckets, last update time, and busy count protected by a spinlock.

## Dependencies and Integration Points
It depends on the clock framework, OPP/dev_pm_opp, nvmem, devfreq, devfreq cooling, and Panfrost job paths that call the busy/idle hooks. fdinfo uses `current_frequency` and `fast_rate`.

## Risks
Busy-count imbalance produces wrong utilization and warns on negative idle transitions. Multi-supply platforms silently run without devfreq. Optional OPP and speed-bin failures have different severity; treating a required nvmem error as optional would choose unsafe OPPs. Debug logging divides by `total_time / 100`, which assumes nonzero elapsed time.

## Test Signals
Exercise OPP table parsing, speed-bin variants, thermal cooling registration, suspend/resume, concurrent jobs, busy/idle balance under reset and timeout paths, fdinfo frequencies, and governor frequency changes under GPU load.
