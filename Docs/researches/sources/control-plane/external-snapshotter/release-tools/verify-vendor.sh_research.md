<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/release-tools/verify-vendor.sh -->
# sources/control-plane/external-snapshotter/release-tools/verify-vendor.sh

## Purpose
`verify-vendor.sh` verifies that Go module files and, when present, the `vendor/` directory are up to date with `go mod tidy` and `go mod vendor`.

## Important APIs, Types, and Functions
The script runs only when `go.mod` exists. In Prow presubmit jobs it can skip dependency checks when the diff does not touch `go.mod`, `go.sum`, `vendor`, `release-tools`, or Go import blocks. Otherwise it runs `GO111MODULE=on go mod tidy`, checks `git status --porcelain -- go.mod go.sum`, optionally runs `go mod vendor`, then checks `git status --porcelain -- vendor`.

## Control Flow, State, and Persistence
The script mutates the worktree during verification, then fails if the mutation produced differences. It prints diffs/status for stale `go.mod`, `go.sum`, or `vendor` and exits nonzero. In no-vendor repos it only validates module files.

## Dependencies and Integration Points
It depends on Bash, Go modules, Git, and Prow variables `JOB_NAME`, `JOB_TYPE`, and `PULL_BASE_SHA` for the skip optimization. It is part of release-tools verification and pairs with `update-vendor.sh`.

## Risks and Test Signals
Risks include skip logic missing dependency-affecting changes, failures in shallow or non-Prow clones where base SHA is unavailable, and environment-specific module tidy output. Signals are clean `git status` for module/vendor paths and success messages for up-to-date dependencies.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/release-tools/verify-vendor.sh -->
