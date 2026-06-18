# sources/cloud-native/ostree/rust-bindings/src/tests/collection_ref.rs

## sources/cloud-native/ostree/rust-bindings/src/tests/collection_ref.rs

Unit tests for `CollectionRef` equality, hashing, optional collection IDs, and cloning. The tests are gated on `v2018_6`, matching collection-ref API availability.

Control flow creates `CollectionRef` values with the same and different collection/ref components, hashes them with `DefaultHasher`, and asserts equality or inequality. There is no persistence or external IO. Dependencies are `CollectionRef`, `Hash`, and `Hasher`.

The test signals protect value semantics used by repo collection-ref resolution and remote discovery. They reduce risk that generated boxed equality/hash behavior changes silently, especially for absent collection IDs.
