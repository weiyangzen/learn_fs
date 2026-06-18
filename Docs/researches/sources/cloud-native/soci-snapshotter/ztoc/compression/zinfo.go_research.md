# sources/cloud-native/soci-snapshotter/ztoc/compression/zinfo.go

## Purpose
`zinfo.go` defines the `Zinfo` abstraction for random access into compressed or uncompressed archive data and provides factory functions by compression algorithm.

## Important APIs, Types, and Functions
`Zinfo` includes extraction from buffer/file, close, byte serialization, max span and span size, uncompressed-offset to span mapping, compressed and uncompressed span boundary methods, and header verification. `NewZinfo` deserializes bytes into gzip or tar zinfo. `NewZinfoFromFile` builds zinfo from a file for gzip or uncompressed tar.

## Control Flow, State, and Persistence
The factories switch on algorithm strings. Gzip maps to C-backed checkpoint data. Uncompressed and unknown deserialization map to tar zinfo, while file-based unknown is rejected. Zstd returns a not-implemented error.

## Dependencies and Integration Points
It depends on `fmt` and `io`. ztoc builders and `Ztoc.Zinfo` use these factories as the central compression dispatch point.

## Risks and Test Signals
Unknown is allowed during deserialization but not file construction, which reflects catch-all reading but stricter building. Zstd has a constant and tar provider support for TOC, but no zinfo implementation, so a full zstd zTOC build is unsupported unless a builder is registered externally.
