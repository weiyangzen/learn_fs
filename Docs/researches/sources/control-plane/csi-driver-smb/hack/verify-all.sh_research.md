# sources/control-plane/csi-driver-smb/hack/verify-all.sh

## Purpose
Aggregates major repository verification gates.

## Important APIs, Types, and Functions
Computes `PKG_ROOT` with `git rev-parse --show-toplevel` and runs verify scripts for gofmt, govet, yamllint, boilerplate, Helm chart files, Helm chart content, Helm chart index, and gomod.

## Control Flow
Sequentially executes each gate with `set -euo pipefail`, stopping at the first failure.

## State and Persistence
Mostly read-only, but invoked scripts may install tools or run `go mod tidy/vendor` before diffing.

## Dependencies
Depends on every child verify script and their tools.

## Integration Points
Top-level CI entrypoint for static validation.

## Risks and Edge Cases
Ordering hides later failures. Some child scripts have network and package-manager side effects.

## Test Signals
Zero exit status after all child scripts.
