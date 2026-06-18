# sources/control-plane/rook/.github/workflows/codegen.yml

## Purpose

Verifies generated Go/API code is up to date on pushes, tags, and pull requests.

## Important APIs, Types, and Functions

The `codegen` job sets up Go 1.26, runs `GOPATH=$(go env GOPATH) make codegen`, and validates with `tests/scripts/validate_modified_files.sh codegen`.

## Control Flow

After checkout with full history, the workflow installs Go, runs the Makefile `codegen` target, then fails if generated files differ from committed content.

## State and Persistence Behavior

Generated files are only created or changed in the ephemeral runner. The validation script turns a dirty worktree into a failed check rather than persisting changes.

## Dependencies and Integration Points

It depends on `build/codegen/codegen.sh`, controller/code generator tooling from the Makefile, Go modules, and the validation script. Mergify requires the `codegen` check for release backport automerge.

## Risks and Edge Cases

Generator output can vary with Go/tool versions, so the pinned Go version and Makefile generator versions are important. The job is skipped for PRs labeled `skip-ci`.

## Test Signals

Passing means `make codegen` is deterministic and committed generated sources match the current code.
