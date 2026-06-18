# subset-b-009265 Research

Grouped source research for selected kdevops workflow files under AI benchmark reporting, blktests, build-linux, common workflow wiring, CXL, reboot-limit, fio-tests, and fstests. Each source file has a marker-delimited section for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/workflows/ai/scripts/generate_graphs.py -->
# sources/test-tools/kdevops/workflows/ai/scripts/generate_graphs.py

## Purpose

`generate_graphs.py` loads Milvus AI benchmark result JSON files and renders PNG graph artifacts into a supplied output directory. It targets insert throughput/time trends and query-performance heatmaps, with filesystem and node metadata inferred from result filenames and JSON fields.

## Important APIs, Types, and Functions

Important functions are `_extract_filesystem_config(result)`, `_extract_node_info(result)`, `load_results(results_dir)`, `create_simple_performance_trends(results, output_dir)`, `create_heatmap_analysis(results, output_dir)`, and `main()`. The script uses dictionaries from JSON results rather than custom types. It depends on `json`, `glob`, `os`, `sys`, `collections.defaultdict`, `numpy`, and `matplotlib.pyplot` using the non-interactive `Agg` backend.

## Control Flow

`main()` validates two positional arguments, creates the output directory, loads `results_*.json`, and calls both graph functions. `_extract_filesystem_config()` prefers filename-derived filesystem/block-size labels, then falls back to JSON. `_extract_node_info()` prefers `system_info.hostname`, then strips `results_` and iteration suffixes from the filename. `create_heatmap_analysis()` groups query QPS data by filesystem configuration, builds fixed top-k/batch matrices, and writes `performance_heatmap.png`.

## State and Persistence Behavior

The script does not keep durable state beyond output files. It reads JSON result files and writes PNGs. It mutates loaded result dictionaries by adding `_file` during load.

## Dependencies and Integration Points

It integrates with the AI benchmark workflow that produces `results_*.json` files and the HTML report generator that references `graphs/performance_heatmap.png` and `graphs/performance_trends.png`. Runtime requires numpy and matplotlib.

## Risks and Edge Cases

`create_simple_performance_trends()` initializes `node_performance` but writes to and reads from `fs_performance`, which is undefined in that function; the trend graph path will fail at runtime once insert performance is processed. Filename parsing uses substring checks such as `xfs`, `4k-`, and `-dev`, so unexpected host naming can misclassify configurations. Heatmaps assume fixed `topk_1/topk_10/topk_100` and `batch_1/batch_10/batch_100` keys and silently fill missing points with zero.

## Test Signals

Useful tests include running the script on one valid result, multi-filesystem result sets, malformed JSON, empty directories, and filenames that exercise XFS/ext4/btrfs parsing. A regression test should assert both expected PNG files are created and catch the undefined `fs_performance` failure.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/workflows/ai/scripts/generate_graphs.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/workflows/ai/scripts/generate_html_report.py -->
# sources/test-tools/kdevops/workflows/ai/scripts/generate_html_report.py

## Purpose

`generate_html_report.py` builds a self-contained HTML report for Milvus AI benchmark results, combining summary JSON, detailed result JSON, and graph image references. The report highlights total tests, best insert/query QPS, filesystem comparison sections, configuration summaries, and a detailed per-host table.

## Important APIs, Types, and Functions

Core functions are `load_summary(graphs_dir)`, `load_results(results_dir)`, `generate_table_rows(results, best_configs)`, `generate_config_summary(results_dir)`, `find_performance_trend_graphs(graphs_dir)`, `generate_html_report(results_dir, graphs_dir, output_path)`, and `main()`. The main data contract is a list of dictionaries with `host`, `filesystem`, `block_size`, `type`, `insert_qps`, `query_qps`, `timestamp`, and `is_dev`.

## Control Flow

`main()` expects `<results_dir> <graphs_dir> <output_html>`. `generate_html_report()` loads `summary.json` from the graphs directory or creates a zero-valued fallback, loads detailed JSON results, determines whether multiple filesystems were tested, conditionally injects filesystem and block-size sections, discovers trend graph names, formats the template, and writes the target HTML file.

## State and Persistence Behavior

The script reads summary and result JSON and writes a single HTML file. It does not copy graph assets; the generated report expects relative `graphs/*.png` paths to be valid beside the output. No persistent database or cache is used.

## Dependencies and Integration Points

It integrates with `generate_graphs.py` through graph filenames and `summary.json`, and with AI benchmark jobs through `results_*.json`. It uses Python standard-library modules only: `json`, `os`, `sys`, `glob`, `datetime`, and `pathlib`.

## Risks and Edge Cases

HTML values are interpolated directly from JSON and filenames without escaping, so unexpected strings can break markup. `generate_table_rows()` emits seven table cells while the template header declares six columns, adding a host/code column not represented by the header. Best-config highlighting compares summary config strings to a generated key and may miss when naming conventions diverge. Filename parsing is tightly coupled to `debian13-ai-`, `prod-ai-`, and `-ai-` naming.

## Test Signals

Test with missing `summary.json`, single-filesystem and multi-filesystem summaries, missing graph files, malformed or incomplete result JSON, and filenames for XFS/ext4/btrfs/dev/baseline. HTML structure checks should verify the table column count and that graph references match generated graph paths.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/workflows/ai/scripts/generate_html_report.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/workflows/blktests/Kconfig -->
# sources/test-tools/kdevops/workflows/blktests/Kconfig

## Purpose

This Kconfig file defines kdevops configuration for the blktests workflow: repository locations, data paths, test devices, optional watchdog behavior, manual section coverage, and result-copy policy.

## Important APIs, Types, and Functions

The important exported symbols include `BLKTESTS_WATCHDOG`, `BLKTESTS_WATCHDOG_CHECK_TIME`, `BLKTESTS_WATCHDOG_MAX_NEW_TEST_TIME`, `BLKTESTS_WATCHDOG_KILL_TASKS_ON_HANG`, `BLKTESTS_WATCHDOG_RESET_HUNG_SYSTEMS`, `BLKTESTS_GIT`, `BLKTESTS_DATA`, `BLKTRACE_GIT`, `BLKTRACE_DATA`, `NBD_GIT`, `NBD_VERSION`, `NBD_DATA`, `BLKTESTS_DATA_TARGET`, `BLKTESTS_TEST_DEVS`, `BLKTESTS_MANUAL_COVERAGE`, per-section booleans such as `BLKTESTS_SECTION_NVME`, and `BLKTESTS_RESULTS_ALL`.

## Control Flow

The file is gated by `KDEVOPS_WORKFLOW_ENABLE_BLKTESTS` for most settings. Watchdog suboptions are visible only under `BLKTESTS_WATCHDOG`. Manual coverage exposes per-section choices only when `BLKTESTS_MANUAL_COVERAGE=y`; otherwise defaults are supplied silently. Mirror-aware git defaults use shell helpers to choose local libvirt mirrors when available.

## State and Persistence Behavior

Kconfig itself stores user choices in `.config` and emits selected options into workflow variables through the surrounding kdevops config system. Data-path options decide where blktests, blktrace, nbd, and installed test trees persist on target nodes.

## Dependencies and Integration Points

It depends on global kdevops symbols such as `KERNEL_CI`, `LIBVIRT`, storage-drive selectors, `USE_LIBVIRT_MIRROR`, `GUESTFS`, and default URL symbols. The paired Makefile consumes these symbols to build Ansible extra variables and runtime targets.

## Risks and Edge Cases

`BLKTESTS_DBENCH_GIT_URL` uses `HAVE_MIRROR_XFSDUMP` in its mirror default rather than `HAVE_MIRROR_DBENCH`, which looks like a copy/paste risk. Default test-device paths are provider-specific and can become wrong when storage topology differs. Reset-on-hang is intentionally dangerous and limited to libvirt.

## Test Signals

Run Kconfig resolution for mirror and non-mirror setups, each libvirt drive type, manual and automatic coverage, and watchdog combinations. Validate generated `extra_vars.yaml` and that chosen `BLKTESTS_TEST_DEVS` exists on provisioned guests.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/workflows/blktests/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/workflows/blktests/Makefile -->
# sources/test-tools/kdevops/workflows/blktests/Makefile

## Purpose

This Makefile translates blktests Kconfig symbols into Ansible workflow arguments and exposes user-facing `make` targets for setup, baseline/dev runs, result collection, oscheck-only runs, and interim monitoring.

## Important APIs, Types, and Functions

Important variables are `KDEVOPS_BLKTESTS_SCRIPTS_PATH`, `BLKTESTS_ARGS`, `BLKTESTS_DYNAMIC_RUNTIME_VARS`, `WORKFLOW_ARGS`, and `EXTRA_VAR_INPUTS`. Important targets include `extend-extra-args-blktests`, `blktests`, `blktests-baseline`, `blktests-baseline-skip-kdevops-update`, `blktests-baseline-run-oscheck-only`, `blktests-dev`, `blktests-baseline-results`, `blktests-results`, `blktests-dev-results`, `monitor-results`, and `blktests-help-menu`.

## Control Flow

Make variable expansion strips Kconfig quotes, assembles git/data/install arguments, and appends them to `WORKFLOW_ARGS`. Runtime variables always set `kdevops_run_blktests: True` and conditionally add failure rerun and skip-run flags. Targets invoke `ansible-playbook` with appropriate host limits, tags, skip-tags, and extra-vars.

## State and Persistence Behavior

The Makefile writes `blktests_test_devs` into `$(KDEVOPS_EXTRA_VARS)` through `extend-extra-args-blktests`. Runtime state lives in target nodes, copied results, and `extra_vars.yaml`; the Makefile itself has no durable state beyond generated make/Ansible artifacts.

## Dependencies and Integration Points

It integrates with `playbooks/blktests.yml`, `playbooks/monitor-results.yml`, `extra_vars.yaml`, `KDEVOPS_EXTRA_VARS`, and Kconfig symbols from `workflows/blktests/Kconfig`. `RUN_FAILURES`, `SKIP_RUN`, and `LIMIT_HOSTS` are runtime knobs.

## Risks and Edge Cases

The dynamic runtime variable string is manually concatenated JSON/YAML-like text, so quoting mistakes can break Ansible parsing. `extend-extra-args-blktests` appends to `KDEVOPS_EXTRA_VARS`, so repeated invocation can duplicate entries unless higher-level generation rewrites the file. Host group assumptions require `baseline` and `dev` inventory groups to exist when selected.

## Test Signals

Use `make -n` for every target with and without `RUN_FAILURES`, `SKIP_RUN`, and `LIMIT_HOSTS`. Verify generated extra vars contain expected git/data/test-device values and that baseline/dev result collection works after a minimal blktests run.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/workflows/blktests/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/workflows/blktests/scripts/oscheck-get-failures.sh -->
# sources/test-tools/kdevops/workflows/blktests/scripts/oscheck-get-failures.sh

## Purpose

`oscheck-get-failures.sh` prints the blktests failure/expunge list that applies to the current OS, kernel, and optional test group. It is a helper for discovering which tests would be excluded by the oscheck layer.

## Important APIs, Types, and Functions

Local functions are `oscheck_fail_usage()` and `parse_args()`. It uses library functions from `oscheck-lib.sh`: `oscheck_lib_init_vars`, `oscheck_lib_read_osfiles_verify_kernel`, `oscheck_lib_set_run_group`, `oscheck_lib_set_expunges`, and `oscheck_lib_mktemp`.

## Control Flow

The script sets quiet library defaults, resolves and sources `oscheck-lib.sh`, parses `--test-group` and `--help`, loads OS/kernel metadata, validates or infers the run group, builds expunges, writes the first field of each expunge entry to a temp file, sorts/deduplicates it, prints non-empty lines, and removes the temp file.

## State and Persistence Behavior

It creates one temporary file via `mktemp` or a `/tmp/$$...` fallback and removes it before exit. It reads OS files, expunge files, and blktests `tests/` paths but does not modify the test tree.

## Dependencies and Integration Points

It must run where the blktests tree and kdevops blktests scripts/results/expunges layout are available. It depends on bash, awk, sed, sort, uniq, readlink, and the OS-specific helper scripts loaded by `oscheck-lib.sh`.

## Risks and Edge Cases

The argument parser uses `while [[ ${#1} -gt 0 ]]`, so positional handling is simple but does not validate a missing value after `--test-group`. Temp cleanup is not trap-protected. Duplicate detection in the library is substring-based, which can mis-deduplicate related test IDs.

## Test Signals

Run with `--help`, a valid `--test-group`, an invalid group, missing `oscheck-lib.sh`, and synthetic expunge files under kernel, distro, and `any` directories. Confirm output is sorted, unique, and empty when no expunges apply.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/workflows/blktests/scripts/oscheck-get-failures.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/workflows/blktests/scripts/oscheck-lib.sh -->
# sources/test-tools/kdevops/workflows/blktests/scripts/oscheck-lib.sh

## Purpose

`oscheck-lib.sh` is the shared blktests OS/kernel compatibility library. It detects the current distribution and kernel status, infers or validates the blktests group, loads distro helper hooks, and builds expunge flags for tests that should be skipped.

## Important APIs, Types, and Functions

Important functions include `oscheck_lib_init_vars`, `validate_run_group`, `oscheck_lib_set_run_group`, `oscheck_include_os_files`, `oscheck_run_osfile_read`, `oscheck_read_osfile_and_includes`, `oscheck_distro_kernel_check`, `oscheck_lib_read_osfiles_verify_kernel`, `oscheck_add_expunge_no_dups`, `oscheck_add_expunge_if_exists_no_dups`, `oscheck_handle_special_expunges`, `oscheck_get_group_files`, `oscheck_handle_group_expunges`, `oscheck_lib_set_expunges`, and `oscheck_lib_mktemp`. State variables include `OSCHECK_ID`, `VERSION_ID`, `RUN_GROUP`, `VALID_GROUPS`, `EXPUNGE_TESTS`, `EXPUNGE_FLAGS`, and `OSCHECK_CUSTOM_KERNEL`.

## Control Flow

Initialization sets paths and defaults, discovers `lsb_release`, and defines valid groups. OS reading sources `${OSCHECK_INCLUDE_PATH}/${OSCHECK_ID}/helpers.sh` when present and calls optional distro-specific functions. Kernel checking optionally exits early for distro-kernel queries. Expunge building combines distro helper expunges, result-derived `.bad`/`.dmesg` files, kernel-specific failures, distro-version failures, and generic `any` files.

## State and Persistence Behavior

The library exports shell variables used by wrapper scripts. It reads `/etc/os-release`, helper scripts, result directories, expunge files, and the blktests `tests/` directory. It does not persist state except through caller-visible exported variables.

## Dependencies and Integration Points

It integrates with `oscheck.sh`, `oscheck-get-failures.sh`, distro helper files under `../osfiles`, expunge data under `../expunges`, and blktests test paths. It relies on bash plus `grep`, `awk`, `sed`, `find`, `readlink`, `lsb_release`, and `mktemp`.

## Risks and Edge Cases

Many expansions are unquoted, so spaces or glob characters in paths can break behavior. `oscheck_add_expunge_no_dups()` uses `grep "$1"` over a whitespace list, which can treat `block/1` as a duplicate of `block/10`. `eval $(grep '^ID=' $OS_FILE)` trusts os-release content. Messages in `oscheck_count_check()` refer to `$GROUP`, but run-group state is stored in `$RUN_GROUP`.

## Test Signals

Use unit-style shell tests with synthetic `OSCHECK_OS_FILE`, helper directories, and expunge trees. Exercise distro kernel hook pass/fail, custom kernel mode, every valid group, missing tests, duplicate IDs, fallback kernel expunge paths, and no-expunge cases.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/workflows/blktests/scripts/oscheck-lib.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/workflows/blktests/scripts/oscheck.sh -->
# sources/test-tools/kdevops/workflows/blktests/scripts/oscheck.sh

## Purpose

`oscheck.sh` wraps the upstream blktests `./check` command with kdevops OS/kernel validation, test-group inference, expunge flag generation, optional command display, and kernel log start/done markers.

## Important APIs, Types, and Functions

Local functions are `oscheck_usage`, `copy_to_check_arg`, `parse_args`, `oscheck_run_cmd`, `oscheck_run_groups`, `_cleanup`, and `check_check`. It consumes `oscheck-lib.sh` functions and variables, especially `RUN_GROUP`, `EXPUNGE_FLAGS`, `ONLY_QUESTION_DISTRO_KERNEL`, and `OSCHECK_CUSTOM_KERNEL`.

## Control Flow

The script refuses non-root execution, sources the library, parses known long options, passes unknown arguments through to `./check`, reads OS files and verifies kernel policy, sets the test group, verifies `./check` exists, installs an exit trap, computes expunges, constructs `./check ${RUN_GROUP} $EXPUNGE_FLAGS ${CHECK_ARGS[@]}`, and either prints or executes it under `LC_ALL=C`.

## State and Persistence Behavior

It writes the executed command to `/tmp/run-cmd.txt` when actually running tests and optionally writes start/done markers to `/dev/kmsg`. Test results and persistence are owned by upstream blktests and kdevops Ansible roles.

## Dependencies and Integration Points

It must run as root inside a blktests source tree. It integrates with kdevops playbook tasks that invoke oscheck, with blktests `./check`, and with distro helper/expunge infrastructure from `oscheck-lib.sh`.

## Risks and Edge Cases

`CHECK_ARGS` is declared as an array but appended as a string, then expanded as an array; arguments with spaces are not preserved safely. `DRY_RUN` and `ONLY_CHECK_DEPS` are initialized but unused. The trap references `$status`, which is not assigned in this file. Unknown options are passed through one token at a time, so options requiring values rely on upstream parsing receiving the next token correctly.

## Test Signals

Test as non-root, outside a blktests tree, with `--show-cmd`, `--expunge-list`, `--test-group`, `--is-distro`, pass-through `./check` flags, and `--print-start/--print-done` in an environment where `/dev/kmsg` is writable.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/workflows/blktests/scripts/oscheck.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/workflows/build-linux/Kconfig -->
# sources/test-tools/kdevops/workflows/build-linux/Kconfig

## Purpose

This Kconfig file configures the kdevops build-linux workflow: result location, repeat count, make parallelism, build target, cleaning/stat collection, optional dedicated build filesystem, kernel tag selection, and multi-filesystem testing hooks.

## Important APIs, Types, and Functions

Important symbols include `BUILD_LINUX_RESULTS_DIR`, `BUILD_LINUX_REPEAT_COUNT`, `BUILD_LINUX_MAKE_JOBS`, `BUILD_LINUX_TARGET`, `BUILD_LINUX_CLEAN_BETWEEN`, `BUILD_LINUX_COLLECT_STATS`, `BUILD_LINUX_STORAGE_ENABLE`, `BUILD_LINUX_DEVICE`, `BUILD_LINUX_FSTYPE`, XFS block/sector-size choices, `BUILD_LINUX_USE_LATEST_TAG`, `BUILD_LINUX_CUSTOM_TAG`, and `BUILD_LINUX_ALLOW_MODIFICATIONS`.

## Control Flow

The file is gated by `KDEVOPS_WORKFLOW_ENABLE_BUILD_LINUX`. Storage-specific device and filesystem choices appear only when `BUILD_LINUX_STORAGE_ENABLE=y`; XFS block and sector choices appear only for XFS. `Kconfig.multifs` is sourced only when storage is enabled and declared hosts are not being used.

## State and Persistence Behavior

Kconfig choices are stored in `.config` and output to YAML for Ansible roles. The selected results directory controls where build timing JSON, summaries, logs, visualizations, and HTML reports are persisted.

## Dependencies and Integration Points

It depends on kdevops provider symbols for libvirt and cloud device defaults. The paired Makefile and Ansible roles consume the options and call scripts in `workflows/build-linux/scripts`.

## Risks and Edge Cases

Large repeat counts and clean-between-builds can consume significant time and I/O. Large XFS block/sector sizes require kernel/filesystem support and may fail on unsupported targets. Device defaults are topology-specific and destructive formatting can hit the wrong disk if provider assumptions are stale.

## Test Signals

Validate Kconfig with storage disabled/enabled, each filesystem, XFS size combinations, latest-tag and custom-tag modes, and all provider default devices. Dry-run generated Ansible extra vars and perform a minimal one-build run.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/workflows/build-linux/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/workflows/build-linux/Makefile -->
# sources/test-tools/kdevops/workflows/build-linux/Makefile

## Purpose

This Makefile exposes build-linux workflow targets for provisioning/running repeated kernel builds, collecting results, generating visualizations, collecting monitoring data, and killing monitoring processes.

## Important APIs, Types, and Functions

Key targets are `build-linux`, `build-linux-baseline`, `build-linux-dev`, `build-linux-results`, `build-linux-visualize`, `monitor-results`, `monitor-kill`, and `build-linux-help-menu`. It relies on `KDEVOPS_NODES`, `ANSIBLE_INVENTORY_FILE`, `KDEVOPS_EXTRA_VARS`, `LIMIT_HOSTS`, and configured build-linux Kconfig variables.

## Control Flow

`build-linux` runs `playbooks/build_linux.yml`, then automatically calls result collection and visualization. `build-linux-visualize` checks that `workflows/build-linux/results` exists and is non-empty, generates summary files from build timing JSON when summary files are absent, and runs `visualize_results.py`. Failure output tells users how to install matplotlib/numpy.

## State and Persistence Behavior

Persistent artifacts live under `workflows/build-linux/results/`: raw timing data, summary JSON, logs, generated HTML, and copied monitoring images. The Makefile itself only orchestrates these paths.

## Dependencies and Integration Points

It integrates with Ansible playbooks `build_linux.yml`, `build_linux_results.yml`, `monitor-results.yml`, and `monitor-kill.yml`, plus Python scripts `generate_summaries.py` and `visualize_results.py`.

## Risks and Edge Cases

The results path is hard-coded in the Makefile even though Kconfig defines `BUILD_LINUX_RESULTS_DIR`, so custom result directories may not be honored by visualization. Baseline/dev targets set `HOSTS="baseline"` or `HOSTS="dev"` but the main target uses `LIMIT_HOSTS`, so filtering depends on external make plumbing. Summary generation failures are downgraded to warnings, which can leave visualization to fail later.

## Test Signals

Use `make -n build-linux`, `build-linux-results`, and `build-linux-visualize` with empty, missing, and populated results directories. Run with a one-build result set and assert `html/index.html` is produced.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/workflows/build-linux/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/workflows/build-linux/scripts/build_linux.py -->
# sources/test-tools/kdevops/workflows/build-linux/scripts/build_linux.py

## Purpose

`build_linux.py` performs repeated Linux kernel builds and records timing/statistics. It supports out-of-tree builds, optional checkout of the latest stable v6 tag or a custom tag, optional cleaning between iterations, and optional `/usr/bin/time -v` logging.

## Important APIs, Types, and Functions

The main type is `LinuxBuilder`. Important methods are `run_command`, `get_latest_tag`, `is_git_writable`, `checkout_tag`, `configure_kernel`, `clean_build`, `build_kernel`, `save_results`, and `run`. `main()` defines CLI arguments for source/build/results directories, count, jobs, target, clean/stat flags, and tag selection.

## Control Flow

`main()` parses arguments and calls `LinuxBuilder.run()`. The runner determines the tag, checks out when the git repository is writable, configures the kernel if `.config` is missing, loops over build iterations, optionally cleans, runs make under `/usr/bin/time -v`, records duration/exit code, sleeps between builds, then writes raw and summary JSON.

## State and Persistence Behavior

It creates the results directory, writes per-iteration `build_N.log`, `build_times_<hostname>.json`, and `summary_<hostname>.json`. It may modify the source git checkout and, for in-tree builds with cleaning enabled, runs `git clean -f -x -d`. Out-of-tree cleanup removes everything below the build directory.

## Dependencies and Integration Points

It depends on a Linux source tree, GNU make, git, `/usr/bin/time` when stat collection is enabled, and standard Python modules. Ansible build-linux roles call this script and later collection/visualization scripts consume its JSON contracts.

## Risks and Edge Cases

Commands are built with `shell=True` from path and target arguments, so unsafe input can execute unintended shell syntax. `clean_build()` uses `rm -rf *` in the build directory, making correct `--build-dir` critical. A read-only source tree skips checkout but may build an unexpected tag. Failed builds do not abort the loop, which is useful for data collection but can waste time after systematic failures.

## Test Signals

Run with a tiny `--count 1` out-of-tree build, read-only source simulation, missing `.config`, failing make target, `--jobs 0`, and `--clean-between`. Validate raw/summary JSON schema and build log creation.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/workflows/build-linux/scripts/build_linux.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/workflows/build-linux/scripts/combine_results.py -->
# sources/test-tools/kdevops/workflows/build-linux/scripts/combine_results.py

## Purpose

`combine_results.py` combines per-host build-linux summary JSON files into one `combined_report.json` with host details, totals, and approximate aggregate statistics.

## Important APIs, Types, and Functions

The script has `combine_results(results_dir)` and `main()`. It expects files matching `*_summary_*.json` containing `hostname`, build counts, and `statistics.total_hours`, `statistics.average`, `statistics.min`, and `statistics.max`.

## Control Flow

`main()` parses the results directory and calls `combine_results()`. The function loads all summary files, indexes them by hostname, accumulates total/success/failure counts and total hours, approximates aggregate durations by repeating each host average for its successful build count, writes `combined_report.json`, and prints a console summary.

## State and Persistence Behavior

It reads summary JSON files and writes `combined_report.json` in the same results directory. It does not alter raw timing files.

## Dependencies and Integration Points

It uses Python standard-library modules only. It integrates with `build_linux.py` and `generate_summaries.py` outputs and can feed downstream reporting or manual inspection.

## Risks and Edge Cases

The glob pattern is `*_summary_*.json`, but `build_linux.py` writes `summary_<hostname>.json`, so direct builder output may not be found unless collection renames files or `generate_summaries.py` creates matching names. Aggregate stats are approximated from host averages rather than raw durations, so min/max/average can be misleading across unequal distributions. Missing required keys raise exceptions.

## Test Signals

Test with no summary files, one valid summary, multiple summaries with different successful counts, all-failed summaries, and both `summary_host.json` and `host_summary_host.json` naming conventions.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/workflows/build-linux/scripts/combine_results.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/workflows/build-linux/scripts/generate_summaries.py -->
# sources/test-tools/kdevops/workflows/build-linux/scripts/generate_summaries.py

## Purpose

`generate_summaries.py` creates per-host summary JSON files from raw `build_times` JSON data when summary files are missing from collected build-linux results.

## Important APIs, Types, and Functions

Important functions are `generate_summary_from_timing(timing_file)`, `generate_all_summaries(results_dir)`, and `main()`. The raw input is a list of build entries with `duration` and `success`; output contains host, build counts, default target/jobs metadata, and timing statistics.

## Control Flow

`generate_all_summaries()` finds `*_build_times_*.json`, generates a summary for each, writes `<hostname>_summary_<hostname>.json`, and prints counts and average time. `generate_summary_from_timing()` derives hostname from the filename suffix after `_build_times_`, splits successful and failed entries, and computes statistics over successful builds or all durations if none succeeded.

## State and Persistence Behavior

The script reads raw timing JSON and writes generated summary JSON beside it. It does not remove or update raw timing files.

## Dependencies and Integration Points

It is called by the build-linux Makefile before visualization when no summaries exist. It uses standard Python modules: `json`, `argparse`, `pathlib`, `statistics`, `socket`, and `os`.

## Risks and Edge Cases

The glob expects `*_build_times_*.json`, while `build_linux.py` writes `build_times_<hostname>.json`; collected files may need a hostname prefix for this script to find them. `build_target` is hard-coded to `vmlinux` and `make_jobs` to local `os.cpu_count()`, which may not match the remote run. Empty timing files produce zeroed statistics only through the no-success path.

## Test Signals

Test naming variants, empty lists, all-failed builds, mixed success/failure, single successful build, and malformed entries missing `duration`. Verify visualization can consume generated summaries.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/workflows/build-linux/scripts/generate_summaries.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/workflows/build-linux/scripts/visualize_results.py -->
# sources/test-tools/kdevops/workflows/build-linux/scripts/visualize_results.py

## Purpose

`visualize_results.py` loads build-linux results, generates matplotlib charts, embeds them into an HTML performance report, and consolidates shareable HTML/PNG monitoring assets.

## Important APIs, Types, and Functions

Important functions are `load_all_results`, `create_build_time_comparison_chart`, `create_build_time_distribution`, `create_build_timeline`, `create_success_rate_chart`, `generate_monitoring_section`, `generate_html_report`, `consolidate_html_output`, and `main`. It treats summaries, timings, and monitoring data as nested dictionaries/lists loaded from JSON and text files.

## Control Flow

`main()` validates `results_dir`, loads summaries/timings/monitoring, requires at least one summary, optionally generates HTML, consolidates output, and prints a console summary. Graph helpers return base64 PNG strings when matplotlib is available. `generate_html_report()` computes totals/overall statistics, appends sections and tables, writes `build_performance_report.html`, and `consolidate_html_output()` copies it to `html/index.html` with monitoring PNGs for full-size viewing.

## State and Persistence Behavior

It reads `*_summary_*.json`, `*_build_times_*.json`, and optional `monitoring/` artifacts. It writes `build_performance_report.html`, creates `html/`, and copies PNG monitoring assets. Charts are embedded as base64 in HTML rather than stored as separate generated graph files.

## Dependencies and Integration Points

Matplotlib and numpy are optional but required for charts. The script integrates with build-linux result collection, monitoring roles, and the Makefile `build-linux-visualize` target.

## Risks and Edge Cases

If `total_builds` is zero, the top summary success-rate expression divides by zero. HTML is generated with direct f-string interpolation from hostnames and failure reasons. Host filesystem detection is name-based. The script prints emoji/non-ASCII in status and headings, which is harmless for browsers but can matter in ASCII-only logs. Missing matplotlib degrades graphs but still generates no-data sections.

## Test Signals

Test no summaries, all-failed hosts, zero total builds, missing matplotlib, monitoring with folio/fragmentation plots, and hostnames for XFS/ext4/btrfs/unknown. Validate `html/index.html` and copied monitoring assets.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/workflows/build-linux/scripts/visualize_results.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/workflows/common/Makefile -->
# sources/test-tools/kdevops/workflows/common/Makefile

## Purpose

This common workflow Makefile maps global workflow Kconfig settings into shared Ansible variables for data partitions, kdevops git clone location/version, optional make command override, and data user/group handling.

## Important APIs, Types, and Functions

Important variables are `WORKFLOW_DATA_DEVICE`, `WORKFLOW_DATA_PATH`, `WORKFLOW_DATA_FSTYPE`, `WORKFLOW_DATA_LABEL`, `WORKFLOW_KDEVOPS_GIT`, `WORKFLOW_KDEVOPS_GIT_VERSION`, `WORKFLOW_KDEVOPS_GIT_DATA`, `WORKFLOW_KDEVOPS_DIR`, `WORKFLOW_MAKE_CMD`, `WORKFLOW_DATA_USER`, `WORKFLOW_DATA_GROUP`, and accumulated `WORKFLOW_ARGS`. Targets are `kdevops-git-reset` and `kdevops-help-menu` when git-clone mode is enabled.

## Control Flow

The file strips quotes from Kconfig values and appends data and git settings to `WORKFLOW_ARGS`. If `CONFIG_WORKFLOW_INFER_USER_AND_GROUP=y`, it emits `infer_uid_and_group=True`; otherwise it emits explicit user and group values. Git reset/help targets are only defined when `CONFIG_KDEVOPS_WORKFLOW_GIT_CLONES_KDEVOPS_GIT=y`.

## State and Persistence Behavior

It does not write files directly, but its variables drive generated `extra_vars.yaml` and target-node state such as mounted data partitions and cloned kdevops directories.

## Dependencies and Integration Points

It is included by the larger kdevops Makefile system and integrates with `playbooks/common.yml`, `LIMIT_HOSTS`, and global workflow Kconfig symbols.

## Risks and Edge Cases

Manual quoting is mixed: some paths are escaped with `\"...\"`, others are plain. Paths with spaces are likely fragile. The make command override variable is set but not appended here, so consumers must pick it up elsewhere. Incorrect data device settings can trigger destructive partition operations in playbooks.

## Test Signals

Run make dry-runs with inferred and explicit user/group settings, git-clone mode enabled/disabled, and path values containing shell-sensitive characters. Verify resulting Ansible extra vars match expected keys.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/workflows/common/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/workflows/cxl/Kconfig -->
# sources/test-tools/kdevops/workflows/cxl/Kconfig

## Purpose

This Kconfig file configures the kdevops CXL workflow, especially whether to run CXL test modules and where to fetch/build ndctl.

## Important APIs, Types, and Functions

Important symbols are `ENABLE_CXL_TEST`, `NDCTL_GIT`, `NDCTL_DATA`, and `NDCTL_VERSION`. `NDCTL_GIT` selects upstream pmem/ndctl by default or linux-kdevops GitHub/GitLab alternatives when global git alternative options are enabled.

## Control Flow

The entire file is gated by `KDEVOPS_WORKFLOW_ENABLE_CXL`. When enabled, users can opt into kernel mock CXL test modules and choose ndctl source/version/data path.

## State and Persistence Behavior

Kconfig choices persist in `.config` and feed Ansible variables. `NDCTL_DATA` controls where the ndctl tree is cloned on target systems.

## Dependencies and Integration Points

The paired CXL Makefile consumes these symbols. The workflow integrates with ndctl/cxl tooling, CXL kernel test modules, and optional QEMU CXL DCD topology settings defined elsewhere.

## Risks and Edge Cases

The help for `NDCTL_VERSION` says only a pending branch builds correctly, but the default is `v74`, so build compatibility should be verified. CXL test enablement depends on kernel and QEMU support outside this file.

## Test Signals

Validate Kconfig under upstream, GitHub, and GitLab git modes; build ndctl at the configured version; and run probe/meson targets with `ENABLE_CXL_TEST` both enabled and disabled.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/workflows/cxl/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/workflows/cxl/Makefile -->
# sources/test-tools/kdevops/workflows/cxl/Makefile

## Purpose

This Makefile maps CXL Kconfig symbols to Ansible variables and exposes targets for ndctl/cxl setup, CXL test probing, meson test execution, result collection, memory setup, and dynamic capacity setup.

## Important APIs, Types, and Functions

Important variables are `CXL_ARGS`, `CXL_DYNAMIC_RUNTIME_VARS`, `WORKFLOW_ARGS`, and `BOOTLINUX_CXL_HELP`. Targets include `cxl`, `cxl-test-probe`, `cxl-test-meson`, `cxl-results`, `cxl-mem-setup`, `cxl-create-dc-region`, `cxl-dcd-setup`, `cxl-help-menu`, `cxl-dcd-help`, and `cxl-help-end`.

## Control Flow

The Makefile builds ndctl git/data/version args, optionally appends CXL DCD topology variables from QEMU config, includes `Makefile.kernel`, and defines targets that run `playbooks/cxl.yml` with selected tags and runtime variables.

## State and Persistence Behavior

Persistent state is in target-node ndctl checkouts, CXL memory/device configuration, and copied test results. The Makefile contributes variables to generated extra-vars state through `WORKFLOW_ARGS`.

## Dependencies and Integration Points

It integrates with `playbooks/cxl.yml`, `workflows/cxl/Makefile.kernel`, QEMU CXL DCD configuration, and global host limiting.

## Risks and Edge Cases

`CXL_DYNAMIC_RUNTIME_VARS` directly embeds `$(CONFIG_ENABLE_CXL_TEST)`, which is a Kconfig `y/n` value rather than Python/YAML boolean text unless downstream handles it. Help text contains a typo, `ncdtl`. DCD targets are only useful when matching QEMU topology is enabled.

## Test Signals

Use `make -n` for all CXL targets under test enabled/disabled and DCD enabled/disabled. Run probe and meson targets on a CXL-capable kernel/QEMU setup and verify result collection.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/workflows/cxl/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/workflows/demos/reboot-limit/Kconfig -->
# sources/test-tools/kdevops/workflows/demos/reboot-limit/Kconfig

## Purpose

This Kconfig file defines the reboot-limit demo workflow, which repeatedly reboots hosts to establish reliability bounds and optionally compare regular reboot with kexec.

## Important APIs, Types, and Functions

Important symbols include `WORKFLOWS_REBOOT_LIMIT`, `KDEVOPS_WORKFLOW_NAME`, reboot-type choices, `REBOOT_LIMIT_TEST_TYPE`, `REBOOT_LIMIT_COMPARE_BOTH_ENABLED`, `REBOOT_LIMIT_BOOT_MAX`, watchdog settings, loop steady-state settings, crash-injection settings, data collection paths, and `REBOOT_LIMIT_ENABLE_SYSTEMD_ANALYZE`.

## Control Flow

When `WORKFLOWS_REBOOT_LIMIT=y`, users choose reboot mechanism: Ansible reboot, `systemctl reboot`, `systemctl kexec`, or compare-both. Optional loop testing exposes steady-state goal and incremental counting. Optional data collection exposes base and compare-mode data directories plus systemd-analyze collection.

## State and Persistence Behavior

Configuration persists in `.config` and output YAML. Runtime state is expected under configured reboot-limit data directories, with separate regular/kexec directories in compare mode.

## Dependencies and Integration Points

The paired Makefile consumes these symbols and passes them to `playbooks/reboot-limit.yml` and loop scripts. The workflow depends on Ansible reboot support, systemd commands, optional kexec support, and optional systemd-analyze.

## Risks and Edge Cases

High `REBOOT_LIMIT_BOOT_MAX` multiplied by loop steady-state goals can produce very long tests. Compare mode doubles reboot paths and data locations, increasing state consistency requirements. Crash injection is intentionally disruptive and needs careful target isolation.

## Test Signals

Validate each reboot type, compare-both mode, data collection enabled/disabled, `COUNT` override behavior through the Makefile, loop resume behavior, and crash injection in disposable VMs.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/workflows/demos/reboot-limit/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/workflows/demos/reboot-limit/Makefile -->
# sources/test-tools/kdevops/workflows/demos/reboot-limit/Makefile

## Purpose

This Makefile both documents and implements the reboot-limit demo workflow. It converts Kconfig settings into Ansible variables and defines targets for setup, baseline/dev reboot tests, loops, resets, and result analysis.

## Important APIs, Types, and Functions

Important variables are `REBOOT_LIMIT_TEST_TYPE`, `REBOOT_LIMIT_ARGS`, `REBOOT_LIMIT_DATA`, `REBOOT_LIMIT_DATA_REGULAR`, `REBOOT_LIMIT_DATA_KEXEC`, `REBOOT_LIMIT_MAX`, `REBOOT_LIMIT_LOOP`, `REBOOT_LIMIT_LOOP_KOTD`, and `WORKFLOW_ARGS`. Targets include `reboot-limit`, `reboot-limit-baseline`, `reboot-limit-baseline-loop`, `reboot-limit-baseline-kotd`, `reboot-limit-baseline-reset`, `reboot-limit-tests`, `reboot-limit-dev`, `reboot-limit-dev-loop`, `reboot-limit-dev-kotd`, `reboot-limit-dev-reset`, `reboot-limit-results`, and `reboot-limit-graph`.

## Control Flow

The Makefile strips quotes from Kconfig values, appends data/compare/systemd/crash/max settings, and exports workflow enablement. Baseline and dev targets run first-run/reset tasks, then run tests and copy results. Dev execution checks that the `dev` group has hosts before running. Loop targets dispatch to configured loop scripts.

## State and Persistence Behavior

It writes no files directly except through Ansible and result scripts. Runtime state includes target-node counters, data under configured reboot-limit paths, copied results, and generated graph/analysis artifacts.

## Dependencies and Integration Points

It integrates with `playbooks/reboot-limit.yml`, `extra_vars.yaml`, loop scripts under `scripts/workflows/demos/reboot-limit/`, and `analyze_results.py`.

## Risks and Edge Cases

The dev-host check only inspects one line after `[dev]`, so inventories with comments/blank lines may be misdetected. `reboot-limit` setup passes only `reboot_limit_max` inline and does not pass `extra_vars.yaml`, unlike run targets. Long loops can mask infrastructure failures unless watchdog behavior is implemented.

## Test Signals

Run make dry-runs with compare mode, data collection disabled, crash injection, and `COUNT=N`. Test inventories with no dev hosts and with multiple dev host formatting styles. Run a small `COUNT=1` baseline and dev test.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/workflows/demos/reboot-limit/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/workflows/fio-tests/Kconfig -->
# sources/test-tools/kdevops/workflows/fio-tests/Kconfig

## Purpose

This Kconfig file defines the fio-tests workflow matrix: quick/performance/latency/throughput/mixed/filesystem/multi-filesystem modes, target devices, runtime/ramp time, filesystem creation settings, block sizes, IO depths, job counts, workload patterns, and graphing options.

## Important APIs, Types, and Functions

Important symbols include `FIO_TESTS_QUICK_TEST`, `FIO_TESTS_PERFORMANCE_ANALYSIS`, `FIO_TESTS_FILESYSTEM_TESTS`, `FIO_TESTS_MULTI_FILESYSTEM`, `FIO_TESTS_DEVICE`, `FIO_TESTS_RUNTIME`, `FIO_TESTS_RAMP_TIME`, `FIO_TESTS_REQUIRES_FILESYSTEM`, filesystem device/mount/label options, multi-fs enable flags for XFS/ext4/btrfs variants, `FIO_TESTS_MULTI_FS_COUNT`, block-size booleans/ranges, IO depth booleans, numjobs booleans, workload-pattern booleans, `FIO_TESTS_IOENGINE`, `FIO_TESTS_DIRECT`, `FIO_TESTS_FSYNC_ON_CLOSE`, result/log settings, and graph settings.

## Control Flow

CLI-detected symbols allow runtime/ramp/quick overrides. The mode choice selects A/B infrastructure and filesystem requirements where needed. Filesystem options source `Kconfig.fs` only when required. Multi-filesystem options expose per-variant VM settings and compute a count for validation. Quick test mode narrows defaults for runtime, ramp, IO depth, jobs, and patterns.

## State and Persistence Behavior

Kconfig choices persist in `.config` and YAML output. Runtime results persist under `FIO_TESTS_RESULTS_DIR`; filesystem tests format/mount configured devices and create test files under the mount point.

## Dependencies and Integration Points

It integrates with fio Ansible playbooks, filesystem-formatting roles, provider storage symbols, and visualization scripts. Filesystem modes require extra block devices and mkfs tooling.

## Risks and Edge Cases

The test matrix can expand quickly and produce long runtimes/logs. Device defaults are provider-specific and formatting is destructive. `FIO_TESTS_MULTI_FS_COUNT` only has special defaults for a few combinations and otherwise falls back to `8`, so validation may be coarse. Large block-size and bigalloc configurations require kernel/filesystem support.

## Test Signals

Validate Kconfig for quick, performance, filesystem, and multi-filesystem modes; confirm generated hosts and extra vars match enabled filesystem variants; run smoke fio tests against `/dev/null` and a disposable filesystem device; verify graphing option dependencies install correctly.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/workflows/fio-tests/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/workflows/fio-tests/Makefile -->
# sources/test-tools/kdevops/workflows/fio-tests/Makefile

## Purpose

This Makefile exposes the fio-tests workflow targets for running tests, establishing baselines, collecting results, graphing, comparing baseline/dev results, trend analysis, multi-filesystem comparison, and result cleanup.

## Important APIs, Types, and Functions

Targets are `fio-tests`, `fio-tests-baseline`, `fio-tests-results`, `fio-tests-graph`, `fio-tests-compare`, `fio-tests-trend-analysis`, `fio-tests-multi-fs-compare`, `fio-tests-clean-results`, and `fio-tests-help-menu`. It uses `KDEVOPS_EXTRA_VARS`, `TOPDIR`, `CONFIG_KDEVOPS_WORKFLOW_ENABLE_FIO_TESTS`, and `KDEVOPS_DESTROY_DEPS`.

## Control Flow

Each run/analysis target invokes a dedicated Ansible playbook with `--extra-vars=@$(KDEVOPS_EXTRA_VARS)`. Cleanup removes `$(TOPDIR)/workflows/fio-tests/results/`. When the workflow is enabled, cleanup is added to `KDEVOPS_DESTROY_DEPS`.

## State and Persistence Behavior

Persistent state is primarily the workflow results directory removed by `fio-tests-clean-results`. Test execution and graphing state live in Ansible-managed target and local result paths.

## Dependencies and Integration Points

It integrates with playbooks named after each operation: `fio-tests.yml`, `fio-tests-baseline.yml`, `fio-tests-results.yml`, `fio-tests-graph.yml`, `fio-tests-compare.yml`, `fio-tests-trend-analysis.yml`, and `fio-tests-multi-fs-compare.yml`.

## Risks and Edge Cases

Targets do not pass `LIMIT_HOSTS`, so host scoping depends on playbook internals or extra vars. Cleanup is a direct `rm -rf` of the local results tree. The Makefile has no preflight for missing extra vars, missing playbooks, or absent graph dependencies.

## Test Signals

Use `make -n` for all targets, run cleanup on a disposable results directory, verify destroy dependency registration only when the workflow is enabled, and smoke-test quick fio mode end to end.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/workflows/fio-tests/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/workflows/fio-tests/scripts/generate_comparison_graphs.py -->
# sources/test-tools/kdevops/workflows/fio-tests/scripts/generate_comparison_graphs.py

## Purpose

`generate_comparison_graphs.py` loads fio JSON results from selected filesystem-specific result directories and generates PNG comparison charts for IOPS, bandwidth, block-size impact, IO-depth scaling, and an overview dashboard.

## Important APIs, Types, and Functions

Important functions are `load_fio_results`, `create_comparison_bar_chart`, `create_block_size_comparison`, `create_iodepth_scaling`, `create_summary_dashboard`, and `main`. Data is stored as nested dictionaries keyed by display filesystem name and test key such as `randread_16k_1_1`.

## Control Flow

`main()` validates a single results directory, loads results for hard-coded XFS/ext4/btrfs configurations, creates `graphs/`, and calls four graph functions. Loading parses test parameters from filenames of the form `results_<pattern>_bs<size>_iodepth<depth>_jobs<num>.json`, extracts metrics from the first fio job, and normalizes bandwidth/latency.

## State and Persistence Behavior

It reads JSON files under per-filesystem subdirectories and writes PNG files under `<results_dir>/graphs`: `multi_filesystem_comparison.png`, `block_size_comparison.png`, `iodepth_scaling.png`, and `performance_dashboard.png`.

## Dependencies and Integration Points

It depends on matplotlib and numpy and integrates with fio-tests multi-filesystem playbooks and the comprehensive analysis script. Expected directory names are `debian13-fio-tests-xfs-16k`, `debian13-fio-tests-ext4-bigalloc`, and `debian13-fio-tests-btrfs-zstd`.

## Risks and Edge Cases

The filesystem list and directory names are hard-coded, so enabled Kconfig variants such as XFS 4K/32K/64K, ext4 standard, or btrfs standard are ignored unless paths match this script. Bar-label offsets use `max(iops_values)` and can be zero. Summary ranking divides by the best result when calculating percentages and can divide by zero if all values are zero. The script imports `matplotlib.patches` and `Path` but does not use them.

## Test Signals

Test missing directories, one filesystem only, all-zero results, write workloads, malformed filenames, and all configured multi-fs variants. Assert all four PNGs are generated and non-empty.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/workflows/fio-tests/scripts/generate_comparison_graphs.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/workflows/fio-tests/scripts/generate_comprehensive_analysis.py -->
# sources/test-tools/kdevops/workflows/fio-tests/scripts/generate_comprehensive_analysis.py

## Purpose

`generate_comprehensive_analysis.py` generates a text report summarizing multi-filesystem fio performance across selected XFS, ext4, and btrfs configurations.

## Important APIs, Types, and Functions

The script has `load_and_analyze_results(results_dir)`, `generate_analysis_report(analysis, output_file)`, and `main()`. It stores analysis under `analysis["filesystems"][fs_name][test_key]` with pattern, block size, IO depth, job count, IOPS, bandwidth, and latency.

## Control Flow

`main()` uses a hard-coded `results` directory, loads analysis, and writes `results/comprehensive_analysis.txt`. Loading walks hard-coded filesystem directories, parses fio result filenames, extracts the first job's read metrics, and returns the analysis. Report generation writes infrastructure notes, performance matrices, rankings, scaling summaries, block-size impact, key insights, generated graph names, and A/B testing notes.

## State and Persistence Behavior

It reads fio result JSON files and writes one text report. It does not generate graphs or mutate result JSON.

## Dependencies and Integration Points

It uses standard Python modules and is intended to complement `generate_comparison_graphs.py`. It expects the same hard-coded multi-filesystem directory naming convention.

## Risks and Edge Cases

`main()` ignores CLI arguments and always uses `results`, so running from a different working directory fails. Only read metrics are extracted, even for write-pattern tests. Ranking percentage math can divide by zero when the top IOPS is zero. The report contains non-ASCII bullets/medal symbols, which may be undesirable in plain logs. The infrastructure text says six VMs even though loaded directories represent three baseline-style filesystem names.

## Test Signals

Run from the workflow directory and from another cwd, with missing result directories, all-zero results, write-only results, and malformed JSON. Verify `comprehensive_analysis.txt` content covers expected test keys and handles empty data gracefully.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/workflows/fio-tests/scripts/generate_comprehensive_analysis.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/workflows/fio-tests/sections.conf -->
# sources/test-tools/kdevops/workflows/fio-tests/sections.conf

## Purpose

`sections.conf` is an INI-style manifest describing concrete filesystem configurations for fio-tests multi-filesystem runs.

## Important APIs, Types, and Functions

Sections include `[xfs-4k]`, `[xfs-16k]`, `[xfs-all-block-sizes]`, `[xfs-32k]`, `[xfs-64k]`, `[ext4-std]`, `[ext4-bigalloc]`, `[btrfs-std]`, and `[btrfs-zstd]`. Most sections define `filesystem`, `mkfs_opts`, and `mount_opts`.

## Control Flow

There is no executable control flow. Consumers parse sections to decide filesystem type, mkfs command options, mount options, and potentially expansion behavior for aggregate sections such as `xfs-all-block-sizes`.

## State and Persistence Behavior

The file is static configuration. Runtime state is produced by consumers that create filesystems, mount them, and run fio workloads.

## Dependencies and Integration Points

It integrates with fio-tests roles/playbooks and Kconfig options that enable the same filesystem variants. Options assume mkfs.xfs, mkfs.ext4, and mkfs.btrfs support the listed flags.

## Risks and Edge Cases

`[xfs-all-block-sizes]` contains only a comment and no key/value pairs, so consumers must special-case it or skip it. XFS large block sizes and ext4 bigalloc require compatible kernels and tools. Mount options for btrfs zstd assume compression support.

## Test Signals

Parse with the intended config parser, verify each enabled Kconfig option maps to a section, validate mkfs/mount commands on disposable devices, and test consumer behavior for the empty aggregate section.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/workflows/fio-tests/sections.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/workflows/fstests/Kconfig -->
# sources/test-tools/kdevops/workflows/fstests/Kconfig

## Purpose

This Kconfig file defines the extensive fstests workflow configuration: target filesystem, watchdog behavior, result trimming, repository choices, test-device strategy, sparse-file backing, test devices/mounts, run selection, large-disk/soak controls, and journald integration.

## Important APIs, Types, and Functions

Important symbols include filesystem choices (`FSTESTS_XFS`, `FSTESTS_BTRFS`, `FSTESTS_EXT4`, `FSTESTS_NFS`, `FSTESTS_CIFS`, `FSTESTS_TMPFS`), `FSTESTS_FSTYP`, `FSTESTS_TFB_COPY_ENABLE`, watchdog symbols, per-filesystem sourced Kconfigs, `FSTESTS_GIT`, `FSTESTS_DATA`, `FSTESTS_GIT_VERSION`, `FSTESTS_DATA_TARGET`, test-device strategy choices, sparse-file settings, `FSTESTS_TEST_DEV`, `FSTESTS_SCRATCH_DEV_POOL`, logwrites/logdev/rtdev/ZNS settings, `FSTESTS_RUN_TESTS`, run group/custom tests, large-disk tests, soak duration choices, and `FSTESTS_ENABLE_JOURNAL`.

## Control Flow

Most settings are gated by `KDEVOPS_WORKFLOW_ENABLE_FSTESTS`. The target filesystem choice selects helper booleans and per-filesystem Kconfig includes. Non-network/non-tmpfs modes expose device strategy choices. Sparse-file mode exposes backing filesystem/path/size/prefix and default loop devices. Soak duration has CLI detection and preset/custom choices.

## State and Persistence Behavior

Configuration persists in `.config` and selected symbols output to YAML. Runtime state includes cloned fstests source, generated configs, sparse backing files, loop/NVMe devices, copied results, xunit files, expunges, watchdog logs, and optional journald entries.

## Dependencies and Integration Points

It integrates with per-filesystem Kconfig files, provider storage symbols, mirror/default git URL symbols, Makefile fragments, Ansible fstests roles, and upstream fstests semantics for variables such as `TEST_DEV`, `SCRATCH_DEV_POOL`, `LOGWRITES_DEV`, and `SOAK_DURATION`.

## Risks and Edge Cases

There appears to be an `if FSTESTS_TFB_ENABLE` guard around `FSTESTS_TFB_COPY_LIMIT`, but the visible symbol is `FSTESTS_TFB_COPY_ENABLE`; this may hide the copy-limit option unintentionally. Device defaults are destructive if pointed at the wrong disk. Sparse loop numbering encodes historic assumptions and can conflict with local loop use. Long soak presets can add days or months of runtime.

## Test Signals

Validate Kconfig for every filesystem choice, sparse and NVMe strategies, ZNS, watchdog combinations, custom group CLI detection, and soak presets. Generate fstests configs locally with the Makefile debug target and run a minimal auto group on disposable devices.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/workflows/fstests/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/workflows/fstests/Makefile -->
# sources/test-tools/kdevops/workflows/fstests/Makefile

## Purpose

This Makefile maps fstests Kconfig options into Ansible variables, includes filesystem-specific fragments, and exposes targets for setup, baseline/dev/test runs, config generation, result collection, TFB trimming, monitoring, and result display.

## Important APIs, Types, and Functions

Important variables are `FSTESTS_ARGS`, `FSTESTS_ARGS_SEPARATED`, `FSTESTS_ARGS_DIRECT`, `FSTESTS_BASELINE_EXTRA`, exported `FSTYP`, `FS_CONFIG`, `FSTESTS_DYNAMIC_RUNTIME_VARS`, `LAST_KERNEL`, `FIND_PATH`, `PATTERN`, and `XARGS_ARGS`. Targets include `fstests`, `fstests-kdevops-setup`, `fstests-baseline`, skip/update/oscheck variants, `fstests-config`, `fstests-config-debug`, `fstests-dev`, `fstests-tests`, TFB list/trim targets, results targets, `monitor-results`, `fstests-show-results`, and help.

## Control Flow

The Makefile strips Kconfig quotes, constructs role template paths, conditionally includes XFS/Btrfs/NFS/CIFS/tmpfs/sparsefile fragments, appends workflow args, and builds a runtime extra-vars string from make variables such as `RUN_FAILURES`, `SKIP_RUN`, `INITIAL_BASELINE`, `START_AFTER`, `SKIP_TESTS`, and `COUNT`. Targets call `playbooks/fstests.yml` with appropriate host limits, tags, skip-tags, and extra-vars.

## State and Persistence Behavior

It reads `workflows/fstests/results/last-kernel.txt` to choose a result display path. Persistent runtime state includes generated fstests configs, sparse backing devices, local copied results under `workflows/fstests/results`, TFB-trimmed files, and optional systemd journal forwarding.

## Dependencies and Integration Points

It integrates with per-filesystem Makefile fragments, `playbooks/fstests.yml`, `monitor-results.yml`, `extra_vars.yaml`, host groups `baseline` and `dev`, and upstream fstests result formats including `xunit_results.txt`.

## Risks and Edge Cases

The dynamic runtime variable string is hand-built and quote-sensitive. `fstests-show-results` uses `find | xargs`; empty results can invoke `cat` with no input unless xargs behavior is guarded by platform defaults. `COUNT` maps to `oscheck_extra_args: "-I $(COUNT)"`, so its meaning is delegated to oscheck/fstests. Result path selection depends on `last-kernel.txt` being coherent.

## Test Signals

Use `make -n` for all run/config/result targets with runtime knobs. Generate config locally with `fstests-config-debug`, run a small baseline on disposable sparse devices, test TFB list/trim behavior, and verify `fstests-show-results` with empty and populated result trees.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/workflows/fstests/Makefile -->
