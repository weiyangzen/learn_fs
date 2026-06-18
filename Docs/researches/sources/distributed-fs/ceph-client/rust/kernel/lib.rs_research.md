# sources/distributed-fs/ceph-client/rust/kernel/lib.rs

Purpose: defines the root Rust `kernel` crate, module exports, module initialization traits, panic handling, core macros, and small helpers shared by Rust kernel code.

Important APIs/types/functions: crate feature gates, module exports, `Module`, `InPlaceModule`, `ModuleMetadata`, `ThisModule`, `container_of!`, `assert_same_type`, `concat_literals!`, architecture-specific `asm!`, panic handler, and `file_from_location`. It also publicly re-exports `bindings`, `macros`, `uapi`, and `ffi`.

Control flow: module crates implement `Module::init`; `InPlaceModule` adapts that into pin-init by constructing `Self` then writing into the provided slot. `ThisModule` wraps the raw `THIS_MODULE` pointer. Panics print emerg and call `BUG()`. `container_of!` computes a field offset, subtracts it from a field pointer, then type-checks the field pointer. `asm!` normalizes kernel inline assembly syntax, adding AT&T syntax on x86. `file_from_location` selects the best available compiler API for C-string source filenames.

State and persistence behavior: root crate owns no durable runtime state. It controls compile-time API surface through `CONFIG_*` conditional modules and unstable feature gates. `ThisModule` is a raw module pointer with static use expectations.

Dependencies and integration points: this is the integration hub for nearly every Rust kernel abstraction. It depends on generated bindings, proc macros, pin-init, kernel configuration symbols, architecture assembly generation, and the kernel BUG/logging facilities.

Risks: any exported module or feature gate change affects all Rust kernel users. `container_of!` is unsafe at call sites and relies on same-allocation provenance. The panic handler intentionally terminates via `BUG()`. Conditional compilation must be correct; the crate emits a `compile_error!` when `CONFIG_RUST` is missing to avoid silent misbuilds.

Test signals: crate-level build coverage across representative kernel configs is the main signal. Macro doctests exercise `container_of!` and `file_from_location`. Architecture build tests should cover `asm!` on x86 and non-x86. Module initialization tests should ensure `Module` and `InPlaceModule` paths both run destructors correctly on later teardown.
