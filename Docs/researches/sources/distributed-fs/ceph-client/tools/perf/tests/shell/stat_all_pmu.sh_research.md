## sources/distributed-fs/ceph-client/tools/perf/tests/shell/stat_all_pmu.sh

Purpose: exclusive broad test for all non-parameterized PMU events from `perf list --raw-dump pmu`.
Important behavior: removes parameterized event patterns containing `?`, runs `perf stat -e "$p" true`, accepts supported, not-supported, permission-limited, and access-limited outcomes, and retries missing output with a longer synthesize benchmark.
Control flow: traps print the last result on unexpected signal; loops every PMU event and accumulates `err`.
State and persistence: no temp files, only shell `result`/`output`.
Dependencies and integration: PMU sysfs metadata, perf list/stat, and benchmark fallback.
Risks: can be slow/noisy on systems with many PMUs; parser/output changes around unsupported events affect classification.
Test signals: every event either appears, is unsupported/permission-limited, or causes a failure.
