# sources/cloud-native/stargz-snapshotter/metadata/testutil/testutil.go

## Purpose
Provides a comprehensive reusable test suite for `metadata.Reader` implementations.

## Important APIs, Types, And Functions
`ReaderFactory`, `TestableReader`, `TestingT`, `Runner`, and `TestRunner` abstract over test frameworks and metadata backends. `TestReader` builds fixture archives and runs check functions including `numOfNodes`, `hasFile`, `hasDirChildren`, `sameNodes`, `linkName`, `hasNumLink`, device checks, xattr/owner/mode/modtime checks, chunk checks, and preread checks.

## Control Flow
The suite iterates over path prefixes, compression formats, chunk sizes, and file layouts. It builds eStargz archives, opens readers with telemetry and decompressor options, dumps node trees for diagnostics, applies all expected checks, verifies telemetry hooks were called, then clones a second reader and repeats checks. A final clone-ID-stability test compares path-to-ID maps.

## State And Persistence
All fixture data is generated in memory. Test state includes telemetry call booleans, random 64KB payloads, and reader-specific metadata maps. No durable state is written by the suite.

## Dependencies And Integration
Depends on eStargz building utilities, gzip/zstd/external TOC compression factories, the common metadata interfaces, and digest calculations. Memory and other metadata backends reuse this suite to prove contract compliance.

## Risks And Test Signals
Signals cover empty archives, regular files, directories, hardlinks, symlinks, device nodes, FIFOs, normalized paths, chunks, preread of neighboring files, telemetry, and clone stability. Risks include assumptions about generated eStargz layout and test runtime from the compression/prefix matrix.
