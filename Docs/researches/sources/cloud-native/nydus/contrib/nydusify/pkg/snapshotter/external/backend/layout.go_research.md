# sources/cloud-native/nydus/contrib/nydusify/pkg/snapshotter/external/backend/layout.go

Purpose: declares binary on-disk layout structs and constants for external backend metadata.

Important APIs/types/constants: `MetaMagic`, `MetaVersion`, `Header`, `ChunkMeta`, `ObjectMeta`, `ChunkOndisk`, `ObjectOffset`, and `ObjectOndisk`.

Control flow: no executable flow; the file defines fixed-size header/meta structures and variable-size object records. Comments describe section ordering: header, chunk metadata and entries, object metadata, optional object offsets, and object records.

State and persistence: these structs represent persisted metadata layout. `Header` is 4096 bytes, `ChunkMeta` and `ObjectMeta` are 256 bytes each, with reserved padding for future compatibility.

Dependencies and integration points: snapshotter external backend metadata writer/reader code and tests that assert layout sizes.

Risks and test signals: changing field order, types, or padding breaks on-disk compatibility. `ObjectOndisk` contains a slice and is not fixed-size directly; encoding code must handle its variable payload explicitly.
