# Research Report: subset-b-000287

This grouped report covers the XZ Utils files assigned to `subset-b-000287`. Each source file has a separate delimited section for deterministic reconciliation into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/configure.ac -->
# sources/compression/xz/configure.ac

Purpose: Autoconf input for the XZ Utils build. It establishes package identity/versioning, canonical host detection, configure-time feature switches, generated `config.h` macros, Automake conditionals, Libtool setup, gettext setup, platform probes, and generated makefiles/scripts.

Important APIs/types/functions: the public surface is the generated `configure` options such as `--enable-encoders`, `--enable-decoders`, `--enable-match-finders`, `--enable-checks`, `--enable-threads`, `--enable-sandbox`, `--enable-small`, `--enable-symbol-versions`, and component toggles for `xz`, `xzdec`, `lzmadec`, `lzmainfo`, scripts, docs, and Doxygen. It defines `HAVE_ENCODER_*`, `HAVE_DECODER_*`, `HAVE_CHECK_*`, `MYTHREAD_*`, `HAVE_*CRC*`, `HAVE_LINUX_LANDLOCK`, `ASSUME_RAM`, and symbol-versioning macros.

Control flow: the script first normalizes host/Windows behavior, validates requested filters and checks, enforces LZMA2 requiring LZMA1, validates match-finder availability for LZ encoders, selects threading, components, sandboxing, POSIX shell and compiler, then runs feature probes for headers, typedefs, functions, CRC intrinsics, external SHA-256, Landlock/Capsicum/Pledge, gettext, visibility, warnings, and Libtool symbol versioning before emitting all configured files.

State and persistence: generated state is persisted in `config.h`, makefiles, script substitutions, `AM_CFLAGS`, `LIBS`, `LTLIBINTL`, conditional Automake variables, and substituted executable names. No runtime state is kept by this file.

Dependencies and integration: depends on Autoconf, Automake, Libtool, gnulib macros, gettext macros, `build-aux/version.sh`, tuklib feature macros, platform headers, compiler/linker probes, and downstream makefiles in `lib`, `src`, `tests`, and `debug`.

Risks: invalid option combinations are blocked, but the file is a high-blast-radius integration point: a missed macro affects many C translation units. Symbol versioning has Linux/PIC/static-library caveats. Landlock rejects sanitizer builds. Feature-disabled liblzma builds can break examples/tools expecting filters/checks. The warning flag loop depends on `-Werror` probes being clean.

Test signals: confidence comes from successful `autoreconf`/`configure`, generated `config.h`, `make`, platform CI, and feature-specific builds that exercise disabled filters, threading variants, sandbox choices, and CRC intrinsic paths.
<!-- END_FILE_RESEARCH: sources/compression/xz/configure.ac -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/debug/Makefile.am -->
# sources/compression/xz/debug/Makefile.am

Purpose: Automake recipe for non-installed debug helper programs in `debug/`.

Important APIs/types/functions: declares `noinst_PROGRAMS` for `repeat`, `sync_flush`, `full_flush`, `memusage`, `crc32`, `known_sizes`, `hex2bin`, and `testfilegen-arm64`; sets include paths for `src/common` and liblzma API headers; links against `src/liblzma/liblzma.la`, optional `lib/libgnu.a`, and `$(LTLIBINTL)`.

Control flow: Automake builds each listed helper from same-named sources, applies `AM_CPPFLAGS`, and conditionally appends gnulib support when `COND_GNULIB` is true.

State and persistence: no runtime state; persisted build outputs are local, non-installed helper executables.

Dependencies and integration: integrates with top-level `configure.ac` conditionals, liblzma, common headers, gnulib replacement objects, and gettext/linker flags.

Risks: debug helpers are linked against current build-tree liblzma, so stale builds or missing optional gnulib objects can cause misleading failures. They are intentionally not installed, so packaging should not rely on them.

Test signals: `make -C debug` should produce all helpers; link failures indicate broken liblzma or replacement-function configuration.
<!-- END_FILE_RESEARCH: sources/compression/xz/debug/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/debug/crc32.c -->
# sources/compression/xz/debug/crc32.c

Purpose: tiny stdin-to-stdout tool that computes liblzma CRC32 over input and prints the resulting value as four little-endian hex bytes.

Important APIs/types/functions: `main` reads `stdin` in `BUFSIZ` chunks and calls `lzma_crc32(buf, size, crc)`. It uses `uint32_t`, `uint8_t`, `PRIX32`, and stdio.

Control flow: initialize CRC to zero, repeatedly `fread`, update CRC even for the last partial read, stop on EOF or read error, then print low-to-high bytes.

State and persistence: state is process-local CRC accumulator and buffer; no files are opened beyond standard streams.

Dependencies and integration: includes `sysdefs.h` for portability and `lzma.h` for CRC API. Used as an ad hoc debugging/test utility for expected CRC values.

Risks: read errors only stop the loop; they do not change the exit status or report diagnostics. Output is not the conventional big-endian CRC string, intentionally favoring hex-editor workflows.

Test signals: compare output against `xz --check=crc32` metadata or an independent CRC32 implementation; pipe known byte sequences through the tool.
<!-- END_FILE_RESEARCH: sources/compression/xz/debug/crc32.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/debug/full_flush.c -->
# sources/compression/xz/debug/full_flush.c

Purpose: debug encoder that creates an `.xz` stream while issuing multiple `LZMA_FULL_FLUSH` actions around fixed-size input chunks.

Important APIs/types/functions: global `lzma_stream strm`, `FILE *file_in`, helper `encode(size_t size, lzma_action action)`, `lzma_lzma_preset`, `lzma_stream_encoder`, `lzma_code`, and `lzma_end`.

Control flow: `main` opens an optional input file, builds an LZMA2+CRC32 stream encoder using preset 1, then calls `encode` with zero-length and small chunk sizes followed by `LZMA_FINISH`. `encode` refills input while `size > 0`, runs `lzma_code` with `LZMA_RUN` until chunk completion, flushes generated output, and asserts expected return codes.

State and persistence: stream state persists globally across multiple flush calls; output is written to stdout. No durable state is stored.

Dependencies and integration: depends on liblzma streaming encoder and `sysdefs.h` `my_min`.

Risks: `fopen` is not checked for failure. `size` is decremented by requested bytes rather than `fread` bytes, intentionally testing stream behavior but fragile on short reads. Write errors are ignored.

Test signals: resulting stream should decompress successfully and preserve input prefix covered by requested chunks; useful for regression checks around `LZMA_FULL_FLUSH`.
<!-- END_FILE_RESEARCH: sources/compression/xz/debug/full_flush.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/debug/hex2bin.c -->
# sources/compression/xz/debug/hex2bin.c

Purpose: command-line converter from textual hexadecimal pairs to raw binary bytes.

Important APIs/types/functions: `getbin(int)` maps ASCII hex digits to nibble values; `main` loops over `getchar`, `isxdigit`, `putchar`, and reports invalid odd/incomplete hex pairs.

Control flow: non-hex characters are skipped until a first hex digit is found. The next character must also be hex; the two nibbles are combined and emitted. EOF after non-hex separators exits successfully.

State and persistence: stateless streaming filter over stdin/stdout.

Dependencies and integration: depends on `sysdefs.h`, stdio, and ctype. It complements debug tools that print or consume byte-oriented test vectors.

Risks: `getbin` assumes callers passed hex digits; it treats any non-digit/non-uppercase input as lowercase hex. `putchar` errors are reported, but read errors are not distinguished from EOF.

Test signals: round trip known strings such as `00 ff 5D` to binary and inspect with `od`; malformed single trailing hex digit should return failure.
<!-- END_FILE_RESEARCH: sources/compression/xz/debug/hex2bin.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/debug/known_sizes.c -->
# sources/compression/xz/debug/known_sizes.c

Purpose: debug encoder that manually constructs an `.xz` stream whose block header records known compressed and uncompressed sizes.

Important APIs/types/functions: uses `lzma_lzma_preset`, `lzma_block`, `lzma_block_encoder`, `lzma_block_header_size`, `lzma_block_header_encode`, `lzma_index_init`, `lzma_index_append`, `lzma_index_encoder`, `lzma_stream_header_encode`, and `lzma_stream_footer_encode`.

Control flow: read up to 1 MiB of stdin into memory, encode a single LZMA2 block into an output buffer, backfill the block header, build and encode an index, synthesize stream flags/header/footer, then write the complete stream.

State and persistence: all encoding buffers and liblzma structures are process-local; output is emitted to stdout only.

Dependencies and integration: exercises lower-level block/index/container APIs instead of the high-level stream encoder.

Risks: output buffer is also 1 MiB and the comment admits overflow is possible for poorly compressible input near the limit. Many errors return `1` without diagnostics. It does not check `fread`/`fwrite` errors.

Test signals: generated output should pass `xz -t` and `xz --list` should show known block sizes; inputs close to the buffer limit are useful negative tests.
<!-- END_FILE_RESEARCH: sources/compression/xz/debug/known_sizes.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/debug/memusage.c -->
# sources/compression/xz/debug/memusage.c

Purpose: prints encoder and decoder memory usage for a hard-coded raw LZMA1 filter chain.

Important APIs/types/functions: initializes `lzma_options_lzma`, builds a `lzma_filter` array, calls `lzma_raw_encoder_memusage` and `lzma_raw_decoder_memusage`.

Control flow: no input processing; `main` constructs options with a 1.5 GiB dictionary and BT4 match finder, queries memory usage, prints byte counts, and exits.

State and persistence: no persistent state.

Dependencies and integration: depends on liblzma raw-filter memory accounting. It is a debug probe for memory limit and option validation behavior.

Risks: hard-coded extreme dictionary size may return values not representative of normal presets. It does not check for `UINT64_MAX` error returns from memory-usage APIs.

Test signals: compare printed values to expected memory formulae or regressions when liblzma memory accounting changes.
<!-- END_FILE_RESEARCH: sources/compression/xz/debug/memusage.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/debug/repeat.c -->
# sources/compression/xz/debug/repeat.c

Purpose: emits a user-provided string repeatedly, originally useful for stress testing run-length/subblock behavior.

Important APIs/types/functions: `main` parses `COUNT` with `strtoull`, measures `STRING` with `strlen`, writes it with `fwrite`, and checks output stream errors at exit.

Control flow: validate exactly two arguments, convert count, loop until count reaches zero, writing the byte sequence each time.

State and persistence: no persistent state; output is stdout.

Dependencies and integration: only common portability includes and stdio/string conversion.

Risks: invalid numeric text is accepted as zero or partial conversion because `strtoull` end pointer and overflow are ignored. Very large counts can produce unbounded output.

Test signals: run with small counts and compare byte-for-byte output; simulate closed stdout to verify nonzero exit.
<!-- END_FILE_RESEARCH: sources/compression/xz/debug/repeat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/debug/sync_flush.c -->
# sources/compression/xz/debug/sync_flush.c

Purpose: debug encoder that emits a stream using repeated `LZMA_SYNC_FLUSH` operations, with commented code for testing filter updates.

Important APIs/types/functions: same structure as `full_flush.c`, but uses explicit `lzma_options_lzma`, optional `lzma_options_delta`, `lzma_stream_encoder`, `lzma_code`, and possible `lzma_filters_update`.

Control flow: configure LZMA2 with a 64 KiB dictionary and HC3 match finder, initialize stream encoder, perform zero/small-size sync flushes, then finish. `encode` handles chunked reads, output draining, and return-code checks.

State and persistence: persistent global `lzma_stream` across flush calls; stdout contains the encoded stream.

Dependencies and integration: targets liblzma streaming behavior around sync flush and filter boundary handling.

Risks: optional input `fopen` is unchecked, write errors are ignored, and short reads are not treated as errors. The unused delta options exist only to silence warning-sensitive builds.

Test signals: generated output should decompress successfully; modifying the commented filter-update block can probe dynamic filter update regressions.
<!-- END_FILE_RESEARCH: sources/compression/xz/debug/sync_flush.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/debug/testfilegen-arm64.c -->
# sources/compression/xz/debug/testfilegen-arm64.c

Purpose: generates raw ARM64 instruction bytes for testing the ARM64 BCJ filter.

Important APIs/types/functions: `put32le` writes little-endian words and advances pseudo-PC `pc4`; `putbl` emits branch-link encodings; `putadrp32` emits ADRP-like encodings with varied immediate/register bits.

Control flow: `main` emits boundary BL immediates, PC-relative negative cases, ADRP test cases, then page-aligns and iterates immediate sizes to cover positive and negative ADRP ranges.

State and persistence: only process-local `pc4`; generated binary test data is written to stdout.

Dependencies and integration: standalone C using stdint/stdbool/stdio. Its output feeds filter tests or manual compression/decompression comparisons.

Risks: no output error handling. Encodings are handcrafted and tightly coupled to ARM64 filter recognition rules; a rule change may require updated vectors.

Test signals: compress/decompress through ARM64 filter and compare to original; inspect generated instruction distribution around immediate and page-boundary edges.
<!-- END_FILE_RESEARCH: sources/compression/xz/debug/testfilegen-arm64.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/debug/translation.bash -->
# sources/compression/xz/debug/translation.bash

Purpose: helper script for translators to view representative translated `xz` output.

Important APIs/types/functions: resolves an `xz` executable, prints version/source/locale, switches to `tests/files`, puts xz in `PATH`, then evaluates a fixed list of commands covering errors, memory-limit output, help, filters help, verbose mode, and list tables.

Control flow: starts with `set -e` for setup validation, accepts optional executable path, locates top source directory relative to the script, then switches to `set +e` because many test commands intentionally fail.

State and persistence: no persistent repo state; only stdout/stderr diagnostics.

Dependencies and integration: depends on bash, built `xz`, `locale`, optional git, and sample test files. Integrates with translation QA rather than automated tests.

Risks: uses `eval` over hard-coded command strings; safe in current form but fragile if user-provided commands were ever added. Requires being run from a source tree with `tests/files`.

Test signals: translators inspect output manually, often with `less -S`; missing/misaligned translations or malformed tables are the main signal.
<!-- END_FILE_RESEARCH: sources/compression/xz/debug/translation.bash -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/doc/examples/01_compress_easy.c -->
# sources/compression/xz/doc/examples/01_compress_easy.c

Purpose: documented sample showing multi-call `.xz` compression from stdin to stdout with `lzma_easy_encoder`.

Important APIs/types/functions: `get_preset`, `init_encoder`, `compress`, `lzma_stream`, `LZMA_STREAM_INIT`, `lzma_easy_encoder`, `lzma_code`, `LZMA_RUN`, `LZMA_FINISH`, and `lzma_end`.

Control flow: parse preset `0-9` plus optional `e`, initialize CRC64 preset encoder, loop reading input and calling `lzma_code`, flush output when the output buffer fills or stream ends, handle liblzma errors explicitly, then close stdout.

State and persistence: one `lzma_stream` holds encoder state; stdin/stdout are the only data channels.

Dependencies and integration: primary public API example for applications embedding liblzma.

Risks: intended as sample code, not a full CLI. It is careful with read/write errors, but uses stdio buffering and single-threaded flow only.

Test signals: compile with `-llzma`, compress a file, and validate with `xz -t` or decompression comparison.
<!-- END_FILE_RESEARCH: sources/compression/xz/doc/examples/01_compress_easy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/doc/examples/02_decompress.c -->
# sources/compression/xz/doc/examples/02_decompress.c

Purpose: documented sample for decompressing one or more `.xz` files to stdout.

Important APIs/types/functions: `init_decoder`, `decompress`, `lzma_stream_decoder`, `LZMA_CONCATENATED`, `lzma_code`, `LZMA_FINISH`, and error handling for `LZMA_FORMAT_ERROR`, `OPTIONS_ERROR`, `DATA_ERROR`, and `BUF_ERROR`.

Control flow: loop over filename arguments, reinitialize the decoder for each file using the same stream object, read file data, call `lzma_code`, write decompressed output, and report per-file errors while continuing to later files when possible.

State and persistence: decoder state is reused across files and freed once at the end; output concatenates decompressed inputs.

Dependencies and integration: demonstrates the recommended `LZMA_CONCATENATED` flag for normal `.xz` files.

Risks: memory limit is `UINT64_MAX`, so malicious inputs can request large decoder memory. It targets clarity over sandboxing or robust CLI behavior.

Test signals: run on valid, concatenated, corrupt, truncated, and non-xz files and check diagnostics/exit status.
<!-- END_FILE_RESEARCH: sources/compression/xz/doc/examples/02_decompress.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/doc/examples/03_compress_custom.c -->
# sources/compression/xz/doc/examples/03_compress_custom.c

Purpose: documented sample for building a custom filter chain with x86 BCJ followed by LZMA2.

Important APIs/types/functions: `init_encoder`, `lzma_lzma_preset`, `lzma_filter`, `LZMA_FILTER_X86`, `LZMA_FILTER_LZMA2`, `lzma_stream_encoder`, and the same multi-call `compress` loop as the easy example.

Control flow: initialize LZMA2 options from default preset, build a terminated filter array, create a CRC64 stream encoder, then stream stdin to stdout with `lzma_code`.

State and persistence: encoder state lives in `lzma_stream`; output is stdout.

Dependencies and integration: teaches liblzma filter-chain API and BCJ/LZMA2 ordering. Depends on builds that include both filters.

Risks: compression benefits only for x86 executable-like input. `LZMA_OPTIONS_ERROR` can occur in feature-reduced liblzma builds.

Test signals: compile and compress sample x86 binaries/plain text, validate stream with `xz -t`, and compare compression ratios to easy mode.
<!-- END_FILE_RESEARCH: sources/compression/xz/doc/examples/03_compress_custom.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/doc/examples/04_compress_easy_mt.c -->
# sources/compression/xz/doc/examples/04_compress_easy_mt.c

Purpose: documented sample for multi-threaded `.xz` compression using preset-based LZMA2.

Important APIs/types/functions: `lzma_mt`, `lzma_cputhreads`, `lzma_stream_encoder_mt`, `preset`, `threads`, `block_size`, `timeout`, `check`, and the shared streaming `compress` loop.

Control flow: configure threaded encoder defaults, detect CPU threads, fall back to one thread when unknown, cap at eight threads, initialize the MT encoder, then stream stdin to stdout.

State and persistence: liblzma owns worker/block state behind `lzma_stream`; no persistent files beyond stdout.

Dependencies and integration: depends on liblzma built with threading and the CPU thread detection path.

Risks: one-thread MT mode is not equivalent to normal single-threaded mode and can use more memory. The arbitrary thread cap may be wrong for some RAM/preset combinations.

Test signals: compile against threaded liblzma, compress/decompress large files, and test builds without thread support for expected initialization failure.
<!-- END_FILE_RESEARCH: sources/compression/xz/doc/examples/04_compress_easy_mt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/doc/examples/11_file_info.c -->
# sources/compression/xz/doc/examples/11_file_info.c

Purpose: documented sample for reading `.xz` index information and printing uncompressed sizes without full decompression.

Important APIs/types/functions: `print_file_size`, `lzma_file_info_decoder`, `lzma_code`, `LZMA_SEEK_NEEDED`, `strm->seek_pos`, `lzma_index_uncompressed_size`, and `lzma_index_end`.

Control flow: determine input file size with `fseek`/`ftell`, initialize file-info decoder, feed buffers until liblzma asks for seeks or returns stream end, then print decoded uncompressed size and filename.

State and persistence: stream object is reused across files; `lzma_index` is allocated per successful file and freed after reporting.

Dependencies and integration: demonstrates the random-access file-info decoder and caller-managed seeking.

Risks: if `fopen` fails, `main` still calls `print_file_size` with `NULL`, which would crash; sample code needs a `continue`. `ftell`/`long` is not large-file-safe on 32-bit systems, as the comments note.

Test signals: run on valid multi-stream `.xz`, corrupt headers, unsupported options, and failed open paths; validate reported size against `xz --list`.
<!-- END_FILE_RESEARCH: sources/compression/xz/doc/examples/11_file_info.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/doc/examples/Makefile -->
# sources/compression/xz/doc/examples/Makefile

Purpose: simple standalone makefile for compiling the documented liblzma examples outside the Autotools build.

Important APIs/types/functions: variables `CC=c99`, `CFLAGS=-g`, `LDFLAGS=-llzma`, `PROGS`, pattern rule `.c:`, and `clean`.

Control flow: `all` builds the five example programs by compiling each source file directly with the configured compiler and linker flags.

State and persistence: persists local executable outputs and removes them in `clean`.

Dependencies and integration: assumes an installed liblzma and C99 compiler are available in normal system paths.

Risks: not tied to build-tree headers/libraries, so it may compile against a different liblzma than the source checkout. No dependency tracking or platform-specific flags.

Test signals: `make`, then run each example on small sample inputs and validate generated `.xz` streams or file-info output.
<!-- END_FILE_RESEARCH: sources/compression/xz/doc/examples/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/dos/Makefile -->
# sources/compression/xz/dos/Makefile

Purpose: hand-written DJGPP makefile to build `xz.exe` for DOS without the Autotools generated build.

Important APIs/types/functions: defines compiler/link flags, large `SRCS_C` source list covering getopt, tuklib, liblzma, and xz frontend, assembler CRC sources, object derivation, generated `getopt.h`, and final `xz.exe` recipe with `exe2coff`/CWSDPMI stub.

Control flow: build all C/assembly objects with include paths and `HAVE_CONFIG_H`, link them into `xz.exe`, strip, convert to COFF, prepend DPMI stub, and clean intermediate executable forms.

State and persistence: persists objects in source-adjacent paths and final DOS executable.

Dependencies and integration: depends on DJGPP, DOS commands (`del`, `copy`), `update`, `exe2coff`, `CWSDSTUB.EXE`, and curated source list consistency.

Risks: source list must be manually kept in sync with liblzma/xz changes. Object outputs live outside `dos/`, increasing cleanup risk. It hard-codes full feature selection via `dos/config.h`.

Test signals: build under DJGPP, run `xz.exe --version`, compress/decompress fixtures, and verify x86 assembly CRC linkage.
<!-- END_FILE_RESEARCH: sources/compression/xz/dos/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/dos/config.h -->
# sources/compression/xz/dos/config.h

Purpose: static configuration header for DJGPP/DOS builds.

Important APIs/types/functions: defines `ASSUME_RAM`, enabled checks, all listed encoders/decoders, LZMA match finders, x86 CRC assembly, lzip decoder, C headers/types, `NDEBUG`, package metadata, `SIZEOF_SIZE_T`, visibility, builtin byte-swap/alignment support, and fast unaligned access.

Control flow: no execution; preprocessor macros drive conditional compilation across liblzma, tuklib, getopt, and xz.

State and persistence: compile-time state only.

Dependencies and integration: consumed when `HAVE_CONFIG_H` is set by `dos/Makefile`.

Risks: diverges from Autoconf probes and must match DJGPP reality manually. Missing macros for newer features can silently disable code paths; incorrect macros can cause portability bugs.

Test signals: successful DOS build plus runtime compression/decompression tests; preprocessor inspection can verify expected feature gates.
<!-- END_FILE_RESEARCH: sources/compression/xz/dos/config.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/doxygen/update-doxygen -->
# sources/compression/xz/doxygen/update-doxygen

Purpose: wrapper script for generating versioned Doxygen HTML documentation for liblzma API or XZ Utils internals.

Important APIs/types/functions: `show_usage`, modes `api` and `internal`, optional absolute source/output directories, `build-aux/version.sh`, `doxygen -q -`, and appended Doxyfile overrides.

Control flow: validate mode and doxygen availability, resolve in-tree or out-of-tree paths, check Doxyfile/output directory, compute package version, remove old target docs, pipe base Doxyfile plus mode-specific overrides into Doxygen.

State and persistence: deletes and recreates `doc/api` or `doc/internal` under the chosen output directory.

Dependencies and integration: depends on `/bin/sh`, Doxygen, source-tree layout, and `build-aux/version.sh`. Called by documentation build workflows.

Risks: uses `rm -rf` on computed output subdirectories; path validation limits but does not eliminate operator mistakes. Output directory must preexist.

Test signals: run `update-doxygen api` and `internal`, verify generated HTML contains current package version and correct input scope.
<!-- END_FILE_RESEARCH: sources/compression/xz/doxygen/update-doxygen -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/extra/7z2lzma/7z2lzma.bash -->
# sources/compression/xz/extra/7z2lzma/7z2lzma.bash

Purpose: primitive converter from a simple `.7z` archive containing one default-parameter LZMA stream to legacy `.lzma` format.

Important APIs/types/functions: bash `int2bin` writes little-endian integers; `7za l -slt` extracts metadata; `sed` parses packed size, uncompressed size, and dictionary; `dd` copies compressed payload after a 32-byte archive header.

Control flow: validate two arguments, enable `pipefail`, collect 7z metadata, reject multiple blocks, parse sizes/method, write `.lzma` properties/dictionary/uncompressed-size header, then append compressed bytes from the archive.

State and persistence: writes the output file incrementally and may leave a corrupt/partial file on failure.

Dependencies and integration: depends on bash, GNU-ish tools, `7za`/p7zip, and assumptions about 7z layout.

Risks: explicitly does not verify CRC32 and assumes default lc/lp/pb. Archive parsing and fixed 32-byte skip are fragile; success does not guarantee valid output.

Test signals: decompress original `.7z` and generated `.lzma`, compare raw output byte-for-byte, and test rejection of multi-block archives.
<!-- END_FILE_RESEARCH: sources/compression/xz/extra/7z2lzma/7z2lzma.bash -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/extra/scanlzma/scanlzma.c -->
# sources/compression/xz/extra/scanlzma/scanlzma.c

Purpose: scans stdin for a legacy LZMA-alone header and emits the selected embedded stream to stdout.

Important APIs/types/functions: `find_lzma_header` checks property byte, dictionary-size byte constraints, and unknown-size/zero-size patterns; `main` parses stream index, scans 4096-byte blocks, writes from match offset, then copies the rest of stdin.

Control flow: require `numlzma` argument, read full blocks with `fread`, inspect offsets up to `BUFSIZE - 23`, decrement requested match count until target, then stream remaining bytes.

State and persistence: no persistent state; output is stdout.

Dependencies and integration: standalone GPL utility for firmware/recovery workflows, intended to pipe into `lzma -d`.

Risks: block-boundary matches can be missed because scanning does not overlap buffers. Header heuristic is narrow (`0x5d`) and can false-positive/false-negative. It returns failure if no target stream is found.

Test signals: run on firmware fixtures with known embedded LZMA offsets; compare extracted decompressed content to expected strings/files.
<!-- END_FILE_RESEARCH: sources/compression/xz/extra/scanlzma/scanlzma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/lib/Makefile.am -->
# sources/compression/xz/lib/Makefile.am

Purpose: Automake recipe for the small bundled gnulib replacement library.

Important APIs/types/functions: declares `noinst_LIBRARIES = libgnu.a`, uses `$(LIBOBJS)` as dependencies/additions, distributes getopt implementation/header fragments, and generates `getopt.h` from `getopt.in.h`.

Control flow: if `configure` determines replacement objects are needed, Automake builds `libgnu.a`; `getopt.h` is generated by prefixing a do-not-edit comment to the template and atomically moving it into place.

State and persistence: generated `getopt.h`, temporary `getopt.h-t`, and static archive in the build tree.

Dependencies and integration: controlled by `COND_GNULIB` and `gl_GETOPT`; linked into debug/tools when replacement getopt is required.

Risks: project intentionally avoids full `gnulib-tool`, so imports must be updated manually. Header generation assumes build directory include ordering finds generated `getopt.h`.

Test signals: configure on a platform lacking `getopt_long`, then build and run xz option parsing tests.
<!-- END_FILE_RESEARCH: sources/compression/xz/lib/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/lib/getopt-cdefs.h -->
# sources/compression/xz/lib/getopt-cdefs.h

Purpose: compatibility shim providing glibc-style cdefs macros expected by shared getopt headers.

Important APIs/types/functions: defines `__BEGIN_DECLS`, `__END_DECLS`, `__GNUC_PREREQ`, and `__THROW`, optionally including `<sys/cdefs.h>`.

Control flow: preprocessor-only; each macro is defined only if absent.

State and persistence: compile-time declarations only.

Dependencies and integration: included by `getopt.in.h` before `getopt-core.h` and `getopt-ext.h`.

Risks: feature detection uses compiler macros and must remain compatible with C and C++. Incorrect exception macro handling can alter C++ prototypes.

Test signals: compile getopt users as C and C++ on non-glibc systems, including MSVC/Clang/GCC variants.
<!-- END_FILE_RESEARCH: sources/compression/xz/lib/getopt-cdefs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/lib/getopt-core.h -->
# sources/compression/xz/lib/getopt-core.h

Purpose: public declarations for basic portable `getopt` state and function.

Important APIs/types/functions: declares globals `optarg`, `optind`, `opterr`, `optopt`, and `getopt(int, char *const *, const char *)`.

Control flow: header-only declarations documenting short-option parsing behavior, optional arguments, `--`, permutation, `+`, `-`, and `POSIXLY_CORRECT`.

State and persistence: exposes process-global parser state through standard getopt globals.

Dependencies and integration: included through generated `getopt.h`; used by xz argument parsing when system getopt is missing/replaced.

Risks: prototypes use standards-compatible `char *const *` even though permutation requires a writable argv array. Global state is not thread-safe.

Test signals: run short-option parsing tests including missing arguments, non-option ordering, and reset via `optind`.
<!-- END_FILE_RESEARCH: sources/compression/xz/lib/getopt-core.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/lib/getopt-ext.h -->
# sources/compression/xz/lib/getopt-ext.h

Purpose: public declarations for GNU long-option extensions.

Important APIs/types/functions: defines `struct option`, `no_argument`, `required_argument`, `optional_argument`, `getopt_long`, and `getopt_long_only`.

Control flow: header-only; callers pass a null-terminated long-option table and optional returned index.

State and persistence: uses the same global getopt state as core parsing.

Dependencies and integration: included through `getopt-pfx-ext.h` and `getopt.h`; backs xz's long CLI options.

Risks: `has_arg` remains `int` for compatibility. Long-only behavior can be surprising when single-dash options overlap with short options.

Test signals: parse exact, abbreviated, ambiguous, flag-setting, required-argument, optional-argument, and long-only options.
<!-- END_FILE_RESEARCH: sources/compression/xz/lib/getopt-ext.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/lib/getopt-pfx-core.h -->
# sources/compression/xz/lib/getopt-pfx-core.h

Purpose: wrapper that optionally prefixes core getopt symbols to avoid collisions with system getopt.

Important APIs/types/functions: `__GETOPT_PREFIX`, `__GETOPT_ID`, and macro remapping for `getopt`, `optarg`, `opterr`, `optind`, and `optopt`.

Control flow: if a prefix is configured, undefine public names, define prefixed aliases, apply a macOS workaround, clear `_GETOPT_CORE_H`, then include `getopt-core.h`.

State and persistence: compile-time symbol renaming only.

Dependencies and integration: used by generated `getopt.h` for standalone applications embedding gnulib getopt.

Risks: relies on include guard manipulation and platform-specific system header behavior. Misordered includes can still expose unprefixed declarations.

Test signals: compile a program defining `__GETOPT_PREFIX` alongside system `<unistd.h>` and verify only prefixed symbols are exported.
<!-- END_FILE_RESEARCH: sources/compression/xz/lib/getopt-pfx-core.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/lib/getopt-pfx-ext.h -->
# sources/compression/xz/lib/getopt-pfx-ext.h

Purpose: wrapper that optionally prefixes GNU long-option getopt extension symbols.

Important APIs/types/functions: remaps `getopt_long`, `getopt_long_only`, `option`, and `_getopt_internal`; sets `__getopt_argv_const` based on prefixed or compatibility mode.

Control flow: if prefixing is active, build prefixed identifiers, clear extension include guard, then include `getopt-ext.h`.

State and persistence: compile-time renaming only.

Dependencies and integration: pairs with `getopt-pfx-core.h` inside generated `getopt.h`.

Risks: compatibility prototypes intentionally differ when not prefixed. Include guard resets are delicate but needed for system-header collisions.

Test signals: compile prefixed getopt_long users and check symbols with `nm`; verify non-prefixed mode matches expected GNU prototypes.
<!-- END_FILE_RESEARCH: sources/compression/xz/lib/getopt-pfx-ext.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/lib/getopt.c -->
# sources/compression/xz/lib/getopt.c

Purpose: gnulib/GNU implementation of short and long option scanning, including global and reentrant parser entry points.

Important APIs/types/functions: globals `optarg`, `optind`, `opterr`, `optopt`; static `getopt_data`; helpers `exchange`, `process_long_option`, `_getopt_initialize`; public/internal functions `_getopt_internal_r`, `_getopt_internal`, and `getopt`.

Control flow: initialization selects ordering mode from optstring, `POSIXLY_CORRECT`, and caller flags. `_getopt_internal_r` permutes non-options if needed, handles `--`, dispatches long options, processes short option clusters, handles `-W;` long-option forwarding, and returns option codes or errors.

State and persistence: global parser state persists across calls; reentrant state lives in caller-provided `_getopt_data`. It mutates `argv` during permutation.

Dependencies and integration: used when platform getopt is missing or insufficient. Standalone mode disables NLS and alloca, and maps locking to no-ops when unavailable.

Risks: global parser is not thread-safe. Argument permutation requires writable `argv`. Ambiguous long-option tracking may allocate memory; failure degrades diagnostics. Error messages are intentionally untranslated in XZ's standalone build.

Test signals: built-in `-DTEST` harness plus xz CLI parsing tests for permutation, POSIX ordering, long abbreviations, missing args, optional args, and invalid options.
<!-- END_FILE_RESEARCH: sources/compression/xz/lib/getopt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/lib/getopt.in.h -->
# sources/compression/xz/lib/getopt.in.h

Purpose: template for generated `getopt.h`.

Important APIs/types/functions: defines `_GETOPT_H`, optional prefix pre-includes, `_GL_ARG_NONNULL`, and includes `getopt-cdefs.h`, `getopt-pfx-core.h`, and `getopt-pfx-ext.h`.

Control flow: preprocessor-only; `lib/Makefile.am` prepends a generated-file comment.

State and persistence: compile-time declarations only; generated `getopt.h` persists in build output.

Dependencies and integration: central public header for bundled getopt replacement.

Risks: assumes included fragment headers are discoverable via include path. Prefix pre-includes are intended to prevent later system declarations from conflicting.

Test signals: generated header should compile both prefixed and unprefixed consumers with nonnull attributes where supported.
<!-- END_FILE_RESEARCH: sources/compression/xz/lib/getopt.in.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/lib/getopt1.c -->
# sources/compression/xz/lib/getopt1.c

Purpose: implements GNU `getopt_long` and `getopt_long_only` entry points plus reentrant variants.

Important APIs/types/functions: `getopt_long`, `_getopt_long_r`, `getopt_long_only`, `_getopt_long_only_r`, all delegating to `_getopt_internal` or `_getopt_internal_r`.

Control flow: long mode passes `long_only=0`; long-only mode passes `long_only=1`. Reentrant variants accept caller-owned `_getopt_data`.

State and persistence: public functions share global getopt state; `_r` variants use supplied state.

Dependencies and integration: included in `libgnu.a` when replacement long-option parsing is needed.

Risks: same argv mutation and global-state caveats as `getopt.c`. The test harness is compile-time only.

Test signals: compile with `-DTEST` and run sample long options; xz long-option parsing provides integration coverage.
<!-- END_FILE_RESEARCH: sources/compression/xz/lib/getopt1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/lib/getopt_int.h -->
# sources/compression/xz/lib/getopt_int.h

Purpose: internal declarations and state structure for the gnulib getopt implementation.

Important APIs/types/functions: `enum __ord`, `struct _getopt_data`, `_GETOPT_DATA_INITIALIZER`, `_getopt_internal`, `_getopt_internal_r`, `_getopt_long_r`, and `_getopt_long_only_r`.

Control flow: no runtime logic; defines how parser state tracks current scan pointer, ordering mode, skipped non-option ranges, and standard getopt globals.

State and persistence: describes both global-copy and reentrant state layouts.

Dependencies and integration: included by `getopt.c` and `getopt1.c`.

Risks: layout changes affect both source files and any internal reentrant consumers. Initialization requires `optind=1`, `opterr=1`, and cleared internal initialized flag.

Test signals: reentrant parser tests should run two argument vectors independently and confirm no cross-state leakage.
<!-- END_FILE_RESEARCH: sources/compression/xz/lib/getopt_int.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/po/POTFILES.in -->
# sources/compression/xz/po/POTFILES.in

Purpose: gettext input manifest listing C files that contain translatable program strings.

Important APIs/types/functions: line-oriented file list for `xgettext`, covering xz frontend sources, `lzmainfo`, `tuklib_exit`, and liblzma string conversion.

Control flow: gettext tooling reads the manifest to extract `_`, `N_`, `W_`, and related message strings.

State and persistence: affects generated POT/PO catalogs, not runtime directly.

Dependencies and integration: used by gettext build/update scripts and `po/Makevars` configuration.

Risks: new translatable strings outside this manifest will be missing from catalogs. Removed files can break extraction.

Test signals: run translation update target and verify new/changed strings appear in `xz.pot`.
<!-- END_FILE_RESEARCH: sources/compression/xz/po/POTFILES.in -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/po4a/po4a.conf -->
# sources/compression/xz/po4a/po4a.conf

Purpose: po4a configuration for translated man pages.

Important APIs/types/functions: declares languages `ar de fr it ko pt_BR ro sr sv uk`, POT path `xz-man.pot`, and man-page source-to-output mappings with optional author addenda.

Control flow: `po4a` reads each `[type: man]` mapping, updates translations, and writes localized man pages under `po4a/man/$lang/`.

State and persistence: controls generated `.po`, `.pot`, and localized man page outputs.

Dependencies and integration: consumed by `po4a/update-po`; source man pages live in `src/xz`, `src/xzdec`, `src/lzmainfo`, and `src/scripts`.

Risks: adding a man page or language requires updating this file. Bad addenda or paths can prevent generation for one or more languages.

Test signals: run `po4a/update-po` and verify localized man pages are regenerated for all configured languages.
<!-- END_FILE_RESEARCH: sources/compression/xz/po4a/po4a.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/po4a/update-po -->
# sources/compression/xz/po4a/update-po

Purpose: updates translated man-page POT/PO files and regenerates localized man pages.

Important APIs/types/functions: checks for `po4a`, locates `po4a.conf`, derives `PACKAGE_VERSION`, creates temporary `*.po.authors` addenda from translator comments, invokes `po4a` with diff-friendly options, post-processes tables with Perl, and rewrites `xz-man.pot` header.

Control flow: validate tool/config, generate author addenda for each `.po`, run `po4a --force`, remove addenda, insert `\&` after non-ASCII table chars, then replace POT header from `po/xz.pot-header`.

State and persistence: modifies `.po`, `xz-man.pot`, and `man/*/*.1`; temporary `.po.authors` files are removed.

Dependencies and integration: depends on `/bin/sh`, po4a, perl, sed, and `build-aux/version.sh`.

Risks: in-place Perl editing touches generated man pages broadly. The script exits if po4a is missing, which is acceptable for update workflow but not for ordinary builds.

Test signals: run from `po4a/`, inspect git diff for expected POT version/header changes and valid localized man pages.
<!-- END_FILE_RESEARCH: sources/compression/xz/po4a/update-po -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/Makefile.am -->
# sources/compression/xz/src/Makefile.am

Purpose: top-level Automake dispatcher for XZ Utils source subdirectories.

Important APIs/types/functions: `SUBDIRS` always includes `liblzma` and `xzdec`, conditionally adds `xz`, `lzmainfo`, and `scripts`; `EXTRA_DIST` lists common helper sources/resources.

Control flow: Automake descends into enabled subdirectories according to configure conditionals.

State and persistence: build artifacts are created in child directories; this file persists distribution membership for common files.

Dependencies and integration: controlled by component conditionals from `configure.ac`.

Risks: forgetting a common file in `EXTRA_DIST` can break release tarballs. Conditional subdir ordering matters because tools link against liblzma.

Test signals: `make distcheck` validates distribution completeness; configure toggles should include/exclude subdirs as expected.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/common/my_landlock.h -->
# sources/compression/xz/src/common/my_landlock.h

Purpose: header-only Linux Landlock helper for creating deny-all ruleset attributes and syscall wrappers.

Important APIs/types/functions: `my_landlock_ruleset_attr_forbid_all`, `my_landlock_create_ruleset`, `my_landlock_restrict_self`, fallback `LANDLOCK_ACCESS_FS_*` macros, and cached ABI version state.

Control flow: query ABI version once with `landlock_create_ruleset(... VERSION)`, optionally detect buggy RHEL 9 ABI 6 signal scope, fill `landlock_ruleset_attr` with all known restrictions, then mask fields unsupported by the runtime ABI.

State and persistence: static cached ABI version and RHEL detection flag; no filesystem persistence.

Dependencies and integration: included by sandbox code only when Landlock support is configured. Requires Linux Landlock, syscall numbers, `prctl`, and `uname`.

Risks: note says only one file should include it and only one thread should call it because of static state. ABI/version backport quirks are explicitly handled but future ABI changes may need updates.

Test signals: sandbox tests on kernels with no Landlock, ABI 1-9 features, and RHEL backport variants; verify unsupported access bits are not passed.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/common/my_landlock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/common/mythread.h -->
# sources/compression/xz/src/common/mythread.h

Purpose: portability abstraction for threading, mutexes, condition variables, one-time initialization, and signal masks.

Important APIs/types/functions: `MYTHREAD_ENABLED`, `mythread_sync`, `mythread_once`, `mythread_create`, `mythread_join`, mutex helpers, condition helpers, `mythread_condtime_set`, `MYTHREAD_RET_TYPE`, and platform-specific typedefs.

Control flow: preprocessor selects no-thread, POSIX pthread, Win95, or Vista implementations. POSIX thread creation temporarily blocks all signals; condition variables prefer monotonic clocks when available. Windows uses `_beginthreadex`, critical sections, events or condition variables, and tick-count timeouts.

State and persistence: synchronization state is caller-owned; no persistent state except static once guards inside macros.

Dependencies and integration: selected by `MYTHREAD_POSIX`, `MYTHREAD_WIN95`, or `MYTHREAD_VISTA` from `configure.ac`; used by threaded liblzma and tools.

Risks: no-thread `mythread_once` is not thread-safe by design. Win95 once support is absent. Assertions check synchronization API errors, so release behavior depends on `NDEBUG`.

Test signals: threaded encoder/decoder tests on POSIX and Windows variants, timeout behavior under clock changes, and signal-mask inheritance checks.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/common/mythread.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/common/sysdefs.h -->
# sources/compression/xz/src/common/sysdefs.h

Purpose: central portability header for common includes, integer format fallbacks, Windows stdio selection, bool/alignment compatibility, and small utility macros.

Important APIs/types/functions: `memzero`, `my_min`, `my_max`, `ARRAY_SIZE`, `lzma_attr_alloc_size`, `FALLTHROUGH`, `alignas`, fallback `UINT*_C`, `PRI*`, `UINT*_MAX`, and `SIZE_MAX` validation.

Control flow: include generated `config.h` when available, select MinGW ANSI stdio behavior, include standard headers conditionally, define missing integer/printf macros, enforce 32/64-bit `size_t`, provide fake `bool` if needed, and select alignment/fallthrough attributes.

State and persistence: compile-time only.

Dependencies and integration: included broadly by xz, debug helpers, and common modules.

Risks: assumptions about integer widths are explicit; unsupported `size_t` widths hard-error. MinGW stdio choice affects binary size and formatting behavior.

Test signals: compile on C99, pre-C99-like, MinGW/UCRT/MSVCRT, big-endian, and unusual `size_t` platforms.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/common/sysdefs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/common/tuklib_common.h -->
# sources/compression/xz/src/common/tuklib_common.h

Purpose: common base header for tuklib modules.

Important APIs/types/functions: `TUKLIB_SYMBOL_PREFIX`, `TUKLIB_SYMBOL`, concatenation macros, C++ declaration guards, `TUKLIB_GNUC_REQ`, `tuklib_attr_format_printf`, `tuklib_attr_noreturn`, and `TUKLIB_DOSLIKE`.

Control flow: include `tuklib_config.h`, define symbol-prefixing and attributes based on compiler/language/platform macros.

State and persistence: compile-time only.

Dependencies and integration: every tuklib module includes it; allows symbol prefixing when tuklib is embedded in libraries.

Risks: prefix settings must be consistent across declarations and definitions. Attribute selection affects diagnostics and ABI annotations.

Test signals: compile tuklib modules with custom `TUKLIB_SYMBOL_PREFIX`, C++, C23, GCC/Clang/MSVC, and DOS-like targets.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/common/tuklib_common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/common/tuklib_config.h -->
# sources/compression/xz/src/common/tuklib_config.h

Purpose: thin configuration include for tuklib modules.

Important APIs/types/functions: includes `sysdefs.h` when `HAVE_CONFIG_H` is available; otherwise includes standard `stddef.h`, `stdbool.h`, `inttypes.h`, and `limits.h`.

Control flow: preprocessor-only fallback used by standalone tools such as table generators.

State and persistence: compile-time include state only.

Dependencies and integration: sits between tuklib common code and project-specific configuration.

Risks: no-config fallback assumes standard headers exist and lacks Autoconf feature macros, so only limited standalone modules should use it.

Test signals: compile `crc32_tablegen.c` or similar no-config consumers and normal configured builds.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/common/tuklib_config.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/common/tuklib_cpucores.c -->
# sources/compression/xz/src/common/tuklib_cpucores.c

Purpose: detects the number of online CPU cores/threads.

Important APIs/types/functions: `tuklib_cpucores(void)` with platform paths for Windows `GetSystemInfo`, Linux `sched_getaffinity`, FreeBSD `cpuset_getaffinity`, BSD `sysctl`, POSIX `sysconf`, and HP-UX `pstat_getdynamic`.

Control flow: initialize return to zero, execute the first compile-time selected method, validate positive counts, and return zero if unknown.

State and persistence: no state beyond local variables.

Dependencies and integration: selected by `TUKLIB_CPUCORES_*` macros from configure; used by threaded compression defaults and hardware reporting.

Risks: CPU affinity APIs can report a constrained set rather than physical cores, which is usually desired. Fixed `cpu_set_t` may undercount on systems with very large CPU sets.

Test signals: compare to OS tools under normal and affinity-restricted execution; test unknown-method fallback returns zero.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/common/tuklib_cpucores.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/common/tuklib_cpucores.h -->
# sources/compression/xz/src/common/tuklib_cpucores.h

Purpose: public tuklib declaration for CPU core detection.

Important APIs/types/functions: `tuklib_cpucores` symbol macro and `extern uint32_t tuklib_cpucores(void)`.

Control flow: declaration-only.

State and persistence: no state.

Dependencies and integration: included by tools/examples that need CPU thread count, with optional symbol prefixing.

Risks: callers must handle zero meaning unknown.

Test signals: compile/link against `tuklib_cpucores.c`; verify prefixed symbol builds.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/common/tuklib_cpucores.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/common/tuklib_exit.c -->
# sources/compression/xz/src/common/tuklib_exit.c

Purpose: exits a program after flushing/closing stdout and stderr, converting close errors into a caller-specified error status.

Important APIs/types/functions: `tuklib_exit(int status, int err_status, int show_error)`, `ferror`, `fclose`, `progname`, `_`, and `strerror(errno)`.

Control flow: if current status is not already error status, close stdout and optionally print a localized diagnostic on failure; then close stderr and adjust status if needed; call `exit`.

State and persistence: consumes stdio stream state; process terminates.

Dependencies and integration: requires tuklib gettext and progname modules; used by command-line tools to catch delayed write errors.

Risks: once stdout fails, diagnostic depends on stderr still being usable. `errno` use after `fclose` is meaningful only for close failures, handled separately from `ferror`.

Test signals: pipe xz output to a command that closes early and verify error status/message handling.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/common/tuklib_exit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/common/tuklib_exit.h -->
# sources/compression/xz/src/common/tuklib_exit.h

Purpose: declaration for `tuklib_exit`.

Important APIs/types/functions: prefixed `tuklib_exit` symbol and `tuklib_attr_noreturn` declaration.

Control flow: header-only.

State and persistence: none.

Dependencies and integration: documents dependency on tuklib progname/gettext modules.

Risks: callers should not expect return; incorrect status arguments can hide write errors.

Test signals: compile with compilers honoring noreturn and check no fallthrough warnings at call sites.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/common/tuklib_exit.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/common/tuklib_gettext.h -->
# sources/compression/xz/src/common/tuklib_gettext.h

Purpose: gettext wrapper that provides localization macros with or without NLS.

Important APIs/types/functions: `TUKLIB_GETTEXT`, `tuklib_gettext_init`, `_`, `ngettext`, `N_`, and `W_`.

Control flow: if NLS is enabled, include `libintl.h`, set locale, bind text domain, and use gettext. Otherwise still set locale but map translations to original strings.

State and persistence: initializes process locale and gettext text domain; no file writes.

Dependencies and integration: used by xz frontend and tuklib modules; `W_` coordinates with xgettext options for word-wrapped strings.

Risks: locale initialization is process-global. Disabled NLS still depends on locale for multibyte handling.

Test signals: run tools under translated locale and under `--disable-nls`; verify plural handling and word-wrap comments extraction.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/common/tuklib_gettext.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/common/tuklib_integer.h -->
# sources/compression/xz/src/common/tuklib_integer.h

Purpose: portable integer, endian, unaligned/aligned access, byte-swap, and bit-scan helpers.

Important APIs/types/functions: `byteswap16/32/64`, `conv16/32/64{be,le}`, `read*/write*{ne,be,le}`, `aligned_read*/aligned_write*`, `bsr32`, `clz32`, `ctz32`, and `bsf32`.

Control flow: preprocessor selects compiler/system byte-swap intrinsics or fallback expressions, endian conversion macros, fast-unaligned `memcpy` or byte-by-byte implementations, aligned access with `__builtin_assume_aligned` when possible, and bit-scan implementations using compiler builtins, inline x86 assembly, MSVC intrinsics, or portable shifts.

State and persistence: stateless inline/macro operations.

Dependencies and integration: consumed throughout liblzma for parsing headers, CRC, range coding, and optimized data access.

Risks: macro arguments may be evaluated more than once for conversion/write macros. Optional unsafe type punning can violate strict aliasing. Bit-scan functions are undefined for zero input.

Test signals: unit tests on big/little-endian and strict-align architectures; sanitizer/UB builds without unsafe punning; compare read/write round trips for aligned and unaligned buffers.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/common/tuklib_integer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/common/tuklib_mbstr.h -->
# sources/compression/xz/src/common/tuklib_mbstr.h

Purpose: public declarations for multibyte string display-width helpers.

Important APIs/types/functions: `tuklib_mbstr_width`, `tuklib_mbstr_width_mem`, and `tuklib_mbstr_fw`.

Control flow: declaration-only; comments define behavior for invalid, partial, or non-printable multibyte input and printf field-width alignment.

State and persistence: none.

Dependencies and integration: used by terminal/help/list formatting where byte length differs from column width.

Risks: callers must handle `(size_t)-1` and `-1` error returns. `tuklib_mbstr_fw` has undefined behavior for null strings, nonpositive minimum columns, or field widths over `INT_MAX`.

Test signals: width tests for ASCII, UTF-8, invalid sequences, CJK, combining characters, and fallback single-byte builds.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/common/tuklib_mbstr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/common/tuklib_mbstr_fw.c -->
# sources/compression/xz/src/common/tuklib_mbstr_fw.c

Purpose: computes a printf field width that aligns a multibyte string to a minimum terminal column count.

Important APIs/types/functions: `tuklib_mbstr_fw(const char *str, int columns_min)` calls `tuklib_mbstr_width`.

Control flow: get display width and byte length; return `-1` on width failure, `0` if string already exceeds minimum columns, otherwise add the column shortfall to byte length and return it as field width.

State and persistence: stateless.

Dependencies and integration: supports table formatting in CLI output.

Risks: relies on caller meeting header preconditions; cast to `int` assumes result fits.

Test signals: align ASCII and multibyte names in formatted tables; invalid sequence should return `-1`.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/common/tuklib_mbstr_fw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/common/tuklib_mbstr_nonprint.c -->
# sources/compression/xz/src/common/tuklib_mbstr_nonprint.c

Purpose: detects non-printable characters in strings and masks them with `?`.

Important APIs/types/functions: static `is_next_printable`, `has_nonprint`, public `tuklib_has_nonprint`, `tuklib_mask_nonprint_r`, and `tuklib_mask_nonprint`.

Control flow: with `mbrtowc`, decode one multibyte character at a time, treating incomplete/invalid/non-printable sequences as non-printable; without it, use `isprint` bytewise. Masking frees old caller memory, returns original string if printable, otherwise allocates a modified copy replacing bad characters.

State and persistence: `tuklib_mask_nonprint` uses a static allocation and is not thread-safe; reentrant form uses caller-owned `char **mem`. `errno` is preserved.

Dependencies and integration: used for safe display of untrusted filenames or messages.

Risks: allocation failure returns `"???"`, losing the original string. Windows UTF-16 replacement behavior is special-cased for non-BMP UTF-8.

Test signals: strings with control bytes, invalid UTF-8, incomplete trailing sequences, printable Unicode, and repeated reentrant calls.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/common/tuklib_mbstr_nonprint.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/common/tuklib_mbstr_nonprint.h -->
# sources/compression/xz/src/common/tuklib_mbstr_nonprint.h

Purpose: declarations and contract for non-printable string masking.

Important APIs/types/functions: `tuklib_has_nonprint`, `tuklib_mask_nonprint_r`, and `tuklib_mask_nonprint`.

Control flow: header-only documentation of reentrant memory ownership and single-threaded convenience behavior.

State and persistence: documents that `tuklib_mask_nonprint` has internal static state and `tuklib_mask_nonprint_r` frees/replaces caller memory.

Dependencies and integration: included by CLI display code handling untrusted filenames.

Risks: callers must initialize `*mem` to NULL before first reentrant use and must not use the static convenience function concurrently.

Test signals: API tests should verify errno preservation, ownership behavior, and thread-safety limitations.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/common/tuklib_mbstr_nonprint.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/common/tuklib_mbstr_width.c -->
# sources/compression/xz/src/common/tuklib_mbstr_width.c

Purpose: calculates terminal display width for null-terminated or length-delimited multibyte strings.

Important APIs/types/functions: `tuklib_mbstr_width`, `tuklib_mbstr_width_mem`, `mbrtowc`, `wcwidth`, and `mbsinit`.

Control flow: null-terminated wrapper records byte length with `strlen`; length-based function either returns byte length in single-byte fallback mode or decodes each multibyte character, sums `wcwidth`, and validates shift state.

State and persistence: stateless.

Dependencies and integration: used by field-width and wrapping helpers for localized CLI output.

Risks: returns `(size_t)-1` for invalid sequences or negative `wcwidth`. Without `wcwidth`, each multibyte character is assumed one column, which is wrong for CJK but better than byte count.

Test signals: UTF-8 width fixtures under locales with and without `wcwidth`; invalid/partial sequences should fail.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/common/tuklib_mbstr_width.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/common/tuklib_mbstr_wrap.c -->
# sources/compression/xz/src/common/tuklib_mbstr_wrap.c

Purpose: word-wraps multibyte strings to a `FILE` stream, with support for indentation modes and selected control-character markup.

Important APIs/types/functions: `tuklib_wraps`, `tuklib_wrapf`, `struct tuklib_wrap_opt`, `tuklib_mbstr_width_mem`, `vasprintf`/`vsnprintf`, and `TUKLIB_WRAP_*` status flags.

Control flow: validate margins, track current/pending indentation and newline state, scan to next break opportunity, measure width, wrap when needed, suppress trailing spaces, handle `\t`, `\b`, `\v`, `\r`, `\n`, and implicit final newline. `wrapf` formats into a temporary buffer before wrapping.

State and persistence: local state only; writes to caller-provided stream. `wrapf` allocates a temporary string and frees it.

Dependencies and integration: used for translated help/messages where manual wrapping is error-prone.

Risks: writes one byte at a time, so stream buffering matters. Invalid multibyte input aborts wrapping. Fallback `vsnprintf` path truncates at 128 KiB.

Test signals: wrap fixtures for long words, multiple spaces, zero-width tabs, unbreakable blocks, alternative indentation, invalid UTF-8, and simulated I/O errors.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/common/tuklib_mbstr_wrap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/common/tuklib_mbstr_wrap.h -->
# sources/compression/xz/src/common/tuklib_mbstr_wrap.h

Purpose: public API and detailed contract for multibyte word wrapping.

Important APIs/types/functions: `TUKLIB_WRAP_WARN_OVERLONG`, error flags, `struct tuklib_wrap_opt`, `tuklib_wraps`, and printf-annotated `tuklib_wrapf`.

Control flow: header-only; documents special markup semantics for `\t`, `\b`, `\v`, `\r`, and `\n`, and translator guidance via `W_`.

State and persistence: no state; output state is in the target `FILE`.

Dependencies and integration: included by CLI message/help code and tied to gettext extraction comments.

Risks: only `\n` and sometimes `\t` should appear in translatable strings; other control markup can confuse translators/tools. Right-to-left and no-space languages may need manual care.

Test signals: compile-time format checking for `wrapf`; golden output tests for documented control characters and status flags.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/common/tuklib_mbstr_wrap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/common/tuklib_open_stdxxx.c -->
# sources/compression/xz/src/common/tuklib_open_stdxxx.c

Purpose: ensures file descriptors 0, 1, and 2 are open before a command-line tool proceeds.

Important APIs/types/functions: `tuklib_open_stdxxx(int err_status)`, `fcntl(F_GETFD)`, `open("/dev/null")`, `close`, and `exit`.

Control flow: on DOS-like systems do nothing. Else iterate descriptors 0-2; when a descriptor is closed, open `/dev/null` with mode chosen to occupy that exact descriptor, otherwise exit with the supplied status.

State and persistence: mutates process file descriptor table only.

Dependencies and integration: protects later opens from accidentally becoming stdin/stdout/stderr.

Risks: mode selection appears reversed from the comment's intuitive direction (`stdin` gets `O_WRONLY`, outputs get `O_RDONLY`), likely intentionally making accidental wrong-direction I/O fail but worth preserving carefully. If `/dev/null` open returns a different descriptor, it exits silently.

Test signals: run a small tool with closed fd 0/1/2 and verify descriptors are reopened predictably.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/common/tuklib_open_stdxxx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/common/tuklib_open_stdxxx.h -->
# sources/compression/xz/src/common/tuklib_open_stdxxx.h

Purpose: declaration for `tuklib_open_stdxxx`.

Important APIs/types/functions: prefixed `tuklib_open_stdxxx(int err_status)`.

Control flow: declaration-only.

State and persistence: none in header.

Dependencies and integration: used by program startup code before normal file handling.

Risks: callers should invoke it early, before opening other files, or descriptor repair may not occupy 0/1/2.

Test signals: compile/link with implementation and test closed standard descriptors.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/common/tuklib_open_stdxxx.h -->
