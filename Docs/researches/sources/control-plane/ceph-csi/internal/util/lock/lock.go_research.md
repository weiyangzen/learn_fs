<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/lock/lock.go -->
## sources/control-plane/ceph-csi/internal/util/lock/lock.go

**Purpose:** Wraps RADOS object locks as an `IOCtxLock` interface for exclusive volume-level locking with consistent error/log behavior.

**Important APIs and types:** `IOCtxLock` declares `LockExclusive` and `Unlock`. `NewLock` builds a private `lock` with IO context, volume ID, lock name, cookie, description, and timeout. `LockExclusive` calls `ioctx.LockExclusive`; `Unlock` calls `ioctx.Unlock`.

**Control flow, state, and persistence:** Lock state is persisted/managed by RADOS. `LockExclusive` maps negative return codes for `EBUSY` and `EEXIST` into descriptive errors and wraps other failures. `Unlock` logs success, missing-lock `ENOENT`, or other errors but does not return an error to callers.

**Dependencies and integration points:** Depends on go-ceph `rados.IOContext`, syscall errno values, `context`, and logging. It integrates with volume operations that need distributed mutual exclusion across processes.

**Risks and test signals:** Unlock failures are only logged, so callers cannot recover programmatically. Correctness depends on stable lock name/cookie pairs and timeout values. No direct tests in this subset; integration tests with RADOS are needed for errno mapping and distributed behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/lock/lock.go -->
