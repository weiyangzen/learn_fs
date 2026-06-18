# sources/control-plane/rook/.github/workflows/integration-tests-on-release.yaml

## Purpose

Runs the main integration test matrix on pushes to `master`, release branches, and version tags.

## Important APIs, Types, and Functions

Jobs cover Helm suite, multi-cluster deploy, smoke suite, Rook upgrade, Helm upgrade, object without TLS, and object with TLS. Most jobs matrix Kubernetes `v1.31.14`, `v1.32.13`, `v1.33.12`, and `1.35.5`; object jobs use oldest/latest split.

## Control Flow

Release branch or tag pushes trigger full checkout, cluster setup, targeted Go tests, namespace-specific log collection, and failure artifact upload. This workflow omits PR debug composites and failfast flags present in PR workflows.

## State and Persistence Behavior

State is per-job and ephemeral in minikube, devices, Helm tags/releases, namespaces, and integration output logs. Failure artifacts persist.

## Dependencies and Integration Points

It integrates with the setup composite, all core Go integration suites, `github-action-helper.sh`, and release branch gating. Its check names are referenced by Mergify backport automerge rules.

## Risks and Edge Cases

Several matrix values use `1.35.5` without the `v` prefix while other workflows use `v1.35.5`; minikube may accept it, but it is inconsistent. The multi-cluster job sets `export BLOCK="$/dev/${DEVICE_NAME}"`, which looks like a typo and may produce an invalid block path if the test consumes `BLOCK`.

## Test Signals

Passing indicates the release branches pass the full integration suite across the configured Kubernetes versions.
