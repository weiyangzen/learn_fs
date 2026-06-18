<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/devfreq/governor_performance.c -->
# sources/distributed-fs/ceph-client/drivers/devfreq/governor_performance.c

Purpose: registers the standard `performance` governor, which always requests the maximum available frequency.

Important APIs and control flow: `devfreq_performance_func()` returns `DEVFREQ_MAX_FREQ`; the core clamps this to the current max frequency and passes least-upper-bound/floor behavior to the profile target. `devfreq_performance_handler()` performs one immediate `update_devfreq()` on `DEVFREQ_GOV_START`. Module init/exit add and remove the governor.

State and persistence behavior: only global state is the static governor object. No per-device governor data is allocated.

Dependencies and integration points: depends on devfreq core and governor API. It is used by drivers that want deterministic maximum performance, including HiSilicon uncore when not platform-controlled.

Risks and test signals: it does not react to suspend/resume/update-interval events itself, so updates after QoS/OPP changes rely on core notifiers. Test signals include initial max-frequency transition, PM QoS max limiting the result, OPP table changes triggering core updates, and successful governor removal when no devices use it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/devfreq/governor_performance.c -->
