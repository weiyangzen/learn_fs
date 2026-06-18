# sources/control-plane/longhorn-engine/pkg/sync/rpc/list_test.go

Purpose: tests `SnapshotHashList` CRUD behavior and retention refresh triggers.

Important APIs/types/functions: registers a gocheck `TestSuite`. `TestSnapshotHashListCRUD` adds, gets, deletes, and verifies missing lookups. `TestSnapshotHashListRefreshTriggerByAdd` adds more than `MaxSnapshotHashJobSize` completed jobs and asserts size is capped. `TestSnapshotHashListRefreshTriggerByGet` marks jobs complete during gets and verifies refresh eventually shrinks the list.

Control flow: each test creates jobs with cancellable contexts, mutates job state directly to terminal complete, and observes list size after add/get operations.

State and persistence: in-memory only. Context cancel functions are created but not called, which is acceptable for these inert jobs but not representative of executing jobs.

Dependencies and integration points: exercises `SnapshotHashList` from `list.go` and `replica.NewSnapshotHashJob`.

Risks: does not test duplicate in-progress rejection, completed replacement for same snapshot, error-state retention, deletion idempotence, or `BackupList`. Directly mutating job state without locks is acceptable in tests but bypasses production status locking.

Test signals: good regression coverage for hash job retention cap and basic CRUD.
