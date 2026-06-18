## sources/distributed-fs/beegfs-rust/shared/src/parser/integer_unit.rs

### Purpose
Parses unsigned integers with optional SI or IEC unit prefixes from config/CLI strings.

### Important APIs, Types, and Functions
- Regex accepts a positive integer, optional prefix among `k`, `M`, `G`, `T`, `P`, `E` with optional `i`, and arbitrary alphabetic unit suffix.
- `parse_optional(input)` returns `Option<u64>`.
- `parse(input)` returns `anyhow::Result<u64>`.
- Serde `Visitor` accepts string, unsigned integer, and nonnegative signed integer inputs.
- `deserialize(de)` invokes string deserialization.

### Control Flow and State
Parsing trims input, extracts the number and prefix, parses `u64`, multiplies by base-10 or base-2 factor, and returns the result. Multiplication is saturating.

### Dependencies and Integration Points
Uses `regex`, `serde`, `anyhow`, and `LazyLock`. Used for byte/count-like configuration values where unit labels are syntactic convenience and the trailing unit word is ignored.

### Risks and Edge Cases
Saturating multiplication may silently turn too-large values into `u64::MAX`. Lowercase `m` is not megascale because only uppercase `M` is accepted. Arbitrary alphabetic trailing units are ignored, so typos after a valid prefix can still parse. `deserialize` uses string deserialization, so numeric visitor methods may not be used by all deserializers.

### Test Signals
Unit tests cover base values, SI prefixes, IEC prefixes, whitespace, invalid missing numbers, invalid `i` suffix alone, negative values, garbage, and empty strings.
