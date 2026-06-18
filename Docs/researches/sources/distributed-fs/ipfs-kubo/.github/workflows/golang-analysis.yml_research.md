# sources/distributed-fs/ipfs-kubo/.github/workflows/golang-analysis.yml

## Purpose
This workflow enforces Go source hygiene: tidy module files, `go fmt`, `go fix`, and `go vet`.

## Important APIs, Types, And Functions
It uses `protocol/multiple-go-modules@v1.4` for multi-module `go mod tidy` and `go vet`, plain `go fmt ./...`, and `go fix ./...` followed by `git diff` checks.

## Control Flow
After checkout with recursive submodules and Go setup, the job runs tidy, formatting, fix, and vet steps. Later steps use `if: always()` so multiple classes of hygiene failures can be reported in one run.

## State And Persistence Behavior
The workflow intentionally detects generated local modifications to `go.mod`, `go.sum`, or source files and fails instead of persisting them.

## Dependencies And Integration Points
It integrates Go tooling, all Go modules in the repository, Git diff state, and submodule checkout.

## Risks And Test Signals
Risks include `go fix` behavior changes across Go versions and multi-module action drift. Signals are empty formatter output, no post-tidy/post-fix diff, and successful vet.
