## sources/distributed-fs/ceph-client/tools/perf/tests/shell/lib/stat_output.sh

Purpose: shared helpers for perf stat output-format tests, abstracting repeated invocations for standard, CSV, and JSON output validation.
Important functions: `ParanoidAndNotRoot`, `check_no_args`, `check_system_wide`, `check_system_wide_no_aggr`, `check_interval`, `check_event`, `check_per_core`, `check_per_thread`, `check_per_cache_instance`, `check_per_cluster`, `check_per_die`, `check_per_node`, `check_per_socket`, `check_metric_only`, and `check_for_topology`.
Control flow: each `check_*` prints a mode label, optionally skips permission-sensitive modes, runs `perf stat` with mode-specific flags and caller-supplied output options, then calls caller-defined `commachecker`.
State and persistence: no persistent state; it reads `/proc/sys/kernel/perf_event_paranoid`, CPU topology files, `/proc/cpuinfo`, and relies on caller temp files.
Dependencies and integration: sourced by `stat+csv_output.sh` and `stat+std_output.sh`; JSON file duplicates similar logic with Python linting.
Risks: topology skip depends on `physical_package_id` visibility and can mask socket/core/die checks on restricted platforms; `commachecker` must exist in caller scope.
Test signals: success is mode-by-mode output validation, while permission and topology limits are reported as skips rather than failures.
