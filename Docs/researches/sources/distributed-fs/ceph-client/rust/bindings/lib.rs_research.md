# sources/distributed-fs/ceph-client/rust/bindings/lib.rs

## Purpose
Defines the no-std Rust crate that imports generated bindgen output and exposes raw C kernel symbols and helper wrappers to higher-level Rust kernel code.

## APIs, Types, and Functions
`bindings_raw` includes `bindings_generated.rs`, imports helper symbols, manually defines blocklisted kernel integer aliases, and implements `Zeroable` for bindgen bitfield storage. `bindings_helper` includes `bindings_helpers_generated.rs` and rewrites helper names so generated Rust code can call `bindings::foo` while linking to `rust_helper_foo`. The crate re-exports `bindings_raw::*` and provides `compat_ptr_ioctl` as an `Option` depending on `CONFIG_COMPAT`.

## Control Flow, State, and Persistence
All state is compile-time generated source inclusion. Runtime calls are raw unsafe FFI calls into C or helper wrappers. The crate intentionally has broad lint allowances because generated code uses C naming, layout, and unsafe forms. There is no persistence beyond compiled metadata and object files.

## Dependencies and Integration
Depends on `OBJTREE` include paths, bindgen output, the `ffi` crate, `pin_init` marker traits, `cfi_encoding`, and the C helper generation rules. It is the lowest-level Rust integration point and is not meant to be used directly by modules.

## Risks and Test Signals
Risks include generated binding drift, direct user reliance on raw APIs, CFI/signature mismatches, missing `Zeroable` coverage for generated types, and configuration-dependent missing symbols. Test signals are full Rust crate builds, bindgen regeneration, clippy/rusttest libraries where enabled, and higher-level wrappers compiling without reaching into this crate directly.
