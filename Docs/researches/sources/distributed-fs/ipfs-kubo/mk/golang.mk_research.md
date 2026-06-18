<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/mk/golang.mk -->
# sources/distributed-fs/ipfs-kubo/mk/golang.mk

## Purpose

This fragment defines Go build/test helpers and major Kubo test targets.

## Important APIs, Types, and Functions

It enables modules, defines `GOCC`, `GOTAGS`, `GOTFLAGS`, `GOFLAGS=-trimpath`, `GOPATH`, package-name helpers, build macros, coverage exclusions, `test_unit`, `test_cli`, FUSE test targets, `test_examples`, platform build check, formatting, and lint targets. It also aggregates `TEST_GO`, `TEST`, and `TEST_SHORT`.

## Control Flow, State, and Integration

Targets call `go list`, `go build`, `gotestsum`, Kubo CLI integration tests, FUSE tests with `TEST_FUSE=1`, and example module replacement tests. In tarball mode it adds `-mod=vendor`.

## Dependencies, Risks, and Test Signals

Dependencies are GNU Make, Go toolchain, gotestsum, golangci-lint, Kubo test binaries, FUSE environment, and shell utilities. Risks include regex exclusions hiding packages, test timeouts too short or long, local `GOFLAGS` pollution, and module replacement cleanup in `test_examples`. CI test targets are the primary validation signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/mk/golang.mk -->
