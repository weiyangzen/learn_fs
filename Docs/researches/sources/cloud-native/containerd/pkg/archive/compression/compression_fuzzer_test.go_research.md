# sources/cloud-native/containerd/pkg/archive/compression/compression_fuzzer_test.go

## Purpose
Fuzz-tests decompression stream detection and reader construction against arbitrary input bytes.

## Important APIs, Types, And Functions
`FuzzDecompressStream` passes random byte slices through `DecompressStream(bytes.NewReader(data))` and ignores the result.

## Control Flow
The fuzzer stresses detection, peeking, gzip/zstd reader creation, and error handling without reading returned decompressed streams.

## State And Persistence
No persistent state; may touch package-global gzip detection if inputs look gzip-like and path detection initializes.

## Dependencies And Integration Points
Uses Go fuzzing support, bytes reader, and compression package APIs.

## Risks
Because it does not read from successful returned readers, it may miss panics or hangs during actual decompression consumption. External gzip command paths could complicate fuzz environments.

## Test Signals
Useful input-hardening signal for `DecompressStream` setup paths, but not full decompression correctness.
