# sources/cloud-native/containerd/integration/restart_test.go

## Purpose

`restart_test.go` is a cross-platform integration test for recovering CRI sandboxes, containers, and images after restarting containerd.

## Important APIs, Types, and Functions

- `TestContainerdRestart` defines local `sandbox` and `container` structs for expected names, IDs, and states.
- It uses CRI helpers for sandbox/container creation, `containerdClient` to kill a sandbox task directly, `RestartContainerd`, image service list/status, and `SandboxInfo`.

## Control Flow

The test starts a ready sandbox with created/running/exited containers and a not-ready sandbox whose sandbox container is killed. Non-Windows runs also keep a running per-container-PID-namespace container in the not-ready sandbox. It pulls images, snapshots image list state, restarts containerd, lists sandboxes/containers, validates IDs and states, checks ready-sandbox CNI/IP info, removes sandboxes, and compares image metadata before and after restart.

## State and Persistence Behavior

The test validates persisted sandbox/container states, CNI result/IP info, image metadata, and repo tag/digest fields across daemon restart. Direct task kill simulates a dead sandbox while preserving CRI metadata for recovery.

## Dependencies and Integration Points

It integrates CRI runtime/image services, containerd client task APIs, Kubernetes CRI types, image fixtures, OS-specific PID namespace behavior, and daemon restart helpers.

## Risks and Edge Cases

State matching is ID-based but loops do not explicitly fail when a specific ID is absent beyond aggregate counts, so diagnostic precision may be limited. Windows lacks the per-container PID namespace case. CNI and image metadata equality are sensitive to environment and ordering, so repo tags/digests are sorted before comparison.

## Test Signals

This is a core restart regression signal for CRI sandbox/container status restoration, CNI result persistence, and image store persistence.
