# sources/cloud-native/soci-snapshotter/util/testutil/util.go

## Purpose
`util.go` contains general test utilities for logging, project-root discovery, and buffered output.

## Important APIs, Types, and Functions
Constants define the default GOPATH-relative project root, the `SOCI_SNAPSHOTTER_PROJECT_ROOT` environment variable, and `BuildKitVersion`. `TestingL` is a package-level logger. `TestingLogDest` and `BufferedTestingLogDest` return log writers. `GetProjectRoot` resolves the repo path from the env var, GOPATH, or `go env GOPATH`, and validates a `Dockerfile` exists. `TestWriter` adapts `testing.TB` to `io.Writer`. `BufferedWriter` buffers bytes until `Flush`.

## Control Flow, State, and Persistence
Project-root lookup reads environment variables, may execute `go env GOPATH`, and stats candidate paths. Buffered writer state is an in-memory byte slice that is reset on flush.

## Dependencies and Integration Points
The file uses os/exec/env/path utilities and testing/log/io packages. It integrates with the shell test reporter and test harnesses that need repository-relative assets.

## Risks and Test Signals
`GetProjectRoot` assumes a legacy GOPATH layout when the env var is absent, which may fail in module-only checkouts. `TestWriter.Write` logs whole byte chunks as strings, which can add extra test log formatting. Buffered logging is useful for only emitting command logs on failures.
