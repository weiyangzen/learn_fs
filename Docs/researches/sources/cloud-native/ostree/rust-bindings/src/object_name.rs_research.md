# sources/cloud-native/ostree/rust-bindings/src/object_name.rs

## sources/cloud-native/ostree/rust-bindings/src/object_name.rs

Handwritten object-name wrapper around an OSTree checksum plus `ObjectType`. It provides constructors from checksum/type or from serialized variants, serialization/deserialization helpers through crate functions, `Display` via `object_to_string`, and custom `Hash`/`PartialEq` using libostree's variant hash/equality.

Control flow stores checksum as `GString` and object type as an enum, while conversions to/from `glib::Variant` preserve libostree's canonical object-name representation. State is value-level only; persistence occurs when object names index repo contents or traversal results.

Dependencies include `ObjectType`, generated object serialization functions, `glib::Variant`, and Rust hashing/display traits. Risks are canonicalization and hash/equality alignment with C semantics. Local tests cover equality, display/serialization, and hash behavior for object names.
