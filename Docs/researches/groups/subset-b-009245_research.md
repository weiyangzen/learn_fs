# subset-b-009245 research

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/python/workflows/dynamic-kconfig/gen-dynamic-pci.py -->
# sources/test-tools/kdevops/playbooks/python/workflows/dynamic-kconfig/gen-dynamic-pci.py

Purpose: Generates Kconfig entries for PCIe passthrough candidates from `lspci -Dvmmm` output. It enriches labels with sysfs data for NVMe and GPU devices and writes Kconfig directly to stdout.

Key APIs and flow: `main()` validates the input file, scans tagged `Slot`, `SDevice`, `IOMMUGroup`, `Vendor`, and `Device` lines, and calls `add_new_device()` whenever a complete device record ends. `add_new_device()` parses PCI slot topology, assigns sequential config ids, and delegates to `add_pcie_kconfig_entry()`. Device naming goes through `get_kconfig_device_name()`, with helpers for NVMe model/firmware and GPU model/memory display names.

State, dependencies, integration: Reads `/sys/bus/pci/devices`, deletes the input file with `os.unlink()`, and depends only on Python stdlib. It integrates with dynamic-kconfig generation for libvirt PCIe passthrough.

Risks and test signals: It mutates input by deleting it, assumes first NVMe child, catches GPU memory read failures broadly, and `is_gpu_device()` treats regex-like strings as plain substrings. Tests should cover malformed slots, missing IOMMUGroup, NVMe/sysfs absence, GPU naming, quoting, and input deletion expectations.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/python/workflows/dynamic-kconfig/gen-dynamic-pci.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/python/workflows/fio-tests/fio-compare.py -->
# sources/test-tools/kdevops/playbooks/python/workflows/fio-tests/fio-compare.py

Purpose: Compares fio JSON result directories for baseline versus development configurations and emits PNG charts plus a text summary.

Key APIs and flow: `parse_fio_json()` extracts first-job read/write bandwidth, IOPS, and mean latency from fio JSON. `extract_test_params()` decodes block size, IO depth, job count, and pattern from `results_*.json` filenames. `load_results()` builds pandas DataFrames per config. Plotters create side-by-side bars and percentage delta charts, while `generate_summary_report()` writes average metric changes.

State, dependencies, integration: Reads only local result files, creates an output directory, writes PNGs and `<prefix>_summary.txt`. Depends on pandas and matplotlib. Intended for fio workflow A/B analysis.

Risks and test signals: Only the first fio job is used; text-result fallback is discovered but skipped; filename parsing can omit required columns and break groupbys; latency improvement direction differs from throughput. Tests should use minimal fio JSON fixtures, mismatched config sets, zero baselines, malformed filenames, and missing directories.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/python/workflows/fio-tests/fio-compare.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/python/workflows/fio-tests/fio-multi-fs-compare.py -->
# sources/test-tools/kdevops/playbooks/python/workflows/fio-tests/fio-multi-fs-compare.py

Purpose: Aggregates fio JSON results across filesystem configurations and produces overview, block-size heatmap, IO-depth scaling, and CSV summary artifacts.

Key APIs and flow: `collect_results()` recursively finds JSON files, infers filesystem from path or hostname-like path components, parses metrics via `parse_fio_json()`, and returns a DataFrame. `create_filesystem_comparison_plots()` groups by filesystem, plots average bandwidth/IOPS/latency, optional block-size heatmaps, optional IO-depth scaling, and writes `filesystem_performance_summary.csv`.

State, dependencies, integration: Reads `**/*.json`, writes several fixed-name PNGs and one CSV under the output directory. Depends on pandas, matplotlib, seaborn, numpy. It integrates with fio multi-filesystem result trees.

Risks and test signals: Filesystem inference is heuristic and path-order dependent; `--title` is parsed but unused; first fio job only; `iodepth` is stored as a string until plotting. Tests should cover nested host directories, unknown filesystems, missing job options, single-filesystem runs, and no-result exits.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/python/workflows/fio-tests/fio-multi-fs-compare.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/python/workflows/fio-tests/fio-plot.py -->
# sources/test-tools/kdevops/playbooks/python/workflows/fio-tests/fio-plot.py

Purpose: Creates a compact set of fio performance plots for one result directory: bandwidth heatmap, IOPS scaling, latency distribution, and pattern comparison.

Key APIs and flow: `create_performance_matrix()` loads `results_*.json`, uses `parse_fio_json()` for first-job metrics, and merges filename-derived parameters from `extract_test_params()`. Plot helpers guard against missing columns and save prefixed PNGs. `main()` validates inputs, creates output directory, exits on no valid results, and invokes all plotters.

State, dependencies, integration: The script is stateless beyond generated PNG files. It uses pandas and matplotlib and expects kdevops fio result filenames with `bs`, `iodepth`, `jobs`, and workload pattern tokens.

Risks and test signals: Text fallback is intentionally skipped; malformed numeric tokens raise `ValueError`; missing pattern data suppresses some plots; only mean latency is considered. Tests should include read-only, write-only, mixed, missing-latency, malformed filename, and empty-directory fixtures.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/python/workflows/fio-tests/fio-plot.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/python/workflows/fio-tests/fio-trend-analysis.py -->
# sources/test-tools/kdevops/playbooks/python/workflows/fio-tests/fio-trend-analysis.py

Purpose: Performs deeper fio trend analysis across block size, IO depth, latency percentiles, and metric correlations.

Key APIs and flow: `parse_fio_json()` extracts read/write bandwidth, IOPS, mean/stddev/p95/p99 latency, and totals from the first fio job. `extract_test_params()` turns filename tokens into numeric block size, IO depth, job count, and pattern. `load_all_results()` returns a DataFrame, then plotting functions save `block_size_trends.png`, `io_depth_scaling.png`, `latency_percentiles.png`, and `correlation_heatmap.png`.

State, dependencies, integration: Reads local `results_*.json`, writes fixed output files, and depends on pandas, matplotlib, seaborn, and numpy. It is a post-processing tool for fio test sweeps.

Risks and test signals: Block-size parsing supports only bare numbers and `k`; text results are skipped; correlation assumes all numeric columns exist; zero latency values are filtered. Tests should exercise missing percentile fields, non-k block sizes, partial pattern sets, and one-row correlations.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/python/workflows/fio-tests/fio-trend-analysis.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/python/workflows/fstests/augment_expunge_list.py -->
# sources/test-tools/kdevops/playbooks/python/workflows/fstests/augment_expunge_list.py

Purpose: Scans fstests result trees for `.bad` and `.dmesg` failures and augments expunge-list files for oscheck/fstests reruns.

Key APIs and flow: `main()` loads top-level `.config`, walks the results tree, derives hostname/kernel/section/group/test from path layout, builds `group/test` failure lines, chooses an expunge output path, creates missing directories, appends new failures only once, and finally calls `sort-expunges.sh`. Helpers parse kconfig-like booleans and append lines.

State, dependencies, integration: Mutates expunge directories under the requested output root and shells out to the kdevops sort script. It depends on `.config`, filesystem layout conventions, and optional openSUSE/KOTD settings.

Risks and test signals: Path parsing is positional; `base_kernel` is referenced after conditional initialization when kernels do not end with `+`; duplicate detection is substring-like; disabled legacy branch remains. Tests should cover new set creation, existing file append, base-kernel fallback, openSUSE shortcuts, and malformed result paths.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/python/workflows/fstests/augment_expunge_list.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/python/workflows/fstests/bad_files_summary.py -->
# sources/test-tools/kdevops/playbooks/python/workflows/fstests/bad_files_summary.py

Purpose: Produces a simple text or HTML summary of fstests `.bad` files grouped by section for a filesystem.

Key APIs and flow: `main()` walks the result directory, filters `.bad` files, derives kernel, section, test type, and test number from positional path segments, stores `test_type/test_number` entries per section, then dispatches to `parse_results_ascii()` or `parse_results_html()`.

State, dependencies, integration: Reads result files but writes only to stdout. Depends on Python stdlib and expected kdevops fstests path layout such as `results/oscheck-xfs/<kernel>/<fs>/<group>/<test>.out.bad`.

Risks and test signals: HTML is manually concatenated without escaping and has table nesting quirks; kernel is whichever bad file was seen last; positional parsing fails on unexpected layouts. Tests should cover no failures, multiple sections, HTML output, filenames with extra dots, and special characters in section names.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/python/workflows/fstests/bad_files_summary.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/python/workflows/fstests/fstests-checktime-distribution.py -->
# sources/test-tools/kdevops/playbooks/python/workflows/fstests/fstests-checktime-distribution.py

Purpose: Converts fstests `check.time` files into `.distribution` CSV files showing runtime buckets, counts, and percentages.

Key APIs and flow: `main()` walks a results directory, finds files ending in `check.time`, removes any existing `.distribution`, parses lines matching `group/number time`, counts tests per integer time value, sorts by runtime with `OrderedDict`, and writes `time,count,percentage` rows.

State, dependencies, integration: Persists one sibling `<check.time>.distribution` file per input. Uses Python stdlib only; constants for `sort-expunges.sh` are present but unused. It integrates with fstests runtime analysis.

Risks and test signals: Division by zero occurs for empty or wholly unparsable files; files are opened without context managers; non-word group names are ignored by regex; unused variables suggest drift. Tests should cover normal check.time, empty input, malformed lines, repeated runtimes, and pre-existing distribution replacement.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/python/workflows/fstests/fstests-checktime-distribution.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/python/workflows/fstests/gen_results_summary -->
# sources/test-tools/kdevops/playbooks/python/workflows/fstests/gen_results_summary

Purpose: Command-line wrapper around `gen_results_summary.py` for generating text summaries and optional merged xUnit XML from fstests result directories.

Key APIs and flow: `main()` parses `results_dir`, `--merge_file`, `--output_file`, `--verbose`, `--print_section`, and `--results_file`, then calls `gen_results_summary()`. If no matching result files are found, it exits with a message.

State, dependencies, integration: Does not implement parsing itself; all state changes are delegated to the module, which may write output and merged XML files. It imports from local `gen_results_summary`, so execution depends on the script directory being importable.

Risks and test signals: The wrapper uses `sys.exit(string)` for no-results, which reports failure with stderr text. It has no shebang environment portability beyond `/usr/bin/python3`. Tests should verify argument mapping, custom results file names, no-results exit behavior, and successful pass-through with output and merge files.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/python/workflows/fstests/gen_results_summary -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/python/workflows/fstests/gen_results_summary.py -->
# sources/test-tools/kdevops/playbooks/python/workflows/fstests/gen_results_summary.py

Purpose: Library for scanning fstests xUnit results, printing human-readable summaries, and optionally merging xUnit test suites.

Key APIs and flow: `get_results()` finds result XML files; `parse_timestamp()` orders suites; property helpers read and remove JUnit properties; `print_summary()` writes per-suite counts and either verbose test rows or failed/error test lists. `gen_results_summary()` loads all reports, copies properties from the first report, optionally applies `ltm-run-stats`, prints header, sorted summaries, totals, trailer, and writes an atomic-ish merged XML via `.new`/`.bak`.

State, dependencies, integration: Depends on `junitparser`. Reads result XML and optional `ltm-run-stats`; may write text output and merged XML. Integrated by the wrapper script and fstests reporting workflows.

Risks and test signals: Assumes `reports[0].child(Properties)` exists; `failed_tests()` only handles direct `Failure` result shape and is unused; `sys.exc_clear()` is Python 2 legacy but guarded. Tests should cover timezone timestamps, LTM mode, missing properties, verbose small suites, merge backup behavior, skipped/errors/failures.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/python/workflows/fstests/gen_results_summary.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/python/workflows/fstests/get_new_expunge_files.py -->
# sources/test-tools/kdevops/playbooks/python/workflows/fstests/get_new_expunge_files.py

Purpose: Lists expunge files for a filesystem that are not tracked by git.

Key APIs and flow: `main()` parses filesystem and expunge directory, walks all files, filters paths containing the filesystem string, calls `git.is_new_file()`, strips a leading `../` segment for display, and prints new files.

State, dependencies, integration: Reads the filesystem and invokes local `lib.git`, which shells out to `git status -s`. It writes only stdout and is meant to help identify newly generated expunge sections.

Risks and test signals: Filtering uses substring matching across the full path, which can include false positives; `subprocess` and `pwd` are unused; a git timeout returns the string `"Timeout"`, which is truthy and will be printed as if new. Tests should mock `git.is_new_file()`, cover timeout behavior, `../` shortening, missing directories, and filesystem names that appear in parent paths.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/python/workflows/fstests/get_new_expunge_files.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/python/workflows/fstests/lib/git.py -->
# sources/test-tools/kdevops/playbooks/python/workflows/fstests/lib/git.py

Purpose: Minimal git helper module used by fstests expunge tooling to determine whether a file is untracked.

Key APIs and flow: Defines `GitError`, `ExecutionError`, and `TimeoutExpired` exception classes plus `_check()` for return-code enforcement. `is_new_file(file)` runs `git status -s <file>` with a one-second timeout and returns `True` if output starts with `??`, `False` for nonzero git exit or tracked files, and the string `"Timeout"` if `communicate()` times out.

State, dependencies, integration: Uses `subprocess.Popen`; it does not mutate repository state. Integrated by `get_new_expunge_files.py`.

Risks and test signals: Timeout returns a truthy string instead of raising or returning `False`; custom `TimeoutExpired.__init__()` returns a value ineffectively; `_check()` and imported `os` are unused; process cleanup is incomplete on timeout. Tests should mock git output for untracked/tracked/error/timeout and assert callers do not misinterpret timeout.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/python/workflows/fstests/lib/git.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/python/workflows/fstests/xunit_merge_all.py -->
# sources/test-tools/kdevops/playbooks/python/workflows/fstests/xunit_merge_all.py

Purpose: Merges all xUnit XML files in a result tree into a single JUnit test suite.

Key APIs and flow: `get_test_suite()` loads a file with `JUnitXml.fromfile()` and requires the parsed object to be a `TestSuite`. `merge_ts()` appends test cases from one suite to another and updates statistics. `main()` walks the result directory, processes every `.xml`, initializes the aggregate from the first suite, merges the rest, and writes the output.

State, dependencies, integration: Reads XML files and writes the requested output file. Depends on `junitparser`. Used in fstests reporting when downstream consumers want one xUnit file.

Risks and test signals: It rejects `JUnitXml` containers even if they are valid JUnit XML; merge count excludes the first file; ordering follows `os.walk()` order; parse errors other than IOError are not handled. Tests should cover one file, multiple suites, container XML, malformed XML, no XML files, and statistics updates.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/python/workflows/fstests/xunit_merge_all.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/python/workflows/sysbench/sysbench-tps-compare.py -->
# sources/test-tools/kdevops/playbooks/python/workflows/sysbench/sysbench-tps-compare.py

Purpose: Compares two sysbench text outputs by plotting transactions per second over time.

Key APIs and flow: `parse_line()` extracts `[ Ns ] ... tps: X` samples with regex. `read_sysbench_output()` parses all lines concurrently using `ThreadPoolExecutor`. `main()` supports optional input files, legends, matplotlib theme, output path, theme listing, and report interval scaling. It converts the x-axis to hours for runs longer than two hours, builds two pandas DataFrames, and saves an overlay scatter plot.

State, dependencies, integration: Reads two text files and writes one image. Depends on pandas and matplotlib. Used for sysbench A/B comparisons, with defaults tuned for MySQL doublewrite tests.

Risks and test signals: Empty parsed data causes `max()` failures; report interval multiplies already reported timestamps, which may be wrong if timestamps are absolute; no file-not-found handling. Tests should cover empty files, theme listing, long runs, report interval semantics, and irregular sysbench lines.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/python/workflows/sysbench/sysbench-tps-compare.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/python/workflows/sysbench/sysbench-tps-plot.py -->
# sources/test-tools/kdevops/playbooks/python/workflows/sysbench/sysbench-tps-plot.py

Purpose: Generates a single TPS-over-time plot from sysbench text output.

Key APIs and flow: `parse_line()` uses the same sysbench TPS regex as the comparator. `main()` reads the input file, parses lines through a `ThreadPoolExecutor`, exits on file-not-found or no TPS samples, switches the time axis to hours for long runs, constructs a DataFrame, plots points, and writes the output image.

State, dependencies, integration: Reads one text file and writes one PNG by default. Depends on pandas and matplotlib. It is a direct post-processing utility for sysbench workflow logs.

Risks and test signals: The help says text or JSON, but only text lines are parsed; broad use of `exit(1)` rather than `sys.exit`; no theme/backend selection; regex requires decimal TPS. Tests should cover valid logs, empty logs, integer TPS formats, long runs, and missing input.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/python/workflows/sysbench/sysbench-tps-plot.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/python/workflows/sysbench/sysbench-tps-variance.py -->
# sources/test-tools/kdevops/playbooks/python/workflows/sysbench/sysbench-tps-variance.py

Purpose: Computes TPS distribution statistics and generates multiple variance/dispersion plots for one or two sysbench outputs.

Key APIs and flow: `extract_tps()` collects decimal TPS samples; `analyze_tps()` returns mean, median, standard deviation, and variance; `print_statistics()` logs them. Plot functions create histograms, box plots, KDE density, combined histogram/density, normal bell curves, histogram plus bell curve, variance bars, and outlier scatter. `main()` parses optional second file, labels, output directory, colors, applies dark theme, and runs every plotter.

State, dependencies, integration: Reads text files and writes fixed-name images to `--dir`. Depends on numpy, matplotlib, seaborn, and scipy. It is a richer sysbench variability analyzer.

Risks and test signals: Several functions call `min(tps_values2)` before checking if the second dataset exists; `plt.show()` is called after saves; output path concatenates strings and expects trailing slash; empty datasets produce numpy warnings or failures. Tests should cover single-file mode, empty inputs, output dirs with/without slash, and zero-variance data.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/python/workflows/sysbench/sysbench-tps-variance.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/rcloud.yml -->
# sources/test-tools/kdevops/playbooks/rcloud.yml

Purpose: Installs and configures the `rcloud` REST API server as a systemd service on localhost for kdevops VM management.

Key APIs and flow: The play validates that the Rust-built `workflows/rcloud/target/release/rcloud` binary exists, copies it to `/usr/local/bin`, creates a system user and `/etc/rcloud`, writes `/etc/systemd/system/rcloud.service`, adds the service user to the libvirt qemu group, reloads systemd, enables the service, derives a port from `rcloud_server_bind`, and prints health-check commands.

State, dependencies, integration: Mutates host system paths, users, groups, and systemd state. The service depends on libvirtd and environment variables such as `KDEVOPS_ROOT`, storage pool path, base images directory, libvirt URI, and bridge name.

Risks and test signals: It enables but does not start the service; port extraction assumes `host:port`; hardening read/write paths must match storage layout; group name defaults may vary by distro. Tests should run Ansible check mode where possible and validate rendered service content.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/rcloud.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/reboot-limit.yml -->
# sources/test-tools/kdevops/playbooks/reboot-limit.yml

Purpose: Thin playbook entry point for the reboot-limit workflow.

Key APIs and flow: Defines one play, `Configure and run the reboot-limit workflow`, targeting the `baseline:dev` inventory groups and applying the `reboot-limit` role. There are no inline variables or tasks.

State, dependencies, integration: All behavior is delegated to the `reboot-limit` role. This file integrates the role into the standard kdevops baseline/development host split and serves as the playbook invoked by workflow commands.

Risks and test signals: Host pattern requires inventory groups named `baseline` or `dev`; no guard exists for missing role variables because they are role-owned; debugging requires following the role. Tests should validate Ansible syntax, inventory matching, and role variable defaults.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/reboot-limit.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/ai_collect_results/files/analyze_results.py -->
# sources/test-tools/kdevops/playbooks/roles/ai_collect_results/files/analyze_results.py

Purpose: Main AI benchmark analysis tool that loads Milvus benchmark JSON, collects DUT metadata, writes text/HTML reports, generates graphs, and saves consolidated JSON.

Key APIs and flow: `ResultsAnalyzer` owns state. Initialization creates the output directory and collects system, storage, virtualization, and filesystem details via `/proc`, `lsblk`, `nvme`, `systemd-detect-virt`, `dmesg`, and `df`. `load_results()` reads `results_*.json`. Summary and HTML methods aggregate insert, index, and query performance by node and filesystem config. `generate_graphs()` calls five plot methods for insert, query, index, matrix, and node/filesystem comparison. `analyze()` orchestrates all artifacts.

State, dependencies, integration: Writes `benchmark_summary.txt`, `benchmark_report.html`, graph images, and `consolidated_results.json`. Optional graph imports degrade gracefully. Called by `ai_collect_results` Ansible tasks.

Risks and test signals: HTML is string-built without escaping; local DUT info may describe the collector, not remote nodes; filename parsing is policy-heavy; external commands may need privileges. Tests should use fixture JSON for baseline/dev, disabled graph libs, missing fields, and mocked subprocess results.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/ai_collect_results/files/analyze_results.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/ai_collect_results/files/generate_better_graphs.py -->
# sources/test-tools/kdevops/playbooks/roles/ai_collect_results/files/generate_better_graphs.py

Purpose: Standalone AI benchmark graph generator focused on clearer QPS, latency, insert performance, and summary-table visuals.

Key APIs and flow: Filename helpers infer filesystem, node config, baseline/dev type, and iteration. `load_results()` enriches each `results_*.json` object. Chart functions aggregate query QPS and latency across top-k/batch combinations, compare baseline versus development bars, plot insert-rate distributions, and render a performance summary table image. `main()` loads results, creates the output directory, runs all charts, and prints counts.

State, dependencies, integration: Uses matplotlib Agg and writes `qps_comparison.png`, `latency_comparison.png`, `insert_performance.png`, and `performance_summary.png`. Depends on numpy and matplotlib; has a fallback `detect_filesystem()` that may SSH to `debian13-ai` but is not used by main flow.

Risks and test signals: Filename parsing is tailored to `debian13-ai-*`; best-query summary uses maxima rather than matched configurations; random jitter makes scatter placement nondeterministic. Tests should cover dev/baseline filename variants, missing query data, and no comparison pairs.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/ai_collect_results/files/generate_better_graphs.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/ai_collect_results/files/generate_graphs.py -->
# sources/test-tools/kdevops/playbooks/roles/ai_collect_results/files/generate_graphs.py

Purpose: Older/simple AI benchmark graph generator for insert trends and query-performance heatmaps.

Key APIs and flow: `_extract_filesystem_config()` and `_extract_node_info()` infer grouping from filenames or result `system_info`. `load_results()` reads `results_*.json`. `create_heatmap_analysis()` groups query QPS by filesystem config and writes `performance_heatmap.png`. `create_simple_performance_trends()` appears intended to group insert rates/times and write `performance_trends.png`.

State, dependencies, integration: Uses matplotlib Agg, numpy, and JSON result files; writes graphs to the provided output directory. It is copied by `ai_collect_results`, though comments now indicate graph generation is handled by `analyze_results.py`.

Risks and test signals: `create_simple_performance_trends()` references `fs_performance` without defining it after initializing `node_performance`, causing a `NameError` when insert data exists. The `Path` and `datetime` imports are unused. Tests should call both graph functions with minimal result fixtures and catch this regression.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/ai_collect_results/files/generate_graphs.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/ai_collect_results/files/generate_html_report.py -->
# sources/test-tools/kdevops/playbooks/roles/ai_collect_results/files/generate_html_report.py

Purpose: Generates a static Milvus benchmark HTML report that combines summary metadata, graph references, filesystem sections, and detailed result rows.

Key APIs and flow: `HTML_TEMPLATE` defines the full page. `load_summary()` reads `graphs/summary.json` if present. `load_results()` filters JSON files with insert/query data, infers filesystem/block size from filenames and JSON, computes average query QPS, and sorts rows. Helpers generate table rows, configuration summary, and graph image snippets. `generate_html_report()` decides whether multi-filesystem sections are shown and fills the template.

State, dependencies, integration: Reads result JSON and graph summary files, writes one HTML file, and references graph paths under `graphs/`. Called by the AI collection role after `analyze_results.py`.

Risks and test signals: Header/table column counts are inconsistent: the template has six headers while rows emit seven cells. HTML values are not escaped; missing `summary.json` leaves zero best metrics even when results exist. Tests should validate generated HTML structure for single- and multi-filesystem fixtures.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/ai_collect_results/files/generate_html_report.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/ai_collect_results/tasks/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/ai_collect_results/tasks/main.yml

Purpose: Ansible role tasks for collecting AI benchmark result JSON from remote hosts and generating local analysis artifacts.

Key APIs and flow: The role optionally includes `extra_vars.yaml`, sets local result/script directories on localhost, creates directories, copies analysis scripts, templates `analysis_config.json`, checks/fetches remote `results_*.json`, clears and recreates the local result directory, verifies collection, runs `analyze_results.py`, displays output, ensures graph directory, runs `generate_html_report.py`, and prints final paths.

State, dependencies, integration: Mutates local `workflows/ai/results` and `workflows/ai/scripts`, remote analysis directory, and fetched result files. Integrates Ansible `fetch`, local Python analyzers, and variables such as `ai_benchmark_results_dir` and `ai_benchmark_enable_graphing`.

Risks and test signals: It deletes the entire local results directory before collection; copied `generate_graphs.py` may be stale; extra-vars include always succeeds; ownership uses env `USER` for both owner and group. Tests should run syntax checks and fixture plays with no results, multiple hosts, graphing disabled, and analyzer failure.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/ai_collect_results/tasks/main.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/ai_destroy/tasks/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/ai_destroy/tasks/main.yml

Purpose: Destroys the AI benchmark environment by removing Milvus-related containers, Docker network, storage directories, benchmark results, and optionally images.

Key APIs and flow: Tasks optionally include extra vars, remove Milvus/MinIO/etcd containers with `community.docker.docker_container`, remove the Docker network, delete Docker data directories and benchmark results with `file: state=absent`, remove configured images with `docker_image`, and print completion.

State, dependencies, integration: Destructive host mutations gated mostly by `ai_milvus_docker`. Depends on community.docker collection and variables naming containers, images, network, and paths.

Risks and test signals: Several Docker cleanup steps use `failed_when: false`, so missing Docker or removal failures can be hidden; benchmark results are always removed; path variables must be correct to avoid deleting unintended directories. Tests should cover docker and non-docker modes, undefined variables, idempotent reruns, and check-mode behavior for file deletions.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/ai_destroy/tasks/main.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/ai_docker_storage/tasks/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/ai_docker_storage/tasks/main.yml

Purpose: Prepares a dedicated filesystem for Docker storage used by AI/Milvus deployments.

Key APIs and flow: When `ai_docker_storage_enable` is true, it installs filesystem tools, validates `ai_docker_device`, checks whether the mount point is already mounted, creates the mount point, formats the device as XFS/Btrfs/ext4 according to variables, mounts it with `defaults,noatime`, persists it in fstab, checks/stops Docker if active, sets `/var/lib/docker` permissions when applicable, and reports completion.

State, dependencies, integration: Highly stateful and destructive on first run because it formats the target block device. Integrates Linux filesystems, mount/fstab, systemd Docker service, and kdevops AI storage variables.

Risks and test signals: Incorrect device variables can destroy data; `ignore_errors` on Docker stop may hide failures; mountpoint check skips formatting if already mounted, regardless of fstype/options. Tests should use check mode or loop devices to validate format command selection, fstab idempotence, and mounted/unmounted paths.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/ai_docker_storage/tasks/main.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/ai_install/tasks/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/ai_install/tasks/main.yml

Purpose: Installs host prerequisites for the AI benchmark workflow.

Key APIs and flow: Includes `create_data_partition`, optionally includes `common` for user/group inference, ensures `data_path` ownership, includes optional extra vars, installs Docker packages and group membership when Docker Milvus is enabled, installs Python benchmark and graphing dependencies with pip, installs filesystem utilities for XFS/Btrfs, and creates the benchmark results directory.

State, dependencies, integration: Mutates packages, Python environment, user groups, data directories, and benchmark result directory. Integrates variables for Docker deployment, filesystem type, graphing, and data ownership.

Risks and test signals: Pip dependencies install globally unless Ansible config redirects them; extra-vars include always succeeds; adding a user to docker group requires new login to take effect; ext4 utilities are not installed explicitly. Tests should cover Docker disabled, graphing disabled, each filesystem type, and idempotent ownership changes.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/ai_install/tasks/main.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/ai_milvus_storage/tasks/main.yml -->
# sources/test-tools/kdevops/playbooks/roles/ai_milvus_storage/tasks/main.yml

Purpose: Formats and mounts dedicated Milvus data storage with filesystem parameters inferred from variables or node names.

Key APIs and flow: When `ai_milvus_storage_enable` is true, the role installs filesystem tools, validates the device, checks current mount state, creates the mount point, optionally derives fstype and XFS/ext4 parameters from `inventory_hostname`, formats XFS/Btrfs/ext4, mounts and persists fstab, creates Milvus `data`, `etcd`, and `minio` directories, and reports the selected filesystem.

State, dependencies, integration: Destructively formats `ai_milvus_device` on first setup and persists mounts. It integrates with AI benchmark node naming conventions such as `xfs`, `64k`, `4ks`, `ext4`, and `bigalloc`.

Risks and test signals: Inventory-name parsing is brittle; whitespace in folded Jinja facts can leak into command values; mounted devices skip format validation; owner is root for Milvus directories. Tests should validate command rendering for XFS sizes, ext4 bigalloc, Btrfs, mounted idempotence, and absent devices.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/playbooks/roles/ai_milvus_storage/tasks/main.yml -->
