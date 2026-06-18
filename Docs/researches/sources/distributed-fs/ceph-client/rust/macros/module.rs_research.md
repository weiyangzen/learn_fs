# sources/distributed-fs/ceph-client/rust/macros/module.rs

## Purpose
`module.rs` implements the `module!` macro that turns Rust module metadata and a module type into Linux module init/exit glue, `.modinfo` records, optional module parameter registration, and built-in initcall support.

## Important APIs, Types, And Functions
Important types are `ModuleInfo`, `Parameter`, and `ModInfoBuilder`. `module(info: ModuleInfo)` is the main generator. `param_ops_path()` maps supported Rust integer parameter types to kernel `PARAM_OPS_*` symbols. `parse_ordered_fields!` parses macro fields in arbitrary syntax order but enforces the documented order. `ModInfoBuilder::{emit, emit_param, emit_params}` builds `.modinfo` and `__param` static items.

## Control Flow
Parsing requires `type`, `name`, and `license`; optional fields include `authors`, `description`, `alias`, `firmware`, `imports_ns`, and `params`. Generation normalizes the module name into a Rust identifier, emits modinfo records for loadable and built-in variants, reads `RUST_MODFILE` for built-in `file=...`, emits module parameter access statics and `kernel_param` structures, creates `THIS_MODULE`, aliases the user type to `LocalModule`, implements `ModuleMetadata`, and emits double-nested private init/exit glue. Loadable modules expose `init_module` and `cleanup_module`; built-ins use an initcall section or PREL32 global asm plus unique init/exit symbols.

## State And Persistence
Generated persistent state includes `.modinfo` byte strings, parameter access statics, `__param` entries, `THIS_MODULE`, and a `static mut __MOD: MaybeUninit<LocalModule>`. Runtime state is initialized exactly once through `<LocalModule as InPlaceModule>::init(...).__pinned_init(__MOD.as_mut_ptr())` and later destroyed by `__MOD.assume_init_drop()` on successful module unload or built-in exit.

## Dependencies And Integration Points
The macro integrates tightly with Linux module metadata sections, initcall sections, module parameter ABI, `kernel::ThisModule`, `kernel::InPlaceModule`, `kernel::ModuleMetadata`, `pin_init::PinInit`, and `RUST_MODFILE`. It uses `CString` for NUL-terminated names and `AsciiLitStr` for metadata that must be ASCII.

## Risks And Edge Cases
Ordering validation can reject otherwise syntactically valid macro input. `param_ops_path()` panics for unsupported parameter types. Names containing NUL are rejected by `CString::new`; module names with hyphens are converted to underscores only for Rust identifiers. `static mut __MOD` relies on kernel lifecycle guarantees that init and exit are called at most once and in order. Architecture-specific PREL32 initcall emission must match kernel linker expectations.

## Test Signals
Tests should cover full metadata emission, built-in versus loadable cfg output, parameter declarations for every supported integer type, wrong field order and duplicate/unknown field diagnostics, missing `RUST_MODFILE`, hyphenated module names, init failure cleanup behavior, and generated symbol/section inspection in kernel builds.
