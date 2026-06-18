<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/common/check_no_patterns_found.pl -->
# sources/distributed-fs/ceph-client/tools/perf/tests/shell/common/check_no_patterns_found.pl

## Purpose

This Perl helper asserts that none of the supplied regular expressions appear in stdin.

## Research

The script scans every input line against every command-line regex, records any found pattern, then reports found regexes in verbose mode and exits nonzero if any appeared. State is a `%found` hash and a pass flag. Dependencies are Perl regex semantics and the shared verbosity environment. Integration protects negative assertions, for example no segfault text, no manual-page lookup failure, and absent probe/event output. Risks include regexes that are too broad, duplicate regex collapse, and lack of line context for found patterns in quiet mode. Test signal is exit code 0 only when none of the forbidden patterns matched.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/common/check_no_patterns_found.pl -->
