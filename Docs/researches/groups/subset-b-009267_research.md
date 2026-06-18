# subset-b-009267 research

Grouped research report for kdevops nfstest result visualization scripts and pynfs workflow configuration/baseline artifacts. Each section preserves the exact source path and is wrapped for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/workflows/nfstest/scripts/parse_nfstest_results.py -->
# sources/test-tools/kdevops/workflows/nfstest/scripts/parse_nfstest_results.py

## Purpose
Parses kdevops nfstest `.log` output into a normalized JSON result document. The script discovers logs under a results directory, infers suite names, extracts per-test status/assertion/timing information, aggregates suite and overall totals, prints the JSON to stdout, and persists `parsed_results.json` beside the source logs.

## Important APIs, Types, and Functions
The script is a CLI-oriented Python module. `parse_timestamp(timestamp_str)` converts `HH:MM:SS.fraction` strings to seconds, but is currently unused. `parse_test_log(log_path)` is the primary single-file parser and returns a dictionary with `file`, `test_suite`, `tests`, `summary`, `configuration`, and `test_groups`. `parse_all_results(results_dir)` recursively finds `**/*.log`, calls `parse_test_log`, groups outputs by suite key, and builds `overall_summary`. `main()` selects a results directory from argv or `workflows/nfstest/results/last-run`, validates that it exists, emits JSON, and writes `parsed_results.json`.

## Control Flow
`main()` performs input validation, then delegates to `parse_all_results`. `parse_all_results` uses `glob.glob(..., recursive=True)` and sorted iteration for deterministic ordering, chooses a suite key from path segments such as `/interop/` or from the parser's filename inference, appends suite results, and increments aggregate counts/time. `parse_test_log` reads the whole log into memory, scans line by line, builds a `current_test` when it sees `*** `, fills in the name from `TEST: Running test`, records `PASS:` and `FAIL:` assertions, finalizes the test only on a `TIME:` line, parses summary lines matching `N tests (P passed, F failed`, and parses `Total time:` strings in seconds or `XmYs` form.

## State and Persistence Behavior
Parser state is in-memory until `main()` writes `parsed_results.json` to the selected results directory. The emitted JSON contains a generation timestamp from `datetime.now().isoformat()`, so repeated runs are not byte-for-byte stable. `test_groups` is a `defaultdict(list)` while parsing; the standard JSON encoder serializes it as a normal object. Existing `parsed_results.json` is overwritten without backup.

## Dependencies and Integration Points
Depends only on Python standard library modules: `os`, `re`, `sys`, `json`, `glob`, `datetime`, `pathlib`, and `collections.defaultdict`; `Path` is imported but unused. It is invoked by `visualize_nfstest_results.sh` and produces the data expected by downstream visualization tooling, especially `generate_nfstest_html.py` in the same script directory. It assumes nfstest log phrasing such as `OPTS:`, `***`, `TEST: Running test`, `PASS:`, `FAIL:`, `TIME:`, final test summaries, and `Total time:`.

## Risks
Tests without a trailing `TIME:` line are never appended, even if they have pass/fail assertions. A test with multiple assertions is reduced to one final `status`, so mixed pass/fail lines become whatever was seen last before timing. The `TIME:` unit regex `([\d.]+)([ms]?)` cannot distinguish `ms` because the optional group captures one character; millisecond values written as `123ms` are likely parsed as minutes due to the `m` branch. Suite detection uses substring/path checks and can misclassify paths containing suite names incidentally. Configuration parsing only handles narrow `OPTS:` shapes. Files are opened without an explicit encoding or error handling, so malformed logs abort the whole run.

## Test Signals
Useful checks are fixture-driven parser tests for each log suite, logs with missing `TIME:`, failure-only tests, millisecond timing, `Total time` variants, and option lines. Integration tests should run the CLI on a temporary results tree and assert stdout JSON plus `parsed_results.json` contents. The current file has no embedded tests; success is signaled by `visualize_nfstest_results.sh` completing and by downstream HTML generation consuming the JSON.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/workflows/nfstest/scripts/parse_nfstest_results.py -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/workflows/nfstest/scripts/visualize_nfstest_results.sh -->
# sources/test-tools/kdevops/workflows/nfstest/scripts/visualize_nfstest_results.sh

## Purpose
Shell wrapper that turns existing nfstest run logs into an HTML visualization. It validates the result directory, calls the Python parser, calls the HTML generator, and reports the generated output location.

## Important APIs, Types, and Functions
This is a Bash CLI script rather than a library. Important variables are `SCRIPT_DIR`, resolved from `readlink -f "$0"`; `KDEVOPS_DIR`, resolved from `git rev-parse --show-toplevel` with `pwd` fallback; `RESULTS_DIR`, defaulting to `$KDEVOPS_DIR/workflows/nfstest/results/last-run` unless argv[1] is supplied; and `HTML_OUTPUT_DIR`, fixed at `$KDEVOPS_DIR/workflows/nfstest/results/html`.

## Control Flow
The script exits early if `RESULTS_DIR` does not exist or contains no `*.log` files. It then runs `python3 "$SCRIPT_DIR/parse_nfstest_results.py" "$RESULTS_DIR"` and treats a nonzero exit as fatal. Next it runs `python3 "$SCRIPT_DIR/generate_nfstest_html.py" "$RESULTS_DIR"` and prints a warning, not a fatal error, on nonzero status. Final success requires `$HTML_OUTPUT_DIR/index.html`; if present, the script prints open/scp hints and lists generated files, otherwise it exits with an error.

## State and Persistence Behavior
The wrapper itself keeps no durable state. Its child parser writes `parsed_results.json` under the result directory, and the HTML generator is expected to write under `workflows/nfstest/results/html`. Existing parsed JSON or HTML files may be overwritten by those child scripts. Output paths are global to the workflow rather than per-kernel or per-run, so repeated visualizations can replace prior HTML.

## Dependencies and Integration Points
Requires Bash, `readlink -f`, Git if repository-root discovery should work, `find`, `wc`, `python3`, `ls`, `parse_nfstest_results.py`, and `generate_nfstest_html.py`. The user-facing error text points to `make nfstest-baseline` and `make nfstest-dev`, so it is integrated with the kdevops nfstest Make targets and expected results layout.

## Risks
There is no `set -euo pipefail`, so only explicitly checked commands affect control flow. `LOG_COUNT=$(find ... | wc -l)` includes whitespace from `wc`, which is accepted by numeric `[` in typical shells but is still a brittle pattern. HTML generation can fail but still be considered acceptable until the final `index.html` check, which may pass with stale HTML if a previous run left the file in place. `SCRIPT_DIR` relies on GNU-compatible `readlink -f`. The fixed `HTML_OUTPUT_DIR` ignores a custom result directory, which may surprise users visualizing non-default runs.

## Test Signals
Shell tests should cover missing results directory, empty results directory, parser failure, HTML generator failure with no stale index, custom `RESULTS_DIR`, and operation outside a Git checkout. A practical smoke test is to create a temporary result tree with one `.log`, run the wrapper, and verify `parsed_results.json` plus `workflows/nfstest/results/html/index.html`.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/workflows/nfstest/scripts/visualize_nfstest_results.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/workflows/pynfs/Kconfig -->
# sources/test-tools/kdevops/workflows/pynfs/Kconfig

## Purpose
Defines Kconfig options for the kdevops pynfs workflow when `KDEVOPS_WORKFLOW_ENABLE_PYNFS` is enabled. The symbols control where pynfs source is cloned from, what revision is checked out, and whether pNFS block-layout tests are added.

## Important APIs, Types, and Functions
The important symbols are `HAVE_MIRROR_PYNFS`, `PYNFS_REPO_CUSTOM`, `PYNFS_REPO_URL`, `PYNFS_GIT`, `PYNFS_GIT_TAG`, and `PYNFS_PNFS_BLOCK`. `HAVE_MIRROR_PYNFS` is an internal boolean that depends on `USE_LIBVIRT_MIRROR` and shells out to `scripts/check_mirror_present.sh /mirror/pynfs.git`. `PYNFS_GIT` is the derived repository URL used by the Make/Ansible layer; it defaults to `DEFAULT_PYNFS_GIT_URL`, a custom URL, or a guestfs mirror URL built by `scripts/append-makefile-vars.sh`.

## Control Flow
All options are scoped inside `if KDEVOPS_WORKFLOW_ENABLE_PYNFS`. If the user does not select `PYNFS_REPO_CUSTOM` and no mirror is available, `PYNFS_GIT` uses `DEFAULT_PYNFS_GIT_URL`. If `PYNFS_REPO_CUSTOM` is selected, `PYNFS_REPO_URL` becomes visible and feeds `PYNFS_GIT`. If a libvirt mirror is available and `GUESTFS` is enabled, `PYNFS_GIT` is rewritten to the guestfs bridge mirror URL. `PYNFS_GIT_TAG` defaults to `master`; `PYNFS_PNFS_BLOCK` is an independent optional boolean.

## State and Persistence Behavior
The file contributes symbols to kdevops generated configuration, which later appears as `CONFIG_PYNFS_GIT`, `CONFIG_PYNFS_GIT_TAG`, and `CONFIG_PYNFS_PNFS_BLOCK` for Make and as extra-vars for Ansible. It does not persist runtime test results itself. The shell-backed mirror default is evaluated during configuration generation and depends on the host/mirror state at that time.

## Dependencies and Integration Points
Depends on global kdevops symbols such as `KDEVOPS_WORKFLOW_ENABLE_PYNFS`, `USE_LIBVIRT_MIRROR`, `GUESTFS`, `DEFAULT_PYNFS_GIT_URL`, and `KDEVOPS_DEFAULT_BRIDGE_IP_GUESTFS`. Integrates with `workflows/pynfs/Makefile`, which strips quotes from the generated config and passes `pynfs_git`, `pynfs_git_tag`, and optionally `pynfs_pnfs_block` into `WORKFLOW_ARGS`.

## Risks
If neither `DEFAULT_PYNFS_GIT_URL` nor a selected custom URL is valid, `PYNFS_GIT` can be empty or unusable downstream. The mirror default only applies in the `HAVE_MIRROR_PYNFS && GUESTFS` case, so mirror behavior changes with virtualization mode. `PYNFS_REPO_URL` has no default or validation beyond Kconfig typing. The pNFS block option only controls argument emission; the actual test availability depends on the pynfs checkout and server environment.

## Test Signals
Configuration tests should evaluate default, custom repo, mirror-present, and pNFS-block combinations and assert the generated `CONFIG_PYNFS_*` values. A dry-run Make test can then confirm that `workflows/pynfs/Makefile` emits the expected Ansible extra vars.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/workflows/pynfs/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/workflows/pynfs/Makefile -->
# sources/test-tools/kdevops/workflows/pynfs/Makefile

## Purpose
Provides the kdevops Make target layer for the pynfs workflow. It maps Kconfig values into Ansible extra variables, defines targets to install/run/reset pynfs on baseline or dev hosts, displays JSON results, and launches HTML visualization.

## Important APIs, Types, and Functions
Important variables are `PYNFS_GIT`, `PYNFS_GIT_TAG`, `PYNFS_ARGS`, `WORKFLOW_ARGS`, `LAST_KERNEL`, `FIND_PATH`, `PATTERN`, and `XARGS_ARGS`. Important targets are `pynfs`, `pynfs-baseline`, `pynfs-dev-baseline`, `pynfs-dev-reset`, `pynfs-show-results`, `pynfs-visualize`, and `pynfs-help-menu`. The file appends `pynfs-help-menu` to `HELP_TARGETS`.

## Control Flow
At parse time, the Makefile strips quotes from `CONFIG_PYNFS_GIT` and `CONFIG_PYNFS_GIT_TAG`, appends them as `pynfs_git=` and `pynfs_git_tag=`, optionally adds `pynfs_pnfs_block='True'`, and appends the result to global `WORKFLOW_ARGS`. `LAST_KERNEL` is read from `workflows/pynfs/results/last-kernel.txt` if present, otherwise the newest non-`last-run` results directory is selected. `FIND_PATH` uses `last-run` when `LAST_KERNEL` matches the last-kernel file, otherwise a kernel-specific results directory. The run targets call `ansible-playbook` with host limits and tags against `$(KDEVOPS_PLAYBOOKS_DIR)/pynfs.yml`; visualization calls `scripts/workflows/pynfs/visualize_results.py`.

## State and Persistence Behavior
Persistent workflow state is outside the Makefile: Ansible modifies baseline/dev hosts, result JSON is collected under `workflows/pynfs/results/`, `last-kernel.txt` selects the most recent run, and `pynfs-visualize` writes `workflows/pynfs/results/$(LAST_KERNEL)/html/index.html`. `pynfs-show-results` reads JSON result files and streams their contents. Make variables can be overridden by the caller, notably `LAST_KERNEL`, `PATTERN`, and `XARGS_ARGS`.

## Dependencies and Integration Points
Requires kdevops global Make variables such as `Q`, `KDEVOPS_PLAYBOOKS_DIR`, and generated `CONFIG_PYNFS_*` symbols. Runtime dependencies include `ansible-playbook`, `extra_vars.yaml`, `find`, `xargs`, `sed`, `grep`, `ls`, and `python3`. It integrates directly with the `pynfs.yml` playbook and with the checked-in baseline JSON files consumed by result comparison/visualization.

## Risks
`LAST_KERNEL` discovery can become empty if no result directories exist, which makes downstream paths ambiguous. `pynfs-visualize` checks only the kernel-specific directory and will not visualize `last-run` directly unless the `LAST_KERNEL` mapping resolves to a real directory. `pynfs-show-results` allows caller-provided `PATTERN` and `XARGS_ARGS`, which is flexible but can execute arbitrary shell fragments. The visualization success line contains a Unicode check mark, unlike most ASCII-only Make output. The baseline and dev targets duplicate the two-playbook sequence, so tag changes must be kept in sync.

## Test Signals
Use `make -n pynfs`, `make -n pynfs-baseline`, `make -n pynfs-dev-baseline`, and `make -n pynfs-visualize LAST_KERNEL=<fixture>` to verify playbook paths, limits, tags, and extra vars. Fixture tests for `pynfs-show-results` should cover `last-kernel.txt`, newest-directory fallback, custom `PATTERN`, and missing result directories.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/workflows/pynfs/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/workflows/pynfs/baseline/6.2.0-rc7+-v4.0.json -->
# sources/test-tools/kdevops/workflows/pynfs/baseline/6.2.0-rc7+-v4.0.json

## Purpose
Checked-in pynfs NFSv4.0 baseline result for kernel `6.2.0-rc7+`. It provides a stable comparison artifact for workflow result display, visualization, or regression detection against future pynfs runs.

## Important APIs, Types, and Data Shape
The file is a JSON object with aggregate keys `errors`, `failures`, `name`, `skipped`, `testcase`, `tests`, `time`, and `timestamp`. `testcase` is an array of 679 objects. Each testcase has `classname`, `code`, `name`, `time`, and optional `skipped: 1` or optional `failure` object containing `err` traceback text and a concise `message`. The top-level `tests` field is the numeric count `679`, not an array.

## Control Flow
There is no executable control flow, but consumers should treat the file as a JUnit-like result summary: read aggregate counts, iterate `testcase`, count entries with `skipped`, count entries with `failure`, and compare failure messages/codes with current run output. For this baseline, 184 cases are skipped, 4 cases fail, and 491 cases pass. The total recorded runtime is `1774.627598285675` seconds with timestamp `2023-02-14 17:26:51.244161`.

## State and Persistence Behavior
This is persisted fixture state in the source tree. It captures one historical run and should remain stable unless the intended baseline changes. Because `time` values are stored as strings per testcase and as a number at the top level, consumers should normalize types before numeric analysis. The failure tracebacks include absolute paths under `/data/pynfs/nfs4.0/...`, which are historical evidence rather than paths expected to exist in this repository.

## Dependencies and Integration Points
Integrated with the kdevops pynfs workflow and result tooling that reads JSON from `workflows/pynfs/results` or baseline directories. It aligns with `workflows/pynfs/Makefile` targets such as `pynfs-show-results` and `pynfs-visualize`. The `classname` values identify pynfs server test modules, including access, close, commit, create, delegation, lock, lookup, open, read/write, rename, setattr, and verification coverage.

## Risks
The baseline encodes environment-specific expected failures: `SATT18` gets `NFS4ERR_PERM`, `LOOKCHAR` and `LOOKBLK` get `NFS4ERR_NOENT`, and `LOCK24` gets `NFS4ERR_BAD_SEQID`. Treating all four as acceptable forever could hide real regressions if the server or test setup changes. Many skipped cases involve optional features or special file types; a reduced skipped count can be improvement or environment drift. Long-running tests dominate total time, especially `WRT15`, `RENEW3`, `CLOSE8`, `CLOSE9`, replay wait tests, and lock timeout tests, so timing comparisons should avoid overreacting to timeout-sensitive cases.

## Test Signals
Validation should assert that aggregate counts match derived counts from `testcase`: 679 total, 184 skipped, 4 failed, 491 passed, 0 errors, and summed non-skipped testcase time equal to the top-level `time`. Regression tooling should report failure code/message deltas, skipped-count deltas by `classname`, and large timing deltas for timeout-heavy cases.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/workflows/pynfs/baseline/6.2.0-rc7+-v4.0.json -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/workflows/pynfs/baseline/6.2.0-rc7+-v4.1.json -->
# sources/test-tools/kdevops/workflows/pynfs/baseline/6.2.0-rc7+-v4.1.json

## Purpose
Checked-in pynfs NFSv4.1 baseline result for kernel `6.2.0-rc7+`. It acts as the comparison fixture for v4.1 pynfs result visualization and regression analysis.

## Important APIs, Types, and Data Shape
The file is a JSON object with aggregate keys `errors`, `failures`, `name`, `skipped`, `testcase`, `tests`, `time`, and `timestamp`. `testcase` is an array of 262 objects. Each testcase carries `classname`, `code`, `name`, and string-valued `time`, plus optional `skipped: 1` or optional `failure` with traceback `err` and concise `message`. The top-level `tests` key is the numeric count `262`.

## Control Flow
This file has no executable flow; consumers iterate the `testcase` array and compare it against new run results. For this baseline, 91 cases are skipped, 10 fail, and 161 pass. The total runtime is `546.335152387619` seconds with timestamp `2023-02-14 17:36:00.064287`. Failures cluster around char/block special-file handling in `st_putfh`, `st_rename`, and `st_lookupp`.

## State and Persistence Behavior
This is durable source-tree fixture data. It preserves historical absolute traceback paths under `/data/pynfs/nfs4.1/...` and environment-specific behavior for optional file types and pNFS-related suites. Per-test times are strings while aggregate `time` is numeric, so parsers need explicit numeric conversion for timing comparisons.

## Dependencies and Integration Points
Used by kdevops pynfs reporting and visualization flows alongside the v4.0 baseline. It corresponds to NFSv4.1 server test modules such as courtesy locks, xattrs, flex files, sessions, exchange IDs, rename, putfh, lookupp, sequence, trunking, and pNFS-related classes. `workflows/pynfs/Makefile` can display JSON result files and run visualization against collected result directories using the same schema.

## Risks
The baseline's 10 failures are all special-file related and may reflect test environment permissions or export contents rather than generic NFSv4.1 protocol failures. The high skipped count includes whole feature families such as flex, xattr, block, reboot, and delegation; skip deltas must be interpreted with feature configuration context. Several courtesy and exchange-id tests intentionally run around 100 seconds, so total runtime is sensitive to timeout policy and server lease settings. Any consumer that assumes `tests` is an array will fail on this schema.

## Test Signals
Validation should assert aggregate consistency: 262 total testcases, 91 skipped, 10 failed, 161 passed, 0 errors, and summed non-skipped testcase time equal to top-level `time`. Regression reports should highlight the known failing codes `PUTFH1c`, `PUTFH1b`, `RNM1c`, `RNM1b`, `RNM2c`, `RNM2b`, `RNM3c`, `RNM3b`, `LKPP1c`, and `LKPP1b`, plus skipped-count changes by `classname` and timing changes in courtesy/session lease tests.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/workflows/pynfs/baseline/6.2.0-rc7+-v4.1.json -->
