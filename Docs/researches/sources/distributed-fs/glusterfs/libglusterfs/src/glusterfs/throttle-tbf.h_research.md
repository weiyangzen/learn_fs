# sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/throttle-tbf.h

Purpose: `throttle-tbf.h` declares a token-bucket filter used to throttle operation classes such as hash, read, and readdir.

Important APIs and types: `tbf_ops_t` enumerates operation buckets. `tbf_opspec_t` defines an op, token rate, max limit, and generation interval in microseconds. `tbf_bucket_t` stores a lock, token generator thread, current rate/tokens/max, queued requests, and interval. `tbf_t` owns an array of buckets. APIs initialize, modify, and throttle; `TBF_THROTTLE_BEGIN/END` wrap throttle calls.

Control flow and state: `tbf_init` creates buckets from specs. A token generator thread refills tokens. `tbf_throttle` consumes requested tokens or queues/sleeps requests until capacity is available. `tbf_mod` updates specs.

Dependencies and integration: uses Gluster list and lock wrappers plus pthreads. It is suitable for translators/features that need bounded background work rates.

Risks: token generation threads need lifecycle management not visible in this header. Queue fairness, wakeups, and dynamic modification are concurrency-sensitive. `TBF_THROTTLE_END` is empty, so callers cannot rely on paired cleanup.

Test signals: rate-limit accuracy, burst max behavior, multi-threaded fairness, runtime modification, shutdown with queued waiters, and invalid op/spec handling should be tested.
