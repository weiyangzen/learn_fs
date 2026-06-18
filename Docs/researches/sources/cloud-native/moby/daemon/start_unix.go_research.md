# sources/cloud-native/moby/daemon/start_unix.go

## Purpose
`start_unix.go` selects containerd shim/runtime create options for Unix containers.

## Important APIs, Types, And Functions
`getLibcontainerdCreateOptions` ensures `HostConfig.Runtime` is set, checkpoints the container when defaulted, resolves the runtime through `daemonCfg.Runtimes.Get`, and maps errors through `setExitCodeFromError`.

## Control Flow
Callers must hold the container lock. If runtime is empty, it is set to the configured default runtime and persisted. The runtime store returns shim name and options for containerd creation.

## State And Persistence
May persist `HostConfig.Runtime` into the container checkpoint.

## Dependencies And Integration Points
Integrates daemon runtime configuration, container checkpointing, container state exit-code mapping, and containerd create flow in `containerStart`.

## Risks
Runtime resolution failures must set an exit code consistently. Mutating host config under lock is required to avoid races.

## Test Signals
Unix start/runtime integration tests cover default runtime assignment and invalid runtime errors.
