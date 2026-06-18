# sources/distributed-fs/ceph-client/rust/exports.c

## Purpose
Bridges generated Rust symbol lists into the normal C `EXPORT_SYMBOL_GPL()` infrastructure so Rust crates and helpers can be used by loadable kernel modules.

## APIs, Types, and Functions
Defines `EXPORT_SYMBOL_RUST_GPL(sym)` and includes generated headers for core, bindings, kernel, and conditionally helper symbols. It also exports `rust_build_error` when build assertions are allowed for modules.

## Control Flow, State, and Persistence
There is no runtime behavior. The file is compiled into an object containing export records derived from generated header includes. Persistence is in module symbol tables and, when enabled, symbol version metadata.

## Dependencies and Integration
Depends on `include/linux/export.h`, generated `exports_*_generated.h` files from `rust/Makefile`, Rust v0 symbol mangling producing C-identifier-safe names, and Kbuild modversion handling. It integrates Rust-generated code with module loader symbol resolution.

## Risks and Test Signals
Risks include generated header omission, exporting too broad a Rust surface, symbol-version conflicts, helper export differences under `CONFIG_RUST_INLINE_HELPERS`, and mangling changes. Test signals are module builds using Rust APIs, `nm`/`modpost` export checks, GPL-only enforcement, and builds with helpers both inline and non-inline.
