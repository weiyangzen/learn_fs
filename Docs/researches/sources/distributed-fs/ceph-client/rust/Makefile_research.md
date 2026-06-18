# sources/distributed-fs/ceph-client/rust/Makefile

## Purpose
Defines the Rust-for-Linux build graph for core Rust crates, generated C bindings, helper exports, rustdoc, doctests, unit tests, proc-macro support crates, symbol export headers, and optional inline-helper bitcode integration.

## APIs, Types, and Functions
Important targets build `core.o`, `compiler_builtins.o`, `ffi.o`, `bindings.o`, `uapi.o`, `pin_init.o`, `kernel.o`, `build_error.o`, `helpers/helpers.o`, generated binding files, generated export headers, proc-macro rlibs, rustdoc output, rust-analyzer metadata, and doctest KUnit glue. Key variables include `rustdoc_output`, `core-cfgs`, `proc_macro2-cfgs`, `syn-cfgs`, `pin_init-flags`, `bindgen_c_flags_final`, `redirect-intrinsics`, and rules such as `cmd_bindgen`, `cmd_rustc_library`, `cmd_rustdoc`, `cmd_exports`, and `rule_rustc_library`.

## Control Flow, State, and Persistence
The control flow is Kbuild-driven. Under `CONFIG_RUST`, host proc-macro crates are built first, bindgen generates Rust declarations from C helper headers, Rust crates are compiled with generated cfg files and explicit crate dependencies, C helper objects are compiled or linked as LLVM bitcode, and `nm` output is converted into generated `EXPORT_SYMBOL_RUST_GPL()` headers. Build state is persisted only in the object tree: `.o`, `.rlib`, `.rmeta`, generated Rust source, generated C export headers, rustdoc HTML, doctest C/Rust glue, and rust-analyzer JSON.

## Dependencies and Integration
Depends on Kbuild, rustc/rustdoc/clippy, bindgen/libclang, LLVM tools for inline helpers, nm/awk/sed/objcopy, generated kernel cfg files, target JSON, and standard kernel modversion/objtool rules. It integrates the Rust crates with the C kernel build, symbol versioning, docs, tests, and generated bindings.

## Risks and Test Signals
Risks include fragile flag filtering for GCC-vs-Clang bindgen, Rust version conditional logic, ABI mismatches in rustdoc/doctests, missing intrinsic redirection when new compiler builtins appear, symbol export churn, and helper inlining differences under `CONFIG_RUST_INLINE_HELPERS`. Test signals are `make LLVM=1 rustavailable`, `make rust-analyzer`, `make rustdoc`, `make rusttest`, KUnit doctest generation, modversion builds, GCC-built kernel bindgen paths, and architectures covered by `redirect-intrinsics`.
