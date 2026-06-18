# sources/control-plane/rook/.github/workflows/golangci-lint.yaml

## Purpose

Runs Go static analysis, vulnerability checks, and Kubernetes API linting.

## Important APIs, Types, and Functions

Jobs are `golangci` using `golangci/golangci-lint-action` version `v2.12.2`, `govulncheck` using `golang/govulncheck-action`, and `kube-api-lint` running `make go.kube-api-lint KUBE_API_LINT_OPTIONS="--new"`.

## Control Flow

Push and PR triggers run independent jobs. Go 1.26 is installed in each job. `golangci` and `kube-api-lint` check out the repo; `govulncheck` only sets up Go and runs the action with `GOFLAGS=-tags=ceph_preview`.

## State and Persistence Behavior

No repository state is modified. Findings are reported as GitHub checks.

## Dependencies and Integration Points

It integrates with `.golangci.yaml`, Makefile lint targets, Go modules, kube-api-linter tooling, and Mergify-required checks.

## Risks and Edge Cases

`govulncheck` lacks an explicit checkout step, which may rely on action defaults or fail depending on action behavior. Static analysis output can change with tool versions.

## Test Signals

Passing `golangci-lint`, `govulncheck`, and `kube-api-lint` indicate Go lint, vulnerability, and API lint gates are clean.
