# sources/control-plane/csi-lib-utils/release-tools/verify-vendor.sh

## Purpose

This verifier checks that dependency metadata and the vendor directory are up to date for dep-based or Go module repositories.

## Important Behavior

For `Gopkg.toml`, it requires dep version `v0.5+` and runs `dep check`. For `go.mod`, it may skip dependency checks in Prow presubmit jobs when the diff does not touch `go.mod`, `go.sum`, `vendor`, `release-tools`, or import declarations. Otherwise it runs `GO111MODULE=on go mod tidy`, verifies `go.mod`/`go.sum` are clean, and when `vendor/` exists runs `go mod vendor` and verifies vendor is clean.

## State, Dependencies, and Integration

It mutates the worktree during verification and then checks for diffs. Dependencies include bash, git, dep or Go modules, and Prow env vars such as `JOB_NAME`, `JOB_TYPE`, and `PULL_BASE_SHA`. It integrates with Makefile `test-vendor` style targets.

## Risks and Test Signals

The Prow skip heuristic is complex and can miss dependency-affecting changes outside import hunks. Running tidy/vendor can be Go-version sensitive. Test signals are git status/diff output and a nonzero exit if files change or commands fail.
