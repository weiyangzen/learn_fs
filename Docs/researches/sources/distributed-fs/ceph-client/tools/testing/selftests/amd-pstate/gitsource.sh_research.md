# sources/distributed-fs/ceph-client/tools/testing/selftests/amd-pstate/gitsource.sh

Purpose: AMD P-state performance/power benchmark using a Git source tree build/test workload across governors.

Important APIs/types/functions: inclusion guard `FILE_GITSOURCE`; globals for Git 2.15.1 archive and governors; CSV helpers; cleanup helpers; `install_gitsource()` downloads/extracts source; `run_gitsource()` starts AMD pstate tracer and runs `make test` under `perf stat` and `/usr/bin/time`; `parse_gitsource()`, `gather_gitsource()`, comparison helpers, `plot_png_gitsource()`, and `amd_pstate_gitsource()` orchestrate metrics.

Control flow: clears prior outputs, ensures source tree exists, writes CSV headers, backs up governors, loops over `ondemand` and `schedutil`, switches governors, runs workload `LOOP_TIMES`, parses desired performance/frequency/load/time/energy/performance-per-watt, plots PNGs, calculates comparisons, restores governors, and cleans transient logs.

State and persistence: downloads `git-2.15.1.tar.gz`, extracts `git-2.15.1`, writes CSV/result/log/PNG files, modifies cpufreq governors, and creates tracer result directories.

Dependencies/integration: sourced by `run.sh`; relies on `TRACER`, `PERF`, `MAKE_CPUS`, `CPUFREQROOT`, `bc`, `awk`, `gnuplot`, `wget`, `tar`, and benchmark/toolchain availability.

Risks and test signals: network dependency and large workload make it slow/flaky. Shell has typos such as "Comprison" and "Permance"; division by zero is possible if energy parsing fails. Governor restoration depends on backup log integrity.
