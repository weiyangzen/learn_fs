# sources/cloud-native/stargz-snapshotter/nativeconverter/estargz/estargz.go

## Purpose
Provides containerd image converter functions that rewrite layer blobs into eStargz format and annotate descriptors with TOC and uncompressed-size metadata.

## Important APIs, Types, And Functions
`LayerConvertWithLayerAndCommonOptsFunc` supports common eStargz options plus per-layer options keyed by digest. `LayerConvertFunc` returns a `converter.ConvertFunc` that converts layer descriptors, writes converted content to the content store, updates diffID labels, digest, size, media type, TOC digest annotation, and uncompressed-size annotation.

## Control Flow
Non-layer descriptors return nil, meaning no conversion. Layer conversion reads the source blob from content store, builds an eStargz blob with context, opens a content writer with deterministic ref, truncates stale writer state, copies converted bytes, commits with labels unless already exists, adjusts media type if source was uncompressed, and returns an updated descriptor.

## State And Persistence
Converted blobs are persisted in the containerd content store. Labels preserve/update uncompressed digest information. Descriptor annotations carry eStargz TOC digest and uncompressed size. Common options are copied defensively to avoid data races.

## Dependencies And Integration
Depends on containerd content store and converter APIs, image media type helpers, uncompress media helpers, labels, errdefs, local `estargz` builder, and OCI descriptors. Intended to be composed with Docker-to-OCI conversion so annotations are retained.

## Risks And Test Signals
Risks include interrupted writers requiring truncation, already-existing content handling, media type annotation loss for Docker formats without OCI conversion, and per-digest option ambiguity when duplicate layers share a digest. `estargz_test.go` verifies conversion creates at least one layer with a TOC annotation.
