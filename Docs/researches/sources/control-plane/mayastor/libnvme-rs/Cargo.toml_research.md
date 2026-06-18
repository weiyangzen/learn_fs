# sources/control-plane/mayastor/libnvme-rs/Cargo.toml

Purpose: crate manifest for `libnvme-rs`, Rust bindings and safe-ish wrappers around Linux `libnvme`.

Important APIs/types/functions: package metadata sets build script `build.rs`, Apache-2.0 license, edition 2018, and dependencies on `glob`, `libc`, `snafu`, `url`, `mio` with `os-ext`, `udev` with `hwdb`/`mio`, and `uuid` v4. Build dependencies are `bindgen` and `cc`.

Control flow: Cargo invokes bindgen at build time and links against system `libnvme`.

State/persistence: no direct runtime state; dependency set enables NVMe host config reads, udev monitoring, and generated FFI.

Dependencies/integration: consumed by tests/tools needing NVMe-oF connect/disconnect and device enumeration without shelling out to `nvme`.

Risks: tightly coupled to installed libnvme headers/library ABI. Workspace dependency changes can affect generated bindings.

Test signals: build success proves headers and library are available; `nvme_parse_uri` covers URI parsing.
