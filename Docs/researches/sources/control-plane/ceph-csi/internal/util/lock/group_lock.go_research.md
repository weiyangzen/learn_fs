<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/lock/group_lock.go -->
## sources/control-plane/ceph-csi/internal/util/lock/group_lock.go

**Purpose:** Implements two-group mutual exclusion: many operations in the same group may run concurrently, but group A and group B may not overlap.

**Important APIs and types:** `GroupLock` stores a mutex, active counters for each group, and separate condition variables. `NewGroupLock`, `AcquireGroupA`, `ReleaseGroupA`, `AcquireGroupB`, and `ReleaseGroupB` are the full API.

**Control flow, state, and persistence:** Acquire methods lock the mutex, wait while the opposite group count is nonzero, then increment their group count. Release methods decrement their group count and broadcast to the opposite group when the count reaches zero. State is in-memory and per lock instance only.

**Dependencies and integration points:** Depends only on `sync`. It is suitable for node/controller operation classes where same-class concurrency is safe but opposite-class concurrency is not.

**Risks and test signals:** There is no fairness guarantee; a busy group can delay the other. Release without acquire can make counters negative and break exclusion. Broadcast wakes all waiters in the opposite group, creating all-or-nothing group admission. Tests cover same-group concurrency, blocking, deadlock, mutual exclusion, all-or-nothing, stress, and benchmarks.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/lock/group_lock.go -->
