# sources/cloud-native/ostree/rust-bindings/src/auto/sign.rs

## sources/cloud-native/ostree/rust-bindings/src/auto/sign.rs

Generated interface binding for `OstreeSign`. Static helpers expose `Sign::NONE`, `all`, and `by_name`; the `SignExt` trait provides operations for public-key management, commit signing and verification, arbitrary data signing and verification, metadata format lookup, name lookup, and newer blob-reader/data APIs behind feature gates.

Control flow is pure interface dispatch into libostree with GError conversion. State is held by concrete sign implementations and their configured keys; persistence may occur inside the implementation or through repo commit metadata, but this wrapper only calls the interface. Integration points include `Repo`, `glib::Bytes`, `glib::Variant`, `BlobReader`, and static delta/signature APIs in `Repo`.

Risks are security-sensitive: key loading, signature validation semantics, and optional success messages are delegated to backends; users must choose the correct backend and trust model. Feature gates matter because signature APIs evolved over libostree releases. No local tests are present.
