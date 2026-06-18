## sources/distributed-fs/ceph-client/tools/perf/tests/shell/stat+csv_summary.sh

Purpose: verifies CSV interval summary labeling behavior.
Important behavior: runs `perf stat -e cycles -x' ' -I1000 --interval-count 1 --summary` and expects a `summary` first field, then runs with `--no-csv-summary` and expects no summary-labeled line.
Control flow: two pipelines grep for `summary` and read fields; unexpected labels cause exit `1`.
State and persistence: no files.
Dependencies and integration: requires cycles event and interval stat support.
Risks: if cycles is unavailable or output text changes, the shell pipelines may fail under `set -e`.
Test signals: first mode sees `summary`; second mode produces no summary label.
