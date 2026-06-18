# sources/control-plane/rook/.github/workflows/mod-check.yml

## Purpose

Verifies Go module files are tidy and generated module state is current.

## Important APIs, Types, and Functions

The `modcheck` job sets up Go 1.26, runs `GOPATH=$(go env GOPATH) make -j $(nproc) mod.check`, then validates with `tests/scripts/validate_modified_files.sh modcheck`.

## Control Flow

After checkout and Go setup, the Makefile `go.mod.check` target is run in parallel, and the worktree is checked for unexpected module changes.

## State and Persistence Behavior

Any `go.mod` or `go.sum` updates happen only in the runner and fail validation if not committed.

## Dependencies and Integration Points

It integrates with Go modules, Makefile `mod.check`, validation scripts, and Mergify-required `modcheck`.

## Risks and Edge Cases

Module resolution depends on network access and proxy availability. Parallelism can expose nondeterminism in module checks.

## Test Signals

Passing means module files and generated module metadata are already committed.
