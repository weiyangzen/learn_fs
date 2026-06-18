# sources/control-plane/ceph-csi/internal/health-checker/statchecker.go

## Purpose
`statchecker.go` implements a lightweight health checker that calls `os.Stat` on a volume path to detect disappearance or inaccessible filesystem state.

## Important APIs, Types, And Functions
`statChecker` embeds `checker` and stores the checked directory path. `newStatChecker(dir)` constructs the checker and installs a ticker-driven `runChecker` implementation.

## Control Flow And State
The loop starts a ticker using `interval`, listens for stop commands, and otherwise calls `os.Stat(sc.dir)`. A stat error marks the checker unhealthy and preserves the error. A successful stat marks the checker healthy, clears `err`, and updates `lastUpdate` to the tick time.

## State And Persistence Behavior
There are no persistent writes. The checker only observes filesystem metadata and keeps in-memory health state.

## Dependencies And Integration Points
The implementation depends on `os.Stat` and the shared `checker` behavior. It is selected by `healthCheckManager.startStatChecker()` for `StatCheckerType`.

## Risks And Edge Cases
The first check is delayed until the ticker fires, so a missing path may initially report healthy. `os.Stat` cannot prove read/write health and only validates the path exists and can be stated. Slow or blocked stat calls are handled indirectly by `checker.isHealthy()` timeout detection.

## Test Signals
`statchecker_test.go` validates a temp directory remains healthy through several polling iterations. It does not remove the directory, simulate permission failures, or exercise timeout behavior.
