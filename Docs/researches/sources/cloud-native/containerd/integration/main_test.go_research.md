# sources/cloud-native/containerd/integration/main_test.go

## Purpose

This file is the shared integration test harness for containerd CRI tests. It initializes global CRI/containerd clients, defines pod/container config builders, polling utilities, process helpers, raw gRPC access, config/status helpers, restart logic, and image-pull helpers used throughout the integration package.

## Important APIs, Types, And Functions

- `TestMain`, `ConnectDaemons`, and `DisconnectDaemons` manage global `runtimeService`, `runtimeService2`, `imageService`, and `containerdClient`.
- `PodSandboxOpts`, `PodSandboxConfig`, `PodSandboxConfigWithCleanup`, and many `With...` pod options build CRI sandbox configs.
- `ContainerOpts`, `ContainerConfig`, and many `With...` container options build CRI container configs.
- `Eventually` and `Consistently` provide polling assertions.
- Process helpers include `KillProcess`, `KillPid`, `PidOf`, `PidsOf`, and `PidEnvs`.
- `RawRuntimeClient`, `CRIConfig`, `SandboxInfo`, `RestartContainerd`, `EnsureImageExists`, and `GetContainer` expose lower-level integration access.

## Control Flow

`TestMain` parses flags, connects to CRI runtime/image services and containerd, runs tests, then disconnects. Config builders initialize required nested CRI protobuf fields lazily and apply option functions. Polling helpers loop until success, error, or timeout. Restart logic kills containerd by process name, waits for it to exit, then repeatedly reconnects global clients. `CRIConfig` and `SandboxInfo` call verbose CRI status APIs and unmarshal JSON info.

## State And Persistence Behavior

The file owns process-global clients and endpoint state. It creates randomized pod namespaces with generated IDs. Cleanup is registered through `testing.T.Cleanup` for sandboxes and containers. It reads current CRI config/status and process `/proc` state but writes no durable repository files.

## Dependencies And Integration Points

It integrates with containerd client APIs, CRI remote services, gRPC, Kubernetes CRI client dialers, SELinux, containerd CRI config/types, image package flag parsing, OS process utilities, and platform-specific process commands.

## Risks And Edge Cases

Global clients mean restart tests must carefully reconnect and avoid parallel interference. Many helpers assume Linux `/proc`, Unix sockets, or specific process names, with some Windows branches. `Eventually` returns immediately on any error, so callers must decide whether transient errors are retryable.

## Test Signals

Nearly every integration test depends on this harness; broad suite success validates its config construction, cleanup, polling, client connection, and image-pull behavior.
