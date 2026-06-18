# Research: sources/cloud-native/nydus-snapshotter/pkg/metrics/registry/registry.go

This file creates the package-level Prometheus registry and registers all snapshotter, daemon, filesystem, cache, auth, and cleanup metrics. `init` calls `Registry.MustRegister` for standard collectors, then registers each custom filesystem histogram in `data.MetricHists`.

State is the global `Registry`, which is later served by `metrics/listener.go`. Integration points include every metric definition in `metrics/data`, custom histogram collectors in `metrics/types`, and Prometheus HTTP serving. Because `MustRegister` panics on duplicate or invalid collectors, initialization failures surface early.

Risks include adding a metric definition but forgetting to register it, duplicate metric names across files, and tests importing the package multiple ways with global state. There are no direct tests for registry contents in this subset. This file is a monitoring contract boundary: removing or renaming metrics affects external dashboards and alerts.
