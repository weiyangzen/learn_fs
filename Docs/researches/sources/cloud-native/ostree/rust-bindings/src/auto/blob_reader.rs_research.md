# sources/cloud-native/ostree/rust-bindings/src/auto/blob_reader.rs

Purpose: Generated wrapper for the `OstreeBlobReader` interface, exposing blob-reading capability to Rust implementors and users.

Important APIs: `BlobReader` is a `glib::wrapper!` interface with `BlobReader::NONE` and extension trait `BlobReaderExt`. Under feature `v2016_5`, `read_blob` returns `Result<Option<glib::Bytes>, glib::Error>` from `ostree_blob_reader_read_blob`.

Control flow and state: The wrapper performs a synchronous FFI call with optional `gio::Cancellable`, converts GLib errors into `Result`, and converts nullable bytes into `Option`.

Dependencies and integration points: Depends on GLib object/interface mechanics, Gio cancellables, and libostree blob reader implementations. It can be used wherever libostree exposes objects implementing this interface.

Risks: A nullable successful result is represented as `Ok(None)`, so callers must not assume bytes are always returned. Interface implementor behavior is outside this wrapper. Feature gating means code must enable `v2016_5` for the actual read method.

Test signals: Feature-gated compile tests and an integration object implementing/providing `BlobReader` should verify bytes and cancellation/error paths.
