# sources/control-plane/rook/pkg/operator/ceph/cluster/mgr/spec_test.go

## Purpose

This file tests Kubernetes object generation for Ceph manager deployments and services. It focuses on pod spec correctness, resource propagation, Multus sidecars, probe overrides, service selectors, host-network behavior, Prometheus annotations, and manager-specific host-network overrides.

## Important APIs and Test Flow

`TestPodSpec` builds a manager cluster with a Ceph image, dashboard port, priority class, data dir, and resource requests/limits. The traditional deployment subtest validates Ceph labels, expected env vars, the shared pod-template tester's full suite, annotation count, container count, and volume mounts. The Multus subtest sets `Network.Provider = "multus"` and expects an extra annotation, an extra command-proxy container, admin-keyring mount, and `CEPH_ARGS` pointing at the admin keyring. The probe subtest configures mgr startup and liveness probes and confirms generated container probes use the custom initial delays.

`TestServiceSpec` validates `MakeMetricsService()` output: name, single metrics port, labels, and selectors for `app=rook-ceph-mgr`, `mgr_role=active`, and `rook_cluster`. `TestHostNetwork` confirms cluster-level host networking sets `DNSClusterFirstWithHostNet`. `TestApplyPrometheusAnnotations` verifies default scrape annotations are applied only when no mgr-specific annotations are configured. `TestMgrNetwork` covers the precedence of `spec.Mgr.HostNetwork` over cluster network settings when explicitly set.

## State, Dependencies, and Integration

The tests use fake Kubernetes clients, minimum owner references, Rook's pod-template test helpers, and resource quantity assertions. The state under test is generated in-memory Kubernetes object specs, not persisted API server state.

## Risks and Test Signals

These tests are strong signals for object drift that could affect scheduling, monitoring, or networking. They intentionally assert exact counts for annotations, containers, mounts, selectors, and probes. A risk is that exact counts can be brittle when legitimate shared volumes or annotations are added, but that brittleness is useful for catching unintended pod-shape changes.
