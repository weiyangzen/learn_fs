## sources/distributed-fs/seaweedfs/weed/s3api/sses3_multipart_repro_test.go

Purpose: regression-tests SSE-S3 multipart decryption behavior for production-like chunking and lazy chunk fetching.

Important tests/helpers: `TestMultipartSSES3RealisticEndToEnd`, `TestBuildMultipartSSES3Reader_LazyChunkFetch`, and `liveTrackingReadCloser`.

Control flow: the end-to-end test generates one data encryption key and base IV shared by all parts, encrypts each part from offset zero, slices ciphertext at 8 MB chunk boundaries, stores per-chunk IV metadata derived from part-local offsets, assigns global file offsets, then verifies `buildMultipartSSES3Reader` decrypts concatenated plaintext. The lazy test creates many encrypted chunks and asserts construction opens no readers, first read opens one, draining opens all eventually, and peak live readers stays at one.

State and dependencies: in-memory ciphertext map simulates volume fetches; filer chunks carry offsets, sizes, SSE type, and serialized metadata. Depends on SSE-S3 key generation, IV calculation, metadata serialization, and reader assembly code outside this file.

Risks and signals: protects issue paths where global offsets and part-local IVs diverge, and where eager fetches held many HTTP responses open. It does not hit real volume servers but accurately models chunk metadata.
