# sources/cloud-native/soci-snapshotter/soci/util_test.go

Purpose: this file provides test doubles and helpers for SOCI index tests.

Important APIs and types: `parseDigest` parses digest strings while ignoring errors for concise test fixtures. `OrasMemoryStore` adapts `oras-go` memory store to the SOCI `store.Store` interface by adding no-op `BatchOpen`, `Label`, and `Delete`. `fakeContentStore` implements containerd `content.Store` enough for selected tests. `fakeReaderAt` returns a configured size and synthetic read count. `fakeWriter` implements `content.Writer` with no-op writes and optional commit function.

Control flow: tests call `newFakeContentStore` to satisfy builder dependencies without containerd. `ReaderAt` returns a fake reader sized from descriptor size; `Writer` returns a fake writer; unsupported methods panic to reveal accidental use. `NewOrasMemoryStore` wraps a fresh memory store for blob operations.

State and persistence: all state is in memory. The fake content store does not persist bytes; fake reader content is zeros/implicit and only size-aware.

Dependencies and integration points: these helpers support `soci_index_test.go` and potentially conversion tests by satisfying `content.Store` and `store.Store`.

Risks: ignored digest parse errors can hide invalid fixture digests. `fakeReaderAt.ReadAt` returns `int(r.size)` regardless of buffer length, which is not a faithful `ReaderAt` implementation and can mask read semantics. Several `content.Store` methods panic, so helpers are only safe for narrow unit paths. No-op labels mean GC-label code cannot be validated with these helpers.

Test signals: as a support file, its quality determines how much confidence SOCI builder tests provide; it is useful for isolated helper tests but not a substitute for integration content-store tests.
