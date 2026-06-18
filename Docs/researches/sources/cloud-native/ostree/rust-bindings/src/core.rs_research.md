# sources/cloud-native/ostree/rust-bindings/src/core.rs

## sources/cloud-native/ostree/rust-bindings/src/core.rs

Handwritten type aliases and parsing helpers for OSTree core variant formats. It defines `CommitVariantType`, `TreeVariantType`, `DirmetaVariantType`, and `DirMetaParsed`.

The important function is `DirMetaParsed::from_variant`, which tries to decode a GLib variant as `(uuua(ayay))`, then converts UID, GID, and mode from big-endian to host order while retaining xattrs. State is purely decoded data; persistence remains in libostree object variants stored in the repository.

Dependencies are `glib::Variant` and `VariantDict`. Integration points include `Repo::read_dirmeta`, metadata object loading, and callers that parse commit/tree variants. Risks are variant-shape mismatches and endianness mistakes; the explicit `try_get` result helps surface wrong types. There are no local tests in this file, but `Repo::read_dirmeta` relies on it.
