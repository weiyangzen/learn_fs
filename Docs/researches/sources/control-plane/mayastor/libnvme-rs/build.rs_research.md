# sources/control-plane/mayastor/libnvme-rs/build.rs

Purpose: build script that generates Rust FFI bindings for libnvme.

Important APIs/types/functions: `main` emits `cargo:rustc-link-lib=nvme`, rerun tracking for `wrapper.h`, configures `bindgen::Builder` with `wrapper.h`, `CargoCallbacks`, disabled layout tests, and writes `bindings.rs` into `OUT_DIR`.

Control flow: build fails if bindgen cannot parse headers or cannot write generated bindings.

State/persistence: generated bindings live under Cargo build output, not source control.

Dependencies/integration: integrates Cargo, bindgen, clang header parsing, and system libnvme linking.

Risks: generated API varies with installed libnvme version. Disabled layout tests avoid target-specific failures but reduce ABI safety checks.

Test signals: any crate compile requires successful binding generation and linking.
