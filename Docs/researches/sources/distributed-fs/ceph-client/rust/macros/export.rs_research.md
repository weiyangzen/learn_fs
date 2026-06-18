# sources/distributed-fs/ceph-client/rust/macros/export.rs

## Purpose
`export.rs` implements the `#[export]` procedural attribute for Rust functions that C code calls through bindgen-generated kernel bindings. It disables Rust name mangling and emits a compile-time signature compatibility check against the C declaration.

## Important APIs, Types, And Functions
The only helper is `export(f: syn::ItemFn) -> TokenStream`. It extracts `f.sig.ident`, references `::kernel::bindings::<name>`, and emits the original function with `#[no_mangle]`.

## Control Flow
The generated `const _: ()` block contains an `if true { bindings::name } else { name }` expression. Rust type-checks both branches, so the Rust function must match the bindgen declaration. After the check, the original item is emitted with `#[no_mangle]`.

## State And Persistence
No runtime state exists. The output affects the compiled symbol table and compile-time type checking only.

## Dependencies And Integration Points
It integrates with `macros/lib.rs` as `#[proc_macro_attribute] export`, `quote`, `syn::ItemFn`, and `::kernel::bindings`. It is complementary to, but distinct from, Linux `EXPORT_SYMBOL_*`; Rust symbols are currently exported elsewhere.

## Risks And Edge Cases
The macro assumes the Rust function name exactly matches a generated binding. Missing bindings or signature drift fail at compile time. It should not be used for functions called through vtables or function pointers, because those contracts are checked differently.

## Test Signals
Tests should include matching and mismatching C/Rust signatures, missing bindgen declarations, generated `#[no_mangle]` symbol inspection, and confirming the macro rejects non-function input at the public entry point.
