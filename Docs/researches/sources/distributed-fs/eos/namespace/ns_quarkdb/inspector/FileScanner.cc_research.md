## sources/distributed-fs/eos/namespace/ns_quarkdb/inspector/FileScanner.cc

Purpose: Implements full-namespace scanning for file metadata, with optional asynchronous parent-path resolution.

Important APIs and control flow: `FileScannerPrimitive` iterates `eos-file-md` through `QLocalityHash`, deserializes each value into `FileMdProto`, tracks scanned count, and stores deserialization error text. `FileScanner` wraps it. In direct mode it delegates calls to the primitive. In full-path mode, `ensureItemDequeFull()` prefetches up to 500 file protos and starts a `MetadataFetcher::resolveFullPath()` future for each file's container ID. `getItem()` returns the proto and optionally moves the buffered `Item` containing the future path.

State and persistence: read-only scan over QuarkDB metadata. Buffered mode has separate primitive progress and public `mScanned` consumption count.

Dependencies and integration: used by inspector commands and consistency checks that need to scan every file. Depends on `Serialization`, `MetadataFetcher`, `QLocalityHash`, `FileMdProto`, and folly futures.

Risks and test signals: active-mode `hasError()` has the same buffer-dependent behavior as `ContainerScanner`, potentially hiding errors after the deque is empty. Full path future resolves only the parent container path; consumers need to append or format the file name as appropriate. Tests should cover invalid serialized records, direct/buffered count differences, full-path future errors, item move semantics, and buffer refill.
