<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/filesystem/unmounted.go -->
# sources/distributed-fs/beegfs-go/common/filesystem/unmounted.go

Purpose: `Provider` implementation for workflows where a BeeGFS mount may be optional, but most filesystem operations should fail explicitly.

Important APIs/types/functions: `UnmountedFS` implements all `Provider` methods. `GetMountPath` returns empty, `GetRelativePathWithinMount` normalizes paths, and all real operations return `ErrUnmounted`.

Control flow: no branching beyond path normalization; each unsupported operation returns the sentinel.

State and persistence: no state and no filesystem mutation.

Dependencies and integration points: used by callers that decide a missing mount is acceptable for a subset of behavior. It is never returned by `NewFromPath`/`NewFromMountPoint` automatically.

Risks: path normalization simply prefixes `/` and may not match BeeGFS provider edge cases. Callers must explicitly handle `ErrUnmounted` or they will fail at operation time.

Test signals: no direct tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/filesystem/unmounted.go -->
