# Group Research: group_70_9front_sources_os_plan9_9front_sys_src_cmd_bzip2_lib_bzlib_private_h__fadc5d0bc882

Scope checked against `Docs/research_subset_a.md`: all files are under `sources/os/plan9/9front`, which is included in subset A. Each listed file was read completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/bzip2/lib/bzlib_private.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/bzip2/lib/bzlib_private.h

Purpose: Private libbzip2 header for the 9front bzip2 copy, marked as modified from the upstream bzip2 distribution mainly to split the library into smaller pieces.

Key points:
- Defines `BZ_VERSION` as `1.0.1, 23-June-2000`.
- Provides internal assertion, verbose logging, allocation, CRC, randomization, compression-state, and decompression-state macros.
- Defines compression-side `EState`, including block sort arrays, bitstream output fields, CRCs, MTF/Huffman coding tables, selector arrays, and block metadata.
- Defines decompression-side `DState`, including resumable parser state, bitstream input buffer, BWT inverse structures for fast and small modes, CRC state, MTF tables, Huffman decode tables, and saved local variables for coroutine-style decompression.
- Declares internal compression, decompression, Huffman, CRC, allocation, and configuration functions.

Dependencies and interactions:
- Depends on public `bz_stream` and bzip2 typedefs from `bzlib.h`, plus platform typedefs from `os.h`.
- `compress.c`, `decompress.c`, `huffman.c`, `bzread.c`, `bzwrite.c`, and table files rely on these structs and macros.
- CRC macros use `BZ2_crc32Table` from `crctable.c`.
- Randomized block compatibility uses `BZ2_rNums` from `randtable.c`.

Research notes:
- This is the central internal ABI for the split bzip2 library. Changes here affect nearly every bzip2 translation unit.
- The decompressor keeps extensive save fields, which explains the macro-heavy parser in `decompress.c`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/bzip2/lib/bzlib_private.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/bzip2/lib/bzlib_stdio.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/bzip2/lib/bzlib_stdio.h

Purpose: Public stdio-oriented bzip2 API declarations for the split 9front bzip2 library.

Key points:
- Includes `<stdio.h>` and defines `BZ_MAX_UNUSED` as 5000.
- Uses opaque `typedef void BZFILE`.
- Declares zlib-like APIs: `BZ2_bzopen`, `BZ2_bzdopen`, `BZ2_bzread`, `BZ2_bzwrite`, `BZ2_bzflush`, `BZ2_bzclose`, and `BZ2_bzerror`.
- Declares higher-level stdio APIs: `BZ2_bzReadOpen`, `BZ2_bzRead`, `BZ2_bzReadGetUnused`, `BZ2_bzReadClose`, `BZ2_bzWriteOpen`, `BZ2_bzWrite`, `BZ2_bzWriteClose`, and `BZ2_bzWriteClose64`.

Dependencies and interactions:
- Consumed by `bzread.c`, `bzwrite.c`, and `bzzlib.c`.
- Relies on `BZ_EXTERN` and `BZ_API` macros from the public bzip2 header.
- The concrete `BZFILE` implementation is private in `bzlib_stdio_private.h`.

Research notes:
- This file is API surface, not implementation. It preserves upstream bzip2 compatibility while allowing the Plan 9 tree to compile the stdio wrapper separately.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/bzip2/lib/bzlib_stdio.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/bzip2/lib/bzlib_stdio_private.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/bzip2/lib/bzlib_stdio_private.h

Purpose: Private definitions for the stdio wrapper layer around libbzip2 streams.

Key points:
- Replaces silent internal assertion/logging macros from `bzlib_private.h` with stdio-aware versions.
- Defines `BZ_SETERR`, which writes errors both to the caller-provided `bzerror` pointer and to `bzFile.lastErr`.
- Defines concrete `bzFile` containing `FILE *handle`, a `BZ_MAX_UNUSED` buffer, writing/read mode, `bz_stream`, last error, and initialization status.
- Declares `bz_feof(FILE*)`.

Dependencies and interactions:
- Included by `bzread.c`, `bzwrite.c`, and `bzzlib.c`.
- Uses `FILE`, `fprintf`, and optionally `exit` for debug assertions.
- `bzstdio.c` supplies `bz_feof`.

Research notes:
- This header is the glue between the public opaque `BZFILE` handle and the underlying `bz_stream`.
- Error propagation is macro-based and assumes local variables named `bzerror` and `bzf`, so call sites must preserve that convention.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/bzip2/lib/bzlib_stdio_private.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/bzip2/lib/bzread.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/bzip2/lib/bzread.c

Purpose: Implements the high-level stdio read API for bzip2 streams.

Key points:
- `BZ2_bzReadOpen` validates parameters, allocates a `bzFile`, copies caller-provided unused bytes, initializes `BZ2_bzDecompressInit`, and primes `strm.next_in/avail_in`.
- `BZ2_bzRead` fills the input buffer from `FILE*`, calls `BZ2_bzDecompress`, handles `BZ_STREAM_END`, zero-length reads, I/O errors, and unexpected EOF.
- `BZ2_bzReadClose` ends the decompressor if initialized and frees the wrapper.
- `BZ2_bzReadGetUnused` returns unread bytes only after stream end.

Dependencies and interactions:
- Calls core decompressor entry points declared in `bzlib.h`.
- Uses `bz_feof` from `bzstdio.c`.
- Uses `BZ_SETERR` and `bzFile` from `bzlib_stdio_private.h`.

Research notes:
- Read-side behavior is streaming and incremental. It can return partial output at stream end and exposes unused compressed bytes for concatenated or framed consumers.
- The function treats reads from a write-mode `bzFile` as sequence errors.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/bzip2/lib/bzread.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/bzip2/lib/bzstdio.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/bzip2/lib/bzstdio.c

Purpose: Provides a portable EOF probe helper for the bzip2 stdio wrapper.

Key points:
- Defines `bz_feof(FILE *f)`.
- Reads one byte with `fgetc`.
- Returns true if EOF is reached.
- Otherwise pushes the byte back with `ungetc` and returns false.

Dependencies and interactions:
- Used by `bzread.c` to distinguish no buffered input from real file EOF.
- Includes `os.h`, `bzlib.h`, and `bzlib_private.h`.

Research notes:
- The helper deliberately avoids relying only on stdio EOF flags, which may not be set until a read has been attempted.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/bzip2/lib/bzstdio.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/bzip2/lib/bzversion.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/bzip2/lib/bzversion.c

Purpose: Implements the public libbzip2 version query.

Key points:
- `BZ2_bzlibVersion` returns `BZ_VERSION`.
- The file carries the same modified-upstream bzip2 notice and license text as the other split files.

Dependencies and interactions:
- Depends on `BZ_VERSION` from `bzlib_private.h`.
- Exposes a public API declared in `bzlib.h`.

Research notes:
- Minimal implementation; version identity is centralized in the private header.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/bzip2/lib/bzversion.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/bzip2/lib/bzwrite.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/bzip2/lib/bzwrite.c

Purpose: Implements the high-level stdio write API for bzip2 streams.

Key points:
- `BZ2_bzWriteOpen` validates file, block size, verbosity, and work factor, allocates `bzFile`, defaults work factor 0 to 30, and initializes compression.
- `BZ2_bzWrite` feeds input to `BZ2_bzCompress` with `BZ_RUN`, writing produced bytes to the wrapped `FILE*`.
- `BZ2_bzWriteClose` delegates to `BZ2_bzWriteClose64`.
- `BZ2_bzWriteClose64` optionally finishes compression with `BZ_FINISH`, flushes the file, returns low/high 32-bit byte counters, ends compression, and frees the wrapper.

Dependencies and interactions:
- Calls `BZ2_bzCompressInit`, `BZ2_bzCompress`, and `BZ2_bzCompressEnd`.
- Uses `bzFile` and `BZ_SETERR` from `bzlib_stdio_private.h`.
- Write buffering uses the same `BZ_MAX_UNUSED` fixed-size buffer as the read side.

Research notes:
- `abandon` skips finishing/flushing and is used by `bzzlib.c` when close after a write error fails.
- Sequence checks prevent writing to read-mode handles.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/bzip2/lib/bzwrite.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/bzip2/lib/bzzlib.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/bzip2/lib/bzzlib.c

Purpose: Implements zlib-style convenience functions on top of the higher-level bzip2 stdio API.

Key points:
- `bzopen_or_bzdopen` parses mode strings for read/write, block size digits, and small decompression mode.
- `BZ2_bzopen` opens by path or uses stdin/stdout when the path is empty or nil.
- `BZ2_bzdopen` wraps an existing file descriptor using `fdopen` unless strict ANSI disables it.
- `BZ2_bzread` returns byte count, 0 after stream end, or -1 on error.
- `BZ2_bzwrite` returns requested length on success or -1 on error.
- `BZ2_bzflush` is a no-op returning 0.
- `BZ2_bzclose` closes compression/decompression and then closes the underlying file except stdin/stdout.
- `BZ2_bzerror` maps last error codes to strings.

Dependencies and interactions:
- Built on `BZ2_bzReadOpen`, `BZ2_bzWriteOpen`, `BZ2_bzRead`, `BZ2_bzWrite`, and close functions.
- Uses `bzFile.lastErr` directly.
- Contains non-Plan-9 conditional binary-mode support for Windows-like targets.

Research notes:
- This is compatibility glue, explicitly marked as contributed zlib-compatibility code and not originally part of the core upstream library.
- `BZ2_bzerror` assumes non-null `b` and `errnum`; it is a thin compatibility layer rather than a defensive API.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/bzip2/lib/bzzlib.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/bzip2/lib/compress.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/bzip2/lib/compress.c

Purpose: Implements bzip2 compression back-end machinery other than block sorting.

Key points:
- Provides bitstream output helpers: `BZ2_bsInitWrite`, `bsFinishWrite`, `bsW`, `bsPutUInt32`, and `bsPutUChar`.
- `generateMTFValues` converts sorted block data into move-to-front values with run-length coding and symbol frequencies.
- `sendMTFValues` chooses 2 to 6 Huffman groups based on MTF size, iteratively improves code lengths, MTF-encodes selectors, writes mapping tables, selectors, code lengths, and encoded MTF data.
- Fast paths are unrolled for the common six-group, 50-symbol block segment case.
- `BZ2_compressBlock` finalizes block CRCs, emits stream headers/trailers, block magic, CRC, non-randomized flag, original pointer, MTF/Huffman payload, and final combined CRC.

Dependencies and interactions:
- Requires block sorting via `BZ2_blockSort`.
- Calls Huffman helpers from `huffman.c`.
- Uses CRC macros and `EState` fields from `bzlib_private.h`.
- Produces compressed bytes into `EState.zbits`, which overlays the second work array.

Research notes:
- Modern randomization is disabled on output, but the format bit is still emitted for compatibility.
- Storage aliasing among `arr1`, `arr2`, `ptr`, `block`, `mtfv`, and `zbits` is intentional and important for memory footprint.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/bzip2/lib/compress.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/bzip2/lib/crctable.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/bzip2/lib/crctable.c

Purpose: Defines the 256-entry CRC-32 lookup table used by bzip2.

Key points:
- `BZ2_crc32Table` contains the AUTODIN-II/Ethernet/FDDI style CRC table.
- The table is used by CRC update macros in `bzlib_private.h`.

Dependencies and interactions:
- Included in the bzip2 library build as global data.
- Compression and decompression update block and combined CRCs through this table.

Research notes:
- Static data only. Correctness depends on preserving exact values.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/bzip2/lib/crctable.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/bzip2/lib/decompress.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/bzip2/lib/decompress.c

Purpose: Implements bzip2 stream decompression parsing and block setup.

Key points:
- Uses macros `GET_BITS`, `GET_UCHAR`, `GET_BIT`, and `GET_MTF_VAL` to implement a resumable state machine over `DState.state`.
- Validates stream magic `BZh1` through `BZh9`, allocates either fast `tt` storage or small `ll16/ll4` storage.
- Parses block headers, block CRC, randomization flag, original pointer, mapping table, selector list, Huffman code lengths, and MTF/RLE data.
- Builds Huffman decode tables with `BZ2_hbCreateDecodeTables`.
- Reconstructs byte frequency tables and inverse BWT traversal structures.
- Handles both old randomized blocks and normal non-randomized blocks.
- Parses stream trailer and stored combined CRC, returning `BZ_STREAM_END`.

Dependencies and interactions:
- Uses `DState` and decompression macros from `bzlib_private.h`.
- Calls `BZ2_hbCreateDecodeTables` from `huffman.c`.
- Uses allocation callbacks via `BZALLOC`.
- The output phase itself is coordinated with other decompression routines using `DState.state_out_*`, `tPos`, `k0`, and `nblock_used`.

Research notes:
- This file is designed for incremental input: when input is exhausted, it saves local parser state into `DState` and returns `BZ_OK`.
- It performs strong structural validation, returning data errors for impossible selectors, code lengths, MTF values, out-of-range original pointers, and block overflow.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/bzip2/lib/decompress.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/bzip2/lib/huffman.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/bzip2/lib/huffman.c

Purpose: Provides low-level Huffman code generation and decode table construction for bzip2.

Key points:
- `BZ2_hbMakeCodeLengths` builds Huffman code lengths from symbol frequencies using heap operations and retries with adjusted weights if lengths exceed `maxLen`.
- `BZ2_hbAssignCodes` assigns canonical Huffman codes by code length.
- `BZ2_hbCreateDecodeTables` builds `limit`, `base`, and `perm` decode tables from code lengths.

Dependencies and interactions:
- Used by `compress.c` to generate code lengths and assign canonical codes.
- Used by `decompress.c` to build decode tables.
- Uses constants and assertions from `bzlib_private.h`.

Research notes:
- Heap and weight macros pack frequency and depth into integer weights.
- The implementation assumes bzip2’s maximum alphabet and code length constraints.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/bzip2/lib/huffman.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/bzip2/lib/os.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/bzip2/lib/os.h

Purpose: Platform-selection and base typedef header for the bzip2 library.

Key points:
- Defaults to `BZ_UNIX 1`, with conditional switches for `_WIN32` and `PLAN9`.
- Includes `unix.h`, `lccwin32.h`, or `plan9.h` according to selected platform.
- Defines `NORETURN` for GCC.
- Defines core bzip2 typedefs: `Char`, `Bool`, `UChar`, `Int32`, `UInt32`, `Int16`, `UInt16`, `IntNative`.
- Defines `True` and `False`.

Dependencies and interactions:
- Included by all bzip2 library C files.
- `PLAN9` builds include `plan9.h`; otherwise the default Unix header is used.

Research notes:
- Although this lives in the Plan 9 tree, it keeps upstream multi-platform structure.
- Type size assumptions are centralized here.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/bzip2/lib/os.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/bzip2/lib/plan9.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/bzip2/lib/plan9.h

Purpose: Plan 9 platform include shim for bzip2.

Key points:
- Includes `<u.h>`, `<libc.h>`, and `<ctype.h>`.
- Maps `exit(x)` to `exits((x) ? "whoops" : nil)`.
- Defines `size_t` as `ulong`.

Dependencies and interactions:
- Included via `os.h` when `PLAN9` is defined.

Research notes:
- This is a minimal compatibility layer to let upstream-style C code compile against Plan 9 libc conventions.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/bzip2/lib/plan9.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/bzip2/lib/randtable.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/bzip2/lib/randtable.c

Purpose: Defines the 512-entry randomization table used for old bzip2 randomized blocks.

Key points:
- `BZ2_rNums[512]` is static integer data.
- Compression no longer emits randomized blocks, but decompression still supports them for backward compatibility.

Dependencies and interactions:
- Randomization macros in `bzlib_private.h` reference this table.
- `decompress.c` uses the randomization mask path when a block’s randomization bit is set.

Research notes:
- Static compatibility data. Exact values must be preserved.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/bzip2/lib/randtable.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/bzip2/lib/unix.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/bzip2/lib/unix.h

Purpose: Generic Unix platform include shim for bzip2.

Key points:
- Includes standard C/POSIX-ish headers: `stdio.h`, `stdlib.h`, `string.h`, `signal.h`, `math.h`, `errno.h`, and `ctype.h`.

Dependencies and interactions:
- Included by `os.h` when `BZ_UNIX` is selected.

Research notes:
- Minimal platform header. It provides declarations expected by the upstream bzip2 source.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/bzip2/lib/unix.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cal.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/cal.c

Purpose: Plan 9 `cal` command for printing a month or full year calendar.

Key points:
- Supports `-s 1..7` to choose the starting weekday.
- With no arguments, prints the current month. With one argument, interprets a month name/number as current-year month or otherwise a year. With two arguments, prints month and year.
- Uses `Biobuf` for output.
- `number` maps month names and abbreviations to negative month numbers and parses numeric strings.
- `cal` lays out month text into a fixed buffer, handling leap years and the 1752 calendar change.
- `jan1` computes weekday for January 1 with Julian/Gregorian adjustment.
- `curmo` and `curyr` use Plan 9 `localtime`.

Dependencies and interactions:
- Uses Plan 9 headers `<u.h>`, `<libc.h>`, and `<bio.h>`.
- Standalone command, no repository-local helper files.

Research notes:
- Historical calendar behavior is embedded directly, including September 1752 shortened to 19 days and skipped dates handling.
- Output formatting is fixed-width and buffer-oriented rather than dynamically structured.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cal.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/calendar.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/calendar.c

Purpose: Plan 9 `calendar` command that scans calendar files for entries matching today, tomorrow, weekend extension days, or an optional future day.

Key points:
- Options: `-y` requires year matching, `-d` prints generated regexes, `-p days` adds a specific future day.
- Defaults to `/usr/$user/lib/calendar` when no files are supplied.
- Builds linked list of compiled regexes for date patterns.
- `dates` generates patterns for month-day, day-month, `every <weekday>`, and ordinal weekday forms like `the first monday`.
- Input lines are lowercased before regex matching, while original lines are printed.
- `emalloc` wraps allocation with fatal error handling.

Dependencies and interactions:
- Uses Plan 9 `<regexp.h>` and `<bio.h>`.
- Uses `getuser`, `time`, `localtime`, `open`, and `Brdline`.

Research notes:
- Matching is regex-based and intentionally supports abbreviated month/day names with optional suffixes.
- Weekend logic includes extra days when tomorrow lands on Saturday or Sunday.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/calendar.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/camv.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/camv.c

Purpose: Graphical camera viewer and control utility for a Plan 9 camera device directory.

Key points:
- Opens `<cam-device>/ctl` read-write and `<cam-device>/video` for image frames.
- Reads control lines into a linked list of `Control` records containing unit, control name, value, and optional info.
- Creates a draw window and centers frames read with `readimage`.
- Uses a video process that reopens the video stream on read failure.
- Handles resize events in a separate thread.
- Right mouse menu offers quit.
- Middle mouse menu lists controls, prompts for a new value with `enter`, writes quoted control update commands, then refreshes controls.

Dependencies and interactions:
- Uses Plan 9 thread, draw, mouse, keyboard, and bio libraries.
- Expects camera device files with `ctl` and `video` interfaces.
- Uses `quotefmtinstall` for quoted control writes.

Research notes:
- UI is simple but concurrent: draw locking is used around display updates and mouse menu interactions.
- `readctls` appends newly allocated controls after seeking the control stream, and `freectls` is used before refresh.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/camv.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cat.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/cat.c

Purpose: Minimal Plan 9 `cat` implementation.

Key points:
- `cat` copies from an input file descriptor to stdout using an `IOUNIT` stack buffer.
- Reports write or read errors with `sysfatal`.
- With no file arguments, reads stdin.
- With files, opens each read-only, copies, and closes it.

Dependencies and interactions:
- Uses Plan 9 `<u.h>` and `<libc.h>`.
- Standalone command.

Research notes:
- No options are supported.
- Errors are fatal and stop processing immediately.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cat.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cb/cb.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/cb/cb.c

Purpose: Implements `cb`, a C source beautifier/formatter.

Key points:
- Options: `-j` joins continued lines, `-s` strict formatting, `-l width` adjusts line width and maximum indentation.
- `work` is the main lexical/state machine. It tracks braces, parentheses, keywords, declarations, `if/else`, `do/while`, struct initializers, comments, strings, preprocessor lines, operators, and line splitting.
- Handles C and C++-style comments.
- Uses keyword and operator tables from `cb.h`.
- Uses character classification macros from `cbtype.h`.
- Maintains indentation stack `ind`, temporary lookahead buffer `temp`, output line buffer `string`, and state flags such as `keyflag`, `opflag`, `dolevel`, `structlev`, `paren`, and `question`.
- `getnext` performs lookahead across whitespace, comments, and preprocessor lines.
- `ptabs` folds deeply indented code after `maxtabs`.

Dependencies and interactions:
- Uses Plan 9 `<bio.h>` for input/output.
- Includes local `cb.h` and `cbtype.h`; links with `cbtype.c` for `_cbtype_`.
- Reads stdin or named files and writes formatted output to stdout.

Research notes:
- The formatter is not a parser; it is a token-aware state machine with extensive heuristics.
- Static fixed-size buffers drive behavior and impose limits on line and lookahead size.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cb/cb.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cb/cb.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/cb/cb.h

Purpose: Shared constants, tables, globals, macros, and prototypes for the `cb` C beautifier.

Key points:
- Defines keyword classes, operator spacing classes, boolean constants, parser-state constants, and buffer/stack sizes.
- Defines indentation stack structure `struct indent`.
- Defines `key[]` table for C keywords and declaration words.
- Defines `op[]` table for operators and spacing behavior.
- Declares and initializes global formatter state.
- Provides macros for output, indentation bumping, and whitespace consumption.
- Declares all helper functions implemented in `cb.c`.

Dependencies and interactions:
- Included by `cb.c`.
- Depends on `Biobuf` type from `<bio.h>` being included before it.

Research notes:
- This header contains definitions, not just declarations, so it is meant for a small single-program build rather than reuse across many translation units.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cb/cb.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cb/cbtype.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/cb/cbtype.c

Purpose: Defines the ASCII character classification table for `cb`.

Key points:
- `_cbtype_[]` maps characters to bit flags for uppercase, lowercase, numeric, space, punctuation, control, hex digit, and operator.
- Table is sized for ASCII plus leading sentinel offset behavior.

Dependencies and interactions:
- Included through `cbtype.h` macros such as `isop`, `isalpha`, `isdigit`, and `isspace`.
- Used by `cb.c` instead of libc ctype functions.

Research notes:
- This local ctype table gives `cb` deterministic ASCII classification independent of locale or libc behavior.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cb/cbtype.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cb/cbtype.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/cb/cbtype.h

Purpose: Declares `_cbtype_` and defines character classification macros for `cb`.

Key points:
- Defines bit flags `_U`, `_L`, `_N`, `_S`, `_P`, `_C`, `_X`, and `_O`.
- Defines macros for `isop`, `isalpha`, `isdigit`, `isspace`, `ispunct`, `isalnum`, and related functions.
- Defines simple ASCII `toupper`, `tolower`, and `toascii`.

Dependencies and interactions:
- Included by `cb.c` and `cbtype.c`.
- Requires `_cbtype_` from `cbtype.c`.

Research notes:
- Macros index `(_cbtype_+1)[c]`, so callers must pass valid ASCII-range values.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cb/cbtype.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cc/acid.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/cc/acid.c

Purpose: Emits Acid debugger type and variable descriptions from the C compiler front end.

Key points:
- `amap` maps C identifiers that collide with Acid keywords to `$`-prefixed Acid names.
- `acidsue` finds the symbol naming a struct/union/enum type.
- `acidfun` finds the symbol for a function type.
- `acidinit` maps compiler type codes to Acid format characters, adjusting for target `int` and pointer widths.
- `acidmember` emits aggregate member descriptions or printer code.
- `acidtype` emits `sizeof`, `aggr`, and `defn` blocks for structs/unions when debug flag `a` is enabled; with debug `s`, emits assembler-style member offset defines.
- `acidvar` emits Acid `complex` declarations for variables whose effective type is a struct/union.

Dependencies and interactions:
- Uses compiler globals from `cc.h`, including `hash`, `types`, `debug`, `outbuf`, `iostack`, and `thisfn`.
- Called from declaration code in `dcl.c`.

Research notes:
- Acid output is debug side-channel behavior controlled by compiler debug flags.
- The implementation scans global symbol hash tables, so it is tightly coupled to the compiler symbol model.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cc/acid.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cc/bits.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/cc/bits.c

Purpose: Small bitset operations for compiler analysis state.

Key points:
- Implements `bor`, `band`, `bany`, `beq`, `bnum`, `blsh`, and `bset` over `Bits`.
- `Bits` is an array of `BITS` unsigned long words.
- `bnum` returns the index of the first set bit using `bitno`, and diagnoses empty input.

Dependencies and interactions:
- Uses `Bits`, `BITS`, `zbits`, `diag`, and `bitno` from `cc.h`.
- Used by format checking and other compiler analyses.

Research notes:
- `bnot` is commented out but still declared in `cc.h`, indicating historical or conditionally unused functionality.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cc/bits.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cc/cc.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/cc/cc.h

Purpose: Central shared header for the Plan 9 C compiler front end.

Key points:
- Includes Plan 9 system headers, `compat.h`, and links against `../cc/cc.a$O`.
- Defines core structs: `Node`, `Sym`, `Decl`, `Type`, `Io`, `Hist`, `Term`, `Bits`, `Spec`, `Funct`, and `Init`.
- Defines AST operation enum `O*`, type enum `T*`, declaration class enum `C*`, type qualifier/garbage flags `G*`, and bit masks for type/class combinations.
- Declares compiler-wide globals for symbol tables, type tables, parser state, include stack, debug flags, output buffers, offsets, declaration stack, and target settings.
- Declares front-end APIs grouped by parser, lexer, macro handling, declarations, semantic analysis, constant folding, function overloading, tree utilities, Acid output, pickle output, bitsets, pragma checks, code generation hooks, 64-bit lowering, and machine capability checks.
- Defines custom format checker pragmas for compiler diagnostics.

Dependencies and interactions:
- Included by all files in `cmd/cc`.
- Machine-specific compilers provide code generation hooks such as `codgen`, `gextern`, `align`, `maxround`, and `machcap`.
- Parser tokens come from generated yacc output for `cc.y`.

Research notes:
- This is the front-end contract between parser, semantic analysis, declarations, diagnostics, and target back ends.
- Many globals are declared through `EXTERN`, making inclusion context important.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cc/cc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cc/cc.y -->
# File Research: sources/os/plan9/9front/sys/src/cmd/cc/cc.y

Purpose: Yacc grammar for the Plan 9 C compiler front end.

Key points:
- Defines semantic value union for AST nodes, symbols, types, specs, strings, floats, and integers.
- Declares tokens for C keywords, constants, strings, operators, type names, qualifiers, Plan 9 extensions, and varargs.
- Parses external declarations, function definitions, automatic declarations, parameter declarations, struct/union fields, abstract declarators, initializers, labels, statements, expressions, casts, calls, member access, strings, aggregate bodies, enum declarations, and type/class/qualifier lists.
- Builds AST nodes using `new`.
- Uses declaration helpers such as `dodecl`, `doinit`, `markdcl`, `revertdcl`, `argmark`, `fndecls`, `dotag`, and `doenum`.
- Supports extensions including case ranges, compound literals/constructors, `used`, `set`, `signof`, unnamed parameters, and `...`.

Dependencies and interactions:
- Includes `cc.h`.
- Consumes lexer tokens from the compiler lexer.
- Produces trees consumed by semantic analysis in `com.c` and declarations in `dcl.c`.
- Function definitions call `codgen` unless Acid/pickle debug modes suppress code generation.

Research notes:
- The grammar encodes both syntax and early semantic actions, especially declaration scoping and type construction.
- Function bodies are wrapped with declaration-stack marks so local symbols can be reverted and unused diagnostics emitted.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cc/cc.y -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cc/com.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/cc/com.c

Purpose: Performs semantic type checking, expression rewriting, comma hoisting, simplification, constant folding, and comparison diagnostics.

Key points:
- `complex` is the main pipeline: type complexing with `tcom`, comma normalization, rewrite simplification with `ccom`, constant/address analysis via `acom`, and target lowering via `xcom`.
- `tcomo` handles type checking and type assignment for assignments, arithmetic, shifts, comparisons, logical operators, casts, return, function calls, names, strings, address/deref, dot access, `sizeof`, `signof`, and constructors.
- Inserts casts for assignment, return, arguments, array/function-to-pointer conversion, and promotions.
- Checks lvalues, void/incomplete types, pointer arithmetic, function prototypes, argument count/type, divide by zero, invalid shifts, address of bitfield/register, and undeclared functions/names.
- `tcoma` checks function argument lists against prototypes.
- `tcomd` resolves struct/union member access.
- `tcomx` checks struct constructor initializers.
- Comma handling hoists comma operators while preserving short-circuit and conditional semantics.
- `ccom` rewrites no-op casts, address/deref pairs, constant conditionals, arithmetic identities, zero checks, commutative constant folding, and constant expressions.
- `compar` warns about useless or misleading integer comparisons based on inferred type ranges.

Dependencies and interactions:
- Uses type compatibility tables and helper functions declared in `cc.h`.
- Calls `dpcheck` for format-string checking.
- Relies on machine hooks such as `machcap`, `xcom`, and constant conversion helpers.
- Produces trees suitable for code generation.

Research notes:
- This is the central semantic pass for expressions.
- It intentionally includes warnings for C pitfalls such as misleading unsigned comparisons and 32-bit complement casts extended to 64 bits.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cc/com.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cc/com64.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/cc/com64.c

Purpose: Rewrites 64-bit integer operations into runtime helper calls on targets that cannot directly implement them.

Key points:
- Declares global `Node*` handles for helper functions such as `_addv`, `_subv`, `_mulv`, `_divv`, `_modv`, shifts, bitwise operations, comparisons, conversions, increments/decrements, and assignment operations.
- `com64init` initializes helper nodes and conversion type codes.
- `com64` detects `vlong`/`uvlong` operands or result types and rewrites operations into `OFUNC` calls unless `machcap` says the target can handle them.
- Handles boolean contexts by calling `_testv`.
- Handles relational operators with signed/unsigned helper variants.
- Handles casts between vlong and smaller integer, pointer, float, and double types.
- Assignment operators are lowered either to specialized mixed vlong/double helpers or the generic `_vasop`.
- `bool64` rewrites vlong expressions in boolean contexts.
- Provides machine-independent conversion helpers `convvtof`, `convftov`, `convftox`, and `convvtox`.

Dependencies and interactions:
- Uses compiler AST constructors, type tables, `machcap`, and `mixedasop` from the front end.
- Runtime helper symbols are marked with `SIGINTERN`.
- Called by target-independent or target-specific lowering paths.

Research notes:
- The file describes itself as common to “64-bit simulating” machines.
- Some conversion comments are marked `BOTCH`, indicating pragmatic rather than fully precise host-independent conversion behavior.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cc/com64.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cc/compat.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/cc/compat.c

Purpose: Includes shared compiler compatibility support.

Key points:
- Includes `cc.h`.
- Includes `"compat"` without an extension, relying on a repository/build-provided compatibility implementation file.

Dependencies and interactions:
- Uses declarations from `compat.h` via `cc.h`.
- Build system must provide the included `compat` file in the include path or current directory.

Research notes:
- This is a two-line include wrapper, not substantive implementation by itself.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cc/compat.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cc/compat.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/cc/compat.h

Purpose: Declares OS compatibility helpers shared by compilers, linkers, and assemblers.

Key points:
- Defines system type bits: `Plan9`, `Unix`, and `Windows`.
- Declares wrappers for system-type detection, path separator, file access/creation, working directory, exec, dup, fork, pipe, and wait.
- Declares allocator helpers `alloc` and `allocn`.
- Uses `EXTERN` unless already defined.

Dependencies and interactions:
- Included by `cc.h`.
- Implementations are expected from the included compatibility source used by `compat.c`.

Research notes:
- Provides a portability abstraction for the Plan 9 compiler toolchain code.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cc/compat.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cc/dcl.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/cc/dcl.c

Purpose: Implements declaration processing, type construction, initialization handling, struct/union layout, prototypes, scoped symbol restoration, enum handling, type signatures, and automatic initializer zeroing.

Key points:
- `dodecl` walks declarator ASTs to construct arrays, pointers, functions, bitfields, and named declarations.
- `mkstatic` maps block-local statics to unique `$block` symbols.
- `tcopy` copies typedef chains where incomplete arrays need variable-specific width.
- `doinit`, `init1`, `peekinit`, and `nextinit` process scalar, array, string, struct, union, bitfield, and designated initializers.
- Static initializers require constants or address-plus-constant forms and emit data with `gextern`.
- Automatic initializers produce assignment trees, with `contig` adding zeroing code for uninitialized gaps.
- `sualign` lays out structs and unions, including bitfield packing and target alignment hooks.
- `markdcl` and `revertdcl` implement declaration-scope stack management, including unused local/parameter warnings, volatile-use preservation, tag restoration, and label diagnostics.
- `fnproto`, `anyproto`, and `fnproto1` construct and validate function prototype type lists.
- `walkparam`, `argmark`, `fndecls`, `adecl`, `pdecl`, `xdecl`, `edecl`, and `tmerge` handle parameter, auto, external, struct field, and function declarations.
- `sametype` and `rsametype` compare type chains, with special handling for functions, arrays, structs/unions, incomplete tags, and void pointers.
- `signature` and `sign` compute type hashes for `signof`/symbol signatures.
- `dotag`, `dcllabel`, `paramconv`, and `doenum` manage tags, labels, parameter promotions, and enum constants.

Dependencies and interactions:
- Includes `cc.h`.
- Calls expression analysis in `complex`, Acid output in `acidvar/acidtype`, pickle output in `pickletype`, and codegen/data hooks such as `gextern`, `align`, `maxround`, and `exreg`.
- Uses type tables and compatibility predicates from other compiler front-end files.

Research notes:
- This is the main declaration/type system implementation for the compiler.
- Initialization code is particularly broad, supporting Plan 9 extensions such as designated initializers while maintaining old-style C behavior.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cc/dcl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cc/dpchk.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/cc/dpchk.c

Purpose: Implements compiler pragma handling for vararg format checking, packing, floating-point rounding, profiling, and incomplete struct/union declarations.

Key points:
- Maintains format flag classification in `flagbits` and format/type prototype lists `Tprot` and `Tname`.
- `arginit` initializes default printf-style flag parsing and builtin integer format aliases.
- `pragvararg` parses `#pragma varargck` forms for argument position, format type, and ignored flags.
- `getflag` parses a format sequence, tracking ignored flags, width `*` arguments, length modifiers, and verb bits.
- `newprot` records accepted type/format flag combinations.
- `newname` records functions whose format argument should be checked.
- `dpcheck` detects registered vararg calls, finds the format argument, verifies it is a constant char string, and checks remaining arguments.
- `checkargs` compares parsed format directives against actual argument types and warns on mismatch, missing arguments, extra arguments, and invalid `*` width types.
- `pragpack`, `pragfpround`, and `pragprofile` parse on/off or numeric pragma state.
- `pragincomplete` marks struct/union types or tags as intentionally incomplete and supports `_on_`/`_off_` debug toggles.

Dependencies and interactions:
- Includes `cc.h` and generated `y.tab.h`.
- Uses parser/lexer helpers such as `getsym`, `getnsn`, `getnsc`, `getr`, `getc`, and `unget`.
- Uses type comparison helpers `sametype`, `beq`, `bor`, `blsh`, and `bset`.
- Called from semantic function-call checking in `com.c`.

Research notes:
- Format checking is driven by pragmas rather than hardcoded knowledge of every function.
- The format parser supports UTF/rune decoding via `chartorune` and `runetochar`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/cc/dpchk.c -->