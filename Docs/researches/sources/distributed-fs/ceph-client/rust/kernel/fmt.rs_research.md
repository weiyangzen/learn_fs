# sources/distributed-fs/ceph-client/rust/kernel/fmt.rs

## Purpose
`fmt.rs` centralizes formatting traits for Rust kernel code. It re-exports core formatting types and defines an adapter/display pattern that allows kernel macros to format foreign types while avoiding direct orphan-rule conflicts.

## Important APIs, Types, and Functions
The file re-exports `Arguments`, `Debug`, `Error`, `Formatter`, `Result`, and `Write`. `Adapter<T>` is an internal wrapper used by formatting macros. `impl_fmt_adapter_forward!` forwards non-display formatting traits. The custom `Display` trait mirrors `core::fmt::Display`, and `impl_display_forward!` implements it for primitive types, `PanicInfo`, `Arguments`, `str`, and kernel smart pointers that already implement display.

## Control Flow
Formatting macros wrap values in `Adapter`; forwarded trait impls delegate to the underlying type. For display, kernel-local `Display` implementations can be added for foreign types, then `Adapter<&T>` implements real `core::fmt::Display` by delegating through the local trait.

## State and Persistence
No state is stored. The module is purely trait and type glue used at compile time and during formatting calls.

## Dependencies and Integration Points
The module is used by `prelude::fmt!` and kernel printing/logging infrastructure. It integrates with `Arc` and `UniqueArc` formatting and is consumed by other modules such as `error.rs` for debug rendering.

## Risks
The adapter is internal; direct use could confuse trait resolution. Missing custom `Display` implementations for foreign types will surface as compile errors in formatting macros. Any divergence from core formatting semantics would affect diagnostic output.

## Test Signals
Doctest formatting of primitives, `Arguments`, references to custom `Display` implementors, and adapter forwarding for debug/hex/binary/pointer traits.
