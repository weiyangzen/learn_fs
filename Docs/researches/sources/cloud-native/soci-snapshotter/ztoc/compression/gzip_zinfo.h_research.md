# sources/cloud-native/soci-snapshotter/ztoc/compression/gzip_zinfo.h

## Purpose
`gzip_zinfo.h` declares the C ABI for gzip checkpoint metadata generation, extraction, and serialization used by Go cgo.

## Important APIs, Types, and Functions
It defines `offset_t`, version constants, `WINSIZE`, `PACKED_CHECKPOINT_SIZE`, `BLOB_HEADER_SIZE`, error codes, `struct gzip_checkpoint`, and `struct gzip_zinfo`. Public functions expose metadata lookup, zinfo generation from file, extraction from file or buffer, and zinfo-to-blob/blob-to-zinfo conversion.

## Control Flow, State, and Persistence
The header describes persisted blob layout sizes and in-memory state: a gzip zinfo has encoded version, count, allocated size, checkpoint list, and span size.

## Dependencies and Integration Points
It includes stdbool/stdint/stdio/string and zlib headers. Go cgo includes this header from `gzip_zinfo.go`.

## Risks and Test Signals
The ABI couples Go wrappers to C struct layout and return-code semantics. Any change to blob constants or struct fields affects persisted zTOC compatibility. Tests in Go validate invalid blob size handling and extraction behavior through this ABI.
