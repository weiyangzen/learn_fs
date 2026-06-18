<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/common/patterns.sh -->
# sources/distributed-fs/ceph-client/tools/perf/tests/shell/common/patterns.sh

## Purpose

This shared shell file exports regular-expression fragments used by the perf shell testsuite to validate perf output consistently.

## Research

The file defines patterns for decimal and hex numbers, dates/times, addresses, process names, event names, file/path/DSO forms, empty/comment lines, perf-record success lines, trace output, report lines, task names, and segfault diagnostics. These variables are composed by test scripts and passed to Perl checkers. State is a set of exported environment variables; there is no runtime logic beyond assignments. Dependencies are Perl-compatible regex syntax as consumed by `grep -P` or Perl helpers, and `LC_ALL=C` from settings to stabilize text classes. Integration is broad across base_probe/report and other scripts. Risks are regex drift when perf output changes, patterns that are over-specific to English/C locale, and broad patterns masking malformed output. Test signals are indirect: scripts pass when these expressions correctly match expected outputs and reject unexpected lines.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/common/patterns.sh -->
