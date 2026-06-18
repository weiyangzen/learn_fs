# subset-b-009064 research

Grouped research for WiredTiger Evergreen automation, coverage/reporting helpers, fops tests, and format build wiring. Each section is delimited for reconciliation into the mapped per-file document.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/evergreen/checkpoint_stress_test.sh -->
# sources/storage-engines/wiredtiger/test/evergreen/checkpoint_stress_test.sh

Purpose: runs `test_checkpoint` as a concurrent stress workload from the CMake `test/checkpoint` directory. It accepts `tiered`, `times`, `no_of_procs`, `wt_config`, and `timestamp_config`, exports a low-durability `WIREDTIGER_CONFIG`, and builds a command that runs random test mode with high operation/key counts. When `tiered` is enabled it appends `-PT`.

Control flow: for each outer iteration it launches `no_of_procs` background `nohup` jobs with distinct `WT_TEST.$i.$t` homes, then waits for each child via `wait -n`. On failure it filters noisy checkpoint/verification/thread-start lines from all `nohup.out.*` files, remembers the failing exit code, and exits after collecting process results.

State and persistence: creates test home directories and `nohup.out` logs in the current build directory; it does not clean them. It relies on inherited binaries and path context.

Dependencies and integration: called by Evergreen checkpoint stress task definitions in `test/evergreen.yml`; requires `test_checkpoint` and shell support for `wait -n`.

Risks and test signals: argument count is strict, and the command is assembled with `eval`, so quoting depends on Evergreen-supplied config expansions. Success is child exit status; logs become the main diagnostic signal.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/evergreen/checkpoint_stress_test.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/evergreen/checkpoint_test_predictable.sh -->
# sources/storage-engines/wiredtiger/test/evergreen/checkpoint_test_predictable.sh

Purpose: verifies deterministic checkpoint behavior by replaying `test_checkpoint` with predictable mode and timestamps. It must run from the `cmake_build/test/checkpoint` directory and accepts an iteration count followed by arbitrary checkpoint arguments.

Important behavior: `rando()` derives decimal seeds from `/dev/urandom`. A calibration run creates `RUNDIR_0` with fixed data seed and extra seed, runs predictable/timestamp mode (`-x -R` plus `-PSD...`), then reads the stable timestamp using `tools/wt_timestamps`. Each later iteration runs two homes (`RUNDIR_1`, `RUNDIR_2`) to the same stop timestamp and same data seed but different extra seeds, then compares directories with `tools/wt_cmp_dir`.

State and persistence: repeatedly removes and recreates `RUNDIR_0/1/2`; persistent evidence is stdout plus any retained failing directories. It uses no global state except the generated seeds and timestamp.

Dependencies and integration: depends on `test_checkpoint`, `tools/wt_timestamps`, and `tools/wt_cmp_dir`. It is wired into Evergreen checkpoint predictable tasks.

Risks and test signals: failures come from calibration/test binary exit status or directory mismatch. Seed generation strips leading zeroes, but empty output from the pipeline would produce malformed seeds. The cwd guard prevents accidental execution from the wrong build location.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/evergreen/checkpoint_test_predictable.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/evergreen/code_change_report/change_info.py -->
# sources/storage-engines/wiredtiger/test/evergreen/code_change_report/change_info.py

Purpose: defines the small data carrier used by code-change report tooling to represent one parsed diff hunk. `ChangeInfo` stores `status`, `new_file_path`, `old_file_path`, `new_start`, `new_lines`, `old_start`, `old_lines`, and raw pygit2 hunk `lines`.

APIs and dependencies: the only public API is `ChangeInfo.__init__`. It has no imports and no validation; callers are expected to supply values copied from `pygit2.Patch` and `pygit2.Hunk` objects.

Control flow and state: construction is a direct assignment of fields. Instances are transient in-memory objects created by `code_change_helpers.diff_to_change_list()` and consumed by `code_change_info.py` and `per_test_code_coverage_report.py`.

Integration points: the fields mirror pygit2 diff metadata and become JSON in downstream report builders. `lines` remains a list of pygit2 line objects until later converted into serializable dictionaries.

Risks and test signals: because there is no type enforcement or normalization, downstream code assumes the hunk/line objects expose `content`, `new_lineno`, and `old_lineno`. Renames are represented by both old and new file paths, but dictionary consumers key primarily by new path.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/evergreen/code_change_report/change_info.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/evergreen/code_change_report/code_change_helpers.py -->
# sources/storage-engines/wiredtiger/test/evergreen/code_change_report/code_change_helpers.py

Purpose: shared helper module for diff and Metrix++ complexity processing in the code-change report pipeline. It converts pygit2 diffs to `ChangeInfo` lists and normalizes Metrix++ CSV data.

Important APIs: `is_useful_line(content)` filters blank lines and lone braces so gcov line counts are not treated as meaningful code. `diff_to_change_list(diff)` iterates pygit2 patches, logs status and hunk ranges, wraps each hunk in `ChangeInfo`, and returns `{new_file_path: [hunks...]}`. `read_complexity_data(path)` loads CSV rows as dictionaries. `preprocess_complexity_data(rows)` rewrites leading `./` paths to `src/`, groups by file, and indexes only rows whose `type` is `function` by `region` name.

State and persistence: reads CSV files but writes nothing. Returned dictionaries are consumed by code-change and per-test coverage scripts.

Dependencies and integration: imports `csv`, `logging`, `pygit2.Diff`, and local `ChangeInfo`. The path rewrite is tightly coupled to running Metrix++ from `src/` while gcovr and git diffs use `src/...` paths.

Risks and test signals: duplicate function names in a file overwrite earlier rows. `is_useful_line` is intentionally simple and can still count comments/preprocessor-only lines. Diff parsing correctness depends on pygit2 patch objects and new-file path uniqueness.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/evergreen/code_change_report/code_change_helpers.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/evergreen/code_change_report/code_change_info.py -->
# sources/storage-engines/wiredtiger/test/evergreen/code_change_report/code_change_info.py

Purpose: creates the JSON input for the HTML code-change report by joining Git diff hunks, gcovr full JSON coverage, and current/previous Metrix++ complexity CSVs.

Important APIs: `read_coverage_data`, `get_git_diff`, `find_file_in_coverage_data`, `find_line_data`, `find_line_coverage`, and `find_covered_branches` query gcovr data. `get_function_coverage()` counts executable lines and branches in a function range, while `get_function_info()` locates the function containing a changed line and adds complexity, line count, coverage, and previous-version metrics. `create_report_info()` produces `summary_info`, `change_info_list`, and `changed_functions`.

Control flow: `main()` parses coverage, complexity, previous complexity, git root, optional diff file, output, and verbose flags. It reads coverage/CSV inputs, gets a pygit2 diff either from repository HEAD versus parent or from `Diff.parse_diff()`, converts hunks, creates the report object, and writes pretty JSON.

State and persistence: reads repository metadata and report inputs; writes only the output JSON. Summary counters count added/changed useful lines where `old_lineno < 0`.

Dependencies and integration: used by `coverage-report.sh`; depends on pygit2, gcovr JSON schema, Metrix++ CSV columns, and local helpers.

Risks and test signals: HEAD must have a parent when no diff file is supplied. Diff parse failures fall back to an empty diff. Function lookup is line-range based and duplicate function names can collapse. Branch counts assume non-negative gcovr counts except later HTML code handles negative branch counts.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/evergreen/code_change_report/code_change_info.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/evergreen/code_change_report/code_change_report.py -->
# sources/storage-engines/wiredtiger/test/evergreen/code_change_report/code_change_report.py

Purpose: renders `code_change_info.py` JSON into an HTML report and optionally maintains a sticky GitHub PR comment summarizing changed-code coverage and complexity warnings.

Important APIs: report helpers colorize line/branch coverage (`get_html_color`, `get_coverage_html_color`), complexity (`get_complexity_html_color`), and deltas (`change_string`). `generate_summary_table()`, `generate_changed_function_table()`, `generate_file_info_as_html_text()`, and `generate_html_report_as_text()` build HTML as lists of strings. `build_pr_comment()` creates markdown with line/branch coverage links and high-complexity warnings. `post_pr_comment()` searches issue comments for a magic marker, then creates, updates, or deletes it.

Control flow: `main()` parses input JSON, output HTML, optional report URL, GitHub repo/PR/token, and verbose flag. It writes HTML unconditionally and posts comments only when both PR number and token are present.

State and persistence: writes the HTML report, uses GitHub issue comment state when enabled, and reads no repository state directly.

Dependencies and integration: consumes the exact JSON contract from `code_change_info.py`; `coverage-report.sh` builds the URL and PR arguments. Uses `requests` and GitHub REST API.

Risks and test signals: HTML is assembled manually, so structural mistakes are possible. Only `src/` files receive detailed line tables. Existing sticky comment lookup assumes the marker appears in an early page of comments. Coverage URL derivation uses string replacement of Evergreen task and file names.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/evergreen/code_change_report/code_change_report.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/evergreen/code_change_report/git_diff_tool.py -->
# sources/storage-engines/wiredtiger/test/evergreen/code_change_report/git_diff_tool.py

Purpose: produces a Git diff file suitable for pygit2 parsing by excluding newly added empty files, deleted files, and renames involving empty files. This works around pygit2 failures on diffs for newly added zero-length files.

Important APIs: `run_command(directory, command)` temporarily changes cwd and runs a shell command. `get_merge_base_commit()` finds `git merge-base develop HEAD`. `find_zero_length_files()` scans the worktree. `find_deleted_files()` and `find_moved_zero_length_files()` use Git name-status filters. `create_diff_file()` combines exclusions into `:(exclude)` pathspecs and writes `git diff <merge-base> -- ...`.

Control flow: `main()` accepts `--git_root`, `--git_diff_file`, and `--verbose`, then delegates to `create_diff_file()`.

State and persistence: reads worktree and Git history; writes a diff file with a trailing newline. It changes process cwd through `PushWorkingDirectory`.

Dependencies and integration: used by coverage and per-test coverage scripts before `Diff.parse_diff()`. Depends on `git`, pygit2 repository discovery, shell pathspec handling, and a branch named `develop`.

Risks and test signals: `subprocess.run(..., shell=True)` and hand-built command strings make quoting important. Large exclusion lists can exceed command-line length. The helper is not exception-safe if `run_command` fails before `pop()`. Renamed file parsing assumes three whitespace-separated fields.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/evergreen/code_change_report/git_diff_tool.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/evergreen/code_change_report/per_test_code_coverage_report.py -->
# sources/storage-engines/wiredtiger/test/evergreen/code_change_report/per_test_code_coverage_report.py

Purpose: correlates changed functions with per-test gcovr outputs to identify which test commands reached each changed function. It is a diagnostic companion to the full code-change report.

Important APIs: `collate_coverage_data(gcovr_dir)` scans build copy directories, reads `task_info.json` and `full_coverage_report.json`, and indexes by task command. `get_function_info()` maps changed line numbers to Metrix++ function ranges. `create_report_info()` extracts changed functions from a pygit2 diff. `get_function_coverage()` checks each test's file/line counts for any covered line within the function range. `generate_report()` logs changed files/functions and reached-by-test lines.

Control flow: `main()` parses coverage data directory, diff file, complexity CSV, and verbose flag. It parses the diff, reads/preprocesses complexity data, collates coverage JSON, and logs the reachability report.

State and persistence: reads many JSON reports from per-test build copies; writes no report file itself. Output is logging/stdout.

Dependencies and integration: invoked by `code_coverage/coverage-report-per-test.sh` after per-test coverage generation. Depends on gcovr full JSON schema, `task_info.json`, pygit2 diff parsing, and Metrix++ CSV columns.

Risks and test signals: memory use can be large because all coverage JSON is loaded. Build copy names are selected by `build_*copy`. Failed tests may still produce partial coverage but missing JSON will fail reads. The function coverage result is logged only in verbose/debug mode.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/evergreen/code_change_report/per_test_code_coverage_report.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/evergreen/code_change_report/push_working_directory.py -->
# sources/storage-engines/wiredtiger/test/evergreen/code_change_report/push_working_directory.py

Purpose: provides a minimal cwd stack object for scripts that need to run relative shell/Git commands from a specific directory.

API: `PushWorkingDirectory(new_working_directory)` records `os.getcwd()` and immediately calls `os.chdir(new_working_directory)`. `pop()` changes back to the original directory.

Control flow and state: the object mutates process-global current working directory on construction and restoration. It does not implement context-manager methods, so callers must explicitly call `pop()`.

Dependencies and integration: used by `git_diff_tool.py` for `run_command()`, file scans, and deleted/renamed file discovery. A separate duplicate implementation exists in `code_coverage_utils.py`.

Risks and test signals: not exception-safe; an exception between construction and `pop()` leaves the process in the wrong directory. It is also unsafe for concurrent threads in the same process because cwd is process-wide. The class has no validation of target directory existence beyond `os.chdir()` exceptions.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/evergreen/code_change_report/push_working_directory.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/evergreen/code_complexity_analysis.py -->
# sources/storage-engines/wiredtiger/test/evergreen/code_complexity_analysis.py

Purpose: converts Metrix++ complexity outputs into an Atlas-compatible JSON metric document for Evergreen code statistics tasks.

Important APIs: `get_atlas_compatible_code_statistics(summaryFile, dataFile, outfile)` wraps metrics under `Test Name: Code Complexity`. `get_code_complexity()` returns a list containing average complexity, range counts, and top regions. `get_region_list()` uses pandas `nlargest()` on `std.code.complexity:cyclomatic`. `get_complexity_ranges_list()` counts functions above 20, 50, and 90. `get_average()` parses the Metrix++ Python-formatted view output with `ast.literal_eval()` and extracts the aggregate cyclomatic average.

Control flow: `main()` requires `--summary`, optional `--outfile`, and `--data_file`, then writes JSON.

State and persistence: reads Metrix++ view text and CSV; writes the Atlas output, creating the parent directory if needed.

Dependencies and integration: called by `cyclomatic-complexity.sh` after Metrix++ collect/view/export. Depends on pandas and exact CSV column names.

Risks and test signals: `dataFile` is optional in argparse but required by the processing path. `get_average()` error text intends to include exception details but lacks f-string interpolation for `{e.text}`. Parsing uses Python literals rather than strict JSON because Metrix++ view emits Python-like output.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/evergreen/code_complexity_analysis.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/evergreen/code_coverage/code_coverage_config.json -->
# sources/storage-engines/wiredtiger/test/evergreen/code_coverage/code_coverage_config.json

Purpose: drives broad code coverage execution. It defines setup actions to configure a coverage build and a long ordered `test_tasks` list spanning csuite binaries, cppsuite workloads, Python suite tests, examples, `wt` utility commands, ctest filters, and disaggregated hook tests.

Data contract: top-level keys are `_comments`, `setup_actions`, and `test_tasks`. The setup uses `cmake --preset linux-gcc` with coverage and inline-function flags, `ninja -j 16`, creates `WT_HOME_COVERAGE`, runs `ex_hello`, and loads `test_table.json`. `parallel_code_coverage.py` and `per_test_code_coverage.py` expect exactly these keys and command strings.

State and persistence: setup creates build directories and test data used by later commands. The task list is ordered by expected duration so the parallel queue finishes efficiently; `parallel_code_coverage.py --optimize_test_order` can rewrite this file.

Dependencies and integration: referenced by `coverage-report-per-test.sh` and likely Evergreen coverage tasks. Commands assume execution from a copied coverage build directory where `../test/...`, `test/csuite/...`, and `./wt` paths resolve.

Risks and test signals: JSON comments are embedded as strings because JSON has no comments. Duplicate tasks exist intentionally or accidentally and may skew coverage/runtime. Any command containing shell syntax is later split on whitespace, so complex quoting is fragile.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/evergreen/code_coverage/code_coverage_config.json -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/evergreen/code_coverage/code_coverage_config_catch2.json -->
# sources/storage-engines/wiredtiger/test/evergreen/code_coverage/code_coverage_config_catch2.json

Purpose: minimal coverage configuration for running only Catch2 unit tests under the same coverage harness used by broader coverage tasks.

Data contract: contains `_comments`, `setup_actions`, and `test_tasks`. Setup configures a coverage build with `cmake --preset linux-gcc`, unit tests enabled, diagnostics disabled, coverage instrumentation, inline-function flag, Coverage build type, and Ninja generator, then runs `ninja`. The sole test command is `test/catch2/catch2-unittests`.

State and persistence: creates instrumented build directories via the Python coverage runners. Runtime coverage files are emitted by Catch2 execution and collected by gcovr.

Dependencies and integration: used by Evergreen `coverage-report-catch2` and the coverage Python scripts. Requires the Catch2 target to be built and coverage flags to produce `.gcno`/`.gcda`.

Risks and test signals: the setup uses plain `ninja` rather than explicit `-j`, so runtime depends on Ninja defaults. The same command-splitting limitations apply as with the main coverage config. Failure signals come from setup command exit codes, Catch2 exit code, and missing coverage files detected by `check_build_dirs()`.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/evergreen/code_coverage/code_coverage_config_catch2.json -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/evergreen/code_coverage/code_coverage_utils.py -->
# sources/storage-engines/wiredtiger/test/evergreen/code_coverage/code_coverage_utils.py

Purpose: shared execution utilities for parallel and per-test coverage runners. It creates/checks build directories and dispatches tasks across process workers.

Important APIs: `PushWorkingDirectory` changes cwd and restores via `pop()`. `setup_run_tasks_parallel()` initializes each worker process by taking one build directory from a multiprocessing queue and `chdir`ing into it. `run_task_lists_in_parallel()` creates a `ProcessPoolExecutor`, submits all tasks, optionally checks results, and optionally collects timing data. `check_build_dirs()` validates that copied build directories contain compile-time `.gcno` files and logs runtime `.gcda` presence. `setup_build_dirs()` creates build_0, executes setup commands there, then copies it to the remaining build dirs.

State and persistence: creates and copies build directories; reads coverage files to validate state. It does not clean directories.

Dependencies and integration: imported by `parallel_code_coverage.py` and `per_test_code_coverage.py`. Depends on multiprocessing, subprocess, shutil, and command strings from config JSON.

Risks and test signals: `task.split()` is not shell-compatible quoting. `PushWorkingDirectory` is not exception-safe. Setup command failures are logged but not re-raised, so later missing `.gcno` checks may be the effective failure. Worker count equals number of build dirs.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/evergreen/code_coverage/code_coverage_utils.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/evergreen/code_coverage/coverage-report-per-test.sh -->
# sources/storage-engines/wiredtiger/test/evergreen/code_coverage/coverage-report-per-test.sh

Purpose: Evergreen wrapper for per-test coverage collection and changed-function reachability diagnostics.

Control flow: requires `is_patch` and `num_jobs`, runs `find_cmake.sh`, prints disk usage, creates `coverage_data` and `coverage_report`, creates a Python virtualenv, and installs gcovr/pygit2/requests dependencies. It downloads Metrix++, collects/export complexity data from `src`, then runs `code_coverage/per_test_code_coverage.py` with setup enabled, the main coverage config, absolute build dir base, job count, and absolute gcovr output dir. After tests it removes `build*copy*` directories, and for patch builds generates a filtered diff, HTML-friendly diff, logs it, and runs `per_test_code_coverage_report.py`. Finally it tars `coverage_data`.

State and persistence: writes virtualenv, coverage data/report directories, Metrix++ checkout/db, build dirs, diff files, and a tarball.

Dependencies and integration: called by Evergreen `coverage-report-per-test`. Depends on CMake, gcovr, Metrix++, coverage config JSON, git, and local report scripts.

Risks and test signals: very disk-heavy; cleanup occurs only after coverage tests. `rm -Rf build*copy*` prevents command-line length problems for later diff exclusion. Patch-only diagnostics write mostly to logs rather than structured output.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/evergreen/code_coverage/coverage-report-per-test.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/evergreen/code_coverage/parallel_code_coverage.py -->
# sources/storage-engines/wiredtiger/test/evergreen/code_coverage/parallel_code_coverage.py

Purpose: runs coverage test commands in parallel across copied build directories, optionally setting up those directories and optionally rewriting the task list by observed runtime.

Important APIs: `run_task(index, task)` sets `GCOV_PREFIX_STRIP` and `GCOV_PREFIX` for copied-build gcov output remapping, runs the task with stdout/stderr suppressed, exits on failure, and returns timing data. `main()` validates bucket and parallel arguments, loads config JSON, builds or checks build dirs, filters `test_tasks` by `python` or `other`, dispatches through `run_task_lists_in_parallel()`, and in optimize mode sorts tasks by descending runtime and rewrites the config.

State and persistence: setup mode creates build directories via shared utilities. Runtime produces `.gcda` files in per-worker build dirs. Optimize mode mutates the JSON config file.

Dependencies and integration: used by Evergreen split coverage tasks (`coverage-report-python` and `coverage-report-other`). Depends on `code_coverage_utils.py`, gcov cross-profiling environment variables, and command strings that can be safely split.

Risks and test signals: bucket detection is a regex search for `"python"` anywhere in the command. `sys.exit()` inside process workers reports failures through futures only when `--check_errors` is used. Mutating config in optimize mode should not be combined with bucketed subsets, and the script enforces that.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/evergreen/code_coverage/parallel_code_coverage.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/evergreen/code_coverage/per_test_code_coverage.py -->
# sources/storage-engines/wiredtiger/test/evergreen/code_coverage/per_test_code_coverage.py

Purpose: captures coverage separately for each configured test command by running tests in copied build directories, copying each completed build directory, and optionally running gcovr over every copy.

Important APIs: `delete_runtime_coverage_files()` removes `.gcda` files before each task. `run_coverage_task(index, task)` sets GCOV remapping, deletes old runtime coverage, executes the test, copies the build dir to `build_N_copy`, and writes `task_info.json`. `run_gcovr(build_dir_base, gcovr_dir)` scans sibling build copies, creates one output directory per copy, copies task info, and runs gcovr with HTML, summary JSON, and full JSON outputs.

Control flow: `main()` validates arguments, enforces absolute `gcovr_dir`, loads config, sets up or checks build dirs, dispatches all test tasks through the shared process pool, and then runs gcovr when requested.

State and persistence: creates many full build directory copies and gcovr report directories. This is intentionally high-disk-use and later packed by wrapper scripts.

Dependencies and integration: used by `coverage-report-per-test.sh`; output is consumed by `per_test_code_coverage_report.py`.

Risks and test signals: failed test commands are printed but not necessarily fatal unless future exception behavior is triggered; `CalledProcessError` is swallowed in `run_coverage_task`. Copy names depend on task index and can be large. `task.split()` limits commands with quoted arguments.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/evergreen/code_coverage/per_test_code_coverage.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/evergreen/code_coverage/test_table.json -->
# sources/storage-engines/wiredtiger/test/evergreen/code_coverage/test_table.json

Purpose: fixture data loaded into `WT_HOME_COVERAGE` during coverage setup so later `wt` utility commands can operate on a known table.

Data contract: JSON uses `WiredTiger Dump Version` and a `table:test_table` array containing metadata/config and data entries. The table config defines a file-backed btree with string key/value formats, logging enabled, checksum on, and source `file:test_table.wt`. The data section inserts two simple string-key/string-value records.

State and persistence: consumed by `./wt -h WT_HOME_COVERAGE load -j -f ../test/evergreen/code_coverage/test_table.json`, which creates persistent WiredTiger table data in the coverage home.

Dependencies and integration: referenced directly from `code_coverage_config.json` setup actions. Later coverage commands exercise utility operations such as list, dump, verify, alter, write, and drop against `test_table`.

Risks and test signals: format must remain compatible with the `wt load -j` JSON dump parser and WiredTiger version expectations. Changes to table config can alter utility coverage and behavior. Because coverage tasks run destructive `wt` commands, setup copies isolate this fixture per build directory.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/evergreen/code_coverage/test_table.json -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/evergreen/code_coverage_analysis.py -->
# sources/storage-engines/wiredtiger/test/evergreen/code_coverage_analysis.py

Purpose: reads gcovr JSON summary output and prints or writes higher-level coverage metrics, including Atlas-compatible component coverage.

Important APIs: `read_coverage_data()` loads gcovr summary JSON. `read_timing_data()` reads start/end seconds from a two-line file and returns elapsed seconds. `get_branch_coverage()` aggregates branch covered/total counts by component, where component is `filename.split('/')[1]`, inserts overall branch percent, and returns Atlas metric dictionaries. `get_component_coverage()` wraps those metrics under `Test Name: Code Coverage` and writes JSON.

Control flow: `main()` parses summary, outfile, coverage type, timing data, and verbose flag. Default mode prints overall branch coverage and optionally coverage rate per minute. `component_coverage` mode writes the Atlas JSON.

State and persistence: reads `coverage_report/1_coverage_report_summary.json`; optionally writes `atlas_out_code_coverage.json`.

Dependencies and integration: called by `code_coverage_analysis.sh` after gcovr. Depends on gcovr summary fields `branch_percent`, `files`, `filename`, `branch_covered`, and `branch_total`.

Risks and test signals: component extraction assumes paths contain at least two slash-separated parts and nonzero branch totals. Timing file parsing assumes exactly integer seconds. The `outfile` default in `get_branch_coverage` is unused.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/evergreen/code_coverage_analysis.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/evergreen/code_coverage_analysis.sh -->
# sources/storage-engines/wiredtiger/test/evergreen/code_coverage_analysis.sh

Purpose: Evergreen shell wrapper around gcovr and `code_coverage_analysis.py` for full or combined coverage reports.

Control flow: validates at least coverage filter, job count, and Python binary; if `combine_coverage_report` is `True`, requires two tracefile paths. It creates a Python virtualenv, installs gcovr dependencies, creates `coverage_report`, defines gcovr output flags for self-contained HTML details, summary JSON, and full JSON. In combine mode it runs gcovr with two `--add-tracefile` inputs. Otherwise it scans local coverage files with `-f $coverage_filter`, then runs the Python analyzer with timing data. If `generate_atlas_format` is non-empty, it writes component coverage Atlas JSON.

State and persistence: writes virtualenv and coverage report outputs. Reads optional `time.txt` and tracefile inputs.

Dependencies and integration: invoked by Evergreen coverage report tasks. Requires gcovr 5.0 and a build tree with `.gcno/.gcda` files or supplied tracefiles.

Risks and test signals: tests for non-empty strings use unquoted variables (`[ ! -z $combine_coverage_report ]`), so unset/empty values can behave unexpectedly. Combine mode skips the timing/rate print. Success depends on gcovr exit status and analyzer schema compatibility.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/evergreen/code_coverage_analysis.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/evergreen/collect_stat_files.py -->
# sources/storage-engines/wiredtiger/test/evergreen/collect_stat_files.py

Purpose: gathers WiredTiger statistics log files from a build/test tree into a single directory for artifact packaging.

Important APIs: `collect_stat_files(destination_dir, source_dir, regex)` creates a unique destination subdirectory by stripping a leading `./` and replacing slashes with dashes, then copies all files in `source_dir` matching `WiredTigerStat.*`. `main()` walks the current tree, skips the destination directory, and calls the collector once for any directory containing a matching file.

State and persistence: creates destination subdirectories and copies stat files. It does not remove prior collected files.

Dependencies and integration: used in Evergreen upload-stat-files functions from `evergreen.yml` and `evergreen_disagg.yml`, usually from `wiredtiger/cmake_build`.

Risks and test signals: skip logic checks `if destination_dir in walk_dir`, which can skip unrelated paths containing the same substring. Destination naming can collide if different source paths normalize to the same dash-separated string. It only scans files directly in a directory, not recursively per collection call, but the outer `os.walk` covers recursion.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/evergreen/collect_stat_files.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/evergreen/configure_combinations.sh -->
# sources/storage-engines/wiredtiger/test/evergreen/configure_combinations.sh

Purpose: CI smoke script that builds and installs WiredTiger across a matrix of CMake presets and option combinations, then verifies examples and pkg-config output by compiling and running `ex_smoke.c`.

Important functions: argument parsing supports `--generator` and `--parallel`. `discover_compiler()` creates a temporary CMake project with copied `CMakePresets.json` to discover `CMAKE_C_COMPILER` for a preset. `BuildTest(compiler, options, compiler_path)` configures a fresh `build`, builds WiredTiger, builds examples, installs, obtains `pkg-config` flags, compiles `smoke`, and runs it with `LD_LIBRARY_PATH`.

State and persistence: repeatedly deletes and recreates `build`, installs under `installed`, and sets `PKG_CONFIG_PATH`. It leaves the final build/install outputs.

Dependencies and integration: invoked from Evergreen configure-combinations task after `find_cmake.sh` and SWIG setup. Depends on Linux GCC/Clang presets, CMake/Ninja/Make, pkg-config, and examples.

Risks and test signals: the script itself uses `cat >` in the source file, but runtime behavior is intentional. Generator string escaping for Unix Makefiles is delicate. Failures set `ecode=1` after continuing the matrix, providing broad failure coverage but potentially long logs.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/evergreen/configure_combinations.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/evergreen/coverage-report.sh -->
# sources/storage-engines/wiredtiger/test/evergreen/coverage-report.sh

Purpose: generates the changed-code coverage/complexity HTML report after full coverage data is available.

Control flow: accepts `is_patch`, Python binary, GitHub commit, and optional PR args. It creates a virtualenv and installs pygit2/requests. For patch builds it runs `git_diff_tool.py`, writes `diff.txt` and `diff.html`, and passes `-d` to code-change info generation. It downloads Metrix++, collects current complexity from `src`, then creates a detached `wiredtiger_previous` worktree at `github_commit`, checks out either the branch point from develop for patches or `HEAD~` for non-patches, and collects previous complexity. Finally it runs `code_change_info.py`, logs JSON, and runs `code_change_report.py`.

State and persistence: writes virtualenv, Metrix++ checkout/db, `coverage_report/metrixpp*.csv`, diff files, `code_change_info.json`, `code_change_report.html`, and a Git worktree.

Dependencies and integration: Evergreen `code-change-report` task consumes coverage artifacts and uses this wrapper. Depends on `coverage_report/full_coverage_report.json`, git, Metrix++, pygit2, and optional GitHub PR token args.

Risks and test signals: worktree cleanup is not handled here. Patch branch-point logic depends on `dist/common_functions.py last_commit_from_dev`. The script assumes `src` exists and coverage paths align with complexity paths.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/evergreen/coverage-report.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/evergreen/cppsuite_test_run.sh -->
# sources/storage-engines/wiredtiger/test/evergreen/cppsuite_test_run.sh

Purpose: wrapper for running a single cppsuite workload in Evergreen while temporarily adjusting Linux perf permissions needed by latency/performance collection.

Control flow: validates one to three arguments (`test_name`, `test_config_filename`, `test_config`), reads the current `kernel.perf_event_paranoid` value with `sudo sysctl`, sets it to `2`, runs `./run -t ... -C ... -f ... -l 2`, captures exit code, restores the original sysctl value, writes `cppsuite_exit_code`, and if the test failed writes a minimal empty-metrics JSON file named after the test.

State and persistence: mutates kernel sysctl during execution; writes `cppsuite_exit_code` and possibly `<test_name>.json`.

Dependencies and integration: called from Evergreen cppsuite test functions in `test/evergreen.yml`, from the cppsuite build directory where `./run` exists.

Risks and test signals: exits `0` even if the test fails, pushing failure signaling into `cppsuite_exit_code` and generated JSON. Requires passwordless or configured `sudo`. Restoring sysctl is not protected by a trap, so abrupt termination can leave the changed setting.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/evergreen/cppsuite_test_run.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/evergreen/cyclomatic-complexity.sh -->
# sources/storage-engines/wiredtiger/test/evergreen/cyclomatic-complexity.sh

Purpose: collects cyclomatic complexity metrics, enforces high-complexity gates, and writes Atlas-compatible complexity statistics.

Control flow: sources `download_metrixpp.sh`, creates `code_statistics_report`, enters `src`, runs Metrix++ collect/view, reports all functions above complexity 20, then fails if any function exceeds 98 by redirecting Metrix++ limit output to `$t` and grepping for `exceeds`. It writes a Python-format summary JSON and CSV export, creates a virtualenv, installs pandas, and runs `code_complexity_analysis.py`.

State and persistence: creates Metrix++ db under `src`, `code_statistics_report/code_complexity_summary.json`, `metrixpp.csv`, and `atlas_out_code_complexity.json`.

Dependencies and integration: Evergreen `cyclomatic-complexity` task. Depends on Metrix++ pinned clone, Python, pandas, and exact Metrix++ output shape.

Risks and test signals: `$t` is not initialized in the script, so it relies on environment or shell behavior and may fail unexpectedly. Complexity threshold failure is explicit with `[ERROR]` log lines. Running from the wrong repo root breaks relative paths.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/evergreen/cyclomatic-complexity.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/evergreen/doc_update.py -->
# sources/storage-engines/wiredtiger/test/evergreen/doc_update.py

Purpose: pushes already-generated documentation updates to a GitHub Pages repository using a GitHub App installation token.

Control flow and APIs: defines context manager `cwd(path)` to temporarily change directories. At module execution it reads `GITHUB_APP_ID` and `GITHUB_APP_PRIVATE_KEY`, creates `AppAuth` and `GithubIntegration`, reads `GITHUB_OWNER` and `GITHUB_REPO`, finds the app installation for that repo, obtains an installation access token, changes into `wiredtiger.github.com`, and runs `git push https://'<app_id>:<token>'@github.com/<owner>/<repo>`.

State and persistence: reads environment secrets and pushes the current local commit in `wiredtiger.github.com`; it does not generate docs itself.

Dependencies and integration: invoked by Evergreen documentation update workflow after docs are built and committed. Depends on PyGithub, git, environment variables, and local repository layout.

Risks and test signals: uses `subprocess.run([cmd], shell=True)`, mixing list and shell mode. Token appears in the command string, though not printed by the script. All exceptions exit with their message. Missing env vars are explicitly validated.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/evergreen/doc_update.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/evergreen/download_metrixpp.sh -->
# sources/storage-engines/wiredtiger/test/evergreen/download_metrixpp.sh

Purpose: fetches a pinned Metrix++ source checkout for complexity analysis tasks.

Control flow: clones `https://github.com/metrixplusplus/metrixplusplus` into `metrixplusplus`, enters that directory, and checks out commit `78dc5380de9aaa3d615f8be6c84e90cb2ae0d90b`, then returns to the parent directory.

State and persistence: creates a `metrixplusplus` directory in the current working directory. It does not handle an existing checkout; clone failure exits immediately.

Dependencies and integration: sourced by `coverage-report.sh`, `coverage-report-per-test.sh`, and `cyclomatic-complexity.sh`. The pin exists because the latest code needed by WiredTiger is not available from a release archive and uncontrolled latest changes would destabilize metrics.

Risks and test signals: network dependency on GitHub. The script uses `/bin/sh` but is sourced by Bash wrappers as well. Existing `metrixplusplus` directories cause clone failure. Comment text says the pinned version is latest as of February 28, 2024; changing the pin can alter complexity results and report comparability.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/evergreen/download_metrixpp.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/evergreen/ensure_swig_version.sh -->
# sources/storage-engines/wiredtiger/test/evergreen/ensure_swig_version.sh

Purpose: source-only setup script that ensures `swig` version 4.0.0 or later is available on `PATH` for WiredTiger builds.

Control flow: defines required version `4.0.0` and install version `4.2.1`, obtains the current version using `swig -version | awk`, and compares with `sort -V`. If current SWIG is new enough it prints a confirmation. Otherwise it creates a Python virtualenv, activates it, installs `swig==4.2.1` from pip, and prints the resulting version.

State and persistence: may create/activate `venv` in the current directory and mutate the caller's environment, which is why the header says it must be sourced rather than executed.

Dependencies and integration: sourced during Evergreen configure/build paths and spawn-host setup. Depends on `swig` being callable enough to report a version or on pip package availability.

Risks and test signals: if `swig` is absent, the command substitution may produce an empty version and comparison behavior depends on shell utilities. It intentionally changes caller `PATH` via virtualenv activation. The script has no shebang and assumes Bash because it uses `[[ ]]`.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/evergreen/ensure_swig_version.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/evergreen/evg_cfg.py -->
# sources/storage-engines/wiredtiger/test/evergreen/evg_cfg.py

Purpose: CLI helper to check or generate Evergreen task snippets for test directories that should be represented in `test/evergreen.yml`.

Important APIs: `run()` executes shell commands and returns output. `get_make_check_dirs()` finds `CMakeLists.txt` files with `add_test`, `define_c_test`, or `define_test_variants`, excluding build folders and known subtrees. `get_csuite_dirs()` lists csuite child directories. `find_tests_missing_evg_cfg()` derives make-check task names from directory names and checks whether they appear in the config file. `generate_evg_cfg_for_missing_tests()` fills a template and inserts it before a search marker.

Control flow: argparse supports `check` and `generate`, `-t TEST_TYPE`, and verbose. `evg_cfg()` changes to repo root, runs checks for one or all test types, exits nonzero when missing tasks are found, or edits `test/evergreen.yml` in generate mode.

State and persistence: check mode reads files only; generate mode writes `test/evergreen.yml`.

Dependencies and integration: relies on Git repo root, CMake test declarations, task templates, and marker comments.

Risks and test signals: csuite missing check currently skips every csuite directory, so csuite generation is ineffective. Task existence is substring-based. `generate all` calls generation per type and exits if one type has no missing tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/evergreen/evg_cfg.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/evergreen/find_cmake.sh -->
# sources/storage-engines/wiredtiger/test/evergreen/find_cmake.sh

Purpose: discovers or installs usable `cmake` and `ctest` binaries for Evergreen and spawn-host environments.

Control flow: defines fallback CMake version 3.13.0 and `find_cmake()`. The function honors existing `CMAKE`, then checks MongoDB toolchain, Homebrew, CMake.app, `/opt/cmake`, `cmake3`, `cmake`, downloaded Linux binary tarball, Cygwin path, and previous `cmake-install`. If no working CMake is found, it downloads CMake source, bootstraps, builds, and installs under `cmake-install`. It prints paths and versions for both CMake and CTest.

State and persistence: may download `cmake.tar.gz`, create `cmake-3.13.0`, and create `cmake-install`. Exports shell variables only in the running shell when sourced; when executed they affect the script process only.

Dependencies and integration: called or sourced by many Evergreen scripts before configure/build steps.

Risks and test signals: source build is expensive. The ERR trap returns from the function on failure and is cleared at the end. Version 3.13.0 is old for some modern platforms, so earlier path checks matter. Success is visible through printed command paths and version output.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/evergreen/find_cmake.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/evergreen/format_test_predictable.sh -->
# sources/storage-engines/wiredtiger/test/evergreen/format_test_predictable.sh

Purpose: validates deterministic replay of `test/format` by comparing multiple runs stopped at the same operation count/timestamp.

Control flow: accepts `times` and optional extra format args. For each iteration it runs `./t` with `CONFIG.replay` for a short timer into `RUNDIR_1`, reads the stable timestamp using `tools/wt_timestamps`, converts it to operations, then reruns from `RUNDIR_1/CONFIG` with `runs.timer=0` and `runs.ops=$ops` into `RUNDIR_2` and `RUNDIR_3` using different `random.extra_seed` values. It compares `RUNDIR_1` versus `RUNDIR_2`, then `RUNDIR_2` versus `RUNDIR_3`.

State and persistence: removes/recreates `RUNDIR_1/2/3`. On failure the `fail()` helper prints available CONFIG files and exits.

Dependencies and integration: called by Evergreen predictable format tasks from `cmake_build/test/format`. Depends on `./t`, `CONFIG.replay`, `tools/wt_timestamps`, and `tools/wt_cmp_dir`.

Risks and test signals: operation count comes from stable timestamp semantics; if timestamp extraction fails, arithmetic fails. Extra args are passed unquoted as a single variable. Directory compare failures are the main signal for nondeterminism.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/evergreen/format_test_predictable.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/evergreen/perf_submission.sh -->
# sources/storage-engines/wiredtiger/test/evergreen/perf_submission.sh

Purpose: submits Cedar-style performance result JSON to MongoDB's Signal Processing Service/raw performance endpoint.

Control flow: derives `is_mainline` from Evergreen `requester == commit`, extracts a username/order suffix from `revision_order_id`, then POSTs `${perf_file_path}` to a URL containing project, version, variant, order, task name/id, execution, and mainline query parameters. It appends `HTTP_STATUS` to curl output, separates status and response body, exits nonzero unless status is 200, and prints the response body/status.

State and persistence: no local writes. Sends performance data over HTTP to a corp endpoint.

Dependencies and integration: referenced by Evergreen performance tasks after perf JSON is generated. Requires Evergreen expansions such as `project_id`, `version_id`, `build_variant`, `task_name`, `task_id`, `execution`, `revision_order_id`, and `perf_file_path`.

Risks and test signals: unquoted `@${perf_file_path}` and URL variables require sane values. Only HTTP 200 is accepted. Network or service outages fail the task. The script assumes patch revision order IDs append username after underscores.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/evergreen/perf_submission.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/evergreen/print_stack_trace.py -->
# sources/storage-engines/wiredtiger/test/evergreen/print_stack_trace.py

Purpose: finds core dumps and prints/saves debugger stack traces for Evergreen diagnostics.

Important APIs: `border_msg()` formats section headers. `LLDBDumper` and `GDBDumper` locate debuggers and run batch commands. GDB supports optional shared-library search path and writes all-thread backtraces to `<core-base>.stacktrace.txt` after printing a shorter trace to stdout.

Control flow: `main()` parses core and library paths, ensures `~/.gdbinit` contains `/data/mci` auto-load safe path, recursively finds files matching `dump.*core`, uses `file` output to extract `execfn`, adjusts executable path for non-Python cores when needed, then dispatches to GDB on Linux. macOS/Windows branches are placeholders.

State and persistence: mutates `~/.gdbinit` and writes stacktrace text files in the current directory. Reads core files only.

Dependencies and integration: Evergreen post task `dump stacktraces`. Depends on `file`, `gdb` or `lldb`, core files preserving `execfn`, and debug symbols/library paths.

Risks and test signals: `file` output parsing is regex/string based. If `execfn` is missing, the core is skipped. GDB absence exits the script. Output file handles are opened without explicit close but process exit closes them.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/evergreen/print_stack_trace.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/evergreen/python_version_check.py -->
# sources/storage-engines/wiredtiger/test/evergreen/python_version_check.py

Purpose: verifies that the Python interpreter running a script matches the Python interpreter configured in CMake.

Important APIs: `get_python_version_string(python_path)` runs `<python> --version` and returns the stripped output.

Control flow: `main()` parses optional CMake cache path, search string, and verbose flag. It records `sys.executable` and version. If cache/search are provided, it scans the cache for the first matching line, reconstructs the path from the first slash onward, gets that interpreter's version, prints details in verbose mode, and exits success only when versions match.

State and persistence: reads `CMakeCache.txt`; writes only stdout/stderr.

Dependencies and integration: invoked by Evergreen after configure to ensure Python CMake selection matches task Python. Depends on CMake cache line format containing an absolute path with `/`.

Risks and test signals: if cache/search args are missing, `cmake_python_version` remains `None`, causing a mismatch and exit. Path extraction is Unix-centric. It compares full `Python X.Y.Z` strings, so patch-level differences fail even when ABI compatibility might be acceptable.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/evergreen/python_version_check.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/evergreen/recovery_stress_test_script.sh -->
# sources/storage-engines/wiredtiger/test/evergreen/recovery_stress_test_script.sh

Purpose: repeatedly runs recovery/abort stress tests across several transaction/logging modes.

Control flow: accepts `times` and optional truncated-log args. Each iteration alternates `test_timestamp_abort -s` timing stress on even iterations, then runs `test_random_abort` and `test_timestamp_abort` in current write-no-sync mode, memory-based txn mode (`-m`), V1 log compatibility (`-C`), and V1 plus memory mode. It also runs `test_truncated_log` with provided args and sleeps ten seconds between iterations.

State and persistence: test binaries create their own homes/logs in the current build tree. The wrapper does not clean state directly.

Dependencies and integration: Evergreen recovery stress tasks run this from a csuite build context containing `random_abort`, `timestamp_abort`, and `truncated_log` subdirectories.

Risks and test signals: strict argument range but usage text references the wrong script name. `set -o errexit` makes the first failing command terminate the wrapper. Optional args are stored as a single variable, so complex quoting is limited.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/evergreen/recovery_stress_test_script.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/evergreen/run_format_configs.sh -->
# sources/storage-engines/wiredtiger/test/evergreen/run_format_configs.sh

Purpose: reruns known failing `test/format` configurations from `test/format/failure_configs` in parallel to catch regressions and recover aborted tests.

Important functions: `wait_for_process()` polls PIDs, removes completed PIDs from the list, waits to get exit status, maps PID to config via `format_list.txt`, optionally runs recovery (`./t -Rqv`) when the log contains `aborting to test recovery`, prints prefixed logs, removes successful outputs, and records success/failure counts.

Control flow: moves to repo root then `cmake_build/test/format`, validates `t`, parses `-j`, starts `./t -1 -c <config> -h WT_TEST_<config>` jobs up to `parallel_jobs`, then drains. Exits nonzero if any config failed.

State and persistence: writes `format_list.txt`, per-config logs and WT_TEST directories; removes successful outputs and keeps failed CONFIG/logs for diagnostics.

Dependencies and integration: Evergreen format failure-config task. Requires built `t` and failure config files.

Risks and test signals: polling with `ps` and manual PID arrays is race-prone. The script references `fatal_msg` for invalid `-j` but does not define it. Recovery path copies potentially large directories. Logs are always printed for completed configs.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/evergreen/run_format_configs.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/evergreen/run_model_workloads.sh -->
# sources/storage-engines/wiredtiger/test/evergreen/run_model_workloads.sh

Purpose: runs all model workload files through the model test tool in replay mode.

Control flow: changes to `cmake_build/test/model/tools`, validates `model_test`, iterates sorted `*.workload` files under `test/model/workloads`, skips workload `WT-12539` due to a tracked prepare-conflict issue, and runs `./model_test -R -h WT_TEST_<basename> -w <workload>`. It counts successes and failures, prints a summary, and exits nonzero if any workload failed.

State and persistence: creates per-workload `WT_TEST_*` homes in the model tools directory. It does not clean them.

Dependencies and integration: Evergreen memory/model workload tasks. Requires built `model_test`, workload files, and repo layout relative to build dir.

Risks and test signals: uses `[ $RESULT == 0 ]`, relying on Bash. Any nonzero model_test result increments failure but does not stop the loop, providing full workload coverage. The hard-coded skip should be revisited when WT-13232 is resolved.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/evergreen/run_model_workloads.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/evergreen/schema_abort_predictable.sh -->
# sources/storage-engines/wiredtiger/test/evergreen/schema_abort_predictable.sh

Purpose: validates predictable replay for `test_schema_abort`, where concurrent schema operations are replayed to a calibrated operation count and compared.

Control flow: must run from `build/test/csuite/schema_abort`, accepts `times`, sets runtime 20 seconds and 5 threads, performs a calibration run into `RUNDIR_0`, reads stable timestamp from `RUNDIR_0/WT_HOME`, and treats that as operation count. For each iteration it runs two predictable homes with the same data seed, different extra seeds, and a slightly randomized operation limit, then compares `WT_HOME` directories with `wt_cmp_dir`, ignoring `table:wt`.

State and persistence: recreates `RUNDIR_0/1/2`; retains failing directories. Uses generated seeds and operation counts.

Dependencies and integration: Evergreen schema abort predictable task. Requires `test_schema_abort`, `tools/wt_timestamps`, and `tools/wt_cmp_dir`.

Risks and test signals: ignores `table:wt` because that table can be concurrently created/opened/verified/dropped and does not participate in predictable replay. The optional usage text mentions an unused second arg. Failures are binary exit or directory mismatch.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/evergreen/schema_abort_predictable.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/evergreen/setup_spawn_host.sh -->
# sources/storage-engines/wiredtiger/test/evergreen/setup_spawn_host.sh

Purpose: prepares an Evergreen spawn host for debugging a WiredTiger task by unpacking artifacts, configuring debugger paths, installing/finding CMake, setting shell environment, and notifying the user.

Control flow: starts in `$HOME`, notifies logged-in users with `wall`, creates `/data/wiredtiger` and symlinks it, extracts the first non-compile artifact tarball, checks for cores, and if present reads old source path from `CMakeCache.txt` and appends GDB `solib-search-path`, `substitute-path`, pretty printing, and safe path settings. It sources `find_cmake.sh`, appends PATH/LD_LIBRARY_PATH to `~/.profile`, writes `.bash_profile` helpers, then uses Evergreen credentials and AWS instance metadata to send a Slack message with SSH command.

State and persistence: mutates home directory, `/data/wiredtiger`, shell profiles, and `~/.gdbinit`.

Dependencies and integration: spawn-host setup task. Depends on artifacts in `/data/mci`, toolchain path, AWS metadata service, Evergreen CLI, and user credentials.

Risks and test signals: many commands assume Linux/AWS. Existing `wiredtiger` symlink/directory handling is not defensive. Slack notification is best effort when user lookup exists; setup completion is also broadcast with `wall`.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/evergreen/setup_spawn_host.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/evergreen/tcmalloc_install_or_build.sh -->
# sources/storage-engines/wiredtiger/test/evergreen/tcmalloc_install_or_build.sh

Purpose: makes MongoDB's patched TCMalloc shared library available for preloading in Evergreen builds, preferring S3 prebuilt artifacts and building/uploading when missing.

Control flow: requires build variant, defines patched source tag `mongo-20240522`, reads S3 and AWS credential expansions, tries `aws s3 cp --quiet` for `tcmalloc-<tag>-<variant>.tgz`, and extracts on success. If the object is missing, it downloads bazelisk for current OS/arch, sets Bazel 7.5.0, downloads the patched tcmalloc source, writes a Bazel `cc_shared_library` BUILD file, builds `libtcmalloc.so`, packages it under `TCMALLOC_LIB`, uploads to S3, and exits using the local build.

State and persistence: writes bazelisk, tarballs, source dir, `TCMALLOC_LIB`, and S3 object.

Dependencies and integration: called by Evergreen configure when `ENABLE_TCMALLOC=1`; `PREPARE_TEST_ENV` later uses `LD_PRELOAD`.

Risks and test signals: AWS download exit code `1` is treated as expected missing artifact; other codes fail. Build path is unsupported on Windows. Upload failure fails the WT build even though a local library exists, intentionally surfacing cache problems.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/evergreen/tcmalloc_install_or_build.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/evergreen/tsan_warnings_analysis.py -->
# sources/storage-engines/wiredtiger/test/evergreen/tsan_warnings_analysis.py

Purpose: scans TSAN log files, deduplicates warnings by normalized summary, optionally filters to warnings touching recently modified lines, and fails the task when warnings remain.

Important APIs: `get_tsan_warnings()` recursively finds files whose names start with `tsan_logs`, records lines from `WARNING:` through `SUMMARY:`, normalizes summary paths by stripping up to `wiredtiger/` and removing column numbers, and maps summary to `(log_name, warning_lines)`. `get_line_last_modified_times(file_path, line_number)` runs `git blame --line-porcelain` and extracts `author-time`.

Control flow: `main()` parses optional timestamp. When provided, it keeps only warnings whose parsed data-race file/line blame time is at or after the filter timestamp, or warnings it cannot parse. It prints all remaining warning blocks and exits 1, otherwise prints no warnings.

State and persistence: reads TSAN logs and Git history; writes only stdout.

Dependencies and integration: Evergreen TSAN analysis task after sanitizer runs. Depends on TSAN `log_path` naming, summary format, and Git blame availability.

Risks and test signals: only summaries matching `data race (.*):(\d+)` are timestamp-filtered. Deduplication by summary can collapse separate occurrences. `exit(1)` is used in one helper instead of `sys.exit`. Non-data-race TSAN reports are retained when unparseable.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/evergreen/tsan_warnings_analysis.py -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/evergreen/verify_wt_datafiles.sh -->
# sources/storage-engines/wiredtiger/test/evergreen/verify_wt_datafiles.sh

Purpose: verifies and optionally dumps WiredTiger data files generated by `test/format`.

Control flow: accepts optional `-v`, moves to repo root then `cmake_build/test/format`, checks for `WT_TEST.[0-9]*` directories and `../../wt`, extends `LD_LIBRARY_PATH`, finds directories containing `WiredTiger.wt`, and for each directory runs `wt printlog` when logging is enabled, `wt list`, `wt verify <table>`, and `wt dump <table>` for every listed table. Verbose mode prints dump output; default discards it. It counts verified tables and exits 4 if none were found.

State and persistence: reads test directories and may produce stdout dump output; no writes except command side effects from opening homes.

Dependencies and integration: Evergreen post/follow-up validation for format runs. Requires `wt` binary and valid `CONFIG` files.

Risks and test signals: supported exit codes distinguish list, verify, dump, no-table, bad args, missing binary, and missing dirs. `set -e` plus explicit `$?` checks after commands can be redundant. Table names are iterated by whitespace, assuming simple names from `wt list`.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/evergreen/verify_wt_datafiles.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/evergreen_develop.yml -->
# sources/storage-engines/wiredtiger/test/evergreen_develop.yml

Purpose: Evergreen overlay for the WiredTiger develop project. It includes `test/evergreen.yml` and adds develop-only variants for performance, documentation, code statistics, compatibility, infrequent, and LazyFS testing.

Important structures: `perf-tasks-template` defines batchtime, common perf expansions such as TCMalloc, release build type, doubled CPU job count, database name, and a set of perf task selectors. Build variants instantiate this for Ubuntu x86 and Amazon ARM64. `documentation-update` runs weekly doc update tasks across maintained branches. `code-statistics` runs split coverage, coverage merge, catch2 coverage, cyclomatic complexity, code-change report, and modularity metrics. Compatibility, memory-model, and LazyFS variants configure their own task lists and expansions.

State and persistence: declarative YAML only; runtime state is produced by included tasks/functions.

Dependencies and integration: relies on anchors/tasks/functions from included `test/evergreen.yml` and on variant-specific distros. It activates coverage per-test only manually.

Risks and test signals: changes here affect scheduling and build-variant coverage rather than code behavior. Perf tasks use long batch times and disabled stepback for infrequent checks. Missing include anchors or renamed tasks in base Evergreen config will break validation.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/evergreen_develop.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/evergreen_disagg.yml -->
# sources/storage-engines/wiredtiger/test/evergreen_disagg.yml

Purpose: standalone Evergreen project config for WiredTiger disaggregated-storage stress tests marked failure-expected. It duplicates base Evergreen setup/build/artifact functions needed by the `wiredtiger-disagg` project.

Important structures: global `pre`, `post`, `timeout`, and `exec_timeout_secs` define cleanup, environment setup, stacktrace/stat/artifact upload, hang analysis, and cleanup. Functions cover project checkout, GitHub token for automation scripts, configure/build WiredTiger, artifact fetch/upload, disagg format tests, and timestamp-abort disagg tests. Variables define reusable task anchors for disagg switch/multi/multi-validation/delete-enabled variants, timestamp abort, built-in extension flags, and ASan clang flags.

Control flow: `compile` checks out and builds WiredTiger. Stress tasks depend on compile, fetch artifacts, prepare test environment with sanitizer/TCMalloc/extension settings, then run format or timestamp abort loops with disagg-specific args. Build variants schedule normal ARM64 stress with TCMalloc and ASan stress without TCMalloc.

State and persistence: declarative config controls artifact tarballs, S3 uploads, core files, stats, and WT test homes at runtime.

Dependencies and integration: relies on Evergreen expansions, AWS credentials, MongoDB toolchain, CMake presets, tcmalloc script, and WiredTiger disagg test flags.

Risks and test signals: duplicated base config can drift from `test/evergreen.yml`. Many tasks are explicitly failure-expected due to open WT tickets. Sanitizer and TCMalloc are mutually guarded. Post functions preserve diagnostics even on failure.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/evergreen_disagg.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/fops/CMakeLists.txt -->
# sources/storage-engines/wiredtiger/test/fops/CMakeLists.txt

Purpose: builds and registers the `test_fops` file-operation stress executable.

Build contract: `create_test_executable(test_fops SOURCES fops_file.c fops.c t.c)` compiles the three source files into a test binary using the repository's test CMake helper. On Windows, CTest invokes it through `powershell.exe $<TARGET_FILE:test_fops>` because this test has issues running under a normal ctest process, possibly due to resource constraints. Other platforms run `test_fops` directly.

State and persistence: declarative CMake only. Runtime state is created by the executable in its WiredTiger home.

Dependencies and integration: part of the CMake test tree and included in `ctest check`. It depends on shared test utility infrastructure supplied by `create_test_executable`.

Risks and test signals: labels are `check;sanitizer_long`, so it runs in smoke/check lanes and is recognized as long under sanitizers. Changes to source list or invocation affect platform behavior. The Windows special process wrapper is an important integration detail and should not be removed without retesting.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/fops/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/fops/fops.c -->
# sources/storage-engines/wiredtiger/test/fops/fops.c

Purpose: thread driver for the fops stress test. It spawns worker threads that randomly execute WiredTiger file operations and reports per-thread operation counts and throughput.

Important types/functions: local `STATS` records counts for bulk, unique bulk, checkpoint, create, unique create, cursor, drop, and verify operations. `fop_start(nthreads)` allocates `run_stats` and thread IDs, starts workers with `__wt_thread_create`, joins them, computes elapsed seconds, prints stats and ops/sec, and frees memory. `fop(void *arg)` initializes a random state and runs `nops` iterations, randomly choosing among object operation functions. `print_stats()` aggregates unique/non-unique bulk and create counts in output.

State and persistence: `run_stats` is process-global for the run. Worker operations mutate the WiredTiger home via functions in `fops_file.c`.

Dependencies and integration: includes `thread.h`, using global `nops`, operation prototypes, WiredTiger thread helpers, random helpers, and test allocation/check helpers.

Risks and test signals: switch uses `% 9` but has cases 0-7, so one random value performs no operation while still consuming an iteration. Operation failures are handled in callee functions. Throughput division assumes nonzero elapsed time.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/fops/fops.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/fops/fops_file.c -->
# sources/storage-engines/wiredtiger/test/fops/fops_file.c

Purpose: implements the individual WiredTiger operations used by the fops concurrency stress test.

Important APIs: `obj_bulk()`, `obj_bulk_unique(force)`, `obj_cursor()`, `obj_create()`, `obj_create_unique(force)`, `obj_drop(force)`, `obj_checkpoint()`, and `obj_verify()` each open a session, optionally wrap operations in a user transaction, and tolerate expected races such as `EEXIST`, `ENOENT`, `EBUSY`, and selected `EINVAL` results. Unique object functions use a global `uid` protected by `single` rwlock to create names like `<uri>.<uid>`.

Control flow: operations intentionally race on a shared `uri` or short-lived unique URIs. Bulk functions create/open bulk cursors and close them; unique variants drop the object afterward, retrying `EBUSY`. Drop rolls back transactions when expected race errors occurred. Forced checkpoint tolerates busy/missing object races.

State and persistence: creates, drops, verifies, and checkpoints WiredTiger objects in the current test home. Unique object state is transient; shared object may appear/disappear concurrently.

Dependencies and integration: uses globals and prototypes from `thread.h`, WiredTiger session/cursor APIs, pthread lock, and test utility checks.

Risks and test signals: the test intentionally accepts a narrow set of race errors; any other return is fatal. A format string in `obj_bulk_unique` passes `"new_uri"` instead of the variable, weakening diagnostics. Transactions can fail with `EINVAL` under concurrent metadata races and are tolerated in defined places.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/fops/fops_file.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/fops/t.c -->
# sources/storage-engines/wiredtiger/test/fops/t.c

Purpose: main program for the fops test. It configures a WiredTiger home, runs file-operation stress over both file and table URIs, and handles cleanup/logging.

Important globals/functions: defines `use_txn`, `conn`, `single`, `nops`, `uri`, `config`, `logfp`, and `home`. `main()` parses `-C`, `-h`, `-l`, `-n`, `-r`, `-t`, and `-x`, initializes defaults, creates a work dir path, installs SIGINT handler, then for each run and each configured URI calls `shutdown()`, `wt_startup()`, `fop_start()`, and `wt_shutdown()`. `wt_startup()` recreates the home and opens WiredTiger with small cache, statistics, and statistics log. Event handlers suppress expected missing-file/bulk/forced-checkpoint messages.

State and persistence: creates/removes the test home each run, writes optional log file, and emits statistics logs on close via WiredTiger config.

Dependencies and integration: works with `fops.c` and `fops_file.c`; uses WiredTiger public API, internal test helpers, signal handling, and pthread rwlock.

Risks and test signals: `shutdown()` removes the home before every URI, so file/table runs are isolated. Infinite runs are possible with `-r 0`. Signal cleanup removes the home, which can erase failure evidence on interrupt. Expected error filtering must stay aligned with fops race behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/fops/t.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/fops/thread.h -->
# sources/storage-engines/wiredtiger/test/fops/thread.h

Purpose: shared header for the fops test sources, declaring globals and operation entry points.

Important declarations: includes `test_util.h` and `<signal.h>`. Extern globals include `use_txn`, `WT_CONNECTION *conn`, `nops`, `uri`, `config`, and `pthread_rwlock_t single`. Function prototypes cover `fop_start()` and every object operation implemented by `fops_file.c`.

State contract: this header centralizes process-wide mutable state owned by `t.c` and consumed by worker/operation modules. `single` protects unique URI id generation, while `conn` is the shared WiredTiger connection used by all worker sessions.

Dependencies and integration: included by all fops C files. It exposes WiredTiger and pthread/test utility types needed across modules.

Risks and test signals: broad extern global state keeps the test simple but tightly couples all translation units. Any change to transaction behavior, object config, or URI selection in `t.c` immediately affects all operation functions. Missing prototypes here would hide integration errors between the worker dispatcher and operation implementations.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/fops/thread.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/format/CMakeLists.txt -->
# sources/storage-engines/wiredtiger/test/format/CMakeLists.txt

Purpose: builds the main `test/format` executable `t` and registers its smoke test.

Build contract: `format_sources` lists the full set of C modules implementing format behavior: operations, config, timestamps, replay, backup, compaction, history store, disaggregated support, salvage, verification, and utility modules. `create_test_executable(test_format ... EXECUTABLE_NAME "t" ADDITIONAL_FILES ...)` builds the binary and arranges key config/scripts as additional files. The target uses C++ linker language because sanitizer runtimes and some extension dependencies require C++ linkage. `EXT_LIBPATH` is compiled as an empty string, and `wiredtiger_ext` is an explicit dependency so dlopen-loaded extension modules are built.

State and persistence: declarative CMake; runtime smoke test creates format WT homes through `smoke.sh`.

Dependencies and integration: CTest registers `test_format` as `${CMAKE_CURRENT_BINARY_DIR}/smoke.sh` with `check` label. Depends on repository CMake helper macros and extension target.

Risks and test signals: missing source entries can silently drop format features from the executable. Removing C++ linker selection can break sanitized builds. The extension dependency is needed because runtime loading is invisible to the linker.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/format/CMakeLists.txt -->
