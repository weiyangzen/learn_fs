# sources/control-plane/rook/.github/workflows/integration-test-smoke-suite.yaml

## Purpose

Runs the core Ceph smoke integration suite on oldest and latest supported Kubernetes versions for PRs.

## Important APIs, Types, and Functions

The `TestCephSmokeSuite` job matrixes Kubernetes `v1.31.14` and `v1.35.5`, sets `GOFLAGS=-tags=ceph_preview`, and runs `go test -run CephSmokeSuite`.

## Control Flow

Eligible PRs trigger checkout, optional tmate, cluster setup, udev log collection, device discovery, smoke tests with `SKIP_CLEANUP_POLICY=false`, log collection for `smoke-ns`, failure artifact upload, and optional upterm.

## State and Persistence Behavior

State is limited to the ephemeral Kubernetes cluster, local block device, and integration log output. Failure artifacts persist.

## Dependencies and Integration Points

It integrates with the common setup composite, Go integration package, block device helper, and log collector.

## Risks and Edge Cases

Smoke tests are foundational and can fail from environment setup, storage device discovery, or broad Ceph/Rook regressions. The job is skipped for `skip-ci`.

## Test Signals

Passing indicates the baseline Rook/Ceph deployment path succeeds on both supported Kubernetes bounds.
