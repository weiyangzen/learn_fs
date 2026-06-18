## sources/cloud-native/composefs-rs/crates/composefs-oci/src/layer.rs

Purpose: this module contains shared async layer import helpers for OCI image paths. It normalizes media type handling, decompression, tar splitstream import, and raw blob storage.

Important APIs: `is_tar_media_type` identifies supported tar layer media types, including gzip/zstd and non-distributable variants. `decompress_async` wraps an async reader in the appropriate decoder or buffered reader. `import_tar_async` imports an already-decompressed tar stream into a repository splitstream using the OCI tar layer content type. `store_blob_async` writes arbitrary raw bytes to a repository object and finalizes it.

Control flow: `decompress_async` first wraps the input in a `BufReader`, then returns a boxed `AsyncRead` using no decompressor for plain layers, `GzipDecoder` for gzip layers, `ZstdDecoder` for zstd layers, or an error for unsupported media. `import_tar_async` delegates to `tar::split_async` with the repository and `TAR_LAYER_CONTENT_TYPE`. `store_blob_async` creates a repository temp object fd, converts it to a Tokio file, streams all bytes with `tokio::io::copy`, flushes, converts back to std, and calls `finalize_object_tmpfile`.

State and persistence: tar import persists a splitstream and any external objects created by `split_async`; raw blob storage persists a single repository object and returns its object ID, byte size, and storage method. The module itself has no cache.

Dependencies and integration: depends on `async-compression`, `tokio`, `containers-image-proxy` media types, composefs repository APIs, shared IO buffer capacity, and `crate::tar`. It is used by OCI layout, skopeo, and delta paths to keep layer import behavior consistent.

Risks: callers must pass decompressed streams to `import_tar_async`; passing compressed data there would create invalid splitstreams. `decompress_async` boxes readers with lifetimes tied to the input, so caller ownership must remain correct. Unsupported media types are rejected here unless higher-level code stores them as non-tar blobs through `store_blob_async`.

Test signals: this module has no local tests in the file. Coverage is indirect through OCI layout/pull/delta tests and tar round-trip tests that import layers and then read back entries or compose filesystems.
