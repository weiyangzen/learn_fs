## sources/distributed-fs/beegfs-rust/shared/src/parser/integer_range.rs

### Purpose
Parses a single positive integer or inclusive integer range from strings for serde config/CLI fields.

### Important APIs, Types, and Functions
- Regex accepts `lower` or `lower-upper` with optional spaces around `-`.
- `parse_optional<T>` returns `Option<RangeInclusive<T>>` for `T: FromStr + Copy + Ord`.
- `parse<T>` returns `anyhow::Result<RangeInclusive<T>>`.
- Generic serde `Visitor<T>` parses string input.
- `deserialize` exposes the serde hook.

### Control Flow and State
The parser captures the lower bound and optional upper bound. If no upper bound is present, it returns `lower..=lower`. If `upper < lower`, parsing fails. No persistent state exists.

### Dependencies and Integration Points
Uses `regex`, `serde`, `anyhow`, `RangeInclusive`, and generic `FromStr`. Useful for numeric config ranges.

### Risks and Edge Cases
The regex accepts only unsigned decimal syntax, so signed numeric types cannot parse negative ranges. It does not support open-ended ranges. `deserialize` uses string deserialization only. Type-specific overflow is handled by `FromStr` failure.

### Test Signals
Unit tests cover single values, whitespace, valid ranges, invalid strings, missing upper bounds, negative syntax, descending ranges, and empty input.
