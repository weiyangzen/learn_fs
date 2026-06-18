# sources/distributed-fs/juicefs/pkg/meta/utils.go

## Purpose
`utils.go` contains shared metadata constants, error translation, permission/lock helpers, recursive remove and summary traversal logic, atime policy checks, and transaction method-name diagnostics.

## Important APIs, Types, and Functions
Constants include counter names, fallocate flags, clone modes, atime modes, and permission masks. Key types are `msgCallbacks`, `freeID`, `queryMap`, `plockRecord`, `ownerKey`, `PLockItem`, and `FLockItem`. Important functions are `errno`, `accessMode`, `align4K`, `parseOwnerKey`, `loadLocks`, `dumpLocks`, `updateLocks`, `emptyDir`, `emptyEntry`, `Remove`, `GetSummary`, `getDirSummary`, `GetTreeSummary`, `getTreeSummary`, `atimeNeedsUpdate`, `relatimeNeedUpdate`, `txMethod.name`, and `callerName`.

## Control Flow and State
`errno` normalizes Go errors to syscall errno values and logs stacks for unexpected errors. Recursive deletion descends directories with bounded concurrency, batches non-directory unlink operations, retries non-trash directories on `ENOTEMPTY`, and honors cancellation. Summary functions either use stored dir stats or recursively list children and aggregate counts/space with bounded goroutines. `updateLocks` splits, updates, removes, sorts, and merges POSIX lock ranges. `callerName` lazily discovers the outer non-anonymous caller unless the context has an explicit transaction method.

## State and Persistence Behavior
Most state is transient. Summary and removal mutate metadata through `baseMeta` APIs, so persistence is delegated to the active engine. Atime checks influence later persisted attr updates. Counter names define persistent KV counter keys.

## Dependencies and Integration Points
It is used by KV and non-KV metadata engines, lock implementations, quota/stat accounting, command query parsing, and tests. It depends on Redis nil handling, JuiceFS utilities, runtime stack/caller inspection, and platform-specific constants from `utils_*.go`.

## Risks and Test Signals
Risks include errno masking unexpected failures as `EIO`, recursive delete races, summary double-counting when dir stats are stale, lock range merge errors, and caller-name instability. Tests cover atime/relatime and caller-name behavior; broader integration tests should cover recursive remove and summary under concurrent mutations.
