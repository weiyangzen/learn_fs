
<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/images/metrics.go -->
# sources/cloud-native/containerd/internal/cri/server/images/metrics.go

## Purpose

This file declares and registers image-pull metrics for the CRI image service under the `containerd_cri_sandboxed` metric namespace/subsystem.

## Important APIs, Types, and Functions

Metrics are package variables: `imagePulls`, `inProgressImagePulls`, and `imagePullThroughput`. The `init` function creates a docker/go-metrics namespace, constructs a labeled counter for pull success/failure, a gauge for in-progress pulls, and a Prometheus histogram for pull throughput, then registers the namespace.

## Control Flow

At package initialization, the namespace and metric collectors are created and registered. Runtime pull code increments or decrements the gauge, increments the labeled counter by outcome, and observes throughput after successful pull size and duration are known.

## State and Persistence Behavior

Metrics are process-local Prometheus/docker-go-metrics collectors. They are not persisted by this file, but external metrics scraping observes their current values.

## Dependencies and Integration Points

Dependencies are `github.com/docker/go-metrics` and Prometheus client_golang. Integration points are `image_pull.go` and the containerd metrics registry.

## Risks and Edge Cases

Metric registration in `init` can conflict if package initialization happens more than once in unusual test setups. Throughput uses default histogram buckets, which may not fit all image-pull speeds. The status counter currently labels only success and failure, with a TODO for registry domain labels.

## Test Signals

Useful tests would verify registration, counter/gauge updates around successful and failed pulls, and throughput observation on success without adding duplicate collectors.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/images/metrics.go -->
