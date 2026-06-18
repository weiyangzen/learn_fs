# Research: subset-b-000332

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/tests/zstreamtest.c -->
# sources/compression/zstd/tests/zstreamtest.c

## Purpose
`zstreamtest.c` is the main streaming API regression and randomized stress tester for zstd. It combines deterministic unit tests with seeded fuzz loops to validate `ZSTD_CStream`, `ZSTD_DStream`, `ZSTD_CCtx`, `ZSTD_DCtx`, dictionary handling, stable-buffer modes, explicit sequences, external sequence producers, multithreaded streaming compression, malformed input handling, and legacy API compatibility.

## Important APIs, Types, and Functions
Key helpers are `FUZ_rand()`, `FUZ_createDictionary()`, `SEQ_roundTrip()`, `SEQ_generateRoundTrip()`, `getCCtxParams()`, `badParameters()`, `basicUnitTests()`, `findDiff()`, `FUZ_rLogLength()`, `FUZ_randomLength()`, `FUZ_randomClampedLength()`, `setCCtxParameter()`, `fuzzerTests()`, `fuzzerTests_newAPI()`, `FUZ_usage()`, and `main()`. The file uses `buffer_t` for generated dictionary storage and `e_api` to select the older streaming fuzzer or the newer `ZSTD_compressStream2()`/parameter API fuzzer. It exercises public and static-linking-only zstd APIs including `ZSTD_initCStream()`, `ZSTD_compressStream()`, `ZSTD_flushStream()`, `ZSTD_endStream()`, `ZSTD_compressStream2()`, `ZSTD_compress2()`, `ZSTD_decompressStream()`, `ZSTD_CCtx_setParameter()`, `ZSTD_DCtx_setParameter()`, `ZSTD_CCtx_loadDictionary()`, `ZSTD_CCtx_refCDict()`, `ZSTD_DCtx_refDDict()`, `ZSTD_registerSequenceProducer()`, `ZSTD_compressSequences()`, context size estimators, and reset/init variants.

## Control Flow, State, and Persistence
`main()` parses flags (`-i`, `-T`, `-s`, `-t`, `-P`, `-v`, `-q`, `-p`, `--newapi`, `--big-tests`, `--no-big-tests`), derives or accepts a seed, runs `basicUnitTests()` when starting at test zero, then dispatches to either `fuzzerTests()` or `fuzzerTests_newAPI()`. Global state is limited to display level, display timing, optional duration limit, constants, and deterministic seed evolution. Test data is generated in memory by `RDG_genBuffer()`, dictionaries are heap-owned `buffer_t` values, and all compression/decompression contexts are explicitly allocated and freed.

`basicUnitTests()` runs a long, ordered suite over generated compressible noise. It verifies skippable frames, dictionary creation/use, stream sizing APIs, invalid compression parameters, small-increment decompression, no-forward-progress errors, null buffers, pledged source size success/failure, context reuse, empty frames, max block size memory behavior, stable input/output buffer invariants, CDict/DDict persistence and reset semantics, prefix semantics, masked dict IDs, multithreaded compression, sequence table coverage, offset-at-window-size cases, hand-crafted regression frames, raw block streaming, table reuse after uncompressible/small blocks, external sequence producer behavior, static CCtx producer registration, invalid legacy headers, and magicless streaming fallback.

`fuzzerTests()` and `fuzzerTests_newAPI()` create five source corpora with different compressibility levels, randomly choose dictionaries, sizes, flushes, frame flags, compression levels, resets, and output/input buffer sizes, then verify round-trip bytes by XXH64. They intentionally reuse contexts across iterations, occasionally destroy/recreate contexts, inject noise into compressed frames, and confirm decompression either fails cleanly or makes no unsafe progress. The new API fuzzer additionally randomizes `ZSTD_CCtx_params`, multithreading parameters, long-distance matching, rsyncable mode, deterministic ref-prefix, max block sizes, stable parameter preservation, and deterministic compressed output across repeated runs.

## Dependencies and Integration Points
The test depends on zstd public/private headers (`zstd.h`, `zstd_errors.h`, `zdict.h`), test utilities (`datagen.h`, `seqgen.h`, `util.h`, `timefn.h`, `external_matchfinder.h`), xxhash, and memory helpers. It is integrated as a CLI test binary in the zstd test suite and is sensitive to build features such as `ZSTD_MULTITHREAD`, static linking-only APIs, and deprecated API coverage. Its success criteria are process exit status plus diagnostic output; it does not persist fixtures or generated outputs.

## Risks and Test Signals
The main risks are the breadth of API contracts encoded in one large file, reliance on deterministic seeded randomness for reproducibility, high memory/runtime in big-test mode, and subtle false positives if reset/dictionary persistence assumptions change intentionally. Strong signals are successful default and `--newapi` runs with fixed seeds, targeted reruns from `-t`, big-test coverage on 64-bit builds, sanitizer/valgrind cleanliness, exact checksum comparisons, expected zstd error codes for malformed producer sequences and bad frame inputs, and no leaks across all context reset/free paths.
<!-- END_FILE_RESEARCH: sources/compression/zstd/tests/zstreamtest.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/zlibWrapper/Makefile -->
# sources/compression/zstd/zlibWrapper/Makefile

## Purpose
This Makefile builds and tests the zstd zlib-wrapper examples. It can compile the examples in normal zlib-compatible mode or with `ZWRAP_USE_ZSTD=1`, producing paired binaries that exercise zlib API calls routed through zstd-backed compression.

## Important APIs, Types, and Functions
The important targets are `all`, `release`, `test`, `test-valgrind`, `clean`, `example`, `example_zstd`, `fitblk`, `fitblk_zstd`, `minigzip`, `minigzip_zstd`, `zwrapbench`, `zstd_zlibwrapper.o`, `zstdTurnedOn_zlibwrapper.o`, and zstd library build targets. Variables include `ZLIB_LIBRARY`, `ZLIB_PATH`, `ZSTDLIBDIR`, `ZSTDLIBRARY`, `ZLIBWRAPPER_PATH`, `GZFILES`, `EXAMPLE_PATH`, `PROGRAMS_PATH`, `TEST_FILE`, `CPPFLAGS`, `STDFLAGS`, `DEBUGFLAGS`, `CFLAGS`, `LDLIBS`, and Windows `EXT`.

## Control Flow, State, and Persistence
The default path is `release`, which clears strict debug flags and builds `all`. Strict builds otherwise use C89/pedantic compatibility flags plus warning flags and include paths for zlib, zstd lib/common, programs, and wrapper sources. The zstd-enabled object is built from `zstd_zlibwrapper.c` with extra `-DZWRAP_USE_ZSTD=1`, letting the same example object link against either wrapper mode. `test` runs both normal and zstd variants, compresses/decompresses example binaries with `minigzip`, and runs `zwrapbench` on a format document and source directories. `test-valgrind` repeats core examples under valgrind. `clean` removes wrapper/example object files and generated binaries/data.

## Dependencies and Integration Points
It depends on a zlib library selected by `ZLIB_LIBRARY`/`ZLIB_PATH`, the local zstd static library under `../lib/libzstd.a`, wrapper sources in `zlibWrapper`, example sources under `examples`, gzip wrapper objects (`gzclose.o`, `gzlib.o`, `gzread.o`, `gzwrite.o`), and program utilities (`util.o`, `timefn.o`, `datagen.o`) for `zwrapbench`. It delegates building zstd libraries to `make -C ../lib`.

## Risks and Test Signals
Risks include linking against mismatched zlib headers/libraries, stale generated objects when switching `MOREFLAGS`, platform differences in executable suffixes, and tests that modify/delete local example binaries through `minigzip`. Useful signals are successful `make test`, successful `make test-valgrind`, correct production of both normal and `_zstd` variants, and clean rebuilds after `make clean`.
<!-- END_FILE_RESEARCH: sources/compression/zstd/zlibWrapper/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/zlibWrapper/examples/example.c -->
# sources/compression/zstd/zlibWrapper/examples/example.c

## Purpose
`example.c` is a zlib API example adapted to compile against `zstd_zlibwrapper.h`. It validates that the wrapper preserves common zlib behaviors for one-shot compression, gzip file APIs, streaming deflate/inflate, large buffer operation, dynamic compression parameter changes, and preset dictionaries, while skipping unsupported sync/flush recovery tests when zstd compression is enabled.

## Important APIs, Types, and Functions
The main test routines are `test_compress()`, `test_gzio()`, `test_deflate()`, `test_inflate()`, `test_large_deflate()`, `test_large_inflate()`, `test_flush()`, `test_sync()`, `test_dict_deflate()`, `test_dict_inflate()`, and `main()`. It uses zlib-compatible types and APIs from the wrapper: `Byte`, `uLong`, `z_stream`, `compress()`, `uncompress()`, `gzopen()`, `gzputc()`, `gzputs()`, `gzprintf()`, `gzseek()`, `gztell()`, `gzgetc()`, `gzungetc()`, `gzgets()`, `gzread()`, `gzclose()`, `deflateInit()`, `deflate()`, `deflateParams()`, `deflateSetDictionary()`, `deflateEnd()`, `inflateInit()`, `inflate()`, `inflateSetDictionary()`, `inflateSync()`, and `inflateEnd()`. Wrapper-specific integration uses `ZWRAP_isUsingZSTDcompression()` and `zstdVersion()`.

## Control Flow, State, and Persistence
`main()` checks zlib version compatibility, prints zlib and optional zstd versions, allocates cleared compression/decompression buffers, then runs each test. Non-`Z_SOLO` builds first validate `compress()`/`uncompress()` and `gz*` file I/O against `foo.gz` or a CLI-provided path. Small-buffer deflate/inflate force one-byte input/output chunks. Large-buffer tests compress zero-heavy data, feed already-compressed bytes through `deflateParams()`, and verify decompressed byte counts. Dictionary tests store `dictId` from the compressor stream adler and require the inflater to request and accept the same dictionary. `test_flush()` and `test_sync()` are guarded out when `ZWRAP_isUsingZSTDcompression()` reports zstd mode.

## Dependencies and Integration Points
The file depends on `zstd_zlibwrapper.h`, libc allocation/string I/O, and optional `Z_SOLO` custom allocators. It is built by the zlibWrapper Makefile into both `example` and `example_zstd`, providing a compact compatibility test for wrapper builds and gzip wrapper object integration.

## Risks and Test Signals
Risks include assuming zlib-only semantics such as `inflateSync()` recovery, which is why those tests are disabled under zstd compression, and relying on gzip seek/read behavior from wrapper-provided `gz*` functions. Signals include exact string round trips, expected `gzseek()`/`gztell()` positions for the longer wrapper test string, successful large inflate output count, successful dictionary ID handoff, and clean exit from both normal and zstd-linked binaries.
<!-- END_FILE_RESEARCH: sources/compression/zstd/zlibWrapper/examples/example.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/zlibWrapper/examples/example_original.c -->
# sources/compression/zstd/zlibWrapper/examples/example_original.c

## Purpose
`example_original.c` is the baseline upstream zlib example retained beside the wrapper-modified copy. It demonstrates zlib's one-shot, gzip-file, streaming, flush/sync recovery, dynamic parameter, and preset dictionary APIs without zstd wrapper changes.

## Important APIs, Types, and Functions
It defines the same example test surface as the adapted copy: `test_compress()`, `test_gzio()`, `test_deflate()`, `test_inflate()`, `test_large_deflate()`, `test_large_inflate()`, `test_flush()`, `test_sync()`, `test_dict_deflate()`, `test_dict_inflate()`, and `main()`. It includes `zlib.h` directly and uses `compress()`, `uncompress()`, `gz*` APIs, `deflate*`/`inflate*` streaming APIs, `deflateParams()`, `deflateSetDictionary()`, `inflateSetDictionary()`, and `inflateSync()`.

## Control Flow, State, and Persistence
`main()` validates the zlib runtime version, allocates cleared buffers, runs one-shot and gzip-file tests in non-`Z_SOLO` builds, then exercises small-buffer streaming, large-buffer streaming with parameter changes, flush/sync recovery, and preset dictionary round trips. The original test string is shorter (`"hello, hello!"`) and the dictionary is `"hello"`, so gzip seek offsets and expected line lengths differ from the wrapper-modified copy. `test_sync()` intentionally corrupts a full-flush stream and expects `inflate()` after `inflateSync()` to report `Z_DATA_ERROR` because the adler checksum is wrong.

## Dependencies and Integration Points
It depends only on zlib headers/library and standard C library facilities, with optional `Z_SOLO` allocator hooks. In this repository it functions as a comparison/reference for the wrapper-specific `example.c`, not as the Makefile's primary built source.

## Risks and Test Signals
Risks are mostly portability and example assumptions: fixed buffer sizes, direct process exits on failures, generated `foo.gz` state, and strict expectations for zlib checksum/sync behavior that wrapper mode may not support. Strong signals are exact string output, successful gzip seek/read/unget/gets behavior, `Z_STREAM_END` on normal stream completion, `Z_DATA_ERROR` after damaged full-flush recovery, and dictionary adler matching before `inflateSetDictionary()`.
<!-- END_FILE_RESEARCH: sources/compression/zstd/zlibWrapper/examples/example_original.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/zlibWrapper/examples/fitblk.c -->
# sources/compression/zstd/zlibWrapper/examples/fitblk.c

## Purpose
`fitblk.c` is a zlib-wrapper-adapted version of Mark Adler's example for fitting a compressed stream into a requested block size. It estimates how much stdin can be compressed into a target output size through one initial compression and up to two recompression passes, while routing zlib APIs through `zstd_zlibwrapper.h`.

## Important APIs, Types, and Functions
The key routines are `quit()`, `partcompress()`, `recompress()`, and `main()`. Constants `RAWLEN`, `EXCESS`, and `MARGIN` control the intermediate raw buffer size, extra first-pass output allowance, and final safety margin. It uses `z_stream`, `z_streamp`, `deflateInit()`, `deflate()`, `deflateReset()`, `deflateEnd()`, `inflateInit()`, `inflate()`, `inflateReset()`, `inflateEnd()`, plus wrapper-specific `ZWRAP_isUsingZSTDcompression()` and `zstdVersion()`.

## Control Flow, State, and Persistence
`main()` parses a single numeric target size, prints zlib and optional zstd versions, allocates `blk`, initializes a deflater, and calls `partcompress()` until either stdin ends or `size + EXCESS` output capacity fills. If all input fits with at least `EXCESS` spare bytes, it reports unused capacity and exits. Otherwise it initializes an inflater and temporary buffer, resets deflate state, recompresses the first-pass stream into `tmp`, resets both streams, then recompresses `size - MARGIN` bytes from `tmp` into `blk` with exactly `size` output capacity. The adapted file disables writes of compressed data to stdout and instead prints progress/statistics, making it a behavioral test rather than a binary filter.

## Dependencies and Integration Points
It depends on `zstd_zlibwrapper.h`, stdio/stdlib/assert, stdin input, and zlib-compatible stream semantics. The Makefile builds it as `fitblk` and `fitblk_zstd`, and test targets feed `../doc/zstd_compression_format.md` with target sizes of 10240 and 40960 bytes.

## Risks and Test Signals
Risks include relying on zlib stream behavior in a wrapper whose flush/block semantics differ, using asserts for internal invariants, memory pressure for `size + EXCESS` allocations, and disabled stdout output changing its usefulness as a real filter. Signals include successful runs in both wrapper modes, `ret == Z_STREAM_END` after final recompression, no `Z_MEM_ERROR`/`Z_ERRNO`, sane reported unused byte counts, and valgrind-clean cleanup of deflate/inflate states.
<!-- END_FILE_RESEARCH: sources/compression/zstd/zlibWrapper/examples/fitblk.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/zlibWrapper/examples/fitblk_original.c -->
# sources/compression/zstd/zlibWrapper/examples/fitblk_original.c

## Purpose
`fitblk_original.c` is the original zlib example for determining how much input can be compressed into a specified output block size. It is kept as the unmodified baseline for the wrapper-adapted `fitblk.c`.

## Important APIs, Types, and Functions
The program is organized around `quit()`, `partcompress()`, `recompress()`, and `main()`. It includes `zlib.h` directly and uses `z_stream`, `z_streamp`, `deflateInit()`, `deflate()`, `deflateReset()`, `deflateEnd()`, `inflateInit()`, `inflate()`, `inflateReset()`, and `inflateEnd()`. `RAWLEN` is 4096 bytes, `EXCESS` is 256 bytes, and `MARGIN` is 8 bytes.

## Control Flow, State, and Persistence
After parsing a requested block size of at least eight bytes, `main()` allocates `blk`, performs a first pass from stdin into `size + EXCESS` output capacity, and if the entire stream fits, writes the compressed bytes to stdout. If not, it allocates `tmp`, initializes inflate, recompresses the saved stream close to the target, resets streams, then recompresses a truncated intermediate stream into the final output buffer so completion fits within the requested size. It writes the final compressed block to stdout and emits unused-capacity stats to stderr.

## Dependencies and Integration Points
It depends only on zlib and standard C I/O/allocation/assert facilities. As a baseline example, its integration value is documenting the original algorithm and output behavior before wrapper-specific changes such as `Z_SYNC_FLUSH` in the first pass, zstd version printing, and disabled stdout writes.

## Risks and Test Signals
Risks include heuristic constants that may not fit every compressor/block behavior, assert-based invariant handling, possible write errors on stdout, and memory allocation based directly on user-provided size. Signals are valid compressed output that never exceeds the requested size, low unused-byte shortfall for sufficiently large inputs, successful decompression of emitted blocks, and no zlib stream errors or read/write failures.
<!-- END_FILE_RESEARCH: sources/compression/zstd/zlibWrapper/examples/fitblk_original.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/zlibWrapper/examples/minigzip.c -->
# sources/compression/zstd/zlibWrapper/examples/minigzip.c

## Purpose
`minigzip.c` is a minimal gzip-like command-line utility adapted to include `zstd_zlibwrapper.h`. It tests gzip-style file and pipe compression/decompression paths through the wrapper while preserving the classic zlib example's command-line behavior.

## Important APIs, Types, and Functions
The utility defines `error()`, `gz_compress()`, optional `gz_compress_mmap()`, `gz_uncompress()`, `file_compress()`, `file_uncompress()`, and `main()`. Under `Z_SOLO` it also supplies simplified `gzopen()`, `gzdopen()`, `gzwrite()`, `gzread()`, `gzclose()`, `gzerror()`, custom allocators, and a local `gzFile_s` structure around `FILE*`, mode/error fields, and `z_stream`. It uses `gzopen()`, `gzdopen()`, `gzwrite()`, `gzread()`, `gzclose()`, `gzerror()`, `deflateInit2()`, `inflateInit2()`, `deflate()`, `inflate()`, `inflateReset()`, and platform binary-mode helpers.

## Control Flow, State, and Persistence
`main()` derives behavior from argv and executable basename (`gunzip` implies decompression, `zcat` implies decompression to stdout), parses `-c`, `-d`, strategy flags `-f`/`-h`/`-r`, and compression levels `-1` through `-9`. With no file arguments it wraps stdin/stdout using `gzdopen()` and streams data. With file arguments it either writes to stdout or creates/removes `.gz` suffixed files via `file_compress()`/`file_uncompress()`. Compression loops read 16 KiB chunks and require `gzwrite()` to consume them; decompression loops call `gzread()` until zero and write each chunk. `file_compress()` and `file_uncompress()` remove the input file after successful conversion, so the program has persistent filesystem side effects.

## Dependencies and Integration Points
It depends on the zstd zlib wrapper, standard C I/O/string/allocation, optional mmap headers, platform-specific binary mode and Windows CE error helpers, and unlink/delete/remove behavior for final file replacement. The zlibWrapper Makefile builds `minigzip` and `minigzip_zstd`, and its test target uses both to compress/decompress the example binary.

## Risks and Test Signals
Risks include deliberately limited gzip utility behavior, destructive removal of input files after successful compression/decompression, simplified `Z_SOLO` gzip wrappers that read one byte at a time on inflate, filename suffix assumptions, and platform-specific binary/error handling. Signals include pipe and file round trips, strategy/level mode parsing, correct `.gz` suffix handling, successful cross-mode decompression by `minigzip_zstd`, clean close/finalization, and no leftover corrupt output after wrapper-mode compression.
<!-- END_FILE_RESEARCH: sources/compression/zstd/zlibWrapper/examples/minigzip.c -->
