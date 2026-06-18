## sources/distributed-fs/eos/namespace/ns_quarkdb/inspector/ContainerScanner.cc

Purpose: Implements full-namespace scanning for container metadata, with optional asynchronous full-path resolution and direct child counts.

Important APIs and control flow: `ContainerScannerPrimitive` iterates the `eos-container-md` locality hash, deserializes each value into `ContainerMdProto`, tracks scanned count, and records deserialization errors. `ContainerScanner` wraps the primitive. When neither full paths nor counts are requested, it delegates directly. When active, `ensureItemDequeFull()` fills a deque up to 500 items, starting `MetadataFetcher::resolveFullPath()` and/or `countContents()` futures for each proto. `getItem()` returns the front proto and optionally moves the buffered `Item` with pending futures to the caller.

State and persistence: scanning is read-only over QuarkDB locality hashes. Buffered mode separates backend scan progress from caller consumption and tracks its own `mScanned` count.

Dependencies and integration: depends on `QLocalityHash`, namespace serialization, `MetadataFetcher`, folly futures, and container protobufs. Inspector commands can combine this scanner with output sinks and consistency checks.

Risks and test signals: `hasError()` in active mode returns `!mItemDeque.empty() && mScanner.hasError(err)`, which can hide scanner errors after the buffer drains. Futures may resolve after item retrieval and can carry metadata lookup errors. Tests should cover deserialization failures, direct vs buffered modes, count futures, path futures, scan-count semantics, and error reporting at end of scan.
