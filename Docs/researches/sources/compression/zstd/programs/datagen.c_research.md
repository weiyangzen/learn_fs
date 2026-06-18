# sources/compression/zstd/programs/datagen.c

## Purpose
`datagen.c` generates deterministic pseudo-random data with configurable compressibility. It supports both in-memory generation for benchmarks and streaming generation to stdout for CLI data generation.

## Important APIs, types, and functions
The exported functions are `RDG_genBuffer()` and `RDG_genStdout()`. `RDG_rand()` is the local deterministic 32-bit generator. `RDG_fillLiteralDistrib()` builds an 8K literal distribution table using a 24.8 fixed-point probability. `RDG_genBlock()` is the core generator: it alternates literals and back-references according to `matchProba`, with a special sparse-data path when `matchProba >= 1.0`.

## Control flow
`RDG_genBuffer()` initializes the seed and literal table, derives a default literal probability from match probability when unset, then generates one block from position zero. `RDG_genStdout()` allocates a 32 KiB dictionary plus 128 KiB output block, generates an initial dictionary, repeatedly generates blocks with the dictionary as prefix, writes only the requested block portion to stdout, and slides the dictionary forward with `memcpy()`.

Inside `RDG_genBlock()`, position starts at `prefixSize`. If sparse generation is requested, it emits large zero runs separated by generated nonzero bytes. Otherwise it ensures the first byte exists, then repeatedly chooses between a match copy from the prior 32 KiB window or a run of literals. Match copy intentionally supports overlap, mirroring LZ-style repeated sequences.

## State and persistence behavior
There is no persistent state. Output is deterministic for a given `(matchProba, litProba, seed)` tuple. `RDG_genStdout()` mutates stdout mode to binary and writes raw bytes. All generator state is local: seed, literal table, rolling dictionary buffer, and current position.

## Dependencies and integration points
The file depends on `datagen.h`, `platform.h` for `SET_BINARY_MODE`, C stdlib/stdio/string functions, and zstd common `mem.h` for integer aliases. `benchzstd.c` uses `RDG_genBuffer()` to warm benchmark buffers and produce synthetic samples.

## Risks and edge cases
The function assumes the caller passes a valid writable buffer of the requested size. Floating-point probabilities are only loosely bounded; values above one trigger sparse mode, while negative literal probability is clamped inside distribution setup. `RDG_genStdout()` ignores `fwrite()` failures by assigning the result to an unused variable, so pipe errors may not be reported here. Very small buffers are handled by the position checks, but the generator's statistical properties are only meaningful for larger samples.

## Test signals
Tests should verify determinism for fixed seeds, differences across seeds, behavior at `matchProba` 0, typical mid-range probabilities, sparse mode at 1.0, zero-size buffer calls, and stdout generation lengths. Compression-ratio smoke tests can confirm that higher match probability generally produces more compressible output.
