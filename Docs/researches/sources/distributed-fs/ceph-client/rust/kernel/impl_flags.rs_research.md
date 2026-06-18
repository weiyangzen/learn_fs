# sources/distributed-fs/ceph-client/rust/kernel/impl_flags.rs

## Purpose
`impl_flags.rs` provides a macro for declaring compact bitflag and individual flag types with standard bitwise operators and containment helpers.

## Important APIs, Types, and Functions
The exported `impl_flags!` macro consumes a tuple-struct bitmask declaration and an enum of individual flags. It generates `#[repr(transparent)]` flag set struct, `#[repr($ty)]` flag enum, conversions to/from the storage type, `BitOr`, `BitAnd`, `BitXor`, `Not`, assignment operators for both set and single-flag operands, `empty`, `all_bits`, `contains`, `contains_any`, and `contains_all`.

## Control Flow
Expansion-time code builds all operators around the underlying integer. XOR and NOT mask with `all_bits()` so inverted/toggled values cannot set bits outside the declared flag set. Individual enum values can be directly combined, producing the bitmask struct.

## State and Persistence
Generated flag values are plain copyable integer wrappers with no runtime global state.

## Dependencies and Integration Points
The macro is used by wrappers such as `gpu/buddy.rs` to expose C flag constants with Rust operator ergonomics. It depends only on core conversion and operator traits.

## Risks
The macro assumes declared enum values are valid, non-conflicting bit masks. `all_bits()` ORs every declared value; multi-bit flags are allowed but can make containment semantics surprising. It does not generate debug formatting unless the caller derives it.

## Test Signals
Macro tests should cover combining individual flags, assignment operators, contains/all/any behavior, XOR and NOT masking, empty masks, conversion to raw storage, and multi-flag use sites such as GPU buddy allocation flags.
