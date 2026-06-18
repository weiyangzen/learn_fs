# sources/cloud-native/moby/daemon/builder/remotecontext/internal/tarsum/tarsum_test.go

## Purpose
Exercises the legacy internal TarSum implementation against fixture layers, synthetic tar streams, gzip passthrough, alternate hash algorithms, duplicate-path ordering, xattr-sensitive versions, iteration behavior, and performance benchmarks. It is a regression suite for deterministic build-context/layer checksums rather than production logic.

## Important APIs, Types, And Functions
Defines `testLayer`, `sizedOptions`, `testLayers`, helper `sizedTar`, `emptyTarSum`, and `renderSumForHeader`. Tests cover `NewTarSum`, `NewTarSumHash`, `NewTarSumForLabel`, `TarSum.Read`, `TarSum.Sum`, `TarSum.Hash`, and `TarSum.Version`. Benchmarks use `benchmarkTar` over real and in-memory tar streams.

## Control Flow
Fixture entries are opened or generated, wrapped in TarSum readers, partially read with small and larger buffers, drained, and compared to known digests. Empty tar tests run pipe-backed tar writers and compare raw/gzip output. Header iteration constructs one-entry tars and drains them through `tar.NewReader` to force checksum recording.

## State And Persistence
Tests read `testdata` fixtures and create temp files only for benchmark streams. TarSum state is accumulated during reads and finalized by `Sum`; duplicate path tests intentionally depend on archive order and per-entry position.

## Dependencies And Integration Points
Depends on `archive/tar`, `compress/gzip`, crypto hash constructors, fixture layers/json, and `gotest.tools` assertions. It validates behavior consumed by remote build context hashing and archive context cache keys.

## Risks And Test Signals
The suite locks in legacy hashes, so harmless selector changes can break compatibility. Random benchmark data is not used for assertions. Failures signal digest drift, gzip corruption, read-size sensitivity, xattr ordering regressions, or broken support for non-default hash algorithms.
