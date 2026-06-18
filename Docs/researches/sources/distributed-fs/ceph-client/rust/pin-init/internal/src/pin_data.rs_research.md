# sources/distributed-fs/ceph-client/rust/pin-init/internal/src/pin_data.rs

## Purpose
`pin_data.rs` implements the `#[pin_data]` attribute. It marks structurally pinned fields, generates projection types and pin-data metadata used by `pin_init!`, controls `Unpin` derivation, and enforces pinned-drop discipline.

## Important APIs, Types, And Functions
`Args` parses optional `PinnedDrop`. `pin_data(args, input, dcx)` is the main expansion. Helpers include `is_phantom_pinned`, `generate_unpin_impl`, `generate_drop_impl`, `generate_projections`, `generate_the_pin_data`, `SelfReplacer`, and `collect_tuple`. Generated artifacts include `<Struct>Projection`, `project()`, `__ThePinData`, `HasPinData` and `PinData` impls, field initializer/projection functions, and drop/Unpin guard impls.

## Control Flow
The macro accepts structs only. It replaces `Self` in generics and fields with the concrete struct path, strips `#[pin]` field attributes while recording which fields were pinned, warns when a `PhantomPinned` field lacks `#[pin]`, then emits the original struct plus helper items inside a private const. For `Unpin`, it creates an internal `__Unpin` type containing only pinned fields and implements `Unpin` for the original type when that helper is `Unpin`. For drop, it either delegates `Drop` to `PinnedDrop` or creates conflicting traits that prevent normal `Drop` or forgotten `PinnedDrop` declarations.

## State And Persistence
Generated metadata is compile-time type state. At runtime, projection methods create `Pin<&mut Field>` for pinned fields and `&mut Field` for unpinned fields. The generated drop impl is persistent code for the type when `PinnedDrop` is requested.

## Dependencies And Integration Points
It depends on `syn` parsing/visiting, `quote`, `DiagCtxt`, and public `pin_init` traits. The initializer macro uses generated `__ThePinData` methods to ensure pinned fields receive `PinInit` and unpinned fields receive `Init`.

## Risks And Edge Cases
Only named-field structs are supported by generated projection code. `SelfReplacer` must avoid descending into nested items where `Self` changes meaning. Drop-prevention uses trait conflicts, so diagnostics may be compiler-generated but intentional. Forgetting `PinnedDrop` in the attribute or adding `Drop` directly is rejected by design. Unsafe projection correctness depends on the structurally pinned field list matching the user's `#[pin]` attributes.

## Test Signals
Trybuild tests should cover pinned and unpinned fields, generic bounds containing `Self`, tuple/enum/union rejection, `PhantomPinned` warnings/errors, `Unpin` behavior, projection types, direct `Drop` rejection, `PinnedDrop` delegation, and initializer enforcement for pinned fields.
