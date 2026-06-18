# Group Research: group_1521_plan9_sources_os_plan9_plan9_sys_src_cmd_fossil_source_c_sources_os_6025d0221bf9

Scope verified against `Docs/research_subset_a.md`: `sources/os/plan9/plan9` is included in subset A. All listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/fossil/source.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/fossil/source.c

This file implements Fossil’s `Source` abstraction: a locked handle over a Venti/Fossil `Entry` and its block tree. It validates entries, opens roots and child sources, creates/removes/truncates sources, tracks directory entry counts, and reads/updates entry metadata.

The core behavior is copy-on-write block walking. `_sourceBlock` computes pointer indexes for a block number, grows pointer depth when needed, and uses `blockWalk` to fetch or copy blocks into the current epoch. `sourceGrowDepth`, `sourceShrinkDepth`, and `sourceShrinkSize` maintain the Venti pointer tree and remove stale local links.

Locking is coupled to block references: `sourceLock` loads the block containing the source entry and stores it in `r->b`; `sourceUnlock` releases it. `sourceLock2` special-cases siblings in the same entry block and orders locks to reduce deadlock risk.

Snapshot handling appears in `sourceAlloc`, `sourceLoadBlock`, and `_sourceBlock`: writable opens reject snap entries, read-only snapshot sources enforce epoch windows, refresh stale local labels by rewalking from the parent, and reject `VtEntryNoArchive` data for snapshot reads.

Notable observation: `sourceShrinkDepth` contains an explicit `BUG` comment questioning `type++`, so depth-shrink behavior is a known sensitive area.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/fossil/source.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/fossil/srcload.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/fossil/srcload.c

This is a standalone stress/benchmark driver for Fossil `Source` trees. It opens a Fossil filesystem with `fsOpen`, dumps and counts the source tree, repeatedly creates and deletes random directory/file entries, prints stats, and measures total runtime.

The helper routines recursively create entries (`new`), recursively delete entries (`delete`), dump tree structure (`dump`), count descendants (`count`), and report top-level/max-depth statistics (`stats`). A dormant `bench` helper times repeated `sourceGetEntry` calls.

It depends directly on `fsOpen`, `Source` APIs, `Entry`, Venti formatting, and Plan 9 `Biobuf`. It looks like development/test code rather than production command code.

Compatibility note: calls such as `sourceOpen(s, ..., OReadWrite)` use a three-argument form, while `source.c` in this group defines `sourceOpen(Source*, ulong, int, int)`, suggesting this file may be stale relative to the current API or compiled with a wrapper/prototype elsewhere.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/fossil/srcload.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/fossil/stdinc.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/fossil/stdinc.h

This is the common Fossil include shim. It includes Plan 9 base headers `<u.h>` and `<libc.h>`, defines Venti integer aliases (`u64int`, `u8int`, `u16int`), then includes `oventi.h`, `vac.h`, and `fs.h`.

It centralizes the minimal platform and Fossil/Venti type environment used by the surrounding Fossil C files.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/fossil/stdinc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/fossil/trunc.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/fossil/trunc.c

This is a tiny Plan 9 utility that truncates a file to a requested size. It expects `file size`, initializes a null `Dir`, sets `d.length` from `strtoull`, then applies it with `dirwstat`.

It exits with usage on wrong arity and reports `dirwstat` failures via `sysfatal`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/fossil/trunc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/fossil/unpack -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/fossil/unpack

This is an `rc` script for unpacking a Plan 9 distribution ISO into `/n/ehime/testplan9`. It copies and decompresses `plan9.iso.bz2`, starts `9660srv`, mounts the ISO, recreates the destination tree, runs `dircp`, and creates an extra `/n/emelieother` directory for `lp`.

It is operational/test data movement glue, not C source.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/fossil/unpack -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/fossil/vac.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/fossil/vac.c

This file implements Fossil directory metadata serialization, not the standalone `vac` archiver command. It packs/unpacks `MetaBlock`, `MetaEntry`, and `DirEntry` records using big-endian integer macros and Venti/Fossil allocation helpers.

`mbUnpack`, `mbPack`, `mbInsert`, `mbDelete`, `mbResize`, `mbAlloc`, and compaction helpers manage metadata block layout: header, index table, entry payloads, free space, holes, and legacy `MetaMagic-1` “botch” ordering.

`deSize`, `dePack`, and `deUnpack` encode/decode versioned directory entries including element name, data/meta entry references and generations, qid, uid/gid/mid, times, mode, and optional Plan 9/qid-space records. Versions 7 through 9 are accepted, with compatibility behavior for older fields.

Notable behavior: `mbSearch` supports both current and old broken prefix comparison order through `mb->botch`, preserving lookup compatibility with old on-disk metadata.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/fossil/vac.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/fossil/vac.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/fossil/vac.h

This header defines Fossil/Vac metadata structures and constants used by `vac.c` and viewers: `DirEntry`, `MetaEntry`, `MetaBlock`, metadata magic/header/index sizes, directory entry magic, mode bits, and optional directory-entry field tags.

It declares pack/unpack, allocation, search, insert/delete, resize, cleanup, and copy routines for directory metadata.

The mode-bit enum combines Plan 9 style permissions and flags with extra DOS-like flags and snapshot semantics.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/fossil/vac.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/fossil/view.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/fossil/view.c

This is an interactive Fossil/Venti tree viewer using Plan 9 draw/event APIs. It can open a local Fossil cache device/path or a `vac:<score>` root, decode headers, superblocks, labels, entries, pointer blocks, data blocks, metadata blocks, and directory entries, then present them as expandable UI nodes.

The storage side includes local partition address mapping (`PartSuper`, `PartLabel`, `PartData`), block reads via `pread`, label validation, global-score handling through Venti reads, and type/tag checking. The score formatter prints local addresses when possible and full Venti scores otherwise.

The visualization side builds `Tnode` trees lazily. Entries expand to sources, sources expand through pointer trees or data/metadata blocks, data blocks are heuristically decoded as `MetaBlock`, and metadata entries expand to decoded `DirEntry` fields.

The UI draws a simple text tree with plus/minus nubs. Left drag pans, right click toggles expansion, middle menu exits. The `-a` flag shows inactive entries.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/fossil/view.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/fossil/walk.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/fossil/walk.c

This file implements generic traversal over Fossil blocks. `initWalk` initializes a `WalkPtr` for data, directory-entry, or pointer blocks, while `nextWalk` emits the next child score/type/tag and optionally an unpacked `Entry`.

For directory blocks, iteration returns active entry-derived targets using entry type (`BtDir` or `BtData` plus depth). For pointer blocks, it returns child scores with decremented block type and inherited tag. `BtData` has no children.

It is a small reusable walker for archive/check/traversal code.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/fossil/walk.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/freq.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/freq.c

This is a character/rune frequency counter. It reads stdin or named files, counts occurrences in a `Runemax+1` array, and prints nonzero counts in selected formats.

Flags choose decimal, hex, octal, printable character, and rune-aware input. Without numeric/character format flags, it defaults to decimal, hex, octal, and character output.

It uses Plan 9 `Biobuf` APIs and reports read errors after `Bterm`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/freq.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/getmap.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/getmap.c

This utility reads or synthesizes an 8-bit display colormap and writes it to `/dev/draw/<id>/colormap`. It supports named map files, `/lib/cmap/`, screen/display/vga aliases, and generated `gamma`/`rgamma` maps.

`getcmap` loads 256 RGB rows or generates gamma-corrected grayscale entries. `putcmap` writes the full colormap table. `main` opens `/dev/draw/new`, verifies an `m8` display, resolves the selected map, and installs it.

The helper `rep` replicates an n-bit value through a `ulong`, though it is not used by `main`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/getmap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/grap/coord.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/grap/coord.c

This file manages `grap` coordinate systems. It tracks default/current coordinate names, explicit x/y ranges, log-scale flags, and resets graph margins when explicit coordinates are supplied.

`coord` applies pending x/y ranges to an `Obj`, validates positive lower bounds for log axes, records log flags, and disables automatic x numbering. Repeated implicit default coordinate definitions rename the default to `gg<N>` to avoid collision.

`resetcoord` changes the current coordinate object used by later points.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/grap/coord.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/grap/for.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/grap/for.c

This file implements `grap` loop and conditional expansion. A fixed stack of `For` records stores loop variable, limit, operator, step, and body text.

`forloop` initializes the variable and pushes the loop body back onto the input stream. `endfor` advances the variable by `+`, `-`, `*`, or `/`, then schedules the next iteration through `nextfor`.

`ifstat` chooses then/else body text, pushes the chosen source back for parsing, and frees the unused branch.

Notable limitation: `nextfor` has a `BUG` comment that termination should depend on operator and direction; currently it checks `var > SLOP * to`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/grap/for.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/grap/frame.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/grap/frame.c

This file emits the `pic` frame around a graph. It stores default frame height/width and optional side-specific line descriptions.

`frame` writes `frameht`, `framewid`, and a `Frame` box. With no custom sides it emits a normal visible box; with custom sides it emits an invisible frame and explicit lines for top, bottom, left, and right, substituting remembered side descriptors.

`frameside` maps side tokens to side strings and can apply a line descriptor to all sides when no side is specified.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/grap/frame.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/grap/grap.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/grap/grap.h

This is the central `grap` header. It defines error macros, input-source flags, constants for margins/ticks/sides/justification, `Infile`, `Src`, `Arg`, `Point`, `Attr`, `Obj`, and `YYSTYPE`.

It declares global parser/runtime state such as object lists, current coordinate names, numeric lists, tick state, temp file, and codegen flags.

It also declares the cross-module API for coordinate handling, object/attribute management, input stack and macro processing, labels, plotting, graph finalization, and tick/grid generation.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/grap/grap.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/grap/grap.y -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/grap/grap.y

This yacc grammar defines the `grap` language parsed inside `.G1` blocks. It covers graph blocks, statements, frames, ticks, grids, labels, coordinates, plots, lines, circles, draw/next paths, copy/thru includes, for loops, if statements, assignments, strings, formatted strings, points, and numeric expressions.

The grammar actions call the module functions in `grap.h` to update state and emit `pic` output through the temp file. Expressions include arithmetic, comparisons, boolean operators, log/exp/trig/sqrt/random/min/max/int, variable lookup, and assignment.

Multi-line patterns such as `copy thru` and loop/conditional bodies are handled by pushing source strings back into the lexer/input stack.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/grap/grap.y -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/grap/input.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/grap/input.c

This file implements `grap` input management: nested files, strings, macros, one-character pushback, `copy thru`, macro arguments, and error-context reporting.

`pushsrc`/`popsrc` maintain a source stack. `definition`, `delimstr`, `dodef`, and `getarg` collect macro bodies and arguments. `input` and `nextchar` multiplex source types and support `$N` macro argument expansion.

`do_thru` reads data lines, splits fields into macro arguments, stops on `.G2` or an `until` string, and pushes the thru macro for each data row.

The file also implements `copyfile`, `copydef`, `copythru`, `copyuntil`, `copy`, shell-command collection/execution helpers, math `errcheck`, and `yyerror` context printing.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/grap/input.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/grap/label.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/grap/label.c

This file emits graph labels and text sizing/positioning. It tracks point size, label width override, and accumulated label movement offsets.

`label` computes text height/width, emits a `Label` invisible box from a string list, positions it relative to the selected frame side, applies accumulated movement, and frees attributes.

`sizeit` wraps strings in troff size escapes based on per-string size operations or global `pointsize`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/grap/label.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/grap/main.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/grap/main.c

This is the `grap` program driver. It parses `-d` debug and `-l` no-library flags, installs signal handlers, initializes defaults, then processes stdin or named files.

`getdata` copies normal input through unchanged, recognizes `.G1` blocks, emits `.PS`, runs `yyparse`, and closes with `.PE`. It preserves troff `.lf` line directives and updates the current filename/line state.

It uses a temp file for generated graph body output unless debugging directs output to stdout.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/grap/main.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/grap/misc.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/grap/misc.c

This file contains general `grap` utility state and helpers. It stores numeric lists, current text justification/size operators, and provides `savenum`, `setjust`, `setsize`, `tostring`, `lookup`, variable get/set, point construction, and attribute list creation/freeing.

`range` and `halfrange` update coordinate object min/max ranges unless a coordinate bound was explicit. `setvar` special-cases `pointsize` to update global text sizing.

`slprint`, `juststr`, and `sprntf` convert string/attribute lists into `pic` text box output, justification suffixes, and formatted string values.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/grap/misc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/grap/plot.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/grap/plot.c

This file emits `pic` drawing commands for graph data. It handles line/arrow segments, circles, raw pic passthrough, string plots, numeric plots, and path continuation.

`xyname` converts a `Point` into the proper coordinate macro call and applies log validation/transformation. `numlist` turns bare numeric rows into default plotted points or connected path segments.

`drawdesc` assigns default path style/symbols to an object, and `next` either starts or extends a named line path while updating coordinate ranges.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/grap/plot.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/grap/print.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/grap/print.c

This file finalizes generated graph output. `print` computes coordinate ranges, applies margins and log transforms, emits `xy_`, `x_`, and `y_` coordinate macros, emits frames/autoticks, and copies the temp file body to output.

`graph` flushes the previous graph, opens a new temp file, parses a graph name/position, and enforces capitalized graph names by warning. `setup` resets state at each `.G1` and injects initial definitions once.

`reset` preserves definitions and variables while clearing per-graph objects and visual state. `endstat` resets per-statement transient state such as label offsets, tick state, numeric list, and tick length.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/grap/print.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/grap/ticks.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/grap/ticks.c

This file implements tick and grid generation for `grap`. It stores explicit tick values/labels, side selections, tick direction/length, automatic tick side state, and grid descriptors.

`ticks` updates automatic tick policy based on explicit lists, side selection, `in/out`, and `off`. `setauto`, `autoside`, and `autolog` compute automatic linear or log tick quantization/ranges for the default coordinate object.

`do_autoticks`, `iterator`, `ticklist`, `print_ticks`, and `maketick` generate tick marks and labels. `gridlist` reuses tick machinery to emit full grid lines, with optional descriptors and side-specific tick suppression.

Log axes validate positive tick values before transforming them.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/grap/ticks.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/graph/graph.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/graph/graph.c

This is the classic `graph` plotting command. It reads numeric x/y data from stdin, computes axis limits and scales, emits plot protocol commands through `iplot.h`, draws axes/grid/ticks, optional labels, and plotted lines or symbols.

Command-line options control labels, line mode, overlays, automatic abscissas, erase/overlay behavior, grid style, plotting character, transposition, equal scales, breaks, x/y limits including log scale, plot size/offset, and pen color cycling.

Scaling is handled by `getlim`, `setlim`, `setlinlim`, `setloglim`, and `scale`. `plot` iterates overlay series, converts data values to screen coordinates, draws connected vectors, emits symbols/labels, and rotates pen colors.

Notable limitations: this is old K&R-style C with custom `isdigit` and implicit-int functions, and fixed-size mark/label buffers.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/graph/graph.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/graph/iplot.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/graph/iplot.h

This header maps plotting primitives to textual plot protocol commands printed on stdout. It defines macros for arcs, boxes, splines, fills, color, erase, line, move, open/close, pen, point, range, text, vectors, and related operations.

It declares `putnum` for multi-point spline/polygon data and `whoami`.

The `graph` command uses these macros as its backend abstraction.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/graph/iplot.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/graph/subr.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/graph/subr.c

This file implements `putnum`, the helper declared by `iplot.h`. It prints grouped coordinate arrays in braces for plot commands that need a sequence of points, emitting pairs of doubles and line breaks after alternating entries.

It is a small serialization helper for spline/polygon/fill macros.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/graph/subr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/graph/whoami.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/graph/whoami.c

This file defines `whoami`, returning the constant string `"general"`.

It is likely used by shared plot-library conventions to identify the plot backend/environment.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/graph/whoami.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/grep/comp.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/grep/comp.c

This file implements the incremental regex automaton compiler for Plan 9 `grep`. `increment` computes the next DFA state for a state/input byte by following NFA positions, sorting them, and either reusing an existing state from a binary tree or allocating a new one.

`fol1` advances one regex node through alternation, begin/end anchors, byte classes, and optimized case tables, setting the global match flag when a terminal end state is reached.

`re2class` converts character classes into rune ranges, merges overlaps, handles negation, and lowers Unicode/UTF-8 rune ranges into byte-oriented regex fragments using `rclass`.

The design lazily builds DFA transitions during search, trading startup cost for incremental state construction.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/grep/comp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/grep/grep.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/grep/grep.h

This is the shared header for the custom Plan 9 `grep`. It defines regex node (`Re`), regex fragment (`Re2`), DFA state (`State`), node types, limits, pseudo input symbols, command flags, global buffers, and global parser/search state.

The input buffer union provides both pattern-class string space and search buffers with `pre`/`buf` halves so very long matching lines retain a suffix across reads.

It declares regex construction, lexer/parser, state allocation, follow computation, search, and debug print functions.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/grep/grep.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/grep/grep.y -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/grep/grep.y

This yacc grammar parses grep regular expressions. It supports alternation, concatenation, `*`, `+`, `?`, grouping, begin/end anchors, dot, character classes, escaped characters, literal-mode handling after leading `*`, and multiple patterns separated by newlines.

The final regex is wrapped so matching can start anywhere in a line and terminate at line end. New pattern expressions are ORed into the global top regex.

The lexer reads from a string or pattern file, folds ASCII case when `-i` is active, parses bracket classes, and reports syntax errors with pattern/file context.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/grep/grep.y -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/grep/main.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/grep/main.c

This file implements `grep` command-line handling and the search loop. It supports flags `bchiLlnsv`, `-e pattern`, and `-f patternfile`, builds the regex, initializes the DFA state, and searches stdin or files.

`search` reads chunks into the shared buffer, simulates a final newline for files without one, advances the DFA byte by byte, and emits/counts lines on newline boundaries. It handles file prefixes, line numbers, count-only, status-only, matching/nonmatching file names, inverse matching, buffering, and ASCII case folding.

The lazy transition cache calls `increment` when a state lacks a transition for the current byte.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/grep/main.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/grep/sub.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/grep/sub.c

This file provides allocation and regex construction helpers. `mal` is an arena allocator based on `sbrk`; `sal` allocates DFA states; `ral` allocates regex nodes and tracks maximum follow-set size.

It optimizes large OR/class structures into `Tcase` byte dispatch tables via `addcase`, `countor`, and `case1`.

It also implements pattern parsing entry `str2top`, input character retrieval `getrec`, regex fragment combinators (`re2cat`, `re2star`, `re2or`, `re2char`), and debug regex printing.

The allocator and code style are tightly bound to Plan 9-era assumptions.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/grep/sub.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/386.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/386.h

This generated Ghostscript architecture header defines Plan 9 386 scalar alignment, scalar sizes, unsigned maxima, cache sizes, endian behavior, pointer signedness, IEEE float behavior, arithmetic right shift behavior, full-long shift support, and signed division semantics.

It describes a 32-bit little-endian target with 4-byte pointers, 4-byte double alignment, 128 KiB L1 cache, and 4 MiB L2 cache.

It is byte-identical to `default.386.h`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/386.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/alpha.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/alpha.h

This Ghostscript architecture header defines Alpha platform constants: 32-bit pointer/long assumptions in this Plan 9 port, 8-byte double alignment, little endian, IEEE floats, arithmetic right shift, and full-long shift support.

Cache constants are 64 KiB L1 and 128 KiB L2.

It is byte-identical to `default.alpha.h`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/alpha.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/amd64.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/amd64.h

This generated Ghostscript architecture header defines amd64 platform constants. It uses 8-byte pointer size/alignment, 8-byte double alignment, little endian, IEEE floats, arithmetic right shift, and no full-long shift support.

Cache constants are 4 KiB L1 and 4 MiB L2.

It is byte-identical to `default.amd64.h`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/amd64.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/arch.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/arch.h

This is the Ghostscript architecture-selection shim for Plan 9 builds. It includes `386.h`, `mips.h`, `alpha.h`, `arm.h`, or `amd64.h` based on architecture macros such as `T386`, `Tmips`, `Talpha`, `Tarm`, and `Tamd64`.

If no known architecture macro is set, it intentionally emits invalid text telling the maintainer to update `arch.h`.

Notable observation: the `Tpower` branch includes `"mips.h"` rather than `"power.h"`, which looks suspicious given that a `power.h` file exists elsewhere in the directory.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/arch.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/arm.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/arm.h

This Ghostscript architecture header defines ARM platform constants for the Plan 9 port: 32-bit pointers, 4-byte scalar alignment including doubles, little endian, IEEE floats, arithmetic right shift, and full-long shift support.

Cache constants are both set to 1 MiB.

It is byte-identical to `default.arm.h`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/arm.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/contrib9.mak -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/contrib9.mak

This Ghostscript make fragment reintroduces contributed drivers not found in the current upstream distribution. It defines build rules for the Plan 9 bitmap device (`plan9.dev`) and several HP DeskJet-derived color printer devices (`cdj850`, `cdj670`, `cdj890`, `cdj1600`).

The rules set device objects with Ghostscript make macros and compile `gdevplan9.c` and `gdevcd8.c` with the configured Ghostscript compiler variables.

It is Plan 9 port build glue for bundled Ghostscript.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/contrib9.mak -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/default.386.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/default.386.h

This generated Ghostscript default architecture header is the default 386 configuration. It defines 32-bit little-endian scalar sizes/alignment, unsigned maxima, cache sizes, IEEE float behavior, arithmetic right shift, full-long shift support, and division semantics.

It is byte-identical to `386.h`, serving as a default/template copy for the active 386 build header.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/default.386.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/default.alpha.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/default.alpha.h

This Ghostscript default Alpha architecture header defines 32-bit pointer assumptions, 8-byte double alignment, little-endian layout, IEEE floats, arithmetic right shift, full-long shift support, and cache sizes of 64 KiB/128 KiB.

It is byte-identical to `alpha.h`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/default.alpha.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/default.amd64.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/default.amd64.h

This Ghostscript default amd64 architecture header defines 8-byte pointer size/alignment, little-endian layout, IEEE float behavior, arithmetic right shift, no full-long shift support, and cache sizes of 4 KiB/4 MiB.

It is byte-identical to `amd64.h`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/default.amd64.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/default.arm.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/default.arm.h

This Ghostscript default ARM architecture header defines 32-bit pointer/scalar layout, 4-byte double alignment, little-endian layout, IEEE floats, arithmetic right shift, full-long shift support, and 1 MiB cache constants.

It is byte-identical to `arm.h`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/default.arm.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/default.mips.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/default.mips.h

This Ghostscript default MIPS architecture header defines 32-bit scalar/pointer sizes, 4-byte alignment, big-endian layout, IEEE floats, arithmetic right shift, no full-long shift support, and cache constants of 4 KiB/512 KiB.

It is the source of the copied Power defaults noted in `default.power.h`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/default.mips.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/default.power.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/default.power.h

This Ghostscript default Power architecture header defines 32-bit scalar/pointer sizes, 4-byte alignment, big-endian layout, IEEE floats, arithmetic right shift, no full-long shift support, and 4 KiB/512 KiB cache constants.

The file explicitly states it was copied from `default.mips.h` and has not been tested, so it should be treated as provisional platform configuration.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/default.power.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/icclib/icc.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/icclib/icc.h

This is the public header for Graeme W. Gill’s icclib 2.01, bundled under Ghostscript. It defines the ICC profile object model, platform integer aliases, shared-library export handling, file and allocator abstraction classes, and includes `icc9809.h` for ICC signature/type definitions.

The header defines in-memory representations and method tables for ICC tag payloads: integer/fixed arrays, XYZ arrays, curves with reverse lookup tables, data/text/date tags, LUTs, measurements, named colors, text descriptions, profile sequences, screening, UCR/BG, viewing conditions, CRD info, video card gamma, and the profile header.

It defines lookup-object APIs for monochrome, matrix, and multidimensional LUT transforms, including forward/backward lookup functions, normalization, absolute/relative color transforms, ranges, white/black points, and lookup-space metadata.

The main `icc` object exposes methods for reading/writing/dumping profiles, finding/adding/renaming/linking/deleting tags, reading all tags, and constructing lookup objects. Utility declarations include tag/string conversion, enum formatting, XYZ/Lab conversion, standard illuminants, pseudo-Hilbert grid traversal, chromatic adaptation, and Delta E calculations.

This is embedded third-party color-management infrastructure rather than Plan 9 filesystem code.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/icclib/icc.h -->