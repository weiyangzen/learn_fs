# sources/compression/zstd/lib/dictBuilder/divsufsort.c

## Purpose
`divsufsort.c` is a bundled libdivsufsort-lite implementation used by zstd's legacy dictionary trainer to build suffix arrays and optionally Burrows-Wheeler transforms. It implements the SA-IS-style division into type A, B, and B* suffixes, substring sorting, tandem-repeat sorting, induced suffix-array construction, and direct BWT construction.

## Important APIs, Types, And Functions
- `divsufsort(const unsigned char* T, int* SA, int n, int openMP)` validates arguments, allocates bucket arrays, sorts type B* suffixes, and constructs the full suffix array in `SA`.
- `divbwt(const unsigned char* T, unsigned char* U, int* A, int n, unsigned char* num_indexes, int* indexes, int openMP)` constructs the BWT into `U`, optionally using caller-provided temporary array `A` and optional secondary index output.
- `sort_typeBstar()` classifies suffixes, counts buckets, sorts B* substrings with `sssort()`, ranks them, runs tandem-repeat sorting with `trsort()`, and prepares bucket boundaries.
- `construct_SA()` induces B and A suffixes from sorted B* suffixes.
- `construct_BWT()` and `construct_BWT_indexes()` produce BWT bytes directly from induced order.
- The `ss_*` functions implement substring sorting with insertion sort, heapsort fallback, multikey introsort, block merges, rotations, and buffer-assisted merges.
- The `tr_*` functions implement tandem-repeat introsort with an explicit `trbudget_t` to limit repeated work.

## Control Flow
`divsufsort()` handles small `n` directly. For larger inputs it allocates `bucket_A[256]` and `bucket_B[65536]`, calls `sort_typeBstar()` to count and order B* suffixes, then calls `construct_SA()` to fill the full suffix array. `sort_typeBstar()` scans the input backwards to classify suffixes, uses bucket counts to place B* suffix references into the suffix array, sorts each bucket's substrings, computes inverse ranks, and resolves tandem repeats. Negative values in `SA` are used as markers during sorting and induction, then normalized before final output.

`divbwt()` follows the same B* sorting path but calls BWT construction instead of `construct_SA()`. It then copies the temporary integer BWT representation into `U`, inserting `T[n - 1]` at the front and returning the primary index plus one. If secondary indexes are requested, `construct_BWT_indexes()` computes a power-of-two-like sampling mask and records selected positions.

## State And Persistence
All state is held in caller-provided buffers and temporary heap allocations. The suffix array buffer is heavily reused as workspace for B* positions, inverse suffix ranks, temporary BWT bytes, and negative marker values. No state persists after the call except the output `SA`, output BWT `U`, optional `num_indexes/indexes`, and return code. If `divbwt()` receives `A == NULL`, it allocates and frees its own `(n + 1)` integer workspace.

## Dependencies And Integration Points
The file depends only on the C standard library, assertions, and `divsufsort.h`. `zdict.c` calls `divsufsort()` in the legacy trainer to sort the concatenated samples. The optional `LIBBSC_OPENMP` blocks can parallelize substring bucket sorting when compiled with OpenMP support and `openMP` is true; otherwise the `openMP` argument is consumed but unused.

## Risks And Edge Cases
- Public APIs use `int` for sizes and indexes; callers must keep `n` within signed-int limits and supply sufficiently large arrays.
- The implementation relies on intricate in-place negative markers (`~value`) in `SA`; memory corruption or incorrect marker normalization can silently produce invalid suffix arrays.
- `PTRDIFF_TO_INT()` asserts pointer differences fit in `int`, but release builds rely on caller size discipline.
- `construct_BWT_indexes()` writes into `indexes` based on derived sample count; caller must provide enough storage for `*num_indexes`.
- OpenMP sections share bucket cursor state behind critical sections; builds should check both parallel and non-parallel paths if `LIBBSC_OPENMP` is enabled.
- Allocation failure returns `-2`; invalid arguments return `-1`; there is no zstd-style `size_t` error code wrapping.

## Test Signals
Strong tests compare suffix-array order against a simple reference sorter for empty, length 1/2, repeated-byte, monotonic, random, and highly periodic inputs. BWT tests should validate primary index and inverse reconstruction, including in-place `U == T` behavior where expected by the API. Sanitizer and assertion builds are valuable for negative marker handling, bucket bounds, and signed integer conversions. Legacy dictionary-training tests indirectly cover this file through `ZDICT_trainFromBuffer_legacy()`.
