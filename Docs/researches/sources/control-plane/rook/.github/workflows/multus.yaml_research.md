# sources/control-plane/rook/.github/workflows/multus.yaml

## Purpose

Runs focused Multus validation tests for user-facing CLI and stretch cluster networking behavior.

## Important APIs, Types, and Functions

The `test-validation-tool` job triggers on pushes and PRs touching Multus-related paths, sets `NUMBER_OF_COMPUTE_NODES=5`, creates a KinD cluster from `tests/scripts/multus/kind-config.yaml`, builds `rook` with `go build -tags=ceph_preview`, and runs several shell tests from `tests/scripts/multus`.

## Control Flow

The job checks out, sets up Go, creates KinD, optionally enables debugging, installs Multus and NADs, builds the binary, runs CLI validation, labels nodes, runs overlap and cleanup tests, taints nodes, then runs public+cluster, public-only, and cluster-only stretch tests. Later tests use `if` dependencies on earlier step outcomes.

## State and Persistence Behavior

State is held in the KinD cluster, node labels/taints, Multus resources, NADs, and the built `rook` binary. No artifacts are uploaded by this workflow.

## Dependencies and Integration Points

It integrates with `cmd/rook/userfacing`, `pkg/daemon/multus`, KinD, Multus scripts, Kubernetes manifests under `tests/scripts/multus`, and debug composites.

## Risks and Edge Cases

The path filter excludes many general code changes that could still affect Multus indirectly. Conditional step chaining means one early failure skips dependent coverage, which is useful diagnostically but reduces signals in a single run.

## Test Signals

Passing means Multus setup, CLI validation, stretch overlap detection, cleanup, and public/cluster network validation scripts succeeded in KinD.
