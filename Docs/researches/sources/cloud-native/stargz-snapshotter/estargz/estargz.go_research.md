# sources/cloud-native/stargz-snapshotter/estargz/estargz.go

Purpose: Core eStargz reader/writer implementation. It opens stargz blobs for random access, verifies TOC/chunk digests, reads file chunks lazily, writes stargz streams, and appends TOC/footer metadata.

Important APIs/types: `Reader`, open options (`WithTOCOffset`, `WithDecompressors`, `WithTelemetry`), `Open`, `OpenFooter`, `TOCDigest`, `VerifyTOC`, `Verifiers`, `ChunkEntryForOffset`, `Lookup`, `OpenFile`, `OpenFileWithPreReader`, `Writer`, `Unpack`, `NewWriter`, `NewWriterLevel`, `NewWriterWithCompressor`, `Writer.Close`, `AppendTar`, `AppendTarLossLess`, and `DiffID`.

Control flow: `Open` selects decompressor candidates, reads the largest footer needed, parses footer/TOC, initializes maps and chunk lists, resolves hardlinks, creates implicit directories, fills uname/gname/modtime/link counts, and computes next offsets. File reads choose the chunk for the requested offset, open a section of compressed data, decompress from the chunk stream, discard to inner/file offset, and optionally pre-read sibling chunks that share a compressed stream. `Writer.appendTar` reads tar or gzip tar, records TOC entries, chunks regular files, computes regular and chunk digests, manages gzip stream boundaries based on chunk and min-chunk rules, and writes TOC/footer on close.

State and persistence: Reader holds the source section reader, TOC, digest, path maps, chunk index, and decompressor. Writer holds buffered/counting writers, compressor, TOC, diff hash, gzip stream, username/group caches, chunk settings, and uncompressed counters.

Dependencies and integration: Used by metadata readers, converters, TOC digest command, and build logic. Depends on compressor/decompressor interfaces from `types.go` and gzip implementations.

Risks: Random reads require decompressing from compressed chunk offsets and can be expensive. `VerifyTOC` requires complete chunk digests unless fallback to regular file digests is safe. Lossless append rejects existing TOC entries. Path normalization collapses absolute/root-relative names.

Test signals: Many tests exist elsewhere; this subset includes build tests, while symbol scan shows dedicated `estargz_test.go` and gzip tests outside this work item.
