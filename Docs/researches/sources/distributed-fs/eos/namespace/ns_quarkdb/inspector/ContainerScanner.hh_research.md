## sources/distributed-fs/eos/namespace/ns_quarkdb/inspector/ContainerScanner.hh

Purpose: Declares primitive and enhanced scanners for iterating all container metadata stored in QuarkDB.

Important APIs and types: `ContainerScannerPrimitive` exposes iterator-style `valid()`, `next()`, `hasError()`, `getItem()`, and `getScannedSoFar()`. `ContainerScanner::Item` bundles a `ContainerMdProto`, future full path, future file count, and future container count. `ContainerScanner` exposes the same iterator-style API with optional full-path and count enrichment.

State and integration: the enhanced scanner owns a primitive scanner, a `QClient` reference, option flags, an active-mode item deque, and scan count. It is intended for inspector tooling that may need richer but more expensive metadata per container.

Dependencies: `QClient`, `QLocalityHash`, protobuf metadata, and folly futures.

Risks and test signals: callers must call `next()` after `getItem()` to consume entries. In enriched mode, futures are returned to the caller and must be awaited/handled there. Tests should validate item move behavior, default future values when enrichment is disabled, and buffer refill around the 500-item threshold.
