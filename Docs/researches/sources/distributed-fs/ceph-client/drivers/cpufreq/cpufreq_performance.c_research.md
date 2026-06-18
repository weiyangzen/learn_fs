# sources/distributed-fs/ceph-client/drivers/cpufreq/cpufreq_performance.c

Purpose: implements the simple `performance` governor, which drives each policy to its maximum allowed frequency whenever limits are applied.

Important APIs and control flow: `cpufreq_gov_performance_limits()` calls `__cpufreq_driver_target(policy, policy->max, CPUFREQ_RELATION_H)`. The static governor advertises name `performance`, module ownership, strict-target semantics, and the limits callback. It can provide `cpufreq_default_governor()` under `CONFIG_CPU_FREQ_DEFAULT_GOV_PERFORMANCE` and `cpufreq_fallback_governor()` for built-in non-module configurations.

State and persistence behavior: no governor-private state is allocated. Runtime behavior is entirely determined by current policy max and cpufreq core/driver state.

Dependencies and integration points: depends on cpufreq core governor registration macros and target-style drivers. The fallback hook integrates with `cpufreq.c` when dynamic switching governors are disallowed by a driver.

Risks and test signals: risks are mostly integration-related: strict-target max requests may expose driver table/limit bugs, and fallback availability depends on build configuration. Test signals include governor registration, selecting `performance` through sysfs, max-frequency target on min/max limit changes, default-governor selection when configured, and fallback use with `CPUFREQ_NO_AUTO_DYNAMIC_SWITCHING`.
