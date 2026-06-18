# sources/control-plane/rook/.github/workflows/crds-gen.yml

## Purpose

Verifies Kubernetes CRD manifests and CRD API reference docs are regenerated and committed.

## Important APIs, Types, and Functions

The `crds-gen` job sets up Go 1.26, runs `GOPATH=$(go env GOPATH) make crds`, and checks generated changes via `tests/scripts/validate_modified_files.sh crd`.

## Control Flow

Checkout with full history is followed by Go setup, Makefile CRD generation, and a dirty-worktree validation gate.

## State and Persistence Behavior

Generated CRD artifacts exist only in the CI worktree; any uncommitted diff fails the job.

## Dependencies and Integration Points

It depends on the Makefile `crds` target, `controller-gen`, `yq`, `build/crds/build-crds.sh`, `build/crds/generate-crd-docs.sh`, and validation scripts. Mergify requires `crds-gen`.

## Risks and Edge Cases

CRD generation may be sensitive to controller-gen versions, Go tags, or docs generation toggles. The workflow does not explicitly skip `skip-ci`.

## Test Signals

Passing means generated CRDs and CRD docs match committed sources.
