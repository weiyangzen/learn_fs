# sources/cloud-native/nydus/rust-toolchain.toml

## Purpose
`rust-toolchain.toml` pins the Nydus workspace toolchain. It requests Rust channel `1.94.0` and installs the `rustfmt` and `clippy` components.

## Important APIs, Types, And Functions
This is configuration rather than Rust code. The only top-level table is `[toolchain]`; `channel` selects the compiler release and `components` asks rustup to provision formatting and linting tools with the toolchain.

## Control Flow
There is no runtime control flow. Tooling flow is driven by rustup: entering the repository or invoking cargo/rustc/rustfmt/clippy under rustup should resolve to Rust `1.94.0` with the listed components available.

## State, Persistence, And Dependencies
The file affects developer and CI environment state by causing rustup to install or select the pinned toolchain. It does not persist application state. It depends on the Rust release existing in the active rustup distribution channel; if `1.94.0` is not available to an environment, builds fail before source compilation.

## Integration Points
Cargo, rust-analyzer, CI jobs, formatting checks, and lint workflows all consume this file indirectly through rustup. The requested `clippy` and `rustfmt` components match the service crate's likely quality gates.

## Risks
Pinning a future or unavailable compiler version can block reproducibility. It also means code may rely on language/library behavior newer than many distributions provide. If CI images cache an older toolchain, this file forces a download step. There are no feature flags or profile settings here, so all behavior is delegated to workspace manifests and cargo commands.

## Test Signals
The file itself has no tests. Validation is indirect: `rustup show`, `cargo check`, `cargo fmt --check`, and `cargo clippy` would confirm availability and compatibility of the pinned toolchain and components.
