# Group Research: group_154_9front_sources_os_plan9_9front_sys_src_cmd_hjfs_fs1_c_sources_os_pla_df6d72c05381

Scope: `Docs/research_subset_a.md`, specifically `sources/os/plan9/9front`. I read every listed source file completely.

This group covers several 9front command areas: `hjfs` filesystem internals, the `hoc` calculator/interpreter, HTML-to-text/roff converters, image conversion/filtering/histogram tools, boot/init and I/O utilities, IPv6 tunnel clients, and the front half of a CIFS/SMB server.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/hjfs/fs1.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/hjfs/fs1.c

Implements core `hjfs` filesystem storage operations: reference counts, free block allocation, root creation, filesystem reaming, location tracking, copy-on-write block lookup, truncation, directory entry search, deletion, and directory-entry allocation.

Key points:
- `chref`, `getfree`, and `putfree` manage block reference counts in reference blocks and maintain a small free-block channel cache.
- `ream` initializes a fresh filesystem: writes the superblock, initializes reference blocks, reserves metadata blocks, creates root/dump-root dentries, syncs, and later writes the default user database.
- `initfs` loads the superblock, initializes root `Loc` objects for normal and dump views, creates the free-list channel, and loads `/adm/users`.
- `getloc`, `cloneloc`, `putloc`, and `haveloc` maintain an in-memory location tree with references, child links, global links, and delayed deletion for `LGONE` entries.
- `dumpblk` copies shared blocks for snapshots/copy-on-write and increments child block references for indirect and directory-entry blocks.
- `getblk` resolves direct and multi-level indirect file blocks, optionally allocating or copy-on-writing blocks for write/create/overwrite modes.
- `trunc`, `delindir`, and `delindirpart` release file block trees while respecting shared reference counts.
- `findentry`, `newentry`, `delete`, and `deltraverse` implement directory scans, free-slot allocation, duplicate-name detection, recursive directory deletion, and qid/location validation.
- `modified` updates timestamps, mutating user id, and qid version.

Dependencies and interactions:
- Uses `dat.h`/`fns.h` types such as `Fs`, `Dev`, `Buf`, `Dentry`, `FLoc`, `Loc`, and block constants.
- Calls buffer-cache functions (`getbuf`, `putbuf`), channel/file operations (`chanattach`, `chanwalk`, `chancreat`, `chanopen`), user database functions (`userssave`, `usersload`), and permission-sensitive mutation hooks (`willmodify`, `sync`).
- Provides lower-level services used by `fs2.c` channel operations.

Research relevance:
- This is the main on-disk metadata engine for `hjfs`, including allocator correctness, snapshot/copy-on-write behavior, and directory lifecycle semantics.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/hjfs/fs1.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/hjfs/fs2.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/hjfs/fs2.c

Implements the channel-level `hjfs` file API over the lower-level block and dentry primitives in `fs1.c`.

Key points:
- `chanattach` and `chanclone` create file channels rooted at either the live root or dump root.
- `chanwalk` validates directory traversal permissions, handles `.`, `..`, and named entries, and updates `Loc` references.
- `namevalid` rejects empty names, `.`/`..`, slash, control characters, and overlong names.
- `chancreat` validates permissions and read-only flags, allocates a new directory entry, assigns a qid, initializes the new dentry, inherits parent group, and opens the created object as requested.
- `chanopen` enforces read-only/permission/open-mode rules, handles append and truncate semantics, and implements Plan 9 exclusive-file locking with timeout.
- `chanread` reads regular files by block, returns zero-filled holes, and delegates directory reads to `chandirread`.
- `chanwrite` performs copy-on-write/overwrite-aware block writes, honors append mode, updates file size, and marks metadata modified.
- `statbuf`, `chanstat`, and `chandirread` serialize dentries into Plan 9 `Dir` structures for stat and directory reads.
- `chanclunk` releases channels, handles `ORCLOSE` removal, delays deletion for referenced entries, clears exclusive locks, and releases location chains.
- `chanwstat` implements rename, length changes, owner/group changes, mode changes, permission checks, and parent timestamp updates.
- `chanremove` is implemented by setting `CHRCLOSE` and clunking.

Dependencies and interactions:
- Depends on `fs1.c` functions such as `getdent`, `findentry`, `newentry`, `getblk`, `trunc`, `modified`, `delete`, `getloc`, and `putloc`.
- Uses user/group helpers such as `uid2name`, `name2uid`, `ingroup`, and `permcheck`.
- Works under `chbegin`/`chend` read locks unless channel flags suppress locking.

Research relevance:
- This file is the user-visible filesystem operation layer for `hjfs`, mapping Plan 9 file semantics onto the dentry/block implementation.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/hjfs/fs2.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/hjfs/main.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/hjfs/main.c

Provides the `hjfs` program entry point, global errors, allocation helpers, daemon startup, periodic sync, and shutdown.

Key points:
- Defines common error strings used by the filesystem implementation.
- Provides fatal allocation wrappers `emalloc`, `erealloc`, and `estrdup` with malloc/realloc tags.
- `getthrdata` lazily allocates thread-local response state and a response channel.
- `dprint` prefixes debug output with `hjfs:`.
- `syncproc` calls `sync(0)` periodically at `SYNCINTERVAL`.
- `threadmain` parses options:
  - `-A` enables authentication by clearing `FSNOAUTH`.
  - `-r` reams the filesystem.
  - `-S` disables permission checks and allows chown.
  - `-s` serves over stdio.
  - `-f` selects backing device/file.
  - `-n` sets service name.
  - `-m` sets buffer memory budget.
  - `-a` adds announce addresses.
- Initializes the buffer cache, backing device, filesystem, console, sync process, and 9P service.
- `shutdown` write-locks the filesystem, syncs twice, logs, and exits all threads.

Dependencies and interactions:
- Calls `bufinit`, `newdev`, `initfs`, `initcons`, `start9p`, and `sync`.
- Uses Plan 9 thread and process primitives.

Research relevance:
- This file defines how `hjfs` is configured and launched, including reaming, serving mode, authentication/permission flags, and shutdown durability behavior.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/hjfs/main.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/hoc/code.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/hoc/code.c

Implements the virtual machine/runtime for the `hoc` calculator language.

Key points:
- Maintains a fixed-size value stack, instruction array, program counter, current code-generation pointer, and function/procedure call frame stack.
- Provides stack primitives `push`, `pop`, and `xpop`.
- Emits bytecode-like instructions with `code()` and runs them with `execute()`.
- Implements control-flow instructions for `while`, `for`, and `if` by executing saved instruction spans and updating `pc`.
- Implements function/procedure definition and call support:
  - `define` stores code start, formals, and arity.
  - `call` checks arity, saves formal variable values, binds arguments, and executes function code.
  - `restore`, `restoreall`, `funcret`, and `procret` restore dynamic bindings and manage return values.
- Implements arithmetic, comparison, logical, power, unary, assignment, compound assignment, pre/post increment/decrement, builtin-function call, variable evaluation, print, string print, and read-into-variable operations.
- Uses `execerror` for stack overflow/underflow, undefined variables, non-variable assignments, division by zero, and bad returns.

Dependencies and interactions:
- Includes `hoc.h` and yacc token definitions from `y.tab.h`.
- Uses symbol table functions from `symbol.c`, math wrappers from `math.c`, and parser-generated code from `hoc.y`.
- Uses Plan 9 `Biobuf` input for `read()` expressions.

Research relevance:
- This is the core interpreter runtime for `hoc`, separating grammar/code generation from executable semantics.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/hoc/code.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/hoc/hoc.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/hoc/hoc.h

Declares the shared data structures and function prototypes for the `hoc` interpreter.

Key points:
- Defines `Inst` as a function-pointer instruction type and `STOP` as the null instruction.
- Defines:
  - `Symbol` for names, token/type, value/definition/string payload, and symbol-list link.
  - `Symval` union for numeric values, builtin function pointers, function definitions, and strings.
  - `Datum` stack union for numbers or symbol references.
  - `Saveval` for saved formal-variable values during calls.
  - `Formal` for formal parameter lists.
  - `Fndefn` for function/procedure code pointers, formals, and arity.
- Declares symbol, VM, arithmetic, control-flow, call/return, parser, initialization, allocation, and math helper functions.
- Exposes global code-generation pointers `progp`, `progbase`, and `prog`.

Dependencies and interactions:
- Shared by `code.c`, `hoc.y`, `init.c`, `math.c`, and `symbol.c`.
- Token constants are supplied separately by `y.tab.h`.

Research relevance:
- This file is the ABI between the lexer/parser, symbol table, math wrappers, and VM runtime.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/hoc/hoc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/hoc/hoc.y -->
# File Research: sources/os/plan9/9front/sys/src/cmd/hoc/hoc.y

Defines the yacc grammar, lexer, input handling, and top-level execution loop for `hoc`.

Key points:
- Grammar supports assignments, compound assignments, statements, returns, function/procedure calls, print lists, while/for/if/else, blocks, arithmetic, comparisons, logical operators, builtins, `read(var)`, pre/post increment/decrement, and function/procedure definitions.
- Grammar actions emit VM instructions using `code`, `code2`, and `code3`.
- Function/procedure definitions set symbol types, mark parser state as inside a definition, collect formals, emit a default `procret`, and call `define`.
- `yylex` tokenizes whitespace, backslash-newline continuations, `#` comments, numbers, identifiers, UTF-8-ish names, quoted strings with escapes, operators, and newlines.
- Unknown identifiers are installed as `UNDEF` and returned as `VAR`.
- `moreinput` supports stdin, file arguments, and `-e` inline expressions via temporary files.
- `run` uses `setjmp`/`longjmp` recovery and repeatedly initializes code, parses one top-level unit, and executes generated code.
- `execerror`, `yyerror`, `warning`, `fpecatch`, and `intcatch` provide error reporting and recovery.

Dependencies and interactions:
- Includes `hoc.h`, Plan 9 `Biobuf`, libc, and ctype.
- Calls VM functions from `code.c`, symbol functions from `symbol.c`, and initialization from `init.c`.

Research relevance:
- This file defines the language syntax and user-facing input/error behavior of `hoc`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/hoc/hoc.y -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/hoc/init.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/hoc/init.c

Installs `hoc` keywords, constants, and builtin functions into the symbol table.

Key points:
- Registers keywords: `proc`, `func`, `return`, `if`, `else`, `while`, `for`, `print`, and `read`.
- Registers constants: `PI`, `E`, `GAMMA`, `DEG`, and `PHI`.
- Registers builtins: trigonometric functions, checked inverse/hyperbolic/log/exp/sqrt wrappers, integer conversion, and absolute value.
- Builtin symbols are initially installed as `BLTIN`, then their function pointer is written to `s->u.ptr`.

Dependencies and interactions:
- Uses token values from `y.tab.h`.
- Calls `install` from `symbol.c`.
- Checked builtin wrappers are implemented in `math.c`.

Research relevance:
- This file defines the initial language environment available to every `hoc` session.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/hoc/init.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/hoc/math.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/hoc/math.c

Provides checked math wrappers for `hoc` builtins.

Key points:
- Wraps `log`, `log10`, `sqrt`, `exp`, `asin`, `acos`, `sinh`, `cosh`, and `pow`.
- `integer` rejects values outside signed 32-bit integer range before casting to `long`.
- `errcheck` raises `execerror` on NaN results as domain errors and infinity results as range errors.

Dependencies and interactions:
- Uses Plan 9 `isNaN` and `isInf`.
- Reports runtime errors via `execerror` from `hoc.y`.
- Registered by `init.c`.

Research relevance:
- This file turns raw libc math behavior into recoverable interpreter errors.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/hoc/math.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/hoc/symbol.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/hoc/symbol.c

Implements the `hoc` symbol table, checked allocation, and formal-parameter list construction.

Key points:
- Maintains a simple linked-list symbol table.
- `lookup` scans for an exact name match.
- `install` allocates a `Symbol`, copies the name, sets type/value, and prepends it to the list.
- `emalloc` wraps `malloc` and raises `execerror` on allocation failure.
- `formallist` prepends a formal parameter to a formal list and initializes its saved-value stack.

Dependencies and interactions:
- Used by `hoc.y`, `init.c`, and `code.c`.
- Relies on `execerror` for fatal allocation handling.

Research relevance:
- This is the interpreter’s name storage layer and formal-parameter data structure support.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/hoc/symbol.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/html2ms.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/html2ms.c

Implements a standalone loose HTML parser that emits `ms`/`tbl` roff markup.

Key points:
- Defines lightweight `Tag`, `Attr`, `Text`, and `Table` structures for parsing and output state.
- Maintains output buffer growth, rune emission, line position, whitespace collapsing, preformatted mode, font style, font size, and hidden-output state.
- Converts common HTML tags:
  - paragraphs/headings/lists/br/hr/pre to `.LP`, `.SH`, `.IP`, `.br`, `.DS/.DE`
  - emphasis/bold/code/small/big/sub/sup to font/size/vertical roff escapes
  - quotes to `.QS/.QE` or `.QP`
  - tables to `.TS/.TE` with generated cell formats and `T{...T}` enclosure
- Implements a small class/style recognizer for spans (`bold`, `italic`, `subscript`, `superscript`, and `text-align: center`).
- Skips or self-closes metadata, head, style, script, link, meta, and image-like content.
- Parses comments, CDATA-ish blocks, attributes with quoted or unquoted values, tags, HTML entity basics, UTF-8 runes, and text.
- Escapes leading `.` and backslashes so generated roff remains safe.
- Handles nested tables by flattening inner table cells into the nearest outer table.

Dependencies and interactions:
- Uses Plan 9 `Biobuf`, UTF/Rune helpers, ctype, and libc.
- Does not depend on Plan 9 `<html.h>`; it implements parsing itself.

Research relevance:
- This is a purpose-built converter from HTML-ish input to Plan 9 roff/ms output, useful for understanding text-conversion tooling outside filesystem code.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/html2ms.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/htmlfmt/dat.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/htmlfmt/dat.h

Defines shared structures, globals, and prototypes for `htmlfmt`.

Key points:
- Defines `Bytes`, a growable byte buffer.
- Defines `URLwin`, a minimal document/render context with input/output fds, document type, URL, parsed items, and document metadata.
- Declares global options `url`, `aflag`, and `width`.
- Declares HTML loading/rendering, URL window cleanup, allocation/string helpers, error reporting, and buffer growth functions.
- Sets stack and event constants, though this command mostly uses batch rendering.

Dependencies and interactions:
- Uses `Item` and `Docinfo` from Plan 9 `<html.h>`.
- Shared by `html.c`, `main.c`, and `util.c`.

Research relevance:
- This is the small internal interface for the `htmlfmt` command.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/htmlfmt/dat.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/htmlfmt/html.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/htmlfmt/html.c

Renders Plan 9 `<html.h>` parsed document items to wrapped plain text.

Key points:
- `loadhtml` reads all input into a `Bytes` buffer, builds a `URLwin`, calls `rendertext`, and frees parsed document state.
- `rendertext` converts the current URL to runes and calls `parsehtml` to obtain item lists and document metadata.
- Word wrapping uses globals `inword`, `col`, and `wordi`; `emitword` inserts spaces unless the preceding output is whitespace or the word begins with closing punctuation.
- `renderrunes` collapses spaces, preserves blank-line limits, and wraps at `width`.
- URL handling:
  - `baseurl` extracts a scheme/authority/path base using a regexp.
  - `fullurl` resolves relative hrefs against the document URL.
- `render` walks item lists:
  - text is wrapped or emitted as a word depending on `IFwrap`
  - rules render as separator lines
  - images/forms are shown only with `-a`
  - tables render by recursively rendering each cell
  - floats recurse into contained items
  - spacers emit spaces
  - anchors render as numeric references or full URLs depending on `-a`
- `rerender` emits title text, rendered body, and optional reference list.

Dependencies and interactions:
- Uses Plan 9 `<html.h>` structures (`Item`, `Itext`, `Iimage`, `Itable`, `Anchor`, etc.).
- Uses utility functions from `util.c`.

Research relevance:
- This is a text extractor/formatter built around the Plan 9 HTML parser, complementary to the hand-rolled `html2ms.c`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/htmlfmt/html.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/htmlfmt/main.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/htmlfmt/main.c

Provides option parsing, charset conversion setup, and file iteration for `htmlfmt`.

Key points:
- Options:
  - `-a` prints full URLs/images/form markers inline.
  - `-c charset` selects input charset for `/bin/uhtml`.
  - `-l`/`-w` sets wrap width.
  - `-u URL` sets base URL.
- `uhtml` runs `/bin/uhtml -c <charset>` through a pipe, falling back to `/bin/cat` in the child if `uhtml` exec fails.
- Processes stdin when no files are supplied, otherwise opens each file and passes it through `uhtml` into `loadhtml`.
- Reports processing errors with the file name and exits with the error string.

Dependencies and interactions:
- Uses `loadhtml` from `html.c`.
- Uses Plan 9 process, pipe, fd, and exec primitives.

Research relevance:
- This file defines how `htmlfmt` is invoked and how charset normalization is inserted before parsing.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/htmlfmt/main.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/htmlfmt/util.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/htmlfmt/util.c

Provides allocation, string, error, and buffer utilities for `htmlfmt`.

Key points:
- `emalloc` and `erealloc` fatal-exit on allocation failure.
- `estrdup`, `estrstrdup`, `eappend`, and `egrow` build heap strings, with `eappend` freeing the previous base string.
- `error` formats an error to fd 2 and exits; it prefixes messages with `Mail:`, likely inherited from related mail/web tooling.
- `growbytes` expands a `Bytes` buffer in 8000-byte increments, appends data, and NUL-terminates.

Dependencies and interactions:
- Shared by `html.c` and `main.c`.
- Uses Plan 9 `Fmt` for error formatting.

Research relevance:
- This is support code for robust batch rendering and URL/string assembly.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/htmlfmt/util.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/htmlroff/a.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/htmlroff/a.h

Declares the shared interface and constants for `htmlroff`, a troff-to-HTML converter.

Key points:
- Defines private Unicode/rune sentinels for HTML-sensitive/raw characters, nonbreaking space, empty output, formatted diversion markers, and symbol variants.
- Defines units (`UPI`, `UPX`) and input mode bits (`CopyMode`, `ExpandMode`, `ArgMode`, `HtmlMode`).
- Declares request/escape registration, macro/string/register operations, input stack operations, HTML output/tag functions, roff evaluation, output functions, warning/allocation helpers, and section initializers `t1init` through `t20init`.
- Declares global state such as control characters, output buffer, input mode, request state, verbosity, and line position.
- Defines rune allocation convenience macros and installs `%L` format checking.

Dependencies and interactions:
- Included by all `htmlroff` source files.
- Coordinates the central dispatcher in `roff.c` with section-specific modules.

Research relevance:
- This header is the primary internal contract for the `htmlroff` interpreter/converter.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/htmlroff/a.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/htmlroff/char.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/htmlroff/char.c

Maps troff two-character special names to Unicode runes.

Key points:
- Maintains a static translation table initialized on first use.
- Seeds translations for plus/equal/minus symbols, em/en dashes, and prime.
- Reads `/sys/lib/troff/font/devutf/utfmap` to populate additional troff escape mappings.
- `troff2rune` accepts a two-rune troff name and returns the mapped Unicode rune or `Runeerror`.
- Warns if the fixed translation table fills.

Dependencies and interactions:
- Used by `t2.c` for `\(` special character escapes.
- Uses Plan 9 `Biobuf`, `getfields`, and UTF conversion routines.

Research relevance:
- This avoids duplicating troff character maps in source and ties `htmlroff` output to the system troff font mapping.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/htmlroff/char.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/htmlroff/html.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/htmlroff/html.c

Manages explicit and inline HTML tags emitted by `htmlroff`.

Key points:
- Keeps two tag stacks:
  - `tagstack` for block-like `.html` tags that can be closed by id.
  - `tagset` for inline `.ihtml` tags such as current font spans.
- `closingtag` derives closing tags from an opening HTML snippet and handles self-closing/open-close cases.
- `html` emits a block tag, closes any previous tag with the same id, and tracks auto-closing unless id is `-`.
- `closehtml` closes all remaining block tags at EOF.
- `ihtml` toggles inline tags by id, emits close/reopen sequences to keep nesting valid, and avoids duplicate opens.
- `hideihtml` and `showihtml` temporarily close/reopen inline tags around paragraph breaks or raw tag emission.
- Defines escapes for raw `<`, `>`, `&`, quotes, backticks, and minus sentinels.
- `r_html` implements `.html` and `.ihtml` raw requests, translating literal HTML characters into sentinel runes.
- `htmlinit` registers HTML raw requests/escapes and defines the default `font` macro mapping roff font/size state to HTML spans/tags.

Dependencies and interactions:
- Called by `roff.c` paragraph/output logic and font macros.
- Uses string/register functions from `t8.c`.

Research relevance:
- This is the output correctness layer that keeps generated HTML tags balanced despite roff’s stateful formatting model.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/htmlroff/html.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/htmlroff/input.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/htmlroff/input.c

Implements the input stack for `htmlroff`.

Key points:
- `Istack` entries represent input from files, strings/macros, or stdin, with unget buffers, line numbers, names, and pop callbacks.
- Supports pushing immediate input or queueing input after the current bottom entry.
- `pushinputfile`/`queueinputfile` open named files as `Biobuf`s.
- `pushstdin`/`queuestdin` bind stdin through a duplicate fd.
- `pushinputstring` pushes rune-string input, mainly for macros, strings, and register expansion.
- `inputnotify` installs a callback called when the current input source is popped.
- `getrune` pulls from unget, string, or file input, updates line numbers, and pops exhausted inputs.
- `ungetrune` supports up to three pushed-back runes, creating an empty string input if needed.
- `linefmt` reports the active file-backed input and line for diagnostics.
- `setlinenumber` updates the visible file name/line, supporting `.lf`.

Dependencies and interactions:
- Used by `roff.c`, macro expansion in `t7.c`, file switching in `t19.c`, and diagnostics.
- Maintains `.F` and `.B` number/string registers when file input changes.

Research relevance:
- This file is the source-location and input-composition layer for the roff interpreter.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/htmlroff/input.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/htmlroff/main.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/htmlroff/main.c

Provides the `htmlroff` command entry point.

Key points:
- Converts troff `-ms`-style input to HTML.
- Options:
  - `-i` also reads stdin after named inputs.
  - `-m mac` queues `/sys/lib/tmac/tmac.<mac>`.
  - `-r an` sets a one-letter number register to the supplied value.
  - `-u` is accepted as legacy/default.
  - `-v` enables verbose warnings/debug output.
- Queues named input files or stdin, initializes output `Biobuf`, installs `%L` line formatter, then calls `run`.
- Emits a final newline, flushes output, and exits.

Dependencies and interactions:
- Uses input queueing from `input.c`, register setting from `t8.c`, and the main interpreter in `roff.c`.

Research relevance:
- Defines command-line integration for the roff-to-HTML interpreter.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/htmlroff/main.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/htmlroff/roff.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/htmlroff/roff.c

Implements the central `htmlroff` roff dispatcher, input loop, paragraph generation, escape handling, and output emission.

Key points:
- Maintains fixed tables for regular requests, raw requests, and escape handlers.
- Provides `addreq`, `delreq`, `renreq`, `addraw`, `delraw`, `renraw`, and `addesc`.
- `getnext` fetches logical input characters, expanding registered escapes depending on input mode and handling formatted diversion markers.
- `_readx`, `copyarg`, `readline`, and `parseargs` parse request arguments and lines under different expansion/copy modes.
- `dotline` dispatches dot/tick requests to raw handlers, regular handlers, or user-defined macros.
- `newline`, `startoutput`, and `br` translate roff line/paragraph state into styled HTML paragraph tags.
- `runinput` is the main loop: detects requests at beginning of line, handles newlines/traps, starts output, shows inline tags, and writes characters/tabs.
- `run` initializes all supported section modules, registers extra `margin`, sets defaults, runs input, invokes EOF macro, and closes HTML tags.
- `outrune` maps private sentinels to HTML-safe output, handles non-fill spaces, plus/equal/minus symbol output, prime as superscript, and optional diversion callback.
- Includes no-op/warning request and escape handlers for unsupported features.

Dependencies and interactions:
- Calls every `t*.c` initializer, `htmlinit`, input-stack functions, macro functions, register functions, and HTML output functions.
- `t9init` and `t12init` are commented out in `run`, so tabs/fields and drawing/overstrike escapes are not active despite `t12.c` existing.

Research relevance:
- This is the core interpreter loop and output engine for `htmlroff`; most section modules register behavior into this dispatcher.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/htmlroff/roff.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/htmlroff/t1.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/htmlroff/t1.c

Implements basic numeric expression parsing and time-related initialization for `htmlroff`.

Key points:
- `scale2units` maps troff scale suffixes to internal units: inches, centimeters, picas, ems, ens, points, basic units, vertical spacing, and pixels.
- `eval`, `evalscale`, and `eval0` parse integer/fractional numeric expressions with optional scale suffixes.
- Supports parentheses, unary minus, arithmetic, comparisons, bitwise-style `&`, and `:` as OR.
- Handles divide/modulo by zero with diagnostic fallback to divisor 1.
- `t1init` initializes date number registers `dw`, `dy`, `mo`, and `yr`.

Dependencies and interactions:
- Used throughout request handlers to interpret roff numeric arguments.
- Uses current point size and vertical spacing registers for scalable units.

Research relevance:
- This file is foundational for interpreting roff request parameters in later modules.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/htmlroff/t1.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/htmlroff/t10.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/htmlroff/t10.c

Implements input/output conventions and character-translation related roff requests/escapes.

Key points:
- `.ec` sets the escape character; `.eo` disables it.
- `.cc` and `.c2` set the normal and no-break control characters.
- `.lg`, `.ul`, and underline/font helpers are treated as no-ops; `.tr` warns.
- Registers raw comment handling for `.\"`.
- Escapes:
  - `\!` copies the rest of the line directly to output.
  - `\X'...'` emits device-control-like text until quote/newline.
  - `\"` starts a comment except in argument mode where it is preserved for argument parsing.
  - escaped newline disappears.
  - `\e` emits the current escape character.

Dependencies and interactions:
- Updates global `backslash`, `dot`, and `tick` used by `roff.c`.
- Uses `readline`, `out`, `outrune`, and warning helpers.

Research relevance:
- This file handles roff lexical-control features that affect how the rest of the interpreter sees input.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/htmlroff/t10.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/htmlroff/t11.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/htmlroff/t11.c

Implements local motion and width-related escapes for `htmlroff`.

Key points:
- `e_0` returns a digit-width space as a normal space.
- `dv` tracks vertical displacement in `.dv` and emits/removes an inline sub/sup HTML tag through `.ihtml`.
- `\v`, `\u`, `\d`, and `\r` adjust vertical displacement.
- `\h` consumes a quoted horizontal motion and emits nothing.
- `\w'...'` returns the rune length of the quoted argument and sets related registers `st`, `sb`, and `ct` to zero.
- `\k` consumes a register name and warns that horizontal position marks are unavailable.
- Also registers no-op escapes for `\|` and `\^`.

Dependencies and interactions:
- Uses `ihtml` from `html.c`, number registers from `t8.c`, and `getqarg` from `t2.c`.

Research relevance:
- This provides partial support for local motion constructs, primarily enough to represent sub/sup positioning in HTML.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/htmlroff/t11.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/htmlroff/t12.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/htmlroff/t12.c

Contains handlers for overstrike, bracket, line-drawing, and graphics escapes, but its initializer is not called by `roff.c`.

Key points:
- `\o'...'` and `\b'...'` push their quoted argument back into input.
- `\z` consumes one logical character and emits nothing.
- `\l`, `\L`, and `\D` consume quoted arguments and emit nothing.
- `t12init` registers these escapes, but `run()` in `roff.c` has the `t12init()` call commented out.

Dependencies and interactions:
- Uses `getqarg`, `pushinputstring`, and `getnext`.

Research relevance:
- This file documents intended partial support for drawing/overstrike escapes, but active `htmlroff` behavior omits it.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/htmlroff/t12.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/htmlroff/t13.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/htmlroff/t13.c

Registers hyphenation-related roff requests as no-ops.

Key points:
- `.nh`, `.hy`, `.hc`, and `.hw` are accepted and ignored.
- `\%` is registered as a no-op escape.

Dependencies and interactions:
- Uses generic no-op handlers from `roff.c`.

Research relevance:
- This makes hyphenation input accepted without implementing hyphenation behavior in HTML output.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/htmlroff/t13.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/htmlroff/t14.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/htmlroff/t14.c

Implements limited three-part title support, mainly line-title length.

Key points:
- `.lt` sets or adjusts the `.lt` register, defaulting to 6.5 inches if no argument is supplied.
- Supports absolute, `+`, and `-` adjustments.
- `.tl` warns as unsupported.
- `.pc` page-number-character request is accepted as a no-op.

Dependencies and interactions:
- Uses number-register and numeric-scale helpers.

Research relevance:
- This file preserves some title-related state while explicitly not implementing full title rendering.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/htmlroff/t14.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/htmlroff/t15.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/htmlroff/t15.c

Registers output line-numbering requests as warnings.

Key points:
- `.nm` and `.nn` are accepted but warn as ignored/unsupported.

Dependencies and interactions:
- Uses generic warning handler from `roff.c`.

Research relevance:
- Marks line-numbering as unsupported while allowing input files using it to continue.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/htmlroff/t15.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/htmlroff/t16.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/htmlroff/t16.c

Implements conditional input acceptance for `.if`, `.ie`, and `.el`.

Key points:
- Supports numeric conditions, negation, simple condition letters, and quoted string comparisons.
- Treats `o`, `t`, and `h` conditions as true; `n` and `e` as false.
- `.ie` records condition truth on a stack for matching `.el`.
- `startbody` positions input at the conditional body; `skipbody` skips to newline while respecting `\{...\}` groups.
- Registers no-op `\{` and `\}` escapes in HTML/argument modes.

Dependencies and interactions:
- Uses raw request registration, input primitives, expression evaluation, and `iftrue` stack state.

Research relevance:
- This file gives the converter enough conditional processing to handle many macro packages.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/htmlroff/t16.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/htmlroff/t17.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/htmlroff/t17.c

Implements basic roff environment switching.

Key points:
- Defines an `Env` snapshot containing point size, font, fill, adjustment, centering, vertical spacing, line spacing, and input trap state.
- Initializes three environments from `defenv`.
- `saveenv` captures current registers; `restoreenv` writes them back, updates `.ev`, and reruns the `font` macro.
- `.ev` with no argument pops the previous environment; with an argument saves the current environment and switches to environment 0-2.
- Warns and clamps bad environment numbers; detects stack overflow/underflow.

Dependencies and interactions:
- Uses number registers and font macro execution.

Research relevance:
- This preserves enough roff environment state for macro packages that switch formatting contexts.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/htmlroff/t17.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/htmlroff/t18.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/htmlroff/t18.c

Implements insertion from standard input and termination behavior.

Key points:
- `.rd` optionally prints a prompt/BEL on console input, reads stdin until a blank line, stores the text in temporary string `.rd`, and runs it as a macro body with remaining arguments.
- Lazily initializes a `Biobuf` for stdin.
- `.ex` terminates processing by popping all input sources.

Dependencies and interactions:
- Uses macro/string support from `t7.c`/`t8.c` and input stack popping from `input.c`.

Research relevance:
- This supports interactive roff input insertion and explicit early termination.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/htmlroff/t18.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/htmlroff/t19.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/htmlroff/t19.c

Implements input/output file switching and simple external input piping.

Key points:
- `.so` pushes a source file.
- `.nx` ends current/all input and optionally switches to another file.
- `.sy` and `.pi` warn as unimplemented.
- `.cf` copies a named file directly to output rune-by-rune.
- `.inputpipe` forks `/bin/rc -c <cmd>`, writes a generated troff setup plus body lines to the child until a stop marker, waits for completion, and fails on child error.
- Initializes `$$` register to the process id.

Dependencies and interactions:
- Uses input stack functions, output functions, register functions, and Plan 9 fork/pipe/wait.

Research relevance:
- This file handles roff include/switch/copy behavior and a limited preprocessor-like pipe mechanism.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/htmlroff/t19.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/htmlroff/t2.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/htmlroff/t2.c

Implements font, character size, and special character handling for `htmlroff`.

Key points:
- `getqarg` reads single-quoted escape arguments.
- `\N'...'` emits a numeric character code.
- `\(` maps two-character troff names through `troff2rune`.
- Maintains a 10-entry font-position table.
- `ft` changes current font, supports previous font `P`/`0`, numeric positions, and mounted font names.
- `.ft` changes font; `.fp` mounts a font name at a position.
- `\f` reads a font name/number and changes font.
- `ps` changes point size and reruns the `font` macro.
- `.ps` and `\s` support absolute and relative point-size changes, including one- and two-digit forms.
- `t2init` mounts default fonts R/I/B/BI/CW, initializes size registers, registers requests/escapes, and warns on unsupported spacing/emboldening requests.

Dependencies and interactions:
- Uses `html.c` default `font` macro to translate font state to HTML tags/spans.
- Uses `char.c` for special character mapping and `t8.c` number registers.

Research relevance:
- This is the main bridge from troff font/size controls to HTML inline markup.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/htmlroff/t2.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/htmlroff/t20.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/htmlroff/t20.c

Implements miscellaneous roff requests.

Key points:
- `.mc` warns as unsupported.
- `.tm` writes the rest of the line to stderr.
- `.ab` writes a message like `.tm` and exits with `.ab`.
- `.lf` sets the current line number and optionally file name for diagnostics.
- `.pm` prints macro/string definitions or total size.
- `.fl` flushes output.
- Notes that `.ig` is handled as a macro-definition variant in `t7.c`.

Dependencies and interactions:
- Uses string printing from `t8.c`, input location setting from `input.c`, and output `Biobuf`.

Research relevance:
- This file supplies diagnostic/control features used by roff macro packages.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/htmlroff/t20.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/htmlroff/t3.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/htmlroff/t3.c

Implements limited page-control handling.

Key points:
- Maintains page offset registers `.o` and `.o0`.
- `.po` sets/restores/adjusts page offset using vertical-scale parsing.
- Initializes `.o`, `.o0`, and page length `.p`.
- Registers `.pl`, `.pn`, and `.rt` as warnings; `.bp`, `.ne`, and `.mk` as no-ops.

Dependencies and interactions:
- Used by paragraph style generation in `roff.c`, where `.o` contributes to margins.

Research relevance:
- This maps a subset of page geometry into HTML paragraph margin calculations while ignoring page-breaking concepts.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/htmlroff/t3.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/htmlroff/t4.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/htmlroff/t4.c

Implements text filling, centering, and adjustment controls.

Key points:
- `\ ` emits nonbreaking space.
- `\&` emits the private zero-width empty marker.
- `\c` consumes the following raw rune, sets beginning-of-line state, and suppresses output.
- `.br` forces a paragraph break.
- `.fi` and `.nf` toggle fill mode via `.fi`.
- `.ad` sets adjustment mode `.j` for left, right, center, justify, or numeric modes.
- `.na` disables adjustment.
- `.ce` sets the count of next lines to center.
- Initializes fill mode and adjustment defaults.

Dependencies and interactions:
- `roff.c` reads `.fi`, `.j`, and `.ce` when emitting newlines and starting paragraphs.

Research relevance:
- This file controls how roff line layout maps to HTML text alignment and paragraph breaks.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/htmlroff/t4.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/htmlroff/t5.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/htmlroff/t5.c

Implements vertical spacing and no-space mode.

Key points:
- `.vs` sets/restores/adjusts vertical baseline spacing registers `.v` and `.v0`.
- `.ls` sets/restores line spacing registers `.ls` and `.ls0`.
- `sp` ends the current paragraph and emits an empty paragraph with a computed bottom margin.
- `.sp` and `.sv` call `sp`, with absolute spacing mostly ignored.
- `.ns` enables no-space mode; `.rs` clears it.
- Initializes default vertical spacing to 12 points and line spacing to 1.

Dependencies and interactions:
- `roff.c` uses `.v` and `.ls` to compute paragraph line height.

Research relevance:
- This translates vertical-space requests to approximate HTML paragraph spacing.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/htmlroff/t5.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/htmlroff/t6.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/htmlroff/t6.c

Implements line length and indent controls.

Key points:
- `.ll` sets/restores/adjusts line length register `.l`.
- `.in` breaks output, sets/restores/adjusts indent `.i`, and clears temporary indent `.ti`.
- `.ti` breaks output and sets temporary indent `.ti`.
- Initializes default line length to 6.5 inches.

Dependencies and interactions:
- `roff.c` uses `.l`, `.i`, `.ti`, and page offset to compute paragraph margins and text indentation.

Research relevance:
- This file maps roff horizontal layout state into HTML CSS margin/indent values.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/htmlroff/t6.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/htmlroff/t7.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/htmlroff/t7.c

Implements macros, strings, diversions, and simple traps for `htmlroff`.

Key points:
- `runmacro` looks up a macro/string by name, saves arguments on a macro stack, pushes macro text as input, and updates `.$`.
- `runmacro1` executes a macro immediately via a `setjmp`-controlled input run, used for internal hooks such as `font` and `eof`.
- `.de`, `.am`, and `.ig` define, append, or ignore macro bodies until an end marker.
- `.ds` and `.as` define/append strings as raw requests.
- `.rm` removes requests/raw handlers/strings; `.rn` renames them.
- Diversions `.di`/`.da` redirect output through `outcb`, capture formatted output between private markers, and append/store it in strings.
- `.wh`/`.ch` support only zero-position traps; `.dt` warns.
- `.it` schedules an input-line trap; `itrap` runs it when the countdown reaches zero.
- `.em` appends an EOF macro call.
- Escapes:
  - `\$n` expands macro arguments.
  - `\*` expands strings.
  - `\t`, `\a`, `\\`, and `\.` handle copied/argument literal characters.
- Initializes default `eof` and `..` strings.

Dependencies and interactions:
- Uses string/register storage from `t8.c`, input stack callbacks from `input.c`, output callbacks from `roff.c`, and request registration from `roff.c`.

Research relevance:
- This is the macro-processing heart of `htmlroff`, enabling macro packages to be interpreted instead of merely scanned.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/htmlroff/t7.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/htmlroff/t8.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/htmlroff/t8.c

Implements strings and number registers for `htmlroff`.

Key points:
- Uses a shared `Reg` list type for both strings (`dslist`) and number registers (`nrlist`).
- `ds`, `as`, and `getds` define, append, and retrieve strings.
- `_nr`, `nr`, `_getnr`, and `getnr` store and evaluate registers.
- `.nr` creates/updates registers, including relative `+`/`-` updates and auto-increment values.
- `.af` sets number formats; `\g` returns a register’s format.
- `.rr` removes registers.
- `\n` expands registers, supports optional `+`/`-` auto-increment, one/two-character/bracket names, roman/alpha/zero-padded formats, and string-valued internal registers.
- `alpha` and `roman` implement non-decimal format conversions.
- `.pnr` dumps registers for debugging.

Dependencies and interactions:
- Used across almost every `htmlroff` module for roff state and macro strings.
- `getname` is used by multiple escape handlers.

Research relevance:
- This is the persistent state store for roff macros, registers, formatting state, and string expansion.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/htmlroff/t8.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/htmlroff/t9.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/htmlroff/t9.c

Placeholder for tabs, leaders, and fields.

Key points:
- Contains only a section comment and the token `XXX`.
- No valid initializer or implementation is present.
- `roff.c` explicitly has `t9init()` commented out.

Dependencies and interactions:
- Not compiled as functional implementation unless build rules treat it specially; active `htmlroff` does not initialize section 9 behavior.

Research relevance:
- Documents an unimplemented troff feature area.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/htmlroff/t9.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/htmlroff/util.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/htmlroff/util.c

Provides allocation, formatted string, warning, and ASCII-string-to-rune helpers for `htmlroff`.

Key points:
- `emalloc`, `erealloc`, `estrdup`, `erunestrdup`, `erunesmprint`, and `esmprint` fatal-exit on allocation failure.
- `warn` prints `htmlroff: <file>:<line>:` diagnostics using `%L`.
- `L` converts C string literals to cached `Rune*` strings and keys the cache by the literal pointer.
- The `L` cache allows source to use `L("name")` without manually constructing rune strings each time.

Dependencies and interactions:
- Used by all `htmlroff` modules.
- Depends on `linefmt` from `input.c` for warning locations.

Research relevance:
- This is common support code for the rune-oriented roff interpreter.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/htmlroff/util.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/iconv.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/iconv.c

Implements an image channel converter for Plan 9 image files.

Key points:
- Usage: `iconv [-u] [-c chanstr] [file]`.
- Reads a `Memimage` from stdin or one file.
- Parses target channel descriptor with `strtochan`; defaults to the source channel.
- Allocates a destination `Memimage` with the same rectangle and target channel.
- Uses `memimagedraw` to convert/copy pixels between channel formats.
- Writes either compressed image format via `writememimage` or uncompressed Plan 9 image format with `-u`.
- `writeuncompressed` writes the textual image header and each scanline from `unloadmemimage`.

Dependencies and interactions:
- Uses Plan 9 draw/memdraw libraries.

Research relevance:
- A small command-line wrapper around Plan 9 image channel conversion and image serialization.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/iconv.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/idiff.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/idiff.c

Implements an interactive two-file merge tool driven by `diff -n`.

Key points:
- Usage: `idiff [-bw] file1 file2`.
- Rejects directories and opens both inputs as `Biobuf`s.
- Runs `/bin/diff -n`, optionally with `-b` and/or `-w`, into a temporary file.
- `parse` decodes Plan 9 diff `-n` hunk headers into source ranges and command (`a`, `c`, `d`).
- For each hunk, prints the diff, prompts for action, and writes merged output to a second temp file.
- Commands:
  - `<` keeps left side.
  - `>` takes right side.
  - `=` writes the diff hunk itself.
  - `q<`, `q>`, `q=` choose a default for remaining hunks.
  - `!cmd` runs a shell command.
- `copylines`, `skiplines`, and `copy` manage input advancement and output.
- At the end, copies merged temp output to stdout.

Dependencies and interactions:
- Uses `/bin/diff`, `/bin/rc`, Plan 9 temp-file creation with `mktemp`, and `Biobuf`.

Research relevance:
- A classic Plan 9 interactive merge utility; notable for stream-based hunk processing and direct user decisions.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/idiff.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/image/affinewarp.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/image/affinewarp.c

Applies affine transformations to a Plan 9 image read from stdin.

Key points:
- Builds a stack of transformation matrices from command-line operations:
  - `-s x y` scale
  - `-r θ` rotate degrees
  - `-t x y` translate
  - `-S x y` shear
- Options:
  - `-R` enables replicated source sampling.
  - `-q` enables smoothing.
  - `-p` processes output bands in parallel.
- Optional four numeric args set destination rectangle; otherwise source rectangle is used.
- Composes transformations in stack order using `mkxform`.
- Uses `mkwarp` and `memaffinewarp` to render to a transparent destination.
- Parallel mode splits destination rectangle by rows using `initworkrects` and forks workers with shared memory.

Dependencies and interactions:
- Uses shared image utility functions from `image/util.c` and prototypes from `fns.h`.
- Uses Plan 9 `geometry.h` matrices and memdraw warp functions.

Research relevance:
- A command-line image geometry transform tool exposing Plan 9 memdraw affine-warp primitives.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/image/affinewarp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/image/correlate.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/image/correlate.c

Applies an image correlation or convolution kernel to an image read from stdin.

Key points:
- Usage: `correlate [-cRp] kernel [denom]`.
- Reads kernel files from the given path or `/lib/image/filter/<basename>`.
- `readimagekernel` parses whitespace-separated doubles into a rectangular kernel, verifies consistent row width, optionally reverses kernel coefficients for convolution mode, and calls `allocmemimagekernel`.
- Options:
  - `-c` reverses the kernel for convolution.
  - `-R` enables replicated source sampling.
  - `-p` processes row bands in parallel.
- Allocates transparent destination image and calls `memimagecorrelate`.
- Parallel mode uses `NPROC`, row rectangles from `initworkrects`, and `rfork(RFPROC|RFMEM)` workers.

Dependencies and interactions:
- Uses utility functions from `image/util.c`.
- Uses Plan 9 `memdraw` kernel/correlation APIs.

Research relevance:
- A command-line wrapper for Plan 9 image filtering kernels, with optional parallel execution.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/image/correlate.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/image/fns.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/image/fns.h

Declares shared helper functions for the Plan 9 image commands in this group.

Key points:
- Declares row-work splitting, checked memory allocation, checked `Memimage` allocation/read/write, checked display `Image` allocation, and `Memimage` to `Image` conversion.
- Used by `affinewarp.c`, `correlate.c`, `histogram.c`, and `util.c`.

Dependencies and interactions:
- Types come from Plan 9 draw and memdraw headers.

Research relevance:
- Small shared interface for robust image command helpers.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/image/fns.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/image/histogram.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/image/histogram.c

Implements an interactive image viewer with separate per-channel histogram windows.

Key points:
- Reads an image from stdin or a file into `Memimage`, converts it to a display `Image`, and opens a draw window.
- Maintains affine transform matrix/warp for pan and zoom of the displayed source image.
- Samples pixels manually from `Memimage` across depths 1/2/4/8/16/24/32 and channel descriptors, converting to RGBA-like values.
- `measureimage` computes alpha/blue/green/red histograms, averages, and maximum bins over the full image or selected region.
- Draws histogram images with colored bars, average marker line, and grayscale gradients.
- Starts a second window labeled `histograms` to display four stacked histogram panels.
- Mouse behavior:
  - left drag pans source image.
  - middle drag or scroll zooms.
  - right menu toggles smoothing or selects/clears a region.
  - right-drag in histogram window draws freehand marks.
- Keyboard `q` or Delete exits.
- Handles resize and keeps histogram window sized/moved via `/dev/wctl`.

Dependencies and interactions:
- Uses Plan 9 `thread`, `draw`, `memdraw`, `mouse`, `keyboard`, and `geometry`.
- Uses `image/util.c` helpers for allocation and image conversion.

Research relevance:
- A richer interactive image-analysis tool demonstrating Plan 9 graphics, windows, channels, event loops, and raw pixel interpretation.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/image/histogram.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/image/util.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/image/util.c

Provides shared utility functions for image commands.

Key points:
- `initworkrects` splits a rectangle into horizontal bands for parallel processing.
- `emalloc` and `erealloc` fatal-exit on allocation failure and set malloc/realloc tags.
- `eallocmemimage` allocates and clears a `Memimage`.
- `ereadmemimage` and `ewritememimage` wrap image I/O with fatal errors.
- `eallocimage` wraps display `Image` allocation.
- `memimage2image` creates a display `Image` from a `Memimage` by loading one scanline at a time.

Dependencies and interactions:
- Used by `affinewarp.c`, `correlate.c`, and `histogram.c`.

Research relevance:
- Shared reliability and display-conversion support for Plan 9 image-processing commands.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/image/util.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/init.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/init.c

Implements Plan 9 user-space `init`.

Key points:
- Closes inherited boot fds, parses service mode (`-c` cpu, `-t` terminal) and manual mode (`-m`), and optional rc command.
- Sets process priority through `#p/<pid>/ctl`.
- Reads CPU type, user, and system name from kernel devices/environment and sets `objtype`, `service`, and timezone environment files.
- Calls `newns` to build the namespace for the current user.
- On CPU service and non-manual startup, runs `/rc/bin/cpurc` first.
- Main loop repeatedly starts `/bin/rc`, then falls into manual mode after rc exits.
- `fexec` forks a child exec function, forwards interrupts to the child process group via `notepg`, handles wait races/notes, and sleeps forever if exec failed.
- `rcexec` chooses rc command according to command/manual/cpu/terminal mode.
- `readfile`, `readenv`, `setenv`, and `cpenv` support environment setup.
- `procopen` opens process control files and logs warnings.

Dependencies and interactions:
- Uses Plan 9 auth namespace setup, process note handling, `/env`, `#c`, `#e`, and `#p` devices.

Research relevance:
- Central boot/userland process supervisor for Plan 9/9front sessions.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/init.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/io.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/io.c

Implements low-level port/device register read/write utility.

Key points:
- Usage supports size selectors:
  - default byte
  - `-W` 2 bytes
  - `-L` 4 bytes
  - `-M` 8 bytes
- Selects default device files by size: `#P/iob`, `#P/iow`, `#P/iol`, or `#P/msr`.
- `-E` redirects all size device files to `#P/ec`.
- `-f file` overrides device file.
- `-r` reads; `-w` writes.
- Takes address, optional write value, and optional mask.
- Uses `pread`/`pwrite` at the numeric address offset, little-endian encodes/decodes up to 64-bit values, applies masks, and prints final value.

Dependencies and interactions:
- Uses Plan 9 processor-port device files.

Research relevance:
- A privileged diagnostic/control tool for direct I/O, EC, or MSR access.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/io.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/iostats.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/iostats.c

Runs a command through a 9P proxy and reports filesystem I/O statistics.

Key points:
- Usage: `iostats [-dC] cmds [args ...]`.
- Creates a pipe-mounted namespace for the child command and runs `exportfs -r /` behind it.
- Duplicates original stdio fds so the child can keep stdin/stdout/stderr through the mounted namespace.
- Tracks 9P request and response messages:
  - decodes `Fcall`s with `convM2S`
  - matches responses to requests by tag
  - times each RPC with `nsec`
  - tracks protocol bytes in/out
- Maintains fid table mapping fids to qids and paths across attach, walk, open/create, clunk/remove.
- Tracks per-file opens, read counts/bytes, write counts/bytes.
- Handles child completion by posting a private `done` note to the filesystem proxy process.
- Prints total read/write/protocol throughput, RPC counts/timing, protocol byte counts, and per-file open/read/write summary.
- `-d` runs exportfs with debug; `-C` adds `MCACHE` mount flag.

Dependencies and interactions:
- Uses Plan 9 `mount`, `exportfs`, 9P `Fcall`, process namespace isolation, pipes, rfork shared memory, and notes.

Research relevance:
- Useful instrumentation code for observing 9P filesystem workloads at the protocol boundary.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/iostats.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/6in4.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ip/6in4.c

Implements a 6in4/6to4 IPv6-in-IPv4 tunnel client.

Key points:
- Supports automatic 6to4 default local address generation from local IPv4 address and anycast relay `192.88.99.1`.
- Options:
  - `-a` accept any sender.
  - `-d` debug.
  - `-g` add default global IPv6 route.
  - `-m mtu` set MTU.
  - `-x mtpt` set both inside/outside network roots.
  - `-o mtpt` set outside network root.
  - `-i local4` set local IPv4 address.
- Parses local IPv6/mask, remote IPv4, and remote IPv6, with defaults.
- `setup` opens an IPv4 protocol-41/ICMPv6 ipmux tunnel and creates a packet `ipifc` for IPv6.
- Adds local IPv6 address and optional `2000::/3` route.
- `runtunnel` forks background copy processes.
- `ip2tunnel` reads IPv6 packets from packet interface, filters bad source/destination addresses, builds IPv4 headers, sends 6to4 destinations directly or via configured remote IPv4.
- `tunnel2ip` decapsulates IPv4 protocol 41/ICMPv6 packets, validates lengths and bad IPv6 addresses, and writes IPv6 payloads to the packet interface.
- `badipv4` and `badipv6` filter private, loopback, link-local, multicast, unspecified, and invalid 6to4 sources.

Dependencies and interactions:
- Uses Plan 9 `/net` ipmux, `ipifc`, `iproute`, `ip.h`, and process forking.

Research relevance:
- Network tunneling code with explicit packet validation and Plan 9 packet-interface setup.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/6in4.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/arp.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ip/arp.h

Defines ARP packet, cache entry, stats structures, and constants.

Key points:
- `Arppkt` describes Ethernet ARP/RARP wire format, including Ethernet header, hardware/protocol types, lengths, op, sender/target hardware addresses, and sender/target IPv4 addresses.
- `ARPSIZE` is 42 bytes.
- `Arpentry` maps Ethernet address to IPv4 address for user-level ARP interactions.
- `Arpstats` tracks hits, misses, and failures.
- Defines Ethernet type constants for ARP/RARP and operation constants for ARP/RARP request/reply.

Dependencies and interactions:
- Comment notes use by kernel, `arpd`, `snoopy`, and `tboot`.

Research relevance:
- Shared protocol definition header for ARP-related Plan 9 networking components.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/arp.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/ayiya.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ip/ayiya.c

Implements an AYIYA IPv6 tunnel client over UDP with optional shared-secret authentication.

Key points:
- Defines AYIYA header fields, identity/hash/auth/opcode constants, maximum identity/signature/header sizes, and protocol state.
- Supports options:
  - `-d` debug
  - `-g` install global IPv6 route
  - `-m mtu`
  - `-x mtpt` inside network root
  - `-k secret` shared-key authentication seed
- Requires local IPv6/mask, remote UDP endpoint, and remote IPv6.
- `ayiyapack` prepends AYIYA header, identity, timestamp, and signature area before IPv6 payload.
- `ayiyaunpack` decodes AYIYA headers and points identity/signature into the packet.
- `ayiyahash` supports MD5 and SHA1; the configured default uses SHA1 length.
- `ayiyasign` hashes packets with the configured signature placeholder; `ayiyaverify` verifies incoming signature/auth settings.
- `setup` creates a local IPv6 packet interface and optionally adds `2000::/3` route.
- `ip2tunnel` reads IPv6 packets, sends heartbeat packets after read alarms, filters invalid addresses, and forwards with `OpForward`.
- `tunnel2ip` verifies incoming AYIYA packets, handles MOTD/query/echo opcodes, validates forwarded IPv6 payloads, restricts inbound destination to the local subnet, writes to the packet interface, and replies to echo/query as needed.
- `badipv4`/`badipv6` mirror invalid-address filtering from `6in4.c`.

Dependencies and interactions:
- Uses Plan 9 UDP dialing, `ipifc`, `iproute`, `libsec` hashing, alarm/notify, and IP helpers.

Research relevance:
- More complex than `6in4.c`: it demonstrates authenticated tunnel framing, keepalives, control opcodes, and subnet ingress filtering.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/ayiya.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/cifsd/dat.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ip/cifsd/dat.h

Defines core data structures, globals, and constants for `cifsd`.

Key points:
- Defines `Rop` string/name packing operations for ASCII vs Unicode SMB modes.
- Defines `Req` for a single SMB request: command ids, tid/pid/uid/mid, flags, signature, response buffer pointers, packing ops, request name, response callback, and name comparison function.
- Defines `Trans` for SMB transaction requests with parameter/data/setup input and output buffers.
- Defines `File`, `Find`, `Share`, and `Tree` server state structures.
- Declares global configuration/state: debug, space translation, auth requirement, domain, program/OS names, remote system/user, buffer size, start time, timezone offset.
- Defines NT status codes, resource/share types, capability flags, DOS attributes, file access masks, share access modes, create dispositions/actions/options, and buffer size.

Dependencies and interactions:
- Shared by all `cifsd` implementation files.
- `Idmap` is forward-declared and implemented in `idmap.c`.

Research relevance:
- This is the central protocol/server-state contract for the CIFS/SMB server.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/cifsd/dat.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/cifsd/dir.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ip/cifsd/dir.c

Implements case-aware directory lookup, stat, read, and small directory-cache support for `cifsd`.

Key points:
- `xdirdup` deep-copies Plan 9 `Dir` arrays and embedded string fields into one allocation.
- `xdirread` returns a deep copy of directory entries from `xdirread0`.
- `xdirstat` first tries direct `dirstat`; if it fails, it splits path and scans the parent directory with the configured name comparator to find case-insensitive/canonical names.
- Maintains a small linked cache `xdirlist` of up to 8 directory listings keyed by path/qid.
- Cache entries are validated by comparing current `dirstat` qid against cached qid.
- If a cached path has canonical capitalization, callers may have their path replaced with the cached/canonical path.
- `xdirflush` invalidates cached entries for a directory affected by a path mutation.

Dependencies and interactions:
- Uses `splitpath`, `conspath`, and name comparison callbacks (`strcmp` or `cistrcmp`).
- Called by file creation/open and find code.

Research relevance:
- Provides CIFS case-insensitive path semantics over Plan 9 filesystem APIs.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/cifsd/dir.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/cifsd/error.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ip/cifsd/error.c

Maps Plan 9 and NT-style errors into SMB/DOS error encodings.

Key points:
- Defines SMB error classes and DOS/server/hardware command error codes.
- `doserror` maps NT status values to packed DOS/class error values for clients that did not negotiate NT status.
- `smbmkerror` reads the current Plan 9 error string and matches substrings to NT status values.
- Includes mappings for permission denied, directory not empty, no such file/name/path, bad syntax, collision, directory type errors, and several kenfs-specific wstat/create errors.
- Falls back to `STATUS_INVALID_SMB` for unknown errors.
- Debug mode logs error-string-to-status mapping.

Dependencies and interactions:
- Used by SMB request response paths and file/path operation code.

Research relevance:
- Critical compatibility layer between Plan 9 error strings and CIFS/SMB client-visible status codes.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/cifsd/error.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/cifsd/file.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ip/cifsd/file.c

Implements CIFS file open/create, share-mode compatibility, delete-on-close, stat, locking, and close logic.

Key points:
- Maintains an opportunistic/share lock table `locktab` keyed by name hash.
- `getopl` enforces SMB share compatibility:
  - `FILE_SHARE_COMPAT` special rules.
  - read/write/delete desired access vs existing share permissions.
  - canonicalizes path to existing locked path spelling when matched.
- `putopl` removes lock records when last reference closes and performs remove-on-close if requested.
- `createfile` implements SMB create/open dispositions:
  - supersede, open, create, open-if, overwrite, overwrite-if.
  - directory-only and non-directory-only checks.
  - readonly attribute effects on creation mode.
  - delete-on-close validation.
  - truncation/size setting for overwrite/new files.
  - fallback create using canonical parent/name lookup.
- Returns create action and optional `Dir` stat data.
- `statfile` stats by fd or path.
- `lockfile` provides a single logical lock owner per `Opl`.
- `deletefile` toggles delete-on-close; `deletedfile` queries it.
- `putfile` closes fd, clears lock owner, releases `Opl`, and frees the file.

Dependencies and interactions:
- Uses `xdirstat`, `splitpath`, `conspath`, `smbmkerror`, DOS/NT constants, and path hash/name comparators.
- Returned `File` objects are stored in tree fid tables.

Research relevance:
- This is core SMB filesystem semantic emulation over Plan 9 files: share modes, create dispositions, and deletion behavior.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/cifsd/file.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/cifsd/find.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ip/cifsd/find.c

Implements SMB directory search state and wildcard matching.

Key points:
- `iswild` detects SMB wildcard characters `*?<>\"`.
- `matchpattern` implements SMB wildcard semantics:
  - `?` matches one rune.
  - `*` and `<` match variable spans with DOS dot handling.
  - `>` has DOS special behavior around dot/end.
  - `"` matches dot or end.
  - case-insensitive matching uses rune uppercase comparison.
- `matchattr` filters entries by DOS file attributes and search mask.
- `openfind` splits search path into base/pattern, reads a directory for wildcard searches, or stats an exact path for non-wildcard searches.
- Optional `withdot` adds synthetic/current `.` and parent `..` stats.
- `readfind` scans from an index to the next matching `Dir`.
- `putfind` releases directory, dot/dotdot, pattern, and base state.

Dependencies and interactions:
- Uses `xdirread`, `xdirstat`, `splitpath`, `dosfileattr`, and name comparison functions.
- `Find` objects are stored in tree search-id tables.

Research relevance:
- Implements Windows/SMB-style directory enumeration semantics over Plan 9 directories.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/cifsd/find.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/cifsd/fns.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ip/cifsd/fns.h

Declares function prototypes for `cifsd` subsystems.

Key points:
- Declares binary pack/unpack functions.
- Declares error conversion helpers.
- Declares utility functions for logging, remote-name lookup, path building/splitting, hex dumps, time conversions, size/allocation conversions, attribute conversions, hashing, string translation, and SMB string/name packers.
- Declares SMB command dispatcher `smbcmd`.
- Declares share, RAP transaction, tree/fid/search-id, file, find, directory, and idmap APIs.

Dependencies and interactions:
- Shared by all `cifsd` source files.
- Complements structures and constants from `dat.h`.

Research relevance:
- This header exposes the modular boundaries of the CIFS server.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/cifsd/fns.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/cifsd/idmap.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ip/cifsd/idmap.c

Implements user/group name-to-id and id-to-name maps for CIFS shares.

Key points:
- `Idmap` is a hash table of `Ident` records linked both by id hash and name hash.
- `name2id` and `id2name` perform lookup by name/id.
- `idmap` inserts one mapping into both hash chains.
- `readidmap` reads either Unix-style `/etc/passwd`/`/etc/group` or Plan 9 `/adm/users` style files.
- Unix style extracts name and numeric id from colon-separated records.
- Plan 9 style offsets numeric ids by 9,000,000 and extracts names from `/adm/users` records.
- `unixidmap` tries share-local `etc/passwd` and `etc/group`, then share-local `adm/users`, otherwise installs empty maps.
- `unixname`, `unixuid`, and `unixgid` expose lookup helpers.

Dependencies and interactions:
- `Share` objects hold user and group maps.
- Uses `namehash` from utility code.

Research relevance:
- Provides ownership name/id translation for CIFS Unix extensions or file metadata presentation.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/cifsd/idmap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/cifsd/main.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ip/cifsd/main.c

Implements the main SMB1 server loop and request/response header handling for `cifsd`.

Key points:
- Defines NetBIOS session header length, SMB magic constants, SMB flags, flags2, capability-related flags, and case-sensitivity behavior.
- `respond` converts NT status to DOS error if needed, builds an SMB response header, zeroes signatures except for session setup, writes the NetBIOS length prefix, and sends to stdout.
- `receive` decodes SMB headers, rejects non-SMB1 magic including SMB2/3, chooses ASCII vs Unicode `Rop` packers, sets request metadata and name comparator, and dispatches via `smbcmd`.
- `serve` reads a byte stream from stdin, reassembles NetBIOS-framed SMB messages, and calls `receive` for each complete message.
- Command-line options:
  - `-t` disables authentication requirement.
  - `-d` increases debug.
  - `-f log` logs to a file.
  - `-w domain` sets workgroup/domain.
  - `-o trspaces` or `-o casesensitive` toggles options.
- Closes stderr and redirects it to the log or `/dev/null`.
- Initializes remote system, buffer size, start time, pid-based PRNG seed, timezone offset, logs startup/exit, serves, then logs off.

Dependencies and interactions:
- Uses `pack`, `unpack`, SMB string/name packers, `smbcmd`, `logoff`, and utility logging/remote functions.
- This file only handles protocol framing and dispatch; command implementations live elsewhere.

Research relevance:
- Main entry point and wire framing layer for the SMB1/CIFS server.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/cifsd/main.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/cifsd/pack.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ip/cifsd/pack.c

Implements a compact binary format language for SMB message packing and unpacking.

Key points:
- Public wrappers `pack`/`unpack` call `vpack`/`vunpack`.
- Supports format operators:
  - `_` skip/zero byte
  - `b`, `w`, `l`, `v` for little-endian 8/16/32/64-bit values
  - `%n` alignment
  - `f` custom pack/unpack function
  - `#` count field and `@` offset field tied to sub-block index
  - `{}` sub-blocks with counted/offset-delimited regions
  - `[]` copy/expose raw byte ranges
  - `.` capture current pointer
- `vunpack` tracks nested sub-blocks, applies counts/offsets, bounds checks, and returns bytes consumed.
- `vpack` mirrors the same mechanism, backpatching count and offset fields when sub-blocks close.
- Fixed-size sub-block item width can be specified with `{*n}`/`[*n]`.
- Returns 0 on malformed/truncated/bounds-failing input.

Dependencies and interactions:
- Used heavily by SMB request parsing, response construction, transaction/RAP responses, and string/name packers.

Research relevance:
- This is the low-level serialization engine for CIFS protocol handling.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/cifsd/pack.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/cifsd/rap.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ip/cifsd/rap.c

Implements a subset of SMB RAP transaction handling.

Key points:
- `padname` writes fixed-size NUL-padded share/server names.
- `packshareinfo` handles share info levels:
  - level 0: share name only
  - level 1: name, type, remark
  - level 2: name, type, permissions/max uses/current uses, remark, and root
- `transrap` unpacks RAP command, parameter descriptor, and data descriptor strings.
- Supports RAP calls:
  - `NetShareEnum` (`0x0000`) returning the `local` share.
  - `NetShareGetInfo` (`0x0001`) for a named share.
  - `NetServerGetInfo` (`0x000d`) levels 0 and 1.
  - `NetWrkstaGetInfo` (`0x003f`) level 10.
- Packs RAP status/count/length metadata into transaction parameter output and data into transaction data output.
- Logs unknown RAP commands or levels and returns DOS/RAP status codes where appropriate.

Dependencies and interactions:
- Uses `mapshare`, `pack`/`unpack`, SMB 8-bit string packers, `sysname`, `domain`, and `osname`.
- Called by transaction command handling outside this file.

Research relevance:
- Provides legacy LAN Manager/RAP discovery compatibility for CIFS clients.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ip/cifsd/rap.c -->