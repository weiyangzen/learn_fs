## sources/distributed-fs/ceph-client/tools/perf/tests/shell/perftool-testsuite_probe.sh

Purpose: driver for an external/base probe shell test suite under `base_probe`.
Important behavior: requires root, requires a `base_probe` directory next to the script, creates `PERFSUITE_RUN_DIR`, and executes executable `setup.sh`/`test_*` files.
Control flow: accumulates child exit statuses, optionally preserves logs when `PERFTEST_KEEP_LOGS=y`, and exits `1` if any child failed.
State and persistence: temp run directory is exported and removed unless log retention is requested.
Dependencies and integration: integrates legacy perftool tests into perf's shell test discovery; marked exclusive in its description.
Risks: summing statuses can lose exact failing test identity; sourced environment from child scripts can affect later scripts.
Test signals: child exit statuses, root/base directory checks as skip code `2`, and final nonzero failure.
