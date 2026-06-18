# Research report: subset-b-006750

Grouped research for perf shell and C tests under `sources/distributed-fs/ceph-client/tools/perf/tests`. Each section is source-tree aligned and delimited for reconciliation into per-file documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/lib/probe_vfs_getname.sh -->
## sources/distributed-fs/ceph-client/tools/perf/tests/shell/lib/probe_vfs_getname.sh

Purpose: shared shell library for tests that need a `probe:vfs_getname` kernel probe on `getname_flags` to expose filename/pathname data to `perf record`, `perf script`, and `perf trace`.
Important functions: `cleanup_probe_vfs_getname`, `add_probe_vfs_getname`, `skip_if_no_debuginfo`, and `skip_no_probe_record_support`. The library snapshots whether the probe already existed in `had_vfs_getname`, avoids deleting preexisting probes, and tries several source-line regexes for old and new kernel layouts.
Control flow: probe addition lists `getname_flags`, extracts a line containing `initname`, `result->uptr`, or `result->aname`, then attempts a typed `pathname=result->name:string` probe before falling back to `filename:ustring`.
State and persistence: it mutates global kernel perf probe state only when the probe was absent at startup, then removes `probe:vfs_getname*` on cleanup.
Dependencies and integration: requires `perf probe`, kernel debuginfo for line probes, optional libtraceevent support for recording probe events, and is sourced by probe, record/script, and trace tests.
Risks: regexes are kernel-source-layout sensitive; failure codes distinguish unsupported debuginfo (`2`) from actual probe failure (`1`). Existing user probes must not be removed.
Test signals: successful return from `add_probe_vfs_getname`, skip detection in debuginfo/libtraceevent checks, and later consumers seeing `probe:vfs_getname` events.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/lib/probe_vfs_getname.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/lib/setup_python.sh -->
## sources/distributed-fs/ceph-client/tools/perf/tests/shell/lib/setup_python.sh

Purpose: small shared setup library that discovers a Python interpreter for shell tests that validate JSON, metrics, or perf scripting.
Important behavior: if `$PYTHON` is unset it first tries `python3 --version`, then `python --version`; if neither exists it prints a skip message and exits `2`.
Control flow: sourced scripts inherit a populated `PYTHON` variable or terminate immediately with the perf test skip code.
State and persistence: only shell variable state is changed; no files are created.
Dependencies and integration: used by `list.sh`, `python-use.sh`, `script_dlfilter.sh`, JSON/stat metric tests, and data converter tests.
Risks: exits the caller when sourced, so callers must source it only after they are ready to skip; does not validate Python module availability beyond the interpreter command.
Test signals: downstream tests run `$PYTHON` successfully or are skipped with code `2`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/lib/setup_python.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/lib/stat_output.sh -->
## sources/distributed-fs/ceph-client/tools/perf/tests/shell/lib/stat_output.sh

Purpose: shared helpers for perf stat output-format tests, abstracting repeated invocations for standard, CSV, and JSON output validation.
Important functions: `ParanoidAndNotRoot`, `check_no_args`, `check_system_wide`, `check_system_wide_no_aggr`, `check_interval`, `check_event`, `check_per_core`, `check_per_thread`, `check_per_cache_instance`, `check_per_cluster`, `check_per_die`, `check_per_node`, `check_per_socket`, `check_metric_only`, and `check_for_topology`.
Control flow: each `check_*` prints a mode label, optionally skips permission-sensitive modes, runs `perf stat` with mode-specific flags and caller-supplied output options, then calls caller-defined `commachecker`.
State and persistence: no persistent state; it reads `/proc/sys/kernel/perf_event_paranoid`, CPU topology files, `/proc/cpuinfo`, and relies on caller temp files.
Dependencies and integration: sourced by `stat+csv_output.sh` and `stat+std_output.sh`; JSON file duplicates similar logic with Python linting.
Risks: topology skip depends on `physical_package_id` visibility and can mask socket/core/die checks on restricted platforms; `commachecker` must exist in caller scope.
Test signals: success is mode-by-mode output validation, while permission and topology limits are reported as skips rather than failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/lib/stat_output.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/lib/waiting.sh -->
## sources/distributed-fs/ceph-client/tools/perf/tests/shell/lib/waiting.sh

Purpose: polling utilities for asynchronous shell tests that launch workloads or background `perf record`.
Important functions: `wait_for_threads`, `wait_for_perf_to_start`, `wait_for_process_to_exit`, and `is_running`.
Control flow: functions poll `/proc/$pid`, `/proc/$pid/task`, or a perf debug log until conditions are met or a tenths-of-a-second timeout expires.
State and persistence: no persistent state; `tenths` command computes current time with tenths precision.
Dependencies and integration: sourced by `record.sh` and `test_intel_pt.sh` to avoid races around thread creation, perf startup, and workload exit.
Risks: relies on `/proc` and a specific verbose message, `perf record has started`; slow or heavily loaded systems can hit timeout-driven false failures.
Test signals: zero return means the synchronization condition occurred; nonzero return includes a diagnostic suitable for perf test logs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/lib/waiting.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/list.sh -->
## sources/distributed-fs/ceph-client/tools/perf/tests/shell/list.sh

Purpose: validates that `perf list -j` emits syntactically valid JSON.
Important functions: `cleanup`, `trap_cleanup`, and `test_list_json`.
Control flow: discovers Python, creates a temp JSON file, runs `perf list -j -o`, and validates it using `$PYTHON -m json.tool`.
State and persistence: creates and removes one temp file under `/tmp`; no perf state is changed.
Dependencies and integration: depends on `lib/setup_python.sh`, `perf list`, and Python's standard JSON module.
Risks: only validates JSON syntax, not schema or field semantics; exits through trap on failures under `set -e`.
Test signals: successful JSON parse prints success and exits `0`; missing Python exits `2`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/list.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/lock_contention.sh -->
## sources/distributed-fs/ceph-client/tools/perf/tests/shell/lock_contention.sh

Purpose: integration test for `perf lock record` and `perf lock contention`, including BPF mode, aggregations, filters, and CSV output.
Important functions: `check`, `test_record`, `test_bpf`, `test_record_concurrent`, `test_aggr_task`, `test_aggr_addr`, `test_aggr_cgroup`, `test_type_filter`, `test_lock_filter`, `test_stack_filter`, `test_aggr_task_stack_filter`, `test_cgroup_filter`, and `test_csv_output`.
Control flow: root and tracepoint availability are checked first, then a lock-contention perf.data is recorded from `perf bench sched messaging -p`. Subsequent tests replay the file or run live BPF contention with expected one-line or filtered output.
State and persistence: temp perf data, result, and stderr files are removed by traps; kernel BPF/tracepoint state is used but not persisted.
Dependencies and integration: requires root, `lock:contention_begin` tracepoints, at least four CPUs, `perf bench`, and optional BPF support.
Risks: workload may not always trigger specific locks like `tasklist_lock` or call stacks containing `unix_stream`; those subchecks skip when evidence is absent. Output column parsing is brittle to formatting changes.
Test signals: one quiet result line for top-N tests, zero nonmatching filter lines, valid comma counts, and skip code `2` for missing environment.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/lock_contention.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/perf-report-hierarchy.sh -->
## sources/distributed-fs/ceph-client/tools/perf/tests/shell/perf-report-hierarchy.sh

Purpose: smoke test for `perf report --hierarchy`.
Important functions: `cleanup`, `trap_cleanup`, and `test_report_hierarchy`.
Control flow: creates a private temp directory, records `uname`, then runs `perf report --hierarchy` against the generated perf.data.
State and persistence: temp directory is path-checked before deletion to reduce cleanup risk.
Dependencies and integration: exercises the report path after `perf record`; no external helper libraries are sourced.
Risks: only verifies command success, not hierarchy content; perf record permission restrictions can fail the test.
Test signals: nonzero command failure aborts under `set -e`; success prints `perf report --hierarchy test [Success]`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/perf-report-hierarchy.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/perf_sched_stats.sh -->
## sources/distributed-fs/ceph-client/tools/perf/tests/shell/perf_sched_stats.sh

Purpose: validates `perf sched stats` record, report, live, and diff subcommands.
Important functions: `test_perf_sched_stats_record`, `test_perf_sched_stats_report`, `test_perf_sched_stats_live`, and `test_perf_sched_stats_diff`.
Control flow: requires root, records scheduler stats to one or two temp files, checks record output, report/live `Description` output, and diff command success.
State and persistence: two temp perf.data paths and `.old` companions are removed on cleanup.
Dependencies and integration: depends on scheduler trace infrastructure and root permissions.
Risks: checks for literal output strings; format changes may require test updates. Live mode depends on available scheduler events.
Test signals: each subtest updates `err`; final exit is accumulated success/failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/perf_sched_stats.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/perftool-testsuite_probe.sh -->
## sources/distributed-fs/ceph-client/tools/perf/tests/shell/perftool-testsuite_probe.sh

Purpose: driver for an external/base probe shell test suite under `base_probe`.
Important behavior: requires root, requires a `base_probe` directory next to the script, creates `PERFSUITE_RUN_DIR`, and executes executable `setup.sh`/`test_*` files.
Control flow: accumulates child exit statuses, optionally preserves logs when `PERFTEST_KEEP_LOGS=y`, and exits `1` if any child failed.
State and persistence: temp run directory is exported and removed unless log retention is requested.
Dependencies and integration: integrates legacy perftool tests into perf's shell test discovery; marked exclusive in its description.
Risks: summing statuses can lose exact failing test identity; sourced environment from child scripts can affect later scripts.
Test signals: child exit statuses, root/base directory checks as skip code `2`, and final nonzero failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/perftool-testsuite_probe.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/perftool-testsuite_report.sh -->
## sources/distributed-fs/ceph-client/tools/perf/tests/shell/perftool-testsuite_report.sh

Purpose: driver for an external/base report shell test suite under `base_report`.
Important behavior: checks for `base_report`, exports `PERFSUITE_RUN_DIR`, executes executable `setup.sh` and `test_*` files, and cleans logs unless `PERFTEST_KEEP_LOGS=y`.
Control flow: same accumulator model as the probe suite, but without a root precondition.
State and persistence: temp run directory is the only persistent state and is removed by default.
Dependencies and integration: lets perf test treat legacy report tests as one exclusive shell suite.
Risks: broad child environment coupling and aggregate status obscure precise failing case unless logs are kept.
Test signals: missing base directory skips; any nonzero child status fails the suite.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/perftool-testsuite_report.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/pipe_test.sh -->
## sources/distributed-fs/ceph-client/tools/perf/tests/shell/pipe_test.sh

Purpose: validates perf.data pipe mode across `perf record`, `perf report`, and `perf inject` build-id paths.
Important functions: `test_record_report` and `test_inject_bids`.
Control flow: requires `noploop` symbol, records `perf test -w noploop` to stdout and files, reports from `-` and temp files, and repeats inject tests for `-B`, `-b`, `--buildid-all`, and `--mmap2-buildid-all`.
State and persistence: two temp perf.data files plus `.old` companions are removed.
Dependencies and integration: uses `lib/perf_has_symbol.sh`, task-clock user event, report symbol resolution, and build-id injection.
Risks: symbol visibility and architecture-specific workload arguments affect reliability; pipe failures may be hard to diagnose because most commands are pipelines.
Test signals: report output must include `perf` in task view and `noploop` after inject/report paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/pipe_test.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/probe_vfs_getname.sh -->
## sources/distributed-fs/ceph-client/tools/perf/tests/shell/probe_vfs_getname.sh

Purpose: exclusive smoke test that adds and removes the shared `probe:vfs_getname` probe.
Important behavior: sources `lib/probe.sh` and `lib/probe_vfs_getname.sh`, requires perf probe support and root, then calls `add_probe_vfs_getname`.
Control flow: if adding the probe returns `1`, it calls `skip_if_no_debuginfo` to convert missing kernel debuginfo into skip code `2`; cleanup runs before exit.
State and persistence: may add a kernel probe and removes it only if absent at startup.
Dependencies and integration: validates the common probe library before record/trace consumers rely on it.
Risks: kernel source-line matching and debuginfo availability dominate outcomes; incorrect `had_vfs_getname` handling could delete user-created probes.
Test signals: final exit code from add/skip path and clean probe removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/probe_vfs_getname.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/python-use.sh -->
## sources/distributed-fs/ceph-client/tools/perf/tests/shell/python-use.sh

Purpose: validates that Python can import perf's Python binding.
Important behavior: discovers Python, tries to locate `$(dirname $(which perf))/python`, conditionally prepends that path to `sys.path`, imports `perf`, and prints `success!`.
Control flow: builds a small inline Python program and pipes it to `$PYTHON`; grep for `success!` decides pass/fail.
State and persistence: no files; only a shell heredoc command string.
Dependencies and integration: depends on perf's Python extension installation layout or Python path.
Risks: `which perf` path may not match source-tree module location; import-only coverage does not exercise binding APIs.
Test signals: interpreter output containing `success!` yields exit `0`; import failure exits `1`; missing Python exits `2`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/python-use.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/record+probe_libc_inet_pton.sh -->
## sources/distributed-fs/ceph-client/tools/perf/tests/shell/record+probe_libc_inet_pton.sh

Purpose: tests uprobes on libc's `inet_pton` and dwarf callgraph capture during a localhost IPv6 `ping`.
Important functions: `add_libc_inet_pton_event`, `trace_libc_inet_pton_backtrace`, and `delete_libc_inet_pton_event`.
Control flow: discovers libc from `/proc/self/maps`, verifies `inet_pton` in dynamic symbols, adds a `probe_libc` event, records it with callgraph attributes while running `ping -6 -c 1 ::1`, then matches expected stack regexes.
State and persistence: adds a perf uprobe event and deletes it; temp expected/script/perfdata files are removed.
Dependencies and integration: requires root, perf probe, IPv6 loopback, `nm`, `ping`, libc symbols, CFI/unwind data, and libtraceevent record support.
Risks: libc implementation, binary paths, s390x stack shapes, and ping availability can change expected frames.
Test signals: event creation output, perf.data creation, and ordered regex matches in `perf script`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/record+probe_libc_inet_pton.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/record+script_probe_vfs_getname.sh -->
## sources/distributed-fs/ceph-client/tools/perf/tests/shell/record+script_probe_vfs_getname.sh

Purpose: verifies that `perf record` captures the shared `vfs_getname` probe and `perf script` exposes the touched pathname argument.
Important functions: `record_open_file` and `perf_script_filenames`.
Control flow: adds the probe, creates temp perf.data and target file, records `touch $file` with `-e probe:vfs_getname*`, then greps `perf script` for a `touch` event with `pathname="$file"`.
State and persistence: temporary files and the added probe are cleaned up.
Dependencies and integration: requires root, perf probe, kernel debuginfo or existing probe, and libtraceevent support.
Risks: event name suffixes, pathname quoting, and kernel symbol argument naming can break the regex.
Test signals: successful probe addition, record support check, and matching perf script line.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/record+script_probe_vfs_getname.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/record+zstd_comp_decomp.sh -->
## sources/distributed-fs/ceph-client/tools/perf/tests/shell/record+zstd_comp_decomp.sh

Purpose: validates compressed perf.data recording with zstd and equivalent reporting after decompression.
Important functions: `skip_if_no_z_record`, `collect_z_record`, `check_compressed_stats`, and `check_compressed_output`.
Control flow: checks `perf record -h` for compression support, records a high-frequency workload using `-z`, verifies compressed stats in report headers, injects/decompresses, and diffs report output between compressed and decompressed files.
State and persistence: uses temp perf.data plus `.decomp` and output files; cleanup uses a glob-like quoted path that may not expand as intended.
Dependencies and integration: requires zstd-enabled perf, `dd`, `/dev/urandom`, `perf inject`, and report stability.
Risks: report output comparison strips only the last three lines; header/stat format or sample nondeterminism may affect diffs.
Test signals: compressed event stats and zero diff between selected report fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/record+zstd_comp_decomp.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/record.sh -->
## sources/distributed-fs/ceph-client/tools/perf/tests/shell/record.sh

Purpose: broad exclusive integration suite for `perf record` modes and parse terms.
Important functions: `test_per_thread`, `test_register_capture`, `test_system_wide`, `test_workload`, `test_branch_counter`, `test_cgroup`, `test_uid`, `test_leader_sampling`, `test_topdown_leader_sampling`, `test_precise_max`, `test_callgraph`, and `test_ratio_to_prev`.
Control flow: after symbol checks for `test_loop` and `brstack`, it raises file descriptor limits for CPU-thread mode, records workload variants, reports or scripts back evidence, and validates parse-time errors for invalid `ratio-to-prev` use.
State and persistence: temp perf.data and script output files are reused and removed; process state includes background `perf test -w thloop` during per-thread attach.
Dependencies and integration: uses `lib/waiting.sh`, `lib/perf_has_symbol.sh`, perf workloads, CPU PMU sysfs caps, cgroups, `bc`, and hardware event support.
Risks: permissions, hardware capabilities, throttling, hybrid PMUs, and architecture-specific event availability cause skips or tolerance-based checks.
Test signals: report symbols, branch counter dump/script text, CGROUP records, UID sampling output, grouped cycles consistency, and expected parser diagnostics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/record.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/record_bpf_filter.sh -->
## sources/distributed-fs/ceph-client/tools/perf/tests/shell/record_bpf_filter.sh

Purpose: validates `perf record --filter` sample filtering implemented via BPF.
Important functions: `test_bpf_filter_priv`, `test_bpf_filter_basic`, `test_bpf_filter_fail`, `test_bpf_filter_group`, `test_bpf_filter_multi`, and `test_bpf_filter_cgroup`.
Control flow: first probes privilege/support, then records filtered task-clock/page-fault samples, checks forbidden filters produce required sample-type diagnostics, validates multiple filters, and verifies cgroup filtering with `--all-cgroups`.
State and persistence: one temp perf.data file is reused and cleaned.
Dependencies and integration: needs BPF filter support, perf record/script/report, cgroup sample support, and sometimes root or setup-filter pinning.
Risks: kernel 6.2 is explicitly treated as unsupported for one IP filter path; address filters assume kernel addresses have `ffffffff` prefix.
Test signals: absence of filtered-out kernel IPs, expected `PERF_SAMPLE_*` diagnostics, task-clock period thresholds, and root cgroup 100% report.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/record_bpf_filter.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/record_lbr.sh -->
## sources/distributed-fs/ceph-client/tools/perf/tests/shell/record_lbr.sh

Purpose: x86 Last Branch Record validation for callgraph and branch-stack capture, both sequential and parallel.
Important functions: `ParanoidAndNotRoot`, `lbr_callgraph_test`, `lbr_test`, and `parallel_lbr_test`.
Control flow: skips when CPU PMU branch caps are absent, runs `perf record` with LBR callgraph and branch filters, checks report decoding, verifies every sample has a branch stack, and measures empty stack ratio under threshold. Parallel subtests run several filters simultaneously.
State and persistence: temp perf.data/text files per parent or child process; no persistent state.
Dependencies and integration: requires x86 LBR-capable PMU, `perf test -w thloop`, cycles event, and permissions for system-wide modes.
Risks: parallel tests use relaxed 100% thresholds for some filters to avoid hardware contention false failures; permission gates skip system-wide checks.
Test signals: report success with `--stitch-lbr`, nonzero sample count, branch stack count equal to sample count, and acceptable empty-stack ratio.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/record_lbr.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/record_offcpu.sh -->
## sources/distributed-fs/ceph-client/tools/perf/tests/shell/record_offcpu.sh

Purpose: validates `perf record --off-cpu` profiling, child accounting, and threshold behavior.
Important functions: `test_offcpu_priv`, `test_offcpu_basic`, `test_offcpu_child`, `test_offcpu_above_thresh`, and `test_offcpu_below_thresh`.
Control flow: requires root and BPF skeleton support, records off-CPU samples for `sleep` and `perf bench sched messaging`, verifies `offcpu-time` event/report output, then uses timestamp windows to distinguish direct samples above threshold from at-end samples below threshold.
State and persistence: one temp perf.data file and `.old` file are cleaned.
Dependencies and integration: requires BPF skeletons, dummy event, offcpu-time synthetic event, report/script time filtering, and scheduler blocking workload.
Risks: timestamp constants rely on OFF_CPU_TIMESTAMP encoding; timing thresholds can be sensitive on slow systems.
Test signals: `perf evlist` contains `offcpu-time`, report includes `sleep`, child sample count exceeds expected process count, and direct/at-end sample windows match thresholds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/record_offcpu.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/record_sideband.sh -->
## sources/distributed-fs/ceph-client/tools/perf/tests/shell/record_sideband.sh

Purpose: validates sideband tracking events when recording CPU-wide on one CPU while the workload runs on another.
Important functions: `can_cpu_wide` and `test_system_wide_tracking`.
Control flow: probes recording on CPU 0 and CPU 1, records on CPU 0 with `taskset` binding workload to CPU 1, then checks `perf script --show-mmap-events -C 1` for MMAP events.
State and persistence: temp perf.data file is removed.
Dependencies and integration: uses CPU-wide recording, taskset, sideband MMAP synthesis, and `--no-bpf-event`.
Risks: systems with fewer than two CPUs, CPU affinity restrictions, or perf_event_paranoid can skip/fail; only MMAP count is validated.
Test signals: nonzero MMAP event count for CPU 1 while tracing CPU 0.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/record_sideband.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/record_weak_term.sh -->
## sources/distributed-fs/ceph-client/tools/perf/tests/shell/record_weak_term.sh

Purpose: verifies explicit command-line sample period overrides weak/default period terms from sysfs or JSON event definitions.
Important behavior: parses `perf list --json` with Python to find the first event whose encoding contains `period=`, then records it with `-c 1000 -vv`.
Control flow: skips if no such event exists, shows detailed event info, then greps verbose record output for sample period/frequency value `1000`.
State and persistence: no temp files.
Dependencies and integration: requires Python, perf JSON list output, and an event definition with inbuilt period.
Risks: verbose output formatting is literal; event availability depends on PMU metadata.
Test signals: verbose record output includes `{ sample_period, sample_freq }   1000`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/record_weak_term.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/sched.sh -->
## sources/distributed-fs/ceph-client/tools/perf/tests/shell/sched.sh

Purpose: tests core `perf sched` record, latency, script, map, and timehist commands.
Important functions: `start_noploops`, `cleanup_noploops`, `test_sched_record`, `test_sched_latency`, `test_sched_script`, `test_sched_map`, and `test_sched_timehist`.
Control flow: requires root, starts two `noploop` workloads pinned to CPU0, records scheduler events for one second, kills workloads, then verifies each report mode mentions `perf-noploop`.
State and persistence: temp perf.data and two background PIDs are managed by cleanup.
Dependencies and integration: requires taskset, scheduler tracepoints, perf workload `noploop`, and root.
Risks: assumes CPU0 affinity can be set; workload cleanup must run to avoid stale processes.
Test signals: `perf-noploop` appears in all sched output modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/sched.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/script.sh -->
## sources/distributed-fs/ceph-client/tools/perf/tests/shell/script.sh

Purpose: tests Python DB-export mode and `parallel-perf.py` integration for `perf script`.
Important functions: `test_db` and `test_parallel_perf`.
Control flow: DB test skips when Python scripting support is off, creates a temporary Python script with `perf_db_export_*` flags and callbacks, records `true`, and runs `perf script -s`. Parallel test records `uname` with sample CPU and runs `scripts/python/parallel-perf.py` in regular and per-CPU modes.
State and persistence: temp directory contains perf.data, generated script, and parallel output directories; cleanup removes it.
Dependencies and integration: depends on perf Python scripting, ASAN leak suppression, source-tree script path, and Python 3 for parallel-perf.
Risks: generated callback has a malformed-looking print string but only command success is checked; parallel-perf path differs between installed and source builds.
Test signals: command completion for script DB export and parallel processing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/script.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/script_dlfilter.sh -->
## sources/distributed-fs/ceph-client/tools/perf/tests/shell/script_dlfilter.sh

Purpose: validates `perf script --dlfilter` by compiling a small shared-object filter.
Important behavior: generates C code implementing `filter_event`, using `perf_dlfilter_fns.resolve_ip` to pass only samples whose symbol is `test_loop`.
Control flow: requires `cc`, records `perf test -w thloop`, compiles the filter against perf include files, links a shared object, and checks filtered script output contains `test_loop` and not unrelated perf symbols.
State and persistence: temp perf.data, C, object, and shared object files are removed.
Dependencies and integration: requires compiler, perf dlfilter header, dynamic loading, symbol resolution, and `thloop`.
Risks: compiler/include path issues are treated as skips; filtering validation is intentionally simple and may miss non-perf false positives.
Test signals: filtered output includes `test_loop` and excludes obvious `perf` symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/script_dlfilter.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/script_perl.sh -->
## sources/distributed-fs/ceph-client/tools/perf/tests/shell/script_perl.sh

Purpose: validates generated Perl scripts from `perf script -g`.
Important functions: `check_perl_support` and `test_script`.
Control flow: sets `PERF_EXEC_PATH` for source-tree scripts, checks libperl support, tries `sched:sched_switch` first, then `task-clock` if tracepoint recording skips. For each event it records `thloop`, generates a Perl script, executes it, and searches for expected callback output.
State and persistence: temp perf.data and generated `.pl` are cleaned by traps.
Dependencies and integration: requires libperl support, tracepoints or task-clock, Data::Dumper output for generic events, and perf workload.
Risks: tracepoint recording may require permissions; expected output differs by event class.
Test signals: generated script exists and execution output contains `sched::sched_switch` or `$VAR1`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/script_perl.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/script_python.sh -->
## sources/distributed-fs/ceph-client/tools/perf/tests/shell/script_python.sh

Purpose: validates generated Python scripts from `perf script -g`.
Important functions: `check_python_support` and `test_script`.
Control flow: sets `PERF_EXEC_PATH`, checks libpython support, records either `sched:sched_switch` or `task-clock`, generates a Python script, appends a `process_event` callback for generic events if absent, then runs it and searches output.
State and persistence: temp perf.data and generated `.py` are cleaned.
Dependencies and integration: requires perf Python scripting and recordable tracepoint or generic event.
Risks: generated script behavior differs between tracepoint and generic events; permissions can skip both event attempts.
Test signals: output includes `sched__sched_switch` for tracepoint or `param_dict` for generic event.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/script_python.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/stat+csv_output.sh -->
## sources/distributed-fs/ceph-client/tools/perf/tests/shell/stat+csv_output.sh

Purpose: lints field counts for `perf stat` CSV-like output using a custom separator.
Important function: caller-defined `commachecker`, plus checks imported from `lib/stat_output.sh`.
Control flow: sets `csv_sep=@`, runs shared stat checks with `-x@ -o temp`, and verifies each non-comment/nonblank line has the expected number of separators per aggregation mode.
State and persistence: one temp stat output file is reused and removed.
Dependencies and integration: depends on `stat_output.sh`, perf stat modes, CPU topology, and shell regex matching.
Risks: expected field counts are tightly coupled to output format; s390x has a special field-count range for no-aggregation mode.
Test signals: every checked mode prints `[Success]`; topology-restricted modes are skipped when socket id is invalid.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/stat+csv_output.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/stat+csv_summary.sh -->
## sources/distributed-fs/ceph-client/tools/perf/tests/shell/stat+csv_summary.sh

Purpose: verifies CSV interval summary labeling behavior.
Important behavior: runs `perf stat -e cycles -x' ' -I1000 --interval-count 1 --summary` and expects a `summary` first field, then runs with `--no-csv-summary` and expects no summary-labeled line.
Control flow: two pipelines grep for `summary` and read fields; unexpected labels cause exit `1`.
State and persistence: no files.
Dependencies and integration: requires cycles event and interval stat support.
Risks: if cycles is unavailable or output text changes, the shell pipelines may fail under `set -e`.
Test signals: first mode sees `summary`; second mode produces no summary label.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/stat+csv_summary.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/stat+event_uniquifying.sh -->
## sources/distributed-fs/ceph-client/tools/perf/tests/shell/stat+event_uniquifying.sh

Purpose: checks that deduplicated PMU event names are uniquified in `perf stat` output when duplicate PMU instances exist.
Important function: `test_event_uniquifying`.
Control flow: compares `perf list --raw pmu` with verbose raw PMU listing, strips numeric PMU suffixes from verbose-only events, runs `perf stat -e "$event" -A`, and requires output to mention the non-deduplicated PMU event name.
State and persistence: temp stat output file is removed.
Dependencies and integration: relies on PMU sysfs metadata and perf list/stat behavior.
Risks: no duplicate PMUs means no assertions; command failures are converted to skip if no prior hard failure occurred.
Test signals: uniquified verbose PMU event appears in stat output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/stat+event_uniquifying.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/stat+json_output.sh -->
## sources/distributed-fs/ceph-client/tools/perf/tests/shell/stat+json_output.sh

Purpose: validates `perf stat -j` JSON records for multiple aggregation modes.
Important functions: local `ParanoidAndNotRoot`, `check_*` functions for no-args, system-wide, no-aggr, interval, event, per-core/thread/cache/cluster/die/node/socket, metric-only, and `check_for_topology`.
Control flow: each mode writes JSON to a temp file or pipe and invokes `lib/perf_json_output_lint.py` through `$PYTHON` with a mode flag.
State and persistence: one temp JSON file is removed.
Dependencies and integration: requires Python, JSON lint helper, stat modes, CPU topology, and permissions for system-wide modes.
Risks: duplicates logic from `stat_output.sh`; topology and permission skips can reduce coverage.
Test signals: Python linter accepts each mode-specific JSON shape.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/stat+json_output.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/stat+shadow_stat.sh -->
## sources/distributed-fs/ceph-client/tools/perf/tests/shell/stat+shadow_stat.sh

Purpose: verifies derived `insn_per_cycle` shadow-stat metric values against raw instruction/cycle counts.
Important functions: `test_global_aggr` and `test_no_aggr`.
Control flow: skips if system-wide stat is forbidden or hybrid CPU output is detected, then runs global and per-CPU `perf stat -M insn_per_cycle`, recalculates IPC with awk, and fails if difference exceeds `THRESHOLD=0.015`.
State and persistence: no files.
Dependencies and integration: needs cycles/instructions counts, system-wide permissions, and non-hybrid output assumptions.
Risks: parsing depends on text columns and metric rounding; not-counted events are skipped line-by-line.
Test signals: computed IPC matches printed IPC within tolerance for aggregate and no-aggregate modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/stat+shadow_stat.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/stat+std_output.sh -->
## sources/distributed-fs/ceph-client/tools/perf/tests/shell/stat+std_output.sh

Purpose: lints default human-readable `perf stat` output for known default event names and associated metric names.
Important function: caller-defined `commachecker`, backed by `stat_output.sh` mode runners.
Control flow: after each shared stat invocation, skips comments/headers/elapsed time, strips aggregation prefixes, validates event names against `event_name[]`, and validates metric labels against `event_metric[]` unless ignored topdown metrics match `skip_metric[]`.
State and persistence: temp stat output file is removed.
Dependencies and integration: exercises standard output for default stat modes, topology-driven aggregations, and metric-only mode.
Risks: tight coupling to output text and default event set; metric-only check returns on first nonempty line rather than validating all metrics.
Test signals: all parsed lines have expected event/metric names; topology-restricted modes skip cleanly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/stat+std_output.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/stat.sh -->
## sources/distributed-fs/ceph-client/tools/perf/tests/shell/stat.sh

Purpose: broad functional suite for `perf stat` command behavior beyond output-format linting.
Important functions: `test_default_stat`, `test_null_stat`, `find_offline_cpu`, `test_offline_cpu_stat`, `test_stat_record_report`, `test_stat_record_script`, `test_stat_repeat_weak_groups`, `test_topdown_groups`, `test_topdown_weak_groups`, `test_cputype`, `test_hybrid`, `test_stat_cpu`, `test_stat_no_aggr`, `test_stat_detailed`, `test_stat_repeat`, and `test_stat_pid`.
Control flow: runs stat subcommands and parser scenarios, checks output strings, exercises offline CPU handling, stat record/report/script pipes, topdown event reordering, CPU type filtering, hybrid default cycles, CPU list/range handling, detailed output, repeats, and PID attach.
State and persistence: one temp output file and a short-lived `sleep` PID are managed.
Dependencies and integration: reads CPU sysfs online/topology and PMU devices; uses perf stat/report/script and parser behavior.
Risks: hardware event availability and permission settings can make some checks fail rather than skip; topdown/raw encodings are platform-sensitive.
Test signals: expected stat headers, parser diagnostics, CPU columns, variance output, and event names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/stat.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/stat_all_metricgroups.sh -->
## sources/distributed-fs/ceph-client/tools/perf/tests/shell/stat_all_metricgroups.sh

Purpose: attempts every metric group from `perf list --raw-dump metricgroups`.
Important behavior: chooses `-a` unless perf_event_paranoid prevents non-root system-wide access, then runs `perf stat -M "$group" sleep 0.01`.
Control flow: successful groups set overall status to pass; permission errors become skips; Default2/3/4 failures are ignored due to possible unsupported legacy events; other failures set hard failure.
State and persistence: no files.
Dependencies and integration: PMU metric metadata and perf stat metric resolver.
Risks: tiny workload can make some groups unsupported or not counted; broad loop is environment-dependent.
Test signals: each metric group either runs, is permission-skipped, is explicitly ignored, or fails with captured output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/stat_all_metricgroups.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/stat_all_metrics.sh -->
## sources/distributed-fs/ceph-client/tools/perf/tests/shell/stat_all_metrics.sh

Purpose: attempts every individual metric from `perf list --raw-dump metrics`.
Important behavior: uses system-wide `sleep 0.01` when permitted, otherwise a `noploop` workload; retries failures with `perf bench internals synthesize`.
Control flow: treats missing events, not-supported/not-counted output, FP/AMX/PMM issues, and permission restrictions according to expected skip/ignore rules; hard-fails when a non-Default metric cannot be printed.
State and persistence: no files.
Dependencies and integration: metric JSON/sysfs metadata, perf stat metric evaluation, and fallback workloads.
Risks: highly platform-dependent and may be noisy across PMU generations; output match uses first 50 chars of metric name.
Test signals: metric name appears in successful output or a recognized skip/ignore reason is printed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/stat_all_metrics.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/stat_all_pfm.sh -->
## sources/distributed-fs/ceph-client/tools/perf/tests/shell/stat_all_pfm.sh

Purpose: exercises all libpfm4 events exposed through `perf list --raw-dump pfm`.
Important behavior: skips entirely if `HAVE_LIBPFM` is off, skips uncore events and invalid/missing unit mask messages, and runs `perf stat --pfm-events`.
Control flow: first tries `true`, then a longer synthesize benchmark if supported output did not include the event.
State and persistence: no files.
Dependencies and integration: requires libpfm4 build support and PMU/event availability.
Risks: broad hardware-dependent coverage; uncore events are intentionally excluded because they may need extra options.
Test signals: event name appears in stat output or is recognized as not supported/invalid unit mask.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/stat_all_pfm.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/stat_all_pmu.sh -->
## sources/distributed-fs/ceph-client/tools/perf/tests/shell/stat_all_pmu.sh

Purpose: exclusive broad test for all non-parameterized PMU events from `perf list --raw-dump pmu`.
Important behavior: removes parameterized event patterns containing `?`, runs `perf stat -e "$p" true`, accepts supported, not-supported, permission-limited, and access-limited outcomes, and retries missing output with a longer synthesize benchmark.
Control flow: traps print the last result on unexpected signal; loops every PMU event and accumulates `err`.
State and persistence: no temp files, only shell `result`/`output`.
Dependencies and integration: PMU sysfs metadata, perf list/stat, and benchmark fallback.
Risks: can be slow/noisy on systems with many PMUs; parser/output changes around unsupported events affect classification.
Test signals: every event either appears, is unsupported/permission-limited, or causes a failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/stat_all_pmu.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/stat_bpf_counters.sh -->
## sources/distributed-fs/ceph-client/tools/perf/tests/shell/stat_bpf_counters.sh

Purpose: verifies `perf stat --bpf-counters` and `/b` event modifier produce counts comparable to regular counting.
Important functions: `compare_number`, `check_counts`, `test_bpf_counters`, and `test_bpf_modifier`.
Control flow: skips if `--bpf-counters` cannot count instructions, then counts `instructions` for `perf test -w sqrtloop` normally and with BPF, requiring the BPF count to be within +/-20%. It repeats the comparison using named base and bpf events in one stat command.
State and persistence: no files.
Dependencies and integration: requires BPF counters support, instructions event, and `sqrtloop`.
Risks: workload noise beyond 20% fails; not-counted base events skip, but not-counted BPF events fail.
Test signals: comparable instruction totals and successful named modifier output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/stat_bpf_counters.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/stat_bpf_counters_cgrp.sh -->
## sources/distributed-fs/ceph-client/tools/perf/tests/shell/stat_bpf_counters_cgrp.sh

Purpose: validates `perf stat --bpf-counters --for-each-cgroup` with system-wide cgroup counting.
Important functions: `check_bpf_counter`, `find_cgroups`, and `check_system_wide_counted`.
Control flow: probes support using root cgroup, chooses common systemd slices or root/self cgroups, then runs CPU-clock counts for each selected cgroup and fails if any output contains `<not`.
State and persistence: no files.
Dependencies and integration: cgroup v1/v2 files under `/sys/fs/cgroup` and `/proc/self/cgroup`, BPF counters, and system-wide stat.
Risks: cgroup topology and permissions vary widely; result correctness is limited to non-`<not>` output, not value comparison.
Test signals: command success and counted cgroup rows.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/stat_bpf_counters_cgrp.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/stat_metrics_values.sh -->
## sources/distributed-fs/ceph-client/tools/perf/tests/shell/stat_metrics_values.sh

Purpose: runs Intel metric value validation rules through a Python validator.
Important behavior: requires GenuineIntel CPU, discovers Python, sets validator and rule JSON paths, and tests each `/sys/bus/event_source/devices/cpu_*` cputype.
Control flow: for each cputype it invokes `perf_metric_validation.py` with workload `perf bench futex hash -r 2 -s`, an output directory, rules, and cputype; nonzero return prints an error notice and final exit returns the last validator status.
State and persistence: creates a temp output directory and removes it inside the loop.
Dependencies and integration: Intel PMU metrics, Python validation helper, rule JSON, and perf bench futex.
Risks: `tmpdir` is removed after the first iteration, so later validator invocations may depend on recreating output internally; final `ret` is undefined if no `cpu_*` dirs exist.
Test signals: validator exit status and generated validation artifacts on failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/stat_metrics_values.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/test_arm_callgraph_fp.sh -->
## sources/distributed-fs/ceph-client/tools/perf/tests/shell/test_arm_callgraph_fp.sh

Purpose: aarch64-specific check that frame-pointer callgraphs include expected `leaf`, `parent`, and `leafloop` frames.
Important behavior: skips non-aarch64, missing DWARF unwind support, or missing `leafloop` symbol; records `perf test -w leafloop` with `--call-graph fp -e cycles//u --user-callchains`.
Control flow: prints a short script sample for immediate diagnostics, then flattens script output and greps for the expected ordered frame sequence.
State and persistence: temp perf.data is removed by trap.
Dependencies and integration: relies on perf workload symbols and callchain unwinding.
Risks: unwind support is checked even though fp mode is used; symbol names and stack formatting are strict.
Test signals: regex match for `perf -> leaf -> parent -> leafloop`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/test_arm_callgraph_fp.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/test_arm_coresight.sh -->
## sources/distributed-fs/ceph-client/tools/perf/tests/shell/test_arm_coresight.sh

Purpose: exclusive Arm CoreSight ETM trace recording and synthesized sample validation.
Important functions: `skip_if_no_cs_etm_event`, `record_touch_file`, `perf_script_branch_samples`, `perf_report_branch_samples`, `perf_report_instruction_samples`, `is_device_sink`, `arm_cs_iterate_devices`, `arm_cs_etm_traverse_path_test`, `arm_cs_etm_system_wide_test`, `arm_cs_etm_snapshot_test`, `arm_cs_etm_basic_test`, and sparse CPU tests.
Control flow: skips without `cs_etm//`, traverses CoreSight sysfs connections to test each sink, records system-wide, snapshot, per-thread/system-wide/normal timestamp variants, and sparse CPU lists.
State and persistence: temp perf.data and touched file are cleaned; global `glb_err` accumulates failures.
Dependencies and integration: CoreSight PMU sysfs, taskset, trace decode, perf script/report itrace.
Risks: hardware topology traversal is sysfs-name sensitive; snapshot timing and sink support can vary.
Test signals: branch samples in script/report and instruction samples in report for expected command names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/test_arm_coresight.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/test_arm_coresight_disasm.sh -->
## sources/distributed-fs/ceph-client/tools/perf/tests/shell/test_arm_coresight_disasm.sh

Purpose: validates the Arm CoreSight Python disassembly script can reconstruct and disassemble trace ranges without errors.
Important behavior: skips without `cs_etm//`, records kernel trace with `--kcore` when `/proc/kcore` exists, always records userspace trace, and runs `arm-cs-trace-disasm.py -d --stop-sample=30`.
Control flow: checks script output for likely branch instructions (`bl`, `b`, conditional branches, `cbz`).
State and persistence: temp perf.data directory and output temp file are cleaned, with `glb_err` defaulting to failure until all checks pass.
Dependencies and integration: CoreSight decode, Python script path, objdump behavior, `/proc/kcore` for kernel decode.
Risks: branch mnemonic regex is heuristic; kernel test skips when kcore is unavailable.
Test signals: branch instruction text found in disassembly output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/test_arm_coresight_disasm.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/test_arm_spe.sh -->
## sources/distributed-fs/ceph-client/tools/perf/tests/shell/test_arm_spe.sh

Purpose: exclusive Arm SPE trace recording validation for snapshot, system-wide, and discard mode.
Important functions: `skip_if_no_arm_spe_event`, `arm_spe_report`, `perf_script_samples`, `perf_report_samples`, `arm_spe_snapshot_test`, `arm_spe_system_wide_test`, and `arm_spe_discard_test`.
Control flow: skips without `arm_spe_*//`, records snapshot and system-wide traces of `dd`, validates synthesized memory/cache/TLB/branch events in script/report, and tests discard mode by ensuring no AUX/AUXTRACE data remains.
State and persistence: temp perf.data is cleaned; `glb_err` accumulates failures.
Dependencies and integration: Arm SPE PMUs, taskset for discard CPU targeting, perf report/script synthesis.
Risks: event names in `events` regex must track `arm-spe.c`; discard support is optional per PMU instance.
Test signals: synthesized SPE samples present or absent according to mode.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/test_arm_spe.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/test_arm_spe_fork.sh -->
## sources/distributed-fs/ceph-client/tools/perf/tests/shell/test_arm_spe_fork.sh

Purpose: checks that Arm SPE recording does not hang when tracing a workload with forks/threads.
Important behavior: records `perf test -w sqrtloop 10` with `arm_spe/period=65536/ -vvv`, samples perf record log line counts after two one-second intervals, then kills perf.
Control flow: if log line count is unchanged between intervals, it reports a hang failure; otherwise pass.
State and persistence: temp perf.data and log are removed.
Dependencies and integration: Arm SPE PMU and verbose perf record progress output.
Risks: log growth is a proxy for liveness and can be flaky if output quiets naturally; kill/wait behavior assumes perf responds.
Test signals: increasing verbose log line count during recording.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/test_arm_spe_fork.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/test_bpf_metadata.sh -->
## sources/distributed-fs/ceph-client/tools/perf/tests/shell/test_bpf_metadata.sh

Purpose: verifies perf records BPF program metadata for BPF sample filters.
Important function: `test_bpf_metadata`.
Control flow: skips if `libbpf-strings` feature is unavailable, records a task-clock sample filter `ip > 0`, then parses `perf script --show-bpf-events` to find `PERF_RECORD_BPF_METADATA` for `perf_sample_filter` and a `perf_version` entry matching `perf version`.
State and persistence: temp perf.data is removed.
Dependencies and integration: BPF sample filter infrastructure, metadata strings compiled into perf BPF programs, and perf script BPF event display.
Risks: awk parser depends on current `perf script` formatting and entry indentation.
Test signals: metadata event contains current perf version string.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/test_bpf_metadata.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/test_brstack.sh -->
## sources/distributed-fs/ceph-client/tools/perf/tests/shell/test_brstack.sh

Purpose: validates branch stack sampling type/save information and symbolized branch stacks.
Important functions: `is_arm64`, `has_kaslr_bug`, `check_branches`, `test_user_branches`, plus kernel/any branch subtests in the same script.
Control flow: probes support for `--branch-filter any,save_type,u`, requires `brstack_bench`, records `perf test -w brstack`, checks symbolized branch pairs and branch types, then inspects raw branch addresses to ensure user-mode filtering excludes kernel targets.
State and persistence: temp directory holds perf.data, record logs, and script output.
Dependencies and integration: branch-stack PMU support, perf workload symbols, KASLR/address conventions, and script fields `brstacksym`/`brstack`.
Risks: architecture-specific address classification and KASLR bugs need special handling; branch type availability may differ by PMU.
Test signals: expected CALL/RET/IND_CALL/COND/UNCOND branch stack entries and absence of disallowed kernel addresses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/test_brstack.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/test_data_symbol.sh -->
## sources/distributed-fs/ceph-client/tools/perf/tests/shell/test_data_symbol.sh

Purpose: validates data symbol resolution for memory profiling events.
Important behavior: records a `datasym` workload with memory load/store events, then checks `perf report` or `perf script` output for the expected data symbol.
Control flow: chooses event/recording options based on architecture/PMU support, handles AMD IBS `mem-ldst` and `--ldlat` behavior, and uses verbose record logs for diagnostics.
State and persistence: temp perf.data and error log are cleaned.
Dependencies and integration: `perf mem`, data-symbol workload, CPU-specific memory sampling PMUs, and symbol resolution.
Risks: memory event names and latency controls vary by vendor and kernel; older AMD kernels have filtering limits requiring per-CPU mode.
Test signals: expected data symbol appears in decoded memory samples without record errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/test_data_symbol.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/test_event_open_fallback.sh -->
## sources/distributed-fs/ceph-client/tools/perf/tests/shell/test_event_open_fallback.sh

Purpose: tests perf's fallback behavior when opening events with high precise-IP requirements.
Important functions: `perf_record`, `test_decrease_precise_ip`, `test_decrease_precise_ip_complicated`, and `count_result`.
Control flow: records `cycles` and then `cycles:P`, expecting precision to decrease if needed; for systems with `mem-loads-aux`, records a grouped precise memory event combination.
State and persistence: no files; records to `/dev/null`.
Dependencies and integration: event parser/open fallback logic and PMU precise event support.
Risks: script calls `cleanup` near the end but no cleanup function is defined in this file, so if execution reaches that line in strict shells it may fail unless provided by environment; this is a maintenance risk.
Test signals: at least one subtest passes, otherwise all skip; any fallback failure exits `1`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/test_event_open_fallback.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/test_intel_pt.sh -->
## sources/distributed-fs/ceph-client/tools/perf/tests/shell/test_intel_pt.sh

Purpose: large exclusive Intel Processor Trace integration suite.
Important functions: `perf_record_no_decode`, `perf_record_no_bpf`, `can_cpu_wide`, `test_system_wide_side_band`, `can_kernel`, `test_per_thread`, `test_jitdump`, `test_packet_filter`, `test_disable_branch`, `test_time_cyc`, `test_sample`, `test_kernel_trace`, `test_virtual_lbr`, `test_power_event`, `test_no_tnt`, `test_event_trace`, `test_pipe`, `test_pause_resume`, and `count_result`.
Control flow: skips without `intel_pt//`, compiles helper workloads, validates sideband MMAP events, per-thread AUX mmap setup, JIT dump injection, packet filters, feature caps from sysfs, sample mode, virtual LBR, pipe mode, and pause/resume actions.
State and persistence: temp directory holds workloads, awk/Python scripts, perf data, stdout/stderr logs, and is path-checked before deletion.
Dependencies and integration: Intel PT PMU, compiler, libelf for JIT, sysfs caps, `waiting.sh`, taskset, perf inject/script/report.
Risks: hardware cap matrix is broad; compiled helper failures skip some paths; verbose log parsing and AWK fd validation are format-sensitive.
Test signals: accumulated ok/skip/error counters; any error fails, at least one ok passes, all skips exit `2`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/test_intel_pt.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/test_java_symbol.sh -->
## sources/distributed-fs/ceph-client/tools/perf/tests/shell/test_java_symbol.sh

Purpose: verifies Java JIT symbolization through perf's JVMTI agent and `perf inject -j`.
Important behavior: requires `jshell`, locates `libperf-jvmti.so` across source, installed, and prefix paths, records a jshell Fibonacci snippet with the JVMTI agent, injects JIT symbols, and reports them.
Control flow: missing jshell or JVMTI library skips; record/inject/report failures exit `1`.
State and persistence: temp perf.data and injected perf.data are cleaned.
Dependencies and integration: JDK/jshell, libperf-jvmti, perf record/inject/report, JIT symbol DSOs.
Risks: library path heuristics are distribution-specific; report regex assumes symbols like `Interpreter` or `jdk.internal`.
Test signals: report output contains percentage rows with Java/JIT symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/test_java_symbol.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/test_perf_data_converter_ctf.sh -->
## sources/distributed-fs/ceph-client/tools/perf/tests/shell/test_perf_data_converter_ctf.sh

Purpose: tests `perf data convert --to-ctf` for file and pipe-recorded perf.data.
Important functions: `check_babeltrace_support`, `test_ctf_converter_file`, and `test_ctf_converter_pipe`.
Control flow: skips if perf lacks libbabeltrace, records `noploop`, converts to a temp CTF directory with `--force`, and verifies the directory is non-empty; repeats after recording to stdout redirected to a file.
State and persistence: temp perf.data and CTF directory are removed.
Dependencies and integration: libbabeltrace support, perf data converter, and `noploop` workload.
Risks: only checks output existence, not CTF schema validity; pipe path still converts from a saved file, not direct stdin.
Test signals: non-empty CTF output directory for both modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/test_perf_data_converter_ctf.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/test_perf_data_converter_json.sh -->
## sources/distributed-fs/ceph-client/tools/perf/tests/shell/test_perf_data_converter_json.sh

Purpose: tests `perf data convert --to-json` for file and stdin input and validates JSON syntax.
Important functions: `test_json_converter_command`, `test_json_converter_pipe`, and `validate_json_format`.
Control flow: records `noploop`, converts the perf.data to JSON, checks non-empty output, validates with Python `json.load`, then repeats by piping a saved perf.data file to converter with `-i -`.
State and persistence: temp perf.data and JSON result are cleaned.
Dependencies and integration: Python, perf data converter, perf record, and `noploop`.
Risks: syntax validation does not check event content; cleanup uses quoted wildcard for perfdata companions and may not remove `.old`.
Test signals: non-empty valid JSON after each conversion mode.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/test_perf_data_converter_json.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/test_stat_intel_tpebs.sh -->
## sources/distributed-fs/ceph-client/tools/perf/tests/shell/test_stat_intel_tpebs.sh

Purpose: tests Intel TPEBS counting mode through `perf stat --record-tpebs`.
Important functions: `ParanoidAndNotRoot` and `test_with_record_tpebs`.
Control flow: skips non-Intel, non-root with paranoid restrictions, and missing precise `cache-misses` support; then runs `perf stat -e cache-misses:R --record-tpebs -a sleep 0.01` and checks output for embedded perf record messages and event name.
State and persistence: temp stat output is removed.
Dependencies and integration: Intel precise event support, system-wide stat, and TPEBS record integration.
Risks: event name may print as either `cache-misses:R` or PMU slash form; permissions heavily gate coverage.
Test signals: output contains `perf record` and the requested retired precise event.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/test_stat_intel_tpebs.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/test_task_analyzer.sh -->
## sources/distributed-fs/ceph-client/tools/perf/tests/shell/test_task_analyzer.sh

Purpose: exercises `perf script report task-analyzer` output modes and CSV exports.
Important functions: `report`, `check_exec_0`, `find_str_or_fail`, `skip_no_probe_record_support`, `prepare_perf_data`, and test cases for basic, namespace/rename, milliseconds/filter/highlight, extended times, summaries, CSV, and CSV summary.
Control flow: records sched_switch system-wide for one second to `perf.data` in CWD, then runs task-analyzer variants and greps required headers/fields.
State and persistence: uses `perf.data` in current directory plus a temp output directory; cleanup removes both.
Dependencies and integration: libtraceevent, Python script report infrastructure, sched tracepoints, and ASAN leak suppression.
Risks: fixed `perf.data` name can collide with user files if run in an unsafe directory; output header strings are format-sensitive.
Test signals: expected labels like `Comm`, `Out-Out`, `Summary`, and CSV semicolon headers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/test_task_analyzer.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/test_uprobe_from_different_cu.sh -->
## sources/distributed-fs/ceph-client/tools/perf/tests/shell/test_uprobe_from_different_cu.sh

Purpose: verifies `perf probe` can find and add a uprobe for a function defined in a different compilation unit.
Important behavior: generates a header, `foo.c`, and `main.c`, compiles with debug info and LTO for `foo.o`, links an executable, lists functions matching `foo`, and adds a uprobe on `foo`.
Control flow: requires perf probe, root, and gcc; cleanup deletes the probe and temp build tree.
State and persistence: creates temporary source/object/binary files and a perf uprobe event on the generated binary.
Dependencies and integration: gcc debug info, LTO, perf probe CU lookup.
Risks: LTO/debug behavior can vary across compiler versions; cleanup must delete the probe before removing binary.
Test signals: `perf probe -x testfile --funcs foo` finds `foo` and `perf probe -x testfile foo` succeeds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/test_uprobe_from_different_cu.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/timechart.sh -->
## sources/distributed-fs/ceph-client/tools/perf/tests/shell/timechart.sh

Purpose: smoke test for `perf timechart record` and SVG generation.
Important function: `test_timechart`.
Control flow: skips if libtraceevent is missing, tries `perf timechart record -o perfdata true`, then runs `perf timechart -i perfdata -o output.svg` and checks the file is non-empty and contains `svg`.
State and persistence: temp perf.data and SVG output are cleaned.
Dependencies and integration: timechart tracepoints, libtraceevent, SVG output path.
Risks: record failures are treated as skipped inside the test function without setting `err`; permissions and tracepoint availability dominate.
Test signals: generated non-empty SVG-looking file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/timechart.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/top.sh -->
## sources/distributed-fs/ceph-client/tools/perf/tests/shell/top.sh

Purpose: tests noninteractive `perf top --stdio` against a spinning workload.
Important function: `test_basic_perf_top`.
Control flow: starts `perf test -w thloop 20`, runs `timeout 5s perf top --stdio -d 1 -e cpu-clock -p PID` with stdin held open by `sleep`, kills the workload, then greps output for percentages and `test_loop`.
State and persistence: temp log file and background workload PID are cleaned.
Dependencies and integration: `timeout`, `perf top`, cpu-clock sampling, `thloop` symbol.
Risks: sample availability can be timing-sensitive; timeout exit `124` is accepted as expected.
Test signals: log includes percentage rows and the `test_loop` symbol.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/top.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/trace+probe_vfs_getname.sh -->
## sources/distributed-fs/ceph-client/tools/perf/tests/shell/trace+probe_vfs_getname.sh

Purpose: validates `perf trace` uses the `vfs_getname` probe to beautify open filename arguments.
Important function: `trace_open_vfs_getname`.
Control flow: requires perf probe/trace and root, adds the shared probe, builds an event list from available open/openat tracepoints, disables user perf config, runs `perf trace -e events touch $file`, and greps for a formatted open call containing the temp filename and flags.
State and persistence: temp file and added probe are cleaned.
Dependencies and integration: `lib/probe.sh`, `lib/probe_vfs_getname.sh`, syscall tracepoints, and perf trace argument beautifier.
Risks: output formatting and flag names are strict; available syscall tracepoint names vary by kernel.
Test signals: matching open/openat trace line with correct filename and mode/flags.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/trace+probe_vfs_getname.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/trace_btf_enum.sh -->
## sources/distributed-fs/ceph-client/tools/perf/tests/shell/trace_btf_enum.sh

Purpose: tests BTF enum augmentation in `perf trace` for syscall and tracepoint arguments.
Important functions: `check_vmlinux`, `check_permissions`, `trace_landlock`, and `trace_non_syscall`.
Control flow: requires perf trace, root, and `/sys/kernel/btf/vmlinux`; traces `landlock_add_rule` using the `landlock` perf workload when available, then traces `timer:hrtimer_start --max-events=1` and expects enum names such as `LANDLOCK_RULE_*` and `HRTIMER_MODE_*`.
State and persistence: no temp files.
Dependencies and integration: BTF vmlinux, landlock workload/syscall, timer tracepoint, perf trace enum decoding.
Risks: landlock may be absent and is skipped to non-syscall path; permissions can skip.
Test signals: augmented enum names appear in trace output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/trace_btf_enum.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/trace_btf_general.sh -->
## sources/distributed-fs/ceph-client/tools/perf/tests/shell/trace_btf_general.sh

Purpose: tests general BTF-based argument augmentation in `perf trace`.
Important functions: `check_vmlinux`, `trace_config`, `trace_test_string`, `trace_test_buffer`, `trace_test_struct_btf`, and cleanup handlers.
Control flow: creates two temp files and a private perf config, disables display decorations, traces `mv` renameat string arguments, `echo` write buffer contents, and `sleep` clock_nanosleep struct arguments with `--force-btf`.
State and persistence: temp files and temp config are removed.
Dependencies and integration: perf trace, root, BTF vmlinux, syscall tracepoints, and configurable trace formatting.
Risks: regexes depend on exact argument formatting; cleanup trap is installed before cleanup function definition but resolves at runtime in shell.
Test signals: trace output includes decoded strings, buffer content, and timespec-like struct.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/trace_btf_general.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/trace_exit_race.sh -->
## sources/distributed-fs/ceph-client/tools/perf/tests/shell/trace_exit_race.sh

Purpose: regression test that `perf trace` does not lose final `exit_group` events from short-lived subprocesses.
Important function: `trace_shutdown_race`.
Control flow: requires perf trace and root, disables user perf config, runs `perf trace --no-comm -e syscalls:sys_enter_exit_group true` ten times appending to a temp file, then counts lines matching the expected timestamp/PID tracepoint regex.
State and persistence: temp output and optional verbose mismatch file are removed.
Dependencies and integration: syscall tracepoint and trace shutdown flushing.
Risks: strict output regex can be affected by config unless `PERF_CONFIG=/dev/null` is honored; test is race-sensitive by design.
Test signals: exactly ten matching exit_group trace lines.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/trace_exit_race.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/trace_record_replay.sh -->
## sources/distributed-fs/ceph-client/tools/perf/tests/shell/trace_record_replay.sh

Purpose: smoke test for `perf trace record` followed by offline replay.
Important behavior: requires perf trace and root, records `sleep 1` to a temp file, then runs `perf trace -i` and greps for `nanosleep`.
Control flow: direct command failures exit `1`; missing trace support/root skip with code `2`.
State and persistence: temp trace perf.data file is removed after replay.
Dependencies and integration: trace record format and offline trace decoding.
Risks: syscall name can vary (`clock_nanosleep` vs nanosleep patterns), but grep uses broad `nanosleep`.
Test signals: replay output contains a nanosleep syscall.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/trace_record_replay.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/trace_summary.sh -->
## sources/distributed-fs/ceph-client/tools/perf/tests/shell/trace_summary.sh

Purpose: validates `perf trace` summary modes, including BPF and cgroup summaries.
Important function: `test_perf_trace`.
Control flow: requires perf trace and root, runs process and system-wide summary variants (`-s`, `-S`, summary-mode thread/total), then if BPF support is present runs BPF summary variants including cgroup mode. Each invocation checks for at least three summary rows matching open/read/close with percentages.
State and persistence: one temp output file is removed.
Dependencies and integration: syscall tracing, summary aggregation, optional libbpf/BPF summary support.
Risks: expected syscalls for `true` can vary by libc/kernel; system-wide mode uses `--no-bpf-summary` until BPF gate.
Test signals: count of matching summary rows equals three for each mode.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/trace_summary.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/sigtrap.c -->
## sources/distributed-fs/ceph-client/tools/perf/tests/sigtrap.c

Purpose: C unit/integration test for synchronous `SIGTRAP` delivery from perf breakpoint events.
Important APIs/types/functions: `make_event_attr`, optional BTF helpers `attr_has_sigtrap` and `kernel_with_sleepable_spinlocks`, `sigtrap_handler`, `test_thread`, `run_test_threads`, `run_stress_test`, and `test__sigtrap`.
Control flow: installs a SA_SIGINFO SIGTRAP handler, opens a breakpoint event on `ctx.iterate_on` with `inherit_thread`, `remove_on_exec`, `sigtrap`, and `sig_data`, starts five threads, enables the event, and verifies each atomic access triggers a signal.
State and persistence: global `ctx` tracks expected TID signal debt, count, breakpoint target, and first siginfo; BTF handle is cached and freed.
Dependencies and integration: `sys_perf_event_open`, hw breakpoint support, pthreads, atomics, BTF when available, and `BP_SIGNAL_IS_SUPPORTED` from `tests.h`.
Risks: RT kernels with sleepable spinlocks may miss signals and are skipped; libc may lack exposed `si_perf_*` fields.
Test signals: exact signal count, zero remaining TID debt, expected `si_addr`, or skip for unsupported kernel/architecture.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/sigtrap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/stat.c -->
## sources/distributed-fs/ceph-client/tools/perf/tests/stat.c

Purpose: unit tests for synthetic perf stat metadata events.
Important functions: `has_term`, `process_stat_config_event`, `test__synthesize_stat_config`, `process_stat_event`, `test__synthesize_stat`, `process_stat_round_event`, and `test__synthesize_stat_round`.
Control flow: constructs `perf_stat_config` and `perf_counts_values`, synthesizes stat config/stat/stat round records, and validates callback event payload fields.
State and persistence: no persistent state; all data is stack-local synthetic event content.
Dependencies and integration: `perf_event__synthesize_stat_config`, `perf_event__read_stat_config`, `perf_event__synthesize_stat`, and `perf_event__synthesize_stat_round`.
Risks: tests assume the enum count `PERF_STAT_CONFIG_TERM__MAX` and exact AGGR_CORE/scale/interval values; note `process_stat_event` labels `ena`/`run` assertion messages inversely to fields.
Test signals: three suites registered with `DEFINE_SUITE` return success when synthesized payloads match expected values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/stat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/subcmd-help.c -->
## sources/distributed-fs/ceph-client/tools/perf/tests/subcmd-help.c

Purpose: unit tests for libsubcmd command-name list helpers.
Important functions: `test__load_cmdnames`, `test__uniq_cmdnames`, `test__exclude_cmdnames`, and `test__exclude_cmdnames_no_overlap`.
Control flow: creates `struct cmdnames` lists, adds names, checks lookup case-sensitivity, removes adjacent duplicates via `uniq`, and excludes overlapping names between lists.
State and persistence: heap allocations inside cmdname helpers are released with `clean_cmdnames`.
Dependencies and integration: `<subcmd/help.h>` APIs `add_cmdname`, `is_in_cmdlist`, `uniq`, `exclude_cmds`, and `clean_cmdnames`.
Risks: `uniq` assumes sorted input; tests use already-adjacent duplicates and do not cover unsorted behavior.
Test signals: suite `libsubcmd help tests` contains four test cases with count and membership assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/subcmd-help.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/sw-clock.c -->
## sources/distributed-fs/ceph-client/tools/perf/tests/sw-clock.c

Purpose: verifies software clock sampling periods are meaningful under frequency mode and not all forced to period `1`.
Important functions: `__test__sw_clock_freq` and `test__sw_clock_freq`.
Control flow: builds an evlist with `PERF_TYPE_SOFTWARE` cpu-clock or task-clock, sample frequency 500, current TID map and any CPU map, opens/mmaps/enables it, spins for `NR_LOOPS`, disables, reads samples, sums `PERF_SAMPLE_PERIOD`, and fails if total periods equals sample count.
State and persistence: local evlist/evsel/cpu/thread maps and mmap buffers are cleaned.
Dependencies and integration: perf evlist/evsel APIs, mmap sample parsing, `/proc/sys/kernel/perf_event_max_sample_rate` hint.
Risks: insufficient samples or open/mmap permission failures return negative errors; tight spin duration may be system-sensitive.
Test signals: both CPU_CLOCK and TASK_CLOCK paths produce period sums not equal to all ones.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/sw-clock.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/switch-tracking.c -->
## sources/distributed-fs/ceph-client/tools/perf/tests/switch-tracking.c

Purpose: exclusive integration test for mixed tracking events, sched_switch system-wide events, and enabling/disabling sampled events.
Important types/functions: `struct switch_tracking`, `spin_sleep`, `check_comm`, `check_cpu`, `process_sample_event`, `process_event`, `add_event`, `process_events`, and `test__switch_tracking`.
Control flow: creates thread/CPU maps, parses cpu-clock/cycles, adds sched_switch, moves cycles to front, adds dummy tracking event, configures sampling, opens/mmaps, changes process comm four times while toggling cycles, then reads all mmap events sorted by timestamp.
State and persistence: `switch_tracking` tracks per-CPU current TIDs, seen COMM events, and whether cycles appeared before/between/after comm phases.
Dependencies and integration: evlist ordering/config, sched_switch fields `next_pid`/`prev_pid`, tracking COMM synthesis, sample time/CPU/id parsing, and PR_SET_NAME.
Risks: missing sched_switch support causes skip-like success; event ordering is reconstructed from timestamps and can fail if samples lack time.
Test signals: all four COMM events seen, no missing sched_switch transitions, cycles present only while enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/switch-tracking.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/symbols.c -->
## sources/distributed-fs/ceph-client/tools/perf/tests/symbols.c

Purpose: validates loaded DSO function symbols are non-overlapping and non-zero length.
Important types/functions: `struct test_info`, `init_test_info`, `exit_test_info`, `find_module_map`, `get_test_dso_filename`, `create_map`, `test_dso`, `process_subdivided_dso`, `test_file`, and `test__symbols`.
Control flow: initializes a host machine/thread, chooses `dso_to_test` or current perf executable, creates a map for user DSO or finds existing kernel module map, loads symbols, walks cached symbol rb-tree, and checks function/ifunc ranges.
State and persistence: perf environment, machine, thread, map, and DSO refs are created and released.
Dependencies and integration: machine/dso/map/symbol loader APIs, optional kernel module subdivision handling.
Risks: no symbols results in skip; kernel module DSOs can split into section DSOs requiring secondary validation.
Test signals: no overlapping or zero-length function symbols in tested DSO(s).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/symbols.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/task-exit.c -->
## sources/distributed-fs/ceph-client/tools/perf/tests/task-exit.c

Purpose: verifies perf receives exactly one `PERF_RECORD_EXIT` for a simple workload.
Important functions: `sig_handler`, `workload_exec_failed_signal`, and `test__task_exit`.
Control flow: creates a dummy evlist, prepares workload `true`, enables task events and sample parameters, opens/mmaps, starts workload, polls/reads mmap data until child exits and an exit event is seen, then validates `nr_exit == 1`.
State and persistence: globals `exited` and `nr_exit` track SIGCHLD/exec failure and exit event count; evlist maps monitor a prepared workload.
Dependencies and integration: evlist workload preparation/start, SIGCHLD handling, perf mmap event reading, and task event attr.
Risks: retries up to 1000 polls; s390x uses higher sample frequency; exec failure sets `nr_exit=-1`.
Test signals: exactly one `PERF_RECORD_EXIT`; suite is marked exclusive.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/task-exit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/tests-scripts.c -->
## sources/distributed-fs/ceph-client/tools/perf/tests/tests-scripts.c

Purpose: discovers shell test scripts and converts them into perf `struct test_suite` instances.
Important functions: `shell_tests__dir_fd`, `shell_test__description`, `is_shell_script`, `is_test_script`, `strdup_check`, `shell_test__run`, `append_script`, `append_scripts_in_dir`, and `create_script_test_suites`.
Control flow: locates tests/shell in source, executable, or installed paths; recursively scans sorted directories excluding hidden and `base_*`; extracts description from comments after shebang; marks tests with `(exclusive)` in description; stores absolute `/proc/self/fd`-resolved path in suite private data; runs scripts through `system`.
State and persistence: dynamically allocated suite/test arrays and strings are returned NULL-terminated; scripts map shell exit `2` to `TEST_SKIP`.
Dependencies and integration: directory fd APIs, perf test harness structs, shell script executable/read bits, and `verbose` flag.
Risks: recursive fd open lacks explicit error handling for failed subdir opens; generated suite memory ownership must be handled by caller.
Test signals: discovered scripts appear as perf test cases with correct descriptions/exclusive flags and status mapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/tests-scripts.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/tests-scripts.h -->
## sources/distributed-fs/ceph-client/tools/perf/tests/tests-scripts.h

Purpose: header declaring shell script test-suite discovery.
Important API: `struct test_suite **create_script_test_suites(void);`.
Control flow: no executable code; included by harness code that wants dynamic shell test suites.
State and persistence: returned array ownership is defined by implementation rather than the header.
Dependencies and integration: forward-declares `struct test_suite` and includes only the guard.
Risks: minimal header gives no lifetime contract for returned suites; callers must know implementation conventions.
Test signals: compile-time integration with `tests-scripts.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/tests-scripts.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/tests.h -->
## sources/distributed-fs/ceph-client/tools/perf/tests/tests.h

Purpose: central perf test harness declarations, assertion macros, suite registration macros, architecture gates, and workload declarations.
Important APIs/types/macros: `TEST_OK/FAIL/SKIP`, `TEST_ASSERT_VAL`, `TEST_ASSERT_EQUAL`, `struct test_case`, `struct test_suite`, `DECLARE_SUITE`, `TEST_CASE*`, `DEFINE_SUITE*`, `BP_SIGNAL_IS_SUPPORTED`, `struct test_workload`, `DECLARE_WORKLOAD`, and `DEFINE_WORKLOAD`.
Control flow: macros generate static test case arrays and suite objects around `test__name` functions; many `DECLARE_SUITE` entries expose suites defined across the tests directory.
State and persistence: no runtime state in the header, but it declares globals `dso_to_test` and `test_objdump_path`.
Dependencies and integration: used by nearly every C test file and harness registry.
Risks: assertion macros return immediately, so cleanup must be done before or via structured goto in tests; architecture gate disables breakpoint signal tests on several architectures.
Test signals: compile-time suite wiring and consistent result codes for the harness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/tests.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/thread-map.c -->
## sources/distributed-fs/ceph-client/tools/perf/tests/thread-map.c

Purpose: unit tests for thread map creation, synthesis, and removal.
Important functions: `test__thread_map`, `process_event`, `test__thread_map_synthesize`, and `test__thread_map_remove`.
Control flow: sets current process name to `perf`, creates a map by current PID and a dummy map, reads comms and validates pid/comm/refcount; synthesizes a thread map event and reconstructs it; creates a two-PID map and removes entries until empty, then verifies extra removal fails.
State and persistence: temporary `perf_thread_map` objects are refcounted and freed.
Dependencies and integration: thread map APIs, PR_SET_NAME, synthetic event callback path.
Risks: process name mutation affects current process during test; verbose output can print maps to stderr.
Test signals: three suites for thread map, synthesize thread map, and remove thread map return success on correct counts/refcounts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/thread-map.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/thread-maps-share.c -->
## sources/distributed-fs/ceph-client/tools/perf/tests/thread-maps-share.c

Purpose: verifies threads in the same process share `struct maps` and reference counts are maintained.
Important function: `test__thread_maps_share`.
Control flow: initializes machines, creates a process with leader and three threads plus another process missing its explicit leader, checks map pointer equality/refcounts, removes threads from machine rbtrees, then releases refs one by one while validating counts.
State and persistence: host machine/thread objects and map refs are created and destroyed within the test.
Dependencies and integration: `machine__findnew_thread`, `thread__maps`, `maps__refcnt`, `maps__equal`, and `thread__put`.
Risks: relies on machine behavior that creates an implicit leader for process 4; refcount expectations are exact.
Test signals: correct shared maps and decrementing refcounts across thread releases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/thread-maps-share.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/time-utils-test.c -->
## sources/distributed-fs/ceph-client/tools/perf/tests/time-utils-test.c

Purpose: unit tests for parsing absolute and percentage-based perf time ranges.
Important types/functions: `struct test_data`, `test__parse_nsec_time`, `test__perf_time__parse_str`, `test__perf_time__parse_for_ranges`, and `test__time_utils`.
Control flow: validates nanosecond conversion from decimal seconds, parses explicit start/end ranges, then constructs synthetic sessions with first/last sample times to test percentage slices and `perf_time__ranges_skip_sample`.
State and persistence: heap-allocated range arrays from `perf_time__parse_for_ranges` are freed per case.
Dependencies and integration: `parse_nsec_time`, `perf_time__parse_str`, `perf_time__parse_for_ranges`, `perf_time__ranges_skip_sample`, and `perf_session`/`evlist` first-last sample metadata.
Risks: boundary expectations are exact and cover inclusive endpoints; overflow-edge value uses max u64 decimal.
Test signals: all explicit/percentage ranges parse and skip/keep sample timestamps as expected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/time-utils-test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/tool_pmu.c -->
## sources/distributed-fs/ceph-client/tools/perf/tests/tool_pmu.c

Purpose: unit tests for parsing tool PMU events with and without explicit `tool/` PMU name.
Important functions: `do_test`, `test__tool_pmu_without_pmu`, and `test__tool_pmu_with_pmu`.
Control flow: iterates `tool_pmu__for_each_event`, builds either `tool/<event>/` or bare event strings, parses them into an evlist, validates event count, finds an evsel whose PMU is tool PMU, and checks attr config equals the enum value.
State and persistence: evlist and parse error objects are allocated and freed per event.
Dependencies and integration: parser, `tool_pmu__event_to_str`, `perf_pmu__is_tool`, and evsel attr config.
Risks: events with no string are expected to fail parse and count as OK; bare names may parse to additional aliases, so only at least one event is required.
Test signals: suite `Tool PMU` has two cases covering explicit and implicit PMU naming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/tool_pmu.c -->
