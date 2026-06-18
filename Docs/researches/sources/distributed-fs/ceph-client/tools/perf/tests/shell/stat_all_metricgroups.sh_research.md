## sources/distributed-fs/ceph-client/tools/perf/tests/shell/stat_all_metricgroups.sh

Purpose: attempts every metric group from `perf list --raw-dump metricgroups`.
Important behavior: chooses `-a` unless perf_event_paranoid prevents non-root system-wide access, then runs `perf stat -M "$group" sleep 0.01`.
Control flow: successful groups set overall status to pass; permission errors become skips; Default2/3/4 failures are ignored due to possible unsupported legacy events; other failures set hard failure.
State and persistence: no files.
Dependencies and integration: PMU metric metadata and perf stat metric resolver.
Risks: tiny workload can make some groups unsupported or not counted; broad loop is environment-dependent.
Test signals: each metric group either runs, is permission-skipped, is explicitly ignored, or fails with captured output.
