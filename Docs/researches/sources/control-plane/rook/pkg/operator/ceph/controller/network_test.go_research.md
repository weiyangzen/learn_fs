# sources/control-plane/rook/pkg/operator/ceph/controller/network_test.go

## Purpose
`network_test.go` validates Multus network CIDR discovery and Ceph network setting application without launching real Kubernetes Jobs.

## Important APIs, Types, and Functions
The file defines `mockCmdReporter`, `mockNewCmdReporter()`, `mockDiscoverAddressRangesFunc()`, and `mockMonStore` to replace package-level seams. `Test_discoverAddressRanges` covers public/cluster network selection, output parsing, error cases, multiple IPs, and placement propagation. `TestApplyCephNetworkSettings` covers pod-network no-op, Multus discovery, explicit public/cluster ranges, mixed explicit/discovered ranges, host networking, and mon-store failure propagation. Helpers `netStatus()` and `ipAddrOutput()` synthesize Multus annotation and `ip --json` output.

## Control Flow, State, and Persistence
Tests swap package-level function variables and restore them with defers. The command reporter mock returns stdout/stderr/retcode without Kubernetes execution. The mon-store mock verifies `SetIfChanged("global", "<network>_network", "<cidrs>")` calls and avoids real Ceph config writes.

## Dependencies and Integration Points
The tests depend on Ceph network specs, fake `clusterd.Context`, cmdreporter job construction, Kubernetes batch/core types, testify mock/assert, and `k8sutil` network parsers indirectly through production code.

## Risks
Package-level mock replacement means tests must not run these cases in parallel without additional isolation. The generated JSON strings are hand-built and can drift from real CNI output. Mock expectations verify intended calls but do not assert every job field, service account, annotation, or volume/mount detail in all cases.

## Test Signals
Signals are strong for deterministic CIDR logic and decision-making around explicit versus discovered ranges. Remaining gaps are real Multus/downward API behavior, long timeout cancellation, Job cleanup/replacement, and network-status variations from different CNI plugins.
