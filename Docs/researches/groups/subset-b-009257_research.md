# subset-b-009257 research

Grouped research report for kdevops monitoring, NFS, SMB, pynfs/nfstest, selftests, reboot-limit, RDMA software device, Nix cache mirror, package, postfix relay, and steady-state role files. Each section preserves the exact source path and is wrapped for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/monitoring/files/fragmentation_snapshot.py -->
# sources/test-tools/kdevops/playbooks/roles/monitoring/files/fragmentation_snapshot.py

Purpose: creates an interim memory-fragmentation snapshot without losing ongoing monitoring continuity. It stops the running tracker with SIGINT so the tracker writes a valid JSON file, copies the latest `fragmentation_data*.json` to `fragmentation_snapshot.json`, then starts a fresh tracker instance in `/opt/fragmentation`.

Important APIs/types/functions: `get_pid_from_file()`, `is_process_running()`, `stop_tracker_and_save()`, `find_latest_json()`, `start_new_tracker()`, `create_snapshot()`, `main()`.

Control flow: `main()` validates the output directory argument, `create_snapshot()` reads `fragmentation_tracker.pid`, verifies the process with `os.kill(pid, 0)`, calls `stop_tracker_and_save()`, finds the newest data JSON, writes the snapshot, and launches `fragmentation_tracker.py -o fragmentation_data_<timestamp>.json` with stdout/stderr appended to the tracker log.

State and persistence behavior: Persists `fragmentation_snapshot.json`, a new timestamped data file, `fragmentation_tracker.log`, and an updated `fragmentation_tracker.pid` in the configured output directory. It intentionally copies rather than renames the last complete tracker output.

Dependencies and integration points: Called by `monitor_collect_only.yml` on target hosts. Depends on Python 3, process signals, `/opt/fragmentation/fragmentation_tracker.py`, and root-accessible monitoring output paths.

Risks: The wait for tracker exit is unbounded, stale PID reuse is only checked by signalability, and `find_latest_json()` may select an older complete file if the tracker fails before writing. Starting a new process has no post-start health check.

Test signals: Useful signals are `no_pid_file`, `not_running`, `no_json_found`, creation of valid JSON, PID rollover, and continued tracker logging after snapshot.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/monitoring/files/fragmentation_snapshot.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/monitoring/files/fragmentation_tracker.py -->
# sources/test-tools/kdevops/playbooks/roles/monitoring/files/fragmentation_tracker.py

Purpose: runs the eBPF side of memory fragmentation monitoring, centered on the `kmem:mm_page_alloc_extfrag` tracepoint with optional compaction tracepoints. It converts kernel perf events into JSON event records and summary statistics for later visualization.

Important APIs/types/functions: class `FragmentationTracker` with methods `__init__`, `process_event`, `print_summary`, `save_data`, `run`, `main()`.

Control flow: `main()` enforces root, parses `--output`, `--time`, and `--quiet`, installs a SIGINT handler, and starts `FragmentationTracker.run()`. `run()` conditionally enables compaction tracepoint probes, compiles the BCC program, opens the perf buffer, polls until interrupted or timed out, then always prints and saves data. `process_event()` maps raw BPF structs into extfrag, compaction success, or compaction failure dictionaries.

State and persistence behavior: Keeps in-memory `events_data`, per-order extfrag counts, and per-order compaction success/failure counts. On exit it writes metadata, events, and statistics JSON including start/end time, duration, total events, and kernel release.

Dependencies and integration points: Depends on BCC Python bindings, kernel tracepoints, debugfs tracing paths, root privileges, and the monitoring Ansible role that copies it to `/opt/fragmentation` and controls its lifetime.

Risks: Tracepoint field names can vary by kernel, node/zone data for extfrag is placeholder `-1`, SIGTERM from `timeout` may not use the graceful save path, and long runs can retain all events in memory. Compaction support depends on tracepoints existing under debugfs.

Test signals: Test by running as root against a kernel with `mm_page_alloc_extfrag`, checking quiet/timed modes, SIGINT save behavior, parseable JSON schema, nonzero stats under allocation pressure, and graceful behavior when compaction tracepoints are absent.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/monitoring/files/fragmentation_tracker.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/monitoring/files/fragmentation_visualizer.py -->
# sources/test-tools/kdevops/playbooks/roles/monitoring/files/fragmentation_visualizer.py

Purpose: renders detailed single-run and A/B memory-fragmentation dashboards from tracker JSON. It tolerates partially written JSON, visualizes extfrag timelines, compaction events, migration patterns, heatmaps, and comparison summary tables.

Important APIs/types/functions: `load_data()`, `recover_events_line_by_line()`, `get_dot_size()`, `build_counts()`, `get_migrate_type_color()`, `get_migration_severity()`, `get_severity_color()`, `create_overlaid_compaction_graph()`, `create_overlaid_extfrag_timeline()`, `create_combined_migration_heatmap()`, `create_comparison_statistics_table()`, `create_single_dashboard()`, `create_single_migration_heatmap()`, `create_comparison_dashboard()`, `main()`.

Control flow: `main()` loads the primary JSON through `load_data()`, optionally loads `--compare`, then calls `create_single_dashboard()` or `create_comparison_dashboard()`. Dashboard helpers bin events by time, color migratetype transitions, score migration severity, build heatmaps, and save matplotlib figures. JSON recovery falls back from normal parsing to truncation-aware and line-by-line event extraction.

State and persistence behavior: Reads JSON monitoring artifacts and writes PNG output only. It does not mutate source monitoring data. It uses derived arrays and count tables in memory for plotting.

Dependencies and integration points: Depends on matplotlib, numpy, JSON generated by `fragmentation_tracker.py`, and is invoked on targets for single-run plots and on localhost through comparison scripts.

Risks: Large event streams can consume substantial memory and plotting time. Recovery can salvage events but may silently drop malformed tail data. Several visual semantics rely on tracker event keys, so schema drift breaks panels. Some comparison labels infer filesystem identity from filenames.

Test signals: Useful checks are valid output PNGs for full JSON, truncated JSON recovery, single and compare modes, empty-event handling, expected migration-color mapping, and no crash when compaction events are missing.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/monitoring/files/fragmentation_visualizer.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/monitoring/scripts/folio_migration_compare.py -->
# sources/test-tools/kdevops/playbooks/roles/monitoring/scripts/folio_migration_compare.py

Purpose: creates localhost comparison plots for folio migration stats collected from multiple kdevops hosts or filesystem configurations.

Important APIs/types/functions: `parse_stats_file()`, `get_node_label()`, `generate_comparison_plot()`, `generate_all_comparisons()`, `main()`.

Control flow: `generate_all_comparisons()` searches a monitoring result tree for `*_folio_migration_stats*.txt`, groups them into all-host and baseline/dev comparisons, then `generate_comparison_plot()` parses cumulative success counters and writes PNG charts.

State and persistence behavior: Reads copied text stats and writes `folio_migration_comparison*.png` artifacts in the monitoring results directory. It keeps only transient parsed series in memory.

Dependencies and integration points: Depends on matplotlib, numpy, regex parsing of debugfs-style migrate_folio stats, and `visualize.yml` or interim collection tasks.

Risks: Parsing assumes `calls` and `success` lines in each timestamped block. Filename-derived labels can misclassify new workflow naming. Missing or sparse files produce skipped plots.

Test signals: Signals include successful parsing of several timestamp formats, generated all-host and A/B plots, empty-directory no-op behavior, and labels matching baseline/dev host names.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/monitoring/scripts/folio_migration_compare.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/monitoring/scripts/fragmentation_ab_compare.py -->
# sources/test-tools/kdevops/playbooks/roles/monitoring/scripts/fragmentation_ab_compare.py

Purpose: generates multi-panel A/B comparison plots for fragmentation tracker output, emphasizing extfrag counts, migration pages, compaction success, fragmentation index, and migration-focused summaries.

Important APIs/types/functions: `load_fragmentation_data()`, `extract_all_metrics()`, `get_node_label()`, `generate_ab_comparison()`, `generate_migration_focus_plot()`, `generate_all_comparisons()`, `main()`.

Control flow: Loads JSON event lists, bins activity into 60-second windows in `extract_all_metrics()`, derives labels from filenames, and builds comprehensive or migration-focused matplotlib figures. `generate_all_comparisons()` scans monitoring results and emits all-data and pairwise comparison plots.

State and persistence behavior: Purely derived output: reads `*_fragmentation_data*.json` and writes PNG comparison files. No target state is changed.

Dependencies and integration points: Depends on matplotlib, numpy, and tracker JSON. Integrated from `visualize.yml` and complements the richer `fragmentation_visualizer.py` comparison mode.

Risks: The metric extractor expects event types such as `migration` and `compaction` that are not always produced by the current tracker, so some panels can be empty for extfrag-only runs. Labeling and color assignment depend on filename conventions.

Test signals: Exercise extfrag-only JSON, mixed migration/compaction JSON, two-file pair comparisons, multi-file comparisons, parse failures, and generated output existence.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/monitoring/scripts/fragmentation_ab_compare.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/monitoring/scripts/fragmentation_compare.py -->
# sources/test-tools/kdevops/playbooks/roles/monitoring/scripts/fragmentation_compare.py

Purpose: legacy/simple fragmentation comparison script. It extracts extfrag event counts over time and delegates users toward `fragmentation_ab_compare.py` for richer analysis.

Important APIs/types/functions: `load_fragmentation_data()`, `extract_fragmentation_metrics()`, `get_node_label()`, `generate_comparison_plot()`, `generate_all_comparisons()`, `main()`.

Control flow: `generate_all_comparisons()` finds fragmentation JSON files, `extract_fragmentation_metrics()` filters external fragmentation events into time/count arrays, and `generate_comparison_plot()` can render line graphs though the code marks it deprecated.

State and persistence behavior: Reads JSON and writes comparison PNGs under the monitoring results tree. It does not modify source data.

Dependencies and integration points: Depends on matplotlib, numpy, JSON output from the tracker, and `visualize.yml` still invokes it before the A/B script.

Risks: The line graph is explicitly described as not very useful, and it only reflects extfrag event occurrence rather than severity or migratetype transitions. Bad JSON is skipped with a warning.

Test signals: Validate no-op behavior with no files, parse warnings for malformed JSON, and plot output for multiple non-empty fragmentation data files.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/monitoring/scripts/fragmentation_compare.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/monitoring/scripts/generate_fragmentation_comparisons.py -->
# sources/test-tools/kdevops/playbooks/roles/monitoring/scripts/generate_fragmentation_comparisons.py

Purpose: orchestrates higher-quality fragmentation comparisons by selecting likely baseline/dev JSON pairs and invoking `fragmentation_visualizer.py` in compare mode.

Important APIs/types/functions: `find_first_matching_file()`, `generate_comparison()`, `main()`.

Control flow: `main()` scans a fragmentation results directory for filesystem-patterned files, picks first matching files, and calls `generate_comparison()` for ext4 versus XFS, baseline versus dev, and other named comparisons. `generate_comparison()` shells out to the visualizer with `--compare` and `-o`.

State and persistence behavior: Reads existing JSON files and writes comparison PNGs. It reports subprocess failures but does not change collected data.

Dependencies and integration points: Depends on Python subprocess execution, glob/path matching, and a valid visualizer path passed by `monitor_collect.yml`.

Risks: First-match selection can compare unintended hosts when multiple runs are present. Pair discovery is filename-convention-heavy. A visualizer failure surfaces only as comparison-generation output unless callers inspect return codes.

Test signals: Test with synthetic directories containing ext4/XFS/baseline/dev filenames, missing pair cases, explicit `--visualizer`, and command failure handling.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/monitoring/scripts/generate_fragmentation_comparisons.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/monitoring/tasks/common/setup.yml -->
# sources/test-tools/kdevops/playbooks/roles/monitoring/tasks/common/setup.yml

Purpose: shared setup for monitoring collection. It resolves a workflow-specific local monitoring results path and creates the delegated localhost directory when monitoring is enabled.

Important APIs/types/functions: modules `ansible.builtin.debug`, `ansible.builtin.set_fact`, `ansible.builtin.file`; variables/facts `msg`, `monitor_developmental_stats`, `monitor_folio_migration`, `enable_monitoring`, `kdevops_run_fstests`, `kdevops_run_blktests`, `kdevops_workflow_enable_sysbench`, `monitoring_results_path`; tasks `Debug monitoring collection start`, `Set workflow-appropriate monitoring results path`, `Create local monitoring results directory`.

Control flow: Runs a debug task showing monitor flags, sets `monitoring_results_path` to `{{ topdir_path }}/workflows/{{ kdevops_workflow_name }}/results/monitoring`, then creates the directory once on localhost.

State and persistence behavior: Persists only the localhost results directory. The path fact is consumed by later fetch and visualization tasks.

Dependencies and integration points: Imported by monitor collection entrypoints before folio or fragmentation collectors. Depends on `topdir_path`, `kdevops_workflow_name`, and monitor enable flags.

Risks: The directory creation is skipped unless enable flags align; later tasks also reset the path in places, so inconsistent path logic can split outputs.

Test signals: Ansible parseability, debug output with expected booleans, and created localhost directory are the main test signals.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/monitoring/tasks/common/setup.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/monitoring/tasks/install-deps/centos/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/monitoring/tasks/install-deps/centos/main.yml

Purpose: installs monitoring runtime dependencies on centos targets, split between common Python plotting support, folio migration support, and memory fragmentation eBPF support.

Important APIs/types/functions: modules `ansible.builtin.yum`; variables/facts `become_method`; tasks `Install monitoring Python dependencies`, `Install folio migration monitoring dependencies`, `Install memory fragmentation monitoring dependencies`.

Control flow: Uses the `yum` module to install Python 3, matplotlib/numpy-style plotting packages, `stress-ng` for folio migration workloads, and BCC/eBPF packages when the corresponding monitor flags are enabled. Debian updates apt cache first.

State and persistence behavior: Mutates system package state only; no monitoring data is created here.

Dependencies and integration points: Included by `install-deps/main.yml` based on distribution. Depends on package names available in the target distro repositories.

Risks: Package names differ by distro and kernel/BCC packaging can be fragile. Missing debugfs/BCC kernel support will not be caught by package install alone.

Test signals: Signals are successful idempotent package install and later ability to import matplotlib and BCC and run monitor scripts.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/monitoring/tasks/install-deps/centos/main.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/monitoring/tasks/install-deps/debian/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/monitoring/tasks/install-deps/debian/main.yml

Purpose: installs monitoring runtime dependencies on debian targets, split between common Python plotting support, folio migration support, and memory fragmentation eBPF support.

Important APIs/types/functions: modules `ansible.builtin.apt`; variables/facts `become_method`, `update_cache`, `cache_valid_time`; tasks `Update apt cache`, `Install monitoring Python dependencies`, `Install folio migration monitoring dependencies`, `Install memory fragmentation monitoring dependencies`.

Control flow: Uses the `apt` module to install Python 3, matplotlib/numpy-style plotting packages, `stress-ng` for folio migration workloads, and BCC/eBPF packages when the corresponding monitor flags are enabled. Debian updates apt cache first.

State and persistence behavior: Mutates system package state only; no monitoring data is created here.

Dependencies and integration points: Included by `install-deps/main.yml` based on distribution. Depends on package names available in the target distro repositories.

Risks: Package names differ by distro and kernel/BCC packaging can be fragile. Missing debugfs/BCC kernel support will not be caught by package install alone.

Test signals: Signals are successful idempotent package install and later ability to import matplotlib and BCC and run monitor scripts.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/monitoring/tasks/install-deps/debian/main.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/monitoring/tasks/install-deps/fedora/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/monitoring/tasks/install-deps/fedora/main.yml

Purpose: installs monitoring runtime dependencies on fedora targets, split between common Python plotting support, folio migration support, and memory fragmentation eBPF support.

Important APIs/types/functions: modules `ansible.builtin.dnf`; variables/facts `become_method`; tasks `Install monitoring Python dependencies`, `Install folio migration monitoring dependencies`, `Install memory fragmentation monitoring dependencies`.

Control flow: Uses the `dnf` module to install Python 3, matplotlib/numpy-style plotting packages, `stress-ng` for folio migration workloads, and BCC/eBPF packages when the corresponding monitor flags are enabled. Debian updates apt cache first.

State and persistence behavior: Mutates system package state only; no monitoring data is created here.

Dependencies and integration points: Included by `install-deps/main.yml` based on distribution. Depends on package names available in the target distro repositories.

Risks: Package names differ by distro and kernel/BCC packaging can be fragile. Missing debugfs/BCC kernel support will not be caught by package install alone.

Test signals: Signals are successful idempotent package install and later ability to import matplotlib and BCC and run monitor scripts.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/monitoring/tasks/install-deps/fedora/main.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/monitoring/tasks/install-deps/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/monitoring/tasks/install-deps/main.yml

Purpose: dispatches monitoring dependency installation to a distribution-specific task file.

Important APIs/types/functions: modules `ansible.builtin.set_fact`, `ansible.builtin.include_tasks`; variables/facts `kdevops_target_distro_group`; tasks `Set the distro group`, `Import install-deps task for {{ ansible_distribution | lower }}`.

Control flow: Sets `kdevops_target_distro_group` from `ansible_distribution | lower`, then includes `<distro>/main.yml`.

State and persistence behavior: Persists only an Ansible fact.

Dependencies and integration points: Used by monitoring setup roles before monitor scripts run.

Risks: The dispatch uses distribution names like `debian`, `fedora`, `centos`; unsupported names without matching directories will fail.

Test signals: Test by running on each supported distro and confirming the expected include path is selected.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/monitoring/tasks/install-deps/main.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/monitoring/tasks/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/monitoring/tasks/main.yml

Purpose: top-level monitoring role task switchboard for run and collect phases.

Important APIs/types/functions: modules `ansible.builtin.include_vars`, `ansible.builtin.include_tasks`; variables/facts `ignore_errors`, `with_first_found`, `skip`; tasks `Import optional extra_args file`, `Include monitor_run tasks`, `Include monitor_collect tasks`.

Control flow: Imports optional extra vars, includes `monitor_run.yml` when `monitor_run` is true, and includes `monitor_collect.yml` when `monitor_collect` is true.

State and persistence behavior: No direct persistent state beyond loaded variables; included task files create monitor outputs.

Dependencies and integration points: Entry point for playbooks that invoke the monitoring role.

Risks: If both booleans are false this role is a no-op. Extra-vars load ignores errors, which can hide malformed overrides.

Test signals: Signals are correct tag selection and inclusion of run or collect tasks under requested booleans.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/monitoring/tasks/main.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/monitoring/tasks/monitor_collect.yml -->
# sources/test-tools/kdevops/playbooks/roles/monitoring/tasks/monitor_collect.yml

Purpose: final collection path for monitoring data; it stops active monitors, generates target-side or localhost visualizations, fetches artifacts, and invokes comparison scripts.

Important APIs/types/functions: modules `ansible.builtin.set_fact`, `ansible.builtin.stat`, `ansible.builtin.shell`, `ansible.builtin.debug`, `ansible.builtin.find`, `ansible.builtin.file`, `ansible.builtin.fetch`, `ansible.builtin.command`; variables/facts `monitoring_results_path`, `become_method`, `msg`, `ignore_errors`, `patterns`, `file_type`, `flat`, `validate_checksum`, `cmd`, `monitoring_results_dir`; tasks `Set monitoring results path`, `Check if fragmentation monitoring was started`, `Stop fragmentation monitoring`, `Display stop fragmentation monitoring status`, `Generate fragmentation visualization`.

Control flow: Imports common setup and folio collect tasks, computes a workflow-specific results path, SIGINTs fragmentation tracker, records end time, optionally runs `fragmentation_visualizer.py`, finds output files, fetches them to localhost, generates fragmentation comparisons, and includes `visualize.yml`.

State and persistence behavior: Persists fetched files under `<workflow>/results/monitoring`, plus comparison PNGs. Removes the target PID file after shutdown and writes end time on target.

Dependencies and integration points: Invoked after monitored workflows. Integrates tracker/snapshot data, folio migration data, and the scripts under `roles/monitoring/scripts`.

Risks: It resets `monitoring_results_path` once to an fstests default after a richer workflow path calculation, which can misplace outputs unless `monitoring_results_base_path` is set. The stop loop waits indefinitely.

Test signals: Test with folio-only, fragmentation-only, and both monitors; verify fetched artifacts, generated comparisons, and graceful no-data behavior.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/monitoring/tasks/monitor_collect.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/monitoring/tasks/monitor_collect_only.yml -->
# sources/test-tools/kdevops/playbooks/roles/monitoring/tasks/monitor_collect_only.yml

Purpose: interim collection path that snapshots monitoring data while keeping monitoring active.

Important APIs/types/functions: modules `ansible.builtin.shell`, `ansible.builtin.copy`, `ansible.builtin.command`, `ansible.builtin.debug`, `ansible.builtin.set_fact`, `ansible.builtin.file`, `ansible.builtin.stat`, `ansible.builtin.fetch`; variables/facts `become_method`, `cmd`, `msg`, `args`, `chdir`, `monitor_developmental_stats`, `monitor_folio_migration`, `enable_monitoring`, `monitoring_results_path`, `flat`; tasks `Check if fragmentation tracker is running`, `Copy fragmentation snapshot script to target`, `Create fragmentation data snapshot`, `Display fragmentation snapshot status`, `Create snapshot of monitoring data`.

Control flow: Imports setup and folio collect-only tasks, checks tracker status, copies/runs `fragmentation_snapshot.py`, fetches folio and fragmentation snapshots, optionally generates local folio plots, then removes snapshot files from targets.

State and persistence behavior: Persists interim files named `*_interim.txt` and `*_interim.json` on localhost while retaining the long-running monitor. Target snapshot files are cleaned up.

Dependencies and integration points: Used during long workflows to inspect progress. Depends on active PID files, `/root/monitoring`, matplotlib on localhost for plots, and the snapshot helper.

Risks: The folio snapshot task references `folio_migration_data_file` from an imported file; if import is skipped, conditions must remain safe. Plot summary messages are inconsistent and a variable named `folio_interim_plot_generation` is referenced but not set in this file.

Test signals: Signals are continued tracker PID after collection, valid interim JSON/text, generated plots when matplotlib exists, and cleanup of target snapshot files.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/monitoring/tasks/monitor_collect_only.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/monitoring/tasks/monitor_run.yml -->
# sources/test-tools/kdevops/playbooks/roles/monitoring/tasks/monitor_run.yml

Purpose: starts enabled monitoring collectors on target hosts, including folio migration and memory fragmentation tracking.

Important APIs/types/functions: modules `ansible.builtin.file`, `ansible.builtin.copy`, `ansible.builtin.shell`, `ansible.builtin.set_fact`, `ansible.builtin.debug`; variables/facts `become_method`, `async`, `poll`, `fragmentation_monitor_job`, `msg`; tasks `Create fragmentation scripts directory`, `Copy fragmentation monitoring scripts to target`, `Create fragmentation monitoring output directory`, `Start fragmentation monitoring in background`, `Save fragmentation monitor async job ID`.

Control flow: Imports folio migration run tasks, creates `/opt/fragmentation`, copies tracker and visualizer scripts, creates the output directory, starts `fragmentation_tracker.py` with optional `timeout`, saves the PID and start time, and verifies the process exists.

State and persistence behavior: Persists scripts under `/opt/fragmentation`, output/log/PID/start-time files under `monitor_fragmentation_output_dir`, and an async job id fact.

Dependencies and integration points: Consumed before long-running workflows. Depends on root, Python/BCC dependencies, and monitor variables such as `monitor_memory_fragmentation` and `monitor_fragmentation_duration`.

Risks: The `timeout` command can terminate with SIGTERM and may bypass JSON save if not handled. PID verification is immediate and may pass before later BCC compile failures surface in the log.

Test signals: Signals include running PID, populated log, `start_time.txt`, valid JSON after shutdown, and no orphaned process after collection.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/monitoring/tasks/monitor_run.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/monitoring/tasks/monitors/folio_migration/collect.yml -->
# sources/test-tools/kdevops/playbooks/roles/monitoring/tasks/monitors/folio_migration/collect.yml

Purpose: final folio migration collection task. It stops the sampler, plots data, fetches stats and images, and summarizes results.

Important APIs/types/functions: modules `ansible.builtin.stat`, `ansible.builtin.shell`, `ansible.builtin.debug`, `ansible.builtin.copy`, `ansible.builtin.command`, `ansible.builtin.fetch`; variables/facts `become_method`, `msg`, `ignore_errors`, `args`, `chdir`, `flat`, `validate_checksum`; tasks `Check if folio migration monitoring was started`, `Stop folio migration monitoring`, `Display stop monitoring status`, `Check if monitoring data was collected`, `Copy plot_migration_stats.py to target`.

Control flow: Checks the PID file, kills the monitor process, verifies `folio_migration_stats.txt`, copies plot script, checks matplotlib, runs target-side plotting, creates local result directories, fetches stats and plots, then reports collected files.

State and persistence behavior: Persists target stop state and local copied stats/plots under monitoring results.

Dependencies and integration points: Imported by `monitor_collect.yml`. Depends on `/root/monitoring`, plot script, matplotlib availability, and the sampler PID.

Risks: Killing without robust process-group cleanup can miss child shell loops. Target-side plotting requires matplotlib on targets even though other paths plot on localhost.

Test signals: Signals include stopped PID, fetched stats, generated PNG when matplotlib exists, and no failure when data is absent.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/monitoring/tasks/monitors/folio_migration/collect.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/monitoring/tasks/monitors/folio_migration/collect_only.yml -->
# sources/test-tools/kdevops/playbooks/roles/monitoring/tasks/monitors/folio_migration/collect_only.yml

Purpose: interim folio migration collection that copies current stats without stopping the sampler.

Important APIs/types/functions: modules `ansible.builtin.stat`, `ansible.builtin.shell`, `ansible.builtin.fetch`, `ansible.builtin.file`, `ansible.builtin.debug`, `ansible.builtin.command`, `ansible.builtin.find`; variables/facts `become_method`, `flat`, `validate_checksum`, `ignore_errors`, `msg`, `patterns`; tasks `Check if folio migration monitoring data exists`, `Create folio migration snapshot for interim collection`, `Copy folio migration interim data to localhost`, `Clean up folio migration snapshot`, `Display folio migration interim collection status`.

Control flow: Stats the live data file, copies it to a snapshot, fetches it to localhost as an interim result, and leaves the monitor running.

State and persistence behavior: Persists a temporary snapshot on target and an interim stats file on localhost.

Dependencies and integration points: Imported by `monitor_collect_only.yml`. Depends on `/root/monitoring/folio_migration_stats.txt`.

Risks: A simple `cp` can race with the writer and capture a partially updated timestamp block. The caller performs cleanup.

Test signals: Signals are existing source stats, fetched interim text, and unchanged sampler PID.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/monitoring/tasks/monitors/folio_migration/collect_only.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/monitoring/tasks/monitors/folio_migration/files/plot_migration_stats.py -->
# sources/test-tools/kdevops/playbooks/roles/monitoring/tasks/monitors/folio_migration/files/plot_migration_stats.py

Purpose: renders detailed folio migration time-series plots from timestamped debugfs `migrate_folio` stats, including cumulative calls/success, interval rates, and trimmed workload activity windows.

Important APIs/types/functions: `human_format()`, `parse_stats_file()`, `find_start_index()`, `cumulative_to_interval()`, `find_end_of_activity()`, `plot_folio_migration()`, `main()`.

Control flow: `parse_stats_file()` extracts timestamp blocks and `calls`/`success`; `cumulative_to_interval()` converts counters; `find_end_of_activity()` trims trailing idle periods; `plot_folio_migration()` builds one-file, A/B, or comprehensive plots with paired baseline/dev styling; `main()` parses inputs and output path.

State and persistence behavior: Reads stats text and writes matplotlib PNGs. It persists no host state and uses only derived in-memory series.

Dependencies and integration points: Used by folio migration collect and collect-only tasks. Depends on matplotlib and timestamp/stat text generated from `/sys/kernel/debug/mm/migrate_folio_stats`.

Risks: Counter resets or missing timestamp blocks can produce negative or sparse intervals. Activity trimming assumes minute cadence. Very large file sets may crowd legends and labels.

Test signals: Validate ISO and syslog timestamp parsing, cumulative-to-interval conversion, idle-tail trimming, two-file A/B plots, multi-host plots, and output creation with empty data handled predictably.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/monitoring/tasks/monitors/folio_migration/files/plot_migration_stats.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/monitoring/tasks/monitors/folio_migration/run.yml -->
# sources/test-tools/kdevops/playbooks/roles/monitoring/tasks/monitors/folio_migration/run.yml

Purpose: starts folio migration stats sampling on target hosts.

Important APIs/types/functions: modules `ansible.builtin.stat`, `ansible.builtin.file`, `ansible.builtin.shell`, `ansible.builtin.set_fact`, `ansible.builtin.debug`; variables/facts `become_method`, `async`, `poll`, `folio_migration_monitor_job`, `msg`; tasks `Check if folio migration stats are available`, `Create monitoring directory`, `Start folio migration monitoring in background`, `Save async job ID for later termination`, `Verify monitoring started successfully`.

Control flow: Creates `/root/monitoring`, initializes stats files, and backgrounds a shell loop that periodically timestamps and reads debugfs migrate_folio stats into `folio_migration_stats.txt`, recording a PID.

State and persistence behavior: Persists `/root/monitoring/folio_migration.pid`, stats text, logs, and start metadata on targets.

Dependencies and integration points: Imported by `monitor_run.yml` when developmental folio monitoring is enabled. Depends on debugfs migration stats support, root, and interval variables.

Risks: Debugfs paths may not exist on kernels without the experimental stats patch; background shell loops can be orphaned if PID handling fails.

Test signals: Test by confirming PID, increasing stats file over time, readable migrate_folio counters, and clean shutdown by collect tasks.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/monitoring/tasks/monitors/folio_migration/run.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/monitoring/tasks/visualize.yml -->
# sources/test-tools/kdevops/playbooks/roles/monitoring/tasks/visualize.yml

Purpose: localhost visualization aggregator for monitoring result directories.

Important APIs/types/functions: modules `ansible.builtin.stat`, `ansible.builtin.command`, `ansible.builtin.debug`, `ansible.builtin.find`; variables/facts `cmd`, `failed_when`, `changed_when`, `msg`, `patterns`, `recurse`; tasks `Check if monitoring data was collected`, `Generate monitoring visualizations`, `Generate folio migration comparison plots`, `Display folio migration visualization results`, `Generate fragmentation comparison plots`.

Control flow: Stats the result directory, then runs folio migration, simple fragmentation, and A/B fragmentation comparison scripts. It lists generated PNG/HTML files from the root and `fragmentation` subdirectory.

State and persistence behavior: Writes only generated visualization artifacts in the monitoring results tree.

Dependencies and integration points: Included by `monitor_collect.yml`; depends on Python plotting dependencies on localhost and scripts under `role_path`.

Risks: Commands are `failed_when: false`, so visualization failures may be visible only in debug output. The legacy fragmentation script may produce low-value graphs.

Test signals: Signals include non-empty stdout from scripts, generated PNG files, and harmless behavior when no data exists.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/monitoring/tasks/visualize.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/nfsd/defaults/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/nfsd/defaults/main.yml

Purpose: defines default NFS server export settings: export root, default filesystem/storage choices, and service behavior knobs used by `nfsd` and `nfsd_add_export`.

Important APIs/types/functions: variables/facts `nfsd_export_label`, `nfsd_export_fs_opts`, `nfsd_lease_time`, `nfsd_export_storage_local`, `nfsd_export_storage_iscsi`, `kdevops_krb5_enable`.

Control flow: Defaults are read by Ansible variable resolution before task execution.

State and persistence behavior: No runtime state; values shape later directory, storage, and export creation.

Dependencies and integration points: Consumed by NFS server setup and test roles such as pynfs/nfstest that request exports.

Risks: Unsafe defaults can expose broad export permissions if templates use them directly; changes affect multiple workflows.

Test signals: Validate by rendering exports with expected path, fs type, storage mode, and options.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/nfsd/defaults/main.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/nfsd/tasks/install-deps/debian/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/nfsd/tasks/install-deps/debian/main.yml

Purpose: installs NFS server dependencies for debian family systems and dynamically includes filesystem userspace tools for the configured export filesystem.

Important APIs/types/functions: modules `ansible.builtin.include_vars`, `ansible.builtin.set_fact`, `ansible.builtin.apt`; variables/facts `params`, `fsprogs`, `nfsd_packages`, `become_method`, `update_cache`; tasks `Get OS-specific variables`, `Determine which fsprogs package is needed for "{{ nfsd_export_fstype }}"`, `Add {{ fsprogs }} to the nfsd packages list`, `Add gssproxy to the nfsd packages list`, `Install nfsd dependencies`.

Control flow: Loads OS vars, computes the package needed for `nfsd_export_fstype`, appends it to `nfsd_packages` when present, then installs with the distro package manager.

State and persistence behavior: Mutates target package state and the transient `nfsd_packages` fact.

Dependencies and integration points: Included by `nfsd/tasks/main.yml`. Depends on `vars/<OS>.yml` package maps.

Risks: Unknown filesystem types can leave `fsprogs` empty and skip required mkfs tools. RedHat/Suse package names differ.

Test signals: Signals are successful install for btrfs/ext4/xfs exports and no duplicate package-list failures on repeat runs.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/nfsd/tasks/install-deps/debian/main.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/nfsd/tasks/install-deps/redhat/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/nfsd/tasks/install-deps/redhat/main.yml

Purpose: installs NFS server dependencies for redhat family systems and dynamically includes filesystem userspace tools for the configured export filesystem.

Important APIs/types/functions: modules `ansible.builtin.include_vars`, `ansible.builtin.set_fact`, `ansible.builtin.dnf`; variables/facts `params`, `fsprogs`, `nfsd_packages`, `become_method`, `update_cache`, `retries`, `delay`, `until`; tasks `Get OS-specific variables`, `Determine which fsprogs package is needed for "{{ nfsd_export_fstype }}"`, `Add {{ fsprogs }} to the nfsd packages list`, `Install nfsd dependencies`.

Control flow: Loads OS vars, computes the package needed for `nfsd_export_fstype`, appends it to `nfsd_packages` when present, then installs with the distro package manager.

State and persistence behavior: Mutates target package state and the transient `nfsd_packages` fact.

Dependencies and integration points: Included by `nfsd/tasks/main.yml`. Depends on `vars/<OS>.yml` package maps.

Risks: Unknown filesystem types can leave `fsprogs` empty and skip required mkfs tools. RedHat/Suse package names differ.

Test signals: Signals are successful install for btrfs/ext4/xfs exports and no duplicate package-list failures on repeat runs.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/nfsd/tasks/install-deps/redhat/main.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/nfsd/tasks/install-deps/suse/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/nfsd/tasks/install-deps/suse/main.yml

Purpose: installs NFS server dependencies for suse family systems and dynamically includes filesystem userspace tools for the configured export filesystem.

Important APIs/types/functions: modules `ansible.builtin.include_vars`, `ansible.builtin.set_fact`, `community.general.zypper`; variables/facts `params`, `fsprogs`, `nfsd_packages`, `become_method`; tasks `Get OS-specific variables`, `Determine which fsprogs package is needed for "{{ nfsd_export_fstype }}"`, `Add {{ fsprogs }} to the nfsd packages list`, `Add additional packages needed for krb5 to the nfsd packages list`, `Install nfsd dependencies`.

Control flow: Loads OS vars, computes the package needed for `nfsd_export_fstype`, appends it to `nfsd_packages` when present, then installs with the distro package manager.

State and persistence behavior: Mutates target package state and the transient `nfsd_packages` fact.

Dependencies and integration points: Included by `nfsd/tasks/main.yml`. Depends on `vars/<OS>.yml` package maps.

Risks: Unknown filesystem types can leave `fsprogs` empty and skip required mkfs tools. RedHat/Suse package names differ.

Test signals: Signals are successful install for btrfs/ext4/xfs exports and no duplicate package-list failures on repeat runs.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/nfsd/tasks/install-deps/suse/main.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/nfsd/tasks/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/nfsd/tasks/main.yml

Purpose: configures an NFS server host for kdevops workflows, including package dependencies, `/etc/nfs.conf`, optional iSCSI/local storage prep, SELinux policy, firewall handling, and nfs-server service state.

Important APIs/types/functions: modules `ansible.builtin.include_tasks`, `ansible.builtin.template`, `ansible.builtin.include_role`, `ansible.builtin.file`, `ansible.builtin.command`, `ansible.builtin.copy`, `community.general.sefcontext`, `ansible.builtin.service_facts`; variables/facts `become_flags`, `become_method`, `tasks_from`, `volume_group_name`, `changed_when`, `failed_when`, `target`, `setype`, `enabled`; tasks `Debian-specific setup`, `SuSE-specific setup`, `Red Hat-specific setup`, `Generate /etc/nfs.conf`, `Set up an iSCSI initiator`.

Control flow: Dispatches distro dependency tasks, templates `nfs.conf`, optionally includes `iscsi` or `volume_group`, creates the export root, installs a custom SELinux policy when enabled, labels exports as `public_content_rw_t`, stops firewalld, and reloads/enables `nfs-server.service`.

State and persistence behavior: Mutates packages, `/etc/nfs.conf`, export directories, SELinux module/state, firewalld state, and systemd service state.

Dependencies and integration points: Foundation for `nfsd_add_export`, `pynfs`, and `nfstest`. Depends on templates, SELinux tooling, nfs-utils packages, and optional storage roles.

Risks: Disabling firewalld is broad. SELinux setup assumes policy tooling exists. Service reload before exports exist can hide template issues until clients mount.

Test signals: Signals are idempotent package install, rendered config, active nfs-server, correct SELinux labels, and successful `exportfs -v` after adding exports.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/nfsd/tasks/main.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/nfsd/vars/Debian.yml -->
# sources/test-tools/kdevops/playbooks/roles/nfsd/vars/Debian.yml

Purpose: provides Debian-specific NFS server package lists and filesystem userspace package mappings.

Important APIs/types/functions: variables/facts `nfsd_packages`, `fstype_userspace_progs`, `btrfs`, `ext4`, `xfs`, `pipefs_directory`.

Control flow: Variables are loaded by install-deps tasks through `first_found` and then consumed for package installation.

State and persistence behavior: No persistent state; only package variable definitions.

Dependencies and integration points: Integrated with `nfsd` dependency installation and filesystem selection.

Risks: Incorrect package names block NFS setup or filesystem formatting. Suse naming differs from Debian/RedHat for btrfs tools.

Test signals: Signals are package install success and correct package chosen for btrfs, ext4, and xfs.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/nfsd/vars/Debian.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/nfsd/vars/RedHat.yml -->
# sources/test-tools/kdevops/playbooks/roles/nfsd/vars/RedHat.yml

Purpose: provides RedHat-specific NFS server package lists and filesystem userspace package mappings.

Important APIs/types/functions: variables/facts `nfsd_packages`, `fstype_userspace_progs`, `btrfs`, `ext4`, `xfs`, `pipefs_directory`.

Control flow: Variables are loaded by install-deps tasks through `first_found` and then consumed for package installation.

State and persistence behavior: No persistent state; only package variable definitions.

Dependencies and integration points: Integrated with `nfsd` dependency installation and filesystem selection.

Risks: Incorrect package names block NFS setup or filesystem formatting. Suse naming differs from Debian/RedHat for btrfs tools.

Test signals: Signals are package install success and correct package chosen for btrfs, ext4, and xfs.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/nfsd/vars/RedHat.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/nfsd/vars/Suse.yml -->
# sources/test-tools/kdevops/playbooks/roles/nfsd/vars/Suse.yml

Purpose: provides Suse-specific NFS server package lists and filesystem userspace package mappings.

Important APIs/types/functions: variables/facts `nfsd_packages`, `fstype_userspace_progs`, `btrfs`, `ext4`, `xfs`, `pipefs_directory`.

Control flow: Variables are loaded by install-deps tasks through `first_found` and then consumed for package installation.

State and persistence behavior: No persistent state; only package variable definitions.

Dependencies and integration points: Integrated with `nfsd` dependency installation and filesystem selection.

Risks: Incorrect package names block NFS setup or filesystem formatting. Suse naming differs from Debian/RedHat for btrfs tools.

Test signals: Signals are package install success and correct package chosen for btrfs, ext4, and xfs.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/nfsd/vars/Suse.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/nfsd_add_export/defaults/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/nfsd_add_export/defaults/main.yml

Purpose: sets default ownership, group, and permissions for newly added NFS export directories.

Important APIs/types/functions: variables/facts `export_user`, `export_group`, `export_mode`, `export_pnfs`, `nfsd_export_storage_local`, `nfsd_export_storage_iscsi`.

Control flow: Defaults feed the `file` task after storage and mount setup.

State and persistence behavior: No direct state; values affect directory metadata on server hosts.

Dependencies and integration points: Used by `nfsd_add_export` calls from pynfs/nfstest and other workflows.

Risks: Broad modes or root ownership changes affect client write behavior and test assumptions.

Test signals: Validate by checking created export directory owner/group/mode.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/nfsd_add_export/defaults/main.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/nfsd_add_export/tasks/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/nfsd_add_export/tasks/main.yml

Purpose: adds one export to an existing kdevops NFS server, creating requested storage, setting permissions and SELinux context, writing `/etc/exports.d/<name>.exports`, and reloading exports.

Important APIs/types/functions: modules `ansible.builtin.include_tasks`, `ansible.builtin.file`, `ansible.builtin.command`, `ansible.builtin.set_fact`, `ansible.builtin.template`; variables/facts `file`, `become_flags`, `become_method`, `changed_when`, `failed_when`, `template_export_options`, `fsid_is_present`; tasks `Add a local logical volume for the new export`, `Add an iSCSI LUN for the new export`, `Add a tmpfs for the new export`, `Ensure {{ export_volname }} has correct permissions`, `Test whether SELinux is enabled`.

Control flow: Includes local, iSCSI, or tmpfs storage tasks based on variables; fixes permissions; detects SELinux; ensures `/etc/exports.d`; adds a generated fsid for tmpfs when absent; optionally appends `pnfs`; templates the export file; runs `exportfs -ra`.

State and persistence behavior: Persists mounted storage, export directories, `/etc/exports.d` files, SELinux contexts, and NFS export table state on `server_host`.

Dependencies and integration points: Used by nfstest and pynfs to create per-test exports. Depends on `server_host`, storage roles, `exports.j2`, `uuidgen`, and nfsd being configured.

Risks: The pNFS branch overwrites `template_export_options` from `export_options` rather than preserving a generated tmpfs fsid. `/etc/exports.d` mode is `644` on a directory, which is unusual. Parallel export edits are partly serialized only in downstream roles.

Test signals: Signals are mounted export path, valid export file, `exportfs -ra` success, unique fsid for tmpfs, and client mount success.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/nfsd_add_export/tasks/main.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/nfsd_add_export/tasks/storage/iscsi.yml -->
# sources/test-tools/kdevops/playbooks/roles/nfsd_add_export/tasks/storage/iscsi.yml

Purpose: creates and mounts an iSCSI-backed filesystem for a new NFS export.

Important APIs/types/functions: modules `ansible.builtin.include_role`, `community.general.open_iscsi`, `ansible.builtin.command`, `ansible.builtin.set_fact`, `community.general.filesystem`, `ansible.posix.mount`; variables/facts `iscsi_add_devname`, `iscsi_add_size`, `tasks_from`, `become_flags`, `become_method`, `rescan`, `cmd`, `changed_when`, `iscsi_device`, `fstype`; tasks `Create an iSCSI LUN for the new export`, `Rescan iSCSI LUNs on the NFS server`, `Rescan iSCSI LUNs on the target node`, `Enumerate available SCSI devices on the NFS server`, `Select the device that matches {{ export_volname }}`.

Control flow: Delegates iSCSI LUN creation/attachment to storage roles, waits for the block device, formats it, and mounts it under the export root.

State and persistence behavior: Persists remote LUN state, local initiator/device state, filesystem, and mount entry.

Dependencies and integration points: Used when `nfsd_export_storage_iscsi` is true. Depends on iSCSI target/initiator role variables and block device discovery.

Risks: Device naming/timing races can format the wrong device if discovery assumptions change. Cleanup is not represented in this task.

Test signals: Signals are visible iSCSI session, expected block device, mounted export, and client mount success.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/nfsd_add_export/tasks/storage/iscsi.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/nfsd_add_export/tasks/storage/local.yml -->
# sources/test-tools/kdevops/playbooks/roles/nfsd_add_export/tasks/storage/local.yml

Purpose: creates and mounts a local LVM-backed filesystem for a new NFS export.

Important APIs/types/functions: modules `community.general.lvol`, `community.general.filesystem`, `ansible.posix.mount`; variables/facts `become_flags`, `become_method`, `vg`, `lv`, `size`, `fstype`, `dev`, `throttle`; tasks `Create a new LVM partition`, `Format new volume for {{ export_fstype }}`, `Mount volume under {{ nfsd_export_path }}`.

Control flow: Delegates to `server_host`, creates an LVM logical volume in VG `exports`, formats it with `export_fstype`, and mounts it under `nfsd_export_path/export_volname` with fstab persistence.

State and persistence behavior: Persists an LV, filesystem, mount entry, and mounted directory on the server.

Dependencies and integration points: Included by `nfsd_add_export/tasks/main.yml` when local storage is selected.

Risks: Volume creation and fstab edits are stateful and can fail if the VG lacks space or parallel runs collide.

Test signals: Signals are present LV, successful filesystem creation, mounted path, and idempotent rerun.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/nfsd_add_export/tasks/storage/local.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/nfsd_add_export/tasks/storage/tmpfs.yml -->
# sources/test-tools/kdevops/playbooks/roles/nfsd_add_export/tasks/storage/tmpfs.yml

Purpose: mounts a tmpfs-backed directory for an NFS export.

Important APIs/types/functions: modules `ansible.posix.mount`; variables/facts `become_flags`, `become_method`, `throttle`, `fstype`; tasks `Mount a tmpfs under {{ nfsd_export_path }}`.

Control flow: Delegates to `server_host` and mounts `tmpfs` at `nfsd_export_path/export_volname`.

State and persistence behavior: Persists an fstab/system mount entry for tmpfs and runtime memory-backed contents.

Dependencies and integration points: Used when `export_fstype == tmpfs`; main export task adds a unique fsid if needed.

Risks: Tmpfs contents are volatile and consume RAM; missing stable fsid can confuse NFS clients across remounts.

Test signals: Signals are mounted tmpfs, export file with fsid, and successful NFS client access.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/nfsd_add_export/tasks/storage/tmpfs.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/nfstest/defaults/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/nfstest/defaults/main.yml

Purpose: sets nfstest repository, commit, mount point, and whether to use kdevops-managed NFS exports.

Important APIs/types/functions: variables/facts `kdevops_run_nfstest`, `kdevops_workflows_dedicated_workflow`.

Control flow: Defaults are consumed by `nfstest/tasks/main.yml` during clone, export setup, and test execution.

State and persistence behavior: No direct state; controls install paths and export behavior.

Dependencies and integration points: Integrated with nfsd/nfsd_add_export and workflow templates.

Risks: Changing repo/commit or server flags alters reproducibility.

Test signals: Signals are expected clone source/version and generated test script using the configured mount.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/nfstest/defaults/main.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/nfstest/tasks/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/nfstest/tasks/main.yml

Purpose: installs, configures, runs, and collects results for the external nfstest suite in a kdevops workflow.

Important APIs/types/functions: modules `ansible.builtin.include_vars`, `ansible.builtin.package`, `ansible.builtin.include_role`, `ansible.builtin.set_fact`, `ansible.builtin.file`, `ansible.builtin.git`, `ansible.builtin.template`, `ansible.builtin.command`; variables/facts `file`, `with_first_found`, `skip`, `failed_when`, `params`, `become_flags`, `become_method`, `nfstest_install_dir`, `nfstest_test_group`, `nfstest_nfs_server_export`; tasks `Include optional extra_vars`, `Set OS-specific variables`, `Install dependencies for nfstest`, `Create the /data mount point on the target nodes`, `Set the pathname of the install directory`.

Control flow: Loads optional/OS vars, installs dependencies, prepares `/data`, removes old install dir, derives host test group, optionally creates an NFS export, clones nfstest, templates and runs `/tmp/runtest.sh`, records kernel version, fetches `nfstest*.log`, and archives last-run results.

State and persistence behavior: Persists cloned source under data path, target mount point, optional server export, temporary run script/logs, and localhost results under `workflows/nfstest/results`.

Dependencies and integration points: Depends on distro package vars, git, templates per test group, NFS server/export roles, and dedicated workflow variables.

Risks: The so-called full clone also uses `depth: 1`. Test-group derivation is host-name-convention-dependent. Cleaning last-run is delegated run-once and can erase concurrent results.

Test signals: Signals are dependency install, successful clone, mounted export, logs fetched per kernel, and no TAP/log failures in generated nfstest output.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/nfstest/tasks/main.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/nfstest/vars/Debian.yml -->
# sources/test-tools/kdevops/playbooks/roles/nfstest/vars/Debian.yml

Purpose: defines the package set required to run nfstest on Debian family systems.

Important APIs/types/functions: variables/facts `nfstest_packages`.

Control flow: Loaded by `nfstest/tasks/main.yml` through `first_found` and passed to `ansible.builtin.package`.

State and persistence behavior: No persistent state beyond package names.

Dependencies and integration points: Supports nfstest dependency installation across distros.

Risks: Missing Python, git, or NFS client packages will cause later clone/mount/test failures.

Test signals: Signal is successful package installation and ability to run the generated nfstest script.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/nfstest/vars/Debian.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/nfstest/vars/RedHat.yml -->
# sources/test-tools/kdevops/playbooks/roles/nfstest/vars/RedHat.yml

Purpose: defines the package set required to run nfstest on RedHat family systems.

Important APIs/types/functions: variables/facts `nfstest_packages`.

Control flow: Loaded by `nfstest/tasks/main.yml` through `first_found` and passed to `ansible.builtin.package`.

State and persistence behavior: No persistent state beyond package names.

Dependencies and integration points: Supports nfstest dependency installation across distros.

Risks: Missing Python, git, or NFS client packages will cause later clone/mount/test failures.

Test signals: Signal is successful package installation and ability to run the generated nfstest script.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/nfstest/vars/RedHat.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/nfstest/vars/Suse.yml -->
# sources/test-tools/kdevops/playbooks/roles/nfstest/vars/Suse.yml

Purpose: defines the package set required to run nfstest on Suse family systems.

Important APIs/types/functions: variables/facts `nfstest_packages`.

Control flow: Loaded by `nfstest/tasks/main.yml` through `first_found` and passed to `ansible.builtin.package`.

State and persistence behavior: No persistent state beyond package names.

Dependencies and integration points: Supports nfstest dependency installation across distros.

Risks: Missing Python, git, or NFS client packages will cause later clone/mount/test failures.

Test signals: Signal is successful package installation and ability to run the generated nfstest script.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/nfstest/vars/Suse.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/nix-cache-mirror/defaults/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/nix-cache-mirror/defaults/main.yml

Purpose: defines Nix cache mirror enablement, port, upstream cache, local cache path, and nginx configuration paths.

Important APIs/types/functions: variables/facts `nix_cache_mirror_path`, `nix_cache_mirror_port`, `nix_cache_upstream_url`, `nix_cache_mirror_nginx_conf_path`, `nix_cache_mirror_nginx_enabled_path`.

Control flow: Defaults are read by the mirror tasks and templates.

State and persistence behavior: No direct state; controls nginx and systemd artifact locations.

Dependencies and integration points: Used when workflows want a local binary cache proxy/mirror.

Risks: Incorrect paths can conflict with distro nginx layout or permissions.

Test signals: Signals are templates rendering the configured port/upstream/path values.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/nix-cache-mirror/defaults/main.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/nix-cache-mirror/handlers/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/nix-cache-mirror/handlers/main.yml

Purpose: contains the handler that reloads systemd after Nix cache sync service/timer unit files are templated.

Important APIs/types/functions: modules `ansible.builtin.systemd`; variables/facts `daemon_reload`; tasks `reload nginx`, `reload systemd`.

Control flow: `reload systemd` runs `systemctl daemon-reload` when notified by service or timer template tasks.

State and persistence behavior: Mutates systemd manager state only.

Dependencies and integration points: Notified from `nix-cache-mirror/tasks/main.yml`.

Risks: If handler is skipped, newly written units may not be recognized.

Test signals: Signal is daemon-reload execution followed by timer enable/start success.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/nix-cache-mirror/handlers/main.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/nix-cache-mirror/tasks/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/nix-cache-mirror/tasks/main.yml

Purpose: provisions an nginx-backed Nix binary cache mirror/proxy plus a systemd timer for cache synchronization.

Important APIs/types/functions: modules `ansible.builtin.include_vars`, `ansible.builtin.fail`, `ansible.builtin.package`, `ansible.builtin.file`, `ansible.builtin.template`, `ansible.builtin.command`, `ansible.builtin.systemd`, `ansible.posix.firewalld`; variables/facts `ignore_errors`, `with_first_found`, `skip`, `msg`, `changed_when`, `enabled`, `daemon_reload`, `notify`, `failed_when`, `port`; tasks `Import optional extra_args file`, `Fail if nix cache mirror is enabled but user is not root`, `Install nginx for Nix cache mirror`, `Create Nix cache mirror directories`, `Template nginx cache configuration for Nix cache mirror`.

Control flow: Loads extra vars, fails non-root use, installs nginx/curl, creates cache directories owned by `www-data`, templates nginx cache/site config, enables the site, removes default site, validates nginx, starts/reloads nginx, templates sync service/timer, starts the timer, and optionally opens firewalld.

State and persistence behavior: Persists cache directories, nginx configuration, systemd service/timer units, enabled services, and firewall rules.

Dependencies and integration points: Depends on nginx, curl, systemd, templates, root privileges, and `install_nix_cache_mirror`.

Risks: Hard-coded `www-data` owner can be wrong outside Debian-style systems. Firewall opening is tied to `linux_mirror_nfs`. Nginx site paths vary by distro.

Test signals: Signals are `nginx -t`, active nginx, active timer, reachable HTTP port, and cache directory writes.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/nix-cache-mirror/tasks/main.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/pkg/defaults/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/pkg/defaults/main.yml

Purpose: defines package-role defaults, mainly the package manager frontend or command behavior used by distro-specific tasks.

Important APIs/types/functions: Ansible YAML variables/tasks.

Control flow: Defaults feed `pkg/tasks/main.yml` and `pkg/tasks/debian.yml`.

State and persistence behavior: No direct state.

Dependencies and integration points: Small helper role for package-related setup.

Risks: Defaults may be too narrow for non-Debian systems because only Debian task implementation is present in this subset.

Test signals: Signals are variable resolution and successful task include on Debian.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/pkg/defaults/main.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/pkg/tasks/debian.yml -->
# sources/test-tools/kdevops/playbooks/roles/pkg/tasks/debian.yml

Purpose: performs Debian-specific package manager setup for kdevops helper behavior.

Important APIs/types/functions: modules `ansible.builtin.set_fact`; variables/facts `is_bookworm`, `is_bullseye`, `is_buster`, `is_trixie`, `pkg_libaio`; tasks `Debian_libaio rename for buster`, `Debian_libaio rename for debian releases older than trixie`.

Control flow: Runs the task list in order, likely updating package metadata or installing base tools according to role defaults.

State and persistence behavior: Mutates apt/package state on Debian hosts.

Dependencies and integration points: Included only from `pkg/tasks/main.yml`.

Risks: Apt cache/network failures block downstream roles.

Test signals: Signals are idempotent apt task completion and availability of requested package helpers.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/pkg/tasks/debian.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/pkg/tasks/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/pkg/tasks/main.yml

Purpose: dispatches generic package helper setup to Debian-specific tasks.

Important APIs/types/functions: modules `ansible.builtin.import_tasks`; tasks `Oscheck distribution ospecific setup`.

Control flow: Includes `debian.yml` when `ansible_os_family == Debian`.

State and persistence behavior: No direct state; included task performs package configuration.

Dependencies and integration points: Used by roles needing common package-manager behavior.

Risks: Non-Debian systems are no-op.

Test signals: Signal is expected include behavior and idempotent Debian configuration.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/pkg/tasks/main.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/postfix_relay_host/defaults/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/postfix_relay_host/defaults/main.yml

Purpose: defines whether postfix relay-host setup is enabled and the relay host value to write into Postfix configuration.

Important APIs/types/functions: variables/facts `postfix_relay_host_setup`, `postfix_relay_host`.

Control flow: Defaults are consumed by the relay-host task file.

State and persistence behavior: No direct state; variables gate later config mutation.

Dependencies and integration points: Used by host setup that wants outbound mail routed through a relay.

Risks: Incorrect relayhost breaks mail delivery; disabling setup leaves existing config untouched.

Test signals: Signals are expected default variable values and rendered `relayhost` line when enabled.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/postfix_relay_host/defaults/main.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/postfix_relay_host/tasks/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/postfix_relay_host/tasks/main.yml

Purpose: configures Postfix to use a relay host when enabled.

Important APIs/types/functions: modules `ansible.builtin.include_vars`, `ansible.builtin.stat`, `ansible.builtin.lineinfile`, `ansible.builtin.systemd`; variables/facts `ignore_errors`, `with_first_found`, `skip`, `become_flags`, `become_method`, `regexp`, `line`, `enabled`, `masked`; tasks `Import optional extra_args file`, `Check to see if /etc/postfix/main.cf exists`, `Set relayhost on /etc/postfix/main.cf`, `Enable and restart postfix service`.

Control flow: Loads optional extra vars, stats `/etc/postfix/main.cf`, replaces or adds the `relayhost` setting with `lineinfile`, then enables and restarts postfix.

State and persistence behavior: Mutates `/etc/postfix/main.cf` and postfix systemd service state.

Dependencies and integration points: Depends on postfix being installed and `postfix_relay_host_setup`/`postfix_relay_host` variables.

Risks: If Postfix is absent the role silently skips after stat. Bad relayhost values are not validated before restart.

Test signals: Signals are changed relayhost line, active postfix service, and successful mail relay test.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/postfix_relay_host/tasks/main.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/pynfs/defaults/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/pynfs/defaults/main.yml

Purpose: sets pynfs source repository, tag, data path, and pNFS block test enablement defaults.

Important APIs/types/functions: variables/facts `kdevops_run_pynfs`, `pynfs_pnfs_block`, `pynfs_data`.

Control flow: Variables are consumed by clone/build/export/run tasks in the pynfs role.

State and persistence behavior: No direct state; values control source checkout and result behavior.

Dependencies and integration points: Integrated with nfsd_add_export and workflow scripts `run_pynfs.sh` and `run_pynfs_block.sh`.

Risks: Repo/tag drift affects reproducibility; enabling pNFS requires matching server/export support.

Test signals: Signals are checkout at expected tag and expected result files for v4.0/v4.1/block.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/pynfs/defaults/main.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/pynfs/tasks/install-deps/debian/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/pynfs/tasks/install-deps/debian/main.yml

Purpose: installs pynfs build/runtime dependencies on debian family systems.

Important APIs/types/functions: modules `ansible.builtin.apt`; variables/facts `become_method`, `update_cache`; tasks `Install pynfs build dependencies`, `Install xdrlib from Debian package on Debian 13+`.

Control flow: Uses the distro package manager with package lists needed for git, Python tooling, NFS utilities, and Kerberos/RPC support as defined in the task.

State and persistence behavior: Mutates package state only.

Dependencies and integration points: Included by `pynfs/tasks/install-deps/main.yml`.

Risks: Package names and Python version assumptions differ by distribution; missing deps surface later during `setup.py build` or test scripts.

Test signals: Signals are idempotent install and successful subsequent pynfs build.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/pynfs/tasks/install-deps/debian/main.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/pynfs/tasks/install-deps/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/pynfs/tasks/install-deps/main.yml

Purpose: dispatches pynfs dependency installation to Debian, RedHat, or Suse task files.

Important APIs/types/functions: modules `ansible.builtin.import_tasks`; tasks `Oscheck distribution ospecific setup`.

Control flow: Includes the OS-family-specific dependency file based on `ansible_os_family`.

State and persistence behavior: No direct persistent state.

Dependencies and integration points: Called from `pynfs/tasks/main.yml` before cloning/building pynfs.

Risks: Unsupported OS families receive no dependency setup.

Test signals: Test by running on each supported OS family and checking the expected include executes.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/pynfs/tasks/install-deps/main.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/pynfs/tasks/install-deps/redhat/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/pynfs/tasks/install-deps/redhat/main.yml

Purpose: installs pynfs build/runtime dependencies on redhat family systems.

Important APIs/types/functions: modules `ansible.builtin.include_role`, `ansible.builtin.dnf`, `ansible.builtin.pip`; variables/facts `become_method`, `update_cache`, `retries`, `delay`, `until`, `packages`; tasks `Enable the CodeReady repo`, `Install build dependencies for pynfs`, `Install xdrlib3`.

Control flow: Uses the distro package manager with package lists needed for git, Python tooling, NFS utilities, and Kerberos/RPC support as defined in the task.

State and persistence behavior: Mutates package state only.

Dependencies and integration points: Included by `pynfs/tasks/install-deps/main.yml`.

Risks: Package names and Python version assumptions differ by distribution; missing deps surface later during `setup.py build` or test scripts.

Test signals: Signals are idempotent install and successful subsequent pynfs build.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/pynfs/tasks/install-deps/redhat/main.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/pynfs/tasks/install-deps/suse/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/pynfs/tasks/install-deps/suse/main.yml

Purpose: installs pynfs build/runtime dependencies on suse family systems.

Important APIs/types/functions: modules `ansible.builtin.package`, `ansible.builtin.pip`; variables/facts `become_method`; tasks `Install build dependencies for pynfs`, `Install xdrlib3`.

Control flow: Uses the distro package manager with package lists needed for git, Python tooling, NFS utilities, and Kerberos/RPC support as defined in the task.

State and persistence behavior: Mutates package state only.

Dependencies and integration points: Included by `pynfs/tasks/install-deps/main.yml`.

Risks: Package names and Python version assumptions differ by distribution; missing deps surface later during `setup.py build` or test scripts.

Test signals: Signals are idempotent install and successful subsequent pynfs build.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/pynfs/tasks/install-deps/suse/main.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/pynfs/tasks/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/pynfs/tasks/main.yml

Purpose: builds and runs pynfs NFSv4 conformance tests against kdevops-created exports, then collects JSON result files by kernel version.

Important APIs/types/functions: modules `ansible.builtin.include_vars`, `ansible.builtin.set_fact`, `ansible.builtin.file`, `ansible.builtin.include_tasks`, `ansible.builtin.git`, `ansible.builtin.command`, `ansible.builtin.include_role`, `ansible.builtin.script`; variables/facts `ignore_errors`, `with_first_found`, `skip`, `pynfs_workflow_dir`, `pynfs_results_full_path`, `pynfs_results_target`, `become_flags`, `become_method`, `repo`, `update`; tasks `Import optional extra_args file`, `Set the path where we collect our local pynfs results`, `Clean up our localhost results directory and files`, `Create the local results directory`, `Install dependencies`.

Control flow: Loads extra vars, prepares local result dirs and data partition, installs dependencies, reclones pynfs, builds it, creates v4.0/v4.1 and optional pNFS exports, waits for NFS grace period, runs workflow scripts, fetches result JSONs, records kernel revision, and archives last-run results.

State and persistence behavior: Persists source under `pynfs_data`, NFS exports on the server, target run outputs, and localhost results under `workflows/pynfs/results`.

Dependencies and integration points: Depends on git, Python build deps, nfsd server host naming, nfsd_add_export, and workflow scripts.

Risks: Server host is derived from prefix as `<prefix>-nfsd`; if inventory differs, export setup fails. Result fetch assumes JSON files are always produced.

Test signals: Signals include build success, grace-period check, result JSONs for v4.0/v4.1 and optional block, and archived last-run directory.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/pynfs/tasks/main.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/reboot-limit/defaults/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/reboot-limit/defaults/main.yml

Purpose: sets reboot-loop count, test type, data paths, systemd-analyze logging, crash injection, and regular-vs-kexec comparison defaults.

Important APIs/types/functions: variables/facts `reboot_limit_test_type`, `reboot_limits_data`, `reboot_limits_systemctl_analyze_log`, `reboot_limits_count_log`, `reboot_limit_enable_systemd_analyze`, `reboot_limit_boot_count_crash_enable`, `reboot_limit_boot_crash_count`.

Control flow: Defaults feed main loop and per-reboot task files.

State and persistence behavior: No direct state; values determine reboot count and result paths.

Dependencies and integration points: Used by demos/reboot-limit workflow.

Risks: Aggressive defaults can repeatedly reboot or crash hosts; path changes affect result collection.

Test signals: Signals are expected variable values and correct mode selection.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/reboot-limit/defaults/main.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/reboot-limit/tasks/do-reboot-compare.yml -->
# sources/test-tools/kdevops/playbooks/roles/reboot-limit/tasks/do-reboot-compare.yml

Purpose: runs paired regular and kexec reboot iterations for comparison mode.

Important APIs/types/functions: modules `ansible.builtin.debug`, `ansible.builtin.file`, `ansible.builtin.reboot`, `ansible.builtin.include_tasks`, `ansible.builtin.command`, `ansible.builtin.stat`, `ansible.builtin.set_fact`, `ansible.builtin.slurp`; variables/facts `var`, `msg`, `become_method`, `post_reboot_delay`, `reboot_type`, `data_path`, `loop_var`, `kexec_kernel_path`, `kexec_initrd_path`, `reboot_command`; tasks `Print uname for each host`, `Hint to our watchdog our reboot-limit comparison tests are about to kick off`, `Starting Phase 1 - Regular reboot test ({{ reboot_num }} of {{ reboot_limit_max }})`, `Run the regular reboot test using the ansible reboot module`, `Handle regular reboot count and data collection`.

Control flow: Switches facts and paths for regular reboot, includes reboot execution, then switches to kexec paths/type and includes reboot execution again for the same loop iteration.

State and persistence behavior: Persists separate regular and kexec count/analyze logs under comparison directories.

Dependencies and integration points: Included by reboot-limit main when comparison mode is enabled.

Risks: Fact switching must be correct or results can be mixed between modes. Each loop performs two disruptive reboots.

Test signals: Signals are separate count files advancing equally and separate analyze logs populated.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/reboot-limit/tasks/do-reboot-compare.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/reboot-limit/tasks/do-reboot.yml -->
# sources/test-tools/kdevops/playbooks/roles/reboot-limit/tasks/do-reboot.yml

Purpose: executes one reboot iteration in single-mode reboot-limit testing, supporting Ansible reboot, `systemctl reboot`, and `systemctl kexec`.

Important APIs/types/functions: modules `ansible.builtin.debug`, `ansible.builtin.file`, `ansible.builtin.reboot`, `ansible.builtin.command`, `ansible.builtin.stat`, `ansible.builtin.set_fact`, `ansible.builtin.slurp`, `ansible.builtin.shell`; variables/facts `var`, `become_method`, `post_reboot_delay`, `msg`, `reboot_command`, `reboot_timeout`, `loop_var`, `kexec_kernel_path`, `kexec_initrd_path`, `reboot_limit_count`; tasks `Print uname for each host`, `Hint to our watchdog our reboot-limit tests are about to kick off`, `Run the reboot test using the ansible reboot module`, `Reboot using systemctl reboot with proper handling`, `Get current kernel version for kexec`.

Control flow: Touches a local watchdog marker, performs the selected reboot method, loads kexec kernel/initrd and cmdline when requested, reads/increments boot count, optionally triggers sysrq crash on configured intervals, writes count, waits for system boot completion, and appends `systemd-analyze` output.

State and persistence behavior: Mutates host uptime, boot count file, optional kexec loaded kernel, sysrq state, and analyze log.

Dependencies and integration points: Included by main loop. Depends on kernel images/initrds, kexec-tools for kexec mode, systemd, and Ansible reconnection.

Risks: Crash injection is destructive. Kexec path selection uses the first existing candidate and fails if none found. Count writes only update existing files in one branch and create on first run.

Test signals: Signals are host returns, count increments, analyze lines appended, and expected crash behavior under crash settings.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/reboot-limit/tasks/do-reboot.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/reboot-limit/tasks/handle-reboot-data.yml -->
# sources/test-tools/kdevops/playbooks/roles/reboot-limit/tasks/handle-reboot-data.yml

Purpose: post-processes or displays collected reboot-limit data after loop execution.

Important APIs/types/functions: modules `ansible.builtin.set_fact`, `ansible.builtin.file`, `ansible.builtin.stat`, `ansible.builtin.slurp`, `ansible.builtin.copy`, `ansible.builtin.command`, `ansible.builtin.lineinfile`; variables/facts `reboot_type_analyze_file`, `reboot_type_count_file`, `become_method`, `reboot_type_count`, `content`, `line`, `create`; tasks `Set reboot type specific file paths`, `Create the data collection directory for {{ reboot_type }} reboot type`, `Check if the {{ reboot_type }} reboot count file exists`, `Read last {{ reboot_type }} boot count`, `Set the current {{ reboot_type }} boot count into a variable`.

Control flow: Reads target or local logs, organizes data for reporting, and emits debug/summary output according to workflow tags.

State and persistence behavior: May create or update local result summaries but does not perform reboots.

Dependencies and integration points: Integrated with reboot-limit result handling tasks or workflow reporting.

Risks: Parsing depends on `systemd-analyze` output format and expected count log names.

Test signals: Signals are readable summaries and graceful behavior with missing optional logs.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/reboot-limit/tasks/handle-reboot-data.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/reboot-limit/tasks/install-deps/debian/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/reboot-limit/tasks/install-deps/debian/main.yml

Purpose: installs reboot-limit dependencies for debian, especially tools needed for reboot timing and optional kexec mode.

Important APIs/types/functions: modules `ansible.builtin.apt`; variables/facts `become_method`, `update_cache`; tasks `Install kexec-tools and dependencies for reboot-limit on Debian`.

Control flow: Uses the distro package manager to install the role package list.

State and persistence behavior: Mutates package state only.

Dependencies and integration points: Included by reboot-limit dependency dispatcher.

Risks: Missing `kexec-tools` or systemd utilities cause mode-specific failures later.

Test signals: Signal is package install success and availability of `kexec` when kexec mode is selected.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/reboot-limit/tasks/install-deps/debian/main.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/reboot-limit/tasks/install-deps/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/reboot-limit/tasks/install-deps/main.yml

Purpose: dispatches reboot-limit dependency installation by OS family.

Important APIs/types/functions: modules `ansible.builtin.import_tasks`; tasks `Reboot-limit distribution specific setup`.

Control flow: Includes Debian, RedHat, or Suse install task based on `ansible_os_family`.

State and persistence behavior: No direct state.

Dependencies and integration points: Called from reboot-limit main before loops.

Risks: Unsupported OS family gets no dependencies.

Test signals: Signals are expected include and later reboot task availability.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/reboot-limit/tasks/install-deps/main.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/reboot-limit/tasks/install-deps/redhat/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/reboot-limit/tasks/install-deps/redhat/main.yml

Purpose: installs reboot-limit dependencies for redhat, especially tools needed for reboot timing and optional kexec mode.

Important APIs/types/functions: modules `ansible.builtin.dnf`; variables/facts `become_method`, `update_cache`; tasks `Install kexec-tools and dependencies for reboot-limit on Red Hat`.

Control flow: Uses the distro package manager to install the role package list.

State and persistence behavior: Mutates package state only.

Dependencies and integration points: Included by reboot-limit dependency dispatcher.

Risks: Missing `kexec-tools` or systemd utilities cause mode-specific failures later.

Test signals: Signal is package install success and availability of `kexec` when kexec mode is selected.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/reboot-limit/tasks/install-deps/redhat/main.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/reboot-limit/tasks/install-deps/suse/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/reboot-limit/tasks/install-deps/suse/main.yml

Purpose: installs reboot-limit dependencies for suse, especially tools needed for reboot timing and optional kexec mode.

Important APIs/types/functions: modules `community.general.zypper`; variables/facts `become_method`, `update_cache`; tasks `Install kexec-tools and dependencies for reboot-limit on SUSE`.

Control flow: Uses the distro package manager to install the role package list.

State and persistence behavior: Mutates package state only.

Dependencies and integration points: Included by reboot-limit dependency dispatcher.

Risks: Missing `kexec-tools` or systemd utilities cause mode-specific failures later.

Test signals: Signal is package install success and availability of `kexec` when kexec mode is selected.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/reboot-limit/tasks/install-deps/suse/main.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/reboot-limit/tasks/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/reboot-limit/tasks/main.yml

Purpose: orchestrates repeated reboot tests, including optional regular-vs-kexec comparison, result directory setup, reset handling, loop execution, and result fetching.

Important APIs/types/functions: modules `ansible.builtin.include_vars`, `ansible.builtin.include_tasks`, `ansible.builtin.file`, `ansible.builtin.set_fact`, `ansible.builtin.fetch`; variables/facts `ignore_errors`, `with_first_found`, `skip`, `become_method`, `reboot_limit_analyze_file`, `reboot_limit_count_file`, `label`, `reboot_limit_local_results_dir`, `with_sequence`, `loop_var`; tasks `Import optional extra_args file`, `Install dependencies for reboot-limit`, `Create the reboot-limit data collection directory for each host`, `Create the regular reboot data collection directory for comparison mode`, `Create the kexec reboot data collection directory for comparison mode`.

Control flow: Loads extra vars, prepares data partition and dependencies, creates result dirs, sets analyze/count file facts, handles reset tags, creates local result dir, loops through `do-reboot.yml` or `do-reboot-compare.yml`, then fetches analyze/count logs.

State and persistence behavior: Persists boot count and systemd-analyze logs on targets plus copied results under `workflows/demos/reboot-limit/results`.

Dependencies and integration points: Depends on reboot-limit defaults, package deps, Ansible reboot connectivity, and optional kexec support.

Risks: Running this role intentionally disrupts hosts. Comparison mode changes paths but `reboot_limit_analyze_file` initially points at single-mode data.

Test signals: Signals are exact number of boot-count increments, fetched logs, successful reconnection after each reboot, and mode-specific result directories.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/reboot-limit/tasks/main.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/rxe/tasks/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/rxe/tasks/main.yml

Purpose: configures software RoCE (`rdma_rxe`) support by installing a udev rule and reloading udev so target devices are created.

Important APIs/types/functions: modules `ansible.builtin.include_vars`, `ansible.builtin.template`, `ansible.builtin.shell`; variables/facts `file`, `with_first_found`, `skip`, `failed_when`, `become_method`, `force`, `changed_when`; tasks `Include optional extra_vars`, `Insert a udev rule to create an rxe device`, `Reload the udev ruleset`.

Control flow: Loads optional extra vars, templates `99-rxe.rules` or equivalent udev rule, and triggers udev reload.

State and persistence behavior: Persists a udev rules file and affects device creation state.

Dependencies and integration points: Used by workflows needing RXE RDMA devices.

Risks: Incorrect udev rule paths differ by distro; reload without module/device validation may hide failures.

Test signals: Signals are installed rule, udev reload success, loaded rdma_rxe support, and visible RDMA device.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/rxe/tasks/main.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/selftests/defaults/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/selftests/defaults/main.yml

Purpose: defines Linux selftests source/build/run defaults, data paths, section toggles, timeout controls, and special target behavior.

Important APIs/types/functions: variables/facts `data_path`, `target_linux_tree`, `target_linux_dir_path`, `bootlinux_9p_host_path`, `kdevops_workflow_enable_selftests`, `kdevops_run_selftests`, `run_tests_on_failures`, `selftests_skip_run`, `selftests_skip_reboot`, `selftests_build_radix_tree`.

Control flow: Defaults guide dependency install, make targets, userspace/kernelspace splitting, and result collection in `selftests/tasks/main.yml`.

State and persistence behavior: No direct state; values determine what is built and run.

Dependencies and integration points: Consumed by the selftests workflow and 9p build path support.

Risks: Incorrect target toggles can build or run the wrong selftest subset. Timeout defaults affect false failures on slow hosts.

Test signals: Signals are expected target variables and matching make/run commands.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/selftests/defaults/main.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/selftests/scripts/add-suse-repo-if-not-found.sh -->
# sources/test-tools/kdevops/playbooks/roles/selftests/scripts/add-suse-repo-if-not-found.sh

Purpose: helper shell script for Suse selftests dependencies that adds a repository only when it is not already configured.

Important APIs/types/functions: shell commands and conditionals including `zypper`, `grep`, `exit`, `if`.

Control flow: Checks existing zypper repositories, adds the requested repository if absent, and exits with shell status.

State and persistence behavior: Mutates zypper repository configuration on Suse systems.

Dependencies and integration points: Called from Suse dependency tasks to enable packages needed by selftests.

Risks: Repository matching by text can miss aliases or equivalent URLs; adding external repos changes package resolution.

Test signals: Signals are idempotent rerun, repository present after first run, and zypper refresh/install success.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/selftests/scripts/add-suse-repo-if-not-found.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/selftests/tasks/install-deps/debian/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/selftests/tasks/install-deps/debian/main.yml

Purpose: installs Debian target dependencies required to build and run Linux kernel selftests.

Important APIs/types/functions: modules `ansible.builtin.apt`; variables/facts `become_method`, `update_cache`; tasks `Update apt cache`, `Install every single selftest build dependencies`.

Control flow: Uses OS-specific package tasks and, for Suse, repository setup where needed. The localhost variant runs once on the controller when 9p builds are enabled.

State and persistence behavior: Mutates package/repository state on targets or localhost.

Dependencies and integration points: Included by `selftests/tasks/install-deps/main.yml` or directly for localhost 9p builds.

Risks: Dependency drift is common across kernel selftests; missing libraries often appear as make failures rather than install failures.

Test signals: Signals are successful package install, selftests build success, and availability of special tools such as configfs/radix-tree dependencies.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/selftests/tasks/install-deps/debian/main.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/selftests/tasks/install-deps/main-localhost.yml -->
# sources/test-tools/kdevops/playbooks/roles/selftests/tasks/install-deps/main-localhost.yml

Purpose: installs localhost dependencies for 9p selftests builds required to build and run Linux kernel selftests.

Important APIs/types/functions: modules `ansible.builtin.import_tasks`; tasks `Debian-specific setup for localhost`.

Control flow: Uses OS-specific package tasks and, for Suse, repository setup where needed. The localhost variant runs once on the controller when 9p builds are enabled.

State and persistence behavior: Mutates package/repository state on targets or localhost.

Dependencies and integration points: Included by `selftests/tasks/install-deps/main.yml` or directly for localhost 9p builds.

Risks: Dependency drift is common across kernel selftests; missing libraries often appear as make failures rather than install failures.

Test signals: Signals are successful package install, selftests build success, and availability of special tools such as configfs/radix-tree dependencies.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/selftests/tasks/install-deps/main-localhost.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/selftests/tasks/install-deps/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/selftests/tasks/install-deps/main.yml

Purpose: dispatches target-side Linux selftests dependency installation by OS family.

Important APIs/types/functions: modules `ansible.builtin.import_tasks`; tasks `Oscheck distribution ospecific setup`.

Control flow: Includes Debian, RedHat, or Suse task files based on facts.

State and persistence behavior: No direct state.

Dependencies and integration points: Called at the start of `selftests/tasks/main.yml`.

Risks: Unsupported OS families skip dependency setup.

Test signals: Signals are expected include and subsequent selftests build readiness.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/selftests/tasks/install-deps/main.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/selftests/tasks/install-deps/redhat/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/selftests/tasks/install-deps/redhat/main.yml

Purpose: installs RedHat target dependencies required to build and run Linux kernel selftests.

Important APIs/types/functions: modules `ansible.builtin.dnf`; variables/facts `become_method`, `update_cache`, `packages`; tasks `Install every single selftest build dependencies`.

Control flow: Uses OS-specific package tasks and, for Suse, repository setup where needed. The localhost variant runs once on the controller when 9p builds are enabled.

State and persistence behavior: Mutates package/repository state on targets or localhost.

Dependencies and integration points: Included by `selftests/tasks/install-deps/main.yml` or directly for localhost 9p builds.

Risks: Dependency drift is common across kernel selftests; missing libraries often appear as make failures rather than install failures.

Test signals: Signals are successful package install, selftests build success, and availability of special tools such as configfs/radix-tree dependencies.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/selftests/tasks/install-deps/redhat/main.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/selftests/tasks/install-deps/suse/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/selftests/tasks/install-deps/suse/main.yml

Purpose: installs Suse target dependencies required to build and run Linux kernel selftests.

Important APIs/types/functions: modules `ansible.builtin.set_fact`, `ansible.builtin.package`; variables/facts `is_sle`, `is_leap`, `is_tumbleweed`, `is_sle10`, `is_sle11`, `is_sle12`, `is_sle15`, `is_sle10sp3`, `is_sle11sp1`, `is_sle11sp4`; tasks `Set generic SUSE specific distro facts`, `Set SLE specific version labels to make checks easier`, `Set SLE specific version labels to make checks easier when not SLE`, `Install every single selftest build dependencies`.

Control flow: Uses OS-specific package tasks and, for Suse, repository setup where needed. The localhost variant runs once on the controller when 9p builds are enabled.

State and persistence behavior: Mutates package/repository state on targets or localhost.

Dependencies and integration points: Included by `selftests/tasks/install-deps/main.yml` or directly for localhost 9p builds.

Risks: Dependency drift is common across kernel selftests; missing libraries often appear as make failures rather than install failures.

Test signals: Signals are successful package install, selftests build success, and availability of special tools such as configfs/radix-tree dependencies.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/selftests/tasks/install-deps/suse/main.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/selftests/tasks/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/selftests/tasks/main.yml

Purpose: builds, runs, collects, and validates Linux kernel selftests for the selected kdevops selftests workflow.

Important APIs/types/functions: modules `ansible.builtin.include_vars`, `ansible.builtin.include_tasks`, `ansible.builtin.import_tasks`, `ansible.builtin.set_fact`, `ansible.builtin.debug`, `ansible.builtin.fail`, `ansible.builtin.file`, `ansible.builtin.command`; variables/facts `ignore_errors`, `with_first_found`, `skip`, `is_selftest_xarray`, `is_selftest_maple`, `is_selftest_vma`, `selftest_xarray`, `selftest_maple`, `selftest_vma`, `selftest_userspace`; tasks `Import optional extra_args file`, `Install dependencies`, `Install dependencies to build Linux selftests on host`, `Check if this node is in charge of running kernel or userspace tests`, `Check if this node is in charge of userspace tests`.

Control flow: Loads extra vars and deps, classifies hosts into userspace special tests versus kernelspace, prepares firmware/configfs/data, computes make targets, builds selftests on target or localhost 9p, installs built tests, runs special radix-tree/userspace/kernelspace commands, gathers dmesg/TAP/log files, fetches results by kernel, and fails if TAP logs contain `not ok`.

State and persistence behavior: Persists built selftests under data paths, installed selftest workdir, local result trees under `workflows/selftests/results`, watchdog marker files, dmesg/tap/userspace/module logs, and failure facts.

Dependencies and integration points: Depends on kernel source tree paths, make, distro deps, 9p sharing when enabled, host naming conventions for xarray/maple/vma, and workflow variables.

Risks: There is a duplicate `Build selftests` task. Host-name-derived target selection is brittle. TAP failure scan is simple substring matching and may overmatch comments. Cleaning last-run can remove concurrent data.

Test signals: Signals are build/install success, created logs per host, fetched results under last kernel, absence/presence of TAP `not ok`, and correct userspace/kernelspace routing.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/selftests/tasks/main.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/siw/tasks/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/siw/tasks/main.yml

Purpose: configures Soft-iWARP (`siw`) device creation through udev.

Important APIs/types/functions: modules `ansible.builtin.include_vars`, `ansible.builtin.template`, `ansible.builtin.shell`; variables/facts `ignore_errors`, `with_first_found`, `skip`, `become_method`, `force`; tasks `Import optional extra_args file`, `Insert udev rule to create siw device on the target host`, `Force the target host to reload its udev ruleset`.

Control flow: Loads optional extra vars, templates `/usr/lib/udev/rules.d/99-siw.rules`, then runs `udevadm control --reload && udevadm trigger`.

State and persistence behavior: Persists a udev rules file and triggers device-rule application.

Dependencies and integration points: Used by RDMA/NFS or storage workflows needing SIW.

Risks: Hard-coded udev rules directory may not match every distro; no explicit validation of resulting siw device.

Test signals: Signals are installed rule, successful udev reload, and expected RDMA device creation.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/siw/tasks/main.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/smbd/defaults/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/smbd/defaults/main.yml

Purpose: sets the default SMB share label used by the Samba server role and share templates.

Important APIs/types/functions: variables/facts `smbd_share_label`.

Control flow: Default variable is consumed by SMB configuration templates and add-share role.

State and persistence behavior: No direct state.

Dependencies and integration points: Integrated with `smbd/tasks/main.yml` and `smbd_add_share`.

Risks: Changing the label changes share naming expected by clients.

Test signals: Signal is rendered smb.conf with the expected share label.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/smbd/defaults/main.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/smbd/tasks/install-deps/debian/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/smbd/tasks/install-deps/debian/main.yml

Purpose: installs Samba server dependencies and filesystem tools for debian family systems.

Important APIs/types/functions: modules `ansible.builtin.include_vars`, `ansible.builtin.set_fact`, `ansible.builtin.apt`; variables/facts `params`, `fsprogs`, `smbd_packages`, `become_method`, `update_cache`; tasks `Get OS-specific variables`, `Determine which fsprogs package is needed for "{{ smbd_share_fstype }}"`, `Add {{ fsprogs }} to the smbd packages list`, `Install smbd dependencies`.

Control flow: Loads OS vars, derives fsprogs from `smbd_share_fstype`, appends it to `smbd_packages`, and installs packages with apt/dnf/package.

State and persistence behavior: Mutates package state and transient package-list facts.

Dependencies and integration points: Included by `smbd/tasks/main.yml` and dispatcher.

Risks: Unknown fs type can omit mkfs tools. RedHat task uses retries; Debian updates cache.

Test signals: Signals are installed Samba utilities and successful filesystem setup later.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/smbd/tasks/install-deps/debian/main.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/smbd/tasks/install-deps/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/smbd/tasks/install-deps/main.yml

Purpose: dispatches Samba dependency installation by OS family.

Important APIs/types/functions: modules `ansible.builtin.include_tasks`; tasks `Debian-specific set up`, `SuSE-specific set up`, `Red Hat-specific set up`.

Control flow: Includes Debian, Suse, or RedHat task file based on `ansible_os_family`.

State and persistence behavior: No direct state.

Dependencies and integration points: Used by roles that call the install-deps entrypoint instead of main directly.

Risks: Unsupported OS family receives no packages.

Test signals: Signal is expected include selection.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/smbd/tasks/install-deps/main.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/smbd/tasks/install-deps/redhat/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/smbd/tasks/install-deps/redhat/main.yml

Purpose: installs Samba server dependencies and filesystem tools for redhat family systems.

Important APIs/types/functions: modules `ansible.builtin.include_vars`, `ansible.builtin.set_fact`, `ansible.builtin.dnf`; variables/facts `params`, `fsprogs`, `smbd_packages`, `become_method`, `update_cache`, `retries`, `delay`, `until`; tasks `Get OS-specific variables`, `Determine which fsprogs package is needed for "{{ smbd_share_fstype }}"`, `Add {{ fsprogs }} to the smbd packages list`, `Install smbd dependencies`.

Control flow: Loads OS vars, derives fsprogs from `smbd_share_fstype`, appends it to `smbd_packages`, and installs packages with apt/dnf/package.

State and persistence behavior: Mutates package state and transient package-list facts.

Dependencies and integration points: Included by `smbd/tasks/main.yml` and dispatcher.

Risks: Unknown fs type can omit mkfs tools. RedHat task uses retries; Debian updates cache.

Test signals: Signals are installed Samba utilities and successful filesystem setup later.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/smbd/tasks/install-deps/redhat/main.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/smbd/tasks/install-deps/suse/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/smbd/tasks/install-deps/suse/main.yml

Purpose: installs Samba server dependencies and filesystem tools for suse family systems.

Important APIs/types/functions: modules `ansible.builtin.include_vars`, `ansible.builtin.set_fact`, `ansible.builtin.package`; variables/facts `params`, `fsprogs`, `smbd_packages`, `become_method`; tasks `Get OS-specific variables`, `Determine which fsprogs package is needed for "{{ smbd_share_fstype }}"`, `Add {{ fsprogs }} to the smbd packages list`, `Install smbd dependencies`.

Control flow: Loads OS vars, derives fsprogs from `smbd_share_fstype`, appends it to `smbd_packages`, and installs packages with apt/dnf/package.

State and persistence behavior: Mutates package state and transient package-list facts.

Dependencies and integration points: Included by `smbd/tasks/main.yml` and dispatcher.

Risks: Unknown fs type can omit mkfs tools. RedHat task uses retries; Debian updates cache.

Test signals: Signals are installed Samba utilities and successful filesystem setup later.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/smbd/tasks/install-deps/suse/main.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/smbd/tasks/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/smbd/tasks/main.yml

Purpose: configures a Samba server with package dependencies, share root storage, SELinux/firewall access, service startup, and root SMB password.

Important APIs/types/functions: modules `ansible.builtin.include_tasks`, `ansible.builtin.template`, `ansible.builtin.include_role`, `ansible.builtin.file`, `ansible.builtin.command`, `ansible.posix.seboolean`, `ansible.builtin.service_facts`, `ansible.posix.firewalld`; variables/facts `become_flags`, `become_method`, `volume_group_name`, `changed_when`, `failed_when`, `persistent`, `service`, `permanent`, `immediate`, `enabled`; tasks `Debian-specific setup`, `SuSE-specific setup`, `Red Hat-specific setup`, `Create smb.conf`, `Set up a volume group on local block devices`.

Control flow: Dispatches distro deps, templates `/etc/samba/smb.conf`, sets up VG `shares`, creates share root, enables SELinux boolean, opens firewalld samba service, starts `smb`, and runs `smbpasswd -a root -s`.

State and persistence behavior: Mutates packages, Samba config, LVM/storage, share directory, SELinux booleans, firewalld rules, systemd service state, and Samba password database.

Dependencies and integration points: Foundation for `smbd_add_share` and SMB workflows. Depends on templates, `smb_root_pw`, volume_group role, and distro package vars.

Risks: Piping password through shell can expose secrets in process/task logs. Service name `smb` may differ by distro. Re-running `smbpasswd -a` may fail if user already exists unless Samba accepts update semantics.

Test signals: Signals are valid `testparm`, active smb service, accessible share root, SELinux/firewall allowing clients, and successful SMB authentication.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/smbd/tasks/main.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/smbd/vars/Debian.yml -->
# sources/test-tools/kdevops/playbooks/roles/smbd/vars/Debian.yml

Purpose: defines Debian-specific Samba package lists and filesystem userspace tool mappings.

Important APIs/types/functions: variables/facts `smbd_packages`, `fstype_userspace_progs`, `btrfs`, `ext4`, `xfs`.

Control flow: Loaded by SMB install-deps tasks through `first_found`.

State and persistence behavior: No runtime state beyond variable values.

Dependencies and integration points: Supports package installation for `smbd` role.

Risks: Incorrect package names block Samba or formatting setup; Suse btrfs package name differs.

Test signals: Signals are successful install for configured `smbd_share_fstype`.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/smbd/vars/Debian.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/smbd/vars/RedHat.yml -->
# sources/test-tools/kdevops/playbooks/roles/smbd/vars/RedHat.yml

Purpose: defines RedHat-specific Samba package lists and filesystem userspace tool mappings.

Important APIs/types/functions: variables/facts `smbd_packages`, `fstype_userspace_progs`, `btrfs`, `ext4`, `xfs`.

Control flow: Loaded by SMB install-deps tasks through `first_found`.

State and persistence behavior: No runtime state beyond variable values.

Dependencies and integration points: Supports package installation for `smbd` role.

Risks: Incorrect package names block Samba or formatting setup; Suse btrfs package name differs.

Test signals: Signals are successful install for configured `smbd_share_fstype`.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/smbd/vars/RedHat.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/smbd/vars/Suse.yml -->
# sources/test-tools/kdevops/playbooks/roles/smbd/vars/Suse.yml

Purpose: defines Suse-specific Samba package lists and filesystem userspace tool mappings.

Important APIs/types/functions: variables/facts `smbd_packages`, `fstype_userspace_progs`, `btrfs`, `ext4`, `xfs`.

Control flow: Loaded by SMB install-deps tasks through `first_found`.

State and persistence behavior: No runtime state beyond variable values.

Dependencies and integration points: Supports package installation for `smbd` role.

Risks: Incorrect package names block Samba or formatting setup; Suse btrfs package name differs.

Test signals: Signals are successful install for configured `smbd_share_fstype`.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/smbd/vars/Suse.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/smbd_add_share/defaults/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/smbd_add_share/defaults/main.yml

Purpose: sets default ownership and mode for newly created SMB share directories.

Important APIs/types/functions: variables/facts `share_user`, `share_group`, `share_mode`.

Control flow: Defaults feed the permission task in `smbd_add_share/tasks/main.yml`.

State and persistence behavior: No direct state; controls filesystem metadata when task runs.

Dependencies and integration points: Used by SMB share addition workflows.

Risks: Mode `u=rwx,g=rwx,o=rwxt` is broad and sticky; intended semantics should be verified for multi-user tests.

Test signals: Signal is created share directory with expected owner/group/mode.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/smbd_add_share/defaults/main.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/smbd_add_share/tasks/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/smbd_add_share/tasks/main.yml

Purpose: adds one Samba share backed by LVM or tmpfs storage and reloads the SMB service.

Important APIs/types/functions: modules `community.general.lvol`, `community.general.filesystem`, `ansible.posix.mount`, `ansible.builtin.file`, `ansible.builtin.command`, `ansible.builtin.blockinfile`, `ansible.builtin.systemd_service`; variables/facts `become_flags`, `become_method`, `vg`, `lv`, `size`, `fstype`, `dev`, `throttle`, `changed_when`, `failed_when`; tasks `Create a new LVM partition`, `Format new volume for {{ share_fstype }}`, `Mount volume under {{ smbd_share_path }}`, `Mount tmpfs under {{ smbd_share_path }}`, `Ensure {{ share_volname }} has correct permissions`.

Control flow: Delegates to the server, creates/formats/mounts an LVM volume or tmpfs, sets permissions, restores SELinux context, inserts a templated share block into `/etc/samba/smb.conf` with `blockinfile`, and reloads `smb.service`.

State and persistence behavior: Persists LV/filesystem/mount or tmpfs, share directory metadata, smb.conf block, SELinux relabeling, and service reload.

Dependencies and integration points: Depends on configured `server_host`, `share_volname`, `share_fstype`, templates, VG `shares`, and a running Samba setup.

Risks: Parallel fstab and smb.conf edits are throttled but still sensitive to inventory concurrency. tmpfs shares are volatile. No validation with `testparm` occurs before reload.

Test signals: Signals are mounted path, smb.conf block, successful reload, `testparm`, and client access to the share.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/smbd_add_share/tasks/main.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/steady_state/defaults/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/steady_state/defaults/main.yml

Purpose: defines SSD steady-state prefill and fio run criteria: data path, device, block size, iodepth, jobs, runtime, IOPS/BW mean and slope thresholds, and prefill options.

Important APIs/types/functions: variables/facts `steady_state_data`, `ssd_steady_state_device`, `ssd_steady_state_prefill_blocksize`, `ssd_steady_state_iodepth`, `ssd_steady_state_numjobs`, `ssd_steady_state_prefill_loop`, `ssd_steady_state_runtime`, `ssd_steady_state_iops_mean_limit`, `ssd_steady_state_iops_mean_dur`, `ssd_steady_state_iops_slope`.

Control flow: Defaults are consumed by steady-state workflow tasks outside this subset to build fio commands and acceptance gates.

State and persistence behavior: No direct state; values shape fio workload and result thresholds.

Dependencies and integration points: Integrated with storage performance workflows that need preconditioning before measurement.

Risks: Long default runtime and repeated prefill can consume device endurance/time. Device default `/dev/null` is safe but not useful unless overridden.

Test signals: Signals are generated fio command arguments matching defaults and threshold evaluation over collected metrics.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/steady_state/defaults/main.yml -->
