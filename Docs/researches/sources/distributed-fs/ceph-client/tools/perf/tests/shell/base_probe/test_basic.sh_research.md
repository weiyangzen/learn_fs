<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/base_probe/test_basic.sh -->
# sources/distributed-fs/ceph-client/tools/perf/tests/shell/base_probe/test_basic.sh

## Purpose

This perf-probe smoke test validates basic command availability, help/usage text, and quiet-mode behavior.

## Research

The script sources common init, skips if kprobes are unavailable, optionally checks `perf probe --help` for expected manual sections and options when `PARAM_GENERAL_HELP_TEXT_CHECK=y`, always checks invoking `perf probe` without arguments for usage text, and verifies `--quiet --add vfs_read` plus `--quiet --del vfs_read` produce no stdout/stderr. State includes logs in `LOGS_DIR` and temporary kernel probe mutations for the quiet test. Dependencies are debugfs tracing, shared regex checkers, and optional man/help generation. Integration ensures user-facing command option text and output suppression remain stable. Risks include clearing/leaking probes if quiet add/delete fails, help text wording changes, and root/debugfs requirements. Passing signals are regex matches for help/usage and zero log lines under quiet mode.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/base_probe/test_basic.sh -->
