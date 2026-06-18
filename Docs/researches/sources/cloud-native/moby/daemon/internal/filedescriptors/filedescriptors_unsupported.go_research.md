## sources/cloud-native/moby/daemon/internal/filedescriptors/filedescriptors_unsupported.go

Purpose: Supplies the non-Linux build of fd counting.

Important API: `GetTotalUsedFds(context.Context) int` always returns `-1`.

Control flow and state: No branching or state. The `//go:build !linux` tag keeps it out of Linux builds.

Dependencies and integration: Maintains a common package API for platforms where procfs fd counting is unsupported, including Windows.

Risks: Callers must treat `-1` as unsupported/failure rather than a valid count. No tests are present for this build-tag path.

Persistence: None.
