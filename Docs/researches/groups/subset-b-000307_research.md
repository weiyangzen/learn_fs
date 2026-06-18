# subset-b-000307 research

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/contrib/seekable_format/zstdseek_decompress.c -->
# sources/compression/zstd/contrib/seekable_format/zstdseek_decompress.c

Purpose: implements the seekable-format decompression side for zstd seekable streams. It builds a `ZSTD_seekable` object around a `ZSTD_DStream`, a parsed seek table, custom source callbacks, input/output scratch buffers, current decompression position, and an XXH64 state for optional frame checksums. It supports FILE-backed sources, memory-backed sources, and advanced caller-supplied read/seek callbacks.

Important APIs/types/functions: `ZSTD_seekable_create/free`, `ZSTD_seekable_initBuff`, `ZSTD_seekable_initFile`, `ZSTD_seekable_initAdvanced`, `ZSTD_seekable_decompress`, `ZSTD_seekable_decompressFrame`, `ZSTD_seekTable_create_fromSeekable/free`, and frame metadata accessors. Internal types include `buffWrapper_t`, `seekEntry_t`, `ZSTD_seekTable_s`, and `ZSTD_seekable_s`. Platform code defines `LONG_SEEK` to avoid 2 GiB seek limits on several targets.

Control flow: initialization stores callbacks, reads the seekable footer from end-of-file, validates the skippable-frame magic and footer descriptor, allocates one extra seek-table sentinel entry, and converts per-frame compressed/decompressed sizes into cumulative offsets. `ZSTD_seekable_decompress()` clamps the requested length to stream end, binary-searches the frame containing the requested decompressed offset, seeks to the corresponding compressed offset when needed, resets the dstream and checksum state, then decodes forward. Output before the requested offset is discarded into `outBuff`; requested bytes are written into the caller buffer. It carries `in` buffer state across calls when continuing forward within the same frame.

State and persistence: persistent state is entirely in the `ZSTD_seekable` object: parsed table, source callback, current frame, decompressed offset, buffered input position, and checksum state. There is no disk persistence beyond reading the source. Memory ownership is explicit: table entries and dstream are freed by `ZSTD_seekable_free`; copied tables are freed by `ZSTD_seekTable_free`.

Dependencies/integration: depends on zstd static APIs, `zstd_seekable.h`, `zstd_errors.h`, `mem.h`, xxhash, libc FILE IO, and platform-specific large-file seeking. It integrates with the seekable format by interpreting the terminal skippable seek table and with normal zstd streaming decode for each frame.

Risks: custom callbacks must exactly implement full reads and random seeking. `ZSTD_seekTable_getFrameDecompressedSize()` checks `frameIndex > tableLen` but then indexes `frameIndex + 1`, so callers passing exactly `tableLen` risk sentinel overrun. The no-output-progress guard protects against repeated decoder stalls, but malformed inputs still rely heavily on lower zstd errors. In-memory mode has overflow-sensitive position math. Checksums cover only seek-table checksum entries and use the low 32 bits of XXH64.

Test signals: exercise random ranges, whole-frame decompression, in-memory and FILE modes, checksum mismatch, malformed footers, truncated seek tables, empty/last frame boundaries, >4 GiB offsets on 32-bit-sensitive targets, and repeated forward calls that should reuse decoder state.
<!-- END_FILE_RESEARCH: sources/compression/zstd/contrib/seekable_format/zstdseek_decompress.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/contrib/seqBench/Makefile -->
# sources/compression/zstd/contrib/seqBench/Makefile

Purpose: builds the experimental `seqBench` utility against the local zstd source tree and selected program/common helper objects. It is a focused contrib Makefile for sequence-generation/compression benchmarking rather than a general library build.

Important variables/targets: `PROGDIR`, `LIBDIR`, `LIBZSTD`, include `CPPFLAGS`, strict warning `DEBUGFLAGS`, `default`, `all`, `seqBench`, `$(LIBZSTD)`, object rules for `benchfn.o`, `timefn.o`, `datagen.o`, `util.o`, `xxhash.o`, and `clean`.

Control flow: `seqBench` depends on helper objects, `seqBench.c`, and `../../lib/libzstd.a`; the library target recursively invokes `make -C ../../lib libzstd.a` with propagated `CFLAGS`. Each helper object is compiled directly from the programs or common source directory into the contrib directory. `clean` removes local objects, asks the library directory to clean, and deletes the binary.

State and persistence: generated state consists of local `.o` files and the `seqBench` executable plus the library build artifacts under `../../lib`. No runtime state is tracked.

Dependencies/integration: integrates with `../../programs` helper sources and `../../lib`. It assumes GNU-ish make behavior, a C compiler, archive build support in `lib/Makefile`, and warning flags accepted by the selected compiler.

Risks: the recipe compiles `$^`, so dependency ordering matters and adding headers as prerequisites would accidentally pass them to the compiler/linker. `clean` delegates to the library clean target, which can remove artifacts outside this contrib tool. The target is not portable to non-make build systems and is tied to source-tree-relative layout.

Test signals: `make -C contrib/seqBench`, `./seqBench <sample>`, and `make clean` should build, validate sequence compression, and remove generated files without affecting unrelated workspace state beyond the library clean contract.
<!-- END_FILE_RESEARCH: sources/compression/zstd/contrib/seqBench/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/contrib/seqBench/seqBench.c -->
# sources/compression/zstd/contrib/seqBench/seqBench.c

Purpose: minimal experiment for zstd's static sequence APIs. It reads one input file, generates zstd sequences, compresses those sequences with explicit block delimiters, decompresses the result, and compares the output to the original.

Important APIs/functions: `main`, `ZSTD_createCCtx`, `ZSTD_sequenceBound`, `ZSTD_generateSequences`, `ZSTD_CCtx_setParameter(ZSTD_c_blockDelimiters, ZSTD_sf_explicitBlockDelimiters)`, `ZSTD_compressSequences`, `ZSTD_decompress`, `ZSTD_isError`, and `memcmp`.

Control flow: argument count must be exactly two. The program opens the input, uses `fseek/ftell` to determine size, reads it into memory, allocates a sequence array sized by `ZSTD_sequenceBound()`, allocates a compressed buffer with `ZSTD_compressBound()`, generates sequences, compresses from sequences, then decompresses into a validation buffer. It prints success or the first mismatching byte index.

State and persistence: all state is process-local heap memory plus the created `ZSTD_CCtx`. It does not persist outputs to disk; compressed bytes are only kept in memory for validation.

Dependencies/integration: depends on `ZSTD_STATIC_LINKING_ONLY` and therefore on unstable/static zstd APIs. It is built by the adjacent Makefile with the local static library. It uses libc file IO and assumes the whole file fits into `long` and memory.

Risks: there is little error checking for `fopen`, `fseek`, `ftell`, `malloc`, `fread`, sequence-generation return values, decompression errors, or context allocation. `ZSTD_generateSequences()` can produce fewer sequences than the bound, but this example passes the bound onward rather than an observed count, so behavior depends on the API contract. The `printf("ERROR: %lu")` format is not portable for `size_t`, and the bad-index loop uses `int` against a `long` size.

Test signals: use small, empty, and larger files; run under ASan/UBSan to catch unchecked allocation/IO failures; compare generated output against `ZSTD_decompress`; and rebuild when zstd static sequence APIs change.
<!-- END_FILE_RESEARCH: sources/compression/zstd/contrib/seqBench/seqBench.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/contrib/snap/snapcraft.yaml -->
# sources/compression/zstd/contrib/snap/snapcraft.yaml

Purpose: Snapcraft packaging manifest for building a development-mode `zstd` snap exposing the `zstd`, `zstdgrep`, and `zstdless` commands from a make-based build.

Important fields: package `name: zstd`, `version: git`, summary/description, `grade: devel`, `confinement: devmode`, app commands under `usr/local/bin`, plugs `home` and `removable-media`, and a single `parts.zstd` using `source: .`, `plugin: make`, and `build-packages: [g++]`.

Control flow: Snapcraft fetches/uses the current tree as the part source, runs the make plugin, installs the resulting artifacts, and maps three commands as snap apps. Runtime file access is controlled by the listed plugs and devmode confinement.

State and persistence: build artifacts are managed by Snapcraft. The manifest itself carries no runtime persistence; installed commands read/write user files according to snap interfaces.

Dependencies/integration: integrates with Snapcraft's make plugin and assumes the upstream zstd Makefile installs into `usr/local/bin` inside the snap staging area. It depends on a C++ compiler package even though much of zstd is C, likely for build/test compatibility.

Risks: `grade: devel` and `confinement: devmode` are unsuitable for stable channel publication. The manifest does not pin a base, architectures, or install target details. Missing plugs could affect strict confinement later, while broad removable-media access may be too permissive.

Test signals: `snapcraft` should produce a snap containing all three commands; install with devmode and run compression/decompression on home and removable-media paths; strict-confinement migration should test interfaces explicitly.
<!-- END_FILE_RESEARCH: sources/compression/zstd/contrib/snap/snapcraft.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/doc/educational_decoder/Makefile -->
# sources/compression/zstd/doc/educational_decoder/Makefile

Purpose: builds and tests the educational zstd decoder harness. It is documentation-adjacent but executable, compiling all local C files into `harness` and comparing decoder output with files produced by a system `zstd`.

Important variables/targets: `ZSTD ?= zstd`, platform-specific `DIFF`, `HARNESS_FILES=*.c`, `MULTITHREAD_LDFLAGS=-pthread`, `DEBUGFLAGS=-g -DZSTD_DEBUG=1`, include paths into the real zstd tree, strict `CFLAGS`, `harness`, `clean`, and `test`.

Control flow: `harness` compiles local C files with debug/warning flags. `test` compresses `README.md`, decodes it through the educational decoder, diffs output, then trains a dictionary from repeated local files, compresses with that dictionary, decodes with `./harness tmp.zst tmp dictionary`, and diffs again.

State and persistence: produces `harness`, optional object/debug folders, temporary `tmp*` files, and a temporary `dictionary`. Clean removes local harness outputs and macOS debug folders.

Dependencies/integration: depends on an installed `zstd` CLI for tests, `diff` or `gdiff`, pthread linkage, and source-tree variables such as `ZSTDDIR` and `PRGDIR` supplied by the caller/environment.

Risks: tests are tied to `README.md` in the working directory and an installed CLI. `HARNESS_FILES=*.c` means any added C file in the directory becomes part of the harness build. The educational decoder intentionally exits on errors and is not production hardened.

Test signals: `make harness`, `make test`, dictionary and non-dictionary round trips, invalid input behavior through the harness, and compile with `ZDEC_NO_DICTIONARY` to verify conditional dictionary handling.
<!-- END_FILE_RESEARCH: sources/compression/zstd/doc/educational_decoder/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/doc/educational_decoder/harness.c -->
# sources/compression/zstd/doc/educational_decoder/harness.c

Purpose: command-line harness around the educational decoder. It loads a `.zst` file and optional dictionary into memory, chooses an output capacity, invokes `ZSTD_decompress_with_dict()`, and writes the reconstructed bytes to a named output path.

Important APIs/types/functions: `buffer_s`, `read_file`, `write_file`, `freeBuffer`, `ERR_OUT`, `MAX_COMPRESSION_RATIO`, `MAX_OUTPUT_SIZE`, `create_dictionary`, `parse_dictionary`, `ZSTD_get_decompressed_size`, `ZSTD_decompress_with_dict`, and `free_dictionary`.

Control flow: `main` requires `<file.zst> <out_path> [dictionary]`. It reads compressed input and optional dictionary, asks the decoder for frame content size, falls back to `16 * compressed_size` if unknown, caps output at 1 GiB, allocates the output buffer, parses a dictionary unless dictionary support is compiled out, decompresses, frees dictionary state, writes output, and releases all buffers.

State and persistence: state is heap buffers for input, dictionary, and output. Persistent side effect is writing the output file. Error paths call `exit(1)` and may not free all intermediate allocations.

Dependencies/integration: uses `zstd_decompress.h` and the educational decoder implementation, libc file IO, and build-time `ZDEC_NO_DICTIONARY`. It is the executable target used by the Makefile tests.

Risks: `ftell()` result is cast to `size_t` with no negative/overflow check. The fallback compression-ratio assumption can be wrong; too small an output buffer terminates through decoder error paths. `fwrite` loop can spin if `fwrite` returns zero without setting `ferror`. The implementation loads whole files into memory.

Test signals: decode known-size and unknown-size frames, dictionary and raw-content dictionary paths, oversized-output rejection, missing file errors, empty files, and compile/test with and without dictionary support.
<!-- END_FILE_RESEARCH: sources/compression/zstd/doc/educational_decoder/harness.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/doc/educational_decoder/zstd_decompress.c -->
# sources/compression/zstd/doc/educational_decoder/zstd_decompress.c

Purpose: a readable educational implementation of a single-frame zstd decoder. It follows the format specification top-down: frame header, blocks, literals, sequences, match execution, optional dictionaries, and low-level HUF/FSE/bitstream primitives. It is designed for understanding, not production error recovery.

Important APIs/types/functions: public functions are `ZSTD_decompress`, `ZSTD_decompress_with_dict`, `ZSTD_get_decompressed_size`, `create_dictionary`, `parse_dictionary`, and `free_dictionary`. Core internal types include `istream_t`, `ostream_t`, `HUF_dtable`, `FSE_dtable`, `frame_header_t`, `frame_context_t`, `dictionary_s`, `sequence_command_t`, and `sequence_states_t`. Major internal routines include `decode_frame`, `parse_frame_header`, `decompress_data`, `decode_literals`, `decode_huf_table`, `decode_sequences`, `decode_seq_table`, `execute_sequences`, `compute_offset`, `execute_match_copy`, `FSE_decode_header`, `FSE_init_dtable`, and `HUF_init_dtable_usingweights`.

Control flow: `ZSTD_decompress()` creates an empty dictionary and delegates to `ZSTD_decompress_with_dict()`. That wraps input/output buffers in bounds-checked stream objects and decodes one zstd frame. `decode_frame()` validates magic, initializes frame context, parses the header, applies dictionary tables/content, then loops over blocks. Raw and RLE blocks copy directly; compressed blocks split into literal and sequence sections. Literal decoding handles raw/RLE and Huffman-compressed modes, including repeat tables. Sequence decoding reads the count, decodes FSE mode tables, consumes the reverse bitstream into literal length, match length, and offset commands, then execution copies literals and overlapping matches, including dictionary-backed references. Cleanup frees entropy tables after a frame.

State and persistence: frame-local state carries repeated HUF/FSE tables, dictionary pointers, output history length, and repeat offsets across blocks. Parsed dictionaries persist entropy tables, content, prior offsets, and dictionary id until freed. IO streams update in-memory pointers and lengths only; no files are touched.

Dependencies/integration: self-contained C using libc plus `zstd_decompress.h`. The harness and Makefile expose it to CLI tests. It intentionally mirrors zstd format concepts but does not depend on libzstd internals.

Risks: all errors call `exit(1)`, unsuitable for library embedding. It assumes a single frame and rejects skippable/non-zstd frames. Content checksum is skipped rather than verified. It loads output into caller-provided contiguous memory and has simplified bounds/model handling. The decoder is sensitive to malformed bitstreams, table limits, dictionary-id mismatch, and repeated-offset edge cases.

Test signals: Makefile round trips with and without dictionary, fuzz invalid/truncated frames, raw/RLE/compressed block coverage, repeated and FSE-compressed table modes, unknown content size handling through harness, dictionary-id mismatch, and compare outputs against libzstd on a corpus of small frames.
<!-- END_FILE_RESEARCH: sources/compression/zstd/doc/educational_decoder/zstd_decompress.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/doc/educational_decoder/zstd_decompress.h -->
# sources/compression/zstd/doc/educational_decoder/zstd_decompress.h

Purpose: public header for the educational decoder. It exposes a small API for whole-buffer decompression, optional parsed-dictionary decompression, decompressed-size discovery, and dictionary lifecycle management.

Important APIs/types: opaque `dictionary_t`; `ZSTD_decompress(dst, dst_len, src, src_len)`; `ZSTD_decompress_with_dict(dst, dst_len, src, src_len, parsed_dict)`; `ZSTD_get_decompressed_size(src, src_len)`; `create_dictionary()`; `parse_dictionary(dict, src, src_len)`; and `free_dictionary(dict)`.

Control flow/integration: callers create or parse dictionaries separately, allocate an output buffer large enough for the reconstructed frame, and call the decompression function. The implementation assumes a single frame and returns bytes written. The harness uses `ZSTD_get_decompressed_size()` first, then dictionary creation/parsing, then `ZSTD_decompress_with_dict()`.

State and persistence: the header hides dictionary internals, so table/content ownership is controlled by `create_dictionary` and `free_dictionary`. It does not define any global state or file persistence.

Dependencies: only includes `<stddef.h>` for `size_t`. It is intentionally independent of the production `zstd.h` API despite similar names.

Risks: no include guard is present in this header, so repeated inclusion could redeclare types/functions in unusual compile units. The API name overlaps production zstd symbols, so linking this educational decoder with libzstd can create symbol conflicts. Error behavior is not visible from the header: implementation exits instead of returning error codes.

Test signals: compile with multiple C files including the header, call dictionary and non-dictionary paths, verify returned decompressed sizes, and ensure consumers do not link both educational and production `ZSTD_decompress` symbols unintentionally.
<!-- END_FILE_RESEARCH: sources/compression/zstd/doc/educational_decoder/zstd_decompress.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/examples/Makefile -->
# sources/compression/zstd/examples/Makefile

Purpose: builds and smoke-tests the zstd example programs against the local static library. It demonstrates one-shot, dictionary, streaming, multi-file, and memory-usage APIs.

Important targets: `all`, `$(LIB)`, each example binary target, `clean`, and `test`. `LIBDIR=../lib`, `CPPFLAGS += -I$(LIBDIR)`, and `LIB=$(LIBDIR)/libzstd.a` are central integration variables.

Control flow: `all` builds all listed example executables. Each object depends on `common.h`, and each binary depends on the static library. The library target recursively invokes `make -C ../lib libzstd.a`. `test` copies sample files, runs simple compression/decompression, multiple-file examples, streaming decompression, memory usage checks, invalid-input negative tests, zero-size file round trip, streaming multi-file compression, and dictionary compression/decompression.

State and persistence: generated executables, `.o` files, `tmp*`, `result*`, and `.zst` files are local build/test outputs. `clean` removes them.

Dependencies/integration: GNU make, local zstd library Makefile, C compiler/linker defaults, and `README.md`/`Makefile` as test inputs. It relies on shell `!` for expected-failure checks.

Risks: a new example must be added in several places to build and clean. The test suite mutates temporary files in the examples directory and can overwrite matching `tmp*` or `.zst` files. The threaded thread-pool example is not included in `all` here, despite being present in the directory.

Test signals: `make -C examples test`, negative invalid-input commands must fail, zero-byte compression must pass, and every binary should link against the local `libzstd.a`.
<!-- END_FILE_RESEARCH: sources/compression/zstd/examples/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/examples/common.h -->
# sources/compression/zstd/examples/common.h

Purpose: shared helper header for zstd examples. It provides fatal-check macros and small file/memory utilities so example source files can focus on zstd API usage.

Important APIs/types: `COMMON_ErrorCode`, `CHECK`, `CHECK_ZSTD`, `fsize_orDie`, `fopen_orDie`, `fclose_orDie`, `fread_orDie`, `fwrite_orDie`, `malloc_orDie`, `loadFile_orDie`, `mallocAndLoadFile_orDie`, and `saveFile_orDie`. `HEADER_FUNCTION` marks helpers static and optionally unused.

Control flow: helpers either return successful results or print an error and exit with a specific code. File helpers use `stat`, `fopen`, `fread`, `fwrite`, and `fclose`. `mallocAndLoadFile_orDie()` sizes a file, allocates exactly that much memory, then loads it. `CHECK_ZSTD` wraps zstd return codes with `ZSTD_isError()` and `ZSTD_getErrorName()`.

State and persistence: no persistent state. File helpers read and write named paths and allocate caller-owned memory. Error paths terminate the process.

Dependencies/integration: includes libc headers, `sys/stat.h`, and public `zstd.h`. Every examples `.c` file includes it, making its static functions local to each translation unit.

Risks: fatal exits are appropriate for examples but not reusable library helpers. `malloc_orDie(0)` may fail on implementations returning NULL for zero-byte allocation, affecting empty-file cases through `mallocAndLoadFile_orDie`. `fread_orDie` allows short reads on EOF, which is useful for streaming loops but can hide unexpectedly short fixed reads if misused. `saveFile_orDie` and `loadFile_orDie` duplicate some low-level checks instead of using the wrapper functions consistently.

Test signals: examples test suite, large-file size conversion checks, missing files, write-permission failures, zero-length files, and zstd error wrapping.
<!-- END_FILE_RESEARCH: sources/compression/zstd/examples/common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/examples/dictionary_compression.c -->
# sources/compression/zstd/examples/dictionary_compression.c

Purpose: demonstrates one-shot compression of multiple files using a pre-trained zstd compression dictionary loaded once into a `ZSTD_CDict`.

Important functions/APIs: `createCDict_orDie`, `compress`, `createOutFilename_orDie`, `main`, `ZSTD_createCDict`, `ZSTD_createCCtx`, `ZSTD_compress_usingCDict`, `ZSTD_freeCCtx`, `ZSTD_freeCDict`, and helpers from `common.h`.

Control flow: `main` expects one or more input files plus a final dictionary path. It creates a `ZSTD_CDict` at level 3, loops over inputs, creates `<input>.zst` names, loads each file, allocates a compression-bound buffer, compresses using the dictionary in a fresh CCtx, saves output, prints sizes, and frees per-file buffers.

State and persistence: the dictionary object persists for all files. Per-file input/compressed buffers and CCtx are transient. Persistent side effects are `.zst` output files beside the inputs.

Dependencies/integration: public zstd dictionary API, trained dictionary from `zstd --train` or zdict APIs, and `common.h` fatal helpers. The examples Makefile uses it in dictionary tests.

Risks: no dictionary training is performed here; invalid or mismatched dictionary content will surface as zstd errors. Output naming blindly appends `.zst` and can overwrite existing files. It creates a new CCtx per file even though the dictionary is reused; that is simpler but not optimal.

Test signals: compress several files with a trained dictionary, decompress with `dictionary_decompression.c`, verify dictionary ID presence, test invalid dictionary files, and confirm cleanup of output-name allocations.
<!-- END_FILE_RESEARCH: sources/compression/zstd/examples/dictionary_compression.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/examples/dictionary_decompression.c -->
# sources/compression/zstd/examples/dictionary_decompression.c

Purpose: demonstrates in-memory decompression of one or more zstd frames using a preloaded decompression dictionary.

Important functions/APIs: `createDict_orDie`, `decompress`, `main`, `ZSTD_createDDict`, `ZSTD_getFrameContentSize`, `ZSTD_getDictID_fromDDict`, `ZSTD_getDictID_fromFrame`, `ZSTD_createDCtx`, `ZSTD_decompress_usingDDict`, `ZSTD_freeDCtx`, and `ZSTD_freeDDict`.

Control flow: the last CLI argument is the dictionary; earlier arguments are compressed files. For each file, it loads the compressed buffer, requires a known frame content size, allocates the result buffer, compares the frame dictionary ID to the loaded DDict ID, decompresses, verifies returned size, prints a summary, and frees buffers.

State and persistence: one `ZSTD_DDict` persists across all file decodes. Decompressed output is kept in memory only and not written to disk.

Dependencies/integration: relies on frames that include content size and dictionary ID, which the paired dictionary compression example writes by default. Uses `common.h` fatal checks.

Risks: frames without content size are rejected even though streaming decompression could handle them. Raw dictionaries may have ID zero, which can make ID checks less discriminating. Output is not saved, so this is a validation example rather than a decompression utility.

Test signals: paired dictionary round trip from the Makefile, wrong dictionary ID rejection, unknown content-size rejection, non-zstd input rejection, and multi-file reuse of the same DDict.
<!-- END_FILE_RESEARCH: sources/compression/zstd/examples/dictionary_decompression.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/examples/multiple_simple_compression.c -->
# sources/compression/zstd/examples/multiple_simple_compression.c

Purpose: shows efficient one-shot compression of many files by preallocating buffers and reusing one `ZSTD_CCtx`.

Important types/functions: `resources`, `createResources_orDie`, `freeResources`, `compressFile_orDie`, `main`, `ZSTD_createCCtx`, `ZSTD_compressCCtx`, `ZSTD_compressBound`, and common file helpers.

Control flow: resource creation scans all input arguments to find maximum file size and filename length, allocates one input buffer, one compressed buffer, an output filename buffer, and one CCtx. The main loop copies each input name into the reusable output-name buffer with `.zst`, loads the file into the reusable input buffer, compresses into the reusable compressed buffer, and writes the result.

State and persistence: reusable buffers and context persist for all files. Output files are written as `<input>.zst`. No cross-process state exists.

Dependencies/integration: public zstd simple compression API and `common.h`. It is part of examples Makefile tests.

Risks: all files must fit into memory and into `size_t`. Scanning all files before compression means any missing file aborts before producing outputs. Output naming may overwrite existing `.zst` files. The context is reused without explicit reset; `ZSTD_compressCCtx` handles one-shot context reuse under the public API.

Test signals: compress multiple files of different sizes, include zero-length file coverage, compare decompressed output, and test long filenames near the computed output-name capacity.
<!-- END_FILE_RESEARCH: sources/compression/zstd/examples/multiple_simple_compression.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/examples/multiple_streaming_compression.c -->
# sources/compression/zstd/examples/multiple_streaming_compression.c

Purpose: demonstrates streaming compression of multiple files while reusing input/output buffers and a `ZSTD_CCtx`.

Important types/functions: `resources`, `createResources_orDie`, `freeResources`, `compressFile_orDie`, `main`, `ZSTD_CStreamInSize`, `ZSTD_CStreamOutSize`, `ZSTD_CCtx_setParameter`, `ZSTD_CCtx_reset`, and `ZSTD_compressStream2`.

Control flow: resources are allocated once at compression level 7 with checksum enabled. Each file opens input/output, resets only the compression session while keeping sticky parameters, reads chunks of recommended input size, chooses `ZSTD_e_continue` or `ZSTD_e_end`, loops until the chunk is consumed or the frame ends, writes produced output, then closes files. Output filename buffer grows as needed.

State and persistence: buffers and CCtx persist across files; context session state is reset before each file. Outputs are `<input>.zst`.

Dependencies/integration: public streaming compression API, `common.h`, examples Makefile. It illustrates the sticky-parameter contract of `ZSTD_CCtx_reset(..., ZSTD_reset_session_only)`.

Risks: the loop uses `read < toRead` to detect the last chunk, which is correct for regular fread EOF patterns but means a read error must be caught by `fread_orDie`. Output names are appended blindly. Any fatal helper exits the whole multi-file run.

Test signals: multiple files, empty file, files exactly equal to `ZSTD_CStreamInSize()`, checksum verification via decompression, and reuse behavior after compressing several files.
<!-- END_FILE_RESEARCH: sources/compression/zstd/examples/multiple_streaming_compression.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/examples/simple_compression.c -->
# sources/compression/zstd/examples/simple_compression.c

Purpose: smallest one-shot compression example: read one file fully into memory, compress with `ZSTD_compress`, and save `<file>.zst`.

Important functions/APIs: `compress_orDie`, `createOutFilename_orDie`, `main`, `ZSTD_compressBound`, `ZSTD_compress`, `CHECK_ZSTD`, and common file/memory helpers.

Control flow: require exactly one input file, allocate an output name, load the input file, allocate `ZSTD_compressBound(input_size)` bytes, compress at level 1, save compressed bytes, print a summary, and free buffers.

State and persistence: all runtime state is local heap memory. Persistent side effect is the `.zst` output file.

Dependencies/integration: public zstd simple API and `common.h`; built and tested by examples Makefile.

Risks: whole-file memory use and blind output overwrite. It does not set frame checksum or advanced parameters. It is intentionally fatal-on-error.

Test signals: compress regular and zero-size files, decompress with `simple_decompression` or zstd CLI, and test missing/permission-denied input failures.
<!-- END_FILE_RESEARCH: sources/compression/zstd/examples/simple_compression.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/examples/simple_decompression.c -->
# sources/compression/zstd/examples/simple_decompression.c

Purpose: in-memory one-shot decompression example for frames with known content size. It validates that compressed data is zstd and that the frame declares its original size.

Important functions/APIs: `decompress`, `main`, `ZSTD_getFrameContentSize`, `ZSTD_decompress`, `ZSTD_CONTENTSIZE_ERROR`, `ZSTD_CONTENTSIZE_UNKNOWN`, `CHECK_ZSTD`, and common helpers.

Control flow: require one compressed file path, load it, query frame content size, reject non-zstd or unknown-size frames, allocate exact output size, decompress, verify returned size, print summary, and free buffers.

State and persistence: decompressed data is only in memory; no output file is written.

Dependencies/integration: public zstd simple decompression API and `common.h`. The examples Makefile uses it for positive and invalid-input negative tests.

Risks: rejects legitimate frames without content size. Whole-file compressed and decompressed buffers must fit in memory. It is a validator/demo, not a general decompressor.

Test signals: paired output from `simple_compression`, invalid uncompressed input must fail, zero-size frame must succeed, unknown content-size frames should be rejected with a clear check failure.
<!-- END_FILE_RESEARCH: sources/compression/zstd/examples/simple_decompression.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/examples/streaming_compression.c -->
# sources/compression/zstd/examples/streaming_compression.c

Purpose: demonstrates streaming compression of one file with configurable compression level and worker count, checksum enabled, and recommended zstd stream buffer sizes.

Important functions/APIs: `compressFile_orDie`, `createOutFilename_orDie`, `main`, `ZSTD_createCCtx`, `ZSTD_CCtx_setParameter`, `ZSTD_c_compressionLevel`, `ZSTD_c_checksumFlag`, `ZSTD_c_nbWorkers`, `ZSTD_compressStream2`, `ZSTD_e_continue`, and `ZSTD_e_end`.

Control flow: parse `FILE [LEVEL] [THREADS]`, open input/output, allocate recommended buffers, create CCtx, set parameters, optionally request workers, then read chunks. For each chunk, choose end directive based on EOF, repeatedly call `ZSTD_compressStream2` until input is consumed or final frame is complete, and write each produced output buffer.

State and persistence: CCtx and buffers exist for one file. Output persists as `<input>.zst`.

Dependencies/integration: public zstd streaming API, optional multithread support in the linked library, `common.h` IO helpers. It is included in example tests.

Risks: `atoi` rejects level/thread value `0`, so level 0/default cannot be requested through this example. If linked libzstd lacks multithreading, worker setting emits a note and continues. Output overwrite is unchecked.

Test signals: compress with default and explicit level/thread values, decompress output, test exact-buffer-size and empty inputs, and run against both multithread-enabled and single-thread libraries.
<!-- END_FILE_RESEARCH: sources/compression/zstd/examples/streaming_compression.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/examples/streaming_compression_thread_pool.c -->
# sources/compression/zstd/examples/streaming_compression_thread_pool.c

Purpose: demonstrates parallel file compression using pthreads and, when static-only zstd APIs are available, a shared `ZSTD_threadPool` attached to each compression context.

Important types/functions/APIs: `compress_args_t`, `compressFile_orDie`, `createOutFilename_orDie`, `main`, `pthread_create`, `pthread_join`, `ZSTD_createThreadPool`, `ZSTD_CCtx_refThreadPool`, `ZSTD_c_nbWorkers`, and streaming compression APIs.

Control flow: CLI expects `POOL_SIZE LEVEL FILES`. In static-linking builds it creates one shared thread pool; otherwise each zstd context uses its own pool. It allocates arrays of pthreads and args, starts one OS thread per input file, each thread creates its own CCtx and file buffers, optionally references the shared zstd pool, sets compression level/checksum/16 workers, streams input to `<file>.zst`, frees per-thread output name, and returns. Main joins all threads and frees the pool.

State and persistence: per-thread state is isolated except the optional shared zstd thread pool. Persistent outputs are `.zst` files. Args/thread arrays are process-local.

Dependencies/integration: pthreads, public zstd streaming API, static-only thread-pool API behind `ZSTD_STATIC_LINKING_ONLY`, and `common.h`. It is not included in the examples Makefile `all` target in this source snapshot.

Risks: pthread creation return values are not checked. Thread count equals input file count and can oversubscribe. Each compression context also requests 16 workers, so total concurrency can be very high. Output names are freed in worker threads; args arrays are freed only by process exit. Shared-pool behavior depends on static API availability.

Test signals: build with `-pthread` and static-only APIs, compress several files with a small pool size, verify outputs, run under TSAN/ASan, and test pthread creation failures or very large file lists.
<!-- END_FILE_RESEARCH: sources/compression/zstd/examples/streaming_compression_thread_pool.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/examples/streaming_decompression.c -->
# sources/compression/zstd/examples/streaming_decompression.c

Purpose: streaming decompression example that reads a file containing one or more concatenated zstd frames and writes decompressed bytes to stdout.

Important functions/APIs: `decompressFile_orDie`, `main`, `ZSTD_DStreamInSize`, `ZSTD_DStreamOutSize`, `ZSTD_createDCtx`, `ZSTD_decompressStream`, `ZSTD_freeDCtx`, and common IO helpers.

Control flow: open input and use stdout as output, allocate recommended buffers, create DCtx, read chunks, and while input remains call `ZSTD_decompressStream` into an output buffer and write produced bytes. It tracks `lastRet`; after EOF, empty input is rejected and nonzero `lastRet` means the final frame was truncated.

State and persistence: DCtx keeps streaming decompression state across calls and automatically resets at frame boundaries. Persistent effect is writing to stdout, which may be redirected by tests.

Dependencies/integration: public zstd streaming decompression API and `common.h`. The examples Makefile uses it for positive decompression and invalid-input negative tests.

Risks: closes `stdout` via `fclose_orDie(fout)`, which is acceptable for this standalone process but can surprise embedding/reuse. It intentionally rejects trailing non-zstd data at EOF. All errors terminate.

Test signals: decompress output from simple and streaming compression, concatenated frames, empty input must fail, invalid input must fail, truncated frame must report EOF before stream end.
<!-- END_FILE_RESEARCH: sources/compression/zstd/examples/streaming_decompression.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/examples/streaming_memory_usage.c -->
# sources/compression/zstd/examples/streaming_memory_usage.c

Purpose: reports and validates estimated versus actual memory usage for zstd streaming compression/decompression across compression levels, optionally with a caller-supplied window log.

Important functions/APIs: `readU32FromChar`, `main`, `ZSTD_createCCtxParams`, `ZSTD_CCtxParams_setParameter`, `ZSTD_estimateCStreamSize_usingCCtxParams`, `ZSTD_sizeof_CStream`, `ZSTD_sizeof_DStream`, `ZSTD_estimateDStreamSize_fromFrame`, `ZSTD_compressStream`, `ZSTD_endStream`, and `ZSTD_decompressStream`.

Control flow: parse optional window-log-like numeric value with K/M suffix support. For each level up to `MAX_TESTED_LEVEL`, set compression level and window log in params, create CCtx and apply params, compress a tiny in-memory payload without pledged size, finish the frame, create DCtx with optional max window log, decompress the frame, compare actual context sizes to estimates, print KB values, then free contexts. If a window log was supplied, only one level is tested.

State and persistence: all data is in fixed stack buffers and heap zstd contexts; no files are touched.

Dependencies/integration: static-linking-only zstd visibility for size estimation APIs, `common.h` checks, public streaming APIs.

Risks: `readU32FromChar` can overflow silently and does little validation after numeric suffix parsing. The sample payload is tiny, so it exercises maximum allocation behavior by API choice rather than realistic throughput. Output is informational and can vary by build options.

Test signals: examples Makefile invokes it; run with no argument and with explicit window log values, verify actual sizes do not exceed estimates, and test unusual suffix strings.
<!-- END_FILE_RESEARCH: sources/compression/zstd/examples/streaming_memory_usage.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/lib/Makefile -->
# sources/compression/zstd/lib/Makefile

Purpose: primary make entry point for building, cleaning, installing, and uninstalling libzstd static/shared libraries. It composes source lists from `libzstd.mk`, supports optional modules, selects platform-specific shared-library naming/link flags, and uses flag-derived object cache directories.

Important variables/targets: module toggles `ZSTD_LIB_COMPRESSION`, `ZSTD_LIB_DECOMPRESSION`, `ZSTD_LIB_DICTBUILDER`, `ZSTD_LIB_DEPRECATED`; `ZSTD_FILES`, `ZSTD_LOCAL_OBJ`, `VERSION`; `CPPFLAGS_DYNLIB`, `CPPFLAGS_STATICLIB`, `LDFLAGS_DYNLIB`; `libzstd.a`, `libzstd`, `lib`, `%-mt`, `%-nomt`, `%-release`, object pattern rules, `clean`, `libzstd-nomt`, `libzstd.pc`, `install-*`, and `uninstall`.

Control flow: module toggles prune incompatible components, then `libzstd.mk` supplies file/version lists. Without `BUILD_DIR`, library targets reinvoke make with `BUILD_DIR=obj/$(HASH_DIR)` to separate artifacts by flags. With `BUILD_DIR`, static and dynamic object directories are created, sources compile with dependency files, archives or shared libraries are linked, and final artifacts are copied/symlinked into `lib/`. Pattern suffix targets adjust threading and debug flags.

State and persistence: persistent outputs include `libzstd.a`, versioned shared libraries or Windows DLL/import libraries, `obj/` cached objects/dependencies, symlinks, and generated `libzstd.pc`. Install targets write into `DESTDIR`/prefix library/include/pkgconfig paths.

Dependencies/integration: make, compiler, archiver, platform `install`, `sed`, symlink command, `libzstd.mk`, source tree layout, and platform variables from included makefiles. It integrates with examples/contrib via recursive `make -C lib`.

Risks: recursive rebuild logic can be hard to reason about. `clean` removes all `obj/*` and library artifacts. Platform-specific soname/install behavior must stay correct for Darwin, AIX, Windows, BSD, SunOS, and Linux. Module toggles can silently disable dictbuilder/deprecated when compression/decompression are disabled.

Test signals: build `lib`, `libzstd.a`, `libzstd-mt`, `libzstd-nomt`, `lib-release`; run examples; verify generated pkg-config fields; install/uninstall under `DESTDIR`; inspect shared-library soname/symlinks.
<!-- END_FILE_RESEARCH: sources/compression/zstd/lib/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/lib/common/allocations.h -->
# sources/compression/zstd/lib/common/allocations.h

Purpose: centralizes zstd custom-memory allocation wrappers. It adapts the public `ZSTD_customMem` callback structure to internal allocation, calloc, and free calls with default fallbacks.

Important functions: `ZSTD_customMalloc`, `ZSTD_customCalloc`, and `ZSTD_customFree`, all `MEM_STATIC`. Dependencies expose `ZSTD_malloc`, `ZSTD_calloc`, `ZSTD_free`, and `ZSTD_memset`.

Control flow: malloc uses `customMem.customAlloc` when set, otherwise default allocator. calloc uses custom allocation plus explicit zeroing when custom allocation is supplied, otherwise default calloc. free ignores NULL; for non-NULL it uses `customFree` if present, otherwise default free.

State and persistence: no state. Ownership follows the allocator selected by the `ZSTD_customMem` value passed through contexts.

Dependencies/integration: includes `zstd_deps.h`, `compiler.h`, and static-linking-only `zstd.h` for `ZSTD_customMem`. Used by compression/decompression contexts that support caller-provided memory.

Risks: a partially configured `ZSTD_customMem` with custom allocation but missing matching free will allocate with the custom allocator and free with the default allocator, which is unsafe unless upstream validation prevents it. Custom calloc assumes the custom allocator returns memory suitable for `ZSTD_memset`.

Test signals: contexts with default allocator, full custom allocator/free pair, allocation failure, zero-size allocation behavior, and sanitizer checks for allocator mismatch.
<!-- END_FILE_RESEARCH: sources/compression/zstd/lib/common/allocations.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/lib/common/bits.h -->
# sources/compression/zstd/lib/common/bits.h

Purpose: provides low-level bit counting, common-byte counting, high-bit, and rotate helpers used by zstd compression, decompression, and entropy code.

Important functions: `ZSTD_countTrailingZeros32/64`, `ZSTD_countLeadingZeros32/64`, fallback De Bruijn implementations, `ZSTD_NbCommonBytes`, `ZSTD_highbit32`, and `ZSTD_rotateRight_U64/U32/U16`.

Control flow: functions prefer compiler intrinsics on MSVC/GCC/ICCARM and fall back to portable arithmetic. 64-bit versions use native 64-bit intrinsics when available, otherwise split into high/low 32-bit words. `ZSTD_NbCommonBytes()` chooses trailing or leading zero count depending on endian. Rotate helpers mask counts to encourage compiler recognition and avoid undefined shift counts, while asserting valid ranges.

State and persistence: no mutable state; all helpers are inline/static.

Dependencies/integration: includes `mem.h` for integer types, endian/word-size helpers, and assertions. Used by match finding, entropy parsing, bitstream handling, and table decoding.

Risks: most count functions assert input is nonzero; passing zero in release builds can still invoke undefined compiler intrinsic behavior. Architecture conditional paths must match compiler support. Rotate functions assert count bounds but rely on callers to avoid invalid counts.

Test signals: unit tests for zero-excluded inputs, endian-dependent common-byte results, 32/64-bit builds, MSVC/GCC/Clang fallback configurations, and rotate outputs for boundary counts.
<!-- END_FILE_RESEARCH: sources/compression/zstd/lib/common/bits.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/lib/common/bitstream.h -->
# sources/compression/zstd/lib/common/bitstream.h

Purpose: inline bitstream encoder/decoder used by FSE/HUF entropy code. Encoders write forward into a buffer but produce a stream decoded backward as a LIFO bit stack.

Important types/functions: `BIT_CStream_t`, `BIT_DStream_t`, `BIT_DStream_status`, `BIT_initCStream`, `BIT_addBits`, `BIT_addBitsFast`, `BIT_flushBits`, `BIT_flushBitsFast`, `BIT_closeCStream`, `BIT_initDStream`, `BIT_lookBits`, `BIT_readBits`, `BIT_readBitsFast`, `BIT_skipBits`, `BIT_reloadDStream`, `BIT_reloadDStreamFast`, and `BIT_endOfDStream`.

Control flow: compression initializes a local bit container and buffer pointers, accumulates bit fields, flushes whole bytes to memory, appends a one-bit end marker on close, and reports zero if the destination overflowed. Decompression initializes from an exact source size, validates the end marker from the last byte, loads a machine-word container from the end of the stream, reads bits from high positions while advancing `bitsConsumed`, and reloads backward through the buffer with status values distinguishing unfinished, end-of-buffer, completed, and overflow.

State and persistence: stream state lives in the `BIT_*Stream_t` structs: container, bit position/consumption, and buffer pointers. No globals.

Dependencies/integration: `mem.h` for endian unaligned access, `compiler.h` for inline/branch attributes, `debug.h`, `error_private.h`, and `bits.h`. Optional BMI2 intrinsics accelerate masking.

Risks: fast/unsafe functions require clean values, nonzero bit counts, and valid buffer space. Many look/read functions rely on caller ensuring enough bits are loaded. Incorrect source size or missing end marker is detected as corruption, but misuse can become undefined behavior through shifts or out-of-range pointer arithmetic.

Test signals: round-trip bit sequences with varied bit widths, small source sizes below container width, overflow destination buffers, malformed end marker, 32-bit and 64-bit builds, BMI2 and non-BMI2 paths, and exact `BIT_endOfDStream` completion.
<!-- END_FILE_RESEARCH: sources/compression/zstd/lib/common/bitstream.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/lib/common/compiler.h -->
# sources/compression/zstd/lib/common/compiler.h

Purpose: central portability header for compiler attributes, inlining, prefetching, branch prediction, target attributes, SIMD feature macros, fallthrough annotations, alignment helpers, pointer-overflow sanitizer workarounds, and sanitizer poisoning declarations.

Important macros/functions: `INLINE_KEYWORD`, `FORCE_INLINE_ATTR`, `FORCE_INLINE_TEMPLATE`, `HINT_INLINE`, `MEM_STATIC`, `FORCE_NOINLINE`, `TARGET_ATTRIBUTE`, `BMI2_TARGET_ATTRIBUTE`, `PREFETCH_L1/L2`, `PREFETCH_AREA`, `DONT_VECTORIZE`, `LIKELY/UNLIKELY`, `ZSTD_UNREACHABLE`, SIMD feature macros, `ZSTD_FALLTHROUGH`, `ZSTD_ALIGNOF`, `ZSTD_ALIGNED`, `ZSTD_wrappedPtrDiff`, `ZSTD_wrappedPtrAdd`, `ZSTD_wrappedPtrSub`, and `ZSTD_maybeNullPtrAdd`.

Control flow: preprocessor branches select compiler-specific syntax for GCC/Clang/MSVC/IAR/C99/C++ and platform-specific intrinsics. SIMD headers are included only when compile-time features and `ZSTD_NO_INTRINSICS` permit. Sanitizer sections declare ASan/MSan APIs when relevant and disable workspace poisoning on MinGW.

State and persistence: no runtime persistence. It shapes code generation across almost every zstd translation unit.

Dependencies/integration: includes `portability_macros.h`, `<stddef.h>`, optional compiler intrinsic headers, and sanitizer declarations. It is foundational for common, compression, decompression, and entropy code.

Risks: macro definitions affect ABI/performance and must remain compatible with many compilers. Misdetected SIMD or target attributes can break builds. Wrapped pointer helpers intentionally suppress sanitizer findings for zstd algorithms that rely on pointer wrapping; misuse could hide real bugs. Global warning pragmas for MSVC can mask warnings outside narrow code regions.

Test signals: compile matrices across GCC/Clang/MSVC/IAR, C89/C99/C++ consumers, sanitizer builds, MinGW, x86/ARM/RISC-V feature combinations, and codegen/performance checks for hot inlined paths.
<!-- END_FILE_RESEARCH: sources/compression/zstd/lib/common/compiler.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/lib/common/cpu.h -->
# sources/compression/zstd/lib/common/cpu.h

Purpose: runtime x86 CPU feature detection wrapper adapted from folly. It exposes a `ZSTD_cpuid_t` register snapshot and static predicate functions for individual CPU features.

Important types/functions/macros: `ZSTD_cpuid_t` with `f1c`, `f1d`, `f7b`, `f7c`; `ZSTD_cpuid()`; generated predicates such as `ZSTD_cpuid_sse2`, `ZSTD_cpuid_popcnt`, `ZSTD_cpuid_avx`, `ZSTD_cpuid_bmi1`, `ZSTD_cpuid_avx2`, and `ZSTD_cpuid_bmi2`.

Control flow: `ZSTD_cpuid()` initializes feature registers to zero, then on supported MSVC/x86 or GCC/Clang x86 targets executes CPUID leaf 0 to determine max leaf, leaf 1 for base features, and leaf 7 for extended features. Special inline assembly protects reserved `rbx/ebx` in clang/MSVC and i386 PIC cases. Non-x86 targets return all-zero features. Predicate functions test one bit in the captured registers.

State and persistence: no cached global state; callers can store the returned snapshot if desired.

Dependencies/integration: includes `mem.h` and optional MSVC `<intrin.h>`. Used for dynamic dispatch decisions such as BMI2-optimized entropy/table routines.

Risks: inline assembly constraints are platform-sensitive. Returning zeros on non-x86 is safe but means callers must combine this with compile-time feature checks. OS support for AVX state is represented by feature bits but callers must interpret combinations correctly when using AVX instructions.

Test signals: x86 and non-x86 compile/runtime tests, PIC 32-bit builds, clang-cl/MSVC variants, feature predicate validation against known CPU capabilities, and dynamic dispatch fallback behavior.
<!-- END_FILE_RESEARCH: sources/compression/zstd/lib/common/cpu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/lib/common/debug.c -->
# sources/compression/zstd/lib/common/debug.c

Purpose: owns the process-global debug verbosity variable used by `DEBUGLOG` and `RAWLOG` when runtime tracing is enabled.

Important symbol: `int g_debuglevel = DEBUGLEVEL`, conditionally emitted when not building a Linux kernel empty translation unit or when `DEBUGLEVEL >= 2`.

Control flow: there is no executable logic beyond global initialization. The conditional compilation avoids pedantic warnings from an empty translation unit in some kernel builds.

State and persistence: `g_debuglevel` is mutable global process state and controls debug output dynamically. It is not thread-safe.

Dependencies/integration: includes `debug.h`; macros in that header declare `extern int g_debuglevel` when `DEBUGLEVEL >= 2` and read it before printing.

Risks: global mutable verbosity can create data races if changed while other threads log. When `DEBUGLEVEL < 2`, logging macros compile away and the symbol may not exist, so external code must not depend on it unconditionally.

Test signals: build with `DEBUGLEVEL=0`, `1`, and `2+`; ensure no empty-TU warnings in kernel mode; adjust `g_debuglevel` at runtime in a debug build and verify logs appear/disappear.
<!-- END_FILE_RESEARCH: sources/compression/zstd/lib/common/debug.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/lib/common/debug.h -->
# sources/compression/zstd/lib/common/debug.h

Purpose: defines zstd/FSE debug and assertion macros. It centralizes compile-time static assertions, runtime `assert`, and optional trace printing.

Important macros/symbols: `DEBUG_STATIC_ASSERT`, `DEBUGLEVEL`, `assert`, `g_debuglevel`, `RAWLOG`, `DEBUGLOG`, stringification helpers, and dependency flags `ZSTD_DEPS_NEED_ASSERT`/`ZSTD_DEPS_NEED_IO`.

Control flow: at `DEBUGLEVEL >= 1`, real assertions are enabled through `zstd_deps.h`; otherwise `assert` is defined as a no-op if not already present. At `DEBUGLEVEL >= 2`, `g_debuglevel` is declared and `RAWLOG`/`DEBUGLOG` conditionally print through `ZSTD_DEBUG_PRINT`. Below level 2, log macros compile to empty statements.

State and persistence: the header itself has no state, but debug builds rely on the global `g_debuglevel` from `debug.c` for runtime verbosity.

Dependencies/integration: consumed across common, entropy, compression, and decompression code. It deliberately avoids pulling IO/assert dependencies unless the selected debug level requires them.

Risks: default `DEBUGLEVEL=0` removes runtime checks, so invariants must not rely on assert side effects. Global debug level is not thread-safe. Redefining `assert` can interact with prior includes; the guard avoids overriding an existing assert macro.

Test signals: compile with multiple debug levels, verify DEBUGLOG file/line formatting, assert-enabled failures in debug builds, and no extra IO dependency in release builds.
<!-- END_FILE_RESEARCH: sources/compression/zstd/lib/common/debug.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/lib/common/entropy_common.c -->
# sources/compression/zstd/lib/common/entropy_common.c

Purpose: shared FSE/HUF entropy utilities for reading normalized FSE counts and Huffman weight statistics, plus version/error wrappers for the entropy APIs.

Important functions: `FSE_versionNumber`, `FSE_isError`, `FSE_getErrorName`, `HUF_isError`, `HUF_getErrorName`, `FSE_readNCount`, `FSE_readNCount_bmi2`, `FSE_readNCount_body`, `HUF_readStats`, `HUF_readStats_wksp`, and `HUF_readStats_body`. BMI2-specialized bodies are compiled when `DYNAMIC_BMI2` is enabled.

Control flow: `FSE_readNCount_body()` decodes a compact normalized-count header. It handles small headers by copying into an 8-byte buffer and recursing, initializes counters to zero, extracts table log, then reads variable-width probabilities and zero-repeat runs while tracking remaining probability mass. It validates completion and reports consumed bytes. `HUF_readStats_body()` reads either direct 4-bit weights or FSE-compressed weights, computes rank stats and total weight, derives the implied final weight, validates tree consistency, and returns header size.

State and persistence: no persistent state. Destination arrays supplied by callers are filled with normalized counters, weights, rank stats, symbol counts, and table log values.

Dependencies/integration: depends on `mem.h`, `error_private.h`, `fse.h`, `huf.h`, and `bits.h`. It is used by both compression/decompression entropy table readers and dynamic BMI2 dispatch.

Risks: bit-level parsing is sensitive to truncated inputs, overlarge symbol counts, table-log limits, and malformed zero repeat runs. Workspace size must be sufficient for FSE decompression. BMI2 and default paths must stay behaviorally identical.

Test signals: malformed and boundary FSE headers, direct and FSE-compressed HUF weight headers, max symbol/table-log limits, small `srcSize < 8` path, BMI2 dispatch parity, and fuzzing through decompression table readers.
<!-- END_FILE_RESEARCH: sources/compression/zstd/lib/common/entropy_common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/lib/common/error_private.c -->
# sources/compression/zstd/lib/common/error_private.c

Purpose: embeds the canonical string mapping for zstd internal/public error enum values.

Important function: `ERR_getErrorString(ERR_enum code)`. It returns either a stripped generic message when `ZSTD_STRIP_ERROR_STRINGS` is defined or a switch-based message for each `PREFIX(...)` error code.

Control flow: a switch maps known error codes such as `no_error`, `prefix_unknown`, `corruption_detected`, `checksum_wrong`, parameter errors, allocation errors, dictionary errors, destination/source size errors, seekable errors, and sequence producer errors. Unknown or `maxCode` values return `"Unspecified error code"`.

State and persistence: stateless; returns pointers to string literals.

Dependencies/integration: includes `error_private.h`, which defines `ERR_enum`, `PREFIX`, and error code layout. Public wrappers such as zstd/FSE/HUF error-name APIs ultimately rely on this mapping.

Risks: adding a new error enum without updating this switch yields the generic fallback. Stripping error strings reduces binary detail and can affect diagnostics/tests expecting exact messages. Messages are user-visible enough that wording changes can break brittle tests.

Test signals: iterate every known `ERR_enum` value through `ERR_getErrorString`, verify stripped-string builds, confirm `ZSTD_getErrorName`/FSE/HUF wrappers surface expected text, and check unknown codes return fallback.
<!-- END_FILE_RESEARCH: sources/compression/zstd/lib/common/error_private.c -->
