# Group Research: group_1509_plan9_sources_os_plan9_plan9_sys_src_cmd_awk_awkgram_y_sources_os_p_163659b0d163

This group covers Plan 9 userland command sources: the Lucent awk implementation, Plan 9 utility commands, the Plan 9 `bc` translator, and a split-up bzip2/libbzip2 1.0 port. These files are in subset A because they live under `sources/os/plan9/plan9`, but they are mostly command/runtime/compression code rather than filesystem internals.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/awk/awkgram.y -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/awk/awkgram.y

Yacc grammar for the Lucent awk parser.

Defines awk program structure, patterns, actions, expressions, statements, function definitions, regex literals, array references, redirections, `getline`, loops, `BEGIN`/`END`, `pat,pat` ranges, and built-in function syntax. Semantic actions build `Node` trees using helpers from `parse.c` such as `stat*`, `op*`, `linkum`, `makearr`, and `pa2stat`.

Important parser-side state:

- `beginloc`, `endloc`: accumulated `BEGIN` and `END` statement lists.
- `infunc`: tracks function definition context for `return`, `next`, and argument handling.
- `inloop`: validates `break` and `continue`.
- `curfname`, `arglist`: current function metadata.

The grammar performs compile-time validation for unsafe redirections/pipes in safe mode, duplicate function definitions, array/function name conflicts, illegal `index()` regex use, duplicate arguments, and null-pattern truth coercion through `notnull()`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/awk/awkgram.y -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/awk/lex.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/awk/lex.c

Hand-written awk lexer.

It recognizes keywords, identifiers, numbers, strings, regex literals, comments, operators, redirections, field references, and balanced delimiters. Keywords are binary-searched from a sorted table and mapped to yacc tokens or built-in function subcodes.

Key behavior:

- Maintains `lineno`, `bracecnt`, `brackcnt`, and `parencnt`.
- Implements pushback with `unput()`/`unputstr()` and reads either inline `lexprog` or `-f` source via `pgetc()`.
- Handles awk string escapes including octal and hex.
- Uses `startreg()`/`regexpr()` so `/.../` is lexed as a regex only when grammar asks for one.
- Treats `$NF`, `$name`, `$expr`, and function args specially for indirect field references.
- Enforces safe mode for `system`.

It also records recent input in `ebuf`, which `lib.c` uses for syntax-error context printing.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/awk/lex.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/awk/lib.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/awk/lib.c

Runtime support for records, fields, command-line files, and diagnostics.

Main responsibilities:

- Allocates `$0`/field cells with `recinit()`, `makefields()`, and `growfldtab()`.
- Traverses `ARGV`, applies command-line `var=value`, opens input files, tracks `FILENAME`, `NR`, and `FNR`.
- Reads records with `RS`, including paragraph mode when `RS` is empty.
- Splits fields using default whitespace, single-character `FS`, empty `FS`, or regex `FS`.
- Rebuilds `$0` from fields and `OFS` when fields change.
- Invalidates field/record caches via `donefld` and `donerec`.

Diagnostics include `SYNTAX`, `FATAL`, `WARNING`, brace checking, source/input context reporting, floating-point exception handling, and numeric-string detection via `strtod()`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/awk/lib.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/awk/main.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/awk/main.c

Awk program entry point.

Parses options:

- `-safe`
- `-f programfile`
- `-F fieldsep`
- `-v var=value`
- legacy `-m[rf]`
- `-d`
- `-V`

Initializes the symbol table, records, built-in variables, `ARGV`, optionally `ENVIRON`, then runs `yyparse()`. If parsing succeeds, it sets `compile_time = 0` and calls `run(winner)`.

Also implements `pgetc()` for reading multiple `-f` source files and `cursource()` for error reporting.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/awk/main.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/awk/maketab.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/awk/maketab.c

Build-time generator for `proctab.c`.

It reads token values from `y.tab.h`, emits a printable token-name table, and emits `proctab[]`, mapping yacc token numbers to interpreter functions used by `execute()` in `run.c`.

The static `proc[]` table is the authoritative mapping from syntax tokens such as `ADD`, `PRINT`, `CALL`, `MATCHFCN`, and `FOR` to runtime handlers such as `arith`, `printstat`, `call`, `matchop`, and `forstat`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/awk/maketab.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/awk/parse.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/awk/parse.c

AST construction and function-definition support for awk.

Provides:

- `nodealloc`, `node1` through `node4`.
- Statement constructors `stat1` through `stat4`.
- Expression constructors `op1` through `op4`.
- `celltonode()` and `rectonode()` for value nodes.
- `makearr()` to convert variables into awk arrays.
- `pa2stat()` for `pattern,pattern` range actions.
- `linkum()` for statement-list chaining.
- `defn()` for marking a symbol as a user function and storing its body.
- `isarg()` for function argument lookup.

It also contains pointer/integer conversion helpers used to store small integers in `Node *` slots.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/awk/parse.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/awk/proctab.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/awk/proctab.c

Generated dispatch table for the awk interpreter.

Contains:

- `printname[92]`: token names for debugging.
- `proctab[92]`: maps token offsets from `FIRSTTOKEN` to runtime function pointers.
- `tokname()`: returns token names or a fallback formatted token number.

Expression/statement execution in `run.c` depends on this table. Tokens without runtime behavior map to `nullproc`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/awk/proctab.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/awk/proto.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/awk/proto.h

Cross-module prototypes for the awk implementation.

Covers parser, lexer, regex interface, AST construction, symbol table management, record/field handling, diagnostics, runtime execution, built-ins, I/O redirection, substitution, and Plan 9/ANSI C library hooks such as `popen`/`pclose`.

This header documents the major internal subsystem boundaries: scanner/parser, regex adapter, parse tree builder, symbol table/type conversion, record library, and interpreter runtime.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/awk/proto.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/awk/re.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/awk/re.c

Awk-facing regular expression adapter.

It preprocesses awk regex syntax before handing patterns to Plan 9 regexp routines. Conversions include empty regex constructs, character-class edge cases, octal/hex escapes, and common escapes like `\n`, `\t`, and `\b`.

Key functions:

- `compre()`: preprocesses and compiles regexes; caches up to 20 dynamic runtime patterns.
- `match()`: boolean match.
- `pmatch()`: match and export `patbeg`/`patlen`.
- `nematch()`: non-empty match helper for field splitting.
- `quoted()` and `hexstr()`: escape parsing.
- `countposn()`: multibyte/rune position counting for awk-visible positions.
- `regerror()`/`overflow()`: fatal regexp error paths.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/awk/re.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/awk/run.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/awk/run.c

Tree-walking interpreter for awk.

Major runtime pieces:

- `run()` initializes standard I/O slots, executes the root program, then closes files.
- `execute()` dispatches AST nodes through `proctab[]`.
- `program()` runs `BEGIN`, main record loop, and `END`, with `setjmp`/`longjmp` for `exit`.
- Function calls use dynamic stack frames, copied scalar arguments, by-reference arrays, and a temporary return cell.
- Control flow uses special `Cell` values for `break`, `continue`, `next`, `nextfile`, `exit`, and `return`.

Implements awk semantics for arrays, `delete`, `in`, regex matches, booleans, comparisons, temporaries, indirect fields, `substr`, `index`, `sprintf`/`printf`, arithmetic, assignment, concatenation, pattern actions, range patterns, `split`, conditionals, loops, built-ins, printing, redirection, file cache/close/flush, `sub`, and `gsub`.

Notable design details include pooled temporary `Cell`s, cached redirection files/pipes keyed by filename, UTF-aware `substr`/`length`/`split("", ...)`, and special handling for empty-string substitutions.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/awk/run.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/awk/tran.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/awk/tran.c

Symbol table and awk value conversion layer.

Initializes built-in variables including `FS`, `RS`, `OFS`, `ORS`, `OFMT`, `CONVFMT`, `NF`, `NR`, `FNR`, `FILENAME`, `SUBSEP`, `RSTART`, `RLENGTH`, `SYMTAB`, `ARGV`, and optionally `ENVIRON`.

Provides hash-table backed arrays and cells:

- `makesymtab`, `setsymtab`, `lookup`, `rehash`
- `freesymtab`, `freeelem`
- `setfval`, `setsval`
- `getfval`, `getsval`
- `tostring`, `qstring`

The file enforces awk’s dual string/numeric value model and coordinates record/field invalidation when `$0`, `$n`, or `NF`-related values change.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/awk/tran.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/basename.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/basename.c

Plan 9 `basename` implementation.

Behavior:

- Usage: `basename [-d] string [suffix]`.
- Without `-d`, prints the final path component after the last `/`.
- With optional suffix, strips that suffix from the basename if present.
- With `-d`, prints the directory portion before the last `/`, or `.` if none exists.

Uses Plan 9 UTF-aware `utfrrune()` to find the final slash.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/basename.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/bc.y -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/bc.y

Yacc grammar and translator for Plan 9 `bc`.

This is not a standalone arithmetic engine. It parses `bc` syntax and emits `dc` program text, either to stdout with `-c` or through a pipe to `/bin/dc`.

Supports:

- Assignments and compound assignments.
- `scale`, `ibase`/`base`, and `obase`.
- `print`, strings, `sqrt`, `length`, function calls, arrays, increments/decrements.
- `if`, `while`, `for`, `break`, `return`, `define`, `auto`.
- Optional standard math library via `-l`.

The implementation builds output fragments with `bundle()` over a fixed pointer workspace, uses labels like `<128>` for branches, maps functions/arrays to encoded dc registers, and reports parser errors as dc print commands.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/bc.y -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/bind.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/bind.c

Plan 9 `bind` command wrapper.

Parses mount flags:

- `-a`: `MAFTER`
- `-b`: `MBEFORE`
- `-c`: `MCREATE`
- `-q`: quiet failure

Requires exactly `new old`, and rejects combining `-a` and `-b`. Calls Plan 9 `bind()`, then reports targeted errors for missing source or target paths before exiting with `bind`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/bind.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/bsplit.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/bsplit.c

Plan 9 `bsplit`, a copy-light binary splitter.

Options:

- `-p pfx`: output filename prefix, default `bs.`
- `-s size`: maximum output size, default 512 MiB
- `-d`: increments debug flag but does not otherwise affect processing

It reads stdin or listed files into a 128 KiB buffer and writes sequential files named `<prefix><5-digit-number>`. The output loop tries to write sector-aligned chunks when possible, closes the current output when it reaches the size limit, and continues until all inputs are consumed.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/bsplit.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/bzip2/bunzip2.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/bzip2/bunzip2.c

Plan 9 `bunzip2` frontend using the embedded libbzip2 stream API.

Options:

- `-c`: write decompressed output to stdout.
- `-v`: libbzip2 verbosity.
- `-D`: increments a debug flag.

For files, it verifies the `BZh` magic, derives output names by stripping `.bz2` or mapping `.tbz`/`.tbz2` to `.tar`, refuses unsafe overwrite cases, then streams through `BZ2_bzDecompressInit`, `BZ2_bzDecompress`, and `BZ2_bzDecompressEnd`.

Uses Plan 9 `Biobuf` for buffered I/O and removes a partially written output file on failure.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/bzip2/bunzip2.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/bzip2/bzip2.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/bzip2/bzip2.c

Plan 9 `bzip2` frontend using the embedded libbzip2 stream API.

Options:

- `-1` through `-9`: compression level, default `6`.
- `-c`: write compressed output to stdout.
- `-v`: libbzip2 verbosity.
- `-D`: increments a debug flag.

Rejects directories, derives output names as `.bz2` or `.tbz` for `.tar`, and streams input through `BZ2_bzCompressInit`, repeated `BZ2_bzCompress`, and `BZ2_bzCompressEnd`. Uses a one-extra-loop flush hack to drain the output buffer after stream end.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/bzip2/bzip2.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/bzip2/bzip2recover.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/bzip2/bzip2recover.c

Upstream bzip2 1.0 block recovery tool.

It scans a damaged `.bz2` file bit-by-bit looking for bzip2 block headers and end markers, records recoverable block bit ranges, then writes each block into a separate `recNNNN...bz2` file with a synthetic bzip2 header and end marker.

Important pieces:

- `BitStream` abstracts bit-level read/write over `FILE *`.
- `BLOCK_HEADER_*` and `BLOCK_ENDMARK_*` constants detect block boundaries.
- `bStart`, `bEnd`, `rbStart`, `rbEnd` store candidate and recoverable ranges.
- Recovered blocks include the stored block CRC and a new stream wrapper.

The file is explicitly described by upstream as a hacky salvage program, not part of normal compression/decompression.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/bzip2/bzip2recover.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/bzip2/lib/blocksort.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/bzip2/lib/blocksort.c

Core Burrows-Wheeler block sorting machinery from libbzip2 1.0.

Contains two sorting paths:

- Main sort for normal blocks: two-byte radix bucket setup, Sedgewick/Bentley 3-way string quicksort, quadrant descriptors, bucket scanning, and a work budget.
- Fallback sort for highly repetitive or small blocks: initial one-character radix sort followed by exponential bucket refinement inspired by Manber-Myers suffix-array construction.

Key public entry point:

- `BZ2_blockSort(EState *s)`: sorts block rotations into `s->ptr`/`arr1`, chooses main or fallback sort, and records `s->origPtr`.

The work-factor budget controls when the main sort gives up and falls back. The implementation is performance-critical and heavily macro/inline optimized.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/bzip2/lib/blocksort.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/bzip2/lib/buffcompress.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/bzip2/lib/buffcompress.c

Split-out libbzip2 buffer-to-buffer compression helper.

Exports `BZ2_bzBuffToBuffCompress()`. It validates parameters, defaults `workFactor` to 30, initializes a `bz_stream`, points it at caller-provided input and output buffers, runs compression with `BZ_FINISH`, updates `*destLen` on success, and maps unfinished output to `BZ_OUTBUFF_FULL`.

This file is marked as modified from upstream mainly to split the library into smaller pieces for the Plan 9 port.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/bzip2/lib/buffcompress.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/bzip2/lib/buffdecompress.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/bzip2/lib/buffdecompress.c

Split-out libbzip2 buffer-to-buffer decompression helper.

Exports `BZ2_bzBuffToBuffDecompress()`. It validates pointers, `small`, and verbosity, initializes decompression, points the stream at caller-provided buffers, runs one decompression call, updates `*destLen` on stream end, and distinguishes output-buffer exhaustion from unexpected EOF when decompression returns `BZ_OK`.

Like the other split files, it is upstream libbzip2 code reorganized for the Plan 9 tree.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/bzip2/lib/buffdecompress.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/bzip2/lib/bzassert.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/bzip2/lib/bzassert.c

libbzip2 assertion failure handler.

Defines `BZ2_bz__AssertH__fail(int errcode)`, which prints a detailed internal-error message including the libbzip2 version and exits with status 3.

This is the hard assertion path used by `AssertH` in the bzip2 internals, including block sorting and decompression.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/bzip2/lib/bzassert.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/bzip2/lib/bzbuffcompress.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/bzip2/lib/bzbuffcompress.c

Duplicate/split variant of the buffer-to-buffer compression helper.

Defines `BZ2_bzBuffToBuffCompress()` with the same behavior as `buffcompress.c`: validate arguments, initialize a compression stream, compress source to destination with `BZ_FINISH`, update destination length, return `BZ_OK`, `BZ_OUTBUFF_FULL`, or the underlying stream error.

The file carries the same Plan 9 note that the upstream libbzip2 source was split into smaller pieces.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/bzip2/lib/bzbuffcompress.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/bzip2/lib/bzcompress.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/bzip2/lib/bzcompress.c

Core streaming compression state machine for libbzip2.

Provides:

- `BZ2_bzCompressInit()`: validates config, installs allocators, allocates `EState`, block arrays, and frequency table.
- Run-length input staging via `init_RL`, `add_pair_to_block`, `flush_RL`, and `ADD_CHAR_TO_BLOCK`.
- `copy_input_until_stop()` and `copy_output_until_stop()` for incremental stream progress.
- `handle_compress()` to transition between input and output states.
- `BZ2_bzCompress()`: implements `BZ_RUN`, `BZ_FLUSH`, and `BZ_FINISH` sequencing.
- `BZ2_bzCompressEnd()`: frees allocated compression state.

It writes full compressed blocks through `BZ2_compressBlock()` and tracks total input/output counters, flush expectations, finish expectations, block CRCs, and run-length encoding before block sorting.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/bzip2/lib/bzcompress.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/bzip2/lib/bzdecompress.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/bzip2/lib/bzdecompress.c

Core streaming decompression state machine for libbzip2.

Provides:

- `BZ2_bzDecompressInit()`: validates config, installs allocators, initializes `DState`.
- `unRLE_obuf_to_output_FAST()`: inverse BWT/output run decoder using `tt`.
- `unRLE_obuf_to_output_SMALL()`: memory-saving inverse path using `ll16`/`ll4`.
- `BZ2_indexIntoF()`: helper for small-mode inverse mapping.
- `BZ2_bzDecompress()`: drives parser state through `BZ2_decompress()`, emits output, validates per-block and combined CRCs, and returns `BZ_OK`, `BZ_STREAM_END`, or data errors.
- `BZ2_bzDecompressEnd()`: frees decompression state arrays.

It handles both randomized and non-randomized historical bzip2 blocks and preserves partial output state when caller output buffers fill.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/bzip2/lib/bzdecompress.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/bzip2/lib/bzfeof.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/bzip2/lib/bzfeof.c

Small stdio helper for libbzip2.

Defines `bz_feof(FILE *f)`, which probes EOF by reading one byte with `fgetc()` and pushing it back with `ungetc()` when not EOF.

Used by the stdio-oriented bzip2 wrapper layer split out elsewhere in this Plan 9 port.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/bzip2/lib/bzfeof.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/bzip2/lib/bzlib.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/bzip2/lib/bzlib.c

Small libbzip2 support file.

Defines:

- `bz_config_ok()`: verifies expected type sizes: `int` 4 bytes, `short` 2 bytes, `char` 1 byte.
- `default_bzalloc()`: malloc-backed allocator.
- `default_bzfree()`: free-backed deallocator.
- `bz_internal_error()`: Plan 9-added fallback that exits with status 1.

This file supplies allocator/configuration glue used by compression and decompression initialization.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/bzip2/lib/bzlib.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/bzip2/lib/bzlib.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/bzip2/lib/bzlib.h

Public libbzip2 header.

Defines action constants, return codes, the public `bz_stream` structure, DLL/API macros, and prototypes for:

- `BZ2_bzCompressInit`
- `BZ2_bzCompress`
- `BZ2_bzCompressEnd`
- `BZ2_bzDecompressInit`
- `BZ2_bzDecompress`
- `BZ2_bzDecompressEnd`
- `BZ2_bzBuffToBuffCompress`
- `BZ2_bzBuffToBuffDecompress`
- `BZ2_bzlibVersion`

The header is mostly upstream bzip2 1.0 API surface, with a Plan 9 note that the source was modified and split into smaller pieces.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/bzip2/lib/bzlib.h -->