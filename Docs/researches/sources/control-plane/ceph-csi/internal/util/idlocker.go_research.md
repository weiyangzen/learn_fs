<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/idlocker.go -->
## sources/control-plane/ceph-csi/internal/util/idlocker.go

**Purpose:** Provides in-process locking primitives to prevent conflicting operations on the same volume, snapshot, target path, pod, or host ID.

**Important APIs and types:** `IDLocker` is a simple set protected by a mutex with `TryAcquire` and `Release`. `OperationLock` maintains per-operation maps and exposes typed acquire/release methods for snapshot create, clone, delete, restore, expand, and modify. `conflictMatrix` defines which operations block each other.

**Control flow, state, and persistence:** All state is in-memory and process-local. `tryAcquire` checks conflicting operation maps for the same volume ID, increments counters for create/clone/restore, and sets flag-style locks for delete/expand/modify. `release` decrements counters and removes keys at zero; releasing a missing key is a no-op.

**Dependencies and integration points:** Depends on Kubernetes `sets` and internal logging. It integrates with CSI controller/node operation serialization to return “operation already exists” style errors before starting unsafe work.

**Risks and test signals:** Locks do not coordinate across processes or pods. Conflict coverage is policy-sensitive: `createOp` has no conflicts, while delete does not list clone/create as blockers except through attempted clone/expand/modify conflicts. Counter operations allow multiple same-type operations concurrently by design. Tests cover simple ID locking, clone-vs-expand conflict, multiple clone/restore counters, create, and delete, but not all matrix combinations.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/idlocker.go -->
