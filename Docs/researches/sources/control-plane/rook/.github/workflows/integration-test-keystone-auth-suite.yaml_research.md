# sources/control-plane/rook/.github/workflows/integration-test-keystone-auth-suite.yaml

## Purpose

Runs RGW Keystone authentication integration tests on supported Kubernetes versions.

## Important APIs, Types, and Functions

The `TestCephKeystoneAuthSuite` job matrixes Kubernetes `v1.31.14` and `v1.35.5`, installs Helm `v3.18.2`, uses the setup composite with `github-token`, and runs `go test -run CephKeystoneAuthSuite`.

## Control Flow

Eligible PRs trigger the workflow. The job checks out, installs Helm, optionally enables tmate, sets up cluster resources, collects udev logs, chooses a device by `lsblk` size pattern, runs the test suite, collects logs for `keystoneauth-ns`, uploads artifacts on failure, and can open upterm debugging.

## State and Persistence Behavior

Ephemeral state includes minikube resources, Keystone/RGW test namespaces, block devices, and integration logs. Only artifacts persist.

## Dependencies and Integration Points

It integrates with the Go integration package, Helm, local setup composite, GitHub token, and log collection scripts.

## Risks and Edge Cases

Device selection uses `lsblk` matching `14G` or `64G`, which is less abstract than `find_extra_block_dev` and may be runner-shape-sensitive.

## Test Signals

Passing indicates Keystone auth object-store integration works across oldest/latest supported Kubernetes versions.
