# sources/control-plane/rook/.github/workflows/integration-test-upgrade-suite.yaml

## Purpose

Runs Rook and Helm upgrade integration tests on PRs.

## Important APIs, Types, and Functions

The workflow has `TestCephUpgradeSuite` running `CephUpgradeSuite/TestUpgradeRook` and `TestHelmUpgradeSuite` running `CephUpgradeSuite/TestUpgradeHelm`. Both matrix Kubernetes `v1.31.14` and `v1.35.5`; the Helm job installs Helm `v3.18.2` and creates a Helm tag.

## Control Flow

Each job follows checkout, optional debugging, setup composite, udev log collection, block-device discovery, targeted `go test`, log collection for the `upgrade` namespace, artifact upload on failure, and optional upterm.

## State and Persistence Behavior

Upgrade state is held in the ephemeral test cluster, old/new Rook deployment artifacts, Helm release metadata, and integration output logs.

## Dependencies and Integration Points

It integrates with Go upgrade tests, Helm, setup and debug composites, Make/build outputs from setup, and collection scripts.

## Risks and Edge Cases

Upgrade tests are order-sensitive and resource-intensive. The Helm upgrade path depends on `create_helm_tag` and installed Helm version. Both jobs skip on `skip-ci`.

## Test Signals

Passing indicates Rook binary/manifest upgrade and Helm upgrade paths work across the supported Kubernetes matrix.
