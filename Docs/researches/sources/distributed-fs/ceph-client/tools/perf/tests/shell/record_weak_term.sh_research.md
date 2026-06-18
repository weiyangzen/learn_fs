## sources/distributed-fs/ceph-client/tools/perf/tests/shell/record_weak_term.sh

Purpose: verifies explicit command-line sample period overrides weak/default period terms from sysfs or JSON event definitions.
Important behavior: parses `perf list --json` with Python to find the first event whose encoding contains `period=`, then records it with `-c 1000 -vv`.
Control flow: skips if no such event exists, shows detailed event info, then greps verbose record output for sample period/frequency value `1000`.
State and persistence: no temp files.
Dependencies and integration: requires Python, perf JSON list output, and an event definition with inbuilt period.
Risks: verbose output formatting is literal; event availability depends on PMU metadata.
Test signals: verbose record output includes `{ sample_period, sample_freq }   1000`.
