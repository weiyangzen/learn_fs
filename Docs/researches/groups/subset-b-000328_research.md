# subset-b-000328 research

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/tests/fuzz/fuzz_helpers.h -->
# sources/compression/zstd/tests/fuzz/fuzz_helpers.h

## Purpose

`fuzz_helpers.h` is the common C/C++ header for zstd fuzz targets. It centralizes always-on assertions, small utility macros, and allocation/comparison helper declarations so libFuzzer targets fail loudly on invariant violations even in release-style builds.

## Important APIs, Types, And Macros

The public surface is intentionally compact: `FUZZ_malloc()`, `FUZZ_malloc_rand()`, and `FUZZ_memcmp()` are declared for fuzz harness allocation and NULL-tolerant comparison. `FUZZ_ASSERT_MSG()`, `FUZZ_ASSERT()`, and `FUZZ_ZASSERT()` abort on failed predicates or zstd error codes; `FUZZ_ZASSERT()` converts zstd error returns through `ZSTD_getErrorName()`.

`MIN()` and `MAX()` provide local arithmetic helpers used across the fuzz directory. `FUZZ_STATIC` normalizes an unused static-inline declaration across GCC, C99/C++, MSVC, and fallback C compilers. `FUZZ_QUOTE()` stringifies assertion expressions for diagnostics.

## Control Flow

The header itself has no runtime control flow beyond assertion macro expansion. A failed `FUZZ_ASSERT_MSG()` writes file, line, condition text, and an optional message to `stderr`, then calls `abort()`. Successful assertions evaluate to a no-op expression. Callers are expected to use `FUZZ_ZASSERT()` immediately after zstd API calls whose successful result is required for the current fuzz invariant.

## State And Persistence

This file owns no persistent state. It depends on the implementation of the declared helpers elsewhere in the fuzz support code. Allocation semantics matter: `FUZZ_malloc()` may return `NULL` for size zero, while `FUZZ_malloc_rand()` may return a random pointer for size zero and warns callers to free only when the requested size was positive.

## Dependencies And Integration Points

It includes zstd fuzz infrastructure (`fuzz.h`, `fuzz_data_producer.h`), diagnostics (`debug.h`), hashing (`xxhash.h`), and the public zstd API (`zstd.h`). It is included by most fuzz targets in this directory and forms the bridge between arbitrary fuzzer inputs and hard process-failing correctness checks.

## Risks And Edge Cases

`MIN()` and `MAX()` evaluate arguments more than once, so callers must avoid side effects. `FUZZ_malloc_rand()` intentionally permits invalid-looking zero-size pointers, so consumers must preserve the size guard when freeing. Because assertions call `abort()`, any false positive invariant or unexpected zstd error becomes a crash signal in fuzzing and regression replay.

## Test Signals

The useful signal is indirect: fuzz targets using this header should crash with readable diagnostics on corruption, bad zstd return codes, allocation failures, or mismatched round trips. Compiler coverage should include C and C++ builds, GCC/Clang/MSVC-style inline handling, and zero-size allocation paths.
<!-- END_FILE_RESEARCH: sources/compression/zstd/tests/fuzz/fuzz_helpers.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/tests/fuzz/fuzz_third_party_seq_prod.h -->
# sources/compression/zstd/tests/fuzz/fuzz_third_party_seq_prod.h

## Purpose

`fuzz_third_party_seq_prod.h` defines the optional plugin ABI that lets external zstd sequence-producer implementations be linked into zstd fuzzers. It documents how a plugin author supplies setup, teardown, state allocation, state free, and sequence production symbols that replace the default test producer when `FUZZ_THIRD_PARTY_SEQ_PROD` is enabled.

## Important APIs And Types

The required plugin hooks are `FUZZ_seqProdSetup()`, `FUZZ_seqProdTearDown()`, `FUZZ_createSeqProdState()`, `FUZZ_freeSeqProdState()`, and `FUZZ_thirdPartySeqProd()`. The producer signature matches `ZSTD_sequenceProducer_F`: it receives a plugin state pointer, output `ZSTD_Sequence` array and capacity, source and dictionary buffers, compression level, and window size.

`FUZZ_SEQ_PROD_SETUP()` and `FUZZ_SEQ_PROD_TEARDOWN()` are internal harness macros. When `FUZZ_THIRD_PARTY_SEQ_PROD` is defined, setup asserts successful global setup and non-NULL state creation, storing the result in `FUZZ_seqProdState`; teardown asserts state destruction and global teardown success. When the macro is not defined, both expand to no-ops.

## Control Flow

Fuzz targets call `FUZZ_SEQ_PROD_SETUP()` near the start of `LLVMFuzzerTestOneInput()` and `FUZZ_SEQ_PROD_TEARDOWN()` before returning. The actual producer is registered by helper code through `ZSTD_registerSequenceProducer()`, using the state pointer created here. The header assumes each test case uses one shared state object and notes that current fuzzers do not exercise multi-threaded sequence-producer scenarios.

## State And Persistence

The harness-level persistent object is `FUZZ_seqProdState`, declared in `zstd_helpers.h` only under `FUZZ_THIRD_PARTY_SEQ_PROD` and defined by `zstd_helpers.c`. Plugin implementations may also hold global or external resources between setup and teardown. State must be reclaimed per test case to avoid leak accumulation during fuzzing.

## Dependencies And Integration Points

This header requires `ZSTD_STATIC_LINKING_ONLY` and `zstd.h` for the unstable sequence producer API and `ZSTD_Sequence` type. It integrates with `fuzz.py` via `--custom-seq-prod=...`, with libFuzzer/ASan/UBSan builds, and with zstd compression contexts through `ZSTD_registerSequenceProducer()`.

## Risks And Edge Cases

The ABI is intentionally narrow but fragile: plugin code must be built with compatible compiler and sanitizer settings, and setup/state hooks must return exact success values expected by the macros. Multi-threaded use is explicitly not covered. If a producer returns malformed sequences or mishandles dictionaries/window sizes, downstream fuzzers should either validate fallback behavior or expose compressor bugs.

## Test Signals

Successful custom-producer fuzzing should show setup and teardown executing for every test case, non-NULL state creation, registration into compression contexts, and fallback behavior when the producer returns `ZSTD_SEQUENCE_PRODUCER_ERROR`. Sanitizer builds are the primary signal for plugin memory/thread-safety issues.
<!-- END_FILE_RESEARCH: sources/compression/zstd/tests/fuzz/fuzz_third_party_seq_prod.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/tests/fuzz/generate_sequences.c -->
# sources/compression/zstd/tests/fuzz/generate_sequences.c

## Purpose

`generate_sequences.c` fuzzes `ZSTD_generateSequences()` and validates that successful generated sequence streams can be recompressed and decompressed back to the original input. It specifically checks both explicit block delimiter mode and merged no-block-delimiter mode.

## Important APIs And Functions

The harness entry point is `LLVMFuzzerTestOneInput()`. `testRoundTrip()` compresses a provided sequence array with `ZSTD_compressSequences()`, decompresses with `ZSTD_decompress()`, and compares the regenerated bytes to the source.

The test uses `FUZZ_dataProducer_create()`, `FUZZ_dataProducer_reserveDataPrefix()`, and random parameter helpers from `zstd_helpers.c`. Core zstd APIs include `ZSTD_createCCtx()`, `ZSTD_sequenceBound()`, `ZSTD_generateSequences()`, `ZSTD_mergeBlockDelimiters()`, `ZSTD_CCtx_setParameter()`, `ZSTD_CCtx_reset()`, and `ZSTD_compressBound()`.

## Control Flow

The fuzzer splits the input between parameter bytes and source bytes. It creates a compression context, picks a random sequence array capacity from zero up to twice the upper bound, installs random compression parameters, disables target compressed block sizing and workers, then calls `ZSTD_generateSequences()`.

If sequence generation returns `ZSTD_error_dstSize_tooSmall`, the harness asserts that the chosen capacity was below `ZSTD_sequenceBound(size)`. For successful generation, it first enables explicit block delimiters and round-trips the original sequence list. It then merges delimiters with `ZSTD_mergeBlockDelimiters()`, resets the context session, switches to no-block-delimiter mode, and round-trips the merged sequence list.

## State And Persistence

All state is per-input: producer, compression context, sequence array, compressed buffer, and decompressed buffer are allocated and freed during the call. No `STATEFUL_FUZZING` branch is used in this target.

## Dependencies And Integration Points

This target depends on zstd static-linking-only APIs for sequence generation and compression. It integrates with the shared parameter fuzzer in `zstd_helpers.c` and the assertion/allocation helpers in `fuzz_helpers.h`. It covers the interaction between generated internal parser sequences and the public experimental sequence-compression ingestion API.

## Risks And Edge Cases

The main edges are zero-capacity sequence buffers, exact sequence-bound behavior, empty source input, delimiter merging, and random compression parameters that might otherwise introduce threads or target block sizing. The test intentionally disables workers and target block size to keep sequence generation deterministic and compatible with the checked invariants.

## Test Signals

Crashes or assertions indicate sequence generation produced non-round-trippable sequences, reported destination-size errors incorrectly, produced an invalid merged delimiter stream, or let context reset/parameter changes corrupt behavior. Fuzzer corpus entries should include empty inputs, tiny sequence capacities, large compressible inputs, and inputs that drive both block delimiter modes.
<!-- END_FILE_RESEARCH: sources/compression/zstd/tests/fuzz/generate_sequences.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/tests/fuzz/huf_decompress.c -->
# sources/compression/zstd/tests/fuzz/huf_decompress.c

## Purpose

`huf_decompress.c` fuzzes zstd's internal Huffman table-reading and decompression routines on arbitrary compressed-looking input. It is a crash-resistance target: it does not require successful decompression, but it requires table loading and decompression attempts not to crash or access invalid memory.

## Important APIs And Functions

The entry point is `LLVMFuzzerTestOneInput()`. It exercises `HUF_readDTableX1_wksp()` or `HUF_readDTableX2_wksp()` depending on a fuzzer-selected symbol mode, then calls `HUF_decompress1X_usingDTable()` or `HUF_decompress4X_usingDTable()` depending on a stream-count mode.

It allocates `HUF_DTable` storage with `HUF_DTABLE_SIZE(maxTableLog)` and workspace with `HUF_WORKSPACE_SIZE`. Flags include BMI2 when supported, optimal depth, prefer repeat table, suspect uncompressible, disable assembly, and disable fast paths.

## Control Flow

The fuzz data producer consumes prefix bytes to choose streams, X1/X2 decoding, HUF flags, destination buffer size, and maximum table log. The remaining bytes are treated as the Huffman table/compressed payload. The decoder table's first element is initialized from `maxTableLog` before reading the table.

If table reading fails, control jumps to cleanup. If it succeeds, the target attempts a 1X or 4X decompression into a possibly undersized destination buffer and ignores the return code, because any decompression error is a valid result for arbitrary input.

## State And Persistence

All allocation is per invocation: decode table, workspace, and output buffer are freed before return. CPU feature detection through `ZSTD_cpuid()` is read-only process state.

## Dependencies And Integration Points

This file includes internal zstd headers `common/cpu.h` and `common/huf.h`, plus fuzz helper libraries. It tests the lower-level Huffman decoder used by zstd frame/block decoding, including assembly and BMI2-dependent code paths when available.

## Risks And Edge Cases

Important edges include destination size zero, maximum table log extremes, invalid or truncated table payloads, X2 table-log-too-large conditions, repeated-table flags on non-repeat data, and CPU-dependent fast/assembly paths. The test intentionally ignores decompression errors after a valid table load, so it is not a semantic round-trip check.

## Test Signals

The signal is absence of sanitizer findings and process crashes across table-loading and decompression combinations. Corpus inputs that reach successful table reads are valuable because they drive deeper 1X/4X decode paths.
<!-- END_FILE_RESEARCH: sources/compression/zstd/tests/fuzz/huf_decompress.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/tests/fuzz/huf_round_trip.c -->
# sources/compression/zstd/tests/fuzz/huf_round_trip.c

## Purpose

`huf_round_trip.c` fuzzes zstd's internal Huffman compression/decompression pipeline by building a Huffman table from the input, compressing with that table, decompressing with a matching table, and asserting byte-for-byte round-trip correctness.

## Important APIs And Functions

`adjustTableLog()` computes a valid minimum table log for the observed alphabet size using `ZSTD_highbit32()`. The fuzzer entry point calls `HIST_count()`, `HUF_optimalTableLog()`, `HUF_buildCTable_wksp()`, `HUF_writeCTable_wksp()`, `HUF_readDTableX1_wksp()`, `HUF_readDTableX2_wksp()`, `HUF_compress1X_usingCTable()`, `HUF_compress4X_usingCTable()`, and the matching `HUF_decompress*()` routines.

It uses internal constants such as `HUF_WORKSPACE_SIZE`, `HUF_CTABLE_SIZE()`, `HUF_DTABLE_SIZE()`, and `HUF_TABLELOG_MAX`, plus fuzz-selected HUF flags.

## Control Flow

The producer selects stream mode, X1/X2 table read mode, flags, compressed buffer size, and a starting table log. The source payload is capped at 256 KiB. Inputs of size zero/one and RLE-only inputs are skipped because they do not exercise the normal HUF table path.

The harness counts symbols, adjusts table log upward when needed, builds and writes a compression table, reads a decompression table, then compresses using either 1X or 4X. If compression returns zero, the data was not compressed and no round-trip check is performed. Otherwise, decompression must succeed, produce the original size, and match the input via `FUZZ_memcmp()`.

## State And Persistence

All buffers and tables are per input. The only environmental state is CPU feature detection for BMI2 selection. No global context is preserved.

## Dependencies And Integration Points

This target depends on zstd internal histogram, Huffman, CPU, and bit helper headers. It covers table construction and encode/decode implementation used by zstd's literal compression layer, including both one-stream and four-stream variants.

## Risks And Edge Cases

The fuzz target stresses undersized compressed buffers, minimum table-log calculations for non-power-of-two alphabets, X2 decoder fallback to X1 on `tableLog_tooLarge`, RLE/uncompressible cases, and flags that change table depth or fast/assembly paths. Assertions in `adjustTableLog()` assume the computed minimum table log is at most 9 for the byte alphabet cases it sees.

## Test Signals

Any mismatch, decompression-size error, unexpected zstd error, or sanitizer failure is a high-value bug signal. Useful corpus inputs should cover sparse alphabets, near-full 256-symbol alphabets, data near the 256 KiB cap, and compressible versus deliberately uncompressible distributions.
<!-- END_FILE_RESEARCH: sources/compression/zstd/tests/fuzz/huf_round_trip.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/tests/fuzz/raw_dictionary_round_trip.c -->
# sources/compression/zstd/tests/fuzz/raw_dictionary_round_trip.c

## Purpose

`raw_dictionary_round_trip.c` validates zstd compression and decompression with raw-content dictionaries and prefixes. It splits fuzz input into source and dictionary regions, compresses with one of the raw dictionary attachment modes, decompresses with the matching mode, and asserts source recovery.

## Important APIs And Functions

The entry point is `LLVMFuzzerTestOneInput()`. `roundTripTest()` configures the shared `ZSTD_CCtx` and `ZSTD_DCtx`, using `FUZZ_setRandomParameters()`, `ZSTD_CCtx_refPrefix_advanced()`, `ZSTD_CCtx_loadDictionary_advanced()`, `ZSTD_compress2()`, `ZSTD_DCtx_refPrefix_advanced()`, `ZSTD_DCtx_loadDictionary_advanced()`, and `ZSTD_decompressDCtx()`.

The fuzz target also integrates optional sequence-producer hooks via `FUZZ_SEQ_PROD_SETUP()` and `FUZZ_SEQ_PROD_TEARDOWN()`.

## Control Flow

The fuzzer reserves input-prefix bytes for parameter production, then selects a source size inside the remaining data. Bytes after the source become the raw dictionary. It allocates decompression output sized to the source and a compressed buffer of `ZSTD_compressBound(srcSize)` minus a random zero or one byte. Checksum is disabled to allow the slightly smaller buffer in cases where frame overhead remains sufficient.

For each run, it picks either prefix reference mode or dictionary load mode. Compression must succeed. Decompression is configured with the same raw dictionary content type and then must return exactly the source size and identical bytes.

## State And Persistence

`cctx` and `dctx` are static and may persist across calls under `STATEFUL_FUZZING`; otherwise they are freed after each input. Optional third-party sequence producer state is created and destroyed per test case. Source, dictionary, compressed, and decompressed buffers are per input.

## Dependencies And Integration Points

This target depends on zstd public/experimental dictionary APIs, random parameter helpers, fuzz helper assertions, and optional third-party sequence producers. It exercises both dictionary-by-reference prefix behavior and load-method variation for raw-content dictionaries.

## Risks And Edge Cases

Key edges include empty source, empty dictionary, dictionary equal to source tail, random load methods, checksum-disabled small compressed buffers, persistent context reset behavior, and mismatched prefix/load configuration. Because dictionary memory points into the fuzzer input, reference modes also test lifetime assumptions during a single call.

## Test Signals

Valid signals are exact decompressed size and byte equality. Failures indicate dictionary attachment/load regressions, raw dictionary decode mismatch, parameter interactions that break round trips, or sequence-producer fallback issues when custom producers are enabled.
<!-- END_FILE_RESEARCH: sources/compression/zstd/tests/fuzz/raw_dictionary_round_trip.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/tests/fuzz/regression_driver.c -->
# sources/compression/zstd/tests/fuzz/regression_driver.c

## Purpose

`regression_driver.c` is a standalone corpus replay driver for zstd fuzz targets. It reads files from command-line paths, loads each file into memory, and calls the fuzz target's `LLVMFuzzerTestOneInput()` function, allowing deterministic regression testing outside libFuzzer.

## Important APIs And Functions

The only local function is `main()`. It uses `UTIL_createExpandedFNT()` when available to expand file name tables with link following, otherwise `UTIL_createFNT_fromROTable()`. It reads file metadata and contents through `UTIL_getFileSize()`, `UTIL_isRegularFile()`, `fopen()`, `fread()`, and `fclose()`, then invokes `LLVMFuzzerTestOneInput(buffer, fileSize)`.

## Control Flow

The driver constructs a file table from `argv[1..]`, warns on an empty table, and iterates each path. Non-regular files are skipped and cause a nonzero return. Files larger than 128 MiB assert-fail. The read buffer is grown only when the next file is larger than the current buffer, so repeated corpus entries reuse allocation.

After replaying all regular files, it prints a summary showing number of files tested and success/failure, releases the buffer and file table, and returns the accumulated status.

## State And Persistence

State is local to process execution: expanded file table, reusable heap buffer, tested count, and return flag. No corpus mutation or persistent record is written. Fuzz targets may maintain their own static state depending on `STATEFUL_FUZZING`.

## Dependencies And Integration Points

It includes `fuzz.h` for the fuzzer entry declaration, `fuzz_helpers.h` for assertions, and zstd `util.h` for file-list utilities. It is meant to be linked with one fuzz target implementation at a time and used by regression scripts or manual corpus replay.

## Risks And Edge Cases

Path expansion may include files that disappear before replay; the driver treats that as failure but continues. It relies on `UTIL_getFileSize()` being valid for regular files and asserts exact `fread()` length. Very large corpus files are rejected. No partial-read retry logic is present, so unusual filesystems or I/O errors become assertion failures.

## Test Signals

The main signal is successful replay of known crash reproducer files without assertion or sanitizer failures. The final process exit code distinguishes all-regular replay success from skipped/missing/non-regular path failures.
<!-- END_FILE_RESEARCH: sources/compression/zstd/tests/fuzz/regression_driver.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/tests/fuzz/seekable_roundtrip.c -->
# sources/compression/zstd/tests/fuzz/seekable_roundtrip.c

## Purpose

`seekable_roundtrip.c` fuzzes the zstd seekable format by compressing an input into a seekable stream, then randomly selecting an offset and length and verifying seekable decompression returns the matching slice of the original input.

## Important APIs And Functions

The entry point uses `ZSTD_seekable_createCStream()`, `ZSTD_seekable_initCStream()`, `ZSTD_seekable_compressStream()`, `ZSTD_seekable_endStream()`, `ZSTD_seekable_create()`, `ZSTD_seekable_initBuff()`, and `ZSTD_seekable_decompress()`. It sizes the compressed buffer as `ZSTD_compressBound(size) + ZSTD_seekTableFooterSize`.

## Control Flow

The fuzzer reserves prefix bytes for parameter choices, allocates compressed and decompressed buffers, selects compression level, checksum flag, requested uncompressed slice length, and offset. It initializes the seekable compressor, streams all input through it, finalizes the stream, then initializes a seekable reader over the resulting in-memory buffer.

For decompression, it repeatedly calls `ZSTD_seekable_decompress()` for the same `(offset, uncompressedSize)` request until the accumulated decompressed byte count reaches the requested length or a zero-size return stops progress. It asserts exact requested byte count and compares the output with `src + offset`.

## State And Persistence

`stream` and `zscs` are static seekable decompression/compression contexts. They persist under `STATEFUL_FUZZING` and are freed after each input otherwise. The compressed and decompressed buffers are per input.

## Dependencies And Integration Points

This target integrates zstd's seekable extension (`zstd_seekable.h`) with normal zstd compression bounds and fuzz data production. It tests in-memory seek table parsing, checksum option handling, streaming compression, and random-access decompression.

## Risks And Edge Cases

Edges include empty input, zero-length reads, reads ending at the final byte, checksum on/off, repeated decompression calls that must make progress, and compressed buffer sizing that accounts only for the footer overhead. If the seekable format emits more metadata than expected, compression could overrun the expected bound and assert.

## Test Signals

The primary signal is exact slice equality for arbitrary offsets and lengths. Failures point to seek table generation/parsing errors, checksum interaction bugs, offset accounting problems, or state reuse issues in seekable contexts.
<!-- END_FILE_RESEARCH: sources/compression/zstd/tests/fuzz/seekable_roundtrip.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/tests/fuzz/seq_prod_fuzz_example/Makefile -->
# sources/compression/zstd/tests/fuzz/seq_prod_fuzz_example/Makefile

## Purpose

This Makefile builds the example third-party sequence producer object used to demonstrate the custom sequence-producer fuzzing interface. It intentionally produces only `example_seq_prod.o`, which can be passed to `fuzz.py --custom-seq-prod=...`.

## Important Targets And Variables

`CC` defaults to `clang`. `CFLAGS` includes debug info, frame pointers, undefined/address/fuzzer sanitizers, and include paths for the parent fuzz directory and zstd library headers. The `default` phony target depends on `example_seq_prod.o`; that object target compiles `example_seq_prod.c` with `$(CC) -c $(CFLAGS)`.

## Control Flow

Running `make` in the directory builds the object file. There is no link step, clean target, dependency generation, or sanitizer variant matrix.

## State And Persistence

The build output is the local object file `example_seq_prod.o`. No generated sources or persistent test records are created.

## Dependencies And Integration Points

The file assumes clang and sanitizer/fuzzer runtime support are available. Its include paths align with `fuzz_third_party_seq_prod.h` documentation and zstd's `tests/fuzz` and `lib` directories. The resulting object integrates with zstd fuzz builds through `fuzz.py`.

## Risks And Edge Cases

The flags are demonstration-oriented and may not match every platform. GCC is not supported for this plugin path per the header guidance. Because only an object file is built, ABI compatibility depends on using matching compiler and sanitizer options when building the main fuzzer binaries.

## Test Signals

Successful `make` should produce a sanitizer-instrumented `example_seq_prod.o`. The stronger test is linking that object into a fuzzer build with `--custom-seq-prod` and confirming the example producer hooks run without link errors or sanitizer findings.
<!-- END_FILE_RESEARCH: sources/compression/zstd/tests/fuzz/seq_prod_fuzz_example/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/tests/fuzz/seq_prod_fuzz_example/example_seq_prod.c -->
# sources/compression/zstd/tests/fuzz/seq_prod_fuzz_example/example_seq_prod.c

## Purpose

`example_seq_prod.c` is a minimal implementation of the third-party sequence producer ABI. It demonstrates setup/teardown, state allocation, shared-state checking, and producer fallback behavior for fuzzing custom sequence producers.

## Important APIs And Functions

It implements all symbols declared by `fuzz_third_party_seq_prod.h`: `FUZZ_seqProdSetup()`, `FUZZ_seqProdTearDown()`, `FUZZ_createSeqProdState()`, `FUZZ_freeSeqProdState()`, and `FUZZ_thirdPartySeqProd()`. It uses `_Thread_local size_t threadLocalState` and a heap-allocated `size_t` shared state.

`FUZZ_thirdPartySeqProd()` receives the full sequence producer signature but only checks state consistency, increments shared and thread-local counters, and returns `ZSTD_SEQUENCE_PRODUCER_ERROR`.

## Control Flow

Setup resets the thread-local counter to zero. State creation allocates a zeroed `size_t`; free releases it. Each producer invocation asserts the shared state equals the thread-local state, increments both, then returns the special sequence-producer error to force zstd's fallback path when fallback is enabled.

## State And Persistence

The example intentionally uses both thread-local state and shared state to catch unsafe reuse across unexpected threading or lifecycle boundaries. The shared state is per fuzz test case, and the thread-local counter is reset at setup. No dictionary/source data is inspected.

## Dependencies And Integration Points

It depends on `fuzz_third_party_seq_prod.h`, which brings in zstd static APIs and `ZSTD_Sequence`. It is compiled to an object file by the adjacent Makefile and linked into fuzzers that define `FUZZ_THIRD_PARTY_SEQ_PROD`.

## Risks And Edge Cases

The example is not a real producer; it always requests fallback. Its assertions assume single-threaded invocation and ordered setup before production. If future fuzzers exercise sequence producers concurrently, this file is expected to expose that mismatch rather than support it.

## Test Signals

A linked fuzzer should call the producer repeatedly, maintain matching counters, and successfully fall back to zstd's built-in compression behavior. Assertion failures indicate lifecycle or threading changes in the sequence-producer integration.
<!-- END_FILE_RESEARCH: sources/compression/zstd/tests/fuzz/seq_prod_fuzz_example/example_seq_prod.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/tests/fuzz/sequence_compression_api.c -->
# sources/compression/zstd/tests/fuzz/sequence_compression_api.c

## Purpose

`sequence_compression_api.c` is the most comprehensive target in this group for zstd's experimental sequence-ingestion APIs. It generates arbitrary but valid `ZSTD_Sequence` arrays, synthesizes the corresponding source buffer, compresses through `ZSTD_compressSequences()` and sometimes `ZSTD_compressSequencesAndLiterals()`, then verifies decompression restores the generated source.

## Important APIs, Types, And Helpers

The entry point is `LLVMFuzzerTestOneInput()`. Helper functions include `FUZZ_RDG_rand()` and `generatePseudoRandomString()` for deterministic literal data, `generateRandomSequences()` for valid sequence arrays, `decodeSequences()` for reconstructing source bytes from sequences/literals/dictionary, `transferLiterals()` for extracting literal bytes, `roundTripTest_compressSequencesAndLiterals()`, and `roundTripTest()`.

Core zstd APIs include `ZSTD_compressSequences()`, `ZSTD_compressSequencesAndLiterals()`, `ZSTD_decompressDCtx()`, `ZSTD_CCtx_setParameter()`, `ZSTD_CCtx_getParameter()`, `ZSTD_createCDict_advanced()`, `ZSTD_createDDict_advanced()`, `ZSTD_CCtx_refCDict()`, and `ZSTD_DCtx_refDDict()`. It uses `ZSTD_SequenceFormat_e` to choose `ZSTD_sf_noBlockDelimiters` or `ZSTD_sf_explicitBlockDelimiters`.

## Control Flow

The fuzzer creates or reuses compression/decompression contexts, chooses window log, compression level, and sequence format, resets and configures the compression context for deterministic single-threaded sequence validation, and lazily initializes global literal, dictionary, sequence, and source buffers.

`generateRandomSequences()` emits sequences bounded by generated source size, maximum match length, current window size, optional dictionary size, and explicit-block constraints. In explicit delimiter mode it inserts zero-offset delimiter sequences when a block would exceed `min(ZSTD_BLOCKSIZE_MAX, windowSize)`, may split literals into delimiter sequences, and always appends a final delimiter.

`decodeSequences()` reconstructs a generated source buffer by copying literals from the fixed literal buffer and matches from either the dictionary or previously written output. In no-delimiter mode, it appends remaining literal bytes after all sequences. The resulting source and sequence array are passed to `roundTripTest()`, which optionally references global CDict/DDict objects and tests both `compressSequencesAndLiterals()` under its supported parameter combination and `compressSequences()`.

## State And Persistence

Several large static allocations persist under `STATEFUL_FUZZING`: compression/decompression contexts, the literal buffer, generated source buffer, generated sequence array, dictionary buffer, CDict, and DDict. Without `STATEFUL_FUZZING`, most are freed at the end of each input, but the dictionary buffer and CDict/DDict are not released in this file's non-stateful cleanup path, making process lifetime cleanup rely on fuzzer process exit.

The dictionary buffer is a zero-filled raw-content dictionary of size `1 << ZSTD_WINDOWLOG_MAX_32`, with CDict/DDict created by reference. The generator uses this large dictionary when the fuzzer-selected `hasDict` flag is set.

## Dependencies And Integration Points

The target depends on zstd static-linking-only APIs, `zstd_errors.h`, fuzz helpers, random parameter infrastructure, and optional third-party sequence producer setup macros. It directly tests sequence APIs that sit between external sequence producers and zstd frame emission.

## Risks And Edge Cases

This target deliberately explores hard boundaries: huge numbers of sequences, tiny explicit blocks, dictionary offsets that reach before generated output, maximum window-size constraints, `dstSize_tooSmall` in explicit delimiter mode, and `cannotProduce_uncompressedBlock` from `compressSequencesAndLiterals()`. The manual source decoder is itself security-sensitive test code; bugs there could mask or falsely report compressor behavior.

Memory pressure is nontrivial because the dictionary maximum can be large and several 1 MiB buffers are retained. `transferLiterals()` uses assertions about destination slack and source consumption, so malformed generated sequences should be caught before zstd ingestion.

## Test Signals

Round-trip decompressed size and byte equality are the main success conditions. Expected non-round-trip outcomes are limited to documented `dstSize_tooSmall` in explicit delimiter mode and `cannotProduce_uncompressedBlock` for `compressSequencesAndLiterals()`. Valuable corpus cases cover explicit delimiter splits, dictionary-backed matches, window-bound offsets, many small blocks, and toggling validation mode.
<!-- END_FILE_RESEARCH: sources/compression/zstd/tests/fuzz/sequence_compression_api.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/tests/fuzz/simple_compress.c -->
# sources/compression/zstd/tests/fuzz/simple_compress.c

## Purpose

`simple_compress.c` fuzzes the simple one-shot compression API with random input, compression level, and output capacity. It ensures `ZSTD_compressCCtx()` either succeeds or fails only with the expected destination-too-small error.

## Important APIs And Functions

The entry point is `LLVMFuzzerTestOneInput()`. It uses `ZSTD_createCCtx()`, `ZSTD_compressBound()`, `ZSTD_compressCCtx()`, `ZSTD_isError()`, and `ZSTD_getErrorCode()`. Compression levels are selected between `kMinClevel` and `kMaxClevel` from `zstd_helpers.c`.

Optional sequence-producer setup/teardown macros wrap the test, allowing this simple API harness to also exercise registered third-party sequence producers through shared helper configuration.

## Control Flow

The producer reserves prefix bytes, computes the maximum compressed bound for the remaining source, picks an output buffer size from zero to the bound, and chooses a compression level. A static compression context is created if needed. The compression call is performed once; if it returns an error, the error code must be `ZSTD_error_dstSize_tooSmall`.

## State And Persistence

`cctx` is static and persists under `STATEFUL_FUZZING`; otherwise it is freed after each input. The result buffer and data producer are per invocation. Sequence producer state is per test case when enabled.

## Dependencies And Integration Points

The file depends on public zstd compression APIs, zstd error codes, shared fuzz helpers, and optional third-party sequence producer support. It is a broad smoke target for the simplest compression entry point.

## Risks And Edge Cases

The main edge is zero or undersized destination capacity. Since arbitrary output size is allowed, unexpected error codes indicate API contract regression. The target does not validate successful compressed output, so corruption detection is left to round-trip fuzzers.

## Test Signals

Success means no crash and no compression error except `dstSize_tooSmall`. Corpus entries should include empty input, small output buffers, and high/negative compression levels.
<!-- END_FILE_RESEARCH: sources/compression/zstd/tests/fuzz/simple_compress.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/tests/fuzz/simple_decompress.c -->
# sources/compression/zstd/tests/fuzz/simple_decompress.c

## Purpose

`simple_decompress.c` fuzzes one-shot zstd decompression on arbitrary input and random output capacity. It is primarily a crash-resistance target, with an additional consistency check for successful decompressions.

## Important APIs And Functions

The entry point uses `ZSTD_createDCtx()`, `ZSTD_decompressDCtx()`, `ZSTD_findDecompressedSize()`, and zstd content-size sentinel values. It uses `FUZZ_dataProducer` to select an output buffer size up to `10 * size`.

## Control Flow

The fuzzer reserves parameter bytes, creates or reuses a decompression context, allocates an output buffer, and calls `ZSTD_decompressDCtx()` once. If decompression succeeds, it calls `ZSTD_findDecompressedSize()` on the same input and asserts that the result is not `ZSTD_CONTENTSIZE_ERROR` and is either unknown or exactly equal to the returned decompressed size.

## State And Persistence

`dctx` is static and persists only under `STATEFUL_FUZZING`; otherwise it is freed per input. The output buffer and producer are per invocation.

## Dependencies And Integration Points

This target uses zstd static-linking-only mode and public decompression/content-size helpers. It complements `zstd_frame_info.c`, which fuzzes metadata helpers without decompressing.

## Risks And Edge Cases

Important edges include empty input, valid frames with unknown content size, concatenated frames, truncated frames, output buffer size zero, and arbitrary non-frame data. The test intentionally accepts decompression errors but requires successful returns to agree with frame-size discovery.

## Test Signals

Signals include crashes, sanitizer findings, successful decompressions with content-size errors, or mismatches between known content size and returned decompressed size.
<!-- END_FILE_RESEARCH: sources/compression/zstd/tests/fuzz/simple_decompress.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/tests/fuzz/simple_round_trip.c -->
# sources/compression/zstd/tests/fuzz/simple_round_trip.c

## Purpose

`simple_round_trip.c` validates zstd one-shot compression/decompression correctness over randomized compression parameters. It also checks compression determinism for identical parameters and tests in-place decompression margin behavior.

## Important APIs And Functions

`getDecompressionMargin()` compares `ZSTD_decompressionMargin()` with `ZSTD_DECOMPRESSION_MARGIN()` when small-block targeting is not active. `roundTripTest()` drives compression, determinism hashing with `XXH64()`, optional decoder max-block-size enforcement, normal decompression, and margin-based in-place decompression.

Important zstd APIs include `ZSTD_compress2()`, `ZSTD_compressCCtx()`, `ZSTD_decompressDCtx()`, `ZSTD_getFrameHeader()`, `ZSTD_CCtx_getParameter()`, `ZSTD_DCtx_setParameter()`, `ZSTD_decompressionMargin()`, and `ZSTD_DECOMPRESSION_MARGIN()`.

## Control Flow

The input is split into parameter and source bytes. The target allocates an output buffer sized to source size and a compressed buffer of `ZSTD_compressBound(size)` minus zero or one byte. It creates static compression/decompression contexts and calls `roundTripTest()`.

`roundTripTest()` randomly chooses between full random parameter compression via `FUZZ_setRandomParameters()` and simple compression-level compression. In both branches it compresses twice with the same settings and asserts identical compressed size and XXH64 hash. It then optionally sets the decoder max block size, performs normal decompression with exact byte comparison, computes decompression margin, places the compressed frame at the end of a shared buffer, and verifies in-place-style decompression into the front of that buffer.

## State And Persistence

`cctx` and `dctx` are static and persist under `STATEFUL_FUZZING`; otherwise they are freed per input. All source/output/compressed buffers are per test case. Optional third-party sequence producer state is per case.

## Dependencies And Integration Points

The target depends on zstd static APIs, random parameter helpers, xxhash via `fuzz_helpers.h`, and optional sequence producer registration. It is one of the broadest coverage targets for normal frame compression, decompression, frame headers, deterministic output, and decompression-margin contracts.

## Risks And Edge Cases

Edges include empty input, one-byte-shrunken compression buffer, random max block sizes, target compressed block size, long-distance match settings, checksum/content-size/dict-ID flags, and in-place layout where input overlaps the output allocation. The superblock expansion assertion is intentionally disabled because target-block mode can currently expand too much in the worst case.

## Test Signals

High-value signals are nondeterministic compressed output for identical parameters, decompressed-size mismatch, byte corruption, invalid decompression margin, or max-block-size decoder failures. Corpus inputs should exercise both compression branches and the optional random decoder max-block setting.
<!-- END_FILE_RESEARCH: sources/compression/zstd/tests/fuzz/simple_round_trip.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/tests/fuzz/stream_decompress.c -->
# sources/compression/zstd/tests/fuzz/stream_decompress.c

## Purpose

`stream_decompress.c` fuzzes streaming decompression on arbitrary input with randomized input and output chunk boundaries. It validates that the streaming decoder handles partial buffers, zero-size buffers, stable-output mode, and errors without crashing.

## Important APIs And Functions

The helper `makeOutBuffer()` chooses an output buffer capacity from zero to the allocated size and sets `dst` to `NULL` when size is zero. `makeInBuffer()` chooses an input chunk size from zero to remaining bytes and sets `src` to `NULL` when size is zero. The entry point uses `ZSTD_createDStream()`, `ZSTD_DCtx_reset()`, `ZSTD_DCtx_setParameter(ZSTD_d_stableOutBuffer)`, and `ZSTD_decompressStream()`.

## Control Flow

The fuzzer reserves prefix bytes, allocates an output buffer of `MAX(10 * size, ZSTD_BLOCKSIZE_MAX)`, creates or resets the stream, and sometimes enables stable-output-buffer mode. In stable mode, one output buffer covers the entire run and filling it is treated as an error exit. Otherwise, output buffers are randomly remade whenever the previous one fills.

The main loop feeds randomized input chunks until all bytes are consumed. Each input chunk is decompressed in a `do` loop until `in.pos == in.size`. Any zstd error jumps to cleanup and returns success from the fuzz harness because arbitrary input may be invalid.

## State And Persistence

`dstream` is static and may persist under `STATEFUL_FUZZING`; otherwise it is freed per input. A global `uint32_t seed` is declared but unused. Output buffer and data producer are per input.

## Dependencies And Integration Points

This target uses zstd static decompression APIs and fuzz data producer helpers. It covers the streaming decoder boundary contract used by applications that provide partial input/output buffers.

## Risks And Edge Cases

The target exercises zero-size input/output chunks, `NULL` buffer pointers paired with size zero, stable output-buffer semantics, arbitrary invalid frames, and contexts reset with `ZSTD_reset_session_only`. It does not assert a full-frame success invariant, so semantic correctness is covered by round-trip streaming tests.

## Test Signals

The key signal is no crash or sanitizer failure through random chunking and stable buffer mode. Additional regressions are zstd errors on internally valid streaming frames, which are better detected by `stream_round_trip.c`.
<!-- END_FILE_RESEARCH: sources/compression/zstd/tests/fuzz/stream_decompress.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/tests/fuzz/stream_round_trip.c -->
# sources/compression/zstd/tests/fuzz/stream_round_trip.c

## Purpose

`stream_round_trip.c` fuzzes zstd streaming compression and decompression as a complete round trip. It randomizes input chunk sizes, output chunk sizes, flush/end/continue actions, context resets between frames, compression parameters, and in-place decompression margin behavior.

## Important APIs And Functions

Helpers `makeOutBuffer()` and `makeInBuffer()` create nonzero-sized streaming buffers. `compress()` drives `ZSTD_compressStream2()` with randomly selected `ZSTD_e_continue`, `ZSTD_e_flush`, and `ZSTD_e_end` operations. `decompress()` uses `ZSTD_decompressStream()` to consume the generated stream and may configure `ZSTD_d_maxBlockSize` from the compressor's max block size.

The entry point allocates static buffers sized as `ZSTD_compressBound(size) * 15`, creates `ZSTD_CCtx` and `ZSTD_DCtx`, then validates normal and in-place-style decompression.

## Control Flow

Compression starts by resetting the compression session, setting random parameters, and reading the selected max block size. The compressor loops over randomized source chunks. For each input chunk, it randomly chooses actions: flush, end, continue, and a special zero-input/zero-output continue call. When an end operation completes a frame, it resets the session and occasionally selects new random parameters while preserving the same max block size.

After all source bytes are consumed, it repeatedly calls `ZSTD_e_end` with empty input until the final frame is closed. Decompression feeds the complete compressed stream to `ZSTD_decompressStream()` in one input buffer and asserts each return is zero while progress remains, then returns the output position. The entry point checks decompressed size and byte equality, then verifies `ZSTD_decompressionMargin()` by copying the compressed stream to the tail of a combined buffer and decompressing into the front.

## State And Persistence

`cctx`, `dctx`, `cBuf`, `rBuf`, and `bufSize` are static. Buffers grow to meet the largest seen input and persist for stateful fuzzing and across calls until process exit. Contexts are freed per input unless `STATEFUL_FUZZING` is defined; static buffers are not freed in the non-stateful cleanup path.

## Dependencies And Integration Points

The target uses zstd static-linking APIs, random parameter helpers, fuzz allocation/assertion utilities, and optional third-party sequence producer setup. It covers applications that interleave flush/end actions and create multiple frames in one stream.

## Risks And Edge Cases

Important edges include very small output chunks, repeated flushes, ending and resetting frames mid-input, zero-buffer continue calls, multiple frames in a single compressed stream, preserved decoder max-block constraints, large safety multiplier for compressed buffer capacity, and overlap-sensitive decompression margins.

The `decompress()` helper asserts `ret == 0` for every streaming call while input remains. This matches the expectation that a complete compressed stream is available in the input buffer, but it is stricter than generic streaming caller behavior and is tuned for this generated data.

## Test Signals

Failures include streaming API crashes, unexpected compression/decompression zstd errors, incomplete decompression, byte corruption, incorrect decompression margins, and reset/parameter bugs between frames. Corpus inputs that trigger multiple frames, many flushes, and max-block-size changes are especially useful.
<!-- END_FILE_RESEARCH: sources/compression/zstd/tests/fuzz/stream_round_trip.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/tests/fuzz/zstd_frame_info.c -->
# sources/compression/zstd/tests/fuzz/zstd_frame_info.c

## Purpose

`zstd_frame_info.c` fuzzes zstd helper functions that inspect compressed-frame metadata. It intentionally feeds arbitrary input to fast metadata APIs to ensure they handle invalid, empty, truncated, and valid frame data safely.

## Important APIs And Functions

The entry point calls `ZSTD_getFrameContentSize()`, `ZSTD_getDecompressedSize()`, `ZSTD_findFrameCompressedSize()`, `ZSTD_getDictID_fromFrame()`, `ZSTD_findDecompressedSize()`, `ZSTD_decompressBound()`, `ZSTD_frameHeaderSize()`, `ZSTD_isFrame()`, `ZSTD_getFrameHeader()`, and `ZSTD_getFrameHeader_advanced()` with `ZSTD_f_zstd1`.

## Control Flow

For zero-size input, the source pointer is set to `NULL` before calling metadata helpers. All helper return values are ignored except for avoiding crashes; a local `ZSTD_FrameHeader` receives parsed header results where applicable.

## State And Persistence

This target has no persistent state and performs no allocation. It only uses stack state for the frame header.

## Dependencies And Integration Points

It depends on `fuzz_helpers.h` and `zstd_helpers.h`, which enable zstd static APIs. It complements decompression fuzzers by covering metadata-only code paths commonly used for preflight sizing, dictionary ID discovery, and frame identification.

## Risks And Edge Cases

Edges include NULL source with zero size, magicless data, skippable frames, truncated headers, concatenated frames, unknown content size, malformed frame descriptors, and very large size calculations. Since return values are not cross-validated here, logical consistency is checked in other targets such as `simple_decompress.c`.

## Test Signals

The expected signal is no crash, assertion, or sanitizer finding across all helper calls. Valid-frame corpus entries are useful for reaching deeper header parsing, while malformed short inputs stress bounds checks.
<!-- END_FILE_RESEARCH: sources/compression/zstd/tests/fuzz/zstd_frame_info.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/tests/fuzz/zstd_helpers.c -->
# sources/compression/zstd/tests/fuzz/zstd_helpers.c

## Purpose

`zstd_helpers.c` implements shared zstd-specific fuzz helper logic: randomized compression/frame parameter generation, installation of random parameters onto a `ZSTD_CCtx`, optional sequence-producer registration, and quick dictionary training for dictionary fuzz targets.

## Important APIs And Functions

It defines `kMinClevel = -3`, `kMaxClevel = 19`, and `void* FUZZ_seqProdState`. Internal helpers `set()`, `produceParamValue()`, and `setRand()` wrap `ZSTD_CCtx_setParameter()` with fuzz assertions. Public helpers are `FUZZ_randomCParams()`, `FUZZ_randomFParams()`, `FUZZ_randomParams()`, `FUZZ_setRandomParameters()`, and `FUZZ_train()`.

`setSequenceProducerParams()` registers either `FUZZ_thirdPartySeqProd()` with `FUZZ_seqProdState` when `FUZZ_THIRD_PARTY_SEQ_PROD` is defined, or zstd's `simpleSequenceProducer` otherwise. It also configures sequence-producer fallback, disables workers, and disables long-distance matching for that producer mode.

## Control Flow

Random parameter generation consumes deterministic bytes from `FUZZ_dataProducer_t`, first choosing compression parameters within bounded low-to-moderate ranges and passing them through `ZSTD_adjustCParams()`, then choosing frame flags. `FUZZ_setRandomParameters()` writes many zstd compression parameters onto a context, including LDM settings, threading/rsyncable behavior, row matcher, dictionary attach behavior, block splitter, target block size, max block size, validation, repcode resolution, and optional source-size hint.

When zstd is built without multithreading, it still consumes entropy for worker and rsyncable choices before forcing both settings to zero, keeping corpus interpretation reproducible across builds. Sequence producer registration is mandatory under `FUZZ_THIRD_PARTY_SEQ_PROD` and randomly enabled otherwise.

`FUZZ_train()` creates synthetic samples from random offsets in the source, fills unused sample bytes with zeros, configures fastCover parameters, and calls `ZDICT_trainFromBuffer_fastCover()`. On training error, it frees the dictionary buffer and returns a zeroed dictionary struct.

## State And Persistence

`FUZZ_seqProdState` is global state shared with the third-party sequence producer macros. The helper functions otherwise mutate caller-owned compression contexts. `FUZZ_train()` returns heap memory owned by the caller on success. Parameter generation depends on the producer cursor, so helper call order is part of the fuzz contract.

## Dependencies And Integration Points

This file requires `ZSTD_STATIC_LINKING_ONLY` and `ZDICT_STATIC_LINKING_ONLY`, zstd/zdict APIs, `sequence_producer.h`, fuzz helpers, and the third-party sequence producer header. It is linked into many fuzz targets in this directory and controls a large share of their parameter-space coverage.

## Risks And Edge Cases

Because the helper sets many experimental/static-only parameters, changes in zstd parameter bounds can make fuzzers start failing during setup. Cross-build reproducibility depends on consuming entropy even when features such as multithreading are compiled out. Sequence-producer fallback settings differ between built-in and third-party modes and must stay aligned with fuzzer expectations. `FUZZ_train()` must handle tiny or empty sources carefully via `MAX(srcSize, 1) - 1` and zero-sized sample slices.

## Test Signals

Fuzz targets using this helper should continue to reproduce corpus behavior across builds with and without `ZSTD_MULTITHREAD`. Unit-level signals include valid adjusted compression parameters, successful context parameter setting, correct sequence-producer fallback registration, and dictionary training returning either a valid buffer or a clean zeroed result.
<!-- END_FILE_RESEARCH: sources/compression/zstd/tests/fuzz/zstd_helpers.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/tests/fuzz/zstd_helpers.h -->
# sources/compression/zstd/tests/fuzz/zstd_helpers.h

## Purpose

`zstd_helpers.h` declares the shared zstd fuzz helper API implemented by `zstd_helpers.c`. It exposes randomized parameter generation, context parameter installation, quick dictionary training, shared compression level bounds, and optional third-party sequence producer state.

## Important APIs And Types

The header declares `kMinClevel`, `kMaxClevel`, `FUZZ_setRandomParameters()`, `FUZZ_randomCParams()`, `FUZZ_randomFParams()`, and `FUZZ_randomParams()`. It defines `FUZZ_dict_t` as a simple `{ void* buff; size_t size; }` pair returned by `FUZZ_train()`.

When `FUZZ_THIRD_PARTY_SEQ_PROD` is defined, it declares `extern void* FUZZ_seqProdState`, allowing setup macros and helper registration code to share the per-test-case state pointer.

## Control Flow

The header has no direct runtime behavior. It enables fuzz targets to request randomized context setup before compression and to request fast dictionary training from an input buffer.

## State And Persistence

The only declared shared state is `FUZZ_seqProdState` under the third-party producer build. `FUZZ_dict_t` ownership is by convention: callers that receive a nonzero dictionary from `FUZZ_train()` must free `buff` when done.

## Dependencies And Integration Points

It enables `ZSTD_STATIC_LINKING_ONLY` before including `zstd.h`, includes `zstd_errors.h`, and depends on `fuzz_data_producer.h`. It is included by most zstd compression fuzz targets and provides the stable local contract for randomized parameter coverage.

## Risks And Edge Cases

Because the header exposes static-linking-only zstd types and parameters, it is tied to internal/experimental zstd API stability. Callers must treat `FUZZ_train()` as fuzz-only dictionary generation, not production training, and must account for failed training returning an empty struct.

## Test Signals

Compile coverage across fuzz targets is the primary signal for this header. Runtime signals come from successful parameter application, reproducible corpus behavior, and correct dictionary ownership in targets using `FUZZ_train()`.
<!-- END_FILE_RESEARCH: sources/compression/zstd/tests/fuzz/zstd_helpers.h -->
