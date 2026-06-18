# sources/control-plane/rook/.github/workflows/rbac-gen.yaml

## Purpose

Verifies generated RBAC manifests derived from Helm charts are current.

## Important APIs, Types, and Functions

The `gen-rbac` job sets up Go 1.26, runs `GOPATH=$(go env GOPATH) make gen-rbac`, and validates with `tests/scripts/validate_modified_files.sh gen-rbac`.

## Control Flow

Checkout with full history is followed by Go setup, RBAC generation through the Makefile, then dirty-worktree validation.

## State and Persistence Behavior

Generated RBAC output is runner-local and must match committed files.

## Dependencies and Integration Points

It integrates with Helm charts, `build/rbac/gen-common.sh`, Makefile Helm dependencies, `yq`, validation scripts, and Mergify-required `gen-rbac`.

## Risks and Edge Cases

Chart or Helm rendering changes can cascade into generated RBAC. The workflow does not honor `skip-ci`.

## Test Signals

Passing means generated RBAC manifests are reproducible from current Helm charts.
