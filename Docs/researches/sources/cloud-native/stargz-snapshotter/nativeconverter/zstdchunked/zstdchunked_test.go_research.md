# sources/cloud-native/stargz-snapshotter/nativeconverter/zstdchunked/zstdchunked_test.go

Purpose: Unit-tests zstd:chunked layer conversion through containerd's index conversion path.
Important APIs/types/functions: `TestLayerConvertFunc` invokes `LayerConvertFunc` with prioritized files, `converter.DefaultIndexConvertFunc`, `images.Walk`, and metadata constants from eStargz and zstdchunked.
Control flow: the test prepares a hello fixture, converts it with Docker-to-OCI enabled, walks the converted image tree, records media types and layer annotations, then asserts the zstd media type and TOC/manifest annotations exist.
State and persistence: all image content lives in the fixture content store; the test only accumulates observed media types and annotations in maps.
Dependencies and integration points: validates the public converter in the same shape used by higher-level image conversion commands.
Risks: the test checks metadata presence but not chunk manifest correctness, rootfs equivalence, selected zstd level, duplicate layer behavior, or actual lazy-read compatibility.
Test signals: good smoke coverage for conversion plumbing and annotation propagation.
