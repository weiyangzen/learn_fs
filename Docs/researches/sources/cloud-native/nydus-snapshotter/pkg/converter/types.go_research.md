# sources/cloud-native/nydus-snapshotter/pkg/converter/types.go

Purpose: defines converter option structs, layer/backend abstractions, compression flags, and TOC entry accessors used by pack/merge/unpack code.

Important APIs and types: `Compressor` constants and mask; `ErrNotFound`; `Layer`; converter-local `Backend` interface; `PackOption`, `MergeOption`, `UnpackOption`; `TOCEntry` and methods `GetCompressor`, `GetName`, `GetUncompressedDigest`, `GetCompressedOffset`, `GetCompressedSize`, and `GetUncompressedSize`; `Encrypter` callback type.

Control flow: most types are configuration. `TOCEntry.GetCompressor` decodes compressor bits from flags and errors on unsupported values. `GetName` reads a NUL-terminated 16-byte name. Offset/size/digest methods expose binary TOC fields.

State and persistence: option structs carry work dir, builder path, fs version, chunk dict, prefetch, backend, timeouts, encryption, and merge settings across converter calls. `TOCEntry` maps on-disk nydus blob TOC records.

Dependencies and integration points: used by Unix converter implementation, reconverter, and backend implementations. `PackOption.features` is internal and populated from `tool.DetectFeatures`.

Risks: `PackOption` has a misspelled `BacthSize` comment for `BatchSize`, but field is correct. The converter-local `Backend` duplicates `pkg/backend.Backend`; structural typing keeps it compatible but changes must be mirrored. TOC parsing assumes little-endian 128-byte entries matching nydus-image output.

Test signals: no direct tests for TOC accessors in listed files; conversion code indirectly depends on them for `seekFileByTOC`.
