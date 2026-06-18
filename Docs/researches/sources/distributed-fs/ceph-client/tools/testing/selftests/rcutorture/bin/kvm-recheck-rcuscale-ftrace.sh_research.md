# sources/distributed-fs/ceph-client/tools/testing/selftests/rcutorture/bin/kvm-recheck-rcuscale-ftrace.sh

Purpose: analyzes ftrace output for rcuscale grace-period performance when sufficient ftrace records are present.

Important APIs and functions: sources `functions.sh`, counts `rcu_exp_grace_period.*start`, then uses sed/grep/awk to pair start/end records, build distributions, detect lost messages, count piggybacking, and compute percentile durations.

Control flow: exit 10 if fewer than 100 start records. Otherwise parse ftrace lines, accumulate grace-period times, print histogram bucket size, distribution, averages, percentiles, maximum, total grace periods, batches, ratio, and lost count.

State and persistence: read-only.

Dependencies and integration: called first by `kvm-recheck-rcuscale.sh`; success suppresses printk-based fallback.

Risks and test signals: assumes ftrace line fields remain stable. Lost or reordered trace messages can reset pairing and affect statistics.
