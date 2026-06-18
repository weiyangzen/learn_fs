# sources/compression/zstd/lib/dictBuilder/divsufsort.h

## Purpose
`divsufsort.h` declares the small libdivsufsort-lite API bundled for zstd dictionary-building internals: suffix-array construction and Burrows-Wheeler transform construction.

## Important APIs, Types, And Functions
- `int divsufsort(const unsigned char* T, int* SA, int n, int openMP)` constructs the suffix array for `T[0..n-1]` into `SA[0..n-1]`.
- `int divbwt(const unsigned char* T, unsigned char* U, int* A, int n, unsigned char* num_indexes, int* indexes, int openMP)` constructs a BWT string into `U`, optionally using `A` as temporary integer workspace and optionally returning secondary indexes.

## Control Flow
The header has no logic beyond include guards and prototypes. Callers pass raw byte buffers and integer-sized lengths to the implementation in `divsufsort.c`. Return values are conventional integer status/results rather than zstd `size_t` error codes: suffix sorting returns `0` on success, while BWT returns the primary index or a negative error.

## State And Persistence
The API is stateless. All mutable state is supplied by the caller (`SA`, `U`, optional `A`, optional index arrays) or allocated temporarily by the implementation.

## Dependencies And Integration Points
It has no external includes and is consumed by `zdict.c`. The API originates from libdivsufsort-lite, so licensing and ABI expectations are separate from the surrounding zstd-specific files.

## Risks And Edge Cases
- `n` and suffix entries are `int`, so it cannot represent buffers larger than `INT_MAX`.
- Callers must allocate output arrays of the documented lengths; the implementation does not receive capacities.
- `openMP` is only meaningful when the implementation is compiled with the matching OpenMP feature macro.

## Test Signals
Compile tests should ensure C and C++ consumers can include the header. Behavioral tests should call both functions through the header with small known inputs, invalid `NULL` arguments, zero-length input, and optional BWT index output.
