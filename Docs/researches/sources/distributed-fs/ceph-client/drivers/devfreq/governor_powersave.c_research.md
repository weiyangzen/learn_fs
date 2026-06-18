<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/devfreq/governor_powersave.c -->
# sources/distributed-fs/ceph-client/drivers/devfreq/governor_powersave.c

Purpose: registers the standard `powersave` governor, which always requests the minimum available frequency.

Important APIs and control flow: `devfreq_powersave_func()` returns `DEVFREQ_MIN_FREQ`; the core clamps this to the current min frequency. `devfreq_powersave_handler()` forces an immediate update on governor start. Module init and exit add/remove the governor.

State and persistence behavior: no per-device state; only the static governor object persists while loaded.

Dependencies and integration points: depends on devfreq core/governor API and the device profile target callback selected by the consumer driver.

Risks and test signals: like performance, it is event-minimal and relies on core QoS/OPP notifier paths for later constraint changes. Test signals include initial transition to minimum, PM QoS min raising the actual target, OPP availability updates, sysfs governor switching, and clean module unload when unused.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/devfreq/governor_powersave.c -->
