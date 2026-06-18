# subset-b-000318 Research

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/lib/dictBuilder/cover.c -->
# sources/compression/zstd/lib/dictBuilder/cover.c

## Purpose
`cover.c` implements zstd's static-linking-only COVER dictionary trainer and the shared "best candidate" selection utilities used by both COVER and FASTCOVER optimization. It builds dictionaries by scoring repeated `d`-byte substrings ("dmers") across training samples, selecting high-value `k`-sized segments by epoch, finalizing selected raw content into a zstd dictionary, and optionally evaluating many parameter candidates against held-out samples.

## Important APIs, Types, And Functions
- `ZDICT_trainFromBuffer_cover()` is the direct COVER training entry point. It validates `ZDICT_cover_params_t`, initializes a `COVER_ctx_t`, builds a raw dictionary, then calls `ZDICT_finalizeDictionary()`.
- `ZDICT_optimizeTrainFromBuffer_cover()` searches candidate `d` and `k` values, optionally using `POOL_ctx`, and returns the best dictionary plus the winning parameters through the caller's `ZDICT_cover_params_t`.
- `COVER_ctx_t` owns the sample pointer, offsets, counts, partial suffix data, dmer frequencies, and dmer-id lookup table for a single `d` value.
- `COVER_map_t` is a fixed-size linear-probing map for the active segment window. It tracks unique dmer occurrences while sliding a segment over an epoch.
- `COVER_buildDictionary()` repeatedly calls `COVER_selectSegment()` over computed epochs, copies selected source segments into the dictionary buffer from the end backward, and stops when the buffer is full or scoring dries up.
- `COVER_checkTotalCompressedSize()` evaluates a finalized dictionary by creating a `ZSTD_CDict`, compressing selected validation samples, and returning dictionary size plus compressed sizes.
- `COVER_best_*()` manages cross-thread selection of the best candidate dictionary. It tracks live jobs with zstd pthread wrappers and stores the candidate with the smallest `totalCompressedSize`.
- `COVER_selectDict()` finalizes raw dictionary content and, when `shrinkDict` is enabled, searches for the smallest dictionary within the configured regression tolerance.

## Control Flow
The direct path validates parameters, sample count, and destination capacity, then calls `COVER_ctx_init()`. Context initialization computes train/test split counts, sample offsets, a partial suffix array over all possible dmers, stable-sorts that array using the platform qsort variant, groups equal dmers, records per-position dmer ids, and reuses the suffix allocation as the frequency table. `COVER_buildDictionary()` computes epochs with `COVER_computeEpochs()`, scans each epoch with a sliding window, selects the highest scoring segment, zeros the frequencies of covered dmers, and appends the chosen segment at the back of the output buffer. The direct entry then finalizes the selected content using entropy tables derived from all samples.

The optimized path chooses default ranges (`d` 6/8, `k` 50..2000, 40 steps, split point 0.75 unless supplied), initializes one context per `d`, and tries each `k`. Each try clones the frequency table, builds a candidate dictionary, calls `COVER_selectDict()`, and reports the result to `COVER_best_finish()`. The parent waits for all jobs for a `d` before destroying that context, then copies the best dictionary to the caller's buffer.

## State And Persistence
All training state is process-local and transient. `COVER_ctx_t` borrows `samplesBuffer` and `samplesSizes`, but owns allocated `offsets`, `dmerAt`, and either `suffix` or `freqs`. Candidate workers own their opaque argument, cloned frequency table, temporary dictionary buffer, active dmer map, and dictionary-selection allocation until cleanup. `COVER_best_t` persists across candidate jobs during optimization and owns a heap copy of the best dictionary until `COVER_best_destroy()`. The only external writes are to caller-provided dictionary buffers and optional progress messages to `stderr`.

## Dependencies And Integration Points
This file depends on zstd common memory, debug, bits, threading, pool, and compression APIs, plus `../zdict.h` and `cover.h`. It calls `ZDICT_finalizeDictionary()` from `zdict.c`, `ZSTD_createCDict()`, `ZSTD_compress_usingCDict()`, and zstd error helpers. `fastcover.c` reuses `COVER_best_t`, `COVER_computeEpochs()`, `COVER_warnOnSmallCorpus()`, `COVER_sum()`, `COVER_selectDict()`, and compression-size evaluation through `cover.h`. Platform integration is sensitive to `qsort_r`/`qsort_s` ABI differences; the C90 fallback uses a global `g_coverCtx`.

## Risks And Edge Cases
- `COVER_map_t` does not resize and can loop indefinitely if undersized; callers size it from `k - d + 1`, so parameter validation is critical.
- The C90 `qsort()` fallback uses global context and is explicitly not reentrant, making concurrent optimized training unsafe on platforms without reentrant sort support.
- Size casts to `U32` and the `COVER_MAX_SAMPLES_SIZE` limit constrain usable corpus sizes; 32-bit builds are capped much lower.
- `splitPoint == 1.0` makes train and test sets both cover all samples in direct training. Optimized training uses a held-out split by default.
- `COVER_selectDict()` copies and re-finalizes dictionary content repeatedly during shrink search; regressions can appear around overlapping buffers and minimum dictionary size.
- In `COVER_best_finish()`, allocation failure while replacing the best dictionary stores a generic error but still decrements live jobs; callers must check `best.compressedSize`.

## Test Signals
Useful coverage includes parameter-boundary tests for `d`, `k`, `splitPoint`, small sample count, and small destination buffers; deterministic training tests on fixed corpora; optimization tests with one and multiple threads; shrink-dictionary tests validating compressed-size regression tolerance; memory-failure or sanitizer runs around candidate cleanup; and platform builds that exercise GNU, Apple, MSVC/C11, and fallback qsort selection.
<!-- END_FILE_RESEARCH: sources/compression/zstd/lib/dictBuilder/cover.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/lib/dictBuilder/cover.h -->
# sources/compression/zstd/lib/dictBuilder/cover.h

## Purpose
`cover.h` is the internal interface shared by zstd's COVER and FASTCOVER dictionary builders. It defines candidate-selection state, segment and epoch helper types, dictionary-selection result ownership, and the utility functions needed by `cover.c` and `fastcover.c`.

## Important APIs, Types, And Functions
- `COVER_best_t` combines a mutex, condition variable, live job count, best dictionary pointer/size, winning `ZDICT_cover_params_t`, and best compressed-size score.
- `COVER_segment_t` describes a chosen source range with `begin`, `end`, and `score`.
- `COVER_epoch_info_t` records the number and size of epochs used for segment selection.
- `COVER_dictSelection_t` owns a finalized candidate dictionary and its total compressed-size score.
- `COVER_computeEpochs()`, `COVER_warnOnSmallCorpus()`, and `COVER_sum()` are shared corpus/epoch helpers.
- `COVER_checkTotalCompressedSize()` evaluates a dictionary against sample ranges.
- `COVER_best_init/wait/destroy/start/finish()` provide a small synchronization and best-result API.
- `COVER_selectDict()` finalizes raw dictionary content and optionally performs shrink-dictionary selection.

## Control Flow
The header is included after forcing `ZDICT_STATIC_LINKING_ONLY`, so it may expose and consume zstd experimental/static dictionary-training structures. A typical optimized training path initializes `COVER_best_t`, starts jobs before dispatch, lets each job call `COVER_selectDict()`, reports its `COVER_dictSelection_t` through `COVER_best_finish()`, waits for all jobs, then destroys the best-state object.

## State And Persistence
The header defines ownership expectations rather than storing state itself. `COVER_best_t` owns the copied winning dictionary after successful `finish()` calls. `COVER_dictSelection_t` owns `dictContent` until it is transferred/copied or released by `COVER_dictSelectionFree()`. All APIs are process-local; no persistent storage is involved.

## Dependencies And Integration Points
It depends on zstd pthread wrappers from `common/threading.h`, zstd integer and byte types from `common/mem.h`, and `../zdict.h` for parameter types. `fastcover.c` relies on this header heavily to avoid duplicating dictionary finalization, scoring, and threaded best-candidate coordination. Consumers must compile with compatible zstd static-linking-only definitions.

## Risks And Edge Cases
- The thread-safety guarantee is conditional on zstd being built with multithread support; otherwise wrapper behavior depends on the configured threading backend.
- `COVER_best_init()` is the only method documented as not requiring prior initialization. Other methods assume a valid initialized object unless they explicitly return on `NULL`.
- `COVER_dictSelectionIsError()` treats a missing dictionary pointer as an error, even if the score is not an error code.
- The contract for `offsets`, train/check sample counts, and dictionary buffer capacity is shared implicitly with implementation files, so mismatched callers can score the wrong sample range.

## Test Signals
Tests should exercise `COVER_best_t` under serial and threaded candidate completion, verify dictionary-selection ownership/freeing, validate `COVER_computeEpochs()` around small corpora and large dictionaries, and compare `COVER_checkTotalCompressedSize()` against direct compression with a known `ZSTD_CDict`.
<!-- END_FILE_RESEARCH: sources/compression/zstd/lib/dictBuilder/cover.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/lib/dictBuilder/divsufsort.c -->
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
<!-- END_FILE_RESEARCH: sources/compression/zstd/lib/dictBuilder/divsufsort.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/lib/dictBuilder/divsufsort.h -->
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
<!-- END_FILE_RESEARCH: sources/compression/zstd/lib/dictBuilder/divsufsort.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/lib/dictBuilder/fastcover.c -->
# sources/compression/zstd/lib/dictBuilder/fastcover.c

## Purpose
`fastcover.c` implements zstd's FASTCOVER dictionary trainer, a faster variant of COVER that hashes 6- or 8-byte dmers into a fixed-size frequency table instead of sorting exact dmers. It supports direct training and parameter optimization, reusing shared COVER utilities for epoch computation, dictionary finalization, candidate scoring, and best-result synchronization.

## Important APIs, Types, And Functions
- `ZDICT_trainFromBuffer_fastCover()` trains one FASTCOVER dictionary with supplied `ZDICT_fastCover_params_t`, defaulting `splitPoint` to `1.0`, `f` to `20`, and `accel` to `1`.
- `ZDICT_optimizeTrainFromBuffer_fastCover()` searches `d`, `k`, and fixed `f/accel` settings, optionally in a thread pool, and writes winning FASTCOVER parameters back to the caller.
- `FASTCOVER_ctx_t` stores borrowed samples, owned offsets and frequency table, train/test counts, number of dmers, `d`, `f`, acceleration parameters, and display level.
- `FASTCOVER_accel_t` maps an acceleration level to a percentage of training samples used for finalization and a skip count for frequency collection.
- `FASTCOVER_hashPtrToIndex()` maps a dmer pointer to a `2^f` frequency-table index using zstd internal hash functions.
- `FASTCOVER_computeFrequency()` counts hashed dmers over training samples, applying acceleration skips.
- `FASTCOVER_selectSegment()` scores a sliding `k` segment using hashed dmer frequencies and a `U16` per-segment frequency table to avoid double-counting duplicate hash values inside the active segment.
- `FASTCOVER_buildDictionary()` selects segments by epoch and copies them into the output buffer from the back.

## Control Flow
Direct training validates that `d` is 6 or 8, `k <= maxDictSize`, `d <= k`, `0 < f <= 31`, `splitPoint` is in range, and `accel` is 1..10. Context initialization computes sample offsets and allocates a `2^f` frequency table. Frequency collection walks each training sample while `start + MAX(d, 8) <= sampleEnd`, hashes the current dmer, increments the count, and advances by `skip + 1`. Dictionary construction computes epochs, selects high-score segments, zeros frequencies for selected hashes, and emits raw content into the tail of the destination buffer. The result is finalized with `ZDICT_finalizeDictionary()`, using only the configured fraction of training samples for entropy finalization.

Optimized training defaults split point to 0.75, defaults `d` to trying 6 and 8, `k` to 50..2000 across 40 steps, and launches `FASTCOVER_tryParameters()` jobs. Each job clones the frequency table, builds raw content, calls `COVER_selectDict()`, and submits the result to `COVER_best_finish()`. The parent waits after each `d` value before destroying the shared context.

## State And Persistence
FASTCOVER keeps no persistent state outside caller buffers. The context borrows sample data and owns `offsets` and `freqs`. Each candidate owns cloned frequencies, a temporary dictionary buffer, a `segmentFreqs` array sized to `2^f`, and its opaque data object. `COVER_best_t` owns the winning dictionary copy until destroyed. Progress output goes to `stderr` through local display macros.

## Dependencies And Integration Points
This file depends on zstd common memory, pool, threading, internal compression hash functions from `zstd_compress_internal.h`, public/static dictionary types from `../zdict.h`, and shared COVER helpers from `cover.h`. `zdict.c` uses FASTCOVER optimization as the default implementation behind `ZDICT_trainFromBuffer()`. It integrates with `POOL_ctx` for multi-threaded search and with `ZDICT_finalizeDictionary()`/`COVER_selectDict()` for final dictionary construction and scoring.

## Risks And Edge Cases
- Hash collisions mean FASTCOVER approximates dmer identity; this is intentional but can select different content than exact COVER on collision-heavy corpora or small `f`.
- `segmentFreqs` is `U16`; very large `k` with many repeated hashes can overflow per-segment counts.
- `1 << f` allocations can be very large as `f` approaches 31, even though the parameter is technically valid.
- Direct training sets `splitPoint = 1.0` regardless of user input, so all samples are used for both training/finalization; optimized training honors/defaults a held-out split.
- Acceleration reduces frequency fidelity and finalization sample count; higher levels trade quality for speed.
- `ctx.nbDmers = trainingSamplesSize - MAX(d, sizeof(U64)) + 1` relies on earlier size checks to avoid underflow.

## Test Signals
Useful tests cover `d` restrictions, `f` and `accel` bounds, small sample rejection, deterministic fixed-corpus output, default parameter filling, multi-threaded optimization parity with serial optimization, high-acceleration behavior, and sanitizer checks for large `f` allocations and `segmentFreqs` indexing. End-to-end `ZDICT_trainFromBuffer()` tests also exercise this file because it is the default trainer.
<!-- END_FILE_RESEARCH: sources/compression/zstd/lib/dictBuilder/fastcover.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/lib/dictBuilder/zdict.c -->
# sources/compression/zstd/lib/dictBuilder/zdict.c

## Purpose
`zdict.c` provides zstd dictionary helper APIs, dictionary finalization, entropy-table construction, the legacy suffix-array trainer, and the default `ZDICT_trainFromBuffer()` entry point. It bridges raw selected dictionary content to valid zstd dictionary format by adding magic, dictionary id, entropy tables, optional padding, and content.

## Important APIs, Types, And Functions
- `ZDICT_isError()` and `ZDICT_getErrorName()` expose zstd error handling for dictionary APIs.
- `ZDICT_getDictID()` reads a zstd dictionary id from a dictionary header.
- `ZDICT_getDictHeaderSize()` loads dictionary entropy metadata to compute header size.
- `ZDICT_finalizeDictionary()` writes a full dictionary header, computes entropy tables from samples and custom content, applies dict id policy, pads for minimum repcode offset, and copies content into final position.
- `ZDICT_addEntropyTablesFromBuffer()` and its advanced helper add entropy tables to raw content already stored at the end of the output buffer.
- `ZDICT_trainFromBuffer_legacy()` duplicates samples with a noisy guard band and runs the older suffix-array-based segment selector.
- `ZDICT_trainFromBuffer()` is the default public trainer and delegates to `ZDICT_optimizeTrainFromBuffer_fastCover()` with `d = 8`, `steps = 4`, and default compression level.
- Legacy internals include `dictItem`, `ZDICT_analyzePos()`, `ZDICT_tryMerge()`, `ZDICT_trainBuffer_legacy()`, and `ZDICT_fillNoise()`.
- Entropy internals include `ZDICT_countEStats()`, `ZDICT_analyzeEntropy()`, `ZDICT_flatLit()`, and rep-offset helpers.

## Control Flow
The default trainer initializes a FASTCOVER parameter struct and calls optimized FASTCOVER. The legacy trainer first checks minimum corpus size, copies the concatenated samples, appends deterministic noise for safe overreads in match counting, and calls `ZDICT_trainFromBuffer_unsafe_legacy()`. That path allocates a candidate segment list, builds a suffix array with `divsufsort()`, analyzes repeated substrings, merges overlapping/included `dictItem`s, limits the selected content to the target size, copies selected segments from the end of the dictionary buffer backward, then adds entropy tables.

Dictionary finalization starts by writing the magic number and a dictionary id derived from `params.dictID` or an `XXH64` hash of the custom content. It calls `ZDICT_analyzeEntropy()`, which creates a raw-content `ZSTD_CDict`, compresses each sample block, extracts literal and sequence statistics from the compressor's sequence store, normalizes FSE counts, builds a HUF table, writes entropy tables, and writes starting rep offsets. `ZDICT_finalizeDictionary()` then shrinks content if header plus content exceeds capacity, pads if content is smaller than the maximum initial repcode, and writes header, padding, and content in overlap-safe order.

## State And Persistence
All state is transient except caller-provided dictionary buffers. Legacy training owns temporary suffix, reverse suffix, done-mark, file-position, guard-band, and dict-item allocations. Entropy analysis owns a `ZSTD_CDict`, `ZSTD_CCtx`, and block workspace while collecting statistics. The output dictionary buffer persists and contains the zstd dictionary magic, id, entropy tables, padding if needed, and content.

## Dependencies And Integration Points
This file depends on zstd common memory, FSE, HUF, internal compression structures, `XXH64`, `ZSTD_loadCEntropy()`, `ZSTD_compressBlock_deprecated()`, and `divsufsort.h`. It is the central integration point for `cover.c` and `fastcover.c`, which call `ZDICT_finalizeDictionary()` for selected content. It also exposes public dictionary helper functions declared in `zdict.h`.

## Risks And Edge Cases
- Legacy match counting intentionally reads through a noisy guard band; unsafe legacy internals require callers to provide that guard.
- The legacy trainer truncates sample sets above `ZDICT_MAX_SAMPLES_SIZE` because `divsufsort()` uses int-sized indexes.
- Entropy analysis uses deprecated/internal compression APIs and sequence-store layout; compressor-internal changes can break it.
- Very noisy or too-regular literal distributions can produce non-encodable HUF tables, so `ZDICT_flatLit()` substitutes a mostly flat distribution.
- `ZDICT_finalizeDictionary()` must handle overlapping `customDictContent` and `dictBuffer`; it uses `memmove()` before writing header/padding.
- If the computed entropy header leaves too little capacity, content is shrunk; if content is below initial repcode requirements, zero padding is inserted before content.
- `ZDICT_trainFromBuffer_legacy()` returns `0` rather than an error for too-small corpora, which callers may need to distinguish from a valid empty result.

## Test Signals
Tests should validate dictionary id extraction, header-size parsing, finalization with explicit and generated dict IDs, overlap-safe finalization, too-small destination handling, tiny/insufficient corpus behavior, entropy construction on noisy and repetitive corpora, and round-trip compression/decompression using finalized dictionaries. Legacy training should be exercised with sanitizer builds, suffix-array edge cases, and corpora near size limits. Default training tests should assert that the FASTCOVER path produces a usable dictionary.
<!-- END_FILE_RESEARCH: sources/compression/zstd/lib/dictBuilder/zdict.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/lib/dll/example/Makefile -->
# sources/compression/zstd/lib/dll/example/Makefile

## Purpose
This makefile builds a small Windows-oriented DLL/static-library comparison example for zstd's `fullbench.c` and `datagen.c`. It demonstrates linking the same benchmark source against either `libzstd_static.lib` or `libzstd.dll`.

## Important Targets And Variables
- `ZSTDDIR`, `LIBDIR`, and `DLLDIR` point to sibling include, static library, and DLL output directories.
- `CFLAGS`, `CPPFLAGS`, `LDFLAGS`, `MOREFLAGS`, and `FLAGS` assemble compiler and linker options, including warning flags and `-DXXH_NAMESPACE=ZSTD_`.
- `EXT` becomes `.exe` when `$(OS)` matches `Windows%`, otherwise empty.
- `all` builds `fullbench-dll` and `fullbench-lib`.
- `fullbench-lib` links `fullbench.c datagen.c` against `../static/libzstd_static.lib`.
- `fullbench-dll` defines `ZSTD_DLL_IMPORT=1` and links against `../dll/libzstd.dll`.
- `clean` removes both generated binaries.

## Control Flow
The default target delegates to `all`, which invokes the two concrete build targets. Each target compiles the same sources with shared flags but different link inputs and, for the DLL target, a DLL import macro. Platform-specific executable suffix selection occurs before target evaluation.

## State And Persistence
The makefile writes build artifacts `fullbench-dll$(EXT)` and `fullbench-lib$(EXT)` in the example directory. `clean` removes those artifacts. It does not generate dependency files or persist configuration.

## Dependencies And Integration Points
It expects `fullbench.c` and `datagen.c` to be present in the current directory and zstd include/static/DLL artifacts to exist at the configured relative paths. It integrates with standard `make`, `CC`, `RM`, and platform `OS` variables. `ZSTD_DLL_IMPORT=1` must match zstd's DLL import/export declarations.

## Risks And Edge Cases
- The static and DLL library paths use Windows-style `.lib`/`.dll` names even when `EXT` is empty, so non-Windows use may require adjusted artifacts.
- The `clean` recipe contains a trailing backslash before the `@echo` line, which can join commands unexpectedly depending on make/shell parsing.
- `VOID := /dev/null` is defined but unused.
- The makefile assumes relative directory layout after zstd has already built the static and DLL libraries.

## Test Signals
Build tests should run `make` after producing the expected zstd DLL/static artifacts, verify both binaries link, and run `make clean` to ensure generated files are removed without shell syntax errors. Windows/MSYS and non-Windows dry runs are useful because `EXT` and library naming are platform-sensitive.
<!-- END_FILE_RESEARCH: sources/compression/zstd/lib/dll/example/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/lib/install_oses.mk -->
# sources/compression/zstd/lib/install_oses.mk

## Purpose
`install_oses.mk` centralizes OS detection and the list of operating systems for which the zstd library makefiles support install targets.

## Important Variables
- `UNAME := $(shell sh -c 'MSYSTEM="MSYS" uname')` runs `uname` with `MSYSTEM` forced to `MSYS`, improving MSYS/Cygwin-style detection consistency.
- `INSTALL_OS_LIST ?= ...` defines the default supported OS patterns: Linux, Darwin, GNU variants, BSDs, SunOS, Haiku, AIX, MSYS_NT%, and CYGWIN_NT%.

## Control Flow
The file is intended to be included by other makefiles. Inclusion evaluates `UNAME` immediately and provides a default `INSTALL_OS_LIST` only if the including environment has not already set it.

## State And Persistence
There is no file output or persistent state. The included make variables affect target availability and conditional logic in parent makefiles.

## Dependencies And Integration Points
It depends on `sh` and `uname` being available. Parent makefiles can compare `$(UNAME)` against `$(INSTALL_OS_LIST)` to decide whether install/uninstall targets are valid. The `?=` assignment allows packaging systems or callers to override the OS allowlist.

## Risks And Edge Cases
- OS detection is pattern-based and may miss newer or niche systems unless `INSTALL_OS_LIST` is overridden.
- Forcing `MSYSTEM="MSYS"` changes `uname` behavior intentionally but can surprise callers expecting their existing MSYS flavor.
- Systems without POSIX `sh`/`uname` cannot evaluate `UNAME` as written.

## Test Signals
Makefile tests should include this file under representative `uname` outputs, verify `INSTALL_OS_LIST` override behavior, and check install-target conditionals on Linux, macOS, BSD, MSYS, and Cygwin environments.
<!-- END_FILE_RESEARCH: sources/compression/zstd/lib/install_oses.mk -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/lib/legacy/zstd_legacy.h -->
# sources/compression/zstd/lib/legacy/zstd_legacy.h

## Purpose
`zstd_legacy.h` is the internal dispatch layer for decoding pre-1.0 zstd frame formats. It detects legacy frame magic numbers, reports decompressed sizes and frame sizes where supported, performs one-shot legacy decompression, and manages streaming decompression contexts for supported legacy versions.

## Important APIs, Types, And Functions
- `ZSTD_LEGACY_SUPPORT` defaults to `8` when undefined or zero, which means no legacy version headers are included. Lower values include support down to that version.
- `ZSTD_isLegacy()` reads the first four bytes and returns a supported legacy version number 1..7 or `0`.
- `ZSTD_getDecompressedSize_legacy()` returns frame content size for versions 5..7 when their headers expose it, otherwise `0`.
- `ZSTD_decompressLegacy()` dispatches one-shot decompression to version-specific `ZSTDv0X_decompress` or `ZSTDv0X_decompress_usingDict()` implementations.
- `ZSTD_findFrameSizeInfoLegacy()` dispatches frame-size discovery and fills a `ZSTD_frameSizeInfo`, including `nbBlocks` when a decompressed bound is known.
- `ZSTD_findFrameCompressedSizeLegacy()` returns only the compressed-size component.
- `ZSTD_freeLegacyStreamContext()`, `ZSTD_initLegacyStream()`, and `ZSTD_decompressLegacyStream()` manage streaming decode contexts for versions 4..7.

## Control Flow
Compile-time `#if (ZSTD_LEGACY_SUPPORT <= N)` blocks include the version headers and compile the matching switch cases. Detection starts with `MEM_readLE32()` of the frame magic. One-shot decompression normalizes `NULL` zero-size pointers to a local dummy byte to avoid passing null into legacy decoders, then switches on detected version. Versions 1..4 use older no-dictionary APIs where available; versions 5..7 allocate a version-specific DCtx, decompress with optional dictionary, then free it.

Frame-size helpers dispatch to version-specific find functions and convert an oversized compressed-frame report into `ERROR(srcSize_wrong)`. Streaming initialization frees a previous context if the version changes, creates or reuses the version-specific ZBUFF DCtx, initializes it with the dictionary, and stores it through `legacyContext`. Streaming decompression advances `ZSTD_inBuffer.pos` and `ZSTD_outBuffer.pos` according to bytes consumed/produced by the version-specific continue call.

## State And Persistence
This is a header-only collection of `MEM_STATIC` functions. Persistent state exists only in caller-owned `legacyContext` pointers for streaming decompression. The implementation may allocate version-specific contexts in init and frees them through `ZSTD_freeLegacyStreamContext()`. One-shot version 5..7 decompression allocates and frees a temporary DCtx inside the call.

## Dependencies And Integration Points
It includes zstd common memory, private error helpers, and internal buffer/frame types. Depending on `ZSTD_LEGACY_SUPPORT`, it includes `zstd_v01.h` through `zstd_v07.h`. It integrates with the main decoder path to identify unsupported modern-vs-legacy frames, find frame sizes, and delegate decompression to archived decoders.

## Risks And Edge Cases
- The meaning of `ZSTD_LEGACY_SUPPORT` is inverted by threshold: `<= 5` includes v5 support, while the default `8` includes none.
- Versions 1..3 do not support streaming through this layer and return `ERROR(version_unsupported)` for stream operations.
- `ZSTD_getDecompressedSize_legacy()` returns `0` both for unknown size and for unsupported/non-legacy formats, so callers need additional detection when ambiguity matters.
- Header-only static functions increase compile-time coupling to legacy version headers and internal zstd types.
- Dummy-byte substitution for `NULL` zero-size buffers avoids legacy null handling issues but relies on assertions for consistency.
- If a legacy frame-size function returns a compressed size larger than available input, this layer rewrites it to `srcSize_wrong`.

## Test Signals
Tests should compile with multiple `ZSTD_LEGACY_SUPPORT` values, detect each supported magic number, reject unsupported versions, decompress known v1..v7 frames where enabled, validate dictionary paths for v5..v7, exercise streaming v4..v7 with chunked input/output, and check frame-size behavior for truncated inputs.
<!-- END_FILE_RESEARCH: sources/compression/zstd/lib/legacy/zstd_legacy.h -->
