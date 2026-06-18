<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/sh-cpufreq.c -->
# sources/distributed-fs/ceph-client/drivers/cpufreq/sh-cpufreq.c

## Purpose

Provides generic SuperH cpufreq support using per-CPU clock framework objects, either with a clock-provided frequency table or rate rounding.

## APIs, Types, And Functions

Per-CPU `sh_cpuclk` stores CPU clock handles. `struct cpufreq_target` packages a policy and requested frequency for `work_on_cpu()`. `sh_cpufreq_get()`, `sh_cpufreq_target()`, `sh_cpufreq_verify()`, `sh_cpufreq_cpu_init()`, and `sh_cpufreq_cpu_exit()` implement the driver.

## Control Flow

Module init registers the driver. CPU init gets `"cpu_clk"` from the CPU device, installs its frequency table if present or derives min/max from `clk_round_rate()`. Targeting runs on the policy CPU, rounds the requested kHz to a supported Hz rate, verifies limits, emits cpufreq transition begin/end notifications, and calls `clk_set_rate()`.

## State And Persistence

The per-CPU clock reference is the main state. Hardware clock state persists in the SuperH clock framework. Exit releases the per-CPU clock.

## Dependencies And Integration Points

Depends on SuperH clock framework internals (`struct clk` frequency tables), CPU devices, `work_on_cpu()`, and cpufreq transition notification APIs.

## Risks And Test Signals

The target callback uses old-style `.target` rather than `.target_index` and disables automatic dynamic switching. `clk_set_rate()` return value is not propagated through transition end. Test signals include fallback min/max rounding, transition notifications, CPU-affine execution, and clock rate readback through `get`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/sh-cpufreq.c -->
