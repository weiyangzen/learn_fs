## sources/distributed-fs/ceph-client/tools/perf/tests/shell/stat+json_output.sh

Purpose: validates `perf stat -j` JSON records for multiple aggregation modes.
Important functions: local `ParanoidAndNotRoot`, `check_*` functions for no-args, system-wide, no-aggr, interval, event, per-core/thread/cache/cluster/die/node/socket, metric-only, and `check_for_topology`.
Control flow: each mode writes JSON to a temp file or pipe and invokes `lib/perf_json_output_lint.py` through `$PYTHON` with a mode flag.
State and persistence: one temp JSON file is removed.
Dependencies and integration: requires Python, JSON lint helper, stat modes, CPU topology, and permissions for system-wide modes.
Risks: duplicates logic from `stat_output.sh`; topology and permission skips can reduce coverage.
Test signals: Python linter accepts each mode-specific JSON shape.
