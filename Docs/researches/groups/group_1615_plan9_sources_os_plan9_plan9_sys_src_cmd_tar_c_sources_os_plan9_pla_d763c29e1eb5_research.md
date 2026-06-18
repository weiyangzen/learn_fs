# Group Research: group_1615_plan9_sources_os_plan9_plan9_sys_src_cmd_tar_c_sources_os_plan9_pla_d763c29e1eb5

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/tar.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/tar.c

Plan 9 `tar` implementation supporting create, append/update, table-of-contents, and extract modes. It targets POSIX `ustar` for extraction and, by default, creation, while retaining compatibility with older tar headers and GNU/FreeBSD binary large-size fields.

Key structures and constants:
- `Hdr` is a 512-byte tar header union with POSIX `ustar` extension fields.
- `Compress` maps suffixes to compression/decompression filters: gzip, compress, bzip2.
- `Pushstate` tracks forked compression filter processes.
- Archive data is buffered in `nblock` groups of 512-byte `Tblock`s, defaulting to 20 blocks.

Main behavior:
- `main` parses tar keyletters with a custom `TARGBEGIN`, then dispatches to `replace` for `c/r` or `extract` for `x/t`.
- `replace` creates or updates an archive, optionally pushes a compressor, recurses directories through `addtoar`, and writes two zero end blocks.
- `extract` opens an archive, auto-detects decompression by suffix or `-z`, reads headers with checksum validation, matches path prefixes, and calls `extract1`.
- `readhdr`, `hdrsize`, `arsize`, and `chksum` handle header validation, size decoding, and stream resync with `-s`.

Notable details:
- Large file sizes are emitted in GNU-style base-256 binary form when `dir->length >= 1<<32`.
- Extraction refuses to create hard links, symlinks, and FIFOs, printing diagnostics instead.
- Relative extraction is default; `-R` preserves absolute/device-like names.
- `-i` attempts to ignore read errors by zero-filling unread blocks and seeking past errors when possible.
- `skip` and `refill` optimize skipping large members on seekable archives.

Dependencies:
- Plan 9 libc APIs: `Dir`, `dirreadall`, `dirfstat`, `dirfwstat`, `create`, `cleanname`, `seek`, `wait`, `fork`, `execl`.
- `<fcall.h>` for `%M` directory mode formatting.
- `<String.h>` Plan 9 string builder routines.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/tar.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/tarsplit/tar.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/tarsplit/tar.h

Shared tar-format header for `tarsplit`, `tarcat`, and `tarsub.c`.

Defines:
- `Tblock = 512`, `Namesz = 100`.
- Tar link flag values including plain file, hard link, symbolic link, directory, FIFO, and contiguous file.
- `Header` for pre-ustar tar headers through `linkname`.
- `Hblock`, a 512-byte union overlaying `Header`.

Utilities/macros:
- `islink`, `isreallink`, `issymlink`.
- `HOWMANY`, `ROUNDUP`, `TAPEBLKS` for tar block sizing.

Exports from `tarsub.c`:
- Global member names `thisnm`, `lastnm`.
- Archive helpers: `checksum`, `getdir`, `passtar`, `readtar`, `writetar`, `putempty`, `closeout`, `newarch`, `otoi`.

This header intentionally models only the classic tar header subset needed for stream splitting and concatenation.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/tarsplit/tar.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/tarsplit/tarcat.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/tarsplit/tarcat.c

`tarcat` concatenates multiple tar archives into one valid tar archive on stdout.

Behavior:
- Reads each input archive from stdin or named files.
- For each member, `catenate` copies the header with `writetar` and copies payload blocks with `passtar`.
- It deliberately omits the zero end blocks from input archives and emits a fresh end marker through `closeout`.

CLI:
- Supports `-d` for debug logging.
- Usage: `tarcat [-d] [file]...`.

Dependencies:
- `tar.h` and `tarsub.c` for header parsing, checksum validation, block copying, and final zero blocks.

Notable issue:
- The debug message argument order appears reversed: `fprint(2, "%s: reading %s\n", inname, argv0);` prints input name as the command prefix.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/tarsplit/tarcat.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/tarsplit/tarsplit.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/tarsplit/tarsplit.c

`tarsplit` splits a tar archive into independently readable tar archives under a configured maximum size.

Behavior:
- Default output prefix is `ts.` and default target size is `512*1024*1024`.
- `opennext` creates sequential output files named `<prefix><00000...>`, resets output offset with `newarch`, and reports the first/current member.
- `split` reads tar members with `getdir`, computes `header + rounded payload + end marker` size, closes the current output if the next member will not fit, and writes the member intact.
- A single member larger than the target size plus end overhead is fatal.

CLI:
- `-p pfx` chooses output prefix.
- `-s size` chooses max output size.
- Reads stdin or named input archives.

Dependencies:
- `tar.h` and `tarsub.c`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/tarsplit/tarsplit.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/tarsplit/tarsub.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/tarsplit/tarsub.c

Shared tar stream primitives for `tarcat` and `tarsplit`.

Key functions:
- `checksum` computes classic tar header checksum with the checksum field treated as spaces.
- `readtar` reads exact tar-block multiples and zero-fills a short final archive record.
- `getdir` reads one header, returns false on a zero header, validates checksum, stores member length, and updates `thisnm`/`lastnm`.
- `passtar` copies rounded file payload blocks unless the member is a link.
- `writetar` writes to output and tracks `outoff`.
- `closeout` writes two zero blocks and closes the archive.

Notable behavior:
- Size parsing uses octal-only `otoi`.
- Only hard/symbolic links are treated as no-payload entries; directories with nonzero sizes would be copied according to header length.
- `Blocksxfr = 32`, so payload copying uses 16 KiB chunks.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/tarsplit/tarsub.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/tbl/t.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/tbl/t.h

Central header for the Plan 9 `tbl` troff table preprocessor.

Contents:
- Global limits such as `MAXLIN`, `MAXHEAD`, `MAXCOL`, `MAXCHS`, and `CLLEN`.
- Shared global state for table dimensions, parsed styles, fonts, sizes, flags, spans, line drawing, input buffers, and output `Biobuf`.
- Style/flag constants such as `ZEROW`, `HALFUP`, `CTOP`, `CDOWN`, and line direction constants.
- Troff register constants (`S1`, `S2`, `TMP`, `LSIZE`, etc.).
- Function prototypes grouped by source module from `t1.c` through `tv.c`.

Architectural role:
- `tbl` is implemented as many small C files sharing global arrays allocated per table. This header is the single cross-module contract.
- `MAXCOL` is tied to register allocation in `tr.c`; increasing it requires extending `nregs[]`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/tbl/t.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/tbl/t0.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/tbl/t0.c

Global storage definitions for `tbl`.

Defines:
- Table option flags: `expand`, `center`, `box`, `doublebox`, `allbox`, delimiter state, tab character, and printer mode.
- Pointers for dynamically allocated per-table format arrays: `style`, `font`, `csize`, `vsize`, `lefline`, `flags`, `sep`, `used`, spans, and width tracking.
- Static storage for `table`, `stynum`, `fullbot`, `instead`, `linestop`.
- Input/output state including `tabin`, `tabout`, `ifile`, `iline`, and text diversion names.

Role:
- Provides the actual backing objects for the `extern` declarations in `t.h`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/tbl/t0.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/tbl/t1.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/tbl/t1.c

Top-level control and input file switching for `tbl`.

Key functions:
- `main` exits with `"error"` if `tbl` returns nonzero.
- `tbl` initializes output `Biobuf`, reads input lines, echoes them, and invokes `tableput` when `.TS` starts a table.
- `setinp` initializes input from argv or stdin.
- `swapin` skips/handles troff macro options (`-ms`, `-mm`, `-TX`, `-`), opens the next input file, emits `.ds f.` and `.lf` directives, and tracks line numbers.

Notable behavior:
- File closing is explicitly delegated to older preprocessor assumptions, though `Bterm` is called when switching from an existing `tabin`.
- `-TX` enables `pr1403`, affecting line drawing for printer output.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/tbl/t1.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/tbl/t2.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/tbl/t2.c

One-table sequencing driver.

`tableput` runs the full pipeline:
- Save current line/fill/diversion state.
- Parse global table commands with `getcomm`.
- Parse format spec with `getspec`.
- Read table data with `gettbl`.
- Compute drawing stops, usage, delimiter characters, tab stops.
- Emit output with `runout`.
- Release temporary storage and restore troff state.

This file contains no parsing logic itself; it encodes the phase ordering for the preprocessor.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/tbl/t2.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/tbl/t3.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/tbl/t3.c

Parses global table options following `.TS`.

Supported options:
- `expand`, `center`, `box`, `allbox`, `doublebox`, aliases `frame` and `doubleframe`.
- `tab(x)`, `linesize(n)`, `delim(xy)`.
- Uppercase variants for most option names.

Key functions:
- `getcomm` resets option globals, reads the command line, recognizes options before `;`, applies argument values, and pushes remaining input back.
- `backrest` ungets a string plus newline so later parsers consume it.

Notable behavior:
- If the first line lacks `;`, it is treated as part of the format specification.
- Misspelled or unknown global options are fatal via `error`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/tbl/t3.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/tbl/t4.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/tbl/t4.c

Reads and allocates the table format specification.

Key functions:
- `getspec` estimates column count with `findcol`, allocates per-column arrays with `garray`, initializes defaults, calls `readspec`, and removes old right-column registers.
- `readspec` parses format characters, spans, vertical lines, font/size/width modifiers, equal-width flags, zero-width flags, half-up flags, and separator widths until final `.`.
- `findcol` scans the spec line, respecting parentheses, to count style columns.
- `garray` allocates all per-table format and usage arrays.
- `getcore` wraps `calloc`; `freearr` releases per-table arrays.

Notable behavior:
- Spans cannot start in the first column.
- `a` and `n` columns are adjusted when followed by `s` spans.
- `T&` continuation cannot widen the table by more than two columns.
- `sep` is incremented after allocation so `sep[-1]` is valid, then decremented before free.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/tbl/t4.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/tbl/t5.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/tbl/t5.c

Reads table data rows into internal structures.

Key functions:
- `gettbl` reads rows until `.TE`, `.TC`, `.T&`, or `MAXLIN`; allocates row vectors; recognizes full-width horizontal lines `_` and `=`; handles embedded troff control lines; parses cells by the active tab delimiter.
- `nodata` identifies format lines containing no data columns.
- `oneh` detects rows where all columns are the same horizontal-line style.
- `permute` moves vertically spanned content to the bottom row of a span and leaves `\^` placeholders.
- `vspand` and `vspen` recognize vertical span markers.

Notable behavior:
- Text blocks beginning with `T{` are delegated to `gettext`.
- Numerical (`n`) columns are split by `maknew`; alphabetic (`a`) columns place data in `rcol`.
- Character storage is pooled with `chspace` and reset as rows exceed buffer space.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/tbl/t5.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/tbl/t6.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/tbl/t6.c

Computes troff number registers for table column widths and tab stops.

Key functions:
- `maktab` measures cell widths, handles numeric/alphabetic split columns, text diversions, explicit column widths, spans, equal-width columns, expansion to line length, and final table width `TW`.
- `wide` emits troff width expressions for literal strings or diverted text registers.
- `filler` identifies `\R` filler entries.

Important interactions:
- Uses `reg(col, place)` from `tr.c` to assign left/mid/right register names.
- Uses `real`, `point`, `vspen`, `barent`, `fspan`, `lspan`, and cell flags.
- Emits a warning when computed table width exceeds line length.

Notable behavior:
- Numeric columns maintain separate left and right width components around the decimal point or split marker.
- Expansion mode distributes extra space through separators rather than fixed 1n spacing.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/tbl/t6.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/tbl/t7.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/tbl/t7.c

Controls emission of the formatted table.

Key functions:
- `runout` prepares optional boxing/centering, sets field delimiters, defines the tail macro, emits every row with `putline`, handles overflow rows through `yetmore`, and restores centering.
- `runtabs` emits `.ta` tab stops for the current row according to active formats and used columns.
- `ifline` recognizes single-cell line markers.
- `need` emits a `.ne` request sized from text and horizontal-line rows.
- `deftail` defines the `T#` macro used to draw bottom/right borders and vertical continuation lines.

Notable behavior:
- Vertical line rendering is deferred partly into the `T#` macro so output survives page/diversion context.
- `pr1403` changes vertical spacing and line drawing behavior.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/tbl/t7.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/tbl/t8.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/tbl/t8.c

Emits one formatted table row and associated vertical/funny text handling.

Key functions:
- `putline` handles row-level boxes, horizontal rows, vertical spans, line stops, tab stops, alignment, numeric split fields, half-line-up flags, font/size changes, and cell output.
- `puttext` emits a cell string with optional font and size changes.
- `funnies` emits diverted text blocks after normal row output, positioning them in their cells.
- `putfont` and `putsize` emit troff font/size escape sequences.

Notable behavior:
- Uses chosen delimiter characters `F1`/`F2` to let troff field mechanism align left/right/center forms.
- Tracks vertical span state through `#^`, `^-`, per-column `^x` registers, and `topat`.
- Splits long vertical-line output after several escapes to avoid backend limits.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/tbl/t8.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/tbl/t9.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/tbl/t9.c

Handles tables exceeding the fixed `MAXLIN` row storage.

Key functions:
- `yetmore` selects a reusable data row, keeps the last real style row, processes `leftover`, and continues reading/formatting rows one at a time.
- `domore` parses and emits one additional data line using the existing format, preserving horizontal-line and troff-control-line handling.

Notable behavior:
- Reuses `table[0]` storage for streaming extra rows.
- Resets `exstore` so numerical split storage can be reused.
- Contains typoed fatal messages: `"Wierd..."`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/tbl/t9.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/tbl/tb.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/tbl/tb.c

Usage analysis and pooled allocation helpers for `tbl`.

Key functions:
- `checkuse` marks which columns have visible left, right, or split content.
- `real` determines whether a cell pointer represents actual printable content or a nonempty diversion.
- `chspace` allocates/reuses large character buffers.
- `alocv` allocates vector storage from pooled `MAXCHS` blocks and zeroes it.
- `release` resets pool cursors and text split storage.

Notable behavior:
- Comments preserve historical reluctance to `free` vector pools, but the implementation reuses pools by resetting counters.
- `MAXVEC` and `MAXPC` cap temporary character and vector pools.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/tbl/tb.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/tbl/tc.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/tbl/tc.c

Chooses delimiter characters for troff field alignment.

Key functions:
- `choochar` scans all real cell text for used ASCII bytes, then selects two unused characters from a prioritized `COMMON` string.
- `point` distinguishes real string pointers from small integer diversion/register identifiers stored as pointer values.

Notable behavior:
- Fails if no two suitable delimiter characters are available.
- Only scans bytes below 128; non-ASCII bytes do not affect delimiter choice.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/tbl/tc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/tbl/te.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/tbl/te.c

Error handling and character/line input support.

Key functions:
- `error` prints `file:line` diagnostics, says `tbl quits`, and exits.
- `gets1` reads a full line with `Brdline`, swaps input files at EOF, strips newline, tracks `iline`, and folds escaped newlines while inside a table.
- `un1getc` pushes one character into a fixed backup buffer and decrements line number for newlines.
- `get1char` returns backed-up characters before reading from `tabin`, swapping files on EOF.

Notable behavior:
- Backup buffer is fixed at 500 characters.
- A NUL read from `Bgetc` is treated as EOF in this code.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/tbl/te.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/tbl/tf.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/tbl/tf.c

Saves and restores troff fill, diversion, line-number, and field-control state around table output.

Key functions:
- `savefill` defines macro `SF` to restore point size, vertical spacing, indent, fill, and adjustment, then switches to no-fill.
- `rstofill` invokes the saved macro.
- `endoff` clears line-stop registers, removes text diversions, and emits trailing `last` input.
- `ifdivert` defines string `#d` differently depending on diversion context.
- `saveline` and `restline` preserve troff line counters across table preprocessing.
- `cleanfc` clears field control.

This module is mostly troff state hygiene required before and after generated table requests.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/tbl/tf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/tbl/tg.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/tbl/tg.c

Processes multiline `T{ ... T}` text blocks inside table cells.

Key functions:
- `gettext` creates a troff diversion for the text block, applies font/size/vertical spacing and line length, reads until `T}`, records diversion height/width registers, and returns a small identifier stored as a pointer-like value.
- `untext` restores fill mode and line length after text diversions.

Notable behavior:
- Uses `texstr` characters as diversion names and errors when exhausted.
- Handles `T}` followed by the table delimiter by copying remainder back into the current cell buffer.
- Text block line length depends on explicit `w(...)`, column span, and current right register.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/tbl/tg.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/tbl/ti.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/tbl/ti.c

Classifies intersections between horizontal and vertical table rules.

Key functions:
- `interv` determines whether a vertical line crosses, starts, or ends at a horizontal rule position.
- `interh` determines whether a horizontal line crosses or meets vertical rules at a column boundary.
- `up1` finds the previous non-`instead` row.

Used by:
- `drawline` in `tu.c` for horizontal rule endpoint adjustments.
- `drawvert` in `tv.c` for vertical rule endpoint adjustments.

Notable behavior:
- Double boxes (`dboxflg`) force boundary intersections.
- Full horizontal rows and adjacent all-horizontal rows influence classification.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/tbl/ti.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/tbl/tm.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/tbl/tm.c

Splits numeric table entries into left and right parts for decimal alignment.

Key functions:
- `maknew` finds a split point: explicit `\&`, decimal point outside equation delimiters, or last digit boundary. It stores the right part in `exstore`, terminates the left part in place, and returns the right part pointer.
- `ineqn` reports whether a position is inside text delimited by `delim1`/`delim2`.

Notable behavior:
- If a field has no numeric split point, `maknew` returns `0`.
- Split storage is allocated from `chspace` and reused through `exstore`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/tbl/tm.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/tbl/tr.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/tbl/tr.c

Allocates troff number register names for table columns.

Contents:
- `nregs[]` is a fixed list of two-character register names.
- `reg(col, place)` indexes into `nregs` based on `qcol * place + col`.

Notable behavior:
- Enforces that `nregs` has at least `3*qcol` entries.
- Supports left, center/mid, and right register sets via `CLEFT`, `CMID`, and `CRIGHT`.
- `MAXCOL` in `t.h` must stay compatible with this array.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/tbl/tr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/tbl/ts.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/tbl/ts.c

Small string and numeric utility functions for `tbl`.

Functions:
- `match` for exact string equality.
- `prefix` for prefix testing.
- `letter`, `digit` character predicates.
- `numb` decimal integer conversion.
- `max`.
- `tcopy` string copy.

These are local replacements for simple libc-style operations, matching the historical source style.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/tbl/ts.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/tbl/tt.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/tbl/tt.c

Helpers for span and horizontal-line classification.

Key functions:
- `ctype` returns active format style for a row/column, ignoring full horizontal rows and troff-control rows.
- `fspan`, `lspan`, and `ctspan` compute span relationships.
- `tohcol` emits horizontal movement to a column boundary.
- `allh` determines whether an entire row is horizontal rules.
- `thish` returns horizontal rule type for a cell: none, single, double, span continuation, or content-derived rule.

Notable behavior:
- `thish` treats empty cells and vertical spans as neutral/continuation.
- `barent` from `tv.c` is used to treat literal `_`/`=` entries as rule entries.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/tbl/tt.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/tbl/tu.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/tbl/tu.c

Draws horizontal rules and identifies vertical rule extents.

Key functions:
- `makeline` draws a horizontal rule segment for one cell or span.
- `fullwide` draws table-wide horizontal rules while skipping vertical spans.
- `drawline` emits troff line drawing escapes, with endpoint adjustments based on `interv`.
- `getstop` assigns line-stop registers for vertical line starts.
- `left` finds the starting row and width of a vertical line ending at a position.
- `lefdata` returns vertical line kind from format state and box/allbox flags.
- `next` and `prev` skip non-data rows.

Notable behavior:
- Double rules draw two offset lines unless `pr1403` mode collapses them.
- Short line entries are detected by leading backslash.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/tbl/tu.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/tbl/tv.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/tbl/tv.c

Draws vertical table rules and identifies midline intersections.

Key functions:
- `drawvert` emits troff `\L` vertical line escapes from start to end rows, with endpoint adjustments for horizontal line intersections, double lines, printer mode, and diversions.
- `midbar` checks current or previous column for a horizontal rule crossing a vertical boundary.
- `midbcol` resolves spans and returns cell horizontal rule type.
- `barent` recognizes single-character `_`/`=` rule entries, accounting for optional leading backslash.

Notable behavior:
- Vertical drawing depends on `linestop` registers created by `getstop`.
- `barent(nil)` returns `1`, making missing data a neutral line continuation case.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/tbl/tv.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/tcs/8859.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/tcs/8859.h

Static mapping tables from ISO-8859 byte values to Unicode/Plan 9 rune values.

Tables:
- `tab8859_1` through `tab8859_10`.
- `tab8859_15`.

Content:
- Each table is `long[256]`.
- ASCII/control positions are identity mappings.
- Undefined positions are `-1`.
- Non-ASCII ranges map to Latin, Central European, Greek, Cyrillic, Arabic, Hebrew, Turkish, Nordic, and Latin-9 code points depending on variant.

Role:
- Consumed by `tcs` single-byte conversion machinery elsewhere in the directory.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/tcs/8859.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/tcs/big5.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/tcs/big5.c

Large static Big5-to-rune mapping table.

Contents:
- Defines `long tabbig5[BIG5MAX]`.
- Indexed by Big5 ordinal computed by `conv_big5.c`.
- Entries are Unicode/Plan 9 rune values or `-1` for unmapped holes.
- Includes punctuation, symbols, fullwidth Latin, Greek, kana, Cyrillic, CJK ideographs, compatibility code points, and large undefined regions.

Dependencies:
- Includes `big5.h`, which defines `BIG5MAX = 13973`.

Role:
- Primary forward mapping for Big5 input.
- Also used to build reverse rune-to-Big5 map in `big5_out`.
- Used by `tcs/font/bmap.c` to locate Big5 glyph indices for requested runes.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/tcs/big5.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/tcs/big5.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/tcs/big5.h

Header for Big5 conversion tables.

Defines:
- `BIG5MAX 13973`: number of Big5 ordinal slots.
- `BIG5FONT 157`: number of trailing-byte positions per lead-byte row.

Declares:
- `extern long tabbig5[BIG5MAX]`.

Used by:
- `big5.c`, `conv_big5.c`, and `tcs/font/bmap.c`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/tcs/big5.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/tcs/conv.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/tcs/conv.h

Shared declarations and macros for `tcs` converter modules.

Contents:
- Prototypes for Japanese, Big5, GB, GBK, KSC, HTML, and tune input/output converters.
- `emit(x)` macro appends a rune through a `Rune **r` cursor.
- `NRUNE` is `Runemax+1` for reverse lookup table sizing.
- Declares global `long tab[]` reverse mapping table indexed by rune.

Role:
- Lets format-specific converter modules share the same function signatures expected by the main `tcs` driver.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/tcs/conv.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/tcs/conv_big5.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/tcs/conv_big5.c

Big5 input/output converter for `tcs`.

Key functions:
- `big5proc` is a two-state decoder. Lead bytes are `>= 0xA1`; trail bytes map through ranges `0x40..0x7e` and `0xA1..0xFE` into `BIG5FONT` slots.
- `big5_in` reads bytes, feeds `big5proc`, flushes rune buffers to downstream converter with `OUT`.
- `big5_out` lazily builds `tab[rune] = big5_ordinal`, emits ASCII directly, and emits two-byte Big5 for mapped non-ASCII runes.

Error behavior:
- Bad font/glyph or unknown ordinal increments `nerrors`, optionally prints diagnostics under `squawk`, emits `BADMAP`/`BYTEBADMAP` unless `clean` is set.

Dependencies:
- `hdr.h`, `conv.h`, `big5.h`, global `tabbig5`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/tcs/conv_big5.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/tcs/conv_gb.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/tcs/conv_gb.c

GB2312 input/output converter for `tcs`.

Key functions:
- `gbproc` decodes two-byte GB sequences where both bytes are `>= 0xA1`; ordinal is `(lead-0xA0)*100 + (trail-0xA0)`.
- `gb_in` streams input bytes through `gbproc`.
- `gb_out` builds reverse mapping from `tabgb`, emits ASCII directly, and emits two-byte GB for mapped runes.

Error behavior:
- Invalid second byte or unmapped table entry records errors and optionally emits replacement mappings depending on `clean`.

Dependencies:
- `hdr.h`, `conv.h`, `gb.h`, global `tabgb`/`GBMAX`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/tcs/conv_gb.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/tcs/conv_gbk.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/tcs/conv_gbk.c

GBK input/output converter for `tcs`.

Key functions:
- `gbkproc` treats bytes `>= 0x80` as lead bytes, combines lead/trail into a 16-bit code, and looks up `tabgbk[code - GBKMIN]` when within range.
- `gbk_in` streams input through the state machine.
- `gbk_out` builds a reverse table over `GBKMIN..GBKMAX`, emits ASCII below `0x80`, and emits two-byte GBK for mapped runes.

Notable behavior:
- Reverse table initialization writes `tab[tabgbk[i-GBKMIN]] = i` without checking for `-1`, assuming the table/range is suitable.
- Unmapped output emits `BYTEBADMAP` unless `clean` suppresses it.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/tcs/conv_gbk.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/tcs/conv_jis.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/tcs/conv_jis.c

Japanese encoding converters for `tcs`: mixed JIS detection, ISO-2022-JP, Shift-JIS, and EUC-JP.

Input state machines:
- `alljis` handles escape shifts plus possible Shift-JIS byte pairs.
- `ms` handles Shift-JIS, using `CANS2J` and `S2J` to convert to kuten indices.
- `ujis` handles EUC-JP two-byte codes and rejects codeset 2/3.
- `jis` handles ISO-2022-JP style escape shifts and guards against mixed Latin-1/JIS byte pairs.
- `do_in` is the shared streaming wrapper.

Output functions:
- `jisjis_out` emits ISO-2022-JP escape transitions.
- `msjis_out` emits Shift-JIS using `J2S`.
- `ujis_out` emits EUC-JP.
- `tab_init` builds reverse rune-to-kuten mapping from `tabkuten208`.

Notable behavior:
- Supports Japan646 mappings for backslash to yen and tilde to macron in relevant states.
- Negative table entries represent ambiguous mappings; they are emitted as positive code points with optional diagnostics.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/tcs/conv_jis.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/tcs/conv_ksc.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/tcs/conv_ksc.c

Korean EUC/KSC converter for `tcs`.

Key functions:
- `ukscproc` decodes ASCII and codeset-1 two-byte KSC 5601 characters. Backslash maps to U+20A9 when `korean646` is enabled.
- `uksc_in` streams bytes through `ukscproc`.
- `uksc_out` builds reverse mapping from `tabksc5601`, emits ASCII directly, and emits EUC-style two-byte codes with high bits set.

Notable behavior:
- Codeset 2/3 handling is present only as commented-out state names and transitions.
- EOF in the middle of a two-byte character produces a diagnostic and substitutes a fallback second byte.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/tcs/conv_ksc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/tcs/cyrillic.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/tcs/cyrillic.h

Static Cyrillic-related byte-to-rune mapping tables.

Tables:
- `tabucode`: main Cyrillic block in upper half.
- `tabkoi8`: KOI8 Cyrillic layout.
- `tab866`: DOS code page 866 subset with Cyrillic.
- `tabav` and `tabov`: alternative Cyrillic/typographic mappings including arrows, accents, division, plus-minus, numero sign, and currency sign.

Conventions:
- `long[256]` arrays.
- ASCII/control positions are identity mappings.
- Undefined entries are `-1`.

Role:
- Used by `tcs` single-byte conversion definitions outside this subset.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/tcs/cyrillic.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/tcs/font/bbits.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/tcs/font/bbits.c

Reads Big5 bitmap glyphs from a raw font bitfile.

Key function:
- `breadbits(file, n, chars, size, bits, doneptr)` opens a Big5 bits file, seeks to each requested Big5 ordinal, copies glyph rows into an interleaved bitmap buffer, compacts found glyphs, allocates a Plan 9 `Bitmap`, and writes bitmap data into it.

Important details:
- `Charsperfont = 157`, matching `BIG5FONT`.
- Contains Big5 void-range constants and a hard-coded 16x16 `missing` glyph pattern to detect absent glyphs.
- Handles Big5 file layout holes with offset adjustments before seek.
- `done[i]` marks glyphs included in the compacted bitmap.

Dependencies:
- Plan 9 graphics `Bitmap`, `balloc`, `wrbitmap`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/tcs/font/bbits.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/tcs/font/bmap.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/tcs/font/bmap.c

Maps requested rune range to Big5 glyph ordinals.

Key function:
- `bmap(from, to, chars)` initializes output slots to zero, scans `tabbig5`, and records the Big5 ordinal for each rune in range.

Notable behavior:
- Reports how many requested characters were found and one missing rune if any are absent.
- Does not abort on missing mappings; the `exits("map problem")` call is commented out.
- A mapped ordinal of zero is indistinguishable from the initialized “missing” marker for rune equal to `tabbig5[0]`, but typical requested ranges likely avoid that ambiguity.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/tcs/font/bmap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/tcs/font/font.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/tcs/font/font.c

Builds a Plan 9 `Subfont` descriptor from a generated glyph bitmap.

Key function:
- `bf(n, size, b, done)` allocates `Fontchar[n+1]`, creates per-character metrics, skips missing glyphs by assigning width `0`, and calls `subfalloc`.

Metrics:
- Each present glyph is `size` pixels wide and high.
- Ascent is `size*7/8`.
- `x` positions advance only for found glyphs.

Dependencies:
- Plan 9 graphics types `Bitmap`, `Subfont`, `Fontchar`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/tcs/font/font.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/tcs/font/gbits.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/tcs/font/gbits.c

Reads GB glyphs from a BDF font file.

Key function:
- `greadbits(file, n, chars, size, bits, doneptr)` scans BDF `STARTCHAR` records, reads `ENCODING` and `BITMAP`, converts hex rows to bytes, copies matching glyphs into an interleaved bitmap, compacts found glyphs, and returns a Plan 9 `Bitmap`.

Helper:
- `field(bf, name)` advances to a required BDF field or exits on malformed input.

Encoding:
- BDF `ENCODING` is converted to GB ordinal using `(high - 0xA0)*100 + (low - 0xA0)`.

Notable behavior:
- Fixed `buf[1024]` is assumed big enough for one glyph bitmap.
- Uses lowercase hex digit table only.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/tcs/font/gbits.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/tcs/font/gmap.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/tcs/font/gmap.c

Maps requested rune range to GB glyph ordinals.

Key function:
- `gmap(from, to, chars)` scans `tabgb` and stores each matching table index in `chars[rune-from]`.

Notable behavior:
- Missing requested runes are reported but not fatal.
- Mirrors `bmap` and `kmap` structure.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/tcs/font/gmap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/tcs/font/hdr.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/tcs/font/hdr.h

Shared declarations for the `tcs/font` tools.

Defines:
- `readbitsfn`: reader function type returning `Bitmap *`.
- `mapfn`: mapping function type from rune range to glyph ordinals.

Declares:
- Reader/mapping pairs for Kuten/JIS, Big5, GB BDF, and quwei GB sources.
- `bf` for constructing a `Subfont`.

Role:
- Shared by `main.c`, bit readers, and map modules.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/tcs/font/hdr.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/tcs/font/kbits.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/tcs/font/kbits.c

Reads JIS/Kuten bitmap glyphs from a textual bits file.

Key function:
- `kreadbits(file, n, chars, size, bits, doneptr)` opens the bits file, skips two header lines, parses each glyph record, converts hex bitmap rows to bytes, stores matching glyphs, compacts present glyphs, and returns a Plan 9 `Bitmap`.

Notable behavior:
- Uses `strtol(p+17, ...)` for the glyph code and `p += 25` for bitmap data, so it depends on a fixed input record layout.
- Missing glyph diagnostics are present but commented out.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/tcs/font/kbits.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/tcs/font/kmap.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/tcs/font/kmap.c

Maps requested rune range to Kuten/JIS glyph ordinals.

Key function:
- `kmap(from, to, chars)` scans `tabkuten208` and stores the Kuten table index for each rune in range.

Notable behavior:
- Reports but does not abort on missing mappings.
- Does not treat negative ambiguous mapping entries specially; it only matches entries whose stored value is within the requested positive rune range.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/tcs/font/kmap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/tcs/font/main.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/tcs/font/main.c

Main program for generating Plan 9 bitmap/subfont data for a range of Han characters.

CLI behavior:
- Usage: `fontgen [-s] from to`, with additional options `-f file`, `-r`, `-5`, `-g`, `-q`.
- `-s` selects 16px instead of default 24px.
- `-5` selects Big5, `-g` GB BDF, `-q` GB quwei, otherwise JIS.
- `-r` treats requested codes as raw glyph indices rather than mapping from runes.

Flow:
- Chooses source mapping and bitmap reader.
- Allocates `bits`, `chars`, and `found`.
- Maps runes to glyph indices unless raw mode.
- Reads glyph bitmaps, copies bitmap, builds subfont with `bf`, then writes bitmap and subfont to stdout.

Dependencies:
- Plan 9 graphics initialization via `binit`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/tcs/font/main.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/tcs/font/merge.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/tcs/font/merge.c

Merges multiple Plan 9 bitmap/subfont files by choosing the first available glyph for each character index.

Key functions:
- `main` reads all input fonts, validates compatible height/ascent, allocates merged bitmap and `Fontchar` array, calls `choose`, writes bitmap/subfont output.
- `snarf` reads one bitmap and subfont file into memory.
- `choose` iterates character slots, finds the first source font with nonempty glyph width, copies metrics and bitmap data into the merged output.

Notable issues:
- Compatibility checks compare against `ft[1]` rather than `ft[0]` in conditions, likely a bug for `nf > 1`.
- Contains a debugging display line: `bitblt(&screen,...); bflush(); sleep(5000);` before subfont allocation.
- Bitmap copy in `choose` uses `Pt(0, lastx)` and `Rect(0, info[n].x, ht, info[n+1].x)`, reflecting old libg coordinate conventions but worth reviewing if ported.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/tcs/font/merge.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/tcs/font/qbits.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/tcs/font/qbits.c

Reads GB quwei-encoded bitmap glyphs from a textual bits file.

Key function:
- `qreadbits(file, n, chars, size, bits, doneptr)` scans each line, parses the first four decimal digits as quwei code, converts following hex bitmap rows to bytes, stores matching glyphs, compacts found glyphs, and returns a Plan 9 `Bitmap`.

Notable behavior:
- Similar to `kreadbits`, but code parsing uses four leading decimal digits and bitmap data begins at `p += 5`.
- Missing glyph diagnostics are commented out.
- The file argument is still opened even though `main.c` lists no default 16-bit file for `Gb_qw`; callers must pass `-f`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/tcs/font/qbits.c -->