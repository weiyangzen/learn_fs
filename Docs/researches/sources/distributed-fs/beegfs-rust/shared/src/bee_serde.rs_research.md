## sources/distributed-fs/beegfs-rust/shared/src/bee_serde.rs

### Purpose
Implements the core BeeGFS serialization/deserialization framework used for network messages and some on-disk data. It provides primitive encoding, C-string handling, sequence/map layouts, derive-macro helper traits, and enum conversion support.

### Important APIs, Types, and Functions
- `Serializable` and `Deserializable` are the central traits implemented by protocol types.
- `Serializer` writes little-endian primitives into a fixed mutable slice and tracks `write_pos`; it also carries a `bee_msg::Header` for message-specific metadata.
- `Deserializer` reads from a source slice and carries a borrowed or owned `Header` for conditional deserialization.
- `Serializer::bytes`, `cstr`, `seq`, `map`, `zeroes`, and `bytes_written` implement BeeGFS wire primitives.
- `Deserializer::bytes`, `cstr`, `seq`, `map`, `skip`, `finish`, and `take` mirror the read side with bounds checks.
- `BeeSerdeConversion<S>` converts enums and other values to/from raw BeeGFS integer encodings.
- `BeeSerdeHelper<In>` plus helpers `Int`, `Seq`, `Map`, and `CStr` drive the `#[derive(BeeSerde)]` field annotations.
- Primitive integer types implement both serialization traits.

### Control Flow and State
Serialization writes fields sequentially into a caller-owned buffer. Sequence and map serialization reserve count/size placeholders, serialize elements, then patch the placeholders in-place. Deserialization advances the source slice by splitting off consumed bytes; `finish` reports trailing bytes. No persistent state exists beyond each serializer/deserializer instance.

### Dependencies and Integration Points
Coupled to `bee_msg::Header` because some BeeGFS messages depend on header metadata. Uses `anyhow` for error propagation, `Cow` for header ownership, and `HashMap` for map deserialization. All `bee_msg` modules, `conn` send/receive paths, and derive macros depend on this file.

### Risks and Edge Cases
`seq` and `map` trust decoded length values enough to `try_reserve`, so malformed inputs can request large allocations before element reads fail. `cstr` writes length as `u32` using `v.len() as u32`; extremely large inputs would truncate before buffer writes fail. Included sequence total size is skipped but not validated on decode. Arithmetic like `self.write_pos + v.len()` in `bytes` can overflow for pathological values, although normal fixed buffers make this unlikely. Header coupling keeps the generic serializer less reusable.

### Test Signals
Includes unit tests for primitive round-trips, byte blocks, C-string alignment, nested collections, and buffer-length errors. Additional hardening tests should cover malicious sequence lengths, invalid C-string terminators, and mismatched included total sizes.
