# sources/distributed-fs/ceph-client/drivers/cpufreq/mvebu-cpufreq.c

## Purpose

`mvebu-cpufreq.c` is a small Armada XP compatibility initializer. It adds nominal and half-rate OPPs for each present CPU and registers the generic `cpufreq-dt` platform device when the device tree has the newer Armada XP CPU clock binding that exposes PMU DFS registers.

## Important APIs, types, and functions

- `armada_xp_pmsu_cpufreq_init()` is the only function and runs as a `device_initcall()`.
- It uses `of_machine_is_compatible()`, `of_find_compatible_node()`, and `of_address_to_resource()` to validate the CPU clock binding.
- It uses `clk_get()`, `clk_get_rate()`, `dev_pm_opp_add()`, and `dev_pm_opp_set_sharing_cpus()` to register per-CPU OPPs.
- It ends by creating `platform_device_register_simple("cpufreq-dt", ...)`.

## Control flow

On Armada XP only, the initializer finds the `"marvell,armada-xp-cpu-clock"` node and requires resource index 1 to exist. That resource check filters out old device trees whose CPU clock binding lacks PMU DFS registers. It then iterates present CPUs, gets each CPU clock, adds the full clock rate and half clock rate as OPPs, marks OPP sharing as per-CPU, releases the clock, and finally instantiates `cpufreq-dt`.

## State and persistence behavior

The file owns no private runtime state. OPPs are added to CPU device OPP tables and persist for the kernel lifetime. The created `cpufreq-dt` platform device persists; there is no removal path because this is built as an init helper.

## Dependencies

Dependencies include Armada XP machine compatibility, a CPU clock provider with PMU DFS register resource, CPU devices, common clock framework, OPP library, and the generic `cpufreq-dt` driver. It relies on another clock notifier path to perform the PMSU hardware portion of transitions.

## Risks and edge cases

- On old device trees the driver quietly returns after a firmware warning, so cpufreq is unavailable.
- If adding the second OPP fails, it removes the first OPP for that CPU but leaves OPPs already added for earlier CPUs.
- `dev_pm_opp_set_sharing_cpus()` errors are logged but not fatal.
- Only nominal and half-rate states are exposed; hardware or board-specific additional states are not represented.

## Test signals

Boot on Armada XP should register two OPPs per CPU and create a `cpufreq-dt` device only when the CPU clock binding has the PMU DFS resource. Runtime validation should switch between full and half rates, confirm PMSU notifier execution, and test old-DT fallback logs.
