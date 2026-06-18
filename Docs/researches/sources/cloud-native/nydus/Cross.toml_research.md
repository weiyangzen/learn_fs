# sources/cloud-native/nydus/Cross.toml

## Purpose
This config customizes `cross` pre-build setup for cross-compiling Nydus.

## Important APIs, Types, and Functions
The `[build].pre-build` list installs `cmake` and `unzip`, then downloads and installs protobuf `protoc` v29.6 into `/usr/local`.

## Control Flow
When `cross` builds a target, it runs these pre-build shell commands inside the build container before Cargo compilation.

## State and Persistence
State is container-local package installation and `/usr/local` protoc files. No repository files are modified.

## Dependencies and Integration Points
This integrates with release/smoke workflows that install `cross` and run `make static-release` for non-RISC-V Linux architectures. It supports crates or build scripts requiring protobuf generation.

## Risks and Edge Cases
The config downloads from GitHub during builds, so network availability and checksum trust matter. It assumes x86_64 Linux protoc is acceptable in the cross build environment. Apt package names must match the base image.

## Test Signals
Successful cross static builds in smoke/release workflows validate this file.
