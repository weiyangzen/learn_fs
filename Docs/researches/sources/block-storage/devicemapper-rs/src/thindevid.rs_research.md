# File Research: sources/block-storage/devicemapper-rs/src/thindevid.rs

## Purpose
Defines `ThinDevId`, the 24-bit identifier used by dm-thin pools.

## Key APIs
`ThinDevId::new_u64`, `From<ThinDevId> for u32`, `Display`, `FromStr`, serde serialize/deserialize.

## Behavior
`new_u64` accepts values below `2^24` and rejects larger values with `DmError::Dm(ErrorEnum::Invalid, ...)`. Parsing uses shared `parse_value`.

## Notes
Serde deserialization currently wraps the deserialized `u32` directly and does not re-check the 24-bit limit.
