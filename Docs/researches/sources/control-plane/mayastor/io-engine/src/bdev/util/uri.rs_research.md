## sources/control-plane/mayastor/io-engine/src/bdev/util/uri.rs

### Purpose
`bdev/util/uri.rs` provides small URI query/path parsing helpers reused across bdev adapters.

### Important APIs, Types, And Functions
`segments(&Url)` returns normalized path segments with a lone empty segment removed. `boolean(value, empty)` parses yes/on/no/off, numeric booleans, Rust bool strings, and empty values. `uuid(value)` parses an optional UUID string.

### Control Flow
`segments()` delegates to `Url::path_segments()` and normalizes `/` to an empty vector. `boolean()` first handles empty strings, custom yes/no tokens, numeric strings where any nonzero value is true, then falls back to `str::parse::<bool>()`. `uuid()` maps optional strings through `uuid::Uuid::parse_str()` using `transpose()`.

### State, Persistence, And Dependencies
No state or persistence. Dependencies are `url`, `uuid`, and `ParseBoolError`.

### Integration Points
`null_bdev`, `nvmf`, `nvmx::uri`, `nx`, `uring`, and other URI adapters use these helpers for consistent query parsing and error context.

### Risks
Numeric booleans accept any `u32`, so `2` is true. Empty values map to the caller-provided default, which can differ by parameter. `segments()` does not percent-decode beyond what `url` returns in path segment iteration.

### Test Signals
Cover empty path, root path, multiple path segments, yes/on/no/off, true/false, numeric zero/nonzero, invalid boolean strings, empty boolean defaults, valid/invalid UUID, and `None` UUID.
