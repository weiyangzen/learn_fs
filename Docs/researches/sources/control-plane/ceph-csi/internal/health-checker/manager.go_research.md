# sources/control-plane/ceph-csi/internal/health-checker/manager.go

## Purpose
`manager.go` provides the public health-check manager that owns checkers per volume and path. It lets callers start, stop, and query file-based or stat-based checkers, with an option for shared checkers that ignore path at lookup time.

## Important APIs, Types, And Functions
`CheckerType` is a bitmask with `FileCheckerType` and `StatCheckerType`. `Manager` exposes `StartSharedChecker`, `StartChecker`, `StopSharedChecker`, `StopChecker`, and `IsHealthy`. `ConditionChecker` abstracts `start`, `stop`, and `isHealthy`. `healthCheckManager` stores `map[string]ConditionChecker` protected by `sync.Mutex`. `fallbackKey(volumeID, path)` joins volume and path for non-shared checkers.

## Control Flow And State
`NewHealthCheckManager()` initializes an empty checker map. Start methods call `createChecker()`, which dispatches to `startFileChecker()` and/or `startStatChecker()` based on the bitmask. `startChecker()` inserts only when the key is absent and starts the checker immediately. Stop methods look up the key, call `stop()`, and delete the entry. `IsHealthy()` checks the shared volume key first, then falls back to the volume/path key, returning `(true, error)` when no checker exists.

## State And Persistence Behavior
Manager state is purely in memory. Shared checkers use `volumeID` as key; non-shared checkers use `volumeID + path`, so multiple mount paths for the same volume can be tracked independently. Persistent health behavior is delegated to concrete checker implementations.

## Dependencies And Integration Points
The manager integrates concrete constructors from `filechecker.go` and `statchecker.go`. It is the package-level orchestration surface expected by CSI volume health logic.

## Risks And Edge Cases
`StartChecker` with both file and stat bits tries both under the same key; the second start sees the key already present and returns a duplicate error. The map lock does not protect fields inside the checker after start. Returning healthy with an error for missing checkers is unusual and relies on callers reading the error. Synchronous `stop()` may block if the checker goroutine is not consuming commands.

## Test Signals
`manager_test.go` covers missing checker queries, start/stop of a stat checker, shared path-insensitive lookup, and independent non-shared checkers for the same volume. It does not cover file checker creation through the manager, duplicate start errors, combined checker bitmasks, or concurrent start/stop/query behavior.
