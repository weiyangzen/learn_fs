## sources/distributed-fs/eos/namespace/ns_quarkdb/inspector/FileScanner.hh

Purpose: Declares primitive and enhanced scanners for iterating all file metadata stored in QuarkDB.

Important APIs and types: `FileScannerPrimitive` offers iterator-style validity, advance, error, item, and scan-count methods. `FileScanner::Item` contains a file proto and future full path. `FileScanner` exposes the same iterator interface, adding optional path prefetching.

State and integration: the enhanced scanner keeps the primitive scanner, backend client reference, full-path flag, active flag, deque of prefetched items, and consumption count. It is a reusable utility under inspector code.

Dependencies: `QClient`, `QLocalityHash`, file metadata protobufs, and folly futures.

Risks and test signals: in non-active mode, the optional `Item*` argument to `getItem()` is ignored because the primitive only returns the proto. Callers requiring full path must instantiate with `fullPaths=true`. Tests should verify direct-mode behavior, active-mode default item futures, and that `valid()` reflects the deque rather than primitive validity when buffering.
