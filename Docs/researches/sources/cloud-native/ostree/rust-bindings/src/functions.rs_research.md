# sources/cloud-native/ostree/rust-bindings/src/functions.rs

## sources/cloud-native/ostree/rust-bindings/src/functions.rs

Handwritten top-level checksum helpers wrapping libostree file checksum APIs. It exposes synchronous `checksum_file`, async callback `checksum_file_async`, future adapter `checksum_file_async_future`, stream-based `checksum_file_from_input`, and directory-fd relative `checksum_file_at`.

Control flow allocates output checksum pointers, calls the corresponding C function, and funnels return/error/output handling through a helper that returns either a `Checksum` or boxed error. Async paths box `FnOnce` callbacks, finish with `ostree_checksum_file_async_finish`, and provide a `gio::GioFuture` facade. State is transient; no persistence is written, though file contents are read from `gio::File`, `InputStream`, or `dfd/path`.

Dependencies include `Checksum`, `ObjectType`, `ChecksumFlags`, `gio`, `glib`, and FFI functions. Risks include correctly handling the C convention where checksum may be null, ensuring callbacks are consumed once, and main-context/cancellable behavior. Tests are mostly indirect through checksum and repo IO paths.
