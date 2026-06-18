# sources/cloud-native/soci-snapshotter/ztoc/ztoc.go

## Purpose
`ztoc.go` defines the core zTOC data model and extraction APIs for retrieving files from compressed or uncompressed layer archives using TOC metadata and zinfo span checkpoints.

## Important APIs, Types, and Functions
Types include `Version`, `Ztoc`, `CompressionInfo`, `TOC`, `FileMetadata`, and `MetadataEntry`. `FileMetadata.FileMode`, `Equal`, and `Xattrs` provide metadata helpers. `TOC.GetMetadataEntry` resolves file entries and follows links. `Ztoc.ExtractFile` fetches relevant compressed spans through an `io.SectionReader`, decompresses the requested range, and returns bytes. `ExtractFromTarGz` extracts directly from a file path through zinfo. `Zinfo` deserializes algorithm-specific checkpoint state.

## Control Flow, State, and Persistence
`ExtractFile` looks up metadata, handles zero-size files, creates zinfo from stored checkpoints, computes span range for the file, reads all compressed spans into one buffer using an errgroup, and asks zinfo to extract the requested uncompressed byte range. `ExtractFromTarGz` performs similar lookup but lets zinfo read from the file. Stored fields include version, build tool identifier, archive sizes, TOC, span digests, checkpoints, max span ID, and compression algorithm.

## Dependencies and Integration Points
Dependencies include tar/os/time/io, `go-digest`, errgroup, and the compression package. This is the central type consumed by builders, marshaling, OCI artifact handling, and tests.

## Risks and Test Signals
`ExtractFile` has a closure capture risk around loop variable `i` in the errgroup; in modern Go range semantics differ from older loop semantics, but this code uses a `for` loop with a reused variable and should be reviewed for concurrent capture correctness. On `zt.Zinfo()` error, `ExtractFile` returns `nil, nil`, which can hide failures. Link resolution recurses without cycle detection. Tests cover gzip and uncompressed extraction across span sizes, gzip header fields, pigz streams, generation consistency, serialization, and invalid unmarshal handling.
