# sources/distributed-fs/ceph-client/tools/testing/ktest/compare-ktest-sample.pl

Purpose: maintenance script that compares option names used by `ktest.pl` with option names documented in `sample.conf`.

Important APIs, types, and functions: uses Perl hashes `%opt` and `%samp`. It scans `ktest.pl` for `$opt{...}`, hash key declarations, and `set_test_option("...")`; it scans `sample.conf` for uppercase assignment names.

Control flow: opens `ktest.pl`, records discovered option names; opens `sample.conf`, records documented/sample names; prints `opt = NAME` for implementation options missing from the sample and `samp = NAME` for sample entries not seen in implementation.

State and persistence: no file writes; output is diagnostic only.

Dependencies and integration points: assumes it is run from the ktest directory containing `ktest.pl` and `sample.conf`. Depends on Perl regex matching of current source style.

Risks: regexes can miss dynamically generated options or report false positives from comments/strings. It does not handle open failures explicitly. The comparison is name-only and does not validate semantics.

Test signals: a clean sync between script and sample should produce no output. New unmatched options should appear as `opt =` lines.
