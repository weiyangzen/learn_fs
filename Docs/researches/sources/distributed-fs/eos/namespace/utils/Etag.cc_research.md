# sources/distributed-fs/eos/namespace/utils/Etag.cc

## Purpose
`Etag.cc` implements EOS namespace etag generation for FST metadata, namespace file metadata, protobuf file metadata, and container metadata. It preserves compatibility with S3 expectations and historical inode encodings.

## Important APIs, Types, and Functions
Internal `findInode(uint64_t fid)` chooses legacy or new fid-to-inode conversion at a 34 billion fid threshold. Public overloads include `calculateEtag(bool useChecksum, const fst::FmdBase&, std::string&)`, `calculateEtagInodeAndChecksum(const fst::FmdBase&, std::string&)`, `calculateEtagInodeAndMtime(uint64_t, uint64_t, std::string&)`, `calculateEtag(const ns::FileMdProto&, std::string&)`, `calculateEtag(const IFileMD*, std::string&)`, and `calculateEtag(IContainerMD*, std::string&)`.

## Control Flow
FST metadata etags either use checksum or inode+mtime depending on the supplied flag. Checksum-based etags omit inode when checksum type is MD5 so S3 receives a pure MD5 etag; non-MD5 checksums include `inode:checksum`. Namespace file/protobuf overloads first honor forced temporary etag attribute `sys.tmp.etag`. If the layout has a checksum length, they format checksum bytes similarly with MD5 special-casing. Without checksum, they extract modification/change time and fall back to `inode:mtime`. Container etags honor `sys.tmp.etag`, otherwise use hex container ID plus tree mtime seconds and milliseconds.

## State and Persistence Behavior
The functions are pure formatting helpers. They read metadata attributes, IDs, layout IDs, checksums, and timestamps, then overwrite the caller-provided output string. No metadata is modified.

## Dependencies and Integration Points
The file depends on `Etag.hh`, `IFileMD`, `FileId`, FST metadata, checksum helpers, layout IDs, and container/file metadata interfaces. It integrates with HTTP/S3-facing metadata and printing paths that require stable etag strings.

## Risks and Edge Cases
The 34B fid threshold is a compatibility hack that must remain aligned with file ID encoding. File protobuf mtime is recovered by `memcpy` from raw string bytes into a `timespec`-like struct, so malformed or short serialized timestamps could be dangerous if upstream validation is absent. MD5 special handling changes etag shape compared with other checksum types. `calculateEtag(const IFileMD*)` does not null-check the pointer.

## Test Signals
`VariousTests.cc` covers forced temporary etags, inode+mtime fallback, Adler-style inode+checksum etags, pure MD5 etags, and container etag formatting. Additional tests should cover the fid threshold boundary and malformed protobuf timestamp data.
