# sources/cloud-native/moby/daemon/start_windows.go

## Purpose
`start_windows.go` selects runtime create options for Windows containers.

## Important APIs, Types, And Functions
`getLibcontainerdCreateOptions` sets `HostConfig.Runtime` from `daemonCfg.DefaultRuntime` or containerd's default runtime, checkpoints the container, and returns the runtime string with nil options.

## Control Flow
If runtime is already configured it is returned unchanged. Otherwise the function chooses a default and persists it.

## State And Persistence
May persist `HostConfig.Runtime` in the container checkpoint.

## Dependencies And Integration Points
Integrates Windows container start with containerd default runtime selection and daemon configuration.

## Risks
Unlike Unix, this path returns no runtime options; future Windows runtime options would need explicit support.

## Test Signals
Windows lifecycle tests cover runtime defaulting.
