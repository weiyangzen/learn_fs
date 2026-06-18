# sources/cloud-native/containerd/internal/cri/io/metrics.go

## Purpose

This file registers counters for CRI log processing volume and splitting behavior.

## Important APIs, Types, and Functions

Package variables `inputEntries`, `outputEntries`, `inputBytes`, `outputBytes`, and `splitEntries` are `go-metrics` counters. `init` creates namespace `containerd_cri`, initializes the counters, and registers the namespace.

## Control Flow

Initialization runs at package load. `logger.go` increments these counters while redirecting logs. There is no runtime branching in this file after `init`.

## State and Persistence Behavior

Counter values are process-local metrics state exposed through the containerd metrics registry. They are not persisted across restarts.

## Dependencies and Integration Points

It depends on `github.com/docker/go-metrics` and integrates with CRI logging metrics emitted by `redirectLogs`.

## Risks and Edge Cases

Metric names are part of the observable surface; renaming them can break dashboards. Registration happens unconditionally at package init, so duplicate namespace registration would be a risk if package initialization semantics changed.

## Test Signals

Useful tests or integration checks should confirm the counters are registered and increment during log redirect, especially split entries for long log lines.
