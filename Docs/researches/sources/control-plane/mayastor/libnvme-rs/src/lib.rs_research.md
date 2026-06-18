# sources/control-plane/mayastor/libnvme-rs/src/lib.rs

Purpose: crate root exposing generated libnvme bindings plus wrapper modules.

Important APIs/types/functions: includes generated `bindings.rs` from `OUT_DIR` under a clippy-allowed module, re-exports all generated symbols, declares `error`, `nvme_device`, private `nvme_tree`, and private `nvme_uri`, and publicly re-exports `NvmeDevice` and `NvmeTarget`.

Control flow: no runtime flow except compile-time include of generated bindings.

State/persistence: none directly; generated bindings mirror system libnvme stateful APIs.

Dependencies/integration: central integration point for downstream crates to access both raw FFI and higher-level wrapper types.

Risks: public `pub use bindings::*` exposes unsafe C API broadly, so consumers can bypass wrapper invariants. Generated symbol set depends on host libnvme.

Test signals: crate build verifies bindgen output is available and wrapper modules compile.
