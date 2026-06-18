# sources/control-plane/rook/pkg/operator/k8sutil/node_test.go

## Purpose
This file exercises node eligibility and conversion helpers against fake Kubernetes clients and synthetic nodes.

## Important APIs, Types, and Functions
`createNode()` seeds fake nodes. `TestValidNode()` covers ready, not-ready, `scheduleAlways`, and node affinity. `TestNodeIsTolerable()` covers explicit and well-known taints. `TestNodeIsReady()` checks condition semantics. Matching tests cover Rook node specs against Kubernetes nodes. `TestGenerateNodeAffinity()` covers legacy, JSON, and YAML input. `TestGetNotReadyKubernetesNodes()` checks ready-state filtering.

## Control Flow, State, and Persistence
Tests create in-memory fake clientsets. One test uses `t.Setenv("ROOK_CUSTOM_HOSTNAME_LABEL", ...)` to validate custom hostname resolution. There is no persistent cluster state.

## Dependencies and Integration Points
The tests use Rook Ceph API types, `operator/test` fake-client helpers, Kubernetes fake clientsets, and testify. They protect storage scheduling decisions used by CephCluster reconciliation.

## Risks
There is a small helper bug in `taints()` that appends to the parameter slice while iterating; current call patterns still work but the helper is confusing. Tests do not directly cover API list failures, hostname lookup helpers, or all node selector operators.

## Test Signals
High-value signals are `scheduleAlways` behavior, known-taint bypass, missing hostname fallback, custom hostname label override, and YAML/JSON affinity compatibility.
