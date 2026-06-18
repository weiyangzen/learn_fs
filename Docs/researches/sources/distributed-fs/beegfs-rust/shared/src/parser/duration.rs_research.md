## sources/distributed-fs/beegfs-rust/shared/src/parser/duration.rs

### Purpose
Parses positive duration values from strings or integer serde inputs for config/CLI use.

### Important APIs, Types, and Functions
- Regex accepts digits plus optional unit among `ns`, `us`, `ms`, `s`, `m`, `h`, and `d`, with optional spaces.
- `parse_optional(input)` returns `Option<Duration>`.
- `parse(input)` returns `anyhow::Result<Duration>` with a descriptive expectation string.
- Serde `Visitor` accepts strings, unsigned seconds, and signed nonnegative seconds.
- `deserialize(de)` invokes `de.deserialize_str(Visitor::default())`.

### Control Flow and State
Parsing trims input, captures number and suffix, converts the number to `u64`, and constructs a `Duration`. Minute/hour/day conversions use `saturating_mul`, so very large valid numbers saturate rather than error after parsing.

### Dependencies and Integration Points
Uses `regex`, `serde`, `anyhow`, `LazyLock`, and `std::time::Duration`. Intended for serde annotations on configuration fields.

### Risks and Edge Cases
`deserialize` calls `deserialize_str`, so despite the visitor implementing numeric visits, some serde formats may not drive numeric values through this function unless they coerce to string. Saturation can hide overflow-like configuration mistakes. Negative values and malformed units fail.

### Test Signals
Unit tests cover plain seconds, whitespace, several units, invalid negative/malformed values, and too-large parse failure for number parsing.
