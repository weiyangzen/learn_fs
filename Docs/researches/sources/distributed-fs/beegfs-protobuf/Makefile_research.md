# sources/distributed-fs/beegfs-protobuf/Makefile

## Purpose

This Makefile is the canonical protobuf generation and verification driver for Go, C++, and Rust BeeGFS protobuf artifacts.

## Important APIs, Types, And Functions

Targets include `all`, `protos`, `test`, `test-protos`, `clean`, `check-tools`, and `install-tools`. Variables define source and output directories plus pinned tool versions: protoc 29.2, protoc-gen-go 1.36.2, protoc-gen-go-grpc 1.5.1, and protoc-rs 0.6.0. `protos` runs `protoc` for Go/gRPC and C++ outputs and `protoc-rs` for Rust outputs. `test-protos` regenerates and fails if `git status` sees changes under generated output directories.

## Control Flow

`protos` depends on `check-tools`, ensuring exact codegen versions before generation. `install-tools` downloads protoc, installs Go plugins with `go install`, and installs ThinkParQ's `protoc-rs` with Cargo from a git tag. `clean` removes generated outputs, target, and Cargo.lock.

## State And Persistence

Generated code is written into `go`, `cpp`, and `rust` directories and expected to be committed. Tool installation writes under `$HOME/.local`. `clean` is destructive to generated directories but intended before regeneration.

## Dependencies And Integration Points

It integrates with GitHub Actions checks, Go module paths under `github.com/thinkparq/protobuf/go`, C++ protobuf runtime, Rust prost/tonic code, curl, unzip, cargo, go, and protoc.

## Risks And Test Signals

Exact version checks improve reproducibility but can make local builds brittle if users have different tools. `install-tools` assumes Linux and maps `aarch64` to `aarch_64`. `test-protos` is a strong drift detector but mutates the worktree, as documented. Generated-code consumers rely on this Makefile as the source of truth.
