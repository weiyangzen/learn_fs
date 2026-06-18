# sources/cloud-native/moby/daemon/builder/remotecontext/utils_test.go

## Purpose
Provides a shared test helper for creating files with specific contents and permissions inside temporary build-context directories.

## Important APIs, Types, And Functions
Defines `createTestTempFile(t, dir, filename, contents string, perm os.FileMode) string`.

## Control Flow
The helper joins `dir` and `filename`, writes bytes with `os.WriteFile`, fails the test on error, and returns the created path.

## State And Persistence
Creates test-scoped filesystem files. Cleanup is owned by the temp directory from callers.

## Dependencies And Integration Points
Used by remotecontext tests such as archive hash and remote download tests.

## Risks And Test Signals
It does not create parent directories, so callers must prepare subdirectories. Because it calls `t.Fatalf`, failures stop the active test immediately.
