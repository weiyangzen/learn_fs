# sources/distributed-fs/ipfs-kubo/.github/workflows/golint.yml

## Purpose
This workflow runs the repository lint target for Go code.

## Important APIs, Types, And Functions
The job sets Kubo test/lint environment variables, checks out the repo, sets up Go from `go.mod`, and runs `make -O test_go_lint`, which is backed by the Make rules and `.golangci.yml`.

## Control Flow
It runs on master pushes, pull requests except Markdown-only changes, and manual dispatch, gated to the canonical repo unless manually triggered.

## State And Persistence Behavior
Linting is read-only aside from Go/action caches and temporary build outputs.

## Dependencies And Integration Points
It integrates Make rules, `golangci-lint`, the Go module graph, and Kubo's resource manager default check environment.

## Risks And Test Signals
Risks include linter version changes in Make dependencies and repository-specific runner differences. The test signal is `make test_go_lint` exiting successfully.
