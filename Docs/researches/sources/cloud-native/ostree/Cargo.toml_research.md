<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/Cargo.toml -->
## sources/cloud-native/ostree/Cargo.toml

### Purpose
This manifest defines the `ostree` Rust crate, workspace membership, public bindings library, integration test, dependencies, and feature gates mirroring libostree API versions.

### APIs, Types, and Control Flow
The package is version `0.20.5`, edition 2021, Rust minimum 1.77.0, and exposes library `rust-bindings/src/lib.rs`. The workspace includes the root crate and `rust-bindings/sys`. Runtime dependencies include GLib/GIO bindings, `ostree-sys` via path package `ffi`, `bitflags`, `base64`, `hex`, `libc`, `once_cell`, and `thiserror`. The feature chain starts at `v2014_9` and incrementally enables later `ffi/v...` features through `v2025_3`; `dox` enables documentation support.

### State, Dependencies, and Integration
The manifest controls cargo package inclusion, excluding generated sys/gir config directories while including Rust binding sources. It integrates with `rust.yml`, docs.rs metadata, and the sys crate generated from C introspection.

### Risks and Test Signals
Feature chains are easy to break when adding versions: each later feature must include its predecessor and matching sys feature. The C and Rust latest-feature constants in CI must stay aligned. Test signals are cargo build/test/doc across default selected feature, no-feature mode, and live libostree integration.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/Cargo.toml -->
