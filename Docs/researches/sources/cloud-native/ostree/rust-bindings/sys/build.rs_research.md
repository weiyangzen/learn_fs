# sources/cloud-native/ostree/rust-bindings/sys/build.rs

## sources/cloud-native/ostree/rust-bindings/sys/build.rs

Build script for the `ostree_sys` crate. For docs.rs it defines an empty `main` to avoid linking system libraries during documentation builds. In normal builds it calls `system_deps::Config::new().probe()`, prints any probe error, and exits with status `1` on failure.

Control flow is intentionally minimal: docs builds skip probing/linking, while local/package builds require system dependency discovery to succeed. State is Cargo build-script output and linker metadata emitted by `system-deps`; no repository files are modified.

Dependencies are `system-deps` and `std::process`. Integration points are Cargo, pkg-config/system dependency metadata, and docs.rs. Risks include environment-sensitive failures when libostree development files are missing, and docs.rs hiding link problems by design. There are no local tests for the build script.
