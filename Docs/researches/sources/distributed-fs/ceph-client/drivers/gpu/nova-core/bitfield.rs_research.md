# sources/distributed-fs/ceph-client/drivers/gpu/nova-core/bitfield.rs

## Purpose

`bitfield.rs` defines the `bitfield!` macro used by Nova register and ABI wrappers to create transparent integer newtypes with typed accessors, builder-style setters, `Debug`, and `Default` implementations.

## Important APIs, Types, And Functions

The macro accepts `vis struct Name(storage) { hi:lo field as type [=> Into] [?=> TryInto]; }`. It generates `#[repr(transparent)]` structs, `From<Name> for storage`, field constants for masks/shifts/ranges, getters, `set_` setters, `Debug`, and default initialization through field defaults. It uses `kernel::bits::genmask_u8/u16/u32/u64`, `kernel::build_assert!`, and `kernel::macros::paste!`.

## Control Flow

Expansion dispatches from the public rule into core struct definition, field collection, bounds checks, accessor generation, then debug/default generation. Getter flow masks and shifts the stored integer, then optionally casts, converts with `From`, or converts with `TryFrom`. Setter flow converts the typed value into the primitive field type, shifts, masks, clears the old field, and writes the new field bits.

## State And Persistence Behavior

Generated bitfield values are copyable transparent wrappers around integer storage. Setters are pure value transformers that return updated `Self`; no external state is persisted. Generated default values depend on each field's `Default` conversion path rather than raw zero alone.

## Dependencies And Integration Points

It is foundational for `regs.rs`, GSP ABI wrappers, and hardware register programming across Nova. It depends on Rust macro expansion, kernel formatting, kernel bit helpers, build-time assertions, and typed conversion traits.

## Risks And Test Signals

Risks include unchecked values being silently masked in setters, bool fields requiring one-bit ranges, storage sizes outside 1/2/4/8 bytes causing build errors, default generation failing for fields whose converted type lacks `Default`, and try-getters surfacing hardware-reserved values. Test with compile-fail coverage for invalid ranges, runtime/unit checks for masks and shifts, debug output, default values, and register wrapper build coverage across all generated bindings.
