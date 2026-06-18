<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/lock/group_lock_test.go -->
## sources/control-plane/ceph-csi/internal/util/lock/group_lock_test.go

**Purpose:** Tests and benchmarks the two-group mutual exclusion lock under concurrency, blocking, stress, and all-or-nothing wakeup behavior.

**Important APIs and functions:** Tests include `TestGroupLock_MultipleGroupA`, `TestGroupLock_GroupABlocksGroupB`, `TestGroupLock_NoDeadlock`, `TestGroupLock_MutualExclusion`, `TestGroupLock_AllOrNothing`, and `TestGroupLock_StressTest`. Benchmarks are `BenchmarkGroupLock_GroupA` and `BenchmarkGroupLock_Alternating`.

**Control flow, state, and persistence:** Tests spawn goroutines, use wait groups, atomics, timers, and channels to observe concurrency properties. All state is in-memory. Some assertions are timing-based.

**Dependencies and integration points:** Depends on `sync`, `sync/atomic`, `time`, and `math/rand` for benchmarks. It validates a primitive intended for broader operation synchronization.

**Risks and test signals:** Strong concurrency signal for intended properties, but timing-based tests can be flaky under severe scheduler load. Tests do not cover release-without-acquire or starvation over unbounded load, which the implementation explicitly does not prevent.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/lock/group_lock_test.go -->
