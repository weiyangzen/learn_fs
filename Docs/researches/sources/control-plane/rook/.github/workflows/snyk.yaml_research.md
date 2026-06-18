# sources/control-plane/rook/.github/workflows/snyk.yaml

## Purpose

Runs Snyk vulnerability scanning for the main Rook repository on pushes to master, release branches, and tags.

## Important APIs, Types, and Functions

The `security` job gates on `github.repository == 'rook/rook'`, checks out full history, sets up Go 1.26, installs Snyk CLI `v1.1302.1`, and runs `snyk test --debug` with `SNYK_TOKEN` and `GOFLAGS=-buildvcs=false`.

## Control Flow

Pushes trigger setup, CLI install, and vulnerability scan. There is no PR trigger.

## State and Persistence Behavior

No repository state is written. Scan results are persisted only as GitHub check logs and Snyk-side records if the CLI reports them.

## Dependencies and Integration Points

It integrates with Snyk secrets, Go modules, Snyk CLI, and release branch security checks.

## Risks and Edge Cases

`--debug` can produce verbose logs. The scan is unavailable in forks or without `SNYK_TOKEN`. Vulnerability database updates can change results without code changes.

## Test Signals

Passing means Snyk did not find blocking vulnerabilities under the current policy and dependency graph.
