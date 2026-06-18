# sources/cloud-native/moby/integration/container/diff_test.go

Purpose: Verifies `ContainerDiff` reports filesystem changes for running or stopped containers after creating a directory and file.

Important APIs and flow: `TestDiff` runs a container that creates `/foo/bar`, waits for it to stop, then calls `apiClient.ContainerDiff` and compares exact `FilesystemChange` entries. `TestDiffStoppedContainer` repeats the stopped-container path and includes Windows-specific expected shape, though Windows is skipped because change kinds and path prefixes differ.

State and dependencies: The tests mutate a container writable layer and then inspect diff output. They depend on busybox shell commands and storage-driver diff semantics.

Risks and signals: They catch regressions in change ordering, add/modify classification, and stopped-container diff availability. Failures are strong signals that the daemon's layer differ has changed user-visible API output.
