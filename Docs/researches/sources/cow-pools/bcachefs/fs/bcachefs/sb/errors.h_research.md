# File Research: sources/cow-pools/bcachefs/fs/bcachefs/sb/errors.h

This header exposes persistent error-counting APIs.

Key elements:
- Exports error string table and ID-to-text renderer.
- Declares filesystem error text rendering.
- Exports `bch_sb_field_ops_errors`.
- Declares increment, serialize, and load functions for superblock error counts.
- Includes `errors_types.h` for the in-memory darray type.
