## sources/distributed-fs/ceph-client/tools/perf/tests/shell/trace_record_replay.sh

Purpose: smoke test for `perf trace record` followed by offline replay.
Important behavior: requires perf trace and root, records `sleep 1` to a temp file, then runs `perf trace -i` and greps for `nanosleep`.
Control flow: direct command failures exit `1`; missing trace support/root skip with code `2`.
State and persistence: temp trace perf.data file is removed after replay.
Dependencies and integration: trace record format and offline trace decoding.
Risks: syscall name can vary (`clock_nanosleep` vs nanosleep patterns), but grep uses broad `nanosleep`.
Test signals: replay output contains a nanosleep syscall.
