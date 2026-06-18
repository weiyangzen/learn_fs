# sources/control-plane/rook/.github/workflows/integration-test-helm-suite.yaml

## Purpose

Runs the Go `CephHelmSuite` integration tests for Helm installs on PRs that touch non-doc/design paths.

## Important APIs, Types, and Functions

The `TestCephHelmSuite` job matrixes Helm `v3.13.3` and `v3.18.3` against Kubernetes `v1.35.5`, sets `GOFLAGS=-tags=ceph_preview`, installs Helm, invokes the setup composite, creates a Helm tag, and runs `go test -run CephHelmSuite`.

## Control Flow

PRs to master/release branches trigger the workflow unless docs/design-only. The job is skipped on `skip-ci` and on direct master refs. It collects udev logs, determines a device filter, runs tests with cleanup disabled, collects logs, uploads failure artifacts, and can open post-job upterm debugging.

## State and Persistence Behavior

State lives in the temporary minikube cluster, generated Helm tag, local block device, and integration output directory. Artifacts persist only on failure.

## Dependencies and Integration Points

It integrates with Azure Helm setup, cluster setup composite, Go integration tests, `github-action-helper.sh`, and `collect-logs.sh`.

## Risks and Edge Cases

The workflow uses a narrow Kubernetes matrix but a two-version Helm matrix. Device discovery and cleanup behavior are runner-sensitive.

## Test Signals

Passing means Helm-based deployment and upgrade/cleanup paths in `CephHelmSuite` work for the matrix.
