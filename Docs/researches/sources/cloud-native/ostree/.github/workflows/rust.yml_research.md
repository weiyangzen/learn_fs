<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/.github/workflows/rust.yml -->
## sources/cloud-native/ostree/.github/workflows/rust.yml

### Purpose
This workflow validates the Rust bindings for libostree under featureful, no-feature, live-C-library, and dependency-policy configurations.

### APIs, Types, and Control Flow
The `build` job runs in the FCOS buildroot, caches cargo dependencies, installs `just`, checks format, builds/tests with `CARGO_PROJECT_FEATURES=v2022_6`, runs clippy, and builds docs with warnings denied. `build-no-features` runs cargo tests without features. `build-git-libostree` checks out submodules/history, builds the C lib through `./ci/build.sh`, installs it from `target/c`, then tests Rust bindings against `LATEST_LIBOSTREE`. `cargo-deny` runs bans, sources, and license checks.

### State, Dependencies, and Integration
It integrates cargo, `just`, `rust-cache`, the C autotools build, and `cargo-deny`. Environment variables pin the default binding feature and latest C API feature currently exercised.

### Risks and Test Signals
Feature values must stay in sync with `Cargo.toml` and the C library's supported API. Cache/action pinning is mixed: rust-cache is commit-pinned, checkout versions vary. Test signals are cargo fmt/test/clippy/doc, no-feature compilation, live C-library integration tests, and cargo-deny policy success.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/.github/workflows/rust.yml -->
