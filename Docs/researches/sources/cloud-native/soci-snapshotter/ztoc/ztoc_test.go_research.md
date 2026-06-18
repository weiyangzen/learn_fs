# sources/cloud-native/soci-snapshotter/ztoc/ztoc_test.go

## Purpose
`ztoc_test.go` is the main behavior suite for zTOC generation, extraction, serialization, consistency, and benchmarking across gzip and uncompressed tar.

## Important APIs, Types, and Functions
Helpers `buildTarGZ`, `buildTar`, and `tarGenerator` create archives and expected contents. `testZtocs` enumerates gzip and uncompressed variants. Tests include `TestDecompress`, `TestDecompressWithGzipHeaders`, `TestDecompressWithPigz`, `TestZtocGenerationConsistency`, `TestZtocGeneration`, `TestZtocSerialization`, `TestWriteZtoc`, and `TestReadZtocInWrongFormat`. Benchmarks use `BenchmarkZtocGeneration`, `ztocGenBenchmarkFiles`, and `benchmarkZtocGeneration`. `getPositionOfFirstDiffInByteSlice` aids diagnostics.

## Control Flow, State, and Persistence
Tests generate deterministic random tar entries, write temp archives, build zTOCs with varied span sizes, extract every file, compare against original content maps, marshal/unmarshal zTOCs, compare checkpoint bytes and metadata, and validate deterministic descriptor digest/size for a simple fixture. Pigz tests shell out to a real `pigz` binary when installed and skip otherwise.

## Dependencies and Integration Points
Dependencies include gzip, os/exec, io/bytes, reflect, `go-digest`, compression constants, and testutil archive/random helpers. The tests exercise the full path across builders, C gzip zinfo, tar zinfo, marshaler, and extraction APIs.

## Risks and Test Signals
These tests are strong behavioral signals but can be resource-heavy due to multi-megabyte random files and benchmarks. Pigz coverage is optional. `ExtractFromTarGz` is used for uncompressed variants too, despite the name. The suite would catch many regressions in span offsets, gzip header handling, concatenated gzip streams, deterministic checkpoint generation, and FlatBuffer persistence.
