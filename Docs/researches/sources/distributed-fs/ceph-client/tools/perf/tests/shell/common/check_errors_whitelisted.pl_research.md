<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/common/check_errors_whitelisted.pl -->
# sources/distributed-fs/ceph-client/tools/perf/tests/shell/common/check_errors_whitelisted.pl

## Purpose

This Perl helper validates stderr output against a whitelist file, failing on any line that does not match one of the file's regexes.

## Research

The script accepts one whitelist path, reads regex lines from it, honors `TESTLOG_ERR_MSG_MAX_LINES` and `TESTLOG_VERBOSITY`, then scans stdin line by line. Each input line must match at least one whitelist regex after chomp; unmatched lines are optionally printed and cause nonzero exit. State is local arrays and counters. Dependencies are readable whitelist files and Perl regex behavior. Integration is used by report tests where stderr may contain known benign warnings but unknown errors should fail the case. Risks include an absent whitelist causing a hard die, overly broad whitelist entries masking real failures, and newline/comment handling in whitelist files. Test signal is exit code 0 when stderr is empty or fully whitelisted.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/common/check_errors_whitelisted.pl -->
