<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/kvstore/errors.go -->
# sources/distributed-fs/beegfs-go/common/kvstore/errors.go

Purpose: sentinel errors for Badger-backed map store operations and locking failures.

Important APIs/types/functions: `ErrEntryAlreadyExistsInDB`, `ErrEntryNotInDB`, `ErrEntryLockAlreadyExists`, `ErrEntryAlreadyDeleted`, `ErrEntryLockAlreadyReleased`, and `ErrEntryIllegalKey`.

Control flow: no flow; `mapstore.go` returns/wraps these errors and tests can use `errors.Is`.

State and persistence: none.

Dependencies and integration points: depends on the unexported `reservedKeyPrefix` constant from `mapstore.go`, so error text changes with that reserved prefix.

Risks: exact messages are less stable than sentinels. `ErrEntryIllegalKey` is constructed from a package constant, so moving constants can affect initialization.

Test signals: mapstore tests outside this work item likely cover these sentinels; this subset includes only the error definitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/kvstore/errors.go -->
