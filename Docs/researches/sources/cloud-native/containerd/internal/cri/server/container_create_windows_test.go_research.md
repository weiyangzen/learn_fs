# sources/cloud-native/containerd/internal/cri/server/container_create_windows_test.go

## Purpose
This Windows test fixture and suite validates Windows CRI container spec generation, including process command formatting, mounts, network namespace, HostProcess constraints, resources, credentials, and annotations.

## Important APIs, Types, and Functions
It defines `getSandboxConfig` and Windows `getCreateContainerTestData`. Tests include `TestContainerWindowsNetworkNamespace`, `TestMountCleanPath`, `TestMountNamedPipe`, `TestHostProcessRequirements`, and `TestEntrypointAndCmdForArgsEscaped`.

## Control Flow, State, and Persistence
Tests call `buildContainerSpec` with synthetic CRI configs and inspect only the in-memory OCI spec. No hcsshim runtime is started. The entrypoint test table varies image `Entrypoint`, `Cmd`, `ArgsEscaped`, CRI `Command`, and CRI `Args` to verify `Process.Args` versus `Process.CommandLine`.

## Dependencies and Integration Points
The file integrates CRI Windows resources with `spec.Windows.Resources`, Windows network namespace setting, mount path normalization, named pipe mount preservation, HostProcess pod/container consistency, credential spec forwarding, username selection, affinity CPU handling, and default CRI annotations.

## Risks and Test Signals
Risks include malformed Windows command lines, unsafe HostProcess mixing, incorrect path normalization for drive paths or named pipes, lost credential specs, and missing HNS namespace wiring. Signals are exact command-line/args checks and hard errors when HostProcess settings differ between pod and container.
