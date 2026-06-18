# sources/distributed-fs/beegfs-protobuf/Cargo.toml

## Purpose

This manifest defines the Rust crate metadata for generated BeeGFS protobuf definitions.

## Important APIs, Types, And Functions

The package is named `protobuf`, version `0.0.0`, edition 2021, with ThinkParQ authorship, repository homepage, README, and `publish = false`. Dependencies are `tonic`, `prost`, `tonic-prost`, and `prost-types` at version `0.14`. The library root is `rust/lib.rs`.

## Control Flow

Cargo uses this manifest to compile the generated Rust modules under `rust/`. There is no build script here; generation is handled by the Makefile through `protoc-rs`.

## State And Persistence

The manifest does not persist runtime state. `Cargo.lock` is removed by `make clean`, suggesting this repository treats generated libraries and tool checks as source artifacts rather than a published locked application.

## Dependencies And Integration Points

Version comments require dependency versions to match the `protoc-rs` generator version used in the Makefile. The generated Rust files import prost/tonic types according to this manifest.

## Risks And Test Signals

Because the crate is unpublished and named generically `protobuf`, consumers likely use path/git dependencies rather than crates.io. Dependency version drift relative to `protoc-rs` can break generated code compilation. CI `make test-protos` catches generation drift, but a Rust compile/test job would be needed to catch all Cargo compatibility issues.
