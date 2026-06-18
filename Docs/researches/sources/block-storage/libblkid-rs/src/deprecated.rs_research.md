# File Research: sources/block-storage/libblkid-rs/src/deprecated.rs

Purpose: Adds deprecated libblkid filter methods onto `BlkidProbe` behind the crate’s `deprecated` feature.

Key APIs:
- `filter_usage`
- `filter_types`
- `invert_filter`
- `reset_filter`

Implementation notes:
- Mirrors old libblkid APIs and routes errors through `errno!`.
- Converts `&[&str]` into a null-terminated C pointer array for type filters.

Notable risks:
- The string-list conversion is duplicated from newer probe filter methods.
- Any `CString::new` failure is collapsed to `InvalidConv`, losing the original nul-byte location.
- Deprecated methods remain public when the feature is enabled, so behavior should stay aligned with libblkid compatibility expectations.
