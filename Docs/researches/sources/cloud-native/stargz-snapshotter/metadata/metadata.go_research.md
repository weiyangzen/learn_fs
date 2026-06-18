# sources/cloud-native/stargz-snapshotter/metadata/metadata.go

## Purpose
Defines the common metadata abstraction used by stargz snapshotter readers, independent of a concrete memory or database-backed implementation.

## Important APIs, Types, And Functions
`Attr` represents file metadata including size, mode, ownership, device numbers, xattrs, symlink target, and link count. `Store` constructs a `Reader`. `Reader` exposes ID-based tree traversal, offsets, TOC digest, file opening, preread opening, clone, and close. `File` combines chunk lookup with `ReadAt`. `Decompressor` extends `estargz.Decompressor` with `DecompressTOC`. Options include `WithTOCOffset`, `WithTelemetry`, and `WithDecompressors`.

## Control Flow
This file is interface and option plumbing. Implementations consume options, expose stable IDs, and provide chunk entries for reader cache logic. Telemetry hooks allow implementations to report footer, TOC fetch, and TOC deserialization latency.

## State And Persistence
No state is stored in this file. It defines what state implementations expose and how callers configure them.

## Dependencies And Integration
Depends on `estargz`, standard IO/filesystem/time types, and OpenContainers digest. It is the contract between metadata backends, `fs/reader`, and tests.

## Risks And Test Signals
Risks include interface changes affecting all metadata implementations and ambiguous ID stability requirements without documentation in the interface. Shared tests in `metadata/testutil` validate important contract behavior against implementations.
