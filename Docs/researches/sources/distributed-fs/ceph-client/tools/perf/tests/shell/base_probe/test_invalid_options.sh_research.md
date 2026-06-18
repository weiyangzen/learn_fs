<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/base_probe/test_invalid_options.sh -->
# sources/distributed-fs/ceph-client/tools/perf/tests/shell/base_probe/test_invalid_options.sh

## Purpose

This perf-probe test checks diagnostics for missing arguments, optional argument handling, and mutually exclusive option combinations.

## Research

After common initialization and kprobe availability checks, the script records a hint if DWARF support is missing. It loops over `-a`, `-d`, `-L`, and `-V` expecting “requires a value” errors. It then tests `-F` and `-l` without explicit arguments, expecting no stderr. Finally it enumerates incompatible option pairs among add/delete/line/vars/list/functions modes and requires an “cannot be used with” diagnostic for each. State is log files under `LOGS_DIR`, including an aggregate mutually-exclusive error log. Dependencies are perf probe option parsing and shared pattern checkers. Integration targets CLI error handling rather than kernel probe state. Risks include help/error wording changes and one apparent loop bug that always runs `perf probe -F` while naming both `-F` and `-l`. Test signal is successful rejection or acceptance with expected diagnostics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/base_probe/test_invalid_options.sh -->
