
<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/metrics.go -->
# sources/cloud-native/containerd/internal/cri/server/metrics.go

## Purpose

This file declares and registers CRI server operation metrics for sandbox, container, checkpoint, and network plugin operations.

## Important APIs, Types, and Functions

Package metrics include timers for sandbox list/network create/network delete, labeled timers for sandbox runtime create/stop/remove, container create/start/stop/remove/checkpoint, a container-events-dropped counter, and labeled counters/timers for network plugin operations and errors. Constants `networkStatusOp`, `networkSetUpOp`, and `networkTearDownOp` preserve dockershim-compatible operation labels.

## Control Flow

The `init` function creates a `containerd_cri` metrics namespace, initializes every metric collector with names, help strings, and labels, then registers the namespace.

## State and Persistence Behavior

Metrics are process-local collectors registered with docker/go-metrics. The file does not persist values but exposes them for the containerd metrics endpoint.

## Dependencies and Integration Points

The only import is `github.com/docker/go-metrics`. Other CRI server files observe or increment these metrics around lifecycle and network plugin operations.

## Risks and Edge Cases

Registration happens at package initialization and can conflict in unusual test configurations if duplicate namespaces are registered. Metric names and labels are compatibility-sensitive, especially network operation labels kept for kubelet/dockershim compatibility.

## Test Signals

Useful tests would verify metrics registration, expected names/labels, and that lifecycle paths record timers and counters without duplicate collector errors.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/metrics.go -->
