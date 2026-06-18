# sources/distributed-fs/ceph-client/tools/testing/selftests/rcutorture/bin/kvm-recheck-rcuscale.sh

Purpose: analyzes rcuscale performance output, preferring ftrace data and falling back to printk-derived writer-duration records.

Important APIs and functions: calls `kvm-recheck-rcuscale-ftrace.sh`; fallback awk parses `-scale: ... gps: ... batches:`, `writer-duration`, and optional grace-period kthread CPU time.

Control flow: validate result dir and path, try ftrace analyzer, exit success if it works, else parse console log for durations and print histogram, average, min, percentiles, max, GP/batch ratio, and CPU time.

State and persistence: read-only.

Dependencies and integration: suite-specific recheck for rcuscale.

Risks and test signals: if neither ftrace nor printk format is present, it prints "No rcuscale records found???". It is performance summarization, not a strict failure detector by itself.
