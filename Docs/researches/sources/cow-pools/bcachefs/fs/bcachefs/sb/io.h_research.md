# File Research: sources/cow-pools/bcachefs/fs/bcachefs/sb/io.h

This header exposes superblock IO, field, version, magic, and rendering APIs.

Key elements:
- Defines the superblock readback scratch buffer size.
- Provides version compatibility and incompatible-feature request helpers.
- Defines typed superblock field get/resize/minsize/delete helpers.
- Defines `struct bch_sb_field_ops` for field validation/rendering dispatch.
- Provides filesystem-specific journal and bset magic derivation from UUID.
- Declares superblock copy, allocation, validation, read, silent read, write, feature, upgrade/downgrade, and text-rendering functions.

Important invariant:
- `bch2_request_incompat_feature()` is a fast-path check against `c->sb.version_incompat`; only unsupported requests call the slower superblock-updating path.
