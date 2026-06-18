<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/common/check_all_patterns_found.pl -->
# sources/distributed-fs/ceph-client/tools/perf/tests/shell/common/check_all_patterns_found.pl

## Purpose

This Perl helper validates that every supplied regular expression appears at least once in stdin.

## Research

The script builds `%found` as it scans input lines, sets quiet mode from `TESTLOG_VERBOSITY`, and after reading reports any missing regex before exiting nonzero. It does not require every line to match and does not count occurrences. State is in-memory found flags only. Dependencies are Perl regex matching and caller-provided patterns. Integration is used for positive evidence checks such as required report headers, record messages, probe diagnostics, and help text sections. Risks include loose regexes matching unintended text, duplicate regexes collapsing to one hash entry, and quiet mode suppressing missing-pattern messages. Test signal is exit code 0 only when all expected patterns were observed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/common/check_all_patterns_found.pl -->
