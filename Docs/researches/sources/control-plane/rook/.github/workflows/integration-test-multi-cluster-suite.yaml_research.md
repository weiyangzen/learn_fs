# sources/control-plane/rook/.github/workflows/integration-test-multi-cluster-suite.yaml

## Purpose

Runs the Ceph multi-cluster deployment integration suite for PRs.

## Important APIs, Types, and Functions

The `TestCephMultiClusterDeploySuite` job uses Kubernetes `v1.35.5`, exports `BLOCK`, `TEST_SCRATCH_DEVICE`, and `DEVICE_FILTER`, then runs `go test -run CephMultiClusterDeploySuite`.

## Control Flow

The job checks out, optionally opens debugging, sets up minikube resources, collects udev logs, derives a device name through `find_extra_block_dev`, runs tests, collects logs from both `multi-core` and `multi-external`, always uploads artifacts, and supports post-job debugging.

## State and Persistence Behavior

The test creates multiple namespaces/clusters in the runner's Kubernetes environment and writes logs under the integration output tree. Artifacts always persist, not only on failure.

## Dependencies and Integration Points

It integrates with local setup, Go integration tests, multi-cluster namespaces, block device environment variables, and log collection.

## Risks and Edge Cases

Multi-cluster tests are sensitive to device reuse, namespace cleanup, and resource pressure. Always uploading artifacts increases storage use but improves diagnostics.

## Test Signals

Passing means internal and external multi-cluster deployment flows work for the selected Kubernetes version.
