# sources/control-plane/ceph-csi/internal/health-checker/filechecker.go

## Purpose
`filechecker.go` implements a health checker that proves a volume path is writable and readable by writing a JSON timestamp file and reading it back.

## Important APIs, Types, And Functions
`fileChecker` embeds `checker` and stores `filename`, always `<dir>/csi-volume-condition.ts`. `newFileChecker(dir)` constructs the checker and installs its loop. `readTimestamp()` reads and JSON-decodes a `time.Time`; `writeTimestamp()` JSON-encodes a timestamp and writes it with mode `0644`.

## Control Flow And State
The checker loop starts a ticker at `interval`. On each tick it writes the tick timestamp, reads the file, compares the value exactly with `now`, and updates `healthy`, `err`, and `lastUpdate` under the mutex. Any write, read, unmarshal, or mismatch error marks the checker unhealthy and keeps the loop running. A command received on `commands` clears `isRunning` and exits.

## State And Persistence Behavior
The persistent side effect is a timestamp file in the volume path. The file is overwritten on every successful tick and can be inspected for debugging. Health state itself is in memory and is lost when the checker object is discarded.

## Dependencies And Integration Points
The implementation uses `os.ReadFile`, `os.WriteFile`, `path.Join`, `time.Time.MarshalJSON`, and `time.Time.UnmarshalJSON`. It is created by `healthCheckManager.startFileChecker()` for `FileCheckerType`.

## Risks And Edge Cases
The first actual I/O check does not happen until the first ticker event, while the default state is healthy. Exact timestamp comparison relies on the same JSON round trip and local filesystem write/read visibility. The file mode permits world-readable timestamp metadata. Parent directory absence, read-only mounts, stalled I/O, or corrupted timestamp contents all surface as unhealthy errors.

## Test Signals
`filechecker_test.go` starts a checker against a temporary directory, waits for it to run, repeatedly checks healthy status, and verifies direct write/read helpers. It does not force write failures, read corruption, timestamp mismatch, or timeout handling.
