# sources/cloud-native/stargz-snapshotter/cmd/containerd-stargz-grpc/db/reader.go

Purpose: Implements `metadata.Reader` backed by bbolt. It parses eStargz/zstd metadata once into buckets, then serves filesystem metadata and random file reads.

Important APIs: `NewReader`, `RootID`, `TOCDigest`, `Clone`, `Close`, `GetOffset`, `GetAttr`, `GetChild`, `ForeachChild`, `OpenFile`, `OpenFileWithPreReader`, `NumOfNodes`, and `NumOfChunks`.

Control flow: `NewReader` applies metadata options, tries gzip and configured decompressors, reads the footer, parses/decompresses TOC, creates a reader, and calls `init`. `init` creates a unique filesystem id and root node, copies the decompressed TOC to a temp file while computing TOC digest, then launches background node initialization. Most methods call `waitInit` before viewing bbolt. `initNodes` streams TOC JSON entries, creates or reuses nodes, resolves hardlinks, creates implicit directories, records chunks and stream relationships, then writes sorted metadata and stream addenda.

State and persistence: Persists each reader's metadata under a random `fsID` in shared bbolt. `Close` deletes that filesystem bucket. Runtime state includes section reader, root id, TOC digest, decompressor, and init errgroup.

Dependencies and integration: Implements the DB metadata store selected by `fsopts` and `stargz-store`. Depends on eStargz TOC types, metadata interfaces, bbolt, and `go-json`.

Risks: Initialization has no timeout. Read methods block on background init. Corrupt TOC/DB can surface late. `ReadAt` decompresses from compressed stream offsets and may read up to the next offset, which is correct but potentially costly.

Test signals: `reader_test.go` runs shared metadata, fs reader, and layer suites against this implementation.
