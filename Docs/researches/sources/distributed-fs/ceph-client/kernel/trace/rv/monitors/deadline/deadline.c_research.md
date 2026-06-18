# sources/distributed-fs/ceph-client/kernel/trace/rv/monitors/deadline/deadline.c

## Purpose
`deadline.c` registers a Runtime Verification monitor container named `deadline`. It groups deadline scheduler specifications and exposes shared state used by other deadline-related monitors.

## Important APIs, types, and functions
The key object is `struct rv_monitor rv_deadline`, with name `deadline`, a descriptive string, no custom enable/disable/reset callbacks, and initial `enabled = 0`. The file also defines `struct sched_class *rv_ext_sched_class` for use by other monitors. Lifecycle functions are `register_deadline()` and `unregister_deadline()`.

## Control flow
On module init, `register_deadline()` checks `CONFIG_SCHED_CLASS_EXT`; when enabled it resolves `ext_sched_class` with `kallsyms_lookup_name()` and warns if absent. It then registers the monitor with `rv_register_monitor(&rv_deadline, NULL)`. Module exit unregisters it with `rv_unregister_monitor()`.

## State and persistence
Runtime state is the registered RV monitor object and the optional cached pointer to `ext_sched_class`. There is no persistent storage, and the monitor has no internal enable or reset state beyond the RV core's handling of `rv_monitor.enabled`.

## Dependencies and integration points
It depends on the RV core, module init/exit infrastructure, kallsyms, scheduler class declarations from `deadline.h`, and optionally the sched_ext class symbol. Other deadline monitors can use `rv_ext_sched_class` to recognize external scheduler-class interactions.

## Risks and test signals
Risks include `kallsyms_lookup_name()` returning NULL when sched_ext is expected, the container registering successfully even though dependent monitors may lack ext scheduler awareness, and no enable/disable callbacks for container-specific validation. Test signals include successful RV monitor registration, warning behavior with `CONFIG_SCHED_CLASS_EXT` but missing `ext_sched_class`, clean unregister on module unload, and downstream deadline monitors finding `rv_ext_sched_class` when sched_ext is present.
