# Group Research: group_181_9front_sources_os_plan9_9front_sys_src_cmd_tbl_t8_c_sources_os_plan9_ef21801fc189

Scope verified against `Docs/research_subset_a.md`: `sources/os/plan9/9front` is included in subset A. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/tbl/t8.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/tbl/t8.c

Implements the main per-row emission path for the Plan 9 `tbl` formatter.

Key points:
- `putline` writes one formatted table row to `tabout`, handling top/bottom full-width rules, explicit replacement lines, vertical spans, font/size changes, horizontal alignment registers, numeric split columns, half-line raising, and deferred diverted text.
- Uses `watchout` to detect diverted/text-block cells that require a second positioning pass through `funnies`.
- Emits troff/nroff requests such as `.ne`, `.mk`, `.nr`, `.vs`, `\h`, and `\v` to place table content and line art.
- Numeric and alphabetic columns may be split into left/right fields via `table[nl][c].rcol`, with `F1`/`F2` delimiter characters around fields.
- `puttext`, `putfont`, and `putsize` wrap raw cell text with selected font and point-size escapes.
- `funnies` repositions diverted text blocks after the normal row pass, computes indentation from column registers, restores fonts, tracks row bottom position, and draws any vertical lines that cross the row.

Dependencies and interactions:
- Depends on global table state from `t.h`: `table`, `style`, `font`, `csize`, `flags`, `linestop`, `topat`, `ncol`, `nlin`, and troff register constants.
- Calls helpers from neighboring files: `fullwide`, `runtabs`, `ctype`, `left`, `drawvert`, `tohcol`, `reg`, `ctspan`, `makeline`, `ifline`, `filler`, `vspen`, `point`, `prev`, `next`, and `allh`.

Research relevance:
- This is the central renderer for `tbl`: it converts parsed table rows into troff positioning commands and line drawing operations.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/tbl/t8.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/tbl/t9.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/tbl/t9.c

Handles continuation output for tables larger than the normal in-memory row set.

Key points:
- `yetmore` finds an existing real table row to reuse as the formatting template, maps it to `table[0]`, identifies the last real format line, then streams leftover and subsequent input lines through `domore`.
- `domore` stops at `.TE`, passes through non-data troff commands, handles single `_` and `=` lines as full-width rules, splits tab-separated input fields into `table[0][icol]`, and applies numeric/alphabetic right-column splitting.
- Reuses `exspace` after each emitted row so numeric split scratch storage does not grow unbounded.

Dependencies and interactions:
- Uses parser globals `leftover`, `cstore`, `cspace`, `tab`, `fullbot`, `instead`, and `table`.
- Calls `gets1`, `prefix`, `ctype`, `maknew`, `putline`, `domore`, and `error`.

Research relevance:
- This file provides the streaming fallback that lets `tbl` process very long tables without keeping every row resident.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/tbl/t9.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/tbl/tb.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/tbl/tb.c

Provides cell-use analysis and simple arena-style storage for `tbl`.

Key points:
- `checkuse` scans all real table rows and marks per-column usage arrays: `used`, `lused`, and `rused`.
- Numeric/alphabetic split columns are tracked separately so zero-width left or right fields can be skipped during output.
- `real` distinguishes absent/empty cells from actual text or encoded non-pointer sentinel values.
- `chspace` allocates reusable character arenas of `MAXCHS + MAXLINLEN`, limited by `MAXVEC`.
- `alocv` allocates zeroed vector storage from reusable `MAXCHS` chunks, with `tpcount` and `thisvec` acting as a bump allocator.
- `release` resets allocation cursors and `exstore`; it intentionally does not free the underlying arenas.

Dependencies and interactions:
- Uses global column/row state from `t.h`.
- Allocation failures and excessive storage requests terminate through `error`.

Research relevance:
- This is support infrastructure for `tbl` layout decisions and memory reuse across tables.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/tbl/tb.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/tbl/tc.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/tbl/tc.c

Chooses internal delimiter characters for marking table field boundaries in generated troff.

Key points:
- `choochar` scans all real cell text and right-column text for ASCII characters already present.
- It chooses `F1` and `F2` from a priority string of uncommon control/punctuation/letter characters, falling back through `Y` and `u`.
- Fails if two unused delimiters cannot be found.
- `point` classifies a `char *` value as a real pointer versus a small encoded sentinel by checking whether the cast address is at least 128.

Dependencies and interactions:
- Used by output code that wraps fields with `F1` and `F2`.
- Depends on `ctype`, `point`, `table`, `instead`, `fullbot`, `nlin`, and `ncol`.

Research relevance:
- This file protects generated troff field delimiters from colliding with user table text.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/tbl/tc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/tbl/te.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/tbl/te.c

Implements error reporting and low-level input handling for `tbl`.

Key points:
- `error` prints the active input file and line, announces `tbl quits`, and exits.
- `gets1` reads one logical line from `tabin`, increments `iline`, swaps input files when needed, bounds-checks the caller buffer, strips the newline, and folds escaped newlines while inside a table.
- `un1getc` implements a small pushback buffer and adjusts `iline` for pushed-back newlines.
- `get1char` reads from pushback or `tabin`, swaps input files on EOF, errors on unexpected EOF, and increments `iline` for newline characters.

Dependencies and interactions:
- Uses Plan 9 `Biobuf` routines `Brdline`, `Blinelen`, and `Bgetc`.
- Calls `swapin` for multi-file input sequencing.

Research relevance:
- This is the shared input/error layer used by the parser and text-block reader.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/tbl/te.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/tbl/tf.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/tbl/tf.c

Saves and restores troff fill state around generated tables.

Key points:
- `savefill` defines a macro that restores point size, vertical spacing, indentation, fill mode, and adjustment mode, then switches table output to no-fill mode.
- Initializes `#~`, an output-device-specific offset used for T450/nroff box adjustment.
- `rstofill` invokes the saved-state macro.
- `endoff` clears line-stop registers, removes text diversions, and emits `last`.
- `ifdivert` sets string `#d` to either `.d` or `nl` depending on diversion state.
- `saveline` and `restline` preserve input line accounting around table processing.
- `cleanfc` resets field characters with `.fc`.

Dependencies and interactions:
- Uses `linestop`, `texstr`, `texct`, `last`, `iline`, and `linstart`.
- Emitted macros are consumed by later row and line rendering code.

Research relevance:
- This file isolates table rendering from the surrounding document’s troff fill and line-count state.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/tbl/tf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/tbl/tg.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/tbl/tg.c

Processes `T{ ... T}` multiline text blocks inside table cells.

Key points:
- `gettext` starts a diversion for the current text block, appends it to the right-column register macro, and emits setup for fill mode, fonts, point size, vertical spacing, line length, and indentation.
- Reads lines until `T}` or `T}<tab>`; missing terminator resets `iline` to the starting line before reporting an error.
- Stores diversion height and width in registers named from `texname`.
- Copies any text after `T}<tab>` back into the caller buffer as remaining cell content.
- Advances `texname` through `texstr` and returns the diversion character used for the text block.
- `untext` restores no-fill table mode and line length after text-block processing.

Dependencies and interactions:
- Calls `gets1`, `match`, `tcopy`, `reg`, `ctspan`, `ctype`, and `rstofill`.
- Uses globals `textflg`, `texname`, `texstr`, `texct`, `vsize`, `cll`, `tab`, and line/column style arrays.

Research relevance:
- This is the bridge between `tbl` cells and troff diversions for multiline formatted text.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/tbl/tg.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/tbl/ti.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/tbl/ti.c

Classifies horizontal/vertical line intersections for table rule drawing.

Key points:
- `interv` determines how a vertical line at column boundary `c` intersects a horizontal rule at row `i`, returning `TOP`, `BOT`, `THRU`, or no intersection.
- Handles double boxes specially at left/right borders.
- `interh` performs the complementary classification for horizontal context around a vertical line, considering full bottom rules and double-box borders.
- `up1` skips replacement rows while looking upward for the previous meaningful row.

Dependencies and interactions:
- Calls `lefdata`, `allh`, `thish`, and `up1`.
- Used by `drawline` and `drawvert` to slightly extend or retract rule endpoints so intersections render correctly.

Research relevance:
- Encodes the geometry needed for visually coherent table borders and internal rules.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/tbl/ti.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/tbl/tm.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/tbl/tm.c

Splits numeric table fields into left and right parts for decimal alignment.

Key points:
- `maknew` searches a field for an explicit `\&` split marker, otherwise finds a decimal point outside `eqn` delimiters, otherwise finds the boundary after the final numeric run.
- If no numeric split point exists, returns `0` and leaves the field unsplit.
- Copies the right-hand part into reusable `exspace` storage and truncates the original string at the split point.
- `ineqn` tracks whether a candidate split position lies between equation delimiters `delim1` and `delim2`.

Dependencies and interactions:
- Uses `chspace`, `exstore`, `exlim`, `exspace`, `digit`, and global equation delimiters.
- Called when parsing numeric columns in normal and continuation table paths.

Research relevance:
- Provides `tbl`’s decimal/numeric alignment behavior.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/tbl/tm.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/tbl/tr.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/tbl/tr.c

Allocates troff number-register names for table column measurements.

Key points:
- `nregs` is a fixed table of two-character register names.
- The comment notes it must contain at least `3*qcol` entries because each column needs left, middle, and right measurement registers.
- `reg(col, place)` bounds-checks against `qcol` and returns the register name for a given column and place.

Dependencies and interactions:
- Used throughout table rendering for column left/middle/right positions.
- Errors through `error` if too many columns are requested.

Research relevance:
- This is the central register-name mapping for `tbl` layout.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/tbl/tr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/tbl/ts.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/tbl/ts.c

Contains small string and numeric helper routines for `tbl`.

Key points:
- `match` checks full string equality.
- `prefix` checks whether one string is a prefix of another.
- `letter`, `digit`, `numb`, and `max` provide simple character/integer utilities.
- `tcopy` copies a NUL-terminated string.

Dependencies and interactions:
- Used by parser, text-block handling, numeric splitting, and option logic.

Research relevance:
- Utility file with no table-specific state, but used broadly by the command.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/tbl/ts.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/tbl/tt.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/tbl/tt.c

Provides helpers for table style lookup, spanning, and horizontal-rule classification.

Key points:
- `ctype` maps a data row and column to the active style character, suppressing replacement/full-rule rows.
- `fspan`, `lspan`, and `ctspan` identify horizontal span relationships.
- `tohcol` emits troff horizontal movement to a column boundary or midpoint between adjacent columns.
- `allh` returns true when a row is entirely horizontal-rule content and contains at least one real rule.
- `thish` classifies a cell as no rule, empty, single rule, double rule, or vertically spanned placeholder; it follows spans leftward and recognizes `_`, `=`, and escaped rule entries.

Dependencies and interactions:
- Uses `table`, `style`, `stynum`, `fullbot`, `ncol`, `nlin`, and helpers `reg`, `point`, `vspen`, and `barent`.
- Called heavily by horizontal/vertical line drawing.

Research relevance:
- This file is the rule/spanning query layer used by the renderer.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/tbl/tt.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/tbl/tu.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/tbl/tu.c

Draws horizontal rules and maintains line-stop metadata for `tbl`.

Key points:
- `makeline` expands a single cell rule into the full span of adjacent compatible rule cells, unless it is a short escaped rule.
- `fullwide` draws full-width top/bottom/all-table rules while skipping vertically spanned columns.
- `drawline` emits troff `\l` line-drawing commands, choosing one or two strokes for single/double rules and adjusting endpoints at vertical intersections.
- Handles printer-specific behavior for `pr1403` and line-size adjustments via `LSIZE`.
- `getstop` assigns line-stop registers used as vertical-line endpoints.
- `left` finds the start row and width of a vertical line segment at a column boundary.
- `lefdata` derives vertical-line style from explicit left-line style, box/double-box/all-line flags, and spans.
- `next` and `prev` skip full-rule/replacement rows while walking table data.

Dependencies and interactions:
- Calls `thish`, `ctype`, `interv`, `tohcol`, `reg`, `vspand`, `lefdata`, `prev`, and `next`.
- Feeds vertical-line drawing by populating `linestop`.

Research relevance:
- This is the core horizontal-line renderer and vertical-line segment discovery code.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/tbl/tu.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/tbl/tv.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/tbl/tv.c

Draws vertical table rules.

Key points:
- `drawvert` emits troff `\L` vertical line commands from a start row to an end row at column boundary `c`.
- Handles single and double vertical rules by drawing multiple offset strokes.
- Adjusts top and bottom endpoints based on adjacent horizontal rules, full bottom rules, all-horizontal rows, and intersection classifications.
- Uses `linestop` registers and string `#d` to account for normal versus diversion vertical position.
- `midbar` and `midbcol` detect whether a horizontal bar crosses the vertical line boundary.
- `barent` recognizes cell strings that encode `_` or `=` rule entries, including escaped forms.

Dependencies and interactions:
- Calls `interh`, `midbar`, `midbcol`, `barent`, `allh`, `ctype`, and `point`.
- Consumes line stops created by `getstop`.

Research relevance:
- Complements `tu.c` by rendering vertical borders and separators with correct intersections.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/tbl/tv.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/tc/cgen.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/tc/cgen.c

Implements expression, address, boolean, and structure code generation for the 9front Thumb C compiler backend.

Key points:
- `cgen` is the main expression generator. It handles assignments, bitfields, arithmetic/logical operations, division/modulo optimizations, compound assignments, calls, indirection, comparisons, casts, comma/conditional expressions, and pre/post increment/decrement.
- Constant power-of-two signed division/modulo is lowered into shifts/masks with sign correction.
- Multiplication by constants delegates to `mulcon`.
- `reglcgen`, `reglpcgen`, and `lcgen` generate l-values/addresses, folding small constant offsets into indirect-register addressing where possible.
- `bcgen` and `boolgen` generate branches or boolean materialization for comparisons, constants, logical operators, conditionals, and generic truth tests.
- `sugen` copies or constructs aggregate and 64-bit-like values, including struct literals, struct assignment, function-returned structs, conditional structs, and block copies using `MOVM` where profitable.

Dependencies and interactions:
- Uses register allocation and instruction emission from `txt.c`.
- Uses bitfield helpers, switch/string/global helpers from `swt.c`, multiply table logic from `mul.c`, and type/complextity analysis from `sgen.c`.
- Relies on shared backend globals declared in `gc.h`.

Research relevance:
- This is the core lowering layer from C AST nodes to Thumb backend instructions.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/tc/cgen.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/tc/gc.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/tc/gc.h

Defines shared data structures, constants, globals, and prototypes for the Thumb C compiler backend.

Key points:
- Includes common C compiler definitions and ARM object definitions from `../cc/cc.h` and `../5c/5.out.h`.
- Sets target type sizes for Thumb: 1-byte char, 2-byte short, 4-byte int/long/pointer/float, 8-byte vlong/double.
- Defines backend structures: `Adr`, `Prog`, `Case`, `C1`, `Multab`, `Hintab`, `Var`, `Reg`, and `Rgn`.
- Declares global codegen, register allocation, control-flow, switch, string, and optimization state.
- Defines register allocator bitset helpers and cost constants.
- Declares function prototypes for `sgen.c`, `cgen.c`, `txt.c`, `swt.c`, `list.c`, `reg.c`, and `peep.c`.
- Registers custom Plan 9 `Fmt` conversions for instructions, addresses, registers, symbols, and bitsets.

Dependencies and interactions:
- Every `tc` backend source includes this file.
- Shared with assembler/object constants from the ARM toolchain headers.

Research relevance:
- This is the interface contract tying together the backend files in this group.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/tc/gc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/tc/list.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/tc/list.c

Provides formatting routines for debug/listing output from the Thumb compiler backend.

Key points:
- `listinit` installs custom formatters for opcodes, programs, strings, names, bitsets, addresses, and register lists.
- `Bconv` prints compiler bitsets as variable names or constant offsets.
- `Pconv` formats `Prog` instructions, including special cases for `MOVM` and `DATA`.
- `Aconv` maps opcode numbers through `anames`.
- `Dconv` formats all backend address kinds: extern/static/name, const, offset register, register, float register, PSR, branch, floating constant, and string constant.
- `Rconv` formats `MOVM` register-list constants.
- `Sconv` escapes fixed-size string constants.
- `Nconv` formats symbolic address names relative to `SB`, `SP`, or `FP`.

Dependencies and interactions:
- Uses `Fmt`, `Adr`, `Prog`, `Var`, symbol tables, and opcode names from `gc.h`.
- Called by debug printing in codegen, register allocation, and object emission.

Research relevance:
- This file makes backend diagnostics and listings readable.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/tc/list.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/tc/mul.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/tc/mul.c

Finds short shift/add/subtract sequences for multiplication by integer constants.

Key points:
- `mulcon0` normalizes negative constants, checks a small cache, searches an exception hint table, then tries bounded sequence generation.
- Encoded sequences use pairs such as shift letters (`a` plus amount) and add/subtract operators with operand-routing digits.
- `docode` validates and expands encoded hints into executable sequence codes while simulating register values.
- `gen1`, `gen2`, and `gen3` recursively search for sequences within `maxmulops`, tracking whether temporary values have been shifted or used.
- If the constant has trailing zero bits, the code can recursively generate a sequence for the odd factor and append a final shift.
- `hintab` contains hand-supplied sequences for constants that the bounded search misses; `hintabsize` exports its length.

Dependencies and interactions:
- `swt.c` consumes generated `Multab` entries in `mulcon`.
- Uses `Multab` and `Hintab` definitions from `gc.h`.

Research relevance:
- Implements a classic compiler strength-reduction path for constant multiplication on Thumb.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/tc/mul.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/tc/peep.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/tc/peep.c

Performs peephole and copy/constant propagation over backend register-flow nodes.

Key points:
- `peep` completes missing `Reg` nodes between optimizer blocks, repeatedly eliminates redundant register moves via copy propagation, applies substitution propagation, folds constant moves, rewrites `EOR -1,x,y` to `MVN x,y`, and removes redundant repeated byte/halfword extension moves.
- `excise` turns an instruction into `NOP`.
- `uniqp` and `uniqs` detect unique predecessor/successor paths.
- `subprop` rewrites register copy direction through a basic path to make later copy elimination possible.
- `copyprop` and `copy1` implement the main copy-propagation data walk.
- `constprop` replaces repeated identical constants with register references until the register is clobbered or control merges.
- `copyu` classifies instruction use/set behavior for registers and constants across moves, arithmetic, branches, calls, returns, and `MOVM`.
- `copyas`, `copyau`, `copyau1`, `copysub`, and `copysub1` perform address equality, address-use checks, and substitution.

Dependencies and interactions:
- Operates on `Reg` graph built by `reg.c`.
- Uses backend opcodes/address classes from `gc.h`.

Research relevance:
- This is the late local optimizer for removing redundant Thumb instructions after global register optimization.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/tc/peep.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/tc/reg.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/tc/reg.c

Implements global register allocation and data-flow optimization for the Thumb compiler backend.

Key points:
- `regopt` builds a `Reg` control-flow graph from emitted `Prog`s, records variable uses/sets, links branches, computes loop structure, propagates liveness and synchrony, identifies profitable live regions, assigns registers, rewrites code, runs peephole optimization, recomputes program counters, patches branches, removes `NOP`s, and recycles `Reg` nodes.
- `mkvar` maps address operands to tracked variables and classifies externs, params, constants, and address-taken/punned variables.
- `prop` propagates reference/call liveness backwards through predecessors.
- `postorder`, `rpolca`, `doms`, `loophead`, `loopmark`, and `loopit` compute reverse postorder, approximate dominators, and loop weighting.
- `synch` propagates variable/register synchrony forward.
- `paint1` scores a candidate live region; `paint2` finds register conflicts; `allreg` selects integer or float registers; `paint3` rewrites references to use the chosen register and inserts loads/stores with `addmove`.
- `RtoB`, `BtoR`, `FtoB`, and `BtoF` map registers to allocator bit masks.

Dependencies and interactions:
- Calls `peep` unless disabled by debug flags.
- Uses instruction emission/address structures from `gc.h` and formatting helpers for diagnostics.
- Inserts actual load/store instructions by allocating new `Prog` nodes.

Research relevance:
- This is the main backend optimizer and register allocator for generated Thumb code.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/tc/reg.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/tc/sgen.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/tc/sgen.c

Generates code for statements and computes addressability/complexity for expressions.

Key points:
- `codgen` emits a function prologue `TEXT`, handles the first register argument, generates the function body, warns on missing returns, emits final return code, invokes register optimization, and adjusts stack size for argument-safe space.
- `supgen` generates code in suppression mode for dead or constant-folded branches without keeping emitted instructions.
- `gen` handles statement nodes: lists, returns, labels, gotos, cases, switches, loops, continue/break, if/else, and used/set pseudo-operations.
- Switch statement generation collects cases, emits body and break target, then calls `doswit`.
- `usedset` emits `NOP` markers for volatile/set/use tracking.
- `noretval` emits pseudo uses of return registers to preserve return-value liveness.
- `xcom` computes expression addressability and register complexity, folds address/indirect patterns, normalizes constant operands, rewrites power-of-two multiplies/divides/modulos into shifts/ands, and marks function calls as high complexity.
- `bcomplex` prepares conditional expressions, performs type compatibility checks, constant-deadhead detection, 64-bit boolean lowering, and branch generation.

Dependencies and interactions:
- Calls `complex`, `cgen`, `sugen`, `doswit`, `regopt`, and many emission helpers from `txt.c`.
- Uses global control-flow labels `breakpc`, `continpc`, and `cases`.

Research relevance:
- This file is the statement-level frontend to the backend code generator.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/tc/sgen.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/tc/swt.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/tc/swt.c

Implements switch lowering, bitfield helpers, string/global data emission, object serialization, and target alignment.

Key points:
- `doswit` collects `case` nodes, validates defaults and duplicates, sorts cases, and dispatches to `swit1`.
- `swit1` emits either linear comparisons for small switches or recursive binary-search comparisons for larger switches.
- `bitload` and `bitstore` load, mask, sign/zero extend, merge, and store bitfield values.
- `outstring` and `outlstring` place string data into `ADATA` records, chunked by `NSNAME` and respecting suppression/alignment.
- `mulcon` consumes `mul.c` sequences to lower multiplication by constants into shifts/adds/subtracts.
- `nullwarn` warns on unused expression results while still generating side effects.
- `sextern` and `gextern` emit static/global data initializers.
- `outcode`, `zwrite`, `zname`, `zaddr`, and `outhist` serialize instructions, symbols, history, names, addresses, constants, and signatures to the object stream.
- `ieeedtod` encodes host doubles into Plan 9 IEEE words.
- `align` and `maxround` implement target-specific struct, argument, and automatic-storage alignment.

Dependencies and interactions:
- Uses output buffer `outbuf`, symbol tables, history records, and backend instruction stream.
- Called by statement/expression generation, global initialization, and final compiler cleanup.

Research relevance:
- This file covers several backend boundary concerns: switch code shape, object format emission, data layout, and constant multiply lowering.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/tc/swt.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/tc/txt.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/tc/txt.c

Provides backend initialization, register allocation helpers, address lowering, instruction emission, type moves, branches, pseudo-ops, and target type tables.

Key points:
- `ginit` initializes the Thumb/ARM backend identity, formatter hooks, program list state, return/safe pseudo nodes, 64-bit support, and register usage.
- `gclean` checks leaked registers, flushes string data, emits global declarations, appends `AEND`, and calls `outcode`.
- `nextpc` allocates and appends a zeroed `Prog`.
- `gargs` and `garg1` evaluate call arguments, precomputing call-heavy arguments into temporaries and assigning register/stack/aggregate argument slots.
- `nodconst`, `nod32const`, `nodfconst`, `nodreg`, `regret`, `regalloc`, `regialloc`, `regfree`, `regsalloc`, `regaalloc1`, `regaalloc`, and `regind` manage temporary nodes and fixed register allocation.
- `naddr` converts AST nodes into backend `Adr` operands; `raddr` extracts register operands.
- `gmove` handles loads, stores, and all scalar/float/integer conversion move opcodes.
- `gins`, `gopcode`, `gopcode2`, `gbranch`, `patch`, and `gpseudo` emit real and pseudo instructions.
- `sconst`, `sval`, and `exreg` classify constants and allocate external register slots.
- `ewidth` and `ncast` define target type widths and legal no-op cast families.

Dependencies and interactions:
- Heavily used by `cgen.c`, `sgen.c`, `swt.c`, and `reg.c`.
- Emits opcodes from `5.out.h` and uses type metadata from the common compiler.

Research relevance:
- This is the backend’s instruction construction and target ABI/layout support layer.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/tc/txt.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/tcs/8859.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/tcs/8859.h

Defines ISO-8859 charset-to-Unicode mapping tables for `tcs`.

Key points:
- Contains 256-entry `long` tables for ISO-8859 variants: `tab8859_1`, `_2`, `_3`, `_4`, `_5`, `_6`, `_7`, `_8`, `_9`, `_10`, and `_15`.
- Values are Unicode code points; unmapped slots are represented by `-1`.
- `tab8859_1` is identity mapping for all 256 bytes.
- Invalid-entry counts observed while reading: `_3` has 7, `_6` has 45, `_7` has 6, `_8` has 38; the other listed tables have no `-1` entries.
- Tables cover Latin, Cyrillic, Arabic, Greek, Hebrew, Turkish, Nordic, and Latin-9/Euro mappings.
- Some comments identify external provenance for ISO-8859-10 and ISO-8859-15 mappings.

Dependencies and interactions:
- Intended to be included by the `tcs` charset conversion command.
- Complements `big5.h`/`big5.c` for non-ISO mappings.

Research relevance:
- Static conversion data for single-byte encodings to Plan 9 runes/Unicode.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/tcs/8859.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/tcs/big5.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/tcs/big5.c

Defines the Big5-to-Unicode mapping table for `tcs`.

Key points:
- Includes `big5.h` and defines `long tabbig5[BIG5MAX]`.
- The table has `BIG5MAX` entries, 13,973 total.
- Entries are Unicode code points for Big5 ordinals; unmapped entries are `-1`.
- Reading/counting found 270 invalid `-1` slots.
- Non-invalid values range from `0x23` through `0xff5d`; the first entry is `0x3000`.
- The table covers punctuation, fullwidth forms, symbols, radicals, CJK ideographs, and extended Big5 ranges, ending with unmapped padding slots.

Dependencies and interactions:
- Size and extern declaration come from `big5.h`.
- Consumed by the `tcs` charset conversion implementation when decoding Big5 input.

Research relevance:
- Large static charset data table, not executable logic, but essential for Big5 conversion.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/tcs/big5.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/tcs/big5.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/tcs/big5.h

Declares constants and external storage for the Big5 mapping table.

Key points:
- Defines `BIG5MAX` as `13973`.
- Defines `BIG5FONT` as `157`.
- Declares `extern long tabbig5[BIG5MAX]`, described as runes indexed by Big5 ordinal.

Dependencies and interactions:
- Included by `big5.c` and charset conversion code using the Big5 table.

Research relevance:
- Small header that fixes the Big5 table size and public symbol.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/tcs/big5.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/tcs/charsets.awk -->
# File Research: sources/os/plan9/9front/sys/src/cmd/tcs/charsets.awk

Generates charset alias entries from IANA charset XML and a local `tcs.txt`-style mapping file.

Key points:
- Intended input is `character-sets.xml` plus a second mapping file supplied as `ARGV[2]`.
- On `<name>` blocks, normalizes the charset name to lowercase, records it as canonical, and starts an alias list.
- On `<alias>` blocks, normalizes aliases to lowercase and adds them to the current canonical name.
- In `END`, reads the second file; for each `tcs` charset name found in the parsed IANA names, prints `"alias", "converter",` entries for every alias associated with that canonical name.
- Uses simple XML tag stripping with `gsub(/[<>\/]+/, " ")`.

Dependencies and interactions:
- Used as a build/generation helper for `tcs` charset alias tables.
- Assumes a simple IANA XML structure where name/alias text is in `$2` after tag stripping.

Research relevance:
- Build-time script that keeps `tcs` charset aliases aligned with IANA names and local converter names.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/tcs/charsets.awk -->