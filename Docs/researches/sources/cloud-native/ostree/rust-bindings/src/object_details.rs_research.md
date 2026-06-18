# sources/cloud-native/ostree/rust-bindings/src/object_details.rs

## sources/cloud-native/ostree/rust-bindings/src/object_details.rs

Handwritten representation for metadata returned by repo object-listing APIs. `ObjectDetails` stores whether an object is loose and the pack/checksum list where it appears, with constructors/parsers from GLib variants and a `Display` implementation.

Control flow decodes a variant emitted by libostree's object listing into Rust fields. State is read-only metadata; persistence is the underlying repository object store. Integration is with `repo.rs` `list_objects`, which returns `HashMap<ObjectName, ObjectDetails>`.

Dependencies are GLib variant extraction and formatting traits. Risks include variant-shape mismatch and lossy interpretation if libostree changes object-list detail layout. Tests are not local in this file; behavior is exercised by repo object listing consumers.
