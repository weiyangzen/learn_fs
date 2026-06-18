<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/utils/src/types.rs -->
## sources/cloud-native/nydus/utils/src/types.rs

### Purpose
This small Unix-specific utility module defines byte-size measurement for OS-native string/path values, avoiding confusion between character counts and filesystem byte representation.

### APIs, Types, and Control Flow
`ByteSize` exposes `byte_size(&self) -> usize`. Implementations for `OsString` and `OsStr` call Unix `OsStrExt::as_bytes().len()`. The `PathBuf` implementation delegates to `as_os_str().byte_size()`.

### State, Dependencies, and Integration
There is no runtime state or persistence. The module depends on `std::os::unix::ffi::OsStrExt`, making behavior explicitly Unix byte-oriented. It integrates with path validation, archive metadata sizing, or filesystem serialization code that needs byte lengths rather than Unicode scalar or display lengths.

### Risks and Test Signals
This trait is not portable to non-Unix targets as written. Consumers should not assume `PathBuf::byte_size()` includes a trailing separator; it measures the actual path buffer. Tests cover empty strings, ASCII strings, and incremental `PathBuf` construction through `/test/a`.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/utils/src/types.rs -->
