# sources/cloud-native/soci-snapshotter/integration/convert_standalone_test.go

Purpose: validates `soci convert --standalone` for OCI directory/archive inputs and outputs without requiring a running containerd during conversion.

Important APIs and flow: `TestStandaloneConvertBasic` exports a mirrored image to OCI dir/tar, stops containerd, converts dir-to-tar, tar-to-tar, dir-to-dir, and tar-to-dir, then imports outputs and calls `validateConversion`. `TestStandaloneConvertSpecificPlatform` verifies platform filtering. `TestStandaloneInvalidConversion` checks nonexistent input, unsupported format, and missing destination errors. `TestStandaloneConvertIdempotent` converts an already converted output and expects identical digests. `TestStandaloneConvertAllPlatforms` saves all platforms, converts with `--all-platforms`, validates conversion, and checks each source platform has both image and SOCI index descriptors. `readIndex` unwraps single-index import wrappers.

State and persistence: creates temp OCI directories and tar archives inside the test shell, imports converted outputs into containerd after conversion, and cleans temp directories.

Dependencies and integration: uses Docker registry shell helpers, `nerdctl save`, `tar`, `soci convert`, `ctr images import`, OCI index parsing, platform formatting, and shared conversion validation from `convert_test.go`.

Risks and test signals: strong coverage for standalone input/output formats, platform selection, idempotency, and multi-arch output shape. It still depends on public image availability and registry/containerd setup for input preparation and result validation.
