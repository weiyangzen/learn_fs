# sources/distributed-fs/ceph-client/tools/testing/selftests/rcutorture/bin/kvm-end-run-stats.sh

Purpose: appends end-of-run summary diagnostics and returns the recheck status.

Important APIs and functions: sources `functions.sh`, calls `kcsan-collapse.sh`, runs `kvm-recheck.sh`, tees output into run log, and prints elapsed duration via `get_starttime_duration`.

Control flow: validate result directory, establish start time, print summary header, collapse KCSAN reports, run recheck into temp output, append output and final status to log, exit with recheck code.

State and persistence: appends to `$rundir/log` and may create `kcsan.sum`.

Dependencies and integration: final step for `kvm.sh`, `kvm-again.sh`, and remote runs.

Risks and test signals: recheck status is authoritative. If recheck tooling misses a failure, this summary will report success.
