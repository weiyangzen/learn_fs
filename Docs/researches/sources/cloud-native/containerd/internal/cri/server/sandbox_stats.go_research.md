# sources/cloud-native/containerd/internal/cri/server/sandbox_stats.go

## Purpose

This file implements the CRI `PodSandboxStats` RPC wrapper and common cgroup metrics container type.

## Important APIs, Types, and Functions

`PodSandboxStats` looks up a sandbox and delegates to platform-specific `podSandboxStats`, returning a `PodSandboxStatsResponse`. `cgroupMetrics` holds either cgroup v1 or v2 metrics.

## Control Flow

The RPC fails on missing sandbox or platform stats failure and wraps errors with sandbox ID context.

## State and Persistence Behavior

No state is mutated. It reads the sandbox store and platform metrics.

## Dependencies and Integration Points

It integrates with CRI stats API, sandbox store, cgroup stats packages, and platform-specific stats implementations.

## Risks and Test Signals

Risk lies mostly in platform metrics collection and ready-state assumptions. Stats integration tests on Linux are needed for full confidence.
