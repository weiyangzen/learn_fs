# sources/control-plane/mayastor/.cargo/config.toml

## Purpose
Workspace Cargo configuration for Mayastor builds on `x86_64-unknown-linux-gnu`, plus release profile optimization settings.

## Important APIs and Settings
Target rustflags set `target-cpu=nehalem`, link against `lzma`, and request `lld` with `-fuse-ld=lld`. Release profile enables fat LTO and sets `codegen-units = 1`.

## Control Flow
Cargo reads this file automatically for builds in the workspace. The target-specific rustflags affect compiler and linker invocation; release profile settings affect optimization and code generation.

## State and Persistence
No runtime state. It changes build artifacts under Cargo target directories by altering compilation flags.

## Dependencies and Integration Points
Requires toolchains/linkers that support `lld` and an available `liblzma`. The nehalem CPU baseline influences binary compatibility for x86_64 deployments. Integrates with Nix/dev/CI build environments.

## Risks
Machines without `lld` or `liblzma` fail to link. `target-cpu=nehalem` may exclude older CPUs but keeps a relatively conservative baseline. Fat LTO and single codegen unit improve optimization but increase release build time and memory use.

## Test Signals
Run `cargo build` and `cargo build --release` in the intended Nix/CI environment. Verify produced binaries run on supported CPUs.
