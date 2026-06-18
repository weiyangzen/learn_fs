# sources/cloud-native/nydus/contrib/nydus-backend-proxy/Makefile

## Purpose
This Makefile provides local build, format-check, release, static-release, and clean targets for the Rust backend proxy.

## Important APIs, Types, and Functions
Targets include `all`, `.format`, `.musl_target`, `.release_version`, `build`, `release`, `static-release`, and `clean`. Variables include `current_dir`, `rust_arch`, and `CARGO_BUILD_FLAGS`.

## Control Flow
Default `all` runs format check and build. Release targets append `--release`; static release adds a musl target `${rust_arch}-unknown-linux-musl`. Build delegates to `cargo build`; clean delegates to `cargo clean`.

## State, Persistence, and Dependencies
The Makefile persists build artifacts through Cargo target directories. It depends on `cargo`, `rustfmt`, and musl target availability for static builds.

## Integration Points
This is the developer and release entrypoint for the proxy crate. CI can use `.format` or `release` to enforce formatting and optimized build.

## Risks and Test Signals
`uname -p` does not always match Rust target architecture naming on every platform. There is no test target. Static release will fail unless the musl Rust target and C toolchain are installed.
