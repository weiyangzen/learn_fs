# sources/control-plane/rook/pkg/operator/k8sutil/network_test.go

## Purpose
This test file validates Multus annotation generation and IP parsing/classification behavior.

## Important APIs, Types, and Functions
`TestApplyMultus()` drives `ApplyMultus()` with unknown selectors, public/cluster selectors, JSON selectors, mixed selector formats, OSD labels, and non-OSD metadata. `TestParseLinuxIpAddrOutput()` uses a realistic mixed IPv4/IPv6 JSON fixture. `TestGetIpAddressType()` checks endpoint address type classification.

## Control Flow, State, and Persistence
All tests are local and deterministic. Multus tests create `cephv1.NetworkSpec` values and inspect metadata annotations. IP parser tests unmarshal a static fixture and a truncated variant.

## Dependencies and Integration Points
The tests depend on Rook Ceph network selector parsing, network-attachment-definition types, Kubernetes discovery address constants, and testify.

## Risks
The test intentionally expects unknown network selectors to result in an empty annotation instead of an error, which may hide misconfiguration depending on caller expectations. No test verifies Multus status annotation parsing or interface lookup.

## Test Signals
Strong signals include stable public-before-cluster ordering, JSON and short selector compatibility, empty raw IP output errors, syntax errors, IPv4-only and IPv6-only address typing, and mixed-family rejection.
