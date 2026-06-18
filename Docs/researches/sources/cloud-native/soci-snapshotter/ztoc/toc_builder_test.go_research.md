# sources/cloud-native/soci-snapshotter/ztoc/toc_builder_test.go

## Purpose
This test validates TOC building across supported tar providers and failure modes.

## Important APIs, Types, and Functions
`TestTocBuilder` creates deterministic large file entries, defines generators for tar, gzip tar, and zstd tar, registers providers, and runs a table of algorithm cases.

## Control Flow, State, and Persistence
Each case writes a temp archive, calls `builder.TocFromFile`, removes the file, and verifies either expected error or metadata count matching tar entry count.

## Dependencies and Integration Points
The test uses gzip, zstd, os/io, compression constants, and testutil archive generation. It validates `TocBuilder` independently from zinfo construction.

## Risks and Test Signals
The test checks metadata count but not every metadata field, offset, mode, xattr, or file type. It is useful as a provider registration and decompressor compatibility signal.
