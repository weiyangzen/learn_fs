# Group Research: group_1510_plan9_sources_os_plan9_plan9_sys_src_cmd_bzip2_lib_bzlib_private_h__66f9e795d2b1

Scope verified against `Docs/research_subset_a.md`: all files are under `sources/os/plan9/plan9`, which is included in subset A. Every listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/bzip2/lib/bzlib_private.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/bzip2/lib/bzlib_private.h

Private libbzip2 header for the Plan 9 split of bzip2 1.0.1. It defines shared constants, assertion/verbosity macros, allocator macros, CRC/randomisation helpers, compression/decompression states, and the internal `EState` and `DState` structs.

`EState` holds compression-side block buffers, block sorting aliases, run-length state, CRCs, bitstream writer state, selectors, Huffman lengths/codes, and MTF frequencies. `DState` holds decompression state-machine state, bitstream reader state, fast/small inverse BWT buffers, CRCs, selector/Huffman decode tables, MTF decode arrays, and saved locals for resumable decompression.

This file is central glue for all bzip2 library modules in this directory. It declares internal entry points such as `BZ2_blockSort`, `BZ2_compressBlock`, `BZ2_decompress`, Huffman helpers, default allocation, and config checks. The Plan 9 modification note says the original library was split into smaller pieces by Russ Cox.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/bzip2/lib/bzlib_private.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/bzip2/lib/bzlib_stdio.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/bzip2/lib/bzlib_stdio.h

Public stdio-oriented bzip2 API declarations for the split Plan 9 libbzip2 copy. It defines `BZ_MAX_UNUSED`, aliases `BZFILE` to an opaque `void`, and declares zlib-like high-level file APIs.

The API surface includes `BZ2_bzopen`, `BZ2_bzdopen`, `BZ2_bzread`, `BZ2_bzwrite`, `BZ2_bzflush`, `BZ2_bzclose`, and `BZ2_bzerror`, plus the lower-level `BZ2_bzReadOpen/Read/ReadClose/ReadGetUnused` and `BZ2_bzWriteOpen/Write/WriteClose/WriteClose64`.

It depends on `FILE` from stdio and on the public `BZ_EXTERN`/`BZ_API` macros from `bzlib.h`. The comments preserve upstream bzip2 changelog notes around zero-length flush/read behavior and parameter fixes.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/bzip2/lib/bzlib_stdio.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/bzip2/lib/bzlib_stdio_private.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/bzip2/lib/bzlib_stdio_private.h

Private header for the stdio wrapper layer. It overrides the no-op/private-header assertion and verbose-print macros so stdio code can report diagnostics through `stderr` and `BZ2_bz__AssertH__fail`.

It defines `BZ_SETERR`, which updates both the caller’s `bzerror` pointer and the `bzFile.lastErr` field when available. The internal `bzFile` struct stores the underlying `FILE*`, an unused/input-output staging buffer, mode flag, embedded `bz_stream`, last error, and initialization flag.

The only external helper declared here is `bz_feof(FILE*)`, implemented in `bzstdio.c`. This header is consumed by `bzread.c`, `bzwrite.c`, and `bzzlib.c`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/bzip2/lib/bzlib_stdio_private.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/bzip2/lib/bzread.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/bzip2/lib/bzread.c

Implements the lower-level stdio decompression API: `BZ2_bzReadOpen`, `BZ2_bzRead`, `BZ2_bzReadClose`, and `BZ2_bzReadGetUnused`.

`BZ2_bzReadOpen` validates parameters, copies any caller-supplied unused compressed bytes into the `bzFile` buffer, initializes `bz_stream`, then calls `BZ2_bzDecompressInit`. `BZ2_bzRead` fills `avail_out`, refills compressed input with `fread` when needed, repeatedly calls `BZ2_bzDecompress`, handles stream end, I/O errors, and unexpected EOF.

`BZ2_bzReadClose` ends decompression and frees the wrapper. `BZ2_bzReadGetUnused` is only valid after `BZ_STREAM_END` and returns remaining compressed bytes in the decompressor input buffer.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/bzip2/lib/bzread.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/bzip2/lib/bzstdio.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/bzip2/lib/bzstdio.c

Small stdio helper module for the split bzip2 library. It implements `bz_feof(FILE*)` by attempting `fgetc`, returning true on `EOF`, otherwise pushing the byte back with `ungetc`.

This is used by `bzread.c` to distinguish depleted input buffers from true file EOF. The implementation is intentionally simple and avoids relying directly on stdio `feof` state before attempting a read.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/bzip2/lib/bzstdio.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/bzip2/lib/bzversion.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/bzip2/lib/bzversion.c

Implements `BZ2_bzlibVersion`, returning the `BZ_VERSION` string from `bzlib_private.h`.

The file is part of the Plan 9 split of upstream `bzlib.c`; all meaningful behavior is the single version accessor.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/bzip2/lib/bzversion.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/bzip2/lib/bzwrite.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/bzip2/lib/bzwrite.c

Implements lower-level stdio compression APIs: `BZ2_bzWriteOpen`, `BZ2_bzWrite`, `BZ2_bzWriteClose`, and `BZ2_bzWriteClose64`.

`BZ2_bzWriteOpen` validates stream, block size, verbosity, and work factor, then initializes `BZ2_bzCompressInit`. `BZ2_bzWrite` feeds caller input to `BZ2_bzCompress(BZ_RUN)`, flushing produced bytes through `fwrite` from the internal buffer.

Close paths optionally abandon, otherwise finish the stream with repeated `BZ2_bzCompress(BZ_FINISH)` calls, write remaining compressed bytes, `fflush`, return 32/64-bit byte counters from `bz_stream`, end compression, and free the wrapper.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/bzip2/lib/bzwrite.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/bzip2/lib/bzzlib.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/bzip2/lib/bzzlib.c

Implements the zlib-style convenience API contributed upstream by Yoshioka Tsuneo: `BZ2_bzopen`, `BZ2_bzdopen`, `BZ2_bzread`, `BZ2_bzwrite`, `BZ2_bzflush`, `BZ2_bzclose`, and `BZ2_bzerror`.

`bzopen_or_bzdopen` parses mode strings for read/write, compression level, and small decompression mode, opens a path or fd as binary stdio where applicable, then delegates to `BZ2_bzReadOpen` or `BZ2_bzWriteOpen`. Empty or null paths map to stdin/stdout.

The thin `bzread`/`bzwrite` wrappers translate bzip2 errors into `-1`/byte counts. `bzclose` closes the bzip2 wrapper then closes non-stdin/stdout files. `bzerror` maps negative bzip2 error codes to string names.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/bzip2/lib/bzzlib.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/bzip2/lib/compress.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/bzip2/lib/compress.c

Compression back end excluding block sorting. It implements bitstream output helpers, byte-use mapping, MTF/RLE generation, adaptive selector/Huffman table generation, and final block/stream emission.

`generateMTFValues` converts sorted BWT block output into MTF symbols, encoding runs of zero MTF values as `BZ_RUNA/BZ_RUNB` and collecting frequencies. `sendMTFValues` chooses 2-6 Huffman groups based on MTF count, iteratively refines tables, MTF-encodes selectors, writes mapping bits, selectors, code lengths, and compressed MTF data.

`BZ2_compressBlock` finalizes block CRC, updates combined CRC, calls `BZ2_blockSort`, emits stream magic on the first block, emits block magic/CRC/randomised-bit/origPtr/data for nonempty blocks, and emits end magic plus combined CRC for the final block.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/bzip2/lib/compress.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/bzip2/lib/crctable.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/bzip2/lib/crctable.c

Static CRC32 lookup table module for libbzip2. It defines `UInt32 BZ2_crc32Table[256]`, used by `BZ_UPDATE_CRC` in `bzlib_private.h`.

The comment identifies it as an AUTODIN-II/Ethernet/FDDI style 32-bit CRC table, vaguely derived from comp.compression FAQ code. No executable functions are present.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/bzip2/lib/crctable.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/bzip2/lib/decompress.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/bzip2/lib/decompress.c

Core bzip2 decompression state machine. `BZ2_decompress(DState*)` incrementally reads the compressed bitstream and can return `BZ_OK` when input is exhausted, saving local state fields in `DState` for later resumption.

It validates stream magic, allocates fast or small-memory inverse-BWT storage, reads block/end headers, block CRC, randomisation bit, original pointer, byte mapping, selectors, Huffman code lengths, builds decode tables, decodes MTF/RLE data into block storage, checks block bounds, and prepares inverse BWT traversal.

Fast mode builds `tt`; small mode uses `ll16` plus packed `ll4` with pointer reversal. It recognizes stream trailer magic, reads stored combined CRC, sets idle state, and returns `BZ_STREAM_END`. Data validation returns `BZ_DATA_ERROR` or `BZ_DATA_ERROR_MAGIC`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/bzip2/lib/decompress.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/bzip2/lib/huffman.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/bzip2/lib/huffman.c

Low-level Huffman support for bzip2. `BZ2_hbMakeCodeLengths` builds bounded-length code lengths from symbol frequencies using heap-based tree construction and frequency rescaling if any code exceeds `maxLen`.

`BZ2_hbAssignCodes` assigns canonical Huffman codes from lengths. `BZ2_hbCreateDecodeTables` builds decoder `limit`, `base`, and `perm` tables from lengths for min/max code lengths.

The implementation uses local fixed arrays sized from `BZ_MAX_ALPHA_SIZE` and assertion checks for heap/node bounds.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/bzip2/lib/huffman.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/bzip2/lib/os.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/bzip2/lib/os.h

Portability header for the embedded bzip2 library. It defaults to generic Unix, detects non-Cygwin Win32, and switches to Plan 9 when `PLAN9` is defined.

It includes `unix.h`, `lccwin32.h`, or `plan9.h` based on the selected platform, defines `NORETURN` for GCC, and establishes bzip2’s basic integer and boolean typedefs: `Char`, `Bool`, `UChar`, `Int32`, `UInt32`, `Int16`, `UInt16`, and `IntNative`.

The Plan 9 copy is modified from upstream and provides a stable type substrate for all bzip2 sources in this directory.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/bzip2/lib/os.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/bzip2/lib/plan9.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/bzip2/lib/plan9.h

Plan 9 platform adapter for bzip2. It includes `<u.h>`, `<libc.h>`, and `<ctype.h>`.

It maps `exit(x)` to Plan 9 `exits((x) ? "whoops" : nil)` and defines `size_t` as `ulong`, giving imported bzip2 code enough compatibility with expected C library names.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/bzip2/lib/plan9.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/bzip2/lib/randtable.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/bzip2/lib/randtable.c

Static randomisation table for legacy bzip2 randomised blocks. It defines `Int32 BZ2_rNums[512]`.

Modern compression in this copy always writes the randomised bit as false, but decompression still supports randomised old streams through macros in `bzlib_private.h` that consume this table.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/bzip2/lib/randtable.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/bzip2/lib/unix.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/bzip2/lib/unix.h

Unix portability include shim for bzip2. It includes standard headers used by the imported code: stdio, stdlib, string, signal, math, errno, and ctype.

No types or functions are defined here; it exists as the platform-specific include set selected by `os.h`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/bzip2/lib/unix.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cal.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/cal.c

Plan 9 `cal` command. It prints the current month, a specified month, or a full year using Plan 9 `Biobuf` output.

It supports month names/abbreviations via a dictionary in `number`, formats month grids in `cal`, trims output rows in `pstr`, and computes Jan 1 weekdays in `jan1`. The calendar logic includes the 1752 calendar changeover by shortening September and skipping days.

Current month/year come from `localtime(time(0))`. Valid years are 1 through 9999; invalid input prints `cal: bad argument`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cal.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/calendar.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/calendar.c

Plan 9 `calendar` reminder matcher. It builds a linked list of regular expressions for today, tomorrow, weekend carry-over days, and optionally a user-specified ahead day.

Options are `-y` to require matching year, `-d` to print generated regexps, and `-p days` to add a future day. With no files it reads `/usr/$user/lib/calendar`; otherwise it scans provided files.

`dates` emits regexps for month-day, day-month, `every <weekday>`, and `the <nth> <weekday>`. Input lines are lowercased before matching; matching original lines are printed.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/calendar.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/calls.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/calls.c

Static C call graph printer. It preprocesses each input file with `cpp -+`, scans the resulting C token stream, records function definitions and call sites, and prints indented call trees.

Core structures are `Rname` for named functions, `Rinst` for call instances, and hash buckets for lookup. The scanner skips comments, strings, character constants, preprocessor line markers, reserved words, and extern declarations, using brace depth to distinguish definitions from calls.

Options include roots via `-f`, APE include mode `-p`, terse/full output `-t/-v`, output width `-w`, and forwarded `-D/-I/-U` cpp options. Output marks recursion and external functions; default roots are functions not called by any other tracked function.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/calls.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cat.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/cat.c

Minimal Plan 9 `cat`. `cat(int f, char *s)` reads 8192-byte chunks from a file descriptor and writes them to stdout, aborting via `sysfatal` on read/write errors.

`main` reads stdin when no files are supplied; otherwise it opens each named file read-only, copies it, and closes it. It sets `argv0 = "cat"` for diagnostics.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cat.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cb/cb.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/cb/cb.c

Plan 9 C beautifier main implementation. It reads stdin or named files and rewrites C source with indentation, spacing, newline, comment, preprocessor, string, block, `if/else`, `do/while`, `struct`, and operator handling.

Options are `-j` to join continuation lines, `-s` for stricter spacing, and `-l width` to set line width/folding thresholds. The formatter is a single-pass lexer/printer with lookahead buffering (`getnext`, `temp`, `inswitch`) and output buffering (`string`, `outs`, `putch`).

It relies heavily on globals from `cb.h`, keyword/operator tables, and classification macros from `cbtype.h`. It handles C and C++ comments, string/char escapes, nested brackets, preprocessor lines, ternary `?:`, and type/struct-specific formatting.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cb/cb.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cb/cb.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/cb/cb.h

Shared definitions and global state for `cb`. It defines keyword/operator type constants, spacing flags, indentation limits, buffer sizes, output macros, and helper macros for eating whitespace.

It declares the `indent`, `keyw`, and `op` structures and initializes global keyword and operator tables directly in the header. It also defines formatter global variables including input/output buffers, indentation stack, do/if tracking, parser flags, lookahead buffers, width counters, and line state.

Function prototypes cover all formatter operations implemented in `cb.c`, including lexical handling, indentation output, comments, operators, lookahead, and EOF error reporting.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cb/cb.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cb/cbtype.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/cb/cbtype.c

Character classification table for `cb`. It defines `_cbtype_[]`, an ASCII table whose bit flags classify control, whitespace, punctuation, operator, digit, uppercase/lowercase, and hex characters.

The table backs the custom `isalpha`, `isdigit`, `isop`, and related macros in `cbtype.h`, avoiding dependency on libc ctype behavior inside the formatter.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cb/cbtype.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cb/cbtype.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/cb/cbtype.h

Header for `cb`’s private ASCII ctype implementation. It defines classification bit masks and declares `_cbtype_[]`.

Macros classify operators, alphabetics, digits, whitespace, punctuation, printable/control ASCII, and hex digits by indexing `_cbtype_ + 1`. It also defines simple ASCII-only `toupper`, `tolower`, and `toascii`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cb/cbtype.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cc/acid.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/cc/acid.c

Plan 9 C compiler support for emitting Acid debugger type information. It maps C aggregate/member types into Acid `aggr`, `complex`, and printer definitions when debug flag `a` is enabled.

`amap` avoids Acid keyword conflicts by mapping reserved names to `$`-prefixed forms. `acidsue` and `acidfun` search compiler symbol hashes for struct/union tags and functions. `acidmember` emits aggregate member metadata or print code depending on mode.

`acidtype` emits Acid aggregate definitions or, with debug `s`, assembler-style `#define` offsets. `acidvar` emits `complex` bindings for locals, parameters, globals, and enum constants when the variable’s type is a struct/union or pointer thereto.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cc/acid.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cc/bits.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/cc/bits.c

Small bitset utility module for the C compiler. `Bits` is a fixed-width array defined in `cc.h`.

Functions implement bitwise union `bor`, intersection `band`, any-bit test `bany`, equality `beq`, first-set-bit number `bnum`, single-bit construction `blsh`, and membership test `bset`. A `bnot` implementation is present but disabled in comments.

These utilities support compiler data-flow or register/variable-set style operations elsewhere in the compiler.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cc/bits.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cc/cc.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/cc/cc.h

Central shared header for the Plan 9 C compiler. It defines AST `Node`, symbol `Sym`, declaration `Decl`, type `Type`, input/history structures, bitsets, enums for AST ops, type codes, storage classes, type flags, ABI targets, and global compiler state.

It declares compiler-wide tables for type compatibility, names, type categories, signatures, and machine widths, plus globals for lexer/parser state, declarations, include paths, output buffers, current function, debug flags, and configuration flags.

The prototype set covers platform compatibility, parser/lexer, macro processing, declarations, semantic/type processing, constant evaluation, function declarations, subtree utilities, Acid/pickle/debug output, bitsets, varargs/pragma checking, machine code generation hooks, 64-bit emulation rewrites, and machine capability checks.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cc/cc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cc/cc.y -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/cc/cc.y

Yacc grammar for the Plan 9 C compiler frontend. It parses external declarations, function definitions, declarators, parameter declarations, struct/union/enum bodies, initializers, blocks, statements, labels, expressions, type names, storage classes, and qualifiers.

Semantic actions construct `Node` trees with `new`, manage declarations through `dodecl`, `markdcl`, `revertdcl`, `argmark`, `pdecl`, `adecl`, and `xdecl`, and call `codgen` for completed functions unless Acid/debug modes suppress codegen.

The grammar supports Plan 9 extensions such as `signof`, `used`, `set`, type strings, compound structure constructors, anonymous generated tags, and `...` prototypes. It also handles string literal concatenation for byte and wide/rune strings.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cc/cc.y -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cc/com.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/cc/com.c

Semantic typing and tree simplification pass for the Plan 9 C compiler. `complex` drives the sequence: type/lvalue checking (`tcom`/`tcomo`), comma hoisting, canonical simplification (`ccom`), constant evaluation (`acom`), machine-specific 64-bit/helper rewrites, and final machine expression complexity (`xcom`).

`tcomo` handles every major AST operator: assignments, arithmetic, shifts, comparisons, logical ops, casts, return, function calls/prototypes, names, string literals, struct member access, address/indirection, `sizeof`, `signof`, and structure constructors. It inserts casts, performs type compatibility checks, marks lvalues, diagnoses invalid operations, and performs array/function address decay when requested.

Later helpers validate function argument lists, resolve struct fields, validate structure constructors, hoist comma expressions out of subtrees, simplify address/indirection and arithmetic identities, fold constants, warn about divide-by-zero/stupid shifts, and diagnose useless or misleading comparisons using 128-bit range modeling.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cc/com.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cc/com64.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/cc/com64.c

Common 64-bit integer emulation rewrite support for Plan 9 compilers targeting machines without direct `vlong` support. It creates AST nodes for runtime helper functions such as `_addv`, `_divv`, `_eqv`, `_f2v`, `_v2d`, `_vasop`, and increment/decrement helpers.

`com64init` initializes all helper nodes and an encoded-type conversion table. `com64` rewrites vlong arithmetic, comparisons, casts, logical tests, compound assignments, and inc/dec operations into helper function calls when `machcap` does not handle them natively.

`bool64` converts vlong truth tests to `_testv`. The file also includes common float/integer conversion helpers and `convvtox`, which masks/sign-extends constants to a target integer type width.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cc/com64.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cc/compat.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/cc/compat.c

Compatibility allocation shim for the Plan 9 C compiler. It includes `cc.h` and `"compat"`, then redirects standard allocation calls to the compiler arena allocator.

`malloc` and `calloc` call `alloc`; `free` is a no-op; `realloc` prints an error and aborts. `mallocz` allocates with optional zeroing and exists for profiling support. `setmalloctag` is a no-op.

The file makes code expecting libc allocation APIs work inside the compiler’s non-freeing hunk allocator model.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/cc/compat.c -->