# Group Research: group_78_9front_sources_os_plan9_9front_sys_src_cmd_dtracy_act_c_sources_os_pl_3196e7fd19f7

Scope confirmed against `Docs/research_subset_a.md`: these files are inside `sources/os/plan9/9front`, which is included in subset A. Every listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/dtracy/act.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/dtracy/act.c

This file converts parsed dtracy clauses into kernel-facing `DTClause`/`DTActGr` structures and parses trace records returned from the kernel. It owns global clause storage (`clause`, `clauses`, `nclauses`) and the enabled-probe lookup table keyed by epid.

Key responsibilities:
- Builds clauses from parser callbacks: `clausebegin`, `addprobe`, `addstat`, `addarg`, `addpred`, `clauseend`.
- Normalizes probe names with `insertstars`, filling empty probe tuple components with `*`.
- Prepares print/printf actions, including kernel trace actions for runtime values via `tracegen`.
- Allocates aggregation IDs, records aggregate metadata, and emits `ACTAGGKEY`/`ACTAGGVAL`.
- Packs generated clauses with `dtclpack`.
- Parses binary trace buffers, fault records, and record payloads through `unpack`, `parsebuf`, `parsefault`, `parseclause`, and `receval`.

Important implementation notes:
- `receval` re-evaluates record-side expressions against captured record fields, supporting variables like `time` and `probe`.
- String record extraction allocates a copy and has a TODO leak comment.
- `execprintf` manually constructs a vararg block, matching the rewritten format prepared by `prepprintf`.
- `dump` provides a detailed debug view of generated kernel bytecode and record formatting.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/dtracy/act.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/dtracy/agg.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/dtracy/agg.c

This file implements user-space aggregation result collection for dtracy. Kernel aggregation records are parsed into per-aggregation AVL trees keyed by the aggregation key bytes.

Key responsibilities:
- Defines `ANode`, an AVL node containing key bytes plus aggregate state (`val`, `cnt`, `sq`).
- Initializes one AVL tree per aggregation in `agginit`.
- Parses aggregation buffers in `aggparsebuf`, validates IDs, key sizes, and record bounds, then creates or updates tree nodes.
- Handles aggregation types: count, sum, min/max storage, average, and standard deviation.
- Prints aggregation keys and values in `aggdump`.

Important implementation notes:
- `aggparsebuf` validates that the packed record ID type and key size match the corresponding `Agg`.
- Standard deviation uses Plan 9 multiprecision integers (`mp`) in `variance` to avoid overflow when combining squared sums.
- `aggnote` marks interruption so the aggregation reader can stop and dump accumulated results.
- `aggkeyprint` currently assumes an 8-byte integer key and formats `*(u64int*)a->key`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/dtracy/agg.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/dtracy/cgen.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/dtracy/cgen.c

This file generates dtracy VM bytecode (`DTExpr`) from typed expression AST nodes and inserts trace actions for expressions that must be evaluated in the kernel.

Key responsibilities:
- Maintains a small register allocator over 16 registers using `regsused`.
- Encodes constants with `constenc`, emitting `DTE_LDI` and `DTE_XORI` pieces.
- Generates arithmetic, bitwise, comparison, logical, ternary, cast, and variable-load bytecode in `egen`.
- Emits short branch labels and patches branch displacements after code generation.
- Builds predicate and value expressions with `codegen`.
- Converts record-marked nodes into trace actions with `tracegen`.

Important implementation notes:
- Logical operators are handled with short-circuit branch generation in `condgen` and value-producing boolean code in `condvgen`.
- `tracegen` emits `ACTTRACE` for integer runtime values and `ACTTRACESTR` for string runtime values, assigning record offsets as it walks the AST.
- Branch fixups assume an 8-bit relative offset and assert the target fits.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/dtracy/cgen.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/dtracy/dat.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/dtracy/dat.h

This header defines the main internal data model for dtracy: types, symbols, AST nodes, statements, clauses, enabled probe entries, and aggregation metadata.

Key structures:
- `Type`: integer, pointer, and string type descriptors with size/sign/reference fields.
- `Symbol`: global symbols, currently mostly variables (`SYMVAR`) with kernel variable index and type.
- `Node`: expression AST with node kind, operator, child pointers, symbol/string/number payload, source line, type, and analysis fields used by cast elision and record insertion.
- `Stat`: clause statements for expressions, print/printf, and aggregations.
- `Clause`: parsed probe clause with probes, predicate bytecode, and statements.
- `Enab`: runtime epid-to-clause mapping from kernel enablement data.
- `Agg`: user-space wrapper around `DTAgg` plus display name.

Important implementation notes:
- `SYMHASH` is 256 for global symbol buckets.
- Custom Plan 9 format pragmas are declared for node/type/operator diagnostics.
- Globals such as `dflag`, `noagg`, `aggid`, and `aggs` are shared across compilation, execution, and aggregation handling.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/dtracy/dat.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/dtracy/dtracy.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/dtracy/dtracy.c

This is the main dtracy command driver. It initializes parsing, installs formatters, connects to the kernel dtracy device, uploads generated programs, reads epid mappings, and streams trace and aggregation output.

Key responsibilities:
- Provides allocation wrappers `emalloc`, `erealloc`, `dtmalloc`, and `dtfree`.
- Defines built-in variables (`arg0`-`arg9`, `pid`, `machno`, `time`, `probe`) in `globvars`.
- Opens `#Δ/clone`, discovers the dtracy instance number, and opens the trace buffer in `setup`.
- Packs and writes compiled clauses to the kernel `prog` file in `progcopy`.
- Reads epid-to-clause mappings from the kernel `epid` file in `epidread`.
- Streams buffers through `parsebuf` in `bufread`.
- Forks an aggregation reader in `aggproc` when aggregations are present.

Important implementation notes:
- `-d` runs a compile/debug dump instead of attaching to the kernel device.
- Aggregation reading uses shared memory `rfork(RFPROC|RFMEM)` so interruption state can be shared.
- Runtime output uses a `Biobuf` around stdout for normal trace records.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/dtracy/dtracy.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/dtracy/fns.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/dtracy/fns.h

This header declares dtracy’s internal functions across parser, lexer, type checker, code generator, action builder, runtime parser, and aggregation modules.

Important exported groups:
- Parser/lexer: `yyparse`, `yylex`, `yyerror`, `lexinit`, `lexstring`, `node`, `getsym`.
- Type and formatting: `exprcheck`, `type`, `addtype`, `evalop`, `nodetfmt`, `typetfmt`, `typefmt`, `nodefmt`.
- Clause/action generation: `clausebegin`, `addstat`, `addarg`, `addprobe`, `addpred`, `clauseend`, `packclauses`, `actgradd`, `tracegen`, `codegen`.
- Runtime parsing: `addepid`, `parsebuf`.
- Aggregation: `aggparsebuf`, `aggnote`, `aggdump`, `agginit`.

Important implementation notes:
- It aliases no implementations; it is purely a shared declaration surface.
- `#pragma varargck argpos error 1` is declared in `dat.h`, while `fns.h` exposes the variadic `error`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/dtracy/fns.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/dtracy/lex.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/dtracy/lex.c

This file implements lexical analysis, symbol-table management, AST node construction, type formatting, and primitive type interning for dtracy scripts.

Key responsibilities:
- Tokenizes script strings from memory, including comments, identifiers, probe-name fragments with `:`, numeric literals, string literals, keywords, and multi-character operators.
- Tracks line numbers and error counts.
- Builds AST nodes through `node`.
- Maintains a global symbol table using an FNV-style hash.
- Formats node kinds and types for diagnostics/debug output.
- Provides canonical integer and string types through `type`.

Important implementation notes:
- Keywords and operators are stored in sorted tables with first-character indexes.
- String escapes support common C-style escapes but not octal/hex escapes.
- Identifiers accept bytes `>= 0x80`, matching Plan 9’s UTF-oriented conventions.
- Pointer type interning in `mkptr` searches `typereg`, but the created pointer type is not linked back into `typereg`; pointer support appears incomplete or unused.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/dtracy/lex.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/dtracy/parse.y -->
# File Research: sources/os/plan9/9front/sys/src/cmd/dtracy/parse.y

This yacc grammar defines the dtracy scripting language. It parses probe clauses, optional predicates, actions, expression statements, printing, formatted printing, and aggregations.

Key grammar features:
- A program is a sequence of clauses.
- Clauses contain one or more probes, an optional `if expr` predicate, and either a default action or `{ ... }`.
- Default action is `print(probe)`.
- Statements include expression evaluation, `print`, `printf`, and aggregation assignments like `@name[key] = agg(value)`.
- Expressions support numeric/string/symbol literals, arithmetic, bitwise operations, comparisons, logical operators, unary operators, ternary, parentheses, and casts.
- Type names include `u8/s8` through `u64/s64` and `string`.

Important implementation notes:
- Predicates are immediately type-checked and bytecode-generated in the grammar action.
- Non-predicate action expressions are type-checked through `exprcheck(..., 0)`, allowing record insertion for runtime value capture.
- Greater-than comparisons are normalized by swapping operands and using less-than operators.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/dtracy/parse.y -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/dtracy/type.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/dtracy/type.c

This file performs dtracy expression type checking and optimization before bytecode generation or record capture. It adds casts to model C-like integer semantics, folds constants, decides which subexpressions must be recorded from the kernel, and removes unnecessary casts.

Key responsibilities:
- `typecheck` annotates expressions with `Type`, validates operations, and inserts integer casts.
- `evalop` implements constant/runtime binary operator semantics, including signed/unsigned division and shifts.
- `cfold` folds constant expressions and integer casts.
- `calcrecsize` estimates the minimal record bytes needed to reproduce a value in user space.
- `insrecord` wraps runtime-needed subexpressions in `ORECORD`.
- `elidecasts` tracks known data bits and upper-bit extension to remove redundant casts.
- `exprcheck` runs the whole pipeline and emits debug stages under `-d`.

Important implementation notes:
- The comment explicitly says it uses kencc, not ANSI C, unsigned semantics.
- `icast(int sign, int size, Node *n)` calls `type(TYPINT, sign, size)`, but every other call uses `type(TYPINT, size, sign)`. This looks like a real argument-order bug because `type` expects size first, sign second.
- `DTV_TIME` and `DTV_PROBE` are treated as record-free variables; other variables require record capture.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/dtracy/type.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/du.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/du.c

This is Plan 9 `du`, a disk-usage walker with options for all files, byte counts, qids, access/modify times, autoscaling, quiet warnings, and a read-through mode.

Key responsibilities:
- Parses flags `-aefhnqstu`, block size `-b`, and SI prefix output scale `-p`.
- Recursively walks directories with `dirread`.
- Rounds file lengths to a configured block size with `blkmultiple`.
- Prints totals or per-file values using integer, floating, or autoscaled output.
- Avoids directory cycles with a small qid/type/dev cache in `seen`.
- Optional `-r` reads every block of every file into `readbuf`.

Important implementation notes:
- `dirval` switches reported value between size, qid path, mtime, or atime.
- `dufile` builds child paths with Plan 9 `String`.
- `readflg` suppresses printing and turns traversal into an I/O read test.
- Warnings are suppressed by `-f`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/du.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/echo.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/echo.c

This is a compact Plan 9 `echo` implementation.

Key responsibilities:
- Supports a single `-n` option to suppress the trailing newline.
- Computes the exact output buffer length, allocates it, concatenates arguments separated by spaces, and optionally appends `\n`.
- Writes the buffer to stdout with one `write`.

Important implementation notes:
- The parser only recognizes `-n` as the first argument; all other arguments are printed literally.
- On allocation failure it exits with `"no memory"`.
- On write failure it reports `echo: write error: %r` to stderr and exits with `"write error"`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/echo.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ecp.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ecp.c

This file implements `ecp`, a robust sector-oriented copy tool designed for failing media. It copies in large blocks when possible, falls back to single-sector transfers on errors, can verify after copy, and can copy in reverse.

Key responsibilities:
- Tracks source and destination state in `File`, including start sector, seekability, hard errors, consecutive errors, and fast/slow transfer mode.
- Reads/writes blocks with `bio`, handling short reads, optional reblocking, and zero-filling.
- Retries failed large transfers sector by sector in `bigxfer`.
- Reports bad sector ranges compactly with `io_expl` and `ckendrange`.
- Verifies copied data in a separate pass through `verify`/`vrfysects`.
- Supports confirmation, progress, reverse copy, start offsets, sector size, block size, max consecutive errors, and byte swizzling.

Important implementation notes:
- `copyfile` creates the destination if missing, then opens source and destination with seekability checks.
- Verification is intentionally separate from copying to avoid controller-cache false confidence.
- `swizzlebits` rotates and inverts bytes for the `-Z` mode.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ecp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ed.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ed.c

This is the Plan 9 line editor `ed`. It implements address parsing, command execution, file I/O, temporary-file-backed line storage, regular-expression matching, substitution, global commands, marks, shell escapes, browsing, and hangup recovery.

Key responsibilities:
- Maintains the editable buffer as an array of temporary-file line addresses (`zero`, `dot`, `dol`).
- Runs the command loop in `commands`, handling classic `ed` commands including append/change/delete/edit/read/write/substitute/global/move/copy/join/print/quit.
- Parses addresses with `.`, `$`, marks, numeric offsets, and regex searches.
- Uses Plan 9 regex (`regcomp`, `rregexec`) for searches and substitutions.
- Stores line text in a block-cached temp file using `getblock`, `getline`, and `putline`.
- Handles interrupts and hangups with `notifyf`; on hangup it writes `ed.hup`.
- Implements list/numbered output formatting in `putchr`, `putshst`, and `putd`.

Important implementation notes:
- `global` has a special optimized path for `g/.../d`.
- `substitute` supports numbered match selection, global substitution, `&`, and `\1`-style captured substitutions.
- `quit` protects against unsaved changes when verbose mode is active.
- The code uses Rune buffers throughout for Plan 9 Unicode text handling.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ed.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/eqn/diacrit.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/eqn/diacrit.c

This file renders eqn diacritics over or under an existing box. Supported decorations include vector, dyad, hat, tilde, dot, double dot, bars, underbar, and under-tilde.

Key responsibilities:
- Allocates temporary string/register IDs with `salloc`.
- Computes vertical and horizontal shifts from box height, baseline, current point size, and tuning parameters.
- Emits troff strings for named diacritics from `deftbl` or constructs rule-based bars/underbars.
- Recomputes widths with `nrwid`.
- Appends the diacritic to the existing box string and updates box height where appropriate.

Important implementation notes:
- Italic boxes affect horizontal shift behavior.
- Underbar/utilde reset horizontal/vertical shifts differently from over-diacritics.
- Uses tuning globals such as `Dvshift`, `Dhshift`, `Barv`, `Barh`, `Ubarv`, and `Dheight`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/eqn/diacrit.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/eqn/e.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/eqn/e.h

This header is the shared interface for the eqn implementation. It defines lexical character classes, font constants, device constants, symbol-table structures, input-source structures, argument frames, font stack entries, global state declarations, and function prototypes.

Key contents:
- Character classes used for spacing: `OTHER`, `OLET`, `ILET`, `DIG`, `LPAR`, `RPAR`, etc.
- Font constants: roman, italic, bold, bold italic.
- Device types: CAT, 202, APS, PostScript.
- `tbl` for keyword/reserved/definition/tuning hash tables.
- `Infile`, `Src`, `Arg`, and `Font` for input handling, macro arguments, and font stack.
- Global layout arrays for heights, baselines, fonts, classes, and string-register allocation.
- Prototypes for lexer/input helpers and every equation layout operator.

Important implementation notes:
- Error-reporting macros build `errbuf` and call `error` or `yyerror`.
- Many functions are old-style C declarations, matching the vintage code style.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/eqn/e.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/eqn/eqn.y -->
# File Research: sources/os/plan9/9front/sys/src/cmd/eqn/eqn.y

This yacc grammar defines the eqn language and maps parsed constructs to layout functions. It builds equation boxes and emits troff string-register definitions through semantic actions.

Key grammar features:
- A top-level equation is a sequence of boxes.
- Box constructs include quoted/contiguous text, spaces, sums/products/unions/intersections, fractions, marks, size/font/fat boxes, square roots, subscripts, superscripts, integrals, from/to limits, left/right delimiters, diacritics, moves, piles, and matrices.
- Matrix and pile grammars store intermediate boxes in the global `lp` stack.
- `LINEUP` and `MARK` support alignment across displayed equations.

Important implementation notes:
- Subscript/superscript grammar actions temporarily reduce `ps` by `deltaps`.
- Greater layout complexity lives in the operator files; the grammar mostly dispatches to those functions.
- `stuff` calls `putout` for successful equations and handles parse errors by warning.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/eqn/eqn.y -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/eqn/eqnbox.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/eqn/eqnbox.c

This file concatenates two eqn boxes horizontally.

Key responsibilities:
- Sets `yyval` to the left box register.
- Computes combined baseline and height from both boxes.
- Chooses inter-box spacing with `class[rclass[p1]][lclass[p2]]` and `pad`.
- Handles lineup mode by aligning the left box to register `09`.
- Appends the right box string to the left box string.
- Propagates right font and right class metadata from the right box.
- Frees the right box register.

Important implementation notes:
- This is the core operation used by `eqn : eqn box`.
- The file keeps all spacing decisions dependent on left/right character classes, so text conversion metadata directly affects equation assembly.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/eqn/eqnbox.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/eqn/font.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/eqn/font.c

This file manages local and global font changes in eqn and implements “fat” rendering.

Key responsibilities:
- `setfont` interprets font names/aliases (`I`, `B`, `R`) and pushes a new font stack entry.
- `font` applies a font to a parsed box and restores the previous font.
- `globfont` sets the default font from input.
- `fatbox` overlays a box on itself with a small horizontal shift to simulate bold/fattened output.

Important implementation notes:
- Italic and bold are mapped to troff font positions 2 and 3.
- Unknown font names are treated as roman-style named fonts.
- Font stack overflow is fatal at depth 10.
- Box font metadata is simplified: non-italic renderings are generally marked roman.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/eqn/font.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/eqn/fromto.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/eqn/fromto.c

This file renders lower and upper limits attached to a base box, used for constructs like `sum from ... to ...`.

Key responsibilities:
- Allocates a new result register.
- Measures base, lower, and upper boxes with `nrwid`.
- Computes the maximum width needed to center all components.
- Stacks lower limit below, base in the middle, and upper limit above using vertical and horizontal troff escapes.
- Updates height and baseline for the combined result.
- Frees consumed component registers.

Important implementation notes:
- The lower limit contributes to the baseline offset.
- `ps` is adjusted via `deltaps` to render limits at a smaller size.
- Missing lower or upper boxes are handled independently.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/eqn/fromto.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/eqn/funny.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/eqn/funny.c

This file creates special large operator boxes for sum, product, union, and intersection.

Key responsibilities:
- Maps parser tokens (`SUM`, `PROD`, `UNION`, `INTER`) to predefined troff strings in `deftbl`.
- Allocates a new box register.
- Sets height and baseline using tuning parameters `Funnyps`, `Funnyht`, and `Funnybase`.
- Marks the box as roman on both sides.

Important implementation notes:
- Unknown operator types are fatal.
- The actual glyph definitions are installed by `tuning.c` (`sum_def`, `prod_def`, `union_def`, `inter_def`).
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/eqn/funny.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/eqn/glob.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/eqn/glob.c

This file defines eqn’s global state and default device configuration.

Key contents:
- Default typesetter is `"post"` and device type is `DEVPOST`.
- Default minimum size is 4.
- Debug flag, parser box stack `lp`, string-register usage table, current point size, global size, font, font stack, size stack, display mode, and syntax-error flag.
- Box metadata arrays: `eht`, `ebase`, `lfont`, `rfont`, `lclass`, `rclass`.
- Final equation state: `eqnreg`, `eqnht`.
- Inline delimiter chars and mark/lineup state.

Important implementation notes:
- This file is pure shared state; most eqn files read and mutate these globals.
- The default font is initialized to italic position `'2'`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/eqn/glob.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/eqn/input.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/eqn/input.c

This file implements eqn’s layered input system: files, strings, macros, pushed-back characters, includes, macro arguments, and error context printing.

Key responsibilities:
- Maintains an input source stack with `pushsrc` and `popsrc`.
- Supports macro argument collection in `dodef` and `getarg`.
- Reads characters from files, strings, macros, free strings, and pushback in `input`.
- Handles `$n` macro argument expansion.
- Implements `unput` and `pbstr`.
- Reports errors with file/line context and recent input around the error in `eprint`.

Important implementation notes:
- Includes close files and restore previous `.lf` line directives when popped.
- `eprint` injects `\n.EN\n` as a recovery/safety pushback after errors.
- Macro argument storage uses fixed-size frames and buffers, reflecting old eqn constraints.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/eqn/input.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/eqn/integral.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/eqn/integral.c

This file creates integral symbols and attaches optional subscript/superscript limits.

Key responsibilities:
- `setintegral` allocates a box containing the predefined integral glyph from `deftbl`.
- Sets integral height, baseline, and roman font metadata from tuning parameters.
- `integral` positions lower and/or upper limit boxes around the integral symbol.
- Delegates combined limit layout to `shift2` or `bshiftb`.

Important implementation notes:
- Lower and upper limits are shifted by separate horizontal/vertical tuning values (`Int1h`, `Int1v`, `Int2h`, `Int2v`) before being attached.
- Integral handling reuses the same sub/sup machinery used for ordinary boxes.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/eqn/integral.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/eqn/lex.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/eqn/lex.c

This file is the eqn lexer and directive processor. It turns input into grammar tokens, expands definitions, handles quoted strings, recognizes keywords, and processes top-level eqn directives.

Key responsibilities:
- Skips whitespace and maps `~` to space and `^` to thin space.
- Reads quoted text into `token` and returns `QTEXT`.
- Reads unquoted tokens with `getstr`.
- Expands definitions from `deftbl`, including macros with arguments.
- Recognizes keywords through `keytbl`.
- Processes `define`, `ifdef`, `delim`, `gsize`, `gfont`, `include`, and `space`.
- Handles inline equation termination via `righteq`.

Important implementation notes:
- `define` can tune special floating parameters if the name is in `ftunetbl`.
- `include` opens a file, pushes it onto the input stack, and emits `.lf`.
- `delim off` is represented by setting both delimiter chars to `'\0'`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/eqn/lex.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/eqn/lookup.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/eqn/lookup.c

This file implements eqn keyword, reserved-word, and definition tables.

Key responsibilities:
- Defines `keytbl`, `restbl`, and `deftbl` hash tables.
- Lists language keywords and maps them to yacc tokens.
- Lists reserved mathematical words/symbols and maps them to troff strings or Unicode Greek letters.
- Provides simple additive `hash`, `lookup`, and `install`.
- Initializes tables in `init_tbl`, then calls `init_tune`.

Important implementation notes:
- Keyword aliases include `integral` for `int`, `pile/lpile/cpile/rpile` for column forms, and `copy` for include.
- Reserved words cover relations, arrows, Greek letters, operators, and function names.
- Existing names are updated in place by `install`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/eqn/lookup.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/eqn/main.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/eqn/main.c

This is the eqn command driver. It parses options, initializes device and symbol tables, reads input files, detects display and inline equations, runs the parser, and emits troff output.

Key responsibilities:
- Handles options for delimiters/debug, size, sub/sup size delta, minimum size, font, no-output equations, and typesetter.
- Initializes the typesetter with `settype`.
- Reads each input stream through `getdata`.
- Detects `.EQ`/`.EN` display equations and inline delimiter equations.
- Runs `yyparse` for equation bodies.
- Emits final equation strings, height spacing, `.lf` line synchronization, and mark/lineup support.
- Manages string-register allocation with `salloc`/`sfree`.
- Converts point sizes and em units with `ABSPS`, `DPS`, `EFFPS`, `EM`, and `REL`.

Important implementation notes:
- Inline equations accumulate surrounding text and equation fragments into a temporary string register.
- `putout` adds vertical spacing before/after equations when needed and clears `spaceval`.
- Register IDs 11-99 are available for equation strings.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/eqn/main.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/eqn/mark.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/eqn/mark.c

This file implements eqn `mark` and `lineup`.

Key responsibilities:
- `mark` stores the current horizontal position in troff register `09` with `\k(09`, marks the equation line as containing a mark, and leaves the input box as the result.
- `lineup` marks lineup usage and, when used standalone, creates a box that horizontally moves to the saved mark position.

Important implementation notes:
- `markline` is set to `1` for mark and `2` for lineup, letting `main.c` emit `.nr MK`.
- `lineup(1)` is used when a `LINEUP` precedes a box; `lineup(0)` creates an explicit alignment box.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/eqn/mark.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/eqn/matrix.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/eqn/matrix.c

This file implements matrix column bookkeeping and final matrix assembly.

Key responsibilities:
- `startcol` records the start of a column in the global `lp` array.
- `column` fills in row count and separation for a column.
- `matrix` normalizes row heights and baselines across columns, converts each column into a pile, then concatenates column piles with matrix spacing.

Important implementation notes:
- Matrix layout assumes consistent row counts and a list of columns.
- Row baseline normalization is done before each column is piled.
- Final result uses `Matspace` between column boxes and frees intermediate column pile registers.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/eqn/matrix.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/eqn/move.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/eqn/move.c

This file implements explicit movement commands: `fwd`, `back`, `up`, and `down`.

Key responsibilities:
- Converts the movement amount from hundredths of an em into current-size ems with `EM`.
- Rewrites the box string to include horizontal (`\h`) or vertical (`\v`) motion around the original box.
- Leaves height and baseline metadata unchanged.
- Returns the moved box as `yyval`.

Important implementation notes:
- Horizontal movement prefixes the box with positive or negative `\h`.
- Vertical movement wraps the box in equal and opposite vertical shifts so subsequent output resumes at the original baseline.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/eqn/move.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/eqn/over.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/eqn/over.c

This file implements fractions with the `over` operator.

Key responsibilities:
- Measures numerator and denominator widths.
- Chooses the maximum width plus extra rule width.
- Places denominator below and numerator above the fraction bar.
- Emits a horizontal rule between them.
- Updates combined height and baseline.
- Frees the denominator and temporary width register.

Important implementation notes:
- Tuning parameters `Overgap`, `Overwid`, and `Overline` control spacing and bar length.
- The numerator register is reused as the final result.
- Both left and right font metadata are cleared because the result is a composed object.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/eqn/over.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/eqn/paren.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/eqn/paren.c

This file builds scalable delimiters around an equation box for `left ... right ...`.

Key responsibilities:
- Computes delimiter height from the inside box height.
- Handles special cases for braces, floors, ceilings, brackets, parentheses, vertical bars, and custom delimiters.
- Builds tall delimiters from top/middle/bottom glyph pieces with `brack`.
- Centers or shifts the inside box based on baseline balance.
- Updates height and baseline for the parenthesized result.

Important implementation notes:
- PostScript output applies a small delimiter vertical shift through `Parenshift`.
- Brace height is forced odd and at least three parts.
- `left n`/empty left delimiter emits no left delimiter.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/eqn/paren.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/eqn/pile.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/eqn/pile.c

This file stacks boxes vertically for piles and matrix columns.

Key responsibilities:
- Reads pile metadata and member boxes from the global `lp` array.
- Computes inter-row gap from explicit separation, column type, or `Pilegap`.
- Computes total height and baseline based on the middle element.
- Measures maximum member width.
- Emits a troff string that vertically positions each member and aligns it left, right, or centered.
- Frees all member box registers.

Important implementation notes:
- Column types `LCOL`, `RCOL`, `CCOL`, and `COL` select horizontal alignment.
- Even-length piles use `Pilebase` for baseline placement.
- The final box clears left/right font metadata.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/eqn/pile.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/eqn/shift.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/eqn/shift.c

This file implements subscripts and superscripts.

Key responsibilities:
- `subsup` dispatches to single sub/sup handling or combined sub+sup handling.
- `bshiftb` attaches one subscript or superscript to a base box.
- `shift2` attaches both subscript and superscript, measuring their widths and aligning them as a pair.
- Updates height, baseline, font, and character class metadata after shifts.
- Emits point-size transitions for smaller sub/sup text.

Important implementation notes:
- Spacing depends on italic/roman state and character classes.
- Tuning globals include `Subbase`, `Supshift`, `Sub1space`, `Sup1space`, `Sub2space`, `SS1space`, and `SS2space`.
- Combined sub/sup uses a temporary width register and frees both attached boxes.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/eqn/shift.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/eqn/size.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/eqn/size.c

This file manages local and global point-size changes.

Key responsibilities:
- `setsize` parses relative and absolute size strings and pushes size-stack state.
- `size` wraps a box with troff size changes and restores the previous size.
- `globsize` changes the global size and recomputes default sub/sup delta unless explicitly set.

Important implementation notes:
- Absolute local sizes save the current troff size in numbered registers.
- `DPS` is used for relative transitions; `ABSPS` is used for absolute transitions.
- Invalid size strings generate warnings and leave state mostly unchanged.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/eqn/size.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/eqn/sqrt.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/eqn/sqrt.c

This file renders square roots.

Key responsibilities:
- Estimates a radical point size from the operand height and current point size.
- Adjusts output height based on device type.
- Measures operand width.
- Emits a radical glyph and overbar rule around the operand.
- Preserves the operand register as the result.
- Marks left/right font metadata as roman.

Important implementation notes:
- PostScript uses a different radical scale than CAT/APS/202 devices.
- The code uses register `10` for computed radical size and sets `.af 10 01` once to make it print as two digits.
- Comments acknowledge square-root rendering is approximate and device-specific.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/eqn/sqrt.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/eqn/text.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/eqn/text.c

This file converts eqn text tokens into troff strings and tracks spacing/font metadata for later box composition.

Key responsibilities:
- Defines the character-class spacing matrix used by `eqnbox` and text conversion.
- Converts UTF-8-ish input tokens rune by rune with `textc`.
- Handles quoted text, spaces, thin spaces, tabs, reserved words, letters, digits, punctuation, operators, arrows, troff escapes, and special italic `f`/`j`.
- Adds font transitions and class-based padding through `cadd`, `sadd`, `shim`, and `pad`.
- Sets box height, baseline, left/right font, and left/right class.

Important implementation notes:
- Quoted text without embedded `\f` is wrapped in the current font.
- Reserved words are looked up in `restbl`.
- `cadd` emits font changes only when needed and uses `wctomb` for runes.
- Warnings are emitted for unquoted troff commands other than simple `\(xx` forms.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/eqn/text.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/eqn/tuning.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/eqn/tuning.c

This file defines eqn layout tuning constants and default glyph/string definitions.

Key contents:
- Vertical spacing around sub/sup results.
- Diacritic shifts, bar dimensions, and height adjustments.
- Fat-box shift.
- Large operator sizing and baseline corrections.
- Integral sizing and limit offsets.
- Matrix spacing, fraction spacing, delimiter sizing, pile gaps, and sub/sup spacing.
- Default definitions for vec, dyad, hat, tilde, dot, dotdot, utilde, sum, union, intersection, product, and integral.
- `ftunetbl` support for user-tunable floating parameters.

Important implementation notes:
- `init_tune` installs string definitions into `deftbl` and tunable names into `ftunetbl`.
- `ftune` currently supports only `Subbase` and `Supshift`.
- `ftune` has no fallback if an unknown name reaches it, but callers only use names found in `ftunetbl`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/eqn/tuning.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/evdump.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/evdump.c

This command opens a small draw window and dumps mouse, keyboard, and window-control events. It temporarily remaps keyboard entries to private rune values so it can identify the original layer/keycode/rune mapping on key events.

Key responsibilities:
- Reads `/dev/kbmap`, records mappings, then opens it for writing.
- Installs a note handler to restore the original keyboard map.
- Rewrites mappings to private runes starting at `Kmbase`.
- Opens a new window and initializes draw/mouse.
- Starts keyboard and window-control threads.
- Prints key down/up/repeat, mouse button/position, resize, and window focus/current-state events.

Important implementation notes:
- `k2s` maps many special keyboard runes to symbolic names.
- `wctlproc` restores or reapplies keyboard remapping when the window loses/gains current status.
- `kbproc` compares `/dev/kbd` `k` and `K` records to infer key down/up transitions.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/evdump.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/execnet/client.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/execnet/client.c

This file implements per-client state and I/O behavior for the `execnet` 9P service. Each client represents an executed command exposed as a network-like connection with `ctl` and `data`.

Key responsibilities:
- Allocates/reuses `Client` slots with `newclient`.
- Manages teardown, reference counts, process killing, queued request cleanup, and message cleanup with `closeclient` and `die`.
- Queues read/write 9P requests and read messages.
- Matches queued output messages to queued read requests.
- Runs reader and writer threads around the command pipe.
- Handles flushes for queued or current read/write/exec requests.
- Executes commands via `/bin/rc -c "exec <cmd>"`.
- Parses control writes for `connect` and `hangup`.

Important implementation notes:
- `Zmsg` marks EOF/no-more-data in the message queue.
- `connect` strips any suffix after `!`, then prepends `exec `.
- Writer wakeups use a buffered `writerkick` channel.
- Process setup uses a pipe, duping the command’s stdin/stdout onto the same fd.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/execnet/client.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/execnet/dat.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/execnet/dat.h

This header defines the execnet internal structures and shared API.

Key contents:
- `Msg`: queued output data with linked-list pointer and read pointer/end pointer.
- `Client`: per-connection state including status, pid, command, pipe fds, queued read/write requests, output messages, ioprocs, active write request, and exec request.
- External globals for client table and service object.
- Function prototypes for data reads/writes, client creation/closure, control writes, flush handling, filesystem initialization, and name customization.
- Allocation aliases to lib9p helpers: `emalloc9p`, `estrdup9p`, `erealloc9p`.
- Status enum: `Closed`, `Exec`, `Established`, `Hangup`.
- `STACK` size constant.

Important implementation notes:
- `Client.status` is surfaced through the 9P `status` file.
- The header centralizes the contract between `client.c`, `fs.c`, and `main.c`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/execnet/dat.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/execnet/fs.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/execnet/fs.c

This file implements the 9P filesystem served by execnet. It exposes `/exec`, `/exec/clone`, and per-client directories containing `ctl`, `data`, `local`, `remote`, and `status`.

Key responsibilities:
- Defines qid path encoding with type and client number.
- Fills directory metadata in `fillstat`.
- Generates root, exec, and connection directory entries.
- Handles reads for directories, ctl number, data stream, local pid, remote command, and status.
- Handles writes to ctl and data.
- Handles flushes by routing them to the corresponding client.
- Implements attach, walk, open, clunk handling, and request serialization.

Important implementation notes:
- Opening `clone` creates a new client and rewrites the fid to that client’s `ctl`.
- A dedicated `fsthread` serializes lib9p callbacks through channels, which simplifies shared client-state mutation and flush handling.
- `destroyfid` closes client references when opened fids are clunked.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/execnet/fs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/execnet/main.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/execnet/main.c

This is the execnet command entry point.

Key responsibilities:
- Parses `-D` to enable chatty 9P diagnostics and `-n` to set the served protocol directory name.
- Accepts an optional mount point, defaulting to `/net`.
- Calls `rfork(RFNOTEG)`, installs quote formatting, initializes the filesystem, and posts/mounts the service with `threadpostmountsrv`.

Important implementation notes:
- Usage is `execnet [-n exec] [/net]`.
- `-n` changes the visible protocol directory name from `exec` to the supplied name.
- The service is mounted `MBEFORE`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/execnet/main.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/execnet/note.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/execnet/note.c

This file overrides/augments libthread note handling for execnet. It is explicitly marked `BUG BUG BUG` and includes private `threadimpl.h`.

Key responsibilities:
- Implements `threadnotify` registration keyed by process pid.
- Stores delayed notes in a fixed `notes[128]` table.
- Delivers pending notes when a proc leaves splhi state.
- Implements `_threadnote`, `_procsplhi`, and `_procsplx`.

Important implementation notes:
- Notes are associated with `Proc*` and delivered to handlers registered for that proc’s pid.
- Unhandled notes either fall back to default handling, abort on `sys:` notes, or exit all threads.
- `"threadint"` notes are continued immediately.
- This file reaches into libthread internals and should be treated as compatibility/special-case code rather than ordinary application logic.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/execnet/note.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/exportfs/exportfs.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/exportfs/exportfs.c

This is the main entry point for Plan 9 `exportfs`, a 9P file server that exports a local subtree or an already-open server fd.

Key responsibilities:
- Parses options for debug, message size, root path, root shorthand, pattern file, read-only mode, and server fd file.
- Validates incompatible `-S` and `-r`/`-s` combinations.
- Loads include/exclude patterns.
- Initializes process namespace state with `rfork`.
- Determines message size from `iounit` or defaults.
- Allocates fid hash table and installs fcall formatting.
- Changes directory to the exported root when serving a local tree.
- Initializes root file structures and enters the I/O loop.

Important implementation notes:
- `-F` is accepted and ignored for backward compatibility.
- If chdir to the root fails, it sends a mount error response before exiting.
- `readonly` is global and enforced in request handlers.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/exportfs/exportfs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/exportfs/exportfs.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/exportfs/exportfs.h

This header defines exportfs’s shared state, data structures, constants, errors, and function prototypes.

Key structures:
- `Fsrpc`: buffered 9P request wrapper with flush tag and decoded `Fcall`.
- `Fid`: active 9P fid, local fd, associated `File`, open mode, mount id, and cached directory-read state.
- `File`: cached filesystem node with name, refcount, qid, parent/child links, and invalidation flag.
- `Proc`: worker/slave process bookkeeping for blocking I/O.
- `Qidtab`: maps local qids to unique exported qid paths.

Key constants:
- Fid hash size, fid allocation chunk, pseudo mount count, qid hash width/table size.

Important implementation notes:
- `Extern` is controlled by including source files to define or declare globals.
- The header declares all 9P request handlers, I/O helpers, fid/file/qid helpers, allocation helpers, exclusion handling, and directory filtering.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/exportfs/exportfs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/exportfs/exportsrv.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/exportfs/exportsrv.c

This file implements exportfs’s 9P request handlers and blocking worker process pool.

Key responsibilities:
- Handles `Tversion`, `Tauth`, `Tflush`, `Tattach`, `Twalk`, `Tclunk`, `Tstat`, `Tcreate`, `Tremove`, and `Twstat`.
- Enforces read-only mode for mutating requests and write/truncate opens.
- Supports `-S` pseudo-mount attach by mounting the supplied server fd under `/mnt/exportfs/N`.
- Clones fids and walks cached `File` nodes.
- Converts local `Dir` data into 9P stat responses with unique qid paths.
- Dispatches blocking `Topen`, `Tread`, and `Twrite` to slave processes.
- Implements worker allocation, rendezvous dispatch, flush interruption, and worker cleanup.
- Handles mountpoint traversal by spawning a nested exportfs with `openmount`.

Important implementation notes:
- Flush requests locate a busy slave by old tag, set `flushtag`, and post a `"flush"` note.
- `blockingslave` replies to pending flush tags after leaving the busy section.
- `slaveread` uses `preaddir` for filtered directories when a pattern file is active.
- `openmount` carefully closes fds before execing `/bin/exportfs -S/fd/N`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/exportfs/exportsrv.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/exportfs/io.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/exportfs/io.c

This file implements exportfs’s main 9P message loop, reply encoding, fid allocation, file cache management, qid uniqueness, and allocation/fatal helpers.

Key responsibilities:
- Reads 9P messages from stdin, decodes them, and dispatches through `fcalls`.
- Encodes and writes replies in `reply`.
- Sends an initial mount error response in `mounterror`.
- Manages fid lookup/allocation/free lists.
- Allocates and recycles `Fsrpc` buffers.
- Maintains cached `File` trees with parent/child links and reference counts.
- Builds local paths from cached file ancestry with `makepath`.
- Maps local qids to unique exported qids with `Qidtab`, collision handling, and high-bit uniqueness.
- Initializes root and pseudo mount-point cache in `initroot`.
- Implements fatal shutdown by killing slave children.

Important implementation notes:
- `uniqueqid` preserves the low 48 bits of local qid path and uses upper bits to resolve collisions.
- `freefile` recursively releases parent refs as child refs drop to zero.
- `freefid` unmounts pseudo mounts associated with fids.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/exportfs/io.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/exportfs/pattern.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/exportfs/pattern.c

This file implements exportfs include/exclude pattern filtering and filtered directory reads.

Key responsibilities:
- Reads a pattern file where lines beginning `+ ` define required include regexps and lines beginning `- ` define exclude regexps.
- Compiles patterns with Plan 9 regex.
- Applies include and exclude logic in `excludefile`.
- Implements `preaddir`, a directory reader that filters entries while maintaining 9P directory offsets.

Important implementation notes:
- Include patterns are all required: if any include regexp does not match, the path is excluded.
- Exclude patterns reject a path when any regexp matches.
- Paths are normalized by dropping the leading `.` path prefix, with root represented as `/`.
- `preaddir` cannot seek arbitrary directory offsets except reset to 0 or continue from current filtered offset.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/exportfs/pattern.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ext4srv/common.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ext4srv/common.h

This header defines shared ext4srv option and partition structures plus lifecycle prototypes.

Key structures:
- `Opts`: mount/open options including group, as-root mode, ream flag, block size, inode size, and label.
- `Part`: reference-counted, locked mounted partition object. It links into a list, stores the device path, ext4 mountpoint/blockdev/interface/superblock/locks, Plan 9 qid fields, group data, backing fd, and trailing block buffer.

Key functions declared:
- `openpart`
- `closepart`
- `closeallparts`
- `statallparts`
- `syncallparts`

Important implementation notes:
- `Part` embeds both Plan 9 synchronization/reference primitives (`Ref`, `QLock`) and ext4 library structures.
- The flexible `blkbuf[]` tail indicates allocation size depends on block-buffer needs.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ext4srv/common.h -->