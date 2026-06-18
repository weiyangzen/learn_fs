# sources/control-plane/rook/.github/workflows/integration-test-mgr-suite.yaml

## Purpose

Runs the Ceph manager integration suite when explicitly requested.

## Important APIs, Types, and Functions

The `TestCephMgrSuite` job runs on PRs and a daily schedule but has an `if` requiring the PR label `run-mgr-suite`. It uses Kubernetes `v1.35.5` and runs `go test -run CephMgrSuite`.

## Control Flow

After checkout, optional debugging, and cluster setup, the job collects udev logs, selects an extra block device, runs the manager suite, collects logs for `mgr-ns`, uploads artifacts on failure, and optionally opens post-job upterm.

## State and Persistence Behavior

All cluster/test state is ephemeral. Failure artifacts preserve integration output.

## Dependencies and Integration Points

It integrates with PR labels, the setup composite, Go integration tests, and the mgr namespace/operator namespace log collector settings.

## Risks and Edge Cases

The schedule trigger may not satisfy `github.event.pull_request.labels`, making the job effectively label-gated and likely skipped outside PR context. This is intentional or a possible schedule misconfiguration.

## Test Signals

Passing after label selection means the manager integration suite succeeded on Kubernetes `v1.35.5`.
