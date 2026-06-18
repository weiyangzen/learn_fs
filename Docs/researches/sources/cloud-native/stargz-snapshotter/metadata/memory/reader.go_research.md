# sources/cloud-native/stargz-snapshotter/metadata/memory/reader.go

## Purpose
Provides an in-memory `metadata.Reader` implementation over an `estargz.Reader`. It maps eStargz TOC entries to stable numeric IDs and exposes metadata/file access through the common metadata interface.

## Important APIs, Types, And Functions
`NewReader` opens an eStargz section reader with metadata options. `assignIDs` builds `idMap` and `idOfEntry`. Methods implement `RootID`, `TOCDigest`, `GetOffset`, `GetAttr`, `GetChild`, `ForeachChild`, `OpenFile`, `OpenFileWithPreReader`, `Clone`, `Close`, and test helper `NumOfNodes`. `attrFromTOCEntry` converts TOC metadata to `metadata.Attr`.

## Control Flow
New reader options translate telemetry and decompressors into estargz open options. The root TOC entry is looked up by empty name, then entries are recursively assigned IDs, rejecting unresolved hardlink entries. File open calls use the eStargz reader and wrap section readers. `OpenFileWithPreReader` converts preread callbacks from TOC entries to numeric IDs.

## State And Persistence
All metadata is in memory: the estargz reader, root ID, ID maps, and open options. `Clone` opens a new estargz reader over a new section reader while sharing the same ID maps, preserving ID stability. `Close` is a no-op.

## Dependencies And Integration
Depends on `estargz`, the common `metadata` interfaces/options, OpenContainers digest, and filesystem modes. Used by reader tests and as the default lightweight metadata backend.

## Risks And Test Signals
Risks include memory scaling with TOC size, shared ID maps assuming cloned content has identical TOC entries, no cleanup in `Close`, and path/name identity for hardlinks. `metadata/memory/reader_test.go` runs the shared metadata suite across many file types and compression formats.
