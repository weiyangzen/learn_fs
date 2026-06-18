# sources/cloud-native/ostree/rust-bindings/src/auto/commit_sizes_entry.rs

Purpose: Generated boxed wrapper for `OstreeCommitSizesEntry`, representing object size metadata for a commit.

Important APIs: `CommitSizesEntry::new(checksum, objtype, unpacked, archived)` returns `Option<CommitSizesEntry>` and stores checksum, `ObjectType`, unpacked size, and archived size in the underlying C struct.

Control flow and state: The wrapper uses libostree copy/free functions for boxed ownership. Construction may return null, represented as `None`, if libostree rejects inputs.

Dependencies and integration points: Feature-gated by `v2020_1`. Used by `functions::commit_get_object_sizes`, which returns vectors of these entries from commit metadata.

Risks: There are no field accessors in this generated file, so usefulness depends on derived traits and other generated/manual APIs. Caller-provided checksum/object type must be valid. Size units and semantics are inherited from libostree.

Test signals: Construct entries with valid checksums/object types, compile `commit_get_object_sizes` under `v2020_1`, and verify vector conversion does not leak or double free.
