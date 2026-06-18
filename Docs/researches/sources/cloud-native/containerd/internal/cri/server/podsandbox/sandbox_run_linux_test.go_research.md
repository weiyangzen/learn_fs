# sources/cloud-native/containerd/internal/cri/server/podsandbox/sandbox_run_linux_test.go

## Purpose

This large Linux test file validates sandbox OCI spec generation, sandbox file setup, and DNS option rendering for Linux pod sandboxes.

## Important APIs, Types, and Functions

`getRunPodSandboxTestData` creates default CRI sandbox config, image config, and spec assertions. `TestLinuxSandboxContainerSpec` covers entrypoint/cmd validation, namespace modes, host cgroups, SELinux, seccomp, sysctls, user/group handling, passthrough annotations, resources, user namespaces, and privileged behavior. `TestSetupSandboxFiles` checks hostname, hosts, resolv.conf, and shm setup. `TestParseDNSOption` checks resolv.conf formatting.

## Control Flow

Tests mutate default config/image data per case, call `sandboxContainerSpec` or setup helpers, and assert concrete OCI spec fields or files. Some root-sensitive paths skip when privileges are unavailable.

## State and Persistence Behavior

Temporary sandbox roots are written and, for shm cases, mounted and cleaned up. No real containerd tasks are started.

## Dependencies and Integration Points

The tests exercise Linux helpers, CRI config defaults, OCI generation, security profile utilities, and OS abstraction behavior.

## Risks and Test Signals

This is the main regression signal for Linux sandbox spec compatibility. It does not replace full runtime tests because kernel, runtime, and CNI behavior are mostly mocked or skipped.
