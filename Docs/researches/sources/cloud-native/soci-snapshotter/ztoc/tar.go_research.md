# sources/cloud-native/soci-snapshotter/ztoc/tar.go

## Purpose
`tar.go` contains tar-format helpers used by zTOC metadata calculations.

## Important APIs, Types, and Functions
`TarBlockSize` is 512. `AlignToTarBlock(o)` rounds offsets up to the next tar block boundary. `Xattrs(paxHeaders)` extracts PAX records with prefix `SCHILY.xattr.` and strips the prefix.

## Control Flow, State, and Persistence
No persistent state exists. Offset alignment is arithmetic. Xattr conversion allocates a new map only when PAX headers exist.

## Dependencies and Integration Points
The file depends on `strings` and compression offset types. `toc_builder.go`, `ztoc_marshaler.go`, and `FileMetadata.Xattrs` use these helpers.

## Risks and Test Signals
`Xattrs` returns an empty map if headers exist but no xattr-prefixed key matches; callers may need to distinguish nil from empty. Alignment is critical for reconstructing tar header offsets after FlatBuffer deserialization.
