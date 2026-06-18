# sources/cloud-native/ostree/rust-bindings/src/collection_ref.rs

## sources/cloud-native/ostree/rust-bindings/src/collection_ref.rs

Handwritten accessors for generated `CollectionRef` internals. `collection_id` returns `Option<&CStr>` because the underlying pointer can be null and bytes may not be valid UTF-8; `ref_name` returns `&CStr` for the required ref field.

Control flow obtains the raw `OstreeCollectionRef` pointer via `ToGlibPtr`, checks null collection IDs with a small `AsNonnullPtr` helper, and borrows C strings without copying. There is no persistence; this is read-only access to a boxed/ref-counted libostree struct used by collection-ref resolution and remote discovery.

Dependencies are the generated `CollectionRef`, `ffi`, GLib translation, and `CStr`. Risks include borrowed lifetime correctness and caller conversion from `CStr` to UTF-8. Local unit tests cover present/absent collection IDs and ref-name retrieval.
