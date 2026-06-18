## sources/distributed-fs/ceph-client/tools/perf/tests/shell/stat+csv_output.sh

Purpose: lints field counts for `perf stat` CSV-like output using a custom separator.
Important function: caller-defined `commachecker`, plus checks imported from `lib/stat_output.sh`.
Control flow: sets `csv_sep=@`, runs shared stat checks with `-x@ -o temp`, and verifies each non-comment/nonblank line has the expected number of separators per aggregation mode.
State and persistence: one temp stat output file is reused and removed.
Dependencies and integration: depends on `stat_output.sh`, perf stat modes, CPU topology, and shell regex matching.
Risks: expected field counts are tightly coupled to output format; s390x has a special field-count range for no-aggregation mode.
Test signals: every checked mode prints `[Success]`; topology-restricted modes are skipped when socket id is invalid.
