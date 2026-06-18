# sources/cloud-native/cri-o/internal/lib/container_server_linux.go

## Purpose
Provides Linux-specific platform hooks for sandbox SELinux level reference counting and OCI namespace path extraction during sandbox restore.

## Important APIs, Types, And Functions
- `addSandboxPlatform` parses the sandbox process label and increments `state.processLevels[level]`.
- `removeSandboxPlatform` decrements the level count and releases the SELinux label when the count reaches zero.
- `configNsPath(spec *rspec.Spec, nsType rspec.LinuxNamespaceType) (string, error)` finds a non-empty namespace path in the OCI spec.

## Control Flow
Sandbox add/remove parse SELinux context maps and update reference counts under the caller's `stateLock`. Namespace extraction scans `spec.Linux.Namespaces`, returns the matching non-empty path, and errors on empty or missing paths.

## State And Persistence
Mutates in-memory SELinux process level counts and may release SELinux labels through the SELinux library. No files are written here.

## Dependencies And Integration Points
Called by `ContainerServer.AddSandbox`, `RemoveSandbox`, and `LoadSandbox`. Depends on opencontainers SELinux library and runtime-spec namespace types.

## Risks And Edge Cases
Malformed SELinux labels cause sandbox add/remove errors. Level reference counts must stay balanced or labels may leak or be released too early. `configNsPath` assumes `spec.Linux` and `Namespaces` are present when called.

## Test Signals
`container_server_test.go` covers invalid SELinux label failure and missing/empty network namespace behavior through `LoadSandbox`.
