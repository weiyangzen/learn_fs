<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/misc/musl-static/Dockerfile -->
# sources/cloud-native/nydus/misc/musl-static/Dockerfile

## Purpose

This Dockerfile defines a musl-based Rust build environment for producing static Nydus release binaries.

## Important APIs, Types, and Functions

It uses base image `clux/muslrust:1.72.1`, accepts `RUST_TARGET` defaulting to `x86_64-unknown-linux-musl`, installs `cmake`, sets workdir `/nydus-rs`, and runs rustup component/target setup followed by `make static-release`.

## Control Flow

At container runtime, the `CMD` installs clippy/rustfmt/target and invokes the static release make target.

## State and Persistence Behavior

The image layer installs cmake. Build outputs are produced in the mounted or copied `/nydus-rs` workspace at runtime.

## Dependencies and Integration Points

It integrates with the repository Makefile and musl static build/release workflow used by `goreleaser.sh` packaging assumptions.

## Risks and Test Signals

The base Rust version is pinned and may drift from workspace toolchain requirements. Installing rustup components in `CMD` adds runtime network/toolchain dependence unless cached.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/misc/musl-static/Dockerfile -->
