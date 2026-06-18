# sources/cloud-native/soci-snapshotter/fs/reader/reader.go

Purpose: provides a metadata-backed file reader for lazy SOCI layers, mapping file reads to span-manager byte ranges and verifying tar-header metadata before first read.

Important APIs and flow: `Reader` exposes `OpenFile`, `Metadata`, `Close`, and `LastOnDemandReadTime`. `NewReader` stores a metadata reader, layer digest, span manager, and verification flag. `OpenFile` rejects closed readers, opens a metadata file by ID, and returns a `file` reader. `file.ReadAt` optionally calls `Verify`, handles empty/out-of-range reads, computes uncompressed file start/end from metadata offsets, reads contents from `SpanManager.GetContents`, records synchronous remote-fetch/read metrics, stores last on-demand read time, and fills the caller buffer with `io.ReadFull`. `Verify` is once-only and mutex-protected; it reads the tar header bytes via span manager, parses a tar header, checks exact header size, compares attrs/xattrs/name against metadata, and marks verified on success. `attrMatchesTarHeader` handles most tar-visible attributes but intentionally ignores link count.

State and persistence: reader state includes metadata reader, span manager, last read time, closed flag, and disable-verification flag. File state includes metadata file handle and an atomic verified bit. Persistence is delegated to the span manager/cache as reads materialize spans.

Dependencies and integration: used by `layer.Resolver.Resolve` and `layer/node.go` file handles. Depends on `metadata`, `fs/span-manager`, ztoc compression offsets/xattr parsing, common metrics, and tar parsing.

Risks and test signals: verification requires fetching tar header spans before first file read, which adds latency but catches metadata/content mismatch. If verification is disabled, corrupt metadata can drive reads unchecked. `io.ReadFull` turns short reads into errors, which is appropriate for immutable layer content. Tests cover many read offset/span/file-size combinations and non-existent file errors, but not verification mismatch cases or disabled verification.
