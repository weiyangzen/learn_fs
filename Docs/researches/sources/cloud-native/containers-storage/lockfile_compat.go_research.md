# sources/cloud-native/containers-storage/lockfile_compat.go

## Purpose
This compatibility file preserves deprecated storage-package lockfile entry points while delegating to `pkg/lockfile`.

## Important APIs
`type Locker = lockfile.Locker` aliases the deprecated locker type. `GetLockfile(path)` calls `lockfile.GetLockfile(path)`. `GetROLockfile(path)` calls `lockfile.GetROLockfile(path)`. All are marked deprecated in favor of direct `pkg/lockfile` APIs.

## Control Flow and State
There is no local state. Calls pass through to the lockfile package, so persistence and locking semantics are entirely owned by `pkg/lockfile`.

## Dependencies and Integration Points
The only dependency is `github.com/containers/storage/pkg/lockfile`. The file exists for external callers that still import lock helpers from the root storage package.

## Risks and Edge Cases
The file intentionally carries deprecated APIs. Risk is mainly API compatibility: removing or changing it could break downstream users. The staticcheck suppression documents why the deprecated alias is still present.

## Test Signals
No direct tests in this subset. Compatibility is implicitly tested by downstream build coverage and any external users compiling against these symbols.
