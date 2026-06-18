# subset-b-000281 Research

<!-- BEGIN_FILE_RESEARCH: sources/compression/lz4/contrib/gen_manual/Makefile -->
# sources/compression/lz4/contrib/gen_manual/Makefile

## Purpose
This Makefile builds the `gen_manual` C++ utility and uses it to regenerate the HTML manuals for `lz4.h` and `lz4frame.h`. It is a maintenance/build helper rather than part of the runtime compressor.

## Important APIs, Targets, and Variables
The main targets are `default`, `gen_manual`, `manuals`, `$(LZ4MANUAL)`, `$(LZ4FMANUAL)`, and `clean`. `LZ4API`, `LZ4FAPI`, `LZ4MANUAL`, and `LZ4FMANUAL` point at the headers and generated documentation under `../../lib` and `../../doc`. The version is extracted from `lz4.h` with three `sed` commands and joined into `LZ4VER`. `CXXFLAGS`, `CPPFLAGS`, `LDFLAGS`, `MOREFLAGS`, and Windows `EXT` drive compiler behavior.

## Control Flow
`default` builds the `gen_manual` executable from `gen_manual.cpp`. The HTML manual targets depend on both the generator and the corresponding API header, then call `./gen_manual $(LZ4VER) <header> <output>`. The `manuals` phony target builds both HTML outputs. `clean` removes the generator binary.

## State and Persistence
The only persistent build outputs are `gen_manual` or `gen_manual.exe` and the two generated HTML files in `../../doc`. Version state is read dynamically from `lz4.h`; no state file is maintained.

## Dependencies and Integration Points
The Makefile depends on a working C++ compiler, POSIX-style `sed`, `rm`, and the local `gen_manual.cpp`. It integrates with the library headers and documentation tree, and its generated output format is dictated by `gen_manual.cpp`.

## Risks
The version extraction assumes the `#define LZ4_VERSION_*` lines retain the expected whitespace and numeric shape. The Makefile invokes `./gen_manual`, so cross-builds or out-of-tree builds need compatible execution on the build host. Generated manuals can become stale if header dependencies or version parsing fail silently.

## Test Signals
Useful checks are `make -C contrib/gen_manual manuals`, a clean rebuild after `make clean`, and reviewing the generated HTML for expected sections from `lz4.h` and `lz4frame.h`.
<!-- END_FILE_RESEARCH: sources/compression/lz4/contrib/gen_manual/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/lz4/contrib/gen_manual/gen-lz4-manual.sh -->
# sources/compression/lz4/contrib/gen_manual/gen-lz4-manual.sh

## Purpose
This shell script is a lightweight manual-generation wrapper. It extracts the LZ4 library version from `../../lib/lz4.h`, reports it, and runs the `gen_manual` executable against `lz4.h` and `lz4frame.h`.

## Important APIs, Commands, and Variables
The script uses `sed` to compute `LIBVER_MAJOR_SCRIPT`, `LIBVER_MINOR_SCRIPT`, and `LIBVER_PATCH_SCRIPT`, then builds `LIBVER_SCRIPT`. It calls `./gen_manual` twice with labels `lz4 <version>` and `lz4frame <version>`.

## Control Flow
Execution is linear: parse the version macros, echo `LZ4_VERSION=<version>`, generate `./lz4_manual.html`, then generate `./lz4frame_manual.html`. There is no argument parsing and no explicit error handling.

## State and Persistence
The script writes two HTML files in the current directory, unlike the Makefile target which writes into `../../doc`. It does not create temporary files or maintain state.

## Dependencies and Integration Points
It depends on `/bin/sh`, `sed`, the relative header paths, and a previously built `gen_manual` executable in the same directory. It is integrated with the same comment convention expected by `gen_manual.cpp`.

## Risks
Because there is no `set -e`, a failed version extraction or generator invocation may not halt the whole script in a clearly visible way. Its output paths differ from the Makefile's documented manual paths, so users must know whether they want local HTML files or the docs tree updated.

## Test Signals
Run it from `contrib/gen_manual` after building `gen_manual`; expect an echoed version and non-empty `lz4_manual.html` and `lz4frame_manual.html`.
<!-- END_FILE_RESEARCH: sources/compression/lz4/contrib/gen_manual/gen-lz4-manual.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/lz4/contrib/gen_manual/gen_manual.cpp -->
# sources/compression/lz4/contrib/gen_manual/gen_manual.cpp

## Purpose
`gen_manual.cpp` converts annotated LZ4 C headers into a simple HTML manual. It scans comments and declarations in a header, classifies comment markers, emits declaration blocks, chapter headings, and a contents list.

## Important APIs, Types, and Functions
The program uses C++ standard library types `std::string`, `std::vector<std::string>`, `std::stringstream`, `std::ifstream`, and `std::ofstream`. Helpers include `trim()` for removing leading/trailing marker characters, `trim_comments()` for stripping C comment delimiters, `get_lines()` for collecting lines through a terminator or empty-line boundary, and `print_line()` for emitting declaration text while stripping `LZ4LIB_API` or `LZ4FLIB_API`. `main()` owns parsing and HTML emission.

## Control Flow
`main()` requires `version`, `input_file`, and `output_html`. It loads the whole input file into memory, then iterates line by line. `typedef ... { ... }` blocks are emitted directly. Inline `/**<` or `/*!<` comments on declarations are emitted as bold declaration snippets. Larger comments are detected by markers such as `/**=`, `/*!`, `/**`, `/*-`, and `/*=`. `/*!` sections swap comment text with the following declaration block; `/*=` and `/**=` become `<h3>` sections with following declarations; other recognized comments become `<h2>` chapters and are added to the contents list. At the end, the accumulated body is wrapped in a minimal HTML document.

## State and Persistence
All parse state is in memory: `input`, `comments`, `chapters`, `linenum`, and `sout`. The only persistent result is the output HTML file. There is no incremental cache.

## Dependencies and Integration Points
It depends on specific header documentation conventions used by LZ4 headers. It is invoked by the local Makefile and shell script. It does not parse C fully; it relies on line prefixes, C comment delimiters, and empty lines.

## Risks
The parser is intentionally ad hoc. `trim_comments()` assumes both `/*` and `*/` exist and is unused in the current flow, while the main parser assumes marker positions are valid. The generated HTML is not escaped for arbitrary header text, so unusual characters in comments or declarations may affect markup. A malformed comment can desynchronize `linenum` and either skip declarations or capture too much.

## Test Signals
Generate manuals from `lz4.h` and `lz4frame.h`, then inspect that contents, chapter anchors, function declarations, typedefs, and stripped API visibility macros appear as expected.
<!-- END_FILE_RESEARCH: sources/compression/lz4/contrib/gen_manual/gen_manual.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/lz4/contrib/snap/snapcraft.yaml -->
# sources/compression/lz4/contrib/snap/snapcraft.yaml

## Purpose
This Snapcraft manifest packages the LZ4 command-line application as a strict, stable snap named `lz4`.

## Important Fields
Top-level metadata includes `name: lz4`, `version: 1.9.4`, a compression-focused summary and long description, `confinement: strict`, `grade: stable`, and `base: core20`. The `apps.lz4` command is `usr/local/bin/lz4` with the `home` plug. The single part `lz4` uses `source: ../` and the `make` plugin.

## Control Flow
Snapcraft reads the manifest, pulls the parent source tree, builds it with the make plugin, and exposes the installed `lz4` binary as the snap command.

## State and Persistence
No runtime state is defined here. Build output and installed files are managed by Snapcraft. The version is hard-coded rather than extracted from `lz4.h`.

## Dependencies and Integration Points
It integrates with Snapcraft and the repository's make-based install behavior. The strict confinement and `home` plug decide user-visible filesystem access for the packaged CLI.

## Risks
The hard-coded `1.9.4` version can drift from the repository version. `source: ../` is relative to `contrib/snap`, so moving the manifest or invoking it from unexpected layouts can change build context. Strict confinement may block workflows that expect arbitrary filesystem access outside home unless additional plugs are added.

## Test Signals
Build with Snapcraft, inspect the resulting snap metadata, run `lz4 --version` inside the snap, and test compression/decompression on files under `$HOME`.
<!-- END_FILE_RESEARCH: sources/compression/lz4/contrib/snap/snapcraft.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/lz4/examples/Makefile -->
# sources/compression/lz4/examples/Makefile

## Purpose
The examples Makefile builds and tests LZ4 sample programs against a local static `liblz4.a`. It demonstrates the library's block, frame, file, streaming, dictionary, and benchmarking APIs.

## Important Targets and Variables
`LIBDIR`, `LIBLZ4DIR`, `LIBLZ4SRCS`, `LIBLZ4OBJS`, and `SLIBLZ4` define the local static library. `ALL` lists the example programs: `print_version`, `simple_buffer`, `frameCompress`, `fileCompress`, `blockStreaming_doubleBuffer`, `blockStreaming_ringBuffer`, `streamingHC_ringBuffer`, `blockStreaming_lineByLine`, `dictionaryRandomAccess`, and `bench_functions`. `test` builds examples and the CLI under `../programs/lz4`, runs each sample, validates `.lz4` outputs with `lz4 -vt`, and runs a quick benchmark.

## Control Flow
The file includes `../build/make/multiconf.make`, uses its `static_library` helper to create `liblz4.a`, builds all example binaries, then `test` runs examples in a fixed order against `Makefile` and `.gitignore`.

## State and Persistence
Build artifacts include object files, `liblz4.a`, example binaries, compressed files, decoded files, and streaming sample files. `clean` removes these generated outputs.

## Dependencies and Integration Points
It depends on the LZ4 library source files, build helper makefiles, a C compiler, and the `../programs/lz4` CLI for validation. The examples include headers from `../lib`.

## Risks
The examples intentionally write output files beside the test inputs and use fixed suffixes; stale files can obscure failures if not cleaned. Some tests rely on `.gitignore` existing as a small file. The benchmark is timing-sensitive and should not be used as a strict performance regression gate without stronger controls.

## Test Signals
`make -C examples test` is the primary signal. Expected markers include `Verify : OK`, `verify : OK`, successful `lz4 -vt` verification, and `All done` from `bench_functions`.
<!-- END_FILE_RESEARCH: sources/compression/lz4/examples/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/lz4/examples/bench_functions.c -->
# sources/compression/lz4/examples/bench_functions.c

## Purpose
This example explains and benchmarks the public compression/decompression call stack around `LZ4_compress_default()`. It demonstrates `LZ4_compress_fast()`, `LZ4_compress_fast_extState()`, `LZ4_decompress_safe()`, and deprecated `LZ4_decompress_fast()`.

## Important APIs, Types, and Functions
It includes `lz4.h` with `LZ4_DISABLE_DEPRECATE_WARNINGS`. Local helpers are `run_screaming()`, `usage()`, `CHECK`, and `bench()`. Function IDs select benchmark cases. `bench()` uses `LZ4_stream_t` for ext-state compression, `clock()` timing, `memcmp()` verification, and a recursive retry when timer resolution is too low.

## Control Flow
`main()` parses an optional iteration count, builds two static input strings, allocates destination and known-good compressed buffers, then validates each API against the known-good result. It runs two suites: normal text and highly compressible text. Each suite times compression variants and decompression variants, then prints a formatted table of total seconds, iterations per second, nanoseconds per iteration, and percentage of default.

## State and Persistence
All state is process-local heap or stack memory. No files are read or written. The only persistent effect is stdout.

## Dependencies and Integration Points
It integrates with `examples/Makefile` as the `bench_functions` binary and depends on LZ4 block APIs. It uses POSIX feature macros for `time.h` behavior and locale formatting.

## Risks
It compares full `max_dst_size` in warm-up checks for some compression paths, so zero-initialized buffers and deterministic output matter. `clock()` is low resolution on some platforms; the recursive iteration multiplier can grow until the assert guard. The program intentionally uses deprecated unsafe decompression to teach differences; that should not be copied into untrusted-input code.

## Test Signals
Successful execution prints benchmark sections for both source classes and exits zero. Any mismatch in compressed or decompressed output calls `run_screaming()` and exits with a failure code.
<!-- END_FILE_RESEARCH: sources/compression/lz4/examples/bench_functions.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/lz4/examples/blockStreaming_doubleBuffer.c -->
# sources/compression/lz4/examples/blockStreaming_doubleBuffer.c

## Purpose
This example demonstrates block streaming with two alternating input and decode buffers. It writes a simple stream of length-prefixed compressed blocks and verifies decompression against the original file.

## Important APIs, Types, and Functions
It uses `LZ4_stream_t`, `LZ4_streamDecode_t`, `LZ4_initStream()`, `LZ4_setStreamDecode()`, `LZ4_compress_fast_continue()`, and `LZ4_decompress_safe_continue()`. Local helpers serialize `int` block sizes and raw block payloads with `fwrite()` and `fread()`. `compare()` checks file equality.

## Control Flow
`test_compress()` reads up to `BLOCK_BYTES` into alternating `inpBuf[2]` slots, compresses each block with the rolling LZ4 stream, writes the compressed size and payload, and terminates with a zero size. `test_decompress()` reads each size/payload pair, decodes into alternating `decBuf[2]` slots, and writes regenerated bytes. `main()` builds filenames, compresses, decompresses, then compares input and decoded files.

## State and Persistence
The LZ4 compression and decode contexts carry dictionary history across blocks while the double buffers keep the previous block's bytes available. Persistent outputs are `<input>.lz4s-8192` and `<input>.lz4s-8192.dec`.

## Dependencies and Integration Points
It is built by `examples/Makefile` and uses only block streaming APIs from `lz4.h`. Its custom stream format is local to the example and is not the LZ4 frame format.

## Risks
The example does not robustly check `fopen()` failures before asserts or I/O calls. It stores block sizes in host-endian `int`, so files are not portable across architectures. It breaks loops on several errors but still proceeds to verification; production code would need explicit error reporting.

## Test Signals
The example is exercised by `make test` and should print `verify : OK` after writing and decoding the streaming file.
<!-- END_FILE_RESEARCH: sources/compression/lz4/examples/blockStreaming_doubleBuffer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/lz4/examples/blockStreaming_lineByLine.c -->
# sources/compression/lz4/examples/blockStreaming_lineByLine.c

## Purpose
This example compresses a text file line by line using the streaming API and a ring buffer. It is aimed at logfile-style workloads where each message is bounded and history is retained across messages.

## Important APIs, Types, and Functions
It uses `LZ4_createStream()`, `LZ4_freeStream()`, `LZ4_compress_fast_continue()`, `LZ4_createStreamDecode()`, `LZ4_freeStreamDecode()`, and `LZ4_decompress_safe_continue()`. Block sizes are stored as `uint16_t`, and buffers are allocated dynamically based on `MESSAGE_MAX_BYTES` and `RING_BUFFER_BYTES`.

## Control Flow
`test_compress()` reads each line with `fgets()` into the current ring-buffer position, compresses it, writes a 16-bit compressed size and payload, then advances and wraps the input offset. `test_decompress()` reads size/payload pairs, decompresses into a decode ring buffer, writes regenerated bytes, and wraps similarly. `main()` compresses `<input>` to `<input>.lz4s`, decodes to `<input>.lz4s.dec`, then compares files.

## State and Persistence
The stream contexts retain prior ring-buffer data as dictionary history. Persistent outputs are the custom `.lz4s` file and decoded file.

## Dependencies and Integration Points
It is part of `examples/Makefile` and depends on `lz4.h`. The ring buffer size is deliberately much larger than the message size to satisfy streaming dictionary requirements.

## Risks
Compressed block sizes are cast to `uint16_t`; this is safe only while `LZ4_COMPRESSBOUND(messageMaxBytes)` fits in 16 bits. The example does not validate every allocation or `fopen()` result. Its format is host-endian and not self-describing.

## Test Signals
`make test` runs it on the examples Makefile and expects `Verify : OK`. Additional tests should include long lines near `MESSAGE_MAX_BYTES` and empty/final-line cases.
<!-- END_FILE_RESEARCH: sources/compression/lz4/examples/blockStreaming_lineByLine.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/lz4/examples/blockStreaming_ringBuffer.c -->
# sources/compression/lz4/examples/blockStreaming_ringBuffer.c

## Purpose
This example demonstrates streaming compression and decompression with ring buffers, including an intentionally different decode ring-buffer size to show that compressor and decoder buffers do not need to be synchronized exactly.

## Important APIs, Types, and Functions
It uses `LZ4_stream_t`, `LZ4_streamDecode_t`, `LZ4_compress_fast_continue()`, and `LZ4_decompress_safe_continue()`. Constants define `MESSAGE_MAX_BYTES`, `RING_BUFFER_BYTES`, and `DECODE_RING_BUFFER`. Helper functions read and write host-endian `int32_t` block sizes and raw payloads.

## Control Flow
`test_compress()` reads random-length chunks into a static ring buffer, compresses each chunk, writes size and payload, and wraps when the next maximum message would not fit. `test_decompress()` reads each compressed block, decodes into its own ring buffer, writes output, and wraps based on decode capacity. `main()` compresses, decompresses, and compares.

## State and Persistence
The LZ4 contexts and ring buffers hold prior block history needed by continue-mode APIs. Output files are `<input>.lz4s-0` and `<input>.lz4s-0.dec`.

## Dependencies and Integration Points
It is compiled by the examples build and links against the local LZ4 library. The random chunking uses `rand()` without an explicit seed, which gives deterministic default sequences on many C libraries but is not guaranteed as a format contract.

## Risks
The stream format is example-only and host-endian. File open failures are not handled defensively. Random chunk size can make behavior platform-dependent if `rand()` differs, though the output is immediately decoded by the same run. Production ring-buffer use must respect `LZ4_decoderRingBufferSize()` guidance.

## Test Signals
The expected success signal is `Verify : OK` after compress/decompress/compare. It is also useful to run with small and larger files to exercise wraparound.
<!-- END_FILE_RESEARCH: sources/compression/lz4/examples/blockStreaming_ringBuffer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/lz4/examples/dictionaryRandomAccess.c -->
# sources/compression/lz4/examples/dictionaryRandomAccess.c

## Purpose
This example shows how to compress independently addressable blocks with a fixed dictionary and then decompress an arbitrary byte range by using a tail jump table of block offsets.

## Important APIs, Types, and Functions
It uses `LZ4_initStream()`, `LZ4_loadDict()`, `LZ4_compress_fast_continue()`, `LZ4_setStreamDecode()`, and `LZ4_decompress_safe_continue()`. Constants define `BLOCK_BYTES`, `DICTIONARY_BYTES`, `MAX_BLOCKS`, and `kTestMagic`. Helpers perform checked binary I/O and seeking.

## Control Flow
`test_compress()` writes a magic header, then for each 1 KiB input block reloads the dictionary, compresses the block independently, writes compressed bytes, and stores cumulative offsets. It appends the offset table and count at EOF. `test_decompress()` validates magic, reads enough offsets from the tail table to cover the requested range, seeks to the first needed block, reloads the dictionary for each block, decodes, and writes only the requested slice. `main()` loads the dictionary file, compresses, decompresses the requested range, and verifies against the original input at the requested offset.

## State and Persistence
Persistent output is a custom block file `<input>.lz4s-1024` containing magic, compressed block payloads, offsets, and offset count. The decoded slice is written to `<input>.lz4s-1024.dec`.

## Dependencies and Integration Points
It integrates with `examples/Makefile` and the block streaming dictionary API. The test target runs it twice with the same file as input and dictionary, including a tiny `.gitignore` case.

## Risks
`MAX_BLOCKS` caps the number of source blocks and the offset table uses host-endian `int`. Negative offsets, negative lengths, and integer overflow are not fully defended beyond asserts and simple checks. The magic string is deliberately weak and only demonstrates versioning, not robust file identification.

## Test Signals
Expected output is `verify : OK`. Stronger tests should cover zero-length ranges, ranges ending inside a block, ranges spanning multiple blocks, small dictionary files, and malformed offset tables.
<!-- END_FILE_RESEARCH: sources/compression/lz4/examples/dictionaryRandomAccess.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/lz4/examples/fileCompress.c -->
# sources/compression/lz4/examples/fileCompress.c

## Purpose
This example uses the higher-level `lz4file.h` API to compress and decompress a file through FILE-like wrapper functions, then verifies the round trip.

## Important APIs, Types, and Functions
It uses `LZ4_writeFile_t`, `LZ4_readFile_t`, `LZ4F_writeOpen()`, `LZ4F_write()`, `LZ4F_writeClose()`, `LZ4F_readOpen()`, `LZ4F_read()`, `LZ4F_readClose()`, `LZ4F_isError()`, and `LZ4F_getErrorName()`. Local helpers are `get_file_size()`, `compress_file()`, `decompress_file()`, and `compareFiles()`.

## Control Flow
`main()` derives `.lz4` and `.lz4.dec` filenames. `compress_file()` opens an LZ4 file writer with default preferences, reads 16 KiB chunks from input, writes each chunk, closes the writer, and reports errors. `decompress_file()` opens an LZ4 reader, repeatedly reads decompressed chunks, writes them to the output file, then closes the reader. Finally, `compareFiles()` checks decoded content against the original.

## State and Persistence
It writes a frame-formatted `<input>.lz4` file and decoded `<input>.lz4.dec`. Heap state is limited to one chunk buffer and the LZ4 file contexts.

## Dependencies and Integration Points
It depends on `lz4file.h`, which wraps the frame API around standard C `FILE*` I/O. The examples Makefile validates the produced `.lz4` with the `lz4` CLI.

## Risks
Some `fopen()` results are asserted or checked inconsistently. The error reporting in `main()` passes integer return codes to `LZ4F_getErrorName()`, which is not meaningful for local `1` failures. The ratio calculation divides by original file size and can misbehave for empty input.

## Test Signals
Success prints compression stats, `decompress : done`, and `verify : OK`; `lz4 -vt <input>.lz4` should also validate the frame.
<!-- END_FILE_RESEARCH: sources/compression/lz4/examples/fileCompress.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/lz4/examples/frameCompress.c -->
# sources/compression/lz4/examples/frameCompress.c

## Purpose
This example demonstrates direct use of the LZ4 frame API for bounded-memory streaming compression and decompression. It also demonstrates injecting uncompressed data into a frame via `LZ4F_uncompressedUpdate()`.

## Important APIs, Types, and Functions
It defines `kPrefs` as `LZ4F_preferences_t` with 256 KiB linked blocks and no checksums. Compression uses `LZ4F_createCompressionContext()`, `LZ4F_compressBegin()`, `LZ4F_compressUpdate()`, `LZ4F_uncompressedUpdate()`, `LZ4F_compressEnd()`, and `LZ4F_freeCompressionContext()`. Decompression uses `LZ4F_createDecompressionContext()`, `LZ4F_getFrameInfo()`, `LZ4F_decompress()`, and `LZ4F_freeDecompressionContext()`. Important local functions are `safe_fwrite()`, `compress_file_internal()`, `compress_file()`, `get_block_size()`, `decompress_file_internal()`, `decompress_file_allocDst()`, `decompress_file()`, and `compareFiles()`.

## Control Flow
`main()` parses `<input file> [-o <offset> -d <file>]`, compresses input to `<input>.lz4`, decompresses to `<input>.lz4.dec`, then compares output. Compression writes the frame header, loops over input chunks, optionally switches to an uncompressed source file once `uncOffset` is reached, writes each compressed or uncompressed update, and ends the frame. Decompression reads enough input for the header, derives the block-size output buffer, then loops through `LZ4F_decompress()` until the frame ends and rejects trailing data.

## State and Persistence
Frame contexts hold streaming compression/decompression state. Persistent outputs are a `.lz4` frame and decoded `.lz4.dec` file. Optional uncompressed injection reads from a second file but still produces one LZ4 frame.

## Dependencies and Integration Points
It includes both `lz4frame.h` and `lz4frame_static.h`, uses `getopt()`, and is built by the examples Makefile. CLI validation of the generated frame is performed by `lz4 -vt`.

## Risks
The optional injection path has subtle offset accounting and accepts `-o 0` differently from positive offsets in user messages. Several file opens are not checked before use. Decompression intentionally supports only a single frame and treats trailing data as an error, which is stricter than concatenated-frame use cases.

## Test Signals
Successful normal execution prints frame write sizes, `decompress : done`, and `verify : OK`. Additional test signals include CLI validation, injection mode comparison against the alternate uncompressed file at the requested offset, and rejection of trailing data.
<!-- END_FILE_RESEARCH: sources/compression/lz4/examples/frameCompress.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/lz4/examples/print_version.c -->
# sources/compression/lz4/examples/print_version.c

## Purpose
This trivial example prints the linked LZ4 library version number.

## Important APIs, Types, and Functions
The only LZ4 API used is `LZ4_versionNumber()` from `lz4.h`. `main()` ignores its arguments and calls `printf()`.

## Control Flow
Execution is a single call to `printf("Hello World ! LZ4 Library version = %d\n", LZ4_versionNumber())`, then return zero.

## State and Persistence
There is no state and no persistent output beyond stdout.

## Dependencies and Integration Points
It is built by `examples/Makefile` and provides a minimal compile/link smoke test for `lz4.h` and the linked library.

## Risks
It validates only that the symbol is available and callable; it does not confirm ABI compatibility beyond returning an integer.

## Test Signals
`make test` runs it first. Expected output contains `LZ4 Library version =` followed by a numeric version.
<!-- END_FILE_RESEARCH: sources/compression/lz4/examples/print_version.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/lz4/examples/simple_buffer.c -->
# sources/compression/lz4/examples/simple_buffer.c

## Purpose
This example demonstrates the simplest block compression/decompression workflow with `LZ4_compress_default()` and `LZ4_decompress_safe()`.

## Important APIs, Types, and Functions
It uses `LZ4_compressBound()`, `LZ4_compress_default()`, and `LZ4_decompress_safe()`. Local `run_screaming()` prints an error and exits. Standard library dependencies are `malloc()`, `realloc()`, `free()`, `strlen()`, `memcmp()`, and `printf()`.

## Control Flow
`main()` defines a string, computes `src_size`, allocates a destination using `LZ4_compressBound()`, compresses, shrinks the compressed buffer with `realloc()`, allocates a regeneration buffer of the known original size, safely decompresses, frees compressed data, verifies decompressed size and byte equality, then prints the regenerated string.

## State and Persistence
State is heap allocated and freed within the process. There are no files or external state.

## Dependencies and Integration Points
It is the basic block API teaching sample in `examples/Makefile`. It also demonstrates the important integration rule that LZ4 blocks do not carry their own original size, so callers need external metadata.

## Risks
The example assumes `realloc()` failure loses the original pointer and exits, which is acceptable for a short sample but not ideal production ownership handling. It uses a known source string; real applications must store or transmit both compressed size and decompressed bound.

## Test Signals
Successful execution prints a compression ratio, decompression success, validation success, and the original string.
<!-- END_FILE_RESEARCH: sources/compression/lz4/examples/simple_buffer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/lz4/examples/streamingHC_ringBuffer.c -->
# sources/compression/lz4/examples/streamingHC_ringBuffer.c

## Purpose
This example mirrors the ring-buffer streaming example but uses LZ4 high-compression mode for compression and normal safe streaming decode for decompression.

## Important APIs, Types, and Functions
It includes `lz4hc.h` and `lz4.h`. Compression uses `LZ4_streamHC_t` and `LZ4_compress_HC_continue()`. Decompression uses `LZ4_streamDecode_t` and `LZ4_decompress_safe_continue()`. Helpers read and write `int32_t` sizes and compare decoded output to input.

## Control Flow
`test_compress()` reads random-length chunks into a static ring buffer, compresses with the HC stream, writes size and payload, and wraps the input offset. `test_decompress()` reads each block, decodes into an intentionally larger decode buffer, writes decoded bytes, and wraps. `main()` supports an optional `-p` pause flag, compresses, decompresses, compares, and optionally waits for Enter.

## State and Persistence
The HC stream retains compression history in the ring buffer, and decode state tracks previous decoded bytes. Persistent files are `<input>.lz4s-9` and `<input>.lz4s-9.dec`.

## Dependencies and Integration Points
It is built by the examples Makefile and links against both regular and HC LZ4 APIs. The sample demonstrates that HC compression produces blocks compatible with standard LZ4 decompression.

## Risks
Like the other streaming examples, the file format is custom and host-endian. Error handling is minimal, and random chunking can vary by C library. The optional pause is interactive and unsuitable for automated runs unless omitted.

## Test Signals
`make test` expects `Verify : OK`. Useful extended tests include files that force ring-buffer wraparound and comparisons between HC and regular streaming output sizes.
<!-- END_FILE_RESEARCH: sources/compression/lz4/examples/streamingHC_ringBuffer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/lz4/lib/Makefile -->
# sources/compression/lz4/lib/Makefile

## Purpose
The library Makefile builds, installs, and uninstalls LZ4 static and shared libraries, generates pkg-config metadata, and handles platform-specific shared-library naming and Windows DLL resources.

## Important Targets and Variables
Version variables are extracted from `lz4.h` with `sed`. `BUILD_SHARED` and `BUILD_STATIC` gate library types. `SRCFILES`, `OBJFILES`, `LIBLZ4`, `LIBLZ4_EXP`, `SHARED_EXT`, `SHARED_EXT_MAJOR`, and `SHARED_EXT_VER` drive artifacts. Targets include `lib-release`, `lib`, `all`, `all32`, `liblz4.a`, `$(LIBLZ4)`, `liblz4`, `liblz4.pc`, `clean`, `install`, `uninstall`, and `listL120`.

## Control Flow
The default target is `lib-release`, which clears debug flags and builds libraries plus `liblz4.pc`. Shared library handling branches for Darwin, Windows-like environments, AIX, and POSIX. Windows builds generate `liblz4-dll.rc` from the template and compile it with `windres`; non-Windows builds use linker soname flags and symlinks. Install creates library, pkg-config, binary, and header directories and installs static/shared artifacts according to build flags.

## State and Persistence
Build outputs include objects, archives, shared libraries, symlinks, generated `.pc`, generated Windows `.rc`, import libraries, and temporary directories. Install/uninstall persist files under `DESTDIR` plus configured prefix paths.

## Dependencies and Integration Points
It includes `../build/make/lz4defs.make` and `../build/make/multiconf.make`, and relies on their platform variables and library helper macros. It integrates with pkg-config through `liblz4.pc.in` and Windows version resources through `liblz4-dll.rc.in`.

## Risks
Version extraction is duplicated with other build files and can drift if header formatting changes. The `uninstall` Windows conditional appears as `ifeq (WINBASED,yes)` rather than comparing `$(WINBASED)`, which may make that branch ineffective. Platform-specific soname and symlink behavior needs validation on each target OS.

## Test Signals
Run `make -C lib`, inspect produced static/shared artifacts and symlinks, run `make -C lib liblz4.pc`, build with `BUILD_SHARED=no` or `BUILD_STATIC=no`, and validate install paths under a temporary `DESTDIR`.
<!-- END_FILE_RESEARCH: sources/compression/lz4/lib/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/lz4/lib/dll/example/Makefile -->
# sources/compression/lz4/lib/dll/example/Makefile

## Purpose
This Makefile builds a DLL-linking example on Windows-like environments, producing one executable linked against a static import library and one linked against the DLL.

## Important Targets and Variables
`LZ4DIR`, `LIBDIR`, and `DLLDIR` point at headers, static library, and DLL locations relative to the example. `CFLAGS`, `CPPFLAGS`, and `FLAGS` define warning and include settings. Targets are `default`, `all`, `fullbench-lib`, `fullbench-dll`, and `clean`.

## Control Flow
`default` invokes `all`. `fullbench-lib` compiles `fullbench.c` and `xxhash.c` and links with `../static/liblz4_static.lib`. `fullbench-dll` compiles the same sources with `-DLZ4_DLL_IMPORT=1` and links with `../dll/liblz4.dll`. `clean` removes both executables.

## State and Persistence
The persistent outputs are `fullbench-lib(.exe)` and `fullbench-dll(.exe)`. No state files are created.

## Dependencies and Integration Points
It depends on prepared `../include`, `../static`, and `../dll` directories, plus `fullbench.c` and `xxhash.c` in the example directory. `LZ4_DLL_IMPORT=1` integrates with `lz4.h`'s Windows import declaration behavior.

## Risks
The `clean` command has a trailing backslash before the echo line, which can fold commands in unintended ways. Linking directly to `liblz4.dll` may depend on toolchain conventions; many Windows builds link against an import library instead. Relative directory assumptions are strict.

## Test Signals
Build both targets and run them with the DLL present on the runtime search path. Confirm the DLL build imports LZ4 symbols and the static build runs without the DLL dependency.
<!-- END_FILE_RESEARCH: sources/compression/lz4/lib/dll/example/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/lz4/lib/liblz4-dll.rc.in -->
# sources/compression/lz4/lib/liblz4-dll.rc.in

## Purpose
This Windows resource template embeds version and product metadata into the LZ4 DLL.

## Important Fields
The template includes `<windows.h>` and defines a `VERSIONINFO` block. Placeholders `@LIBVER_MAJOR@`, `@LIBVER_MINOR@`, `@LIBVER_PATCH@`, and `@LIBLZ4@` populate `FILEVERSION`, `PRODUCTVERSION`, `FileVersion`, `InternalName`, `OriginalFilename`, and `ProductVersion`. String metadata includes company, description, copyright, product name, and translation.

## Control Flow
It is not executed directly. `lib/Makefile` replaces placeholders with `sed` to create `liblz4-dll.rc`, then compiles that resource to `liblz4-dll.o` with `windres` for inclusion in the DLL link.

## State and Persistence
The template is source state. Generated persistent artifacts are the substituted `.rc` file and compiled resource object during Windows builds.

## Dependencies and Integration Points
It depends on Windows resource compiler syntax and Makefile substitution. It integrates with DLL metadata visible in Windows file properties and installers.

## Risks
Metadata can drift if copyright years, company naming, or product descriptions change. Placeholder substitution must replace all values; unresolved placeholders would ship visibly in DLL metadata.

## Test Signals
On a Windows build, inspect generated `liblz4-dll.rc`, verify `windres` succeeds, and check the built DLL's version resource with a resource viewer or file properties.
<!-- END_FILE_RESEARCH: sources/compression/lz4/lib/liblz4-dll.rc.in -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/lz4/lib/liblz4.pc.in -->
# sources/compression/lz4/lib/liblz4.pc.in

## Purpose
This pkg-config template describes how downstream builds should compile and link against installed `liblz4`.

## Important Fields
Template variables are `@PREFIX@`, `@LIBDIR@`, `@INCLUDEDIR@`, and `@VERSION@`. The generated file exposes `Name: lz4`, description, project URL, `License: BSD-2-Clause`, `Version`, `Libs: -L${libdir} -llz4`, and `Cflags: -I${includedir}`.

## Control Flow
`lib/Makefile` substitutes paths and version, including a pass to preserve `${prefix}` variable references in generated path values. The generated `liblz4.pc` is installed under the configured pkg-config directory.

## State and Persistence
The template itself has no runtime state. The generated `.pc` file becomes installed build metadata for downstream projects.

## Dependencies and Integration Points
It integrates with `pkg-config`, distribution packaging, and `make install`. It depends on the library actually being installed in the substituted `libdir` and headers in `includedir`.

## Risks
Incorrect prefix/libdir substitution breaks downstream discovery. The template does not include private libraries, which is fine for current LZ4 but would need review if link dependencies are added.

## Test Signals
After `make install DESTDIR=<tmp>`, run `pkg-config --cflags --libs` against the generated file with `PKG_CONFIG_PATH` pointed at the temporary pkgconfig directory.
<!-- END_FILE_RESEARCH: sources/compression/lz4/lib/liblz4.pc.in -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/lz4/lib/lz4.c -->
# sources/compression/lz4/lib/lz4.c

## Purpose
`lz4.c` is the core LZ4 block codec implementation. It provides the public block compression/decompression ABI declared by `lz4.h`, streaming compression/decompression state management, dictionary support, low-level portability helpers, and deprecated compatibility wrappers.

## Important APIs, Types, and Functions
Public entry points include version helpers (`LZ4_versionNumber()`, `LZ4_versionString()`), sizing (`LZ4_compressBound()`, `LZ4_sizeofState()`), one-shot compression (`LZ4_compress_default()`, `LZ4_compress_fast()`, `LZ4_compress_fast_extState()`), destination-size compression (`LZ4_compress_destSize*()`), stream lifecycle (`LZ4_createStream()`, `LZ4_initStream()`, `LZ4_resetStream()`, `LZ4_resetStream_fast()`, `LZ4_freeStream()`), dictionary APIs (`LZ4_loadDict()`, `LZ4_loadDictSlow()`, `LZ4_attach_dictionary()`, `LZ4_saveDict()`), streaming compression (`LZ4_compress_fast_continue()`), safe decompression (`LZ4_decompress_safe()`, `LZ4_decompress_safe_partial()`), streaming decode (`LZ4_createStreamDecode()`, `LZ4_setStreamDecode()`, `LZ4_decoderRingBufferSize()`, `LZ4_decompress_safe_continue()`), explicit dictionary decode (`LZ4_decompress_safe_usingDict()`, `LZ4_decompress_safe_partial_usingDict()`), and deprecated fast/obsolete wrappers.

Internal types include byte/int aliases (`BYTE`, `U16`, `U32`, `S32`, `U64`, `reg_t`), `limitedOutput_directive`, `tableType_t`, `dict_directive`, `dictIssue_directive`, and `earlyEnd_directive`. Core helpers include endian-safe readers/writers, `LZ4_wildCopy*()`, `LZ4_memcpy_using_offset*()`, `LZ4_NbCommonBytes()`, `LZ4_count()`, hash table helpers, `LZ4_prepareTable()`, `LZ4_compress_generic_validated()`, `LZ4_compress_generic()`, `LZ4_decompress_unsafe_generic()`, `read_variable_length()`, and `LZ4_decompress_generic()`.

## Control Flow
Compression wrappers normalize acceleration, choose a hash table mode (`byU16` for small inputs, `byU32` or `byPtr` for larger/address-sensitive cases), choose output mode (`notLimited`, `limitedOutput`, or `fillOutput`), then call `LZ4_compress_generic()`. The validated compressor updates stream offsets/dictionary metadata, hashes candidate positions, skips faster through incompressible regions according to acceleration, catches up to extend matches backward, emits literal length, literals, 16-bit offset, and match length, then emits final literals. Streaming compression either uses contiguous prefix history, an external dictionary, or an attached dictionary context; it renormalizes offsets when they approach 32-bit overflow.

Decompression wrappers instantiate `LZ4_decompress_generic()` with full or partial decode and with no dictionary, prefix dictionary, or external dictionary. The safe decoder reads tokens, expands variable-length literal and match lengths with bounds checks, copies literals, validates offsets when dictionaries are smaller than 64 KiB, handles external-dictionary matches that may span into the current output prefix, and enforces LZ4 block end restrictions. A fast decode loop is enabled on x86/x64/aarch64 when enough output space remains; otherwise the safe loop handles boundary cases. Deprecated `LZ4_decompress_fast*()` calls use `LZ4_decompress_unsafe_generic()`, which trusts input size less and is retained for compatibility.

## State and Persistence
There is no filesystem persistence. Compression state lives in `LZ4_stream_t_internal`: hash table, table type, current offset, dictionary pointer/size, and optional attached dictionary context. Decode state lives in `LZ4_streamDecode_t_internal`: prefix end/size, external dictionary pointer, and external dictionary size. Dictionary windows are capped to the LZ4 64 KiB distance limit, and callers must keep referenced dictionary or prefix memory alive unless they call `LZ4_saveDict()`.

## Dependencies and Integration Points
The file includes `lz4.h` with `LZ4_STATIC_LINKING_ONLY` enabled internally. It uses compile-time switches for heap mode, freestanding builds, custom memory functions, memory access strategy, endian-independent output, debug logging, and CPU/compiler-specific optimization. It integrates with `lz4hc`, `lz4frame`, examples, CLI tools, shared-library builds, and downstream applications through the stable C ABI.

## Risks
The code is highly optimized and relies on exact block-format invariants: last literals, match start distance from end, 16-bit offsets, and permitted wild-copy overrun within guarded zones. Incorrect wrapper parameters, stale dictionary memory, undersized ring buffers, or use of deprecated fast decompression on untrusted input can cause failures or security exposure. Compile-time memory access modes can trade portability for speed; `LZ4_FORCE_MEMORY_ACCESS=2` intentionally violates strict C aliasing/alignment assumptions on some targets. Stream fast-reset APIs require correctly initialized state.

## Test Signals
Important tests are one-shot round trips over empty, tiny, incompressible, highly compressible, and maximum-size-adjacent inputs; limited-output failure behavior; destination-size consumed-byte behavior; streaming prefix/ext-dict/attached-dict round trips; ring-buffer wraparound; partial decompression; malformed-block rejection by safe decoders; deprecated compatibility wrappers; big-endian or endian-independent builds; freestanding/custom allocator builds; and sanitizer/fuzzer runs against decompression.
<!-- END_FILE_RESEARCH: sources/compression/lz4/lib/lz4.c -->
