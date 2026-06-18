<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/common/check_all_lines_matched.pl -->
# sources/distributed-fs/ceph-client/tools/perf/tests/shell/common/check_all_lines_matched.pl

## Purpose

This Perl helper validates that every input line matches at least one supplied regular expression.

## Research

The script stores command-line regexes, sets quiet mode unless `TESTLOG_VERBOSITY >= 2`, and caps diagnostics with `TESTLOG_ERR_MSG_MAX_LINES` defaulting to 20. It reads stdin line by line, strips newline, tests all regexes, prints unmatched lines when verbose, marks failure, and exits with nonzero if any line did not match. State is local counters and no persistent files. Dependencies are Perl regex semantics and environment variables set by the shell test framework. Integration is broad across base probe/report tests where unexpected output should fail even when required patterns are present. Risks include regex portability, unanchored patterns accepting too much, and quiet default hiding useful failure context. Test signal for callers is exit code 0 only when every line is whitelisted.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/common/check_all_lines_matched.pl -->
