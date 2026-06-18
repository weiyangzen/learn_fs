# Group Research: group_1591_plan9_sources_os_plan9_plan9_sys_src_cmd_gs_zlib_zlib_h_sources_os__51fcc0e21a95

Scope: `Docs/research_subset_a.md`, source tree `sources/os/plan9/plan9`.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/zlib/zlib.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/zlib/zlib.h

Public zlib 1.2.2 API header bundled under Ghostscript’s local `zlib` directory.

- Defines `z_stream`, allocator callback types, public constants, flush modes, compression levels, strategy values, return codes, and method IDs.
- Declares core stream APIs: `deflate`, `inflate`, `deflateEnd`, `inflateEnd`, plus macro-wrapped `deflateInit`, `inflateInit`, `deflateInit2`, `inflateInit2`, and `inflateBackInit`.
- Declares advanced APIs for dictionaries, stream copy/reset, parameter changes, bounds, raw/gzip wrappers, `inflateBack`, and compile flags.
- Declares convenience APIs: `compress`, `compress2`, `compressBound`, `uncompress`.
- Declares gzip file APIs: `gzopen`, `gzdopen`, `gzread`, `gzwrite`, `gzprintf`, `gzseek`, `gzclose`, `gzerror`, and related helpers.
- Declares checksum APIs `adler32`, `crc32`, `get_crc_table`, plus `zError` and `inflateSyncPoint`.

Dependencies are `zconf.h` and zlib implementation internals. This file is a vendored upstream interface, not Plan 9-specific logic. Comments document API contracts extensively, including buffer ownership, return-code semantics, gzip/zlib/raw wrapper behavior, and memory-allocation requirements.

Notable concerns: this is old zlib 1.2.2-era API text. Consumers must compile against matching implementation objects because init macros pass `ZLIB_VERSION` and `sizeof(z_stream)` for compatibility checks.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/zlib/zlib.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/zlib/zutil.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/zlib/zutil.c

Target-dependent zlib utility implementation.

- Defines `z_errmsg[]`, mapping zlib status codes to messages through `ERR_MSG`.
- Implements `zlibVersion()` and `zlibCompileFlags()`.
- Provides debug-only `z_error()` and `z_verbose`.
- Exports `zError()` for converting zlib return codes to strings.
- Provides fallback `zmemcpy`, `zmemcmp`, and `zmemzero` when `HAVE_MEMCPY` is unavailable.
- Provides `zcalloc()` and `zcfree()` default allocation hooks, with special branches for legacy 16-bit Turbo C and Microsoft C models.

Dependencies are `zutil.h`, libc allocation, optional stdio for debug, and platform macros. In normal Plan 9/Ghostscript builds, the generic allocator path is the relevant one.

Notable concerns: the generic `zcalloc()` uses `malloc(items * size)` on systems with `sizeof(uInt) > 2` without overflow checking, matching old upstream zlib behavior. The many 16-bit branches are portability baggage rather than active Plan 9 behavior.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/zlib/zutil.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/zlib/zutil.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/zlib/zutil.h

Internal zlib configuration and utility header.

- Marks `ZLIB_INTERNAL` and includes the public `zlib.h`.
- Defines internal aliases `uch`, `ush`, `ulg`, `local`, error-message macros, block-type constants, match-length constants, and preset-dictionary flag.
- Selects `OS_CODE`, `F_OPEN`, `fdopen`, and platform includes for many historical targets.
- Defines availability or replacements for `vsnprintf`, `strerror`, `memcpy`, `memcmp`, and `memset`.
- Defines debug tracing/assertion macros and no-op versions for non-debug builds.
- Declares `zcalloc()` and `zcfree()` and wraps them through `ZALLOC`, `ZFREE`, and `TRY_FREE`.

Dependencies are `zlib.h`, standard C headers when `STDC` is enabled, and many compile-time platform defines. Applications should not include it directly; it is for zlib internals.

Notable concerns: platform detection defaults unknown targets to Unix `OS_CODE 0x03`, which is likely how this Plan 9 copy behaves unless build flags override it.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/zlib/zutil.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gview.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gview.c

Interactive Plan 9 graphical viewer/editor for polygonal line graphs.

- Input format: one `x y` point per line, followed by a label line per polyline. Multiple input files or stdin can be loaded.
- Maintains linked-list `fpolygon` objects inside global `univ`, with bounding boxes, display rectangle, slant height, current color/thickness, and optional multi-color schemes parsed from labels.
- Implements coordinate transforms from floating-point data coordinates to screen coordinates, including zoom, zoom-out, square-up, recenter, and slant display.
- Draws axes, tick marks, scaled labels, top range text, clipped polylines, selected-point marker, and optional dot-only plotting.
- Provides selection by mouse proximity, logs selected coordinates and optionally labels, and supports interactive recolor, thicken/thin, delete, undo, restack, read, write, move, and rotate.
- Uses Plan 9 graphics/event APIs: `<draw.h>`, `<event.h>`, `emouse`, `ekbd`, `emenuhit`, `egetrect`, and `initdraw`.

Important data structures: `fpoint`, `frectangle`, `fpolygon`, `fpolygons`, `transform`, `thick_color`, `pt_on_fpoly`, and undo record `e_action`.

Notable concerns:
- Movement and rotation are disabled by default unless `-m` is supplied.
- Several allocations are unchecked or only partially checked, consistent with older C style.
- Input parsing is intentionally simple and treats malformed label/point sequences as syntax errors.
- Output rewrites labels to reflect current color/thickness.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gview.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gzip/gunzip.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gzip/gunzip.c

Plan 9 gzip decompressor built on the system `<flate.h>` inflate API.

- Supports `gunzip [-ctvTD] [file ...]`.
- Reads gzip headers, validates magic and deflate method, parses optional extra, original filename, comment, and header CRC fields.
- Uses `inflateinit()` once, then `inflate()` with `Bgetc` input and `crcwrite` output callback.
- Maintains CRC-32 using `mkcrctab(GZCRCPOLY)` and `blockcrc`.
- Validates trailer CRC and uncompressed length after each gzip member.
- Supports table/listing mode, stdout mode, verbose extraction, and optional restoration of modification time.

State is mostly global: input filename, output-delete path, CRC, length counters, table/verbose flags, and `jmp_buf` for error recovery.

Notable concerns:
- Output filename handling uses a fixed 256-byte buffer.
- Multiple gzip members are supported by looping until input EOF.
- Corruption after a completed gzip member is reported and ignored using `gzok`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gzip/gunzip.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gzip/gzip.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gzip/gzip.c

Plan 9 gzip compressor built on `<flate.h>` deflate.

- Supports `gzip [-vcD] [-1-9] [file ...]`.
- Writes gzip header with magic, deflate method, optional original filename, mtime, and OS field.
- Uses `deflateinit()` and `deflate()` with `crcread` and `gzwrite` callbacks.
- Calculates CRC-32 and total uncompressed length, then writes gzip trailer.
- Converts `.tar` input suffix to `.tgz`; otherwise writes `<name>.gz`.
- Rejects directories and removes incomplete output on write/compression failure.

Dependencies are Plan 9 `libc`, `bio`, `flate`, and local `gzip.h`.

Notable concerns: archive member name is the original path string passed to `gzip()`, not just the basename in all cases. Output filename generation mutates local strings and uses fixed-size buffers.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gzip/gzip.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gzip/gzip.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gzip/gzip.h

Shared gzip-format constants for `gzip.c` and `gunzip.c`.

- Defines gzip magic bytes, deflate method ID, header flag bits, extra flag meanings, OS identifiers, and CRC polynomial.
- Sets `GZOSINFERNO` to `GZOSUNIX`, so this implementation writes Unix-style OS code.
- Provides no functions or state.

This header is a compact local protocol definition for gzip member parsing and generation.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gzip/gzip.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gzip/unzip.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gzip/unzip.c

Plan 9 ZIP extractor/listing utility.

- Supports `unzip [-cistTvD] [-f zipfile] [file ...]`, plus `-a` auto-directory creation.
- Can read central-directory archives or streaming local-header mode with `-s`; if seeking fails it retries as stream mode.
- Parses local headers, central directory headers, end-of-central-directory records, filenames, optional trailer descriptors, and MS-DOS timestamps.
- Supports stored method `0` and deflated method `8`; other methods are rejected.
- Filters requested file names by exact path or directory prefix.
- Extracts to stdout, files, or directories, restores mtimes with `-T`, optionally lowercases names with `-i`, and validates CRC, compressed size, and uncompressed size.

Dependencies are Plan 9 `bio`, `flate`, local `zip.h`, and CRC helpers.

Notable concerns:
- `findCDir()` assumes the end-of-central-directory header is exactly at EOF minus fixed header size, so ZIP file comments are not handled.
- `mkpdirs()` contains an unconditional `print("%s\n", path);`, so `-a` auto-directory mode can emit unexpected path lines.
- Zip64, encryption, patched data, and most compression methods are unsupported.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gzip/unzip.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gzip/zip.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gzip/zip.c

Plan 9 ZIP archive writer.

- Supports `zip [-vD] [-1-9] [-f zipfile] file ...`.
- Recursively archives directories, writing directory entries with trailing slash names.
- Writes local file headers, deflated file payloads, optional data descriptors for stdout archives, central directory entries, and end-of-central-directory record.
- Uses Plan 9 `<flate.h>` deflate callbacks and CRC-32 from `mkcrctab(ZCrcPoly)`/`blockcrc`.
- Stores modification times in MS-DOS time/date format and uses DOS-style external attributes.
- Maintains all `ZipHead` records in a growable in-memory array until the central directory is written.

Dependencies are `zip.h`, `bio`, `flate`, libc file APIs, and stdio-like Plan 9 functions.

Notable concerns:
- The archive is limited to fewer than 65536 entries and 32-bit ZIP sizes/offsets.
- Directory recursion constructs child paths in a fixed “parent + 256” allocation.
- It does not preserve full Unix permissions; attributes are DOS-oriented.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gzip/zip.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gzip/zip.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gzip/zip.h

Shared ZIP-format constants and `ZipHead` structure.

- Defines local header, central directory header, and end-of-central-directory magic numbers.
- Defines general-purpose flag bits such as encryption and trailer/data-descriptor presence.
- Defines CRC polynomial, deflate method ID, file-attribute OS IDs, DOS external attribute bits, and fixed header sizes/offsets.
- `ZipHead` stores version/OS metadata, flags, method, DOS time/date, CRC, sizes, attributes, local-header offset, and filename.

Used by both `zip.c` and `unzip.c` as the local ZIP metadata contract.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gzip/zip.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/hget.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/hget.c

Resumable HTTP/HTTPS/FTP downloader for Plan 9.

- Supports `hget [-dhv] [-o outfile] [-p body] [-x netmtpt] [-r header] url`.
- Parses `http`, `https`, and `ftp` URLs, optional proxy from `httpproxy`, output-file resume offsets, custom request header, and form-urlencoded POST body.
- HTTP path sends HTTP/1.0 requests, supports Range/If-Range resume, redirects, cookies via `/mnt/webcookies/http`, Basic authentication through `auth_getuserpasswd`, response headers, and mtime preservation.
- HTTPS wraps the TCP fd with `tlsClient()`, but explicitly notes certificate checking is missing.
- FTP path supports anonymous login, binary mode, MDTM/SIZE resume checks, REST restart, passive mode first, then active mode fallback.
- Output path tracks offsets and MD5 states to validate already-written resumed bytes before appending new data.

Important structures: `URL`, `Range`, and `Out`. Important helpers include `crackurl`, `dohttp`, `httpheaders`, `doftp`, `ftprestart`, `passive`, `active`, buffered `readline`/`readibuf`, and `output`.

Notable concerns:
- `Range` and output offsets are `long`/`int` in places; comments note only 2 GB range support.
- HTTPS does not verify certificates.
- HTTP proxy support is limited and FTP proxy is marked untested.
- Header parsing and URL parsing are minimal and mutate input URL strings.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/hget.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/histogram.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/histogram.c

Graphical live histogram/strip-chart utility reading numeric values from stdin.

- Supports `histogram [-h] [-c index] [-r minx,miny,maxx,maxy] [-s scale] [-t title] [-v maxv]`.
- Creates a new window, initializes drawing, mouse, keyboard, and a reader process.
- Reader parses one numeric token per input line and sends doubles over a channel.
- Maintains a rolling `double` array sized to the drawable width; new values shift old samples right.
- Draws colored vertical one-pixel bands with a dot-height transition between previous and current values.
- Handles resize redraws, button-3 exit menu, and Delete-key exit.

Dependencies are Plan 9 draw/thread/mouse/keyboard/Bio APIs.

Notable concerns: display buffer grows with window width; the program exits when stdin closes unless `-h` is set. Palette index is modulo the number of color schemes.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/histogram.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/history.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/history.c

Plan 9 dump filesystem history lookup utility.

- Supports `history [-bDfuv] [-d dumpfilesystem] [-s yyyymmdd] files`.
- Resolves each target file to an absolute path and maps `/n/<name>/...` paths to a corresponding `<name>dump` mount unless `-d` is supplied.
- Ensures the dump filesystem is mounted by running `9fs <dump>` when needed.
- Prints current file state, then walks backward through dump snapshots to find earlier versions.
- Supports both traditional dump naming and `snap`-style directories.
- With `-D`, runs `/bin/diff` between adjacent found versions, forwarding selected diff flags.

Important functions: `ysearch`, `lastbefore`, `starttime`, `prtime`, and `darg`.

Notable concerns:
- Time search uses heuristic 12-hour/day stepping and a 30-try backward limit.
- Buffers for paths are fixed-size.
- With `-f`, missing historical files are represented by synthetic `Dir` data to continue reporting removals.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/history.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/hoc/code.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/hoc/code.c

Runtime virtual machine and execution engine for `hoc`.

- Defines fixed-size operand stack (`NSTACK 256`), instruction array (`NPROG 2000`), program counter, subprogram base, and call frame stack (`NFRAME 100`).
- Implements stack primitives, code emission, and instruction dispatch through `execute()`.
- Implements control-flow bytecodes for `while`, `for`, and `if`.
- Implements function/procedure definitions, calls, formal binding, saved variable restoration, and returns.
- Implements arithmetic, comparisons, boolean operations, exponentiation, assignment, compound assignment, increment/decrement, variable evaluation, builtins, printing, string printing, and `read()`.
- Uses `execerror()` for runtime errors and recovery.

Dependencies are `hoc.h`, generated `y.tab.h`, Plan 9 `bio`, `libc`, and math wrappers in `math.c`.

Notable concerns: fixed VM limits cause runtime errors for deep stacks, oversized programs, and deeply nested calls. `modeq()` casts through `long`, unlike `mod()` which uses `fmod`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/hoc/code.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/hoc/hoc.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/hoc/hoc.h

Shared declarations and core data structures for the `hoc` interpreter.

- Defines `Inst` as `void (*)(void)` and `STOP` as null instruction.
- Defines `Symbol`, `Symval`, `Datum`, `Saveval`, `Formal`, and `Fndefn`.
- `Symbol` supports variables, builtins, functions/procedures, strings, keywords, and undefined identifiers.
- `Datum` is the VM stack value union: numeric value or symbol pointer.
- Declares symbol-table, VM, parser, math, function-call, and execution helpers.

This header is the contract between parser (`hoc.y`), VM (`code.c`), builtins (`init.c`/`math.c`), and symbol table (`symbol.c`).
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/hoc/hoc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/hoc/hoc.y -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/hoc/hoc.y

Yacc grammar, lexer, input driver, and error recovery for `hoc`.

- Grammar supports assignments, compound assignments, expressions, `print`, `read`, `if/else`, `while`, `for`, statement blocks, functions, procedures, returns, formal parameters, and argument lists.
- Expression grammar includes arithmetic, `%`, exponentiation, comparisons, logical operators, unary minus, logical not, and pre/post increment/decrement.
- Parser actions emit VM instructions into `prog[]` using `code`, `code2`, and `code3`.
- Lexer recognizes numbers via `Bgetd`, identifiers including high-bit bytes, quoted strings with simple escapes, comments beginning `#`, continuation backslash-newline, and multi-character operators.
- Main input loop supports stdin, file arguments, and `-e` expressions via temporary files.
- Runtime and parse errors call `execerror()`, flush remaining input, restore formal bindings, and longjmp to the top-level parse loop.

Dependencies are `hoc.h`, `bio`, `ctype`, libc, generated `y.tab.h`, and the VM in `code.c`.

Notable concerns: identifiers and strings are limited to 99 bytes. Error recovery seeks to end of the current input file, so one bad expression can skip the rest of that file.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/hoc/hoc.y -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/hoc/init.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/hoc/init.c

Initialization table for `hoc` keywords, constants, and builtins.

- Installs language keywords: `proc`, `func`, `return`, `if`, `else`, `while`, `for`, `print`, and `read`.
- Installs numeric constants: `PI`, `E`, `GAMMA`, `DEG`, and `PHI`.
- Installs math builtins: trigonometric functions, inverse trig wrappers, hyperbolic wrappers, logs, exp, sqrt, integer conversion, and abs.
- Builtins are entered as `BLTIN` symbols with function pointers in `u.ptr`.

Dependencies are `hoc.h`, generated token definitions in `y.tab.h`, and math/libc functions.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/hoc/init.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/hoc/math.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/hoc/math.c

Checked math wrappers for `hoc` builtins.

- Wraps `log`, `log10`, `sqrt`, `exp`, `asin`, `acos`, `sinh`, `cosh`, and `pow`.
- `integer()` validates 32-bit signed range before casting to `long`.
- `errcheck()` maps NaN to “argument out of domain” and infinity to “result out of range” through `execerror()`.

Dependencies are Plan 9 math predicates `isNaN`/`isInf`, libc math functions, and `hoc.h`.

Notable concern: only selected math functions are range-checked through wrappers; direct builtins like `sin`, `cos`, `tan`, `atan`, `tanh`, and `fabs` are installed directly.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/hoc/math.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/hoc/symbol.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/hoc/symbol.c

Symbol-table and allocation helpers for `hoc`.

- Maintains a simple linked-list symbol table.
- `lookup()` linearly searches by symbol name.
- `install()` allocates a new `Symbol`, copies the name, sets type/value, and prepends to the table.
- `emalloc()` wraps `malloc` and reports out-of-memory through `execerror()`.
- `formallist()` builds linked formal-parameter lists for function/procedure definitions.

Notable concerns: symbol lookup is O(n), and installed symbols are never freed during normal interpreter lifetime.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/hoc/symbol.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/html2ms.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/html2ms.c

Lightweight HTML-to-ms/troff converter.

- Reads HTML-like input from stdin and writes ms/troff macros to stdout.
- Uses a tag dispatch table (`Goobie`) mapping many HTML tags to actions or ignores.
- Handles headings, paragraphs, line breaks, horizontal rules, lists, display/pre blocks, font changes, definition-list terms, and table start/end markers.
- Maintains font and list stacks of fixed depth `SSIZE`.
- Decodes a local table of common HTML entities plus numeric ASCII printable entities.
- Collapses whitespace outside `<pre>` and emits newlines/macro starts carefully for troff formatting.

Dependencies are Plan 9 `bio`, `ctype`, and libc.

Notable concerns: this is not a full HTML parser. Tag/attribute parsing is simple, entity buffer is only 8 bytes, and many tags are ignored or only minimally represented.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/html2ms.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/htmlfmt/dat.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/htmlfmt/dat.h

Shared declarations for `htmlfmt`.

- Defines `Bytes`, a growable byte buffer.
- Defines `URLwin`, holding input/output fds, document type, URL, parsed `Item` tree, and `Docinfo`.
- Declares global options `url`, `aflag`, `width`, and `defcharset`.
- Declares HTML loading/rendering, file/memory helpers, charset handling, byte-buffer growth, and URL window cleanup functions.

Depends on Plan 9 `<html.h>` types such as `Item` and `Docinfo`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/htmlfmt/dat.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/htmlfmt/html.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/htmlfmt/html.c

HTML parser adapter and text renderer for `htmlfmt`.

- Reads all input fd bytes into `Bytes`, constructs a `URLwin`, and parses HTML with Plan 9 `parsehtml()`.
- Converts parsed item trees into wrapped plaintext.
- Renders text items, rules, images, form fields, tables, floating items, and spacers.
- Optional `-a` mode emits image/link/form annotations such as `[image URL]` and anchor URLs.
- Builds absolute URLs using a regular expression over schemes and host components.
- Detects charset from an early `<meta ... charset=...>` string, defaulting to ISO-8859-1.

Dependencies are Plan 9 `html.h`, `regexp.h`, draw types, rune conversion helpers, and local `dat.h`.

Notable concerns:
- Charset detection is explicitly a hack and searches only a simple meta/header pattern.
- `rendertext()` comments out freeing `rurl`, leaving a small leak.
- Table rendering flattens cells sequentially rather than preserving layout.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/htmlfmt/html.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/htmlfmt/main.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/htmlfmt/main.c

Command-line driver for `htmlfmt`.

- Supports `htmlfmt [-c charset] [-u URL] [-a] [-l length] [file ...]`.
- `-a` enables anchor/image/form annotations.
- `-u` sets the base URL and also enables annotation mode.
- `-c` injects a synthetic meta charset string and uses `charset()` to set default charset.
- `-l`/`-w` sets output wrap width.
- Processes stdin when no files are given, otherwise files in order until an error.

Dependencies are `dat.h`, Plan 9 `html.h`, and `loadhtml()` from `html.c`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/htmlfmt/main.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/htmlfmt/util.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/htmlfmt/util.c

Utility functions for `htmlfmt`.

- Provides checked allocation helpers `emalloc`, `erealloc`, `estrdup`, `estrstrdup`, `eappend`, and `egrow`.
- Provides `growbytes()` for append-only byte buffer growth with null termination.
- Provides `error()` that prints a formatted message to fd 2 and exits.

Notable concern: `error()` prefixes messages with `Mail: `, likely copied from another program and misleading for `htmlfmt`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/htmlfmt/util.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/htmlroff/a.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/htmlroff/a.h

Central header for `htmlroff`, a troff/ms-to-HTML converter.

- Defines private Unicode/rune sentinels for raw HTML characters, symbols, formatted/unformatted markers, nonbreaking space, and output-control markers.
- Defines unit constants and input mode flags: copy, expand, argument, and HTML modes.
- Declares nearly all parser, request, macro, input, output, register, string, HTML, font, and utility functions.
- Declares global parser/output state such as `backslash`, `bol`, `bout`, `dot`, `inputmode`, `inrequest`, `utf8`, `verbose`, and `linepos`.
- Provides rune allocation/reallocation/move macros and `Fmt` pragma for `%L`.

This header binds together the larger `htmlroff` implementation beyond the files in this group.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/htmlroff/a.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/htmlroff/char.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/htmlroff/char.c

Character translation helpers for `htmlroff`.

- `rune2html()` converts Unicode runes to HTML by spawning `/bin/tcs -t html`, sending runes through a pipe, and caching per-rune results in a two-level cache.
- Handles newline directly and rejects runes outside 16-bit range due to cache shape.
- `troff2rune()` maps two-character troff special names to Unicode runes.
- Initializes a small built-in troff mapping table, then loads `/sys/lib/troff/font/devutf/utfmap`.

Dependencies are `/bin/tcs`, troff `utfmap`, Plan 9 `bio`, pipes/fork/exec, and `a.h`.

Notable concerns: `rune2html()` depends on a long-lived external `tcs` process and uses extra newlines as a flushing hack. `trtab` has a fixed size of 200 entries and warns if too small.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/htmlroff/char.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/htmlroff/html.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/htmlroff/html.c

HTML tag emission and inline HTML state management for `htmlroff`.

- Maintains a stack of block HTML tags and a set/stack of active inline HTML tags.
- `html()` emits block HTML, closes any previous tag with the same id, computes closing tags, and stacks them unless id `-` means immediate close.
- `closehtml()` closes all remaining block tags.
- `ihtml()` manages inline tag changes, closing/reopening nested inline tags as needed.
- `hideihtml()` and `showihtml()` temporarily suppress/reemit inline tags around breaks and block transitions.
- `r_html()` implements `.html` and `.ihtml` raw requests, reading a line in HTML mode and converting raw `<`, `>`, `&`, and spaces to internal sentinels.
- `htmlinit()` registers raw requests, escape handlers, and default font-to-HTML mapping macros.

Notable concerns: `closingtag()` is a heuristic parser for tag strings; it handles ordinary tags and self-closing/closing tags but is not a general HTML parser.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/htmlroff/html.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/htmlroff/input.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/htmlroff/input.c

Input stack implementation for `htmlroff`.

- Defines `Istack` entries for file-backed input, string-backed input, unget runes, line number, logical name, completion callback, and next pointer.
- Supports pushing or queueing input files, stdin, and strings.
- Maintains current top `istack` and bottom `ibottom`.
- Updates `.F` and `.B` registers/strings with current file name and basename-like value.
- `getrune()` reads from unget buffer, string buffer, or `Biobuf`, popping exhausted sources automatically.
- `ungetrune()` pushes back up to three runes, creating an empty input frame if necessary.
- Provides line formatting and line-number/name update helpers.

Dependencies are Plan 9 `bio`, rune helpers, and register/string helpers declared in `a.h`.

Notable concerns: unget storage is small, and input-source ownership is manual. `dup(0, b->fid)` is used to make a Bio wrapper around stdin via an initially opened `/dev/null`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/htmlroff/input.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/htmlroff/main.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/htmlroff/main.c

Command-line driver for `htmlroff`.

- Supports `htmlroff [-iuv] [-m mac] [-r an] [file...]`.
- Initializes output `Biobuf`, `%L` line formatter, and quote formatting.
- `-m` queues a troff macro file from `/sys/lib/tmac/tmac.<name>`.
- `-r` initializes a number register from a compact `namevalue` argument.
- `-u` enables UTF-8 mode; `-v` enables verbose mode; `-i` forces stdin in addition to file inputs.
- Queues named files or stdin, then calls `run()` and terminates output.

Dependencies are `a.h` and the broader `htmlroff` request/parser implementation.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/htmlroff/main.c -->