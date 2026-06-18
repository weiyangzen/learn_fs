# Research: sources/cloud-native/moby/daemon/cluster/executor/container/validate_windows_test.go

## sources/cloud-native/moby/daemon/cluster/executor/container/validate_windows_test.go

Purpose: supplies Windows path constants and the Windows-only named-pipe mount validation test. The build tag is `windows`.

Important content: `testAbsPath` and `testAbsNonExistent` use drive-letter absolute paths, and `TestControllerValidateMountNamedPipe` verifies that named-pipe mounts reject an empty source even when the target is a pipe path. State is synthetic only.

Dependencies are SwarmKit API types and shared `newTestControllerWithMount`. Risks covered are Windows-specific mount semantics and the named-pipe exception to absolute target validation. Gaps include validating named-pipe target format beyond the empty-source rule.
