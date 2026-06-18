# sources/distributed-fs/eos/namespace/utils/Etag.hh

## Purpose
Declares namespace ETag calculation helpers for EOS file and container metadata. The API centralizes how namespace-visible ETags are derived from `IFileMD`, `IContainerMD`, QuarkDB `FileMdProto`, and FST-side file metadata so HTTP/WebDAV-style consumers and MGM/FST paths can share the same identity semantics.

## Important APIs, types, and functions
The exported overloads are `calculateEtag(const IFileMD*, std::string&)`, `calculateEtag(const eos::ns::FileMdProto&, std::string&)`, `calculateEtag(IContainerMD*, std::string&)`, and FST variants taking `fst::FmdBase`. Specialized helpers `calculateEtagInodeAndChecksum()` and `calculateEtagInodeAndMtime()` expose the two main strategies: inode plus checksum when checksum metadata is available, or inode plus modification time as a fallback.

## Control flow
This header only declares the operations. Callers provide metadata and a mutable output string; implementations decide whether to inspect checksum, inode, and timestamps. The `useChecksum` overload makes that choice explicit for FST metadata.

## State and persistence
No state is stored here, but the produced ETag is externally observable and may be cached by clients. Any change in the implementation affects HTTP cache validators and object identity expectations.

## Dependencies and integration points
Depends on EOS namespace interfaces, FST metadata, and generated `proto/FileMd.pb.h`. It integrates namespace metadata services, FST metadata reporting, and MGM frontends that need stable ETags.

## Risks and test signals
Risk centers on compatibility: changing checksum-vs-mtime fallback changes client cache behavior. Tests should cover files with and without checksums, directories, QuarkDB proto input, FST `FmdBase` input, and stable output across equivalent metadata representations.
