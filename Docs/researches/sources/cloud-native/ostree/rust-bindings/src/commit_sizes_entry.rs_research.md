# sources/cloud-native/ostree/rust-bindings/src/commit_sizes_entry.rs

## sources/cloud-native/ostree/rust-bindings/src/commit_sizes_entry.rs

Handwritten convenience accessors for generated `CommitSizesEntry`. It exposes `checksum`, `objtype`, `unpacked`, and `archived`, reading fields directly from `OstreeCommitSizesEntry`.

Control flow borrows the raw struct pointer with `ToGlibPtr`, then converts the checksum C string and object-type enum while returning numeric size fields. There is no persistence; the type represents size metadata usually produced by libostree commit-size calculations.

Dependencies are `auto::CommitSizesEntry`, `auto::ObjectType`, `ffi`, and GLib conversion traits. Risks are low but tied to C layout compatibility. Tests instantiate an entry and verify all accessor values.
