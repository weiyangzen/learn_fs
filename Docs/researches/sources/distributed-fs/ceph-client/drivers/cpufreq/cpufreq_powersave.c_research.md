# sources/distributed-fs/ceph-client/drivers/cpufreq/cpufreq_powersave.c

Purpose: implements the simple `powersave` governor, which drives each policy to its minimum allowed frequency whenever limits are applied.

Important APIs and control flow: `cpufreq_gov_powersave_limits()` calls `__cpufreq_driver_target(policy, policy->min, CPUFREQ_RELATION_L)`. The static governor advertises name `powersave`, module ownership, strict-target semantics, and a limits callback. It can provide `cpufreq_default_governor()` under `CONFIG_CPU_FREQ_DEFAULT_GOV_POWERSAVE`.

State and persistence behavior: no governor-private state is allocated. The target frequency is derived from current policy min at each limits callback.

Dependencies and integration points: depends on cpufreq core governor registration macros and target-style drivers. It appears in `scaling_available_governors` like other registered governors and can be selected by user space or default configuration.

Risks and test signals: risks include performance regressions if selected unexpectedly, strict-target min requests exposing incorrect policy min verification, and no support for drivers that only expose `setpolicy` beyond the cpufreq core's built-in policy names. Test signals include governor registration, sysfs selection, min-frequency target after policy limit changes, default-governor selection when configured, and stable unload/reload when built as a module.
