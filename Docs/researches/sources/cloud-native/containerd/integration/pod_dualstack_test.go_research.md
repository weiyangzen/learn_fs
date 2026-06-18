# sources/cloud-native/containerd/integration/pod_dualstack_test.go

## Purpose

This test verifies CRI pod network status reports additional IPs only when the container network is actually dual-stack. It compares pod status with network information observed inside the container.

## Important APIs, Types, And Functions

- `TestPodDualStack` is the only test.
- It runs `ip address show dev eth0` on Linux or `ipconfig` on Windows.
- `runtimeService.PodSandboxStatus` provides primary and additional pod IPs.

## Control Flow

The test creates a sandbox with a log directory, runs a short-lived BusyBox container that prints network interface information, waits for exit, reads the container log, and retrieves pod sandbox status. Regexes detect IPv4 and IPv6 global addresses in the log. If both are present, the test requires exactly one additional IP, with the primary IP IPv4 and the additional IP IPv6. Otherwise it requires no additional IPs and a non-empty primary IP.

## State And Persistence Behavior

The test observes live CNI-provided network configuration and CRI pod status. The container log is temporary persisted evidence of in-container network state.

## Dependencies And Integration Points

It integrates CRI pod status networking fields, CNI behavior, platform-specific network commands, regex parsing, and Go `net.ParseIP`.

## Risks And Edge Cases

Regex detection is command-output dependent. The test assumes dual-stack means one primary IPv4 plus one additional IPv6, which matches current CRI expectations but not every possible network policy.

## Test Signals

Passing confirms CRI additional IP reporting matches actual single-stack or dual-stack container network state.
