# sources/cloud-native/soci-snapshotter/util/testutil/shell.go

## Purpose
`shell.go` provides integration-test utilities for dockershell execution, buffered test logging, snapshotter log monitoring, content-store injection/removal, remote file copying, and process cleanup.

## Important APIs, Types, and Functions
`TestingReporter` adapts `testing.T` to the dockershell reporter interface while buffering logs until failure. `LogMonitor` scans stdout/stderr through tee readers and invokes registered line callbacks. `RemoteSnapshotMonitor` counts structured log lines indicating remote, local, or deferred snapshot preparation. `IndexDigestMonitor` extracts the SOCI index digest from structured logs. `MonitorStartup` and `LogConfirmStartup` detect fatal or successful snapshotter startup logs. File/content helpers include `TempDir`, `InjectContentStoreContentFromReader`, `InjectContentStoreContentFromBytes`, `WriteFileContents`, and `CopyInDir`. Cleanup helpers include `KillMatchingProcess`, `RemoveContentStoreContent`, and store-specific removal functions.

## Control Flow, State, and Persistence
`LogMonitor.Start` launches one goroutine per stream and calls registered monitors until `Cleanup` closes a `finished` channel. Snapshot counters are updated atomically. Content injection either writes directly into the SOCI content store under `blobs/<algo>/<encoded>` or uses `ctr content ingest` and labels the parent content with an incrementing SOCI integration-test label. `CopyInDir` creates a local tar stream through a pipe, writes it to the remote shell, extracts it, and removes the temporary tar.

## Dependencies and Integration Points
The file depends on `dockershell`, SOCI store path/type helpers, OCI descriptors, `go-digest`, `xid`, and `errgroup`. It integrates tightly with containerd CLI (`ctr`), shell execution environments, SOCI content store layout, and integration-test logs.

## Risks and Test Signals
Several shell commands use string interpolation into `/bin/sh -c` with paths supplied by tests; callers need controlled paths. `InjectContentStoreContentFromReader` ignores returned errors from the two concrete injection helpers because it does not return after the switch call, so failures can be lost. `LogMonitor.Cleanup` does not block on scanner shutdown; it launches a goroutine to wait, which avoids hanging tests but can leave late log processing. Process killing uses SIGINT to preserve coverage output and ignores disappeared processes, which is useful but pattern matching must be precise.
