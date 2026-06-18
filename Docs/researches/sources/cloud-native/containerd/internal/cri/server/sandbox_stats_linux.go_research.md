# sources/cloud-native/containerd/internal/cri/server/sandbox_stats_linux.go

## Purpose

This Linux file collects pod sandbox CPU, memory, process, container, and network statistics for CRI.

## Important APIs, Types, and Functions

`podSandboxStats` validates ready state, loads cgroup metrics, builds `PodSandboxStats`, computes CPU/memory via container stats helpers, collects all non-loopback netns interface stats, lists child container stats, and sums process counts. `getContainerNetIO` and `getAllContainerNetIO` inspect netlink inside a netns. `cgroupMetricsForSandbox` loads cgroup v1 or v2 metrics from the sandbox cgroup parent.

## Control Flow

Stats collection fails if the sandbox is not ready or has no valid cgroup parent. Network stats are collected only when `NetNSPath` is set. Default interface is `eth0` when present, otherwise the first non-loopback interface.

## State and Persistence Behavior

No persistent state is changed. It reads cgroup files and netns link statistics.

## Dependencies and Integration Points

It integrates with cgroups v1/v2, netlink, CNI netns, CRI container stats helpers, and sandbox store metadata/status.

## Risks and Test Signals

Risks include missing cgroup parent, closed netns, cgroup mode differences, and interface ordering. Linux stats integration tests should cover v1/v2 and multi-interface cases.
