# sources/distributed-fs/ceph-client/rust/pin-init/internal/src/init.rs

## Purpose
`init.rs` implements the `init!` and `pin_init!` procedural macros. It parses struct-initializer-like syntax and emits closure-based `Init` or `PinInit` objects that initialize fields in place, enforce field coverage/alignment at compile time, and clean up partially initialized fields on error.

## Important APIs, Types, And Functions
`Initializer` is the parsed macro input, with optional attributes, optional `&this in`, target path, fields, optional `..Zeroable::init_zeroed()`, and optional `? ErrorType`. `InitializerField` supports value fields (`field: expr` or shorthand), in-place fields (`field <- init`), and code blocks (`_: { ... }`). `expand(...)` is the generator. `get_init_kind`, `init_fields`, and `make_field_check` implement zeroing detection, field writes/drop guards, and compile-time checks.

## Control Flow
Expansion selects pinned or unpinned data traits, resolves the error type from explicit `?`, `#[default_error(...)]`, or a default. It obtains field metadata through `HasPinData` or `HasInitData`, optionally zeroes the whole slot if the rest expression is exactly `Zeroable::init_zeroed()`, creates a `this` `NonNull` if requested, emits initialization statements for each field, creates `DropGuard`s after each initialized field, exposes local references for later field initializers, performs unreachable compile-time field/alignment checks, forgets guards on success, and returns a closure converted through `pin_init_from_closure` or `init_from_closure`.

## State And Persistence
Generated initializers are one-shot closures. During initialization, state consists of the destination slot, per-field drop guards, local field bindings, and optional zeroed memory. If a later field initializer returns `Err` or panics after earlier fields initialized, active guards drop those fields; on success guards are forgotten and ownership transfers to the fully initialized object.

## Dependencies And Integration Points
It depends on `pin-init` runtime traits and internal tokens: `HasPinData`, `PinData`, `HasInitData`, `InitData`, `DropGuard`, `InitOk`, `Zeroable`, and initializer constructors. It is invoked by `pin-init/internal/src/lib.rs` for both `init` and `pin_init`.

## Risks And Edge Cases
The macro's safety hinges on never creating references to uninitialized or unaligned data. `make_field_check` uses unreachable code to let the compiler catch missing/duplicate fields and unaligned field references. Only the exact rest syntax `..Zeroable::init_zeroed()` is accepted. Cfg attributes on fields are preserved for initialization and guard forgetting. The `InitOk` token prevents user code from returning success without passing through macro-generated field checks.

## Test Signals
Trybuild coverage should include successful value and in-place fields, missing and duplicate fields, unaligned packed fields, zeroing trailer, custom error types, `&this in` self-references, cfg-gated fields, failure cleanup order, and pinned-field type enforcement.
