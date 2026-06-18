# sources/cloud-native/moby/daemon/internal/system/chtimes_linux_test.go

## Purpose
Linux-specific atime tests for `Chtimes`, complementing cross-platform mtime tests.

## Important APIs, Types, And Functions
`TestChtimesATime` creates a temp file, calls `Chtimes` with epoch, pre-epoch, post-epoch, and max-time combinations, then reads `syscall.Stat_t.Atim`.

## Control Flow
Each subtest updates the same temp file and verifies atime. Pre-epoch atime or mtime inputs are expected to clamp to `unixEpochTime`. Max-time comparisons truncate to seconds to tolerate filesystem precision differences.

## State And Persistence
Mutates a temporary file's timestamps only. The temp directory is test-managed.

## Dependencies And Integration Points
Linux build only. Uses `os.Stat` and syscall stat fields, so it verifies actual kernel/file-system behavior rather than mocks.

## Risks And Test Signals
Atime behavior can be filesystem or mount-option sensitive, but explicit `Chtimes` updates should be visible. The strongest signal is that sytem timestamp clamping applies to atime as well as mtime on Linux.
