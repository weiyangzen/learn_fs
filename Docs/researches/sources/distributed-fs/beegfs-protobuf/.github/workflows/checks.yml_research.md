# sources/distributed-fs/beegfs-protobuf/.github/workflows/checks.yml

## Purpose

This GitHub Actions workflow verifies that generated protobuf outputs are current on pull requests. It regenerates Go, C++, and Rust artifacts and fails if the repository diff changes.

## Important APIs, Types, And Functions

The workflow is named `checks`, runs on `pull_request`, and defines one `checks` job in the `rust` container. It sets `CARGO_NET_GIT_FETCH_WITH_CLI=true`, checks out code, caches tool directories keyed by the Makefile hash, installs `golang` and codegen tools on cache miss, adds `$HOME/.local/bin` to the GitHub path, and runs `git config --global --add safe.directory` plus `make clean && make test-protos`.

## Control Flow

The job installs dependencies only when the cache misses. `make test-protos` regenerates all protobuf outputs and uses `git status` to detect uncommitted generated-code changes.

## State And Persistence

Persistent state is the Actions cache for local bin/include, Cargo, Go, and `/usr/local/go`. Build outputs are regenerated in the checked-out workspace and should end clean.

## Dependencies And Integration Points

It depends on `actions/checkout@v4`, `actions/cache@v4`, apt `golang`, the repository Makefile, protoc/protoc-gen-go/protoc-gen-go-grpc/protoc-rs, and GitHub runner/container semantics.

## Risks And Test Signals

The cache key only hashes the Makefile, so dependency/tool changes outside it may not invalidate. The job uses a mutable `rust` container tag. The safe.directory path is hard-coded to `/__w/protobuf/protobuf`, which assumes repository naming. The main signal is strong: generated files must be reproducible and committed.
