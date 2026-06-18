<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/hack/verify-all -->
# sources/control-plane/juicefs-csi-driver/hack/verify-all

## Purpose
Aggregate verification script for Go formatting, vetting, and linting.

## Important APIs, Types, and Resources
Computes `PKG_ROOT` with `git rev-parse --show-toplevel`, then runs `hack/verify-gofmt`, `hack/verify-govet`, and `hack/verify-golint` in order.

## Control Flow
The script stops at the first failing verifier under `set -euo pipefail`. It provides a single CI entry point for common static checks.

## State and Persistence
No repository state is intended to change, though `verify-golint` may install `golangci-lint` if missing. Failure state is expressed via exit code.

## Dependencies and Integration Points
Depends on git, Bash, Go toolchain, and the three verifier scripts. Integrates with CI and pre-submit workflows.

## Risks
Risks include verifier side effects from auto-installing lint tooling, long runtime, and order hiding later failures until earlier ones are fixed.

## Test Signals
Run `hack/verify-all` in CI and locally; success means gofmt, go vet, and golangci-lint all passed.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/hack/verify-all -->
