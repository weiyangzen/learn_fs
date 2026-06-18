<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/os/testing/fake_os.go -->
# sources/cloud-native/containerd/pkg/os/testing/fake_os.go

## Purpose
Provides a thread-safe fake implementation of pkg/os.OS for tests that need to observe or inject filesystem, mount, symlink, and hostname calls without mutating the host.

## Important APIs, Types, And Functions
FakeOS exposes optional function fields for MkdirAll, RemoveAll, Stat, ResolveSymbolicLink, FollowSymlinkInScope, CopyFile, WriteFile, Mount, Unmount, LookupMount, and Hostname. CalledDetail records call name and arguments. InjectError, InjectErrors, ClearErrors, and GetCalls control and inspect behavior.

## Control Flow
Each fake method records the call, consumes a one-shot injected error for that operation, then delegates to the configured function field or returns a neutral default.

## State And Persistence
Maintains in-memory call history and a map of one-shot errors protected by a mutex. No filesystem persistence occurs unless a test supplies function hooks that perform it.

## Dependencies And Integration Points
Implements github.com/containerd/containerd/v2/pkg/os.OS and uses core/mount.Info in LookupMount. Intended for unit tests across packages that accept the OS interface.

## Risks And Edge Cases
Injected errors are consumed on first use, so tests must be explicit about repeated failures. Default Stat returns nil FileInfo and nil error, which is useful for mocks but can hide assumptions if used carelessly.

## Test Signals
Compile-time interface assertion verifies API coverage. Downstream tests can assert GetCalls ordering and injected-error propagation.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/os/testing/fake_os.go -->
