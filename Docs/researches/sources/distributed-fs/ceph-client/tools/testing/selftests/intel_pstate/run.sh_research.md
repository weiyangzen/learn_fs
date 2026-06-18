# sources/distributed-fs/ceph-client/tools/testing/selftests/intel_pstate/run.sh

Purpose: this shell script drives the Intel P-state selftest. It iterates maximum CPU frequency settings from max to min in 100 MHz steps, loads each CPU with `aperf`, captures observed frequencies and `MSR_IA32_PERF_CTL`, then prints a comparison table.

Important APIs, functions, and variables: `EVALUATE_ONLY` allows re-reading existing `/tmp/result.*` files. `ksft_skip=4` implements kselftest skip. `run_test()` launches `./aperf $cpu` for every CPU, sleeps, captures unique `/proc/cpuinfo` MHz lines, appends `./msr 0`, records `/sys/devices/system/cpu/intel_pstate/max_perf_pct`, and waits for jobs. Main code uses `cpupower frequency-info -l`, `cpupower frequency-set -g powersave --max=...`, `/proc/cpuinfo`, and `pr`.

Control flow: skip non-x86, non-root (unless evaluate-only), or missing `cpupower`. Compute marketing, min, and max frequencies. Unless evaluating only, loop over frequency targets and run load capture for each, then restore max. Finally build `/tmp/result.tab` with Target, Actual, Difference, MSR, and scaled max_perf_pct, and print it in five columns.

State and persistence: writes `/tmp/result.freqs`, `/tmp/result.<freq>`, and `/tmp/result.tab`; changes system CPU frequency policy during the run and attempts to restore max at the end. Background `aperf` processes run until completion.

Dependencies and integration points: requires x86, root, `cpupower`, intel_pstate sysfs, `/dev/cpu/*/msr`, `/proc/cpuinfo`, and helper binaries `aperf` and `msr`.

Risks: there is no trap to restore frequency on interruption; `/tmp/result.*` names are shared and can be stale or collide; parsing marketing frequency and cpuinfo MHz is fragile; multiple similar frequency lines can intentionally trigger manual cleanup; `max_cpus=$(nproc-1)` assumes contiguous CPU IDs from zero. The script exits 0 after table generation even if differences are large, so this is more diagnostic than assertive.

Test signals: skip messages for unsupported environments, captured result files per target frequency, and the final printed table. Meaningful failures include missing helpers/MSR access, cpupower errors, and suspicious Target/Actual differences in the table.
