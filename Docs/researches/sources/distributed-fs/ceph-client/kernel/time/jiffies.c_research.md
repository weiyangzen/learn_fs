# sources/distributed-fs/ceph-client/kernel/time/jiffies.c

Purpose: provides the baseline jiffies clocksource, 64-bit jiffies accessor on 32-bit systems, optional refined-jiffies registration, and sysctl conversion handlers between user units and kernel jiffies.

Important APIs and flow: `clocksource_jiffies` reads global `jiffies`, has minimal rating, coarse `TICK_NSEC` conversion, and registers at `core_initcall`. `clocksource_default_clock()` weakly returns it as the fallback default. `register_refined_jiffies()` clones and slightly increases the rating after computing a more accurate multiplier from cycles-per-second. Sysctl helpers route `proc_dointvec_*_jiffies` and `proc_doulongvec_ms_jiffies_minmax()` through generic proc conversion callbacks.

State and persistence: exports `jiffies`, `jiffies_lock`, and `jiffies_seq`. On 32-bit, `get_jiffies_64()` reads `jiffies_64` with seqcount retry. Registered clocksources persist globally for timekeeping selection.

Dependencies and integration: clocksource core, timekeeping/tick internals, proc sysctl, jiffies conversion helpers, and initcall ordering. It is intentionally the lowest common denominator for platforms without better counters.

Risks and test signals: risks are coarse resolution, lost tick inaccuracy, poor tickless suitability, and unit conversion overflow/minmax behavior. Test by forcing fallback clocksource, validating 32-bit seqcount read consistency, refined-jiffies multiplier calculation, sysctl read/write conversions in seconds/USER_HZ/milliseconds, and no-proc-sysctl `-ENOSYS` stubs.
