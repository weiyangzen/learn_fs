# sources/cloud-native/ostree/rust-bindings/src/tests/mod.rs

## sources/cloud-native/ostree/rust-bindings/src/tests/mod.rs

Test module aggregator for the Rust bindings crate. It includes `collection_ref`, `kernel_args`, and `repo`.

There is no runtime control flow beyond Rust test discovery. State and persistence are absent. The integration point is `lib.rs`, which includes this module under `#[cfg(test)]`.

The file's risk is organizational: tests omitted here will not run as part of the crate test module. It currently wires the subset of handwritten behavior covered by local unit tests.
