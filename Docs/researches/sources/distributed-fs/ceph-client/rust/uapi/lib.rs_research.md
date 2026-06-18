# sources/distributed-fs/ceph-client/rust/uapi/lib.rs

Purpose: provides the Rust kernel `uapi` crate containing bindgen-generated Rust bindings for selected userspace API headers.

Important APIs/types/functions: the crate is `#![no_std]`, imports `pin_init::MaybeZeroable`, declares manual aliases for blocklisted kernel scalar types `__kernel_size_t`, `__kernel_ssize_t`, and `__kernel_ptrdiff_t`, enables `cfi_encoding`, and includes generated code from `$OBJTREE/rust/uapi/uapi_generated.rs`.

Control flow: there is no runtime control flow. Compilation expands the generated binding file and applies broad lint allowances suitable for generated C FFI.

State and persistence: no runtime state. The persistent artifact is the generated Rust source in the object tree; crate contents depend on the kernel build configuration and bindgen output.

Dependencies and integration: integrates with the kernel Rust build, generated UAPI bindings, `pin_init`, and the headers listed in `uapi_helper.h`. Kernel Rust drivers use it when they need UAPI constants, structs, or ioctl definitions.

Risks: generated bindings can vary with headers and build configuration. The many lint allowances hide generated-code rough edges, so ABI correctness must be validated through bindgen and kernel header tests rather than style checks. `include!` requires `OBJTREE` to be set correctly.

Test signals: kernel Rust build with UAPI generation enabled, bindgen regeneration checks, ABI smoke tests for selected constants/struct layouts, and drivers compiling against this crate.
