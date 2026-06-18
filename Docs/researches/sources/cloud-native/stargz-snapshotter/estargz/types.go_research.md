## sources/cloud-native/stargz-snapshotter/estargz/types.go

Purpose: declares the core eStargz data model, public constants/annotations, TOC entry structure, file info adapter, verification interface, and pluggable compression contracts.

Important APIs/types/functions: constants define `TOCTarName`, modern and legacy footer sizes, OCI/container annotations for TOC digest and uncompressed size, and prefetch/no-prefetch landmark names. `JTOC` is the JSON table of contents. `TOCEntry` models filesystem entries and chunks, including tar metadata, offsets, chunk metadata, digest fields, xattrs, children, and runtime-only fields like `NumLink`, `nextOffset`, and `chunkTopIndex`. Methods include `ModTime`, `NextOffset`, `Stat`, `ForeachChild`, `LookupChild`, `addChild`, and `isDataType`. `fileInfo` converts TOC metadata to `os.FileInfo`, including tar mode conversion and special file type bits. `TOCEntryVerifier`, `Compression`, `Compressor`, `Decompressor`, and `WriteFlushCloser` define verification and codec contracts.

Control flow: this file mostly supplies structures and small methods. Writers/readers populate `TOCEntry` fields during tar conversion and TOC parse, build parent-child maps with `addChild`, expose children through lookup/iteration, and convert to stat data for callers. Compression implementations are called by writer and parser code through the interfaces here.

State and persistence: JSON tags define the durable TOC representation; runtime-only fields are intentionally omitted from JSON. Child maps and link counts are built after parse. `modTime` caches parsed `ModTime3339`, and `nextOffset` is computed to support chunk range reads.

Dependencies and integration points: used by all estargz packages, metadata readers, fs/layer logic, and image manifest label handling. Depends on `archive/tar` for mode interpretation, `os.FileInfo` conventions, `opencontainers/go-digest`, and `io/hash` contracts.

Risks: `ForeachChild` iterates Go maps, so order is nondeterministic unless callers sort. The `Compression` interface requires compatible footer/TOC semantics across codecs; mistakes in `ParseFooter` negative offsets or `tocSize` handling can break metadata loading. `fileInfo.Mode` relies on tar mode conversion and manual type mapping, so new TOC types need explicit handling. Runtime-only fields make it important that parsers rebuild indices consistently.

Test signals: covered indirectly by shared compression tests for metadata, modes, xattrs, chunks, owners, children, links, and digest verification; `estargz_test.go` directly covers chunk lookup boundaries.
