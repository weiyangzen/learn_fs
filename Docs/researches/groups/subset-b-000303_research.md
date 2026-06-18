# Research: subset-b-000303

<!-- BEGIN_FILE_RESEARCH: sources/compression/zlib/examples/zpipe.c -->
# sources/compression/zlib/examples/zpipe.c

## Purpose
`zpipe.c` is a compact example program showing correct streaming use of zlib `deflate()` and `inflate()` on `stdin` and `stdout`. With no arguments it compresses; with `-d` it decompresses.

## Important APIs, Types, and Functions
The main routines are `def(FILE *source, FILE *dest, int level)`, `inf(FILE *source, FILE *dest)`, `zerr(int ret)`, and `main()`. They use `z_stream`, `deflateInit()`, `deflate()`, `deflateEnd()`, `inflateInit()`, `inflate()`, and `inflateEnd()`, with `CHUNK` fixed at 16384 bytes.

## Control Flow, State, and Persistence
Compression repeatedly reads input chunks, selects `Z_FINISH` only at source EOF, drains deflate output until the output buffer is not full, then asserts stream completion. Decompression reads input chunks, inflates until each output buffer is not full, converts `Z_NEED_DICT` to `Z_DATA_ERROR`, and reports incomplete streams as data errors. State is limited to local buffers, the zlib stream, and standard I/O binary mode; no files are opened directly.

## Dependencies and Integration Points
It depends on `zlib.h`, libc file I/O, and platform-specific `_setmode()` wrappers for DOS/Windows-like systems. It is an example and smoke-test style integration for the public zlib stream API.

## Risks and Test Signals
Risks are mainly example limitations: fixed buffer size, stdin/stdout-only operation, and assert usage that assumes zlib contract invariants. Useful signals are byte-exact compression/decompression round trips, correct nonzero returns on invalid compressed input, and binary-mode preservation on Windows.
<!-- END_FILE_RESEARCH: sources/compression/zlib/examples/zpipe.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zlib/examples/zran.c -->
# sources/compression/zlib/examples/zran.c

## Purpose
`zran.c` demonstrates indexed random access into zlib, gzip, or raw deflate streams. It builds access points at deflate block boundaries and later resumes raw inflation from the closest point before a requested uncompressed offset.

## Important APIs, Types, and Functions
Public functions are `deflate_index_build()`, `deflate_index_extract()`, and `deflate_index_free()`, declared in `zran.h`. Internal helpers include `add_point()`, optional `inflatePreface()` when `NOPRIME` replaces `inflatePrime()`, and the `TEST` main program. The implementation uses `point_t`, `struct deflate_index`, `inflateInit2()`, `inflateReset2()`, `inflateSetDictionary()`, `inflatePrime()`, and `inflate(..., Z_BLOCK)`.

## Control Flow, State, and Persistence
Index building auto-detects raw/zlib/gzip input, inflates one block at a time, and records compressed offset, bit offset, uncompressed offset, and a copied 32 KiB history window whenever the span threshold is met. Extraction binary-searches the point list, seeks the input file, primes any saved prefix bits, installs the saved dictionary, skips forward to the requested offset, and writes up to the requested length. The index owns heap-allocated point windows and a reusable inflate stream, and gzip multi-member boundaries reset history.

## Dependencies and Integration Points
It depends on `zlib.h`, `zran.h`, standard file APIs, `off_t`, `fseeko()`, and optional `inflatePrime()` support. Applications can save/load the exposed point data because access points avoid opaque inflate-state pointers.

## Risks and Test Signals
Risks include memory cost of roughly 32 KiB per point, index invalidation if the compressed file changes, subtle bit-offset handling, and multi-member gzip trailer/header transitions. Strong signals are successful extraction at offsets before, at, and after access points; raw/zlib/gzip detection; crossing gzip members; and clean `Z_BUF_ERROR`, `Z_DATA_ERROR`, or `Z_ERRNO` on damaged inputs.
<!-- END_FILE_RESEARCH: sources/compression/zlib/examples/zran.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zlib/examples/zran.h -->
# sources/compression/zlib/examples/zran.h

## Purpose
`zran.h` exposes the data structures and API for the random-access deflate index example implemented in `zran.c`.

## Important APIs, Types, and Functions
It defines `point_t`, which stores uncompressed offset, compressed file offset, bit offset, dictionary length, and dictionary bytes. It also defines `struct deflate_index`, containing point count, stream mode, uncompressed length, point list, and reusable `z_stream`. The API surface is `deflate_index_build()`, `deflate_index_extract()`, and `deflate_index_free()`.

## Control Flow, State, and Persistence
The header performs no runtime work. Its comments define the ownership contract: successful builds return an allocated index through `*built`, failed builds return `NULL`, extraction returns byte counts or negative zlib errors, and the caller must eventually free the index.

## Dependencies and Integration Points
It includes `<stdio.h>` and `zlib.h`, so users get `FILE`, `off_t`, `ptrdiff_t`, `size_t`, and `z_stream` through the expected zlib platform layer. It intentionally exposes access-point internals to permit persistence outside this example.

## Risks and Test Signals
Risks are ABI sensitivity and ownership misuse, especially failing to free per-point `window` allocations. Compile and integration tests should verify that applications can build, inspect, extract with, and free a `struct deflate_index` without depending on hidden implementation state.
<!-- END_FILE_RESEARCH: sources/compression/zlib/examples/zran.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zlib/gzclose.c -->
# sources/compression/zlib/gzclose.c

## Purpose
`gzclose.c` provides the generic `gzclose()` dispatcher for zlib gzip file handles, kept in a separate translation unit so linkers can avoid pulling unused read or write close paths.

## Important APIs, Types, and Functions
The only exported function is `gzclose(gzFile file)`. It casts the opaque handle to `gz_statep`, checks for `NULL`, and dispatches to `gzclose_r()` for read mode or `gzclose_w()` for write mode when compression support is enabled.

## Control Flow, State, and Persistence
The function does not own close mechanics itself. It inspects `state->mode` and delegates cleanup, stream finalization, descriptor close, and error return semantics to the mode-specific implementation. With `NO_GZCOMPRESS`, it always calls the read close implementation.

## Dependencies and Integration Points
It includes `gzguts.h`, which defines `gz_statep`, mode constants, and internal close declarations. It is part of the public `gzFile` API implementation.

## Risks and Test Signals
The main risk is dispatching an invalid or corrupted `gzFile` state to the wrong close routine; the mode-specific close functions provide additional validation. Tests should cover closing read handles, write handles with pending compressed output, `NULL` handles returning `Z_STREAM_ERROR`, and builds with `NO_GZCOMPRESS`.
<!-- END_FILE_RESEARCH: sources/compression/zlib/gzclose.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zlib/gzguts.h -->
# sources/compression/zlib/gzguts.h

## Purpose
`gzguts.h` is the private shared header for zlib `gz*` file operations. It centralizes platform feature macros, gzip file modes, the internal `gz_state` layout, and shared helper prototypes.

## Important APIs, Types, and Functions
It defines `ZLIB_INTERNAL`, `GZBUFSIZE`, `GZ_NONE`, `GZ_READ`, `GZ_WRITE`, `GZ_APPEND`, read submodes `LOOK`, `COPY`, `GZIP`, and `gz_state`/`gz_statep`. `gz_state` embeds the public `gzFile_s` prefix plus file descriptor, path, buffers, direct/transparent mode, read state, write state, seek skip count, error message, and in-place `z_stream`. It declares `gz_error()`, `gz_intmax()`, and platform helpers.

## Control Flow, State, and Persistence
The header owns no runtime flow, but its fields define all persistent state for `gzopen()`, `gzread()`, `gzwrite()`, seeking, error reporting, and closing. The `x` prefix must remain compatible with public `gzgetc()` macro expectations.

## Dependencies and Integration Points
It includes `zlib.h`, libc headers, platform I/O headers, large-file compatibility declarations, and Windows/OS-specific error adaptations. It links the otherwise separate `gzlib.c`, `gzread.c`, `gzwrite.c`, and `gzclose.c` internals.

## Risks and Test Signals
Risks include platform macro drift, large-file offset mismatches, public/private struct prefix breakage, and buffer-size assumptions that require doubling to fit in `unsigned`. Test signals include cross-platform compilation, `gzbuffer()` bounds checks, large-file seek/tell behavior, and macro-compatible `gzgetc()` operation.
<!-- END_FILE_RESEARCH: sources/compression/zlib/gzguts.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zlib/gzlib.c -->
# sources/compression/zlib/gzlib.c

## Purpose
`gzlib.c` implements common `gzFile` operations shared by reading and writing: open, descriptor wrapping, buffer sizing, seeking, telling, offset reporting, EOF/error handling, and internal error-message management.

## Important APIs, Types, and Functions
Public functions include `gzopen()`, `gzopen64()`, `gzdopen()`, optional `gzopen_w()`, `gzbuffer()`, `gzrewind()`, `gzseek64()`, `gzseek()`, `gztell64()`, `gztell()`, `gzoffset64()`, `gzoffset()`, `gzeof()`, `gzerror()`, and `gzclearerr()`. Key internals are `gz_open()`, `gz_reset()`, `gz_error()`, `gz_intmax()`, `LSEEK`, and Windows CE `gz_strwinerror()`.

## Control Flow, State, and Persistence
`gz_open()` parses mode flags, allocates `gz_state`, preserves a display path, opens or adopts the descriptor, records the initial read position, and calls `gz_reset()`. Seeking normalizes `SEEK_SET`/`SEEK_CUR` into uncompressed skip state, rewinding for backward reads and synthesizing zero output for forward write seeks elsewhere. Errors are stored in `state->err` and optional allocated `state->msg`.

## Dependencies and Integration Points
It depends on `gzguts.h`, POSIX-like `open()`, `lseek()`, `fcntl()`, `close()` elsewhere, and Windows wide-character support. `gzread.c` and `gzwrite.c` consume the initialized `gz_state` and pending `skip` requests.

## Risks and Test Signals
Risks include mode-string ambiguity, nonblocking descriptor flags, large-file truncation through narrow APIs, allocation failure while constructing path/error messages, and seeking in transparent versus compressed streams. Tests should cover mode combinations (`r`, `w`, `a`, `T`, `G`, `e`, `x`, `N`), rewind, forward/backward seek, tell/offset consistency, and error clearing.
<!-- END_FILE_RESEARCH: sources/compression/zlib/gzlib.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zlib/gzread.c -->
# sources/compression/zlib/gzread.c

## Purpose
`gzread.c` implements all read-side `gzFile` operations, including gzip auto-detection, transparent copying, decompression, buffered character operations, pushback, line reads, direct-mode reporting, and read close.

## Important APIs, Types, and Functions
Public functions are `gzread()`, `gzfread()`, `gzgetc()`, `gzgetc_()`, `gzungetc()`, `gzgets()`, `gzdirect()`, and `gzclose_r()`. Internal helpers are `gz_load()`, `gz_avail()`, `gz_look()`, `gz_decomp()`, `gz_fetch()`, `gz_skip()`, and `gz_read()`.

## Control Flow, State, and Persistence
The read path lazily allocates input/output buffers and initializes an inflate stream on first need. `gz_look()` decides whether the input is gzip or transparent data, `gz_fetch()` dispatches among header lookup, raw copy, and decompression, and `gz_read()` drains existing output before fetching or direct-filling the user buffer. State persists in `how`, `direct`, `junk`, `again`, `eof`, `past`, `skip`, `x.have`, `x.next`, and `x.pos`. `gzclose_r()` frees buffers, ends inflate, closes the descriptor, and returns deferred EOF/data status.

## Dependencies and Integration Points
It uses `gzguts.h`, `read()`, `close()`, `inflateInit2(15 + 16)`, `inflateReset()`, and `inflate()`. It cooperates with `gzlib.c` for open/reset/seek/error state and with `gzclose.c` for generic close dispatch.

## Risks and Test Signals
Risks include nonblocking `EAGAIN` handling, distinguishing trailing garbage from corrupt gzip data, multi-member gzip transitions, pushback buffer room, and deferred errors after returning already-produced bytes. Tests should cover gzip, transparent, empty, truncated, concatenated-member, pushed-back, line-read, nonblocking, and seek-skip reads.
<!-- END_FILE_RESEARCH: sources/compression/zlib/gzread.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zlib/gzwrite.c -->
# sources/compression/zlib/gzwrite.c

## Purpose
`gzwrite.c` implements write-side `gzFile` operations: buffered writes, direct transparent writes, formatted output, flushing, compression parameter changes, synthetic seek holes, and write close.

## Important APIs, Types, and Functions
Public functions include `gzwrite()`, `gzfwrite()`, `gzputc()`, `gzputs()`, `gzvprintf()`, `gzprintf()`, legacy varargs `gzprintf()` for non-stdarg builds, `gzflush()`, `gzsetparams()`, and `gzclose_w()`. Internal helpers are `gz_init()`, `gz_comp()`, `gz_zero()`, `gz_write()`, and conditionally `gz_vacate()`.

## Control Flow, State, and Persistence
Write state is lazily initialized. Compressed mode allocates input/output buffers and calls `deflateInit2()` with `MAX_WBITS + 16` to emit gzip framing; direct mode writes input bytes unchanged. Small writes accumulate in `state->in`, large writes compress directly from caller buffers, pending seek skips are emitted as zero bytes, and `gz_comp()` handles output buffer draining plus `Z_FINISH` reset. `gzclose_w()` emits pending zeros, finishes compression, releases buffers/deflate state, closes the descriptor, and preserves the strongest error.

## Dependencies and Integration Points
It depends on `gzguts.h`, `write()`, `close()`, `deflateInit2()`, `deflate()`, `deflateReset()`, `deflateParams()`, and standard formatted-output facilities when available. It consumes open/mode/skip/error state from `gzlib.c`.

## Risks and Test Signals
Risks include nonblocking partial writes, formatted-output truncation, insecure fallback formatting when explicitly enabled, parameter changes with buffered input, and integer-return API limits. Tests should cover small and large writes, `gzputc()` buffering, `gzprintf()` overflow behavior, `gzflush()` modes, `gzsetparams()`, transparent `T` mode, seek holes, and close-time trailer correctness.
<!-- END_FILE_RESEARCH: sources/compression/zlib/gzwrite.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zlib/infback.c -->
# sources/compression/zlib/infback.c

## Purpose
`infback.c` implements zlib's callback-driven raw deflate inflater. It is designed for applications that provide input and consume output through callbacks while supplying the sliding window buffer.

## Important APIs, Types, and Functions
The public entry points are `inflateBackInit_()`, `inflateBack()`, and `inflateBackEnd()`. It uses `struct inflate_state`, `inflate_table()`, `inflate_fixed()`, `inflate_fast()`, and callback types `in_func` and `out_func`. Macros such as `PULLBYTE()`, `NEEDBITS()`, `ROOM()`, `LOAD()`, and `RESTORE()` implement the bit-buffer and callback control mechanics.

## Control Flow, State, and Persistence
Initialization validates version, window size, callbacks, and caller-supplied window storage, then allocates inflate state. `inflateBack()` resets to `TYPE`, decodes stored/fixed/dynamic deflate blocks, builds dynamic Huffman tables, optionally delegates literal/length decoding to `inflate_fast()`, writes full windows through `out()`, and returns unused input. State persists only in the z_stream state and caller window for the duration of the session.

## Dependencies and Integration Points
It includes `zutil.h`, `inftrees.h`, `inflate.h`, and `inffast.h`. It shares optimized decoding with normal `inflate.c`, but expects raw deflate blocks and a caller-managed I/O model.

## Risks and Test Signals
Risks include callback starvation being reported as `Z_BUF_ERROR`, invalid distance checks against the caller window, dynamic table errors, and linking both callback and normal inflate variants with assembler replacements. Tests should cover stored, fixed, dynamic, malformed block types, out-callback failure, in-callback failure, and exact unused-input reporting.
<!-- END_FILE_RESEARCH: sources/compression/zlib/infback.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zlib/inffast.c -->
# sources/compression/zlib/inffast.c

## Purpose
`inffast.c` provides the hot literal/length/distance decode loop used by `inflate()` and `inflateBack()` when enough input and output are available.

## Important APIs, Types, and Functions
The single internal API is `inflate_fast(z_streamp strm, unsigned start)`. It consumes `struct inflate_state` fields for bit accumulator, Huffman tables, sliding window, distance sanity, and mode updates. It works with `code` table entries from `inftrees.c`.

## Control Flow, State, and Persistence
On entry, callers guarantee `state->mode == LEN`, at least six input bytes, at least 258 output bytes, and fewer than eight buffered bits. The loop decodes literals directly, resolves length and distance table links, copies matches from output or the sliding window, and exits on block end, invalid code, invalid distance, insufficient input, or insufficient output. It writes updated stream pointers, remaining availability, bit state, and mode back to `strm`/`state`.

## Dependencies and Integration Points
It includes `zutil.h`, `inftrees.h`, `inflate.h`, and `inffast.h`. `ASMINF` can replace this C body with assembler. The routine is performance-critical for normal zlib inflate.

## Risks and Test Signals
Risks concentrate around pointer bounds, overlapping match copies, window wraparound, distance-too-far policy, and precondition violations by callers. Strong tests are sanitizer-backed decompression of malformed streams, boundary-sized output buffers, wraparound windows, fixed and dynamic tables, and strict versus permissive invalid-distance builds.
<!-- END_FILE_RESEARCH: sources/compression/zlib/inffast.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zlib/inffast.h -->
# sources/compression/zlib/inffast.h

## Purpose
`inffast.h` is the private declaration header for the fast inflate decoder.

## Important APIs, Types, and Functions
It declares `void ZLIB_INTERNAL inflate_fast(z_streamp strm, unsigned start);`. The warning comment explicitly states that applications must not include it; public consumers should use `zlib.h`.

## Control Flow, State, and Persistence
The header has no runtime state. Its contract is implicit in `inffast.c`: callers provide a valid inflate stream in `LEN` mode with enough input/output headroom and an initialized table/window state.

## Dependencies and Integration Points
It relies on prior inclusion of zlib internal types and the `ZLIB_INTERNAL` visibility macro. It is included by `inflate.c` and `infback.c`.

## Risks and Test Signals
Risk is limited but important: signature drift would break both inflater frontends or assembler replacements. Compile tests across normal C and `ASMINF` configurations are the primary signal.
<!-- END_FILE_RESEARCH: sources/compression/zlib/inffast.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zlib/inffixed.h -->
# sources/compression/zlib/inffixed.h

## Purpose
`inffixed.h` contains the generated static decode tables for fixed Huffman deflate blocks.

## Important APIs, Types, and Functions
It defines `static const code lenfix[512]` and, later in the file, the fixed distance table used by `inflate_fixed()`. Entries encode operation, bit count, and value in the `code` format from `inftrees.h`.

## Control Flow, State, and Persistence
There is no active control flow. Including this header embeds immutable lookup tables into `inftrees.c` when `BUILDFIXED` is not used. The tables are process-static and shared by all inflate streams.

## Dependencies and Integration Points
It depends on `code` being defined before inclusion. `inftrees.c` includes it and points `struct inflate_state` at these tables for fixed-code blocks. The file is generated by the `MAKEFIXED` mode in `inftrees.c`.

## Risks and Test Signals
Risks include generated-table corruption, mismatch with the fixed-code rules, or stale regeneration after `code` semantics change. Test signals are successful fixed-Huffman decompression, `MAKEFIXED` reproducing the table, and table coverage under inflate branch/coverage tests.
<!-- END_FILE_RESEARCH: sources/compression/zlib/inffixed.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zlib/inflate.c -->
# sources/compression/zlib/inflate.c

## Purpose
`inflate.c` is zlib's main decompression engine for zlib-wrapped, gzip-wrapped, and raw deflate streams. It owns stream initialization, reset, header/trailer processing, block decoding, dictionaries, sync recovery, state copying, and validation knobs.

## Important APIs, Types, and Functions
Public APIs include `inflateInit_()`, `inflateInit2_()`, `inflateResetKeep()`, `inflateReset()`, `inflateReset2()`, `inflatePrime()`, `inflate()`, `inflateEnd()`, `inflateGetDictionary()`, `inflateSetDictionary()`, `inflateGetHeader()`, `inflateSync()`, `inflateSyncPoint()`, `inflateCopy()`, `inflateUndermine()`, `inflateValidate()`, `inflateMark()`, and `inflateCodesUsed()`. Key internals are `inflateStateCheck()`, `updatewindow()`, `syncsearch()`, and the bit macros.

## Control Flow, State, and Persistence
`inflate()` is a resumable state machine over modes from `HEAD` through `DONE` or error modes. It parses zlib/gzip/raw headers, handles optional gzip fields, validates dictionaries, decodes stored/fixed/dynamic blocks, builds Huffman tables with `inflate_table()`, uses `inflate_fast()` for large buffers, validates checksums and gzip length trailers, updates the sliding window on return, and reports `Z_BUF_ERROR` when no progress is possible. Persistent state lives in `struct inflate_state`, including mode, wrapper flags, checks, window, bit accumulator, tables, and match-copy bookkeeping.

## Dependencies and Integration Points
It includes `zutil.h`, `inftrees.h`, `inflate.h`, and `inffast.h`, and uses `adler32()`, `crc32()`, allocator hooks, and zlib public stream fields. It is the core implementation behind `inflate()` users and `gzread.c`.

## Risks and Test Signals
Risks include malformed header handling, partial-call resumability, dictionary ID validation, distance/window bounds, dynamic table oversubscription, checksum/length trailer mismatches, and memory allocation failure for the window. Tests should include split-input streaming, every flush mode, zlib/gzip/raw wrappers, gzip optional fields and header CRC, preset dictionaries, sync recovery, `inflateCopy()`, and sanitizer/fuzzer malformed inputs.
<!-- END_FILE_RESEARCH: sources/compression/zlib/inflate.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zlib/inflate.h -->
# sources/compression/zlib/inflate.h

## Purpose
`inflate.h` defines the private state model and mode enumeration for zlib decompression.

## Important APIs, Types, and Functions
It conditionally enables gzip support with `GUNZIP`, defines `inflate_mode` values such as `HEAD`, `TYPE`, `TABLE`, `LEN`, `MATCH`, `CHECK`, `DONE`, `BAD`, and `SYNC`, and defines `struct inflate_state`. The state includes wrapper flags, checksum counters, gzip header pointer, sliding window metadata, bit accumulator, dynamic Huffman work arrays, decode table storage, distance sanity flag, and progress markers.

## Control Flow, State, and Persistence
The header documents the inflate state transitions from wrapper headers through block decoding and trailer validation. Runtime persistence is entirely in `struct inflate_state`, which survives across `inflate()` calls until reset or `inflateEnd()`.

## Dependencies and Integration Points
It depends on `code` and `ENOUGH` from `inftrees.h` and zlib stream types from internal/public headers. `inflate.c`, `infback.c`, and `inffast.c` all consume this exact layout.

## Risks and Test Signals
Risks include mode-order assumptions in `inflateStateCheck()`, table-size coupling to `inftrees.h`, and accidental external use despite private warnings. Compile coverage plus streaming tests that suspend/resume in many modes are the key signals.
<!-- END_FILE_RESEARCH: sources/compression/zlib/inflate.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zlib/inftrees.c -->
# sources/compression/zlib/inftrees.c

## Purpose
`inftrees.c` builds canonical Huffman decode tables for deflate code-length, literal/length, and distance alphabets. It also provides fixed-code table selection or generation.

## Important APIs, Types, and Functions
The main internal API is `inflate_table(codetype type, unsigned short *lens, unsigned codes, code **table, unsigned *bits, unsigned short *work)`. It also defines `inflate_fixed(struct inflate_state *state)`, optional `buildtables()` under `BUILDFIXED`, and a `MAKEFIXED` generator main. Static base/extra arrays encode deflate length and distance semantics.

## Control Flow, State, and Persistence
`inflate_table()` counts code lengths, finds min/max/root widths, rejects over-subscribed or invalid incomplete codes, sorts symbols by length, fills root and sub-tables with replicated entries, links sub-tables, and advances the caller's table pointer. `inflate_fixed()` either points at generated `inffixed.h` tables or builds them once through `z_once()`.

## Dependencies and Integration Points
It includes `zutil.h`, `inftrees.h`, and `inflate.h`. `inflate.c` and `infback.c` call it while decoding dynamic blocks, and fixed-block decoding depends on its fixed-table setup.

## Risks and Test Signals
Risks include table-space overflow if root bits or `ENOUGH_*` constants drift, accepting invalid code sets, and thread-safety caveats with `BUILDFIXED` when atomics are unavailable. Tests should cover over-subscribed tables, missing end-of-block codes, incomplete distance sets, all fixed blocks, and dynamic-code fuzzing.
<!-- END_FILE_RESEARCH: sources/compression/zlib/inftrees.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zlib/inftrees.h -->
# sources/compression/zlib/inftrees.h

## Purpose
`inftrees.h` declares the private Huffman decode-table representation and table-building functions used by zlib inflate internals.

## Important APIs, Types, and Functions
It defines the `code` struct with `op`, `bits`, and `val`, the operation-value encoding, `ENOUGH_LENS`, `ENOUGH_DISTS`, `ENOUGH`, `codetype` values `CODES`, `LENS`, and `DISTS`, plus declarations for `inflate_table()` and `inflate_fixed()`.

## Control Flow, State, and Persistence
The header has no runtime flow. Its constants define the maximum persistent table storage embedded in `struct inflate_state`, and its operation encoding drives the decode loops in `inflate.c`, `infback.c`, and `inffast.c`.

## Dependencies and Integration Points
It is included by all inflate implementation files. The comments explicitly tie `ENOUGH_*` to the root-bit choices used in `inflate_table()` calls, so changes require recalculation with `examples/enough.c`.

## Risks and Test Signals
Risks include changing table root sizes without updating `ENOUGH_*`, misinterpreting `op` bits, and exposing private internals to applications. Compile-time size checks are absent, so runtime table-building coverage and dynamic-block fuzzing are important signals.
<!-- END_FILE_RESEARCH: sources/compression/zlib/inftrees.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zlib/os400/make.sh -->
# sources/compression/zlib/os400/make.sh

## Purpose
`os400/make.sh` is the IBM i / OS/400 build script for zlib, used where standard `make` is not assumed. It creates library objects, copies headers/docs, compiles modules, and builds static/dynamic binding directories and a service program.

## Important APIs, Types, and Functions
Shell procedures include `action_needed()`, `make_module()`, `db2_name()`, and `copy_hfile()`. Tunable variables include `TARGETLIB`, `STATBNDDIR`, `DYNBNDDIR`, `SRVPGM`, `IFSDIR`, `TGTCCSID`, `DEBUG`, `OPTIMIZE`, `OUTPUT`, and `TGTRLS`.

## Control Flow, State, and Persistence
The script resolves `TOPDIR`, extracts `VERSION` from `treebuild.xml`, creates OS/400 library/source-file objects, copies documentation and headers with target CCSID conversion, installs RPG headers, generates and compiles `os400.c`, compiles all XML-listed C sources into modules, rebuilds binding directories when needed, copies binder source, creates the service program, duplicates a versioned backup, and updates dynamic bindings. Persistent outputs are OS/400 library members, IFS include symlinks, modules, binding directories, and service programs.

## Dependencies and Integration Points
It depends on IBM i commands such as `CRTLIB`, `CRTSRCPF`, `CPY`, `CHGPFM`, `CRTCMOD`, `CRTBNDDIR`, `ADDBNDDIRE`, `CRTSRVPGM`, `CRTDUPOBJ`, and `system`, plus `treebuild.xml`.

## Risks and Test Signals
Risks include shell quoting in generated commands, stale dependency detection from XML/header timestamps, CCSID conversion issues, DB2 name truncation collisions, and accidental rebuild/link churn. Test signals are successful clean and incremental OS/400 builds, correct exported service program, valid include symlinks, and module recompilation when headers change.
<!-- END_FILE_RESEARCH: sources/compression/zlib/os400/make.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zlib/test/CMakeLists.txt -->
# sources/compression/zlib/test/CMakeLists.txt

## Purpose
`test/CMakeLists.txt` defines zlib's CMake test executables and installed-package integration tests.

## Important APIs, Types, and Functions
It defines `ZLIB_findTestEnv(testName)` to prepend the built shared library directory to `PATH` on Windows-like platforms. It creates shared and static `example`, `minigzip`, optional 64-bit examples, optional `infcover` coverage tests, install tests, `find_package()` tests, and `add_subdirectory()` tests using generated CMake projects.

## Control Flow, State, and Persistence
The script conditionally adds targets based on `ZLIB_BUILD_SHARED`, `ZLIB_BUILD_STATIC`, `HAVE_OFF64_T`, compiler ID, coverage tool availability, and `ZLIB_INSTALL`. Install tests use CTest fixtures so configure/build checks depend on the install step. Generated test projects are written with `configure_file()` under the binary tree.

## Dependencies and Integration Points
It depends on imported targets `ZLIB::ZLIB` and `ZLIB::ZLIBSTATIC`, CTest, CMake generator expressions, compiler variables, and template files in the same test directory. It validates both build-tree and install-tree consumption paths.

## Risks and Test Signals
Risks include environment setup for shared libraries on Windows, fixture dependency mistakes, coverage flag side effects, generator/platform quoting, and conditional tests passing vacuously when only one library flavor is built. Strong signals are successful CTest runs for shared/static examples, coverage summary when available, install fixture completion, and expected failure for wrong-component or incomplete no-component package tests.
<!-- END_FILE_RESEARCH: sources/compression/zlib/test/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zlib/test/add_subdirectory_exclude_test.cmake.in -->
# sources/compression/zlib/test/add_subdirectory_exclude_test.cmake.in

## Purpose
This CMake template verifies that zlib can be consumed via `add_subdirectory(... EXCLUDE_FROM_ALL)` while still exposing usable shared and static targets.

## Important APIs, Types, and Functions
It sets project metadata, disables `ZLIB_BUILD_TESTING`, mirrors configured `ZLIB_BUILD_SHARED` and `ZLIB_BUILD_STATIC`, calls `add_subdirectory(@zlib_SOURCE_DIR@ ... EXCLUDE_FROM_ALL)`, and builds `test_example` and/or `test_example_static` linked to `ZLIB::ZLIB` or `ZLIB::ZLIBSTATIC`.

## Control Flow, State, and Persistence
After substitution by `configure_file()`, CTest configures this as an isolated project. Shared example tests are skipped for `.dll` suffixes, while static examples always register when static builds are enabled. Build output lives only under the generated test build directory.

## Dependencies and Integration Points
It depends on the parent `test/CMakeLists.txt` install/add-subdirectory test fixture, CMake 3.12...3.31, the zlib source tree, and exported in-build CMake targets.

## Risks and Test Signals
Risks include accidental default target pollution despite `EXCLUDE_FROM_ALL`, target export drift, and platform-specific shared-library execution limitations. Passing configure and build tests prove the subdirectory integration path works for enabled library flavors.
<!-- END_FILE_RESEARCH: sources/compression/zlib/test/add_subdirectory_exclude_test.cmake.in -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zlib/test/add_subdirectory_test.cmake.in -->
# sources/compression/zlib/test/add_subdirectory_test.cmake.in

## Purpose
This CMake template verifies normal `add_subdirectory()` consumption of the zlib source tree from another project.

## Important APIs, Types, and Functions
It defines a small C project, sets `ZLIB_BUILD_TESTING` off, mirrors configured shared/static build options, calls `add_subdirectory(@zlib_SOURCE_DIR@ ${CMAKE_CURRENT_BINARY_DIR}/zlib)`, and conditionally builds example executables linked to `ZLIB::ZLIB` and `ZLIB::ZLIBSTATIC`.

## Control Flow, State, and Persistence
The parent test configures this template into a generated project, then runs CMake configure and build steps. Shared runtime tests are registered except on `.dll` suffix platforms; static runtime tests are registered whenever static builds are enabled.

## Dependencies and Integration Points
It integrates with `test/CMakeLists.txt`, CTest, the source-tree zlib CMake project, and target aliases exported by the subdirectory build.

## Risks and Test Signals
Risks include stale template substitutions, target alias changes, and the final `endif(@ZLIB_BUILD_STATIC)` substitution becoming malformed if the configured value is unexpected. Passing configure/build and example execution demonstrate that source embedding works without installation.
<!-- END_FILE_RESEARCH: sources/compression/zlib/test/add_subdirectory_test.cmake.in -->
