# Research: subset-b-000285

<!-- BEGIN_FILE_RESEARCH: sources/compression/lz4/tests/datagen.c -->
# sources/compression/lz4/tests/datagen.c

## Purpose
`datagen.c` implements the reproducible compressible data generator used by the LZ4 test tools. It can fill a caller-provided buffer or stream bytes to stdout while controlling match probability, literal distribution, and seed. The generated stream deliberately resembles LZ4-friendly data: short literals interleaved with back-references within a 32 KB dictionary window.

## Important APIs, Types, and Functions
The public functions are `RDG_genBuffer()` and `RDG_genOut()`. Internal helpers include `RDG_rand()` for deterministic PRNG state, `RDG_fillLiteralDistrib()` for a 8192-entry literal table, `RDG_genChar()` for weighted byte selection, and `RDG_genBlock()` for literal/match block synthesis. `litDistribTable` is a fixed `BYTE` array sized by `LTLOG`.

## Control Flow, State, and Persistence
All state is in stack buffers and the seed passed by value or pointer. `RDG_genBlock()` starts at `prefixSize`, optionally initializes the first byte, then loops until `buffSize`, choosing match copies or literal runs from PRNG output. `RDG_genOut()` first generates a 32 KB dictionary, then repeatedly fills a 128 KB block after the dictionary, writes the requested amount to stdout, and slides the trailing dictionary with `memcpy`. There is no persistent file state.

## Dependencies and Integration Points
The file depends on `platform.h` for binary stdout mode, `util.h` for fixed-width LZ4 typedefs, and libc allocation/output primitives. `datagencli.c`, benchmarks, and tests use the exported generator through `datagen.h`.

## Risks and Test Signals
Risks are unchecked `fwrite()` failures, extreme `matchProba >= 1.0` behavior producing sparse zero runs, and caller-provided buffer size assumptions. Deterministic seed behavior is a strong test signal: identical probability and seed should reproduce byte-exact output.
<!-- END_FILE_RESEARCH: sources/compression/lz4/tests/datagen.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/lz4/tests/datagen.h -->
# sources/compression/lz4/tests/datagen.h

## Purpose
`datagen.h` declares the public interface for the compressible random data generator used by LZ4 test and benchmark programs.

## Important APIs, Types, and Functions
It exports `RDG_genOut(unsigned long long size, double matchProba, double litProba, unsigned seed)` and `RDG_genBuffer(void* buffer, size_t size, double matchProba, double litProba, unsigned seed)`. `RDG_genOut()` writes to stdout, while `RDG_genBuffer()` fills a supplied memory region.

## Control Flow, State, and Persistence
The header owns no state and performs no work. Its comments define the behavioral contract: `litProba` is optional, `0.0` selects a default derived from match probability, and equal parameters plus seed produce identical generated content.

## Dependencies and Integration Points
It includes only `<stddef.h>` for `size_t`. `datagen.c` implements these declarations and `datagencli.c` calls them when the CLI receives `-P`.

## Risks and Test Signals
The main risk is semantic drift between the comments and implementation, especially deterministic output and default literal probability. Compile-time users get a small, stable API surface with no exposed internal types.
<!-- END_FILE_RESEARCH: sources/compression/lz4/tests/datagen.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/lz4/tests/datagencli.c -->
# sources/compression/lz4/tests/datagencli.c

## Purpose
`datagencli.c` is the command-line frontend for producing test data. With explicit compressibility it emits random LZ4-oriented data; otherwise it emits lorem ipsum text.

## Important APIs, Types, and Functions
`main()` parses options and dispatches to `RDG_genOut()` or `LOREM_genOut()`. `usage()` prints supported flags. Global `displayLevel` and `DISPLAYLEVEL` control stderr diagnostics. Supported options include `-g#` with K/M/G/B suffixes, `-s#`, `-P#`, hidden `-L#`, `-v`, and `-h`.

## Control Flow, State, and Persistence
Parsing supports aggregated short options and updates local `size`, `seed`, `proba`, and `litProba`. `COMPRESSIBILITY_NOT_SET` selects lorem output; otherwise `proba / 100.0` drives `RDG_genOut()`. The program streams generated data to stdout and writes diagnostics to stderr. No files are opened directly.

## Dependencies and Integration Points
It depends on `datagen.h`, `loremOut.h`, `lz4.h` for the version string, and `util.h` typedefs. It is a test utility entry point around the lower-level generators.

## Risks and Test Signals
Risks include minimal validation for malformed numeric suffixes, silent overflow when shifting very large sizes, and unchecked stdout write failures in the generator. Useful signals are deterministic `-s` output, CLI exit code `1` for unknown options, and fallback to lorem output when `-P` is omitted.
<!-- END_FILE_RESEARCH: sources/compression/lz4/tests/datagencli.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/lz4/tests/decompress-partial-usingDict.c -->
# sources/compression/lz4/tests/decompress-partial-usingDict.c

## Purpose
This standalone regression test validates `LZ4_decompress_safe_partial_usingDict()` across no-dictionary, prefix-dictionary, and external-dictionary scenarios.

## Important APIs, Types, and Functions
`main()` compresses a static lorem source with `LZ4_compress_default()` and repeatedly calls `LZ4_decompress_safe_partial_usingDict()`. It allocates a large buffer to position output after prefix memory and a separate dictionary buffer for external dict cases.

## Control Flow, State, and Persistence
The test computes `srcLen`, compresses once into `cmpBuffer`, then loops `i` from `cmpSize` through `cmpSize + 9` so the decoder sees exact input and extra trailing bytes. Each mode checks nonnegative result, exact `srcLen`, and `memcmp()` equality. Heap buffers are process-local; the program returns `-1` on the first failure and `0` on success.

## Dependencies and Integration Points
It uses the public `lz4.h` block API plus libc allocation and assertions. It complements the broader fuzzer by making a focused dictionary partial-decode case easy to run from build scripts.

## Risks and Test Signals
The test intentionally does not free heap memory before exit, which is acceptable for a tiny executable but noisy under strict leak tools. Strong signals are the five dictionary layouts: none, small prefix, large prefix, small external, and large external.
<!-- END_FILE_RESEARCH: sources/compression/lz4/tests/decompress-partial-usingDict.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/lz4/tests/decompress-partial.c -->
# sources/compression/lz4/tests/decompress-partial.c

## Purpose
This compact standalone test validates `LZ4_decompress_safe_partial()` when the compressed input buffer is exact or includes small trailing slack.

## Important APIs, Types, and Functions
`main()` uses `LZ4_compress_default()` to create an LZ4 block from a static lorem source and calls `LZ4_decompress_safe_partial()` in a loop. The fixed `BUFFER_SIZE` is 2048 bytes for source, compressed, and output buffers.

## Control Flow, State, and Persistence
After compression, the loop runs with input sizes from `cmpSize` to `cmpSize + 9`. Each decompression must return `srcLen`, avoid negative errors, and reproduce the static string byte-for-byte. The test has no persistent state, no heap allocation, and exits immediately on failure.

## Dependencies and Integration Points
It includes only stdio/string headers and `lz4.h`. It is a direct signal for the public partial decompression API and provides a simpler counterpart to dictionary and fuzz coverage.

## Risks and Test Signals
The main coverage gap is that it only targets a single small lorem payload and full target output, not a true early-stop target smaller than the source. Its signal is focused: trailing compressed input bytes must be tolerated without corrupting the decoded prefix or result size.
<!-- END_FILE_RESEARCH: sources/compression/lz4/tests/decompress-partial.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/lz4/tests/frametest.c -->
# sources/compression/lz4/tests/frametest.c

## Purpose
`frametest.c` is the randomized and deterministic test driver for the `lz4frame` API. It verifies one-shot frames, streaming compression/decompression, dictionaries, checksums, skippable frames, custom allocators, context size accounting, and decoder recovery after errors.

## Important APIs, Types, and Functions
Key entry points are `unitTests()`, `fuzzerTests()`, `test_lz4f_decompression()`, `test_lz4f_decompression_wBuffers()`, `bug1227()`, and `main()`. It exercises `LZ4F_compressFrame`, `LZ4F_compressBegin`, `LZ4F_compressUpdate`, `LZ4F_uncompressedUpdate`, `LZ4F_flush`, `LZ4F_compressEnd`, `LZ4F_getFrameInfo`, `LZ4F_decompress`, `LZ4F_decompress_usingDict`, `LZ4F_createCDict`, `LZ4F_compressFrame_usingCDict`, `LZ4F_cctx_size`, and `LZ4F_dctx_size`. `Test_alloc_state` tracks custom allocator live bytes.

## Control Flow, State, and Persistence
The unit phase allocates a 2 MB compressible-noise buffer, computes an XXH64 reference checksum, and executes fixed API edge cases. The fuzzer phase builds a 9 MB corpus and loops by count or duration, deriving source windows, preferences, flush behavior, and corruption patterns from a deterministic PRNG. Contexts are reused but reset after errors. State is in heap buffers, LZ4F contexts, custom allocator bookkeeping, global display/pause flags, and PRNG seeds; no durable data is written.

## Dependencies and Integration Points
The file includes `lz4frame.h` multiple times, including static-linking declarations, to validate header safety. It integrates `lz4file.h` write helpers, `lz4.h` constants, and `xxhash` checksums. CLI flags (`-i`, `-T`, `-s`, `-t`, `-P`, `-v`, `-q`, `--no-prompt`) make failures reproducible by seed and test number.

## Risks and Test Signals
Important risks covered include incomplete headers, wrong content size checks, checksum failures, overrun on small dst buffers, stale decompression context state after errors, dictionary regression, allocator accounting drift, and skippable-frame parsing. Some paths intentionally ignore the exact error from noisy input because sanitizer safety is the goal. Strong signals are checksum equality, sentinel-byte preservation, exact input consumption, expected `LZ4F_ERROR_frameHeader_incomplete`, and seeded reproduction.
<!-- END_FILE_RESEARCH: sources/compression/lz4/tests/frametest.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/lz4/tests/freestanding.c -->
# sources/compression/lz4/tests/freestanding.c

## Purpose
`freestanding.c` is a minimal freestanding-environment smoke test for compiling and running LZ4 and LZ4HC without the normal C runtime support expected by hosted programs.

## Important APIs, Types, and Functions
On x86_64 Linux it defines `LZ4_FREESTANDING`, maps LZ4 memory hooks to local `memmove`, `memcpy`, and `memset`, includes `../lib/lz4.c` and `../lib/lz4hc.c` directly, and tests `LZ4_compress_default()`, `LZ4_compress_HC()`, and `LZ4_decompress_safe()`. It also provides `_start()`, `main()`, `MY_exit()`, `MY_abort()`, `__assert_fail()`, and implementations of required memory functions.

## Control Flow, State, and Persistence
Non-x86_64 or non-Linux builds return success without exercising freestanding code. The Linux path compresses and decompresses a static 256-byte README excerpt with both normal and HC compressors, compares bytes, and exits via a raw `SYS_exit` syscall. All buffers are static; there is no heap or persistent state.

## Dependencies and Integration Points
It depends only on `<stddef.h>`, `<stdint.h>`, inline assembly syscall support, and direct inclusion of LZ4 library sources. This test protects the `LZ4_FREESTANDING` configuration used by embedded or kernel-like integrations.

## Risks and Test Signals
Risks include architecture specificity, direct inclusion hiding separate-object link issues, and a small test corpus. Strong signals are absence of libc calls under `-ffreestanding -nostdlib`, byte-exact round trips, and exit code equal to source line on failure.
<!-- END_FILE_RESEARCH: sources/compression/lz4/tests/freestanding.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/lz4/tests/fullbench.c -->
# sources/compression/lz4/tests/fullbench.c

## Purpose
`fullbench.c` is an executable speed analyzer for LZ4 block, HC, dictionary, and frame APIs. It reads real input files, chunks them, runs selected compressors and decompressors repeatedly, reports throughput and ratios, and verifies decompressed data with checksums.

## Important APIs, Types, and Functions
`fullSpeedBench()` is the main benchmark engine. Descriptor tables `compDescArray` and `decDescArray` map CLI-selectable numeric IDs to local wrappers around `LZ4_compress_default`, `LZ4_compress_destSize`, `LZ4_compress_fast`, external-state/streaming variants, HC variants, `LZ4F_compressFrame`, `LZ4F_compressUpdate`, safe/fast dictionary decompressors, partial decompressors, and frame decompressors. `chunkParameters` stores per-chunk original and compressed buffers and sizes.

## Control Flow, State, and Persistence
`main()` parses options such as `-c#`, `-d#`, `-i#`, `-B#`, `-l`, and `--no-prompt`, then passes filenames to `fullSpeedBench()`. Each file is opened, sized with `UTIL_getFileSize()`, limited by `BMK_findMaxMem()`, read into memory, split by `g_chunkSize`, and benchmarked for `g_nbIterations` timed loops. Compression output is later regenerated with default LZ4 for decompression tests. Global LZ4 stream/context objects are reused between iterations where APIs require state.

## Dependencies and Integration Points
It uses `platform.h`, `util.h`, `lz4.h`, `lz4hc.h`, `lz4frame.h`, and `xxhash.h`. It intentionally defines `LZ4_malloc`, `LZ4_calloc`, and `LZ4_free` to exercise `LZ4_USER_MEMORY_FUNCTIONS` builds. Non-DLL builds also benchmark hidden force-ext-dict entry points.

## Risks and Test Signals
Benchmark numbers are sensitive to CPU scheduling, clock granularity, file size, and memory pressure. Some partial decompression wrappers opt out of checksum validation because they intentionally decode less than the full output. Correctness signals include nonzero compression sizes, exact decompressed sizes, XXH32 equality for checked paths, and frame input-consumption checks. Resource risks include large allocations up to the memory cap and process exits on benchmark failures.
<!-- END_FILE_RESEARCH: sources/compression/lz4/tests/fullbench.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/lz4/tests/fuzzer.c -->
# sources/compression/lz4/tests/fuzzer.c

## Purpose
`fuzzer.c` is the broad randomized regression driver for the raw LZ4 block and LZ4HC APIs. It combines deterministic unit tests, generated corpora, dictionary scenarios, streaming/ring-buffer paths, low-address buffers, malformed input, and destination-boundary checks.

## Important APIs, Types, and Functions
Major routines are `FUZ_unitTests()`, `FUZ_test()`, `FUZ_AddressOverflow()`, `FUZ_fillCompressibleNoiseBuffer()`, `FUZ_createLowAddr()`, and `main()`. It exercises default, fast, destSize, external-state, fast-reset, HC, HC destSize, streaming, dictionary attach/load, safe/fast/partial decompression, safe/fast continue, and HC continue APIs. It uses `XXH32`/`XXH64` for reference checks and directly inspects HC context cleanliness through static-linking-only internals.

## Control Flow, State, and Persistence
`main()` parses seed, count, duration, start cycle, compressibility, verbosity, and pause flags. Unless a seed/start cycle is supplied, it runs unit tests at default and optimal-min HC levels, then enters `FUZ_test()`. The randomized loop chooses block size, source offset, dictionary size, compression level, low-address placement, and corruption cases from a deterministic PRNG. State is in heap buffers, LZ4 streams, HC streams, low-address mmap or malloc buffers, checksums, and counters for compression ratios. No artifacts are persisted.

## Dependencies and Integration Points
The file depends on `platform.h`, `util.h`, `lz4.h`, `lz4hc.h`, `xxhash.h`, and `sys/mman.h` on Unix/AIX for low-address testing. It targets sanitizer and CI integration by aborting/`exit(1)` on the first invariant violation and printing seed/cycle coordinates.

## Risks and Test Signals
Covered risks include output/input overrun, too-small buffer success, exact-boundary failure handling, NULL/empty input behavior, address-space overflow on 32-bit builds, decoder shortcut OOB regressions, context dirty-state leaks, dictionary attach mismatches, ring-buffer decoder desynchronization, and HC destSize edge cases. Remaining risks are runtime cost, nondeterminism when seed is omitted, and platform differences in mmap. Signals are canary preservation, exact return sizes, checksum equality, expected failures on malformed data, and reproducible seed/cycle output.
<!-- END_FILE_RESEARCH: sources/compression/lz4/tests/fuzzer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/lz4/tests/loremOut.c -->
# sources/compression/lz4/tests/loremOut.c

## Purpose
`loremOut.c` streams generated lorem ipsum text to stdout for test data generation when the datagen CLI is used without an explicit compressibility percentage.

## Important APIs, Types, and Functions
It implements `LOREM_genOut(unsigned long long size, unsigned seed)`. The function uses a 2 KB stack buffer, calls `LOREM_genBlock()` from `lorem.h`, writes generated bytes to stdout, and updates the seed for each paragraph/block.

## Control Flow, State, and Persistence
The function sets binary stdout mode, initializes `genBlockSize` to the smaller of requested size and 2 KB, and loops until `total == size`. Each iteration asks `LOREM_genBlock()` for up to the current block size, writes exactly the generated amount, and shrinks the final block if fewer bytes remain. All state is local except stdout; no files are opened.

## Dependencies and Integration Points
It depends on `platform.h`, `loremOut.h`, `lorem.h`, stdio, and assertions. `datagencli.c` calls it as the default generator path.

## Risks and Test Signals
The implementation asserts generation bounds but does not handle `fwrite()` errors. Comments explicitly warn that output beyond one paragraph differs from `LOREM_genBuffer()` even with the same seed. Test signals are exact requested byte count, binary stdout mode, and monotonically incremented seeds across blocks.
<!-- END_FILE_RESEARCH: sources/compression/lz4/tests/loremOut.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/lz4/tests/loremOut.h -->
# sources/compression/lz4/tests/loremOut.h

## Purpose
`loremOut.h` declares the stdout-oriented lorem ipsum generator used by the data generator CLI.

## Important APIs, Types, and Functions
The single public API is `LOREM_genOut(unsigned long long size, unsigned seed)`, documented as generating `size` bytes of compressible lorem ipsum text to stdout.

## Control Flow, State, and Persistence
The header has no state, no inline logic, and no includes. Runtime behavior is entirely implemented in `loremOut.c`.

## Dependencies and Integration Points
It is included by `datagencli.c` and implemented by `loremOut.c`. It pairs with `lorem.h`/`lorem.c` buffer generation but exposes only the streaming output form.

## Risks and Test Signals
The public contract is very small, so risk is limited to declaration drift or missing include guards if included repeatedly in unusual translation units. The expected signal is successful link resolution for `LOREM_genOut()` in the datagen CLI.
<!-- END_FILE_RESEARCH: sources/compression/lz4/tests/loremOut.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/lz4/tests/roundTripTest.c -->
# sources/compression/lz4/tests/roundTripTest.c

## Purpose
`roundTripTest.c` is a file-oriented round-trip validator intended for fuzzing workflows such as AFL. It reads one file, compresses it, decompresses it, and aborts on any corruption so fuzzing infrastructure records failures as crashes.

## Important APIs, Types, and Functions
Key functions are `roundTripTest()`, `roundTripCheck()`, `fileCheck()`, `loadFile()`, `getFileSize()`, `isDirectory()`, `select_clevel()`, and `main()`. Compression dispatches through a `compressFn`: levels at or above `LZ4HC_CLEVEL_MIN` use `LZ4_compress_HC`, while lower selected levels use `LZ4_compress_fast`. `XXH32` selects a deterministic compression level when the CLI level is zero.

## Control Flow, State, and Persistence
`main()` parses an optional `-#` level and a filename. `fileCheck()` gets file size, allocates a source buffer even for empty files, loads the full file, and calls `roundTripCheck()`. The compressed and result buffers are allocated at `LZ4_COMPRESSBOUND(srcSize)`. `roundTripTest()` compresses, safely decompresses, validates decompressed size, and scans for the first differing byte. State is heap-local and freed after each check; the input file is only read.

## Dependencies and Integration Points
The file uses `lz4.h`, `lz4hc.h`, `xxhash.h`, libc file I/O, and platform-specific stat variants for MSVC versus POSIX. It is a simple fuzz harness around public block APIs.

## Risks and Test Signals
Risks include `fclose(NULL)` if `fopen()` fails after `isDirectory()` is called, size truncation when very large files exceed `int`-based LZ4 APIs, and only one file processed per invocation. Strong signals are abort-on-corruption behavior, deterministic level selection from input bytes, exact decompressed size, and byte-position reporting for silent decoding differences.
<!-- END_FILE_RESEARCH: sources/compression/lz4/tests/roundTripTest.c -->
