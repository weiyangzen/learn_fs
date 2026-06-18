## sources/distributed-fs/beegfs-rust/shared/src/impl_macros.rs

### Purpose
Defines internal convenience macros for enum conversions, user-facing enum strings, and optional protobuf conversions.

### Important APIs, Types, and Functions
- `impl_enum_bee_msg_traits!` implements `BeeSerdeConversion` for a target enum across integer types `u8`, `u16`, `i16`, `u32`, `i32`, `u64`, `i64`, `usize`, and `isize`.
- `impl_enum_user_str!` adds `user_str()` and `Display` for enum variants.
- `impl_enum_protobuf_traits!` is compiled with feature `grpc` and implements `TryFrom<proto>` plus `From<domain>` and `into_proto_i32`.

### Control Flow and State
Macros expand at compile time. Runtime behavior is simple matching: valid numeric/protobuf values map to enum variants and unknown values return anyhow errors.

### Dependencies and Integration Points
Used heavily by `types.rs`, target/buddy/quota message enums, and gRPC conversion code. Requires `crate::bee_serde::BeeSerdeConversion`, `anyhow`, and optional generated protobuf modules in call sites.

### Risks and Edge Cases
The macro implements many integer conversions, so accidental use of the wrong raw width may compile even when wire definitions require a narrower type. `impl_enum_protobuf_traits!` treats the protobuf unspecified variant as an error on inbound conversion, which is generally correct but must match API semantics. Duplicate numeric values would compile into unreachable or conflicting match arms depending on expansion.

### Test Signals
No direct tests. Enum round-trip tests in message/type modules would exercise expansions. Compile tests are useful for protobuf feature builds.
