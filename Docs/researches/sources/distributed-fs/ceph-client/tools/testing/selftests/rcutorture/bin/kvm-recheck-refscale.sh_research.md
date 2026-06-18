# sources/distributed-fs/ceph-client/tools/testing/selftests/rcutorture/bin/kvm-recheck-refscale.sh

Purpose: extracts refscale reader timing results from console output and summarizes distribution.

Important APIs and functions: awk detects the `Runs Time(ns)` table, collects numeric duration values, sorts with `asort`, and prints points, average, min, median, and max.

Control flow: validate dir, strip timestamps/carriage returns, parse the first timing table, and print computed summary.

State and persistence: read-only.

Dependencies and integration: suite-specific analyzer used by `kvm-recheck.sh` for refscale.

Risks and test signals: a typo-like statement `dataphase == 2` is a comparison, not assignment, so phase termination may not behave as intended. Format drift can result in no records.
