# File Research: sources/block-storage/libblkid-rs/src/version.rs

Purpose: Exposes libblkid version parsing and runtime library version lookup.

Key APIs:
- `parse_version_string`
- `get_library_version`

Implementation notes:
- Converts input version strings to `CString`.
- Reads version and release-date pointers returned by `blkid_get_library_version`.

Notable risks:
- `get_library_version` does not null-check returned version/date pointers before calling `CStr::from_ptr`.
- `parse_version_string` returns the raw integer result and does not classify invalid or sentinel values.
