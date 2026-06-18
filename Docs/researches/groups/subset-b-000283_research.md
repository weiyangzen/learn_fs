# Group Research: subset-b-000283

This grouped report covers the exact source files assigned to work item `subset-b-000283`. Each section is delimited for deterministic reconciliation into one source-tree-aligned per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/compression/lz4/lib/lz4hc.c -->
# sources/compression/lz4/lib/lz4hc.c

## Purpose
`lz4hc.c` implements LZ4 high-compression block and streaming compression. It is not an independent module: it includes or depends on shared `lz4.c` internals for byte access, match counting, wild copies, constants, memory allocation hooks, debug logging, and low-level format encoding.

## Important APIs, Types, And Functions
The public entry points are `LZ4_compress_HC`, `LZ4_compress_HC_extStateHC`, `LZ4_compress_HC_extStateHC_fastReset`, `LZ4_compress_HC_destSize`, `LZ4_createStreamHC`, `LZ4_freeStreamHC`, `LZ4_initStreamHC`, `LZ4_resetStreamHC`, `LZ4_resetStreamHC_fast`, `LZ4_setCompressionLevel`, `LZ4_favorDecompressionSpeed`, `LZ4_loadDictHC`, `LZ4_attach_HC_dictionary`, `LZ4_compress_HC_continue`, `LZ4_compress_HC_continue_destSize`, and `LZ4_saveDictHC`. Internally, `cParams_t` maps compression levels to strategies: `lz4mid` for level 2, hash-chain HC for levels 3-9, and optimal parsing for levels 10-12. `LZ4HC_match_t` carries match offset, length, and negative backtracking.

## Control Flow
The main dispatcher is `LZ4HC_compress_generic_internal()`: it validates sizes, advances `ctx->end`, selects the strategy, and marks the state dirty if compression fails. `LZ4MID_compress()` keeps 4-byte and 8-byte hash tables for a faster medium mode. `LZ4HC_compress_hashChain()` repeatedly finds best, second, and third matches and emits sequences through `LZ4HC_encodeSequence()`. `LZ4HC_compress_optimal()` builds a bounded dynamic-programming price table (`LZ4_OPT_NUM`) and reverse-walks it to encode the cheapest path.

## State, Persistence, And Dependencies
All persistent compression state is in `LZ4HC_CCtx_internal`: hash table, chain table, prefix bounds, external dictionary bounds, `nextToUpdate`, compression level, decompression-speed preference, dirty flag, and optional attached dictionary context. Streaming moves prior input from prefix to external dictionary when blocks are non-contiguous, trims history to the 64 KB LZ4 window, and rejects simultaneous ext-dict and dict-context use. There is no file persistence.

## Integration Points
The file backs the HC API declared by `lz4hc.h`, is linked into liblz4, is exercised by the CLI benchmark, and is heavily targeted by OSS-Fuzz HC and streaming harnesses. It integrates with regular LZ4 decompression because it emits standard LZ4 block sequences.

## Risks
The implementation is pointer- and integer-boundary sensitive: dictionary rollover, 2 GB index limits, 64 KB offsets, `fillOutput` truncation, and output-capacity rollback are key risk areas. Fast reset is only safe for coherent states; failures set `dirty` so the next reset must rebuild state. Compile-time memory access modes can trade portability for speed.

## Test Signals
Useful signals are round-trip tests across all compression levels, `destSize` partial-input behavior, streaming continuation with prefix and external dictionaries, attached dictionaries, tiny output buffers, large inputs near limits, failed compression followed by fast reset, and sanitizer builds with portable memory access.
<!-- END_FILE_RESEARCH: sources/compression/lz4/lib/lz4hc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/lz4/lib/lz4hc.h -->
# sources/compression/lz4/lib/lz4hc.h

## Purpose
`lz4hc.h` declares the stable and static-linking-only API for LZ4 high-compression mode. It exposes block compression, streaming compression, dictionary support, and compatibility wrappers for older HC names.

## Important APIs, Types, And Functions
The public constants define the supported level range: `LZ4HC_CLEVEL_MIN`, `LZ4HC_CLEVEL_DEFAULT`, `LZ4HC_CLEVEL_OPT_MIN`, and `LZ4HC_CLEVEL_MAX`. Block APIs include `LZ4_compress_HC()`, `LZ4_sizeofStateHC()`, `LZ4_compress_HC_extStateHC()`, and `LZ4_compress_HC_destSize()`. Streaming APIs use the opaque `LZ4_streamHC_t` and include create/free, reset, dictionary load/save, continue, continue-destSize, and `LZ4_attach_HC_dictionary()`.

## Control Flow
The header itself has no runtime control flow, but its comments define required call order: initialize or create a stream, optionally set the compression level before loading a dictionary, compress blocks with previous data still accessible, save history if prior buffers cannot remain stable, and reset before reusing a stream.

## State, Persistence, And Dependencies
The static-linking section reveals `LZ4HC_CCtx_internal` with hash and chain tables, prefix and dictionary pointers, window limits, compression level, flags, and attached dictionary context. The `LZ4_streamHC_t` union reserves `LZ4_STREAMHC_MINSIZE` bytes for static allocation. State is process memory only.

## Integration Points
The header includes `lz4.h`, shares `LZ4LIB_API` and deprecation machinery, and exposes experimental static APIs when `LZ4_HC_STATIC_LINKING_ONLY` is defined. CLI, fuzzers, and library consumers include this file for HC compression.

## Risks
Static-linking-only layout is explicitly unstable and must not be used for dynamic-library ABI. `LZ4_saveDictHC(NULL, nonzero)` is invalid. Streaming correctness depends on retaining previous input buffers or explicitly saving history. Deprecated functions are preserved but may have degraded behavior.

## Test Signals
Compile tests should cover public and static-linking modes, C and C++ inclusion, deprecated-warning suppression, static allocation through `LZ4_initStreamHC()`, and dictionary attach/load/save flows.
<!-- END_FILE_RESEARCH: sources/compression/lz4/lib/lz4hc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/lz4/lib/xxhash.c -->
# sources/compression/lz4/lib/xxhash.c

## Purpose
`xxhash.c` implements xxHash 0.6.5 for LZ4: fast non-cryptographic 32-bit and 64-bit hashes, streaming hash state, and canonical big-endian encodings.

## Important APIs, Types, And Functions
The exported functions are `XXH_versionNumber`, `XXH32`, `XXH32_createState`, `XXH32_freeState`, `XXH32_copyState`, `XXH32_reset`, `XXH32_update`, `XXH32_digest`, `XXH32_canonicalFromHash`, `XXH32_hashFromCanonical`, and equivalent `XXH64*` functions when 64-bit support is enabled. Internal primitives include endian-aware reads, rotate/swap helpers, prime constants, per-lane rounds, merge rounds, and final avalanche functions.

## Control Flow
One-shot hashing selects aligned or unaligned paths, normalizes endian behavior unless native format is forced, processes 16-byte chunks for XXH32 or 32-byte chunks for XXH64, then finalizes tail bytes with switch fallthrough. Streaming reset initializes accumulators from the seed, update buffers partial chunks in `mem32` or `mem64`, and digest finalizes without consuming state.

## State, Persistence, And Dependencies
`XXH32_state_t` tracks total length, large-length marker, four accumulators, a 16-byte scratch buffer, and `memsize`. `XXH64_state_t` tracks total length, four 64-bit accumulators, a 32-byte scratch buffer, and `memsize`. There is no persistent storage. Allocation and memory copy are wrapped locally around `malloc`, `free`, and `memcpy`.

## Integration Points
The CLI benchmark uses `XXH64` for data-integrity checks. Fuzz helpers use `XXH32` to seed deterministic random choices. The OSS-Fuzz Makefile namespaces symbols with `-DXXH_NAMESPACE=LZ4_` to avoid collisions.

## Risks
Compile-time switches can permit non-standard unaligned reads. By default, null input is an error for streaming update and unsafe for one-shot calls unless `XXH_ACCEPT_NULL_INPUT_POINTER` is enabled. These hashes are not cryptographic and should not be used for adversarial integrity or authentication.

## Test Signals
Important signals are known xxHash vectors, streaming versus one-shot equivalence, chunk-boundary updates around 16 and 32 bytes, canonical round trips, big-endian behavior, namespaced builds, and sanitizer builds with `XXH_FORCE_MEMORY_ACCESS=0`.
<!-- END_FILE_RESEARCH: sources/compression/lz4/lib/xxhash.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/lz4/lib/xxhash.h -->
# sources/compression/lz4/lib/xxhash.h

## Purpose
`xxhash.h` is the public declaration and optional inline implementation gateway for xxHash 0.6.5. It documents the algorithm, exposes one-shot and streaming APIs, and provides static-linking-only state definitions.

## Important APIs, Types, And Functions
The header defines `XXH_errorcode`, `XXH32_hash_t`, `XXH64_hash_t`, `XXH32_canonical_t`, `XXH64_canonical_t`, opaque `XXH32_state_t` and `XXH64_state_t`, version macros, and all `XXH32*`/`XXH64*` public functions. `XXH_INLINE_ALL` and `XXH_PRIVATE_API` convert definitions to static inline mode by including `xxhash.c`.

## Control Flow
There is no runtime control flow, but preprocessor flow is important. `XXH_NAMESPACE` rewrites public names, `XXH_NO_LONG_LONG` removes 64-bit APIs, and `XXH_STATIC_LINKING_ONLY` reveals state structs for stack allocation or embedding.

## State, Persistence, And Dependencies
The static section defines the exact state fields used by the implementation, including accumulators, temporary buffers, and reserved fields that should never be accessed. The header depends only on `stddef.h` for the normal public surface and `stdint.h` when static definitions use fixed-width types.

## Integration Points
This header is included by `xxhash.c`, fuzz helpers, and benchmark code. It is also safe for consumers that want namespaced or private inline copies to avoid public symbol conflicts.

## Risks
The static state layout is explicitly not stable API. Including with `XXH_INLINE_ALL` pulls the implementation into each translation unit, which is useful for speed but can cause duplicate-code bloat. Namespace macros require all users in a linkage unit to agree on symbol naming.

## Test Signals
Compile coverage should include normal dynamic declarations, namespaced declarations, `XXH_INLINE_ALL`, `XXH_NO_LONG_LONG`, C++ inclusion, canonical type sizes, and static state allocation.
<!-- END_FILE_RESEARCH: sources/compression/lz4/lib/xxhash.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/lz4/ossfuzz/Makefile -->
# sources/compression/lz4/ossfuzz/Makefile

## Purpose
This Makefile builds the LZ4 OSS-Fuzz targets either against libFuzzer through `LIB_FUZZING_ENGINE` or against the local standalone engine when that variable is empty.

## Important APIs, Types, And Functions
The main targets are the ten `*_fuzzer` binaries: block compression/decompression, HC variants, frame variants, round-trip variants, uncompressed frame update, and streaming. It builds `../lib/liblz4.a`, compiles each C file, and links common helper objects `lz4_helpers.o` and `fuzz_data_producer.o`.

## Control Flow
`all` expands to all fuzzers. Pattern rules compile `%.c` to `%.o` with LZ4 include paths, `LZ4_DEBUG`, `XXH_NAMESPACE=LZ4_`, and `FUZZING_BUILD_MODE_UNSAFE_FOR_PRODUCTION`. If no external fuzzing engine is supplied, `standaloneengine.o` is linked so corpus files can be run from the command line.

## State, Persistence, And Dependencies
Build outputs are local object files, fuzzer executables, and the static liblz4 archive. The Makefile consumes standard `CC`, `CXX`, `CFLAGS`, `CXXFLAGS`, `CPPFLAGS`, `LDFLAGS`, `EXT`, and `MOREFLAGS`.

## Integration Points
`ossfuzz.sh` invokes `make V=1 all` from this directory. The OSS-Fuzz project supplies compiler wrappers and `LIB_FUZZING_ENGINE`, while local development can use the standalone fallback.

## Risks
The clean target omits `round_trip_frame_uncompressed_fuzzer_clean`, leaving that binary or object behind. Helper objects are linked into every fuzzer even when a target does not use all helpers. Assertions are enabled through `LZ4_DEBUG`, so behavior differs from release builds.

## Test Signals
`make all`, `make clean`, builds with and without `LIB_FUZZING_ENGINE`, sanitizer builds, and one standalone corpus invocation for each fuzzer validate the file.
<!-- END_FILE_RESEARCH: sources/compression/lz4/ossfuzz/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/lz4/ossfuzz/compress_frame_fuzzer.c -->
# sources/compression/lz4/ossfuzz/compress_frame_fuzzer.c

## Purpose
This harness fuzzes `LZ4F_compressFrame()` with randomized frame preferences and possibly undersized output buffers. If compression succeeds, it requires the compressed frame to decompress exactly back to the input.

## Important APIs, Types, And Functions
`LLVMFuzzerTestOneInput()` uses `FUZZ_dataProducer_create()`, `FUZZ_dataProducer_preferences()`, `FUZZ_getRange_from_uint32()`, `LZ4F_compressFrameBound()`, `LZ4F_compressFrame()`, `LZ4F_isError()`, and `FUZZ_decompressFrame()`.

## Control Flow
The producer consumes control bytes from the end of the fuzz input to choose preferences and a destination-capacity seed. The remaining bytes are treated as payload. The destination size is selected from `[0, compressBound]`. Compression errors are accepted; successful frames are decompressed and compared with `memcmp`.

## State, Persistence, And Dependencies
State is per-input heap allocation for the producer, compressed buffer, and round-trip buffer. Frame decompression state is hidden inside `FUZZ_decompressFrame()`. There is no persistent corpus mutation or file state.

## Integration Points
The target links against liblz4 frame APIs and common fuzz helpers. It complements `round_trip_frame_fuzzer.c`, which always allocates enough output and expects compression success.

## Risks
The source pointer passed to compression remains the original `data`, while `size` is reduced after consuming producer bytes, so control bytes are still in the prefix of the compressed payload and only the tail of the input length is considered. Zero-size malloc behavior is asserted non-null, which can vary by C library.

## Test Signals
Useful findings include crashes on small output capacities, invalid successful frames, frame preference edge cases, checksum modes, and mismatches after decompression.
<!-- END_FILE_RESEARCH: sources/compression/lz4/ossfuzz/compress_frame_fuzzer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/lz4/ossfuzz/compress_fuzzer.c -->
# sources/compression/lz4/ossfuzz/compress_fuzzer.c

## Purpose
This harness fuzzes basic LZ4 block compression with destination buffers ranging from zero to the compression bound. It verifies round trips for successful compression and for `LZ4_compress_destSize()`.

## Important APIs, Types, And Functions
`LLVMFuzzerTestOneInput()` calls `LZ4_compressBound()`, `LZ4_compress_default()`, `LZ4_compress_destSize()`, `LZ4_decompress_safe()`, `FUZZ_dataProducer_retrieve32()`, and `FUZZ_getRange_from_uint32()`.

## Control Flow
The first producer value selects destination capacity. The remaining producer size becomes the effective input size. Regular compression may fail when the destination is too small; success must decompress to the full effective size. If `dstCapacity > 0`, `compress_destSize()` must succeed, update `compressedSize`, and decompress to exactly that prefix.

## State, Persistence, And Dependencies
Only per-call heap buffers and the producer are allocated. There is no shared state or filesystem behavior.

## Integration Points
This is the basic block-compressor OSS-Fuzz target and exercises the same block format later consumed by `decompress_fuzzer.c` and round-trip tests.

## Risks
Like other producer-based harnesses, control bytes are not advanced out of the `data` pointer, only out of the size. Zero-byte input and zero-byte output rely on platform malloc behavior because the harness asserts returned pointers. `size_t` inputs are narrowed to `int` in LZ4 calls, so practical fuzzing depends on OSS-Fuzz input-size limits.

## Test Signals
Strong signals are compression crashes, successful output that cannot decode, `destSize` returning non-positive for positive capacity, and corruption in decoded prefixes.
<!-- END_FILE_RESEARCH: sources/compression/lz4/ossfuzz/compress_fuzzer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/lz4/ossfuzz/compress_hc_fuzzer.c -->
# sources/compression/lz4/ossfuzz/compress_hc_fuzzer.c

## Purpose
This target fuzzes high-compression block APIs with variable compression levels and constrained destination sizes. It covers both normal HC compression and HC destination-size mode.

## Important APIs, Types, And Functions
The harness uses `LZ4_compress_HC()`, `LZ4_compress_HC_destSize()`, `LZ4_sizeofStateHC()`, `LZ4_decompress_safe()`, `LZ4HC_CLEVEL_MIN`, `LZ4HC_CLEVEL_MAX`, and producer helpers for capacity and level selection.

## Control Flow
Two producer values select destination capacity and HC level. Capacity is limited to `[0, size]`, increasing failure pressure. `LZ4_compress_HC()` may fail; successful output must decode to the effective input. When capacity is positive, the harness allocates an HC state, calls `LZ4_compress_HC_destSize()`, asserts success, and checks that the decoded bytes equal the consumed prefix.

## State, Persistence, And Dependencies
The only retained state is the temporary HC workspace allocated with `malloc(LZ4_sizeofStateHC())`. The library initializes that workspace inside the dest-size call. All buffers are freed before return.

## Integration Points
This target directly covers `lz4hc.c` block and fill-output paths. It complements `round_trip_hc_fuzzer.c`, which uses full compression bounds and requires normal HC compression success.

## Risks
`malloc(0)` behavior can affect assertions for zero-size buffers. The harness narrows `size_t` to `int` for library calls. Since capacity is capped at input size rather than `LZ4_compressBound()`, most incompressible cases stress failure cleanup and dirty-state handling.

## Test Signals
Useful signals are crashes, successful HC output that fails decompression, dest-size success with wrong consumed length, and state-size or alignment regressions.
<!-- END_FILE_RESEARCH: sources/compression/lz4/ossfuzz/compress_hc_fuzzer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/lz4/ossfuzz/decompress_frame_fuzzer.c -->
# sources/compression/lz4/ossfuzz/decompress_frame_fuzzer.c

## Purpose
This harness sends arbitrary bytes through LZ4 frame decompression in several option combinations to ensure malformed or partial frames do not crash the frame decoder.

## Important APIs, Types, And Functions
The local `decompress()` helper resets a `LZ4F_dctx` and calls either `LZ4F_decompress()` or static `LZ4F_decompress_usingDict()`. `LLVMFuzzerTestOneInput()` uses producer helpers to choose destination capacity and dictionary size, then toggles `LZ4F_decompressOptions_t.stableDst`.

## Control Flow
The harness consumes seeds, allocates a destination buffer up to four times input size and a zero-filled dictionary up to 64 KB, then runs four decompression attempts: no dictionary with unstable and stable destination, and dictionary with unstable and stable destination. Return values are intentionally ignored because invalid input is expected.

## State, Persistence, And Dependencies
One frame decompression context is reused across the four attempts, with explicit reset before each attempt. Dictionary contents are synthetic zero bytes. There is no persistent state beyond heap allocations.

## Integration Points
This target requires `LZ4F_STATIC_LINKING_ONLY` for dictionary decompression and links against frame internals. It exercises decoder paths that ordinary round-trip tests may not reach.

## Risks
The helper ignores consumed sizes and errors, so it is a crash-only target rather than a semantic validator. Zero-size allocations are asserted. Very large fuzz inputs can amplify allocation size through the `4 * size` capacity expression.

## Test Signals
Findings include decoder crashes, sanitizer errors, invalid memory reads under dictionary modes, and state-reset regressions between repeated decompression attempts.
<!-- END_FILE_RESEARCH: sources/compression/lz4/ossfuzz/decompress_frame_fuzzer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/lz4/ossfuzz/decompress_fuzzer.c -->
# sources/compression/lz4/ossfuzz/decompress_fuzzer.c

## Purpose
This harness fuzzes raw LZ4 block decompression and partial decompression with no dictionary, external dictionaries, and prefix-style dictionaries.

## Important APIs, Types, And Functions
It calls `LZ4_decompress_safe_usingDict()`, `LZ4_decompress_safe_partial()`, and `LZ4_decompress_safe_partial_usingDict()` across small and large dictionary configurations. `MIN` and `MAX` come from `fuzz_helpers.h`.

## Control Flow
The producer selects destination capacity in `[0, 4 * size]`. The harness allocates a backing dictionary large enough to hold a 64 KB dictionary plus the fuzz data, copies the fuzz data after the dictionary, and then performs eleven decompression attempts over raw input and prefix-addressed input. Return codes are ignored because malformed compressed data is expected.

## State, Persistence, And Dependencies
State is limited to per-input destination and dictionary buffers. The dictionary is zero-filled, and the input is copied behind it to create prefix layouts.

## Integration Points
This target stresses the block decoder paths that must safely reject arbitrary compressed data. It is a counterpart to the block compressor and round-trip harnesses.

## Risks
The `dictSize` computation uses `MAX(size + 1, 64 KB - 1)`, so it may allocate substantially more than the minimum for large fuzz inputs. The harness is crash-focused and does not validate expected negative return codes. Allocation of zero-byte destination buffers is asserted.

## Test Signals
Relevant signals are crashes, sanitizer out-of-bounds reports, unsafe dictionary boundary handling, and partial-decompression bugs with prefix and external dictionaries.
<!-- END_FILE_RESEARCH: sources/compression/lz4/ossfuzz/decompress_fuzzer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/lz4/ossfuzz/fuzz.h -->
# sources/compression/lz4/ossfuzz/fuzz.h

## Purpose
`fuzz.h` defines the common libFuzzer-style entry point signature and shared compile-time fuzzing parameters for LZ4 fuzz targets.

## Important APIs, Types, And Functions
The key declaration is `int LLVMFuzzerTestOneInput(const uint8_t *src, size_t size);`. The file also defines `FUZZ_RNG_SEED_SIZE` with a default of 4 bytes and documents build macros such as `LZ4_DEBUG`, `LZ4_FORCE_MEMORY_ACCESS`, and `FUZZING_BUILD_MODE_UNSAFE_FOR_PRODUCTION`.

## Control Flow
There is no runtime control flow. The preprocessor supplies default seed size when a build system has not provided one, and the C++ guard keeps the entry-point declaration linkable from C++ fuzzing engines.

## State, Persistence, And Dependencies
The file holds no state. It depends on `stddef.h` and `stdint.h` for the fuzzer signature.

## Integration Points
Every fuzz target or standalone engine includes this interface either directly or through `fuzz_helpers.h`. OSS-Fuzz and libFuzzer discover `LLVMFuzzerTestOneInput()` through this ABI.

## Risks
The comments refer to zstd in a couple of places even though this is LZ4, which can mislead maintainers about macro names. Changing `FUZZ_RNG_SEED_SIZE` changes corpus interpretation because helpers consume that many leading bytes as deterministic seed material.

## Test Signals
Build signals include C and C++ compilation, custom `FUZZ_RNG_SEED_SIZE` builds, and standalone engine linkage against a target implementing `LLVMFuzzerTestOneInput()`.
<!-- END_FILE_RESEARCH: sources/compression/lz4/ossfuzz/fuzz.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/lz4/ossfuzz/fuzz_data_producer.c -->
# sources/compression/lz4/ossfuzz/fuzz_data_producer.c

## Purpose
`fuzz_data_producer.c` implements a small deterministic input-consumption helper. Fuzz targets use it to derive sizes, compression levels, and frame preferences from the end of the input while preserving the remaining bytes as payload.

## Important APIs, Types, And Functions
The private `FUZZ_dataProducer_s` stores `data` and remaining `size`. Public functions create/free a producer, retrieve a 32-bit-ish seed, map seeds into inclusive ranges, build `LZ4F_frameInfo_t`, build `LZ4F_preferences_t`, and report remaining bytes.

## Control Flow
`FUZZ_dataProducer_retrieve32()` consumes from the tail. Empty input yields zero, inputs shorter than four bytes consume one byte, and inputs of at least four bytes subtract four from `size`. Range generation handles the full 32-bit span specially; otherwise it returns `min + seed % (range + 1)`. Frame preference generation derives block size, block mode, checksums, compression level, auto-flush, and decompression-speed preference.

## State, Persistence, And Dependencies
State is only the mutable remaining-size counter and the original data pointer. The helper allocates its state with `malloc` and frees it with `free`.

## Integration Points
Most OSS-Fuzz targets use this helper instead of `FUZZ_seed()` when they need several deterministic control values. It depends on `fuzz_helpers.h`, `lz4frame.h`, and `lz4hc.h`.

## Risks
For inputs of at least four bytes, `retrieve32()` returns only `*(data + size - 4)`, not a full little-endian 32-bit value, so entropy is much lower than the function name suggests. It also does not advance the data pointer, so callers must remember that only `remainingBytes()` changes.

## Test Signals
Unit tests should cover empty, 1-3 byte, and 4+ byte retrieval; inclusive range boundaries; full-span ranges; and valid frame preferences across all enum ranges.
<!-- END_FILE_RESEARCH: sources/compression/lz4/ossfuzz/fuzz_data_producer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/lz4/ossfuzz/fuzz_data_producer.h -->
# sources/compression/lz4/ossfuzz/fuzz_data_producer.h

## Purpose
This header declares the `FUZZ_dataProducer_t` abstraction used by fuzzers to consume deterministic configuration bytes from fuzz input.

## Important APIs, Types, And Functions
It forward-declares `FUZZ_dataProducer_t` and exposes creation, destruction, `FUZZ_dataProducer_retrieve32()`, `FUZZ_getRange_from_uint32()`, `FUZZ_dataProducer_range32()`, `FUZZ_dataProducer_preferences()`, `FUZZ_dataProducer_frameInfo()`, and `FUZZ_dataProducer_remainingBytes()`.

## Control Flow
There is no runtime control flow in the header. Its comments define the expected use: construct from input, retrieve control values, use remaining bytes as payload, then free the producer.

## State, Persistence, And Dependencies
The state layout is hidden in the `.c` file. The header includes standard integer and allocation headers plus `fuzz_helpers.h`, `lz4frame.h`, and `lz4hc.h` so preference-returning functions have complete types.

## Integration Points
Compression, HC, frame, decompression, and round-trip fuzzers include this header to share the same deterministic control-value generation.

## Risks
There are no include guards, so repeated inclusion relies on the included headers' guards and can still redeclare prototypes benignly. The API name `retrieve32` implies more entropy than the implementation currently provides. Callers may misread `remainingBytes()` as advancing `data`, but it only changes the size.

## Test Signals
Build coverage for repeated inclusion, C++ inclusion through wrappers, and behavior tests paired with the implementation are the main signals.
<!-- END_FILE_RESEARCH: sources/compression/lz4/ossfuzz/fuzz_data_producer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/lz4/ossfuzz/fuzz_helpers.h -->
# sources/compression/lz4/ossfuzz/fuzz_helpers.h

## Purpose
`fuzz_helpers.h` provides always-on assertions, deterministic seed generation, and a tiny pseudo-random generator for the LZ4 fuzz harnesses.

## Important APIs, Types, And Functions
Key macros are `FUZZ_ASSERT_MSG`, `FUZZ_ASSERT`, `FUZZ_STATIC`, `MIN`, and `MAX`. Inline helpers are `FUZZ_seed()`, `FUZZ_rand()`, and `FUZZ_rand32()`. `FUZZ_seed()` hashes up to `FUZZ_RNG_SEED_SIZE` leading bytes with `XXH32` and advances the caller's input pointer and size.

## Control Flow
Assertions print file, line, failed expression, and message to stderr, then abort. `FUZZ_rand()` updates a 32-bit state with multiply/add/rotate and returns high bits. `FUZZ_rand32()` maps that value into an inclusive range.

## State, Persistence, And Dependencies
The helper stores no global state. PRNG state is caller-owned. It includes `fuzz.h`, `xxhash.h`, standard headers, and, when needed, `lz4.c` with `LZ4_COMMONDEFS_ONLY` to access shared LZ4 debug and memory definitions.

## Integration Points
All fuzz targets use these assertions and many use the RNG. `round_trip_stream_fuzzer.c` relies on `FUZZ_seed()` for deterministic stream slicing and dictionary choices.

## Risks
`FUZZ_rand32()` assumes `max >= min` and that `(max - min + 1)` does not wrap unexpectedly. The header defines generic `MIN` and `MAX`, which can collide with other headers. Including `lz4.c` internals from a header is convenient but sensitive to compile-unit macro ordering.

## Test Signals
Useful signals include deterministic output for fixed seeds, seed consumption behavior, assertion failure formatting, sanitizer builds, and compile tests with `LZ4_SRC_INCLUDED` already defined.
<!-- END_FILE_RESEARCH: sources/compression/lz4/ossfuzz/fuzz_helpers.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/lz4/ossfuzz/lz4_helpers.c -->
# sources/compression/lz4/ossfuzz/lz4_helpers.c

## Purpose
`lz4_helpers.c` implements shared LZ4-frame helper routines for fuzz targets: randomized frame preferences and a strict one-shot frame decompression validator.

## Important APIs, Types, And Functions
`FUZZ_randomFrameInfo()` generates `LZ4F_frameInfo_t` from a `FUZZ_rand32()` seed. `FUZZ_randomPreferences()` wraps that in `LZ4F_preferences_t` and chooses compression level, auto-flush, and decompression-speed preference. `FUZZ_decompressFrame()` creates a decompression context, calls `LZ4F_decompress()` with `stableDst=1`, asserts full success and full input consumption, frees the context, and returns regenerated size.

## Control Flow
Preference generation chooses values from valid enum ranges and normalizes a below-minimum block size to default. Decompression initializes options to zero, sets stable destination, performs a single decompress call, and aborts if the frame is incomplete, erroneous, or not fully consumed.

## State, Persistence, And Dependencies
All state is local to the call. `FUZZ_decompressFrame()` owns one temporary `LZ4F_dctx`. There is no persistent data or global state.

## Integration Points
Frame compression and round-trip fuzzers use this helper to verify successful frame outputs. The data-producer implementation mirrors much of the random-preference logic for producer-driven fuzzers.

## Risks
`FUZZ_decompressFrame()` assumes the whole frame can be decompressed in one call and that the destination is large enough; it is suitable for validation of known-good compressed frames, not arbitrary malformed input. It asserts context creation but does not inspect the return code from `LZ4F_createDecompressionContext()`.

## Test Signals
Round trips with each block mode, checksum flag, block size, HC level, and auto-flush setting validate these helpers. Negative tests should confirm malformed frames abort through assertions.
<!-- END_FILE_RESEARCH: sources/compression/lz4/ossfuzz/lz4_helpers.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/lz4/ossfuzz/lz4_helpers.h -->
# sources/compression/lz4/ossfuzz/lz4_helpers.h

## Purpose
This header declares LZ4-specific helper functions shared by frame fuzzers.

## Important APIs, Types, And Functions
It declares `FUZZ_randomFrameInfo()`, `FUZZ_randomPreferences()`, and `FUZZ_decompressFrame()`. The first two take a mutable random seed; the decompression helper accepts destination buffer/capacity and source frame/size.

## Control Flow
There is no runtime control flow in the header. The include guard is `LZ4_HELPERS`, and `lz4frame.h` supplies frame types.

## State, Persistence, And Dependencies
The header stores no state. All state is owned by the implementation or caller. It depends on `uint32_t` being visible from prior includes in some translation units, because it includes `lz4frame.h` but not `stdint.h` directly.

## Integration Points
Frame fuzz targets include this header to avoid duplicating preference selection and strict decompression checks.

## Risks
The guard name is broad and could collide with unrelated code. Missing a direct `stdint.h` include makes the header less self-contained. `FUZZ_decompressFrame()`'s strict semantics should not be used for arbitrary input fuzzing where errors are expected.

## Test Signals
A standalone compile of this header, plus frame round-trip fuzz runs using each declared function, covers the expected behavior.
<!-- END_FILE_RESEARCH: sources/compression/lz4/ossfuzz/lz4_helpers.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/lz4/ossfuzz/ossfuzz.sh -->
# sources/compression/lz4/ossfuzz/ossfuzz.sh

## Purpose
`ossfuzz.sh` is the build entry point called by the Google OSS-Fuzz project to compile and export LZ4 fuzz targets.

## Important APIs, Types, And Functions
The script uses environment variables supplied by OSS-Fuzz: `CC`, `CXX`, `LIB_FUZZING_ENGINE`, `CFLAGS`, `CXXFLAGS`, and `OUT`. It sets `BUILD_ROOT` and appends a parallel job count to `MAKEFLAGS`.

## Control Flow
With `bash -eu`, the script prints build settings, sets `MAKEFLAGS` to use `nproc`, enters the `ossfuzz` directory, runs `make V=1 all`, returns to the repository root, and copies all `ossfuzz/*_fuzzer` binaries into `$OUT`.

## State, Persistence, And Dependencies
It writes build artifacts under `ossfuzz/` and final fuzzers under the OSS-Fuzz output directory. It depends on GNU make, bash, `nproc`, and the OSS-Fuzz compiler environment.

## Integration Points
OSS-Fuzz project Dockerfiles invoke this script during `build_fuzzers`. `travisoss.sh` regression-tests the script by building through OSS-Fuzz infrastructure.

## Risks
`export MAKEFLAGS+="-j$(nproc)"` assumes bash support and a working `nproc`. Copying `*_fuzzer` assumes executable names have no extension. `BUILD_ROOT` is set but not consumed by the script itself.

## Test Signals
The main validation is a full OSS-Fuzz `build_fuzzers lz4` run, plus local script execution with fake `OUT` and both empty and non-empty `LIB_FUZZING_ENGINE`.
<!-- END_FILE_RESEARCH: sources/compression/lz4/ossfuzz/ossfuzz.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/lz4/ossfuzz/round_trip_frame_fuzzer.c -->
# sources/compression/lz4/ossfuzz/round_trip_frame_fuzzer.c

## Purpose
This harness requires LZ4 frame compression to succeed with ample output capacity, then verifies exact decompression back to the input.

## Important APIs, Types, And Functions
It uses `FUZZ_dataProducer_preferences()`, `LZ4F_compressFrameBound()`, `LZ4_compressBound()`, `LZ4F_compressFrame()`, `LZ4F_isError()`, `FUZZ_decompressFrame()`, and `memcmp()`.

## Control Flow
The producer derives frame preferences and the remaining size. The harness allocates a destination using a conservative frame bound over `LZ4_compressBound(size)` and a round-trip buffer for the remaining bytes. Compression is asserted successful; decompression size and content must match.

## State, Persistence, And Dependencies
All state is local heap memory plus the producer. The strict frame decompression context is created inside `FUZZ_decompressFrame()`.

## Integration Points
This target validates the normal success path for frame compression under fuzzed preferences. It complements `compress_frame_fuzzer.c`, which intentionally allows too-small outputs.

## Risks
The original `data` pointer is not advanced after producer consumption, only `size` is reduced, so the tested payload starts at the beginning of the fuzz buffer with a shorter length. The destination bound is larger than necessary, which is safe but may reduce pressure on boundary conditions.

## Test Signals
Signals are frame-compression errors despite sufficient space, strict decompression failures, checksum regressions, and content corruption across preference combinations.
<!-- END_FILE_RESEARCH: sources/compression/lz4/ossfuzz/round_trip_frame_fuzzer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/lz4/ossfuzz/round_trip_frame_uncompressed_fuzzer.c -->
# sources/compression/lz4/ossfuzz/round_trip_frame_uncompressed_fuzzer.c

## Purpose
This target fuzzes the frame API sequence that mixes compressed updates with an explicitly uncompressed block segment, then verifies the whole frame round trips.

## Important APIs, Types, And Functions
The file uses `LZ4F_createCompressionContext()`, `LZ4F_compressBegin()`, `LZ4F_compressUpdate()`, `LZ4F_uncompressedUpdate()`, `LZ4F_compressEnd()`, `LZ4F_decompress()`, and `LZ4F_freeCompressionContext()`. It also includes `lz4frame_static.h` for the uncompressed-update API.

## Control Flow
`compress_independent_block_mode()` builds producer-driven preferences and forces independent block mode. `compress_round_trip()` consumes seeds to choose an uncompressed slice, emits a frame header, compresses bytes before the slice, writes the slice uncompressed, compresses bytes after it, ends the frame, then loops `LZ4F_decompress()` until completion and compares against the original.

## State, Persistence, And Dependencies
State is the producer, compression context, decompression context, compressed buffer, and round-trip buffer. There is no filesystem persistence.

## Integration Points
This target exercises a frame static API not covered by simple `LZ4F_compressFrame()` fuzzers and specifically requires block-independent frames.

## Risks
The decompression helper advances `dstPtr` without explicit final size comparison; corruption is caught by full `memcmp`, but overrun protection depends on `LZ4F_decompress()` respecting capacity. As with other producer harnesses, size is reduced but `data` is not pointer-advanced. The producer is freed inside `compress_round_trip()`, so callers must not reuse it.

## Test Signals
Useful signals include uncompressed block encoding crashes, invalid mixed frames, decompression loop stalls, and corruption around the uncompressed slice boundaries.
<!-- END_FILE_RESEARCH: sources/compression/lz4/ossfuzz/round_trip_frame_uncompressed_fuzzer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/lz4/ossfuzz/round_trip_fuzzer.c -->
# sources/compression/lz4/ossfuzz/round_trip_fuzzer.c

## Purpose
This harness validates raw LZ4 block compression, full decompression, and partial decompression under multiple dictionary pointer configurations.

## Important APIs, Types, And Functions
It uses `LZ4_compress_default()`, `LZ4_decompress_safe()`, `LZ4_decompress_safe_partial()`, and `LZ4_decompress_safe_partial_usingDict()` with no dictionary, small and large prefix dictionaries, and small and large external dictionaries.

## Control Flow
The producer chooses a partial-output size. Compression is done into a buffer preceded by a large prefix area. Full decompression must match the input. Then six partial-decompression variants decode exactly `partialCapacity` bytes and compare that prefix with the original.

## State, Persistence, And Dependencies
The harness allocates one compressed buffer with prefix space, one external dictionary buffer, one full round-trip buffer, and separate partial buffers for each variant. State is not retained between inputs.

## Integration Points
This is the success-path counterpart to `decompress_fuzzer.c`, proving that valid compressed blocks remain decodable across partial and dictionary APIs.

## Risks
The prefix buffers are allocated but not initialized before being offered as dictionaries; for this compressed data they should not be referenced, but the setup may still exercise decoder assumptions. Zero partial capacity leads to `malloc(0)` assertions. Dictionary content is unrelated to the block unless generated references require it.

## Test Signals
Signals include compression failure despite bounded output, full round-trip corruption, partial decode length mismatch, and dictionary-mode partial decode regressions.
<!-- END_FILE_RESEARCH: sources/compression/lz4/ossfuzz/round_trip_fuzzer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/lz4/ossfuzz/round_trip_hc_fuzzer.c -->
# sources/compression/lz4/ossfuzz/round_trip_hc_fuzzer.c

## Purpose
This harness validates high-compression LZ4 block round trips for fuzzed input and fuzzed HC compression levels.

## Important APIs, Types, And Functions
It uses `FUZZ_dataProducer_range32()` for the level, `LZ4_compressBound()`, `LZ4_compress_HC()`, `LZ4_decompress_safe()`, and HC level constants.

## Control Flow
The producer consumes a level from `[LZ4HC_CLEVEL_MIN, LZ4HC_CLEVEL_MAX]` and leaves the remaining byte count as input size. Destination capacity is the standard compression bound, so HC compression is expected to succeed. The decoded result must match exactly.

## State, Persistence, And Dependencies
All state is local: producer, compressed buffer, and round-trip buffer. The HC compressor uses its own internal temporary state through `LZ4_compress_HC()`.

## Integration Points
This is the strict success-path target for `lz4hc.c` block compression and complements `compress_hc_fuzzer.c`, which stresses undersized outputs and `destSize`.

## Risks
`data` is not advanced after producer consumption, so the payload includes leading control bytes with reduced length. Zero-size buffers depend on malloc behavior. The target does not exercise streaming HC dictionaries.

## Test Signals
Signals include HC compression failure with compression-bound capacity, decompression failure, corruption, and level-specific regressions between hash-chain and optimal-parser modes.
<!-- END_FILE_RESEARCH: sources/compression/lz4/ossfuzz/round_trip_hc_fuzzer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/lz4/ossfuzz/round_trip_stream_fuzzer.c -->
# sources/compression/lz4/ossfuzz/round_trip_stream_fuzzer.c

## Purpose
This harness fuzzes streaming compression and decompression for both fast LZ4 and HC LZ4, including prefix mode, external dictionary mode, loaded dictionaries, and attached dictionary streams.

## Important APIs, Types, And Functions
It defines cursor structs and `state_t` to hold fast and HC compression streams, a decode stream, input, compressed output, round-trip output, seed, and HC level. It uses `LZ4_createStream()`, `LZ4_createStreamHC()`, `LZ4_createStreamDecode()`, `LZ4_resetStream_fast()`, `LZ4_resetStreamHC_fast()`, `LZ4_compress_fast_continue()`, `LZ4_compress_HC_continue()`, `LZ4_decompress_safe_continue()`, `LZ4_loadDict()`, `LZ4_loadDictHC()`, `LZ4_attach_dictionary()`, and `LZ4_attach_HC_dictionary()`.

## Control Flow
`LLVMFuzzerTestOneInput()` consumes a deterministic seed, creates state, then runs eight round-trip modes. Each mode resets streams to the same seed, may trim a dictionary prefix into the expected output, compresses random chunk sizes, immediately decompresses each emitted block, and finally compares the rebuilt data against the original.

## State, Persistence, And Dependencies
State is explicit in `state_t` and is recreated per fuzz input. Some modes copy input into a second buffer and alternate source addresses to force external dictionary behavior. No file state is used.

## Integration Points
This is the deepest OSS-Fuzz coverage for streaming APIs in `lz4.c` and `lz4hc.c`, including static-linking-only attach APIs.

## Risks
`state_create()` asserts `state.cstream` twice and never asserts `state.cstreamHC`, so HC stream allocation failure would not be caught at the intended point. Random chunk size can be zero; compression APIs must handle that consistently. Output buffer sizing uses a margin rather than exact proof.

## Test Signals
Signals include stream reset bugs, dictionary attach/load mismatches, ext-dict boundary errors, decompression continuation failures, and corruption after alternating source buffers.
<!-- END_FILE_RESEARCH: sources/compression/lz4/ossfuzz/round_trip_stream_fuzzer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/lz4/ossfuzz/standaloneengine.c -->
# sources/compression/lz4/ossfuzz/standaloneengine.c

## Purpose
`standaloneengine.c` provides a minimal command-line runner for fuzz targets when libFuzzer or another fuzzing engine is not linked.

## Important APIs, Types, And Functions
The only function is `main()`. It opens each filename argument, reads the whole file into a heap buffer, and calls `LLVMFuzzerTestOneInput(buffer, buffer_len)` from `fuzz.h`.

## Control Flow
For each argument, the runner prints the file name, opens it in binary mode, seeks to the end to get length with `ftell()`, seeks back, allocates a zeroed buffer with `calloc()`, reads the full file, invokes the fuzzer, frees the buffer, closes the file, and continues to the next argument. Open and allocation failures are reported to stderr.

## State, Persistence, And Dependencies
State is local file handles and heap buffers. It does not write files or maintain corpus state. It depends on standard C file I/O and allocation.

## Integration Points
The OSS-Fuzz Makefile links this object into every fuzzer when `LIB_FUZZING_ENGINE` is empty, enabling local reproduction with `./target_fuzzer corpus_file`.

## Risks
The code does not check `fseek()`, `ftell()` errors, or short `fread()` results. `ftell()` is stored in `size_t`, which can mishandle negative errors and very large files. Empty files allocate zero bytes with `calloc(0, ...)`; if that returns null, the fuzzer is skipped.

## Test Signals
Run a standalone fuzzer against existing corpus files, missing paths, empty files, and large files. Sanitizer runs can catch allocation and file-size edge cases.
<!-- END_FILE_RESEARCH: sources/compression/lz4/ossfuzz/standaloneengine.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/lz4/ossfuzz/travisoss.sh -->
# sources/compression/lz4/ossfuzz/travisoss.sh

## Purpose
`travisoss.sh` regression-tests the OSS-Fuzz integration by cloning the OSS-Fuzz repository and building LZ4 fuzzers through its Docker-based helper workflow.

## Important APIs, Types, And Functions
The script uses `git clone`, `sed -i`, and `python infra/helper.py build_image --pull lz4` followed by `python infra/helper.py build_fuzzers lz4`. It reads Travis CI variables `TRAVIS_PULL_REQUEST`, `TRAVIS_BRANCH`, `TRAVIS_PULL_REQUEST_BRANCH`, and `TRAVIS_PULL_REQUEST_SLUG`.

## Control Flow
With `set -ex`, the script clones OSS-Fuzz into `/tmp/ossfuzz`, checks that the LZ4 project exists, rewrites the project Dockerfile to build the current branch or pull-request branch, then invokes OSS-Fuzz image and fuzzer builds.

## State, Persistence, And Dependencies
It writes a full clone under `/tmp/ossfuzz` and mutates `/tmp/ossfuzz/projects/lz4/Dockerfile`. It depends on git, Docker-capable OSS-Fuzz helper scripts, Python, GNU sed behavior, and Travis environment variables.

## Integration Points
This script validates `ossfuzz.sh` and the upstream OSS-Fuzz project configuration against the current LZ4 branch or PR.

## Risks
It is Travis-specific and may not work unchanged in other CI systems. `sed -i` syntax is GNU-style. The script always clones into a fixed `/tmp/ossfuzz` path and does not clean it first.

## Test Signals
Successful image and fuzzer builds are the primary signal. Failure to find the LZ4 project, Dockerfile rewrite errors, or helper build failures indicate integration drift.
<!-- END_FILE_RESEARCH: sources/compression/lz4/ossfuzz/travisoss.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/lz4/programs/Makefile -->
# sources/compression/lz4/programs/Makefile

## Purpose
This Makefile builds, installs, and cleans the LZ4 command-line programs: `lz4`, `lz4c`, `unlz4`, `lz4cat`, no-multithread variants, and selected platform-specific binaries.

## Important APIs, Types, And Functions
It derives library version macros from `../lib/lz4.h`, gathers library and program C sources, sets warning and optimization flags, includes shared make definitions from `../build/make`, detects pthread support, and defines targets for release builds, 32-bit builds, symlink aliases, manpage generation, installation, and uninstall.

## Control Flow
The default target is `lz4-release`, which disables debug flags and defines `NDEBUG`. `all` builds the main aliases. The `c_program` macro from included makefiles creates link rules. Thread support is detected by compiling a small `pthread.h` test; if available, `lz4` receives `-DLZ4IO_MULTITHREAD` and `-pthread`.

## State, Persistence, And Dependencies
Build state includes object files, executables, symlinks or copies, generated Windows resources, and generated manpage `lz4.1`. Install/uninstall writes under `DESTDIR`, `bindir`, and `man1dir`. It depends on sed, make helpers, compiler tooling, optional pthreads, optional ronn, and platform variables.

## Integration Points
This is the build surface for the user-facing CLI and benchmark code. It links lib sources directly by default and has `lz4-wlib` for dynamic-library linkage that exposes unstable symbols.

## Risks
Thread detection writes `have_pthread.c` in the working directory and may race under concurrent builds. Platform branches depend on included makefiles. `lz4-wlib` warns that it needs an extended dynamic library exposing unstable symbols.

## Test Signals
Run `make`, `make all`, `make lz4-nomt`, `make clean`, `make install DESTDIR=...`, `make uninstall DESTDIR=...`, and platform builds with and without pthread support.
<!-- END_FILE_RESEARCH: sources/compression/lz4/programs/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/lz4/programs/bench.c -->
# sources/compression/lz4/programs/bench.c

## Purpose
`bench.c` implements the LZ4 command-line benchmark engine. It measures compression and decompression speed, compression ratio, dictionary effects, checksum correctness, decode-only frame speed, and synthetic lorem-ipsum input when no files are supplied.

## Important APIs, Types, And Functions
Public setters include `BMK_setNotificationLevel`, `BMK_setAdditionalParam`, `BMK_setNbSeconds`, `BMK_setBlockSize`, `BMK_setBenchSeparately`, `BMK_setDecodeOnlyMode`, and `BMK_skipChecksums`. The main public entry point is `BMK_benchFiles()`. Internally, `compressionParameters` selects no-stream, fast-stream, or HC-stream functions. `BMK_benchMem()` performs timed loops and validation. Helpers load files, choose max memory, run level ranges, and generate synthetic data.

## Control Flow
`BMK_benchFiles()` clamps levels, optionally loads the last 64 KB of a dictionary file, then benchmarks files together, separately, or synthetic data. `BMK_benchMem()` splits input into blocks, allocates compressed and result buffers, initializes compression state, times repeated compression loops and decompression loops, adapts loop counts toward one-second runs, prints progress, and verifies XXH64 checksums unless decode-only mode is active.

## State, Persistence, And Dependencies
Global settings control display level, duration, block size, separate-file mode, decode-only mode, checksum skipping, and an output-format parameter. `g_dctx` is a process-global frame decompression context and is not freed in this file. Persistent state is limited to reading input and dictionary files; benchmark results are printed.

## Integration Points
The CLI calls this module through `bench.h`. It depends on platform utilities, timing helpers, lorem generation, `xxhash.h`, `lz4.h`, `lz4hc.h`, and `lz4frame.h`. It exercises both normal and HC compression APIs, streaming dictionary attach APIs, and frame decompression for decode-only benchmarks.

## Risks
The code exits the process on many errors through `END_PROCESS()`, so it is not library-friendly. Memory sizing is complex and depends on `LZ4_MAX_INPUT_SIZE`, `maxMemory`, block count, and decode multiplier. `LZ4_isError(errcode)` is defined as `errcode == 0` for compression return values, which is local and easy to confuse with frame error semantics.

## Test Signals
Run synthetic benchmarks, multi-file benchmarks, separate-file mode, custom block sizes, dictionary benchmarks, HC level ranges, decode-only frame benchmarks with and without checksum skipping, quiet output mode, and checksum-corruption tests.
<!-- END_FILE_RESEARCH: sources/compression/lz4/programs/bench.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/lz4/programs/bench.h -->
# sources/compression/lz4/programs/bench.h

## Purpose
`bench.h` declares the public interface from the CLI into the LZ4 benchmark engine implemented by `bench.c`.

## Important APIs, Types, And Functions
The main function is `BMK_benchFiles(const char** fileNamesTable, unsigned nbFiles, int cLevelStart, int cLevelLast, const char* dictFileName)`. Configuration setters control benchmark duration, block size, verbosity, separate-file reporting, decode-only mode, checksum skipping, and an additional hidden formatting parameter.

## Control Flow
The header has no runtime control flow. Its comments define how `BMK_benchFiles()` treats file arrays, compression level ranges, optional dictionaries, and aggregate versus separate reporting.

## State, Persistence, And Dependencies
The header includes `stddef.h` for `size_t`. Runtime state is maintained inside `bench.c` globals after callers invoke the setters. File and dictionary persistence is handled by the implementation.

## Integration Points
The LZ4 CLI includes this header to configure and invoke benchmarks. It isolates benchmark configuration from command-line parsing code.

## Risks
The API is process-global rather than context-based, so concurrent benchmark sessions cannot have independent settings. Decode-only mode and checksum skipping are version-commented but not capability-checked in the header. `BMK_setAdditionalParam()` is intentionally hidden and output-format oriented.

## Test Signals
Compile inclusion from the CLI, setter invocation before and after benchmark calls, level-range behavior, dictionary argument handling, and decode-only option combinations are the relevant signals.
<!-- END_FILE_RESEARCH: sources/compression/lz4/programs/bench.h -->
