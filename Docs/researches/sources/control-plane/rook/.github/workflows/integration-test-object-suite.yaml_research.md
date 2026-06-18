# sources/control-plane/rook/.github/workflows/integration-test-object-suite.yaml

## Purpose

Runs Ceph object storage integration tests with non-TLS coverage on the oldest supported Kubernetes version and TLS coverage on the latest.

## Important APIs, Types, and Functions

Jobs are `TestCephObjectSuite` with Kubernetes `v1.31.14` and `go test -run CephObjectSuite/TestWithoutTLS`, and `TestCephObjectSuiteTLS` with Kubernetes `v1.35.5` and `go test -run CephObjectSuite/TestWithTLS`.

## Control Flow

Each job checks out, optionally opens tmate, sets up cluster resources, collects udev logs, selects a block device, runs the object test subset with `SKIP_CLEANUP_POLICY=false`, collects `object-ns` logs, uploads failure artifacts, and can open upterm.

## State and Persistence Behavior

Object-store resources, pools, buckets, secrets, and logs are runner-local. Only failure artifacts persist.

## Dependencies and Integration Points

It integrates with go-ceph preview APIs through `GOFLAGS`, local setup, object integration tests, and log collection scripts.

## Risks and Edge Cases

Splitting TLS and non-TLS by Kubernetes version optimizes coverage but may miss cross-version TLS-specific regressions. Object tests are long-running and depend on RGW readiness.

## Test Signals

Passing confirms RGW object workflows work without TLS on oldest supported Kubernetes and with TLS on latest supported Kubernetes.
