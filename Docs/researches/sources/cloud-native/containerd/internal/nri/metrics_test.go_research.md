# sources/cloud-native/containerd/internal/nri/metrics_test.go

## Purpose
Tests NRI metrics recording and Prometheus gathering.

## Important APIs, Types, And Functions
Tests call `newNRIMetrics` methods and helper assertions `assertCounter`, `assertGauge`, and `assertTimer` over `prometheus.DefaultGatherer`.

## Control Flow
Each test records one or more observations, gathers all metric families, finds matching labels, and checks counter/gauge/histogram values.

## State And Persistence
Uses global Prometheus/default metrics state, so values can accumulate across tests.

## Dependencies And Integration Points
Uses prometheus client model, testify, gRPC status/codes, and context errors.

## Risks
Because counters are global, tests use greater-or-equal for counters. Reusing labels across tests or packages can create cross-test coupling.

## Test Signals
Good coverage for error-type normalization and metric updates.
