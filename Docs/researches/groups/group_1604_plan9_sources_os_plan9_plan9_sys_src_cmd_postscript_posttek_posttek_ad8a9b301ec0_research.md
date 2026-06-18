# Group Research: group_1604_plan9_sources_os_plan9_plan9_sys_src_cmd_postscript_posttek_posttek_ad8a9b301ec0

Scope verified against `Docs/research_subset_a.md`: all files are under `sources/os/plan9/plan9`, which is included in subset A. I read every listed source file completely and kept the sections in the requested order.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/postscript/posttek/posttek.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/postscript/posttek/posttek.c

Purpose: Implements `posttek`, a Tektronix 4014 stream to PostScript translator. It emits DSC comments, copies a PostScript prologue, translates Tektronix alpha/vector/point modes, and handles multi-page output.

Key behavior:
- `main` initializes signals, writes the PostScript header/prologue, parses options, processes input files/stdin, writes trailer/accounting.
- Options configure aspect ratio, copies, font, magnification, forms per page, page list, orientation, offsets, line width, included files, encoding, request passthrough, debug, and fatal-error behavior.
- `statemachine` drives modes: `RESET`, `ALPHA`, `GIN`, `GRAPH`, `POINT`, `SPECIALPOINT`, `INCREMENTAL`, `EXIT`.
- `alpha`, `graph`, `point`, and `incremental` translate Tektronix character, vector, point, and incremental plot encodings into PostScript operators.
- `control` and `esc` implement Tektronix control/escape handling, including font size, graphics mode, special point mode, formfeed, GIN, line style, and defocused line width.
- `formfeed`, `redirect`, and page-list helpers integrate page selection with DSC page accounting.

Dependencies and integration:
- Uses `comments.h`, `gen.h`, `path.h`, `ext.h`, and `posttek.h`.
- Requires prologue procedures such as `setup`, `pagesetup`, `v`, `t`, `p`, `i`, `l`, `w`, `f`, and `done`.
- Shares common PostScript command-line conventions with other Plan 9 postscript tools.

Risks and notes:
- K&R-style C and global state make reentrancy impossible.
- `redirect` sends unselected pages to `/dev/null`, but page state still advances.
- Graph decoding depends on retained static address fields and must preserve Tektronix byte ordering exactly.
- Uses `/dev/null`, stdio, and legacy `signal` behavior.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/postscript/posttek/posttek.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/postscript/posttek/posttek.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/postscript/posttek/posttek.h

Purpose: Defines Tektronix 4014 constants and data structures used by `posttek.c`.

Key contents:
- ASCII control-code macros from `NUL` through `DEL`.
- Display modes: `OUTMODED`, `ALPHA`, `GIN`, `GRAPH`, `POINT`, `SPECIALPOINT`, `INCREMENTAL`, `RESET`, `EXIT`.
- Pen state constants `UP` and `DOWN`.
- Tektronix coordinate limits `TEKXMAX` and `TEKYMAX`.
- `INTENSITY` table for special point plotting.
- Character size tables `CHARHEIGHT`, `CHARWIDTH`, default `TEKFONT`.
- PostScript line-style dash arrays in `STYLES`.
- `Point` and `Fontmap` structs.
- `FONTMAP` maps shorthand/user font names to PostScript Courier variants.
- Declares `get_font`.

Dependencies and integration:
- Included by `posttek.c`; values directly drive state-machine geometry, text motion, and PostScript line styles.

Risks and notes:
- `STYLES` comment says the values belong in the prologue, but they are embedded in C.
- Font mapping is intentionally small and Courier-oriented.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/postscript/posttek/posttek.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/postscript/tcpostio/dial.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/postscript/tcpostio/dial.c

Purpose: Provides a non-Plan 9 `dial` compatibility routine for `tcpostio`, using BSD/POSIX sockets.

Key behavior:
- Parses `dest` in Plan 9-style `tcp!host!service` or `udp!host!service` format.
- Resolves host with `gethostbyname`.
- Resolves service by name or numeric string.
- Opens a socket or reserved local port if requested.
- Applies a 30-second `alarm` around `connect`.
- Attempts SO_KEEPALIVE handling on non-Plan 9 builds.
- Ignores Plan 9 `dir` and `cfdp` parameters.

Dependencies and integration:
- Used by `tcpostio.c` to connect to printer network services.
- Bridges Plan 9 code to traditional Unix networking.

Risks and notes:
- Several error paths leak `tdest`.
- `sp->s_port` is already network byte order on many systems; wrapping it in `htons` is suspicious.
- SO_KEEPALIVE setup appears to set the option to the existing false value rather than enabling it.
- Uses `gethostbyname`, `strtok`, and `alarm`, all legacy/global-state APIs.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/postscript/tcpostio/dial.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/postscript/tcpostio/tcpostio.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/postscript/tcpostio/tcpostio.c

Purpose: Sends PostScript or printer data to a network printer while concurrently reading printer status.

Key behavior:
- Implements a two-process protocol over a Unix `socketpair`.
- Parent `readprinter` polls printer status with control-T requests and parses `%[ status: ... ]%` messages.
- Child `sendfile` waits for `SEND_DATA` commands, writes chunks to the printer, sends EOT, and waits for end-of-job acknowledgement.
- `parsmesg` normalizes printer status strings into internal states: initializing, idle, busy, waiting, printing, printererror, Error, flushing, unknown.
- `getline` reads until newline, EOT, timeout, or buffer limit.
- Options configure block size from baud rate and debug verbosity.

Dependencies and integration:
- Uses `dial` from `dial.c`.
- Assumes printers understand control-T status requests and EOT framing.
- Intended as a printer transport companion for PostScript output tools.

Risks and notes:
- Protocol is timing-sensitive and uses alarms, sleeps, and select timeouts.
- `fprintf(stderr, buf)` prints printer-provided text as a format string, which is unsafe in modern terms.
- `blocksize = baud/10` is a throughput heuristic.
- Parent/child exit status is ORed; behavior depends on Plan 9/Unix wait status representation.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/postscript/tcpostio/tcpostio.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/postscript/text2post/text2post.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/postscript/text2post/text2post.c

Purpose: Converts plain text/UTF input into structured PostScript pages.

Key behavior:
- Emits DSC header, `postprint` prologue, optional round-page support, encoding, setup, form-per-page support, unknown-character prologue, trailer, fonts, and page count.
- Maintains page, line, character, spacing, tab, and PostScript string state.
- `txt2post` reads runes; high byte selects a Lucida Unicode font bank, low byte selects glyph.
- Handles spaces, tabs, newlines, formfeeds, and backspaces.
- `pagelist` builds a bitmap of selected output pages from ranges.
- Tracks used fonts for the final `DocumentFonts` trailer.

Dependencies and integration:
- Uses Plan 9 `Bio`, `comments.h`, `path.h`, common prologue files, and `/sys/lib/postscript/prologues/pjw.char.ps`.
- Closely follows other Plan 9 PostScript tool setup options.

Risks and notes:
- `pagelist` reallocates without zeroing newly allocated bytes, so page bitmap expansion may inherit garbage bits.
- Unsupported/out-of-range font banks emit `pw`.
- Backspace behavior is partial and mainly moves by previous character width.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/postscript/text2post/text2post.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/postscript/tr2post/Bgetfield.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/postscript/tr2post/Bgetfield.c

Purpose: Provides token/field parsing helpers over Plan 9 `Biobufhdr` streams for `tr2post`.

Key behavior:
- Defines local `isspace` for runes.
- `Bskipws` skips whitespace and updates `inputlineno` on newlines.
- `asc2dig` converts decimal/octal/hex digits.
- `Bgetfield` parses decimal ints, unsigned ints, strings, or single runes and ungets the first delimiter.

Dependencies and integration:
- Used throughout `tr2post` parsing: troff commands, device control commands, DESC files, metrics, and drawing arguments.

Risks and notes:
- The unsigned parser has likely bugs: it checks `*c` where `c` is an uninitialized local byte array, and computes `u = dig + (n * base)` instead of using `u`.
- Returns can conflate EOF and malformed fields in some paths.
- String parsing protects against overflow by requiring room for `UTFmax`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/postscript/tr2post/Bgetfield.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/postscript/tr2post/chartab.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/postscript/tr2post/chartab.c

Purpose: Manages troff font mounting, metric loading, glyph lookup tables, and PostScript font selection for `tr2post`.

Key behavior:
- `mountfont` updates the troff mounted-font table.
- `settrfont` resolves current troff font position to a loaded troff font entry.
- `setpsfont` emits PostScript font changes and optional slant/height changes.
- `findpfn` interns PostScript font names.
- `readpsfontdesc` reads `/sys/lib/postscript/troff/<font>` map ranges from Unicode/troff glyph ranges to PostScript font ranges.
- `readtroffmetric` reads `/sys/lib/troff/font/dev<devname>/<font>` metric files, charsets, widths, special flags, and named character entries.
- `findtfn` lazily loads troff metric and PostScript descriptions.
- `finish` writes trailer font and page metadata.
- `t_slant` and `t_charht` affect later `setpsfont` output.

Dependencies and integration:
- Core service used by `conv.c`, `utils.c`, `readDESC.c`, and prologue generation.
- Relies on `devname`, font directories, `galloc`, `Bgetfield`, and Plan 9 rune conventions.

Risks and notes:
- Many fatal paths for missing or inconsistent font metadata.
- Quote handling in metric charset entries is marked incomplete.
- Font descriptions must not cross 256-glyph block boundaries.
- Global font state is reset indirectly by changing `curpostfontid`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/postscript/tr2post/chartab.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/postscript/tr2post/conv.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/postscript/tr2post/conv.c

Purpose: Main troff device-independent input interpreter for `tr2post`.

Key behavior:
- Reads one command rune at a time and dispatches troff output commands.
- Handles point size, font position, literal rune, special character, absolute/relative motion, compact two-digit motion plus character, page starts, line records, word spaces, drawing commands, and device-control commands.
- Ignores numeric character command `N` after parsing its number.
- Tracks `inputlineno`.
- Calls `endpage` at EOF.

Dependencies and integration:
- Calls `settrfont`, `runeout`, `specialout`, `hgoto`, `vgoto`, `hmot`, `vmot`, `draw`, `devcntl`, `startpage`, and `endpage`.

Risks and notes:
- Unknown troff commands are warnings, not fatal.
- Numeric glyph command `N` is effectively unimplemented.
- Uses `Brdline` to discard trailing data for comments and line records.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/postscript/tr2post/conv.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/postscript/tr2post/devcntl.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/postscript/tr2post/devcntl.c

Purpose: Interprets troff `x` device-control commands for `tr2post`.

Key behavior:
- Maintains `devname`, `resolution`, `minx`, and `miny`.
- Handles font mounting, initialization, resolution, device name, character height, slant, and input encoding stubs.
- For `x X ...` extension commands, dispatches picture inclusion, path begin/end, object begin/end, and PostScript passthrough.
- Explicitly fatal-errors on unimplemented extensions: inline pictures, new baseline, draw text, set text, set color, INFO, ExportPS.

Dependencies and integration:
- Calls `mountfont`, `initialize`, `t_charht`, `t_slant`, `picture`, `beginpath`, `drawpath`, and string flushing helpers.
- Consumes full device-control lines and increments `inputlineno`.

Risks and notes:
- Reads extension payload into fixed buffers.
- Several extensions are recognized but deliberately not implemented.
- `Bungetc(inp)` after reading the line is subtle and preserves newline handling for downstream line consumption.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/postscript/tr2post/devcntl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/postscript/tr2post/draw.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/postscript/tr2post/draw.c

Purpose: Translates troff drawing commands and path grouping commands into PostScript drawing procedure calls.

Key behavior:
- `draw` handles line, circle, ellipse, arc, and spline/wiggly-line commands.
- `drawspline` converts troff spline points to `Ds` prologue procedure calls.
- Updates `hpos`/`vpos` to troff’s expected current point after drawing.
- `beginpath` starts composite paths, emits `gsave`, `newpath`, current move, and sets `/inpath`.
- `drawpath` ends composite paths and either copies raw PostScript or parses friendly path attributes.
- `parsebuf` recognizes stroke/fill variants, gray, color, line width, reverse path, and quoted PostScript passthrough.

Dependencies and integration:
- Depends on drawing procedures from the PostScript prologue, and `pageon`, `endstring`, global position state, and `drawflag`.

Risks and notes:
- `parsebuf` mutates the input buffer and silently ignores unknown tokens.
- Fixed local point arrays limit spline command length.
- Color support assumes a PostScript color dictionary is present.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/postscript/tr2post/draw.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/postscript/tr2post/pictures.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/postscript/tr2post/pictures.c

Purpose: Implements PostScript picture inclusion for `tr2post`.

Key behavior:
- `picture` parses `x X PI` colon-separated arguments: offsets, indent, line length, trap distance, file/page, frame dimensions, and flags.
- Supports centering/justification, outline, whiteout, scale-both, and rotation flags.
- Opens the referenced picture and calls `ps_include` to place it in the current page coordinate system.
- Temporarily restores/saves the surrounding PostScript state around inclusion.
- `picopen` currently opens the path directly.
- `piccopy` copies a fixed byte count between `Biobufhdr`s.
- Inline-picture support is present only inside disabled `#ifdef UNDEF` blocks.

Dependencies and integration:
- Called from `devcntl.c`.
- Uses `ps_include.c`, current troff position, device resolution, and page selection state.

Risks and notes:
- Argument count checks are off by one: code uses `fields[6]` and sometimes `fields[7]`.
- Inline-picture comments describe a larger design that is not active.
- `picopen` fatal-errors on missing files despite caller also checking for NULL.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/postscript/tr2post/pictures.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/postscript/tr2post/ps_include.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/postscript/tr2post/ps_include.c

Purpose: Includes selected pages from an existing PostScript file into the current PostScript output.

Key behavior:
- Scans DSC comments for prologue/setup boundaries, page boundaries, page/global definitions, trailer, and bounding boxes.
- Defaults bounding box to US Letter dimensions if none is found.
- Emits a PostScript wrapper that saves/restores state, disables page operators, clips/scales/rotates/translates the included page, and optionally whiteouts/outlines.
- Copies prologue, global definitions, selected page, and trailer.
- `copy` indents lines beginning with `%` to neutralize nested DSC comments without breaking encodings.
- Resets current font cache after inclusion.

Dependencies and integration:
- Called from `pictures.c`.
- Uses wrapper fragments declared in `ps_include.h`.

Risks and notes:
- `%%PageBoundingBox` handling relies on the current `i` page number from previous parsing, which is fragile.
- DSC parsing is simple and may not handle all valid PostScript documents.
- `global` allocation uses dynamic grow-by-20 sections.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/postscript/tr2post/ps_include.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/postscript/tr2post/ps_include.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/postscript/tr2post/ps_include.h

Purpose: Defines PostScript wrapper text fragments used by `ps_include.c`.

Key contents:
- `PS_head` starts inclusion, saves context, disables page operators, sets up dictionary and stack preservation.
- `PS_setup` computes bounding boxes, transforms, scale factors, clipping, whiteout, rotation, and inclusion graphics state.
- `PS_tail` restores state, optionally draws an outline, restores operand stack and context, and ends inclusion.

Dependencies and integration:
- Included directly by `ps_include.c`.
- The generated PostScript expects variables emitted by `ps_include`.

Risks and notes:
- This header contains static data definitions rather than declarations, so it is meant for single inclusion.
- Wrapper correctness depends on PostScript interpreter behavior and DSC scanning from `ps_include.c`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/postscript/tr2post/ps_include.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/postscript/tr2post/readDESC.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/postscript/tr2post/readDESC.c

Purpose: Reads troff device `DESC` metadata for `tr2post`.

Key behavior:
- Builds the path `%s/dev%s/DESC` from `FONTDIR` and `devname`.
- Recognizes tokens: `PDL`, `Encoding`, `fonts`, `sizes`, `res`, `hor`, `vert`, `unitwidth`, `charset`.
- Stores print description language, encoding, device resolution, unit width.
- Allocates and initializes mounted-font table based on `fonts`.
- Mounts listed fonts and forces metric/font-map loading with `findtfn`.
- Ignores sizes, horizontal/vertical motion resolution, and special charset list.

Dependencies and integration:
- Called early in `tr2post.c`.
- Drives font and resolution state used by glyph output and drawing.

Risks and notes:
- Returns `0` at end even after successful parsing; caller ignores the value.
- Unknown tokens produce warnings unless comment lines.
- Uses global `fontmnt` state to distinguish font count from later font names.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/postscript/tr2post/readDESC.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/postscript/tr2post/tr2post.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/postscript/tr2post/tr2post.c

Purpose: Main program for converting troff device-independent output to PostScript.

Key behavior:
- Parses options for aspect ratio, copies, debug, magnification, forms per page, page list, orientation, offsets, and PostScript passthrough.
- Writes converted page body to a temporary file first.
- Reads device `DESC`, converts stdin or input files via `conv`, then closes temp output.
- Reopens stdout, emits final prologue/setup, copies temporary body to stdout, and writes trailer.
- `prologues` conditionally includes base dpost prologue, drawing prologue if any drawing was used, round page support, encoding, forms setup, passthrough, and charlib definitions for built characters.
- `cleanup` removes the temp file at exit.

Dependencies and integration:
- Coordinates all `tr2post` modules.
- Uses `comments.h`, `path.h`, `common.h`, font/DESC loaders, page-list support, and global `Bstdout`.

Risks and notes:
- Uses `tmpnam`, which is unsafe by modern standards.
- Delayed prologue emission is necessary because draw/charlib use is discovered during conversion.
- Missing input files are reported and skipped.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/postscript/tr2post/tr2post.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/postscript/tr2post/tr2post.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/postscript/tr2post/tr2post.h

Purpose: Shared declarations, types, globals, constants, and prototypes for `tr2post`.

Key contents:
- Constants for special characters, token sizes, and charlib path.
- Externs for debug, font size/position, device state, font tables, current troff font, drawing flag, build-char list.
- `specname`, `charent`, `pfnament`, `psfent`, and `troffont` structures.
- Prototypes for initialization, font mounting/resolution, glyph output, conversion, motion, drawing, device control, errors, page/string state, font selection, DESC parsing, picture/path inclusion, and PostScript inclusion.

Dependencies and integration:
- Included by nearly every `tr2post` source file.
- Ties together `common.h` constants such as `NUMOFONTS` and `FONTSIZE`.

Risks and notes:
- Heavy reliance on global mutable state.
- Function declarations use legacy C style in places.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/postscript/tr2post/tr2post.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/postscript/tr2post/utils.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/postscript/tr2post/utils.c

Purpose: Provides position tracking, horizontal/vertical motion, and glyph emission helpers for `tr2post`.

Key behavior:
- Tracks `hpos`, `vpos`, `fontsize`, and `fontpos`.
- `hgoto`, `vgoto`, `hmot`, and `vmot` update troff current position and flush strings as needed.
- `hmot` compares actual motion with expected glyph width and emits a space when motion matches current font’s space width.
- `findglyph` searches a font’s glyph linked list bucket.
- `glyphout` searches current font, special fonts, fallback font position 1, then Peter-face fallback `pw`; selects PostScript font and emits char strings or charlib build calls.
- Tracks required charlib definitions in `build_char_list`.
- `runeout` and `specialout` convert input to glyph lookup tokens.

Dependencies and integration:
- Core glyph layer used by `conv.c`.
- Depends on font tables from `chartab.c`, `pageon`, `startstring`, `endstring`, `charcode`, and PostScript font maps.

Risks and notes:
- Fallback behavior is warning-heavy and may silently substitute `pw`.
- Spacing logic depends on `expecthmot` matching later `hmot`.
- `nametorune` and `graphfunc` are stubs.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/postscript/tr2post/utils.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/postscript/trofftable/trofftable.mk -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/postscript/trofftable/trofftable.mk

Purpose: Makefile for building/installing the `trofftable` shell script and related PostScript/manual assets.

Key behavior:
- Defines system/version, ownership/group, font/postscript install paths, and man-page directory.
- `trofftable` target rewrites path variables in `trofftable.sh` using `sed`.
- `install` creates target directories if absent, installs executable, `trofftable.ps`, and man page with ownership/mode.
- `clobber` removes generated script.
- `changes` rewrites makefile and manual defaults from current variables.

Dependencies and integration:
- Expects `trofftable.sh`, `trofftable.ps`, and `trofftable.1`.
- Uses traditional Unix `/bin/make`, `sed`, `cp`, `chmod`, `chgrp`, and `chown`.

Risks and notes:
- `clean` is empty.
- Install paths default to old Unix-style directories, not Plan 9 `/sys`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/postscript/trofftable/trofftable.mk -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/postscript/trofftable/trofftable.sh -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/postscript/trofftable/trofftable.sh

Purpose: Generates a PostScript program that builds troff width tables or device descriptions by querying a printer/interpreter.

Key behavior:
- Parses options for copy files, font directory, host font directory, prologue, shell library, device, comments offset, octal escapes, slowdown, and template.
- Sources a shell library from either explicit `-S` or `FONTDIR/dev<DEVICE>/shell.lib`.
- Uses `BuiltinTables` and `awk` to derive the command that builds the requested table.
- Emits PostScript structuring comments and includes configured prologue/data files.
- Supports host-side font file inclusion when available.

Dependencies and integration:
- Built by `trofftable.mk`.
- Requires shell library functions such as `BuiltinTables`.
- Uses `trofftable.ps` and `dpost.ps` style prologues.

Risks and notes:
- Relies on printer serial-port output through PostScript `print`.
- Shell quoting is old-style and not hardened.
- Requires either a device or explicit shell library.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/postscript/trofftable/trofftable.sh -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/pr.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/pr.c

Purpose: Implements Plan 9 `pr`, a file pagination and multi-column formatter with headings, tabs, numbering, margins, and multi-file modes.

Key behavior:
- Parses classic `pr` options: columns, starting page, double-space, tab settings, formfeed, header, input tabs, length, across/multiple files, offset, separator, no heading, width, numbering, balancing, and odd-page padding.
- `pr` opens files/stdin, calculates dates/headings, and loops pages.
- `putpage` emits one page across columns/files with optional line numbers and spacing.
- `nexbuf` fills a page buffer for multi-column output.
- `balance` balances the last page’s columns.
- `get` normalizes input, tab expansion, backspace/escape effects, and EOF across multi-file mode.
- `put` and `putspace` emit output with clipping and output tab compression.
- Open errors are deferred/printed cleanly.

Dependencies and integration:
- Uses Plan 9 `Bio`, `Dir`, `dirstat`, runes, and standard libc.

Risks and notes:
- Fixed `NFILES` limit of 20.
- Many formatting globals interact; option order matters in places.
- Multi-column buffering can fail with page-buffer overflow if sizing assumptions are wrong.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/pr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/primes.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/primes.c

Purpose: Prints prime numbers in an optional numeric range.

Key behavior:
- Accepts `start [finish]`; if no args, reads first nonblank line from stdin as start.
- Prints small primes from a fixed table before switching to segmented sieve.
- Uses a 1000-byte bit table representing 8000 candidate offsets.
- Uses a wheel increment table after marking 3, 5, and 7.
- `mark` marks multiples of a factor within the current segment.
- Supports values up to `big` around 2^53.

Dependencies and integration:
- Uses Plan 9 libc/Bio and floating-point arithmetic for large integer-ish values.

Risks and notes:
- Floating-point representation limits exactness for very large values.
- Does not explicitly skip composite odd values below current segment except through marking.
- `limit < nn` check in two-argument path occurs before `nn` is set from start, but default `nn` is 0, so only negative/zero edge cases are affected.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/primes.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/prof.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/prof.c

Purpose: Reads Plan 9 profiling data and reports either a call graph or flat time/call table.

Key behavior:
- Options: `-v` verbose sum trace, `-d` graph mode, `-r` allow recursion expansion.
- Loads symbols from an executable using `mach.h` helpers.
- Loads `prof.out`-style binary `Data` records, byte-swapping big-endian fields.
- `graph` recursively prints call tree with recursion suppression unless `-r`.
- `plot` builds symbol accumulators, recursively sums exclusive time, sorts by milliseconds, and prints percentage/time/calls/name.
- `defaout` chooses default executable by `$objtype`.

Dependencies and integration:
- Uses Plan 9 `mach` symbol APIs: `crackhdr`, `syminit`, `textsym`, `findsym`.
- Profiling data format stores `down`, `right`, `pc`, `count`, `time`.

Risks and notes:
- Recursion/cycle handling is only in graph mode; sum assumes tree-like data.
- `time < 0` is checked on unsigned-ish stored data after assignment to long.
- Allocates symbol accumulator incrementally with `realloc`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/prof.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/proof/font.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/proof/font.c

Purpose: Handles troff-to-bitmap font mapping and glyph rendering for the interactive `proof` viewer.

Key behavior:
- Maintains troff font names, loaded font cache by font/size, map selection, special font, and fontmap entries.
- `dochar` maps a rune/name to current font, special font, fallback font, or draws the name using the default screen font.
- `loadfont` searches configured bitmap font directory for `.font` or subfont files, with fallbacks.
- `loadfontname` remaps a troff font position and clears cached sizes.
- `readmapfile` parses map files with `xheight`, `map`, `special`, and `troff` sections.
- `buildmap` creates fast `quick` rune maps and linked-list slow maps.
- `buildtroff` maps troff names to bitmap filename prefixes and optional fallback fonts.
- `allfree` forces all font positions to dummy mappings.

Dependencies and integration:
- Uses Plan 9 draw/event/Bio APIs and `proof.h`.
- Called by `proof/main.c` and `proof/htroff.c`.

Risks and notes:
- Fixed maximums: `NMAP`, `NFONT`, `NSIZE`.
- Loading falls back through Times and Pelm paths.
- Missing fonts are fatal.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/proof/font.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/proof/htroff.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/proof/htroff.c

Purpose: Parses troff device-independent output and renders pages into a Plan 9 draw window for preview.

Key behavior:
- Maintains device resolution, current position, scaling divisor, offsets, page views, page index, font, and size state.
- `readpage` interprets troff commands: page starts, characters, special characters, numeric glyphs, drawing commands, size/font changes, motion, comments, lines, and device controls.
- Drawing supports lines, circles, ellipses, arcs, and splines/wiggly lines.
- `devcntrl` handles resolution, device name, and font mounting.
- `skipto` uses buffered input offsets and page index to navigate pages.
- `botpage` handles interactive commands for quit, repaint, magnification, offsets, multi-view layout, page numbers, relative motion, and debug toggle.
- `eresized` refreshes layout on window resize.

Dependencies and integration:
- Uses `proof/main.c` ring-buffer input functions, `screen.c` command input, and `font.c` glyph rendering.

Risks and notes:
- Must parse skipped pages to discover font loads.
- Page offset buffer is bounded by `NPAGENUMS`.
- Some troff device controls are ignored.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/proof/htroff.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/proof/main.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/proof/main.c

Purpose: Program entry point and input buffering layer for the interactive `proof` troff previewer.

Key behavior:
- Parses options for map file, font directory, debug, magnification, tracking, x/y offsets, and number of views.
- Opens optional input file on stdin.
- Initializes Bio, loads font map file, initializes font positions, opens screen, clears screen, and starts `readpage`.
- Implements a circular input buffer allowing recent input to be rewound.
- Provides `getc`, `getrune`, `ungetc`, `offsetc`, `seekc`, and `rdlinec`.

Dependencies and integration:
- Uses Plan 9 draw/event and `proof.h`.
- `track` mode is used by screen event loop to detect file modification.

Risks and notes:
- Ring buffer is fixed at 100000 bytes, typically enough for several pages.
- `seekc` can only rewind within buffered data.
- `strncpy` into fixed arrays may leave unterminated strings if arguments are too long.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/proof/main.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/proof/proof.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/proof/proof.h

Purpose: Shared definitions and declarations for the `proof` previewer.

Key contents:
- Limits for pages, fonts, sizes, minimum size, default magnification, maximum views.
- Externs for device name, magnification, view count, current position/font/size, scaling, offsets, cursor, font directory, debug, and resize flag.
- Declares screen, map, font, rendering, and buffered-input functions.
- Defines `dprint` debug macro.

Dependencies and integration:
- Included by `font.c`, `htroff.c`, `main.c`, and `screen.c`.

Risks and notes:
- Global-state API reflects small single-process viewer design.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/proof/proof.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/proof/screen.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/proof/screen.c

Purpose: Manages window initialization, keyboard/mouse commands, panning, menus, and cursors for `proof`.

Key behavior:
- `mapscreen` initializes draw and event handling.
- `clearscreen` clears display.
- `screenprint` writes prompt/status text.
- `getcmdstr` waits for resize, mouse, keyboard, or tracking timer events and returns command strings for `htroff.c`.
- Keyboard input accumulates a line until newline/return/view key.
- Mouse button 1 pans, button 3 opens menu, button 2 is effectively continue/no-op.
- Menu commands map to next, previous, page prompt, repaint, bigger, smaller, pan, and quit confirmation.
- Defines custom cursors: deadmouse, blot, skull.

Dependencies and integration:
- Uses Plan 9 `event` library and `proof.h`.
- Commands returned here are interpreted by `botpage`.

Risks and notes:
- `confirm` lacks an explicit return type in old C style.
- Tracking reload uses modification time polling.
- Panning scrolls the current screen image and updates global `xyoffset`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/proof/screen.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ps.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ps.c

Purpose: Implements Plan 9 `ps` by reading `/proc`.

Key behavior:
- Options: `-a` show args, `-p` show base/current priority, `-r` show real elapsed time.
- Changes to `/proc`, reads all directory entries, sorts numerically by pid.
- For each process, reads `<pid>/status`, tokenizes fields, and prints user, pid, times, optional priority/real time, memory size, state, and command.
- With `-a`, reads `<pid>/args` and prints arguments with newlines replaced by spaces.

Dependencies and integration:
- Assumes Plan 9 `/proc/<pid>/status` field layout.
- Uses `dirreadall`, `Dir`, `Bio`, and Plan 9 libc.

Risks and notes:
- Ignores processes that disappear or cannot be read.
- Fixed buffers for status and args.
- Sorting uses `atoi` on directory names.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ps.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/pump.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/pump.c

Purpose: Copies input to output through a shared circular buffer, separating reading and writing into different processes.

Key behavior:
- Options configure read/write block sizes, sleep delay, output file, buffer size in KB, initial prefill, seek offset, and output byte/time-style limit.
- Allocates circular buffer, forks with shared memory using `rfork(RFMEM)`.
- Child reads one or more files/stdin into buffer with backpressure.
- Parent writes from buffer to stdout or output file.
- Uses `Lock` to protect `nin`, `nout`, `done`, and buffer counters.
- Supports prefill before publishing `nin`.

Dependencies and integration:
- Plan 9-specific `rfork`, shared memory, `Lock`, and libc.

Risks and notes:
- `done` is shared memory state; process lifetime and exit ordering matter.
- `verb` is never set by options.
- `tsize` option multiplies minutes by a magic byte count, suggesting a throughput/time approximation.
- Error paths may stop one side while the other notices via `done` or EOF.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/pump.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/pwd.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/pwd.c

Purpose: Prints the current working directory.

Key behavior:
- Calls `getwd` into a fixed 512-byte buffer.
- Prints the path on success.
- Prints `pwd: %r` and exits with `getwd` status on failure.

Dependencies and integration:
- Uses Plan 9 libc only.

Risks and notes:
- Fixed path buffer size.
- Minimal command with no options.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/pwd.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/qa/a.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/qa/a.h

Purpose: Shared definitions for the PowerPC assembler `qa`.

Key contents:
- Includes Plan 9 headers and `../qc/q.out.h`.
- Defines assembler limits, buffer sizes, hash sizes, macro limits, allocation macros, and input helpers.
- Structures: `Sym`, `Io`, `Gen`, `Hist`.
- Global state for debug flags, symbol hash, include paths, IO stack, line number, output file, pass number, pc, null address, history, macro defines, and output buffer.
- Declares lexer/parser, assembler, object emission, macro/preprocessor, include, history, memory hunk, and compatibility functions.

Dependencies and integration:
- Used by `a.y` and `lex.c`.
- Shares architecture constants with `qc/q.out.h`.

Risks and notes:
- Uses hunk allocator macros and many process-global variables.
- Compatibility prototypes import shared C compiler support.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/qa/a.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/qa/a.y -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/qa/a.y

Purpose: Yacc grammar for the PowerPC assembler.

Key behavior:
- Defines tokens for instruction classes, registers, constants, names, labels, string constants, and floating constants.
- Handles labels, variable assignments, scheduler directives, and instructions.
- Grammar covers integer loads/stores, floating loads/stores, FPSCR/condition register moves, arithmetic/logical/shift/unary ops, multiply-accumulate, immediates, condition-register ops, branch forms, traps, floating ops, compares, rotate/mask, multiword moves, indexed ops, NOP, WORD, END, TEXT/GLOBL, DATA, and RETURN.
- Defines addressing forms: registers, special registers, condition regs, FPSCR fields, segment regs, indexed addressing, static/name addressing, stack/base/frame pointers, constants and expressions.
- Emits instructions via `outcode` and `outgcode`.

Dependencies and integration:
- Includes `a.h`; generated parser consumed by `lex.c`.
- Uses `pc`, `pass`, `nullgen`, and PowerPC operand encodings from `q.out.h`.

Risks and notes:
- Some register range diagnostics refer to `$$` before assignment in `sreg` rule, likely a bug.
- Undefined label errors happen on pass 2.
- Mask generation validates 0..31 ranges.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/qa/a.y -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/qa/lex.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/qa/lex.c

Purpose: Main program, opcode table, initialization, and object emission for the PowerPC assembler.

Key behavior:
- `main` parses assembler options, supports parallel assembly for multiple files using `$NPROC`, and dispatches `assemble`.
- `assemble` determines output file, include paths, creates output, runs two parser passes, emits history and final object.
- `itab` maps register/opcode names to yacc token types and architecture opcode values.
- `cinit` initializes symbols, null generator, IO state, and reserved names.
- `zname`, `zaddr`, `outsim`, `outcode`, and `outgcode` write Plan 9 object records and operands.
- `outhist` writes file path/history records with Unix/Windows path handling.
- Includes shared compiler lexer, macro preprocessor, and compatibility bodies.

Dependencies and integration:
- Includes generated `y.tab.h`, `a.h`, `../cc/lexbody`, `../cc/macbody`, and `../cc/compat`.
- Uses PowerPC opcode constants from `q.out.h`.

Risks and notes:
- Large opcode table is the source of assembler vocabulary.
- `outfile` is global and reused; multi-file assembly forks to isolate state.
- Symbol cache wraps at `NSYM`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/qa/lex.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/qc/cgen.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/qc/cgen.c

Purpose: PowerPC C compiler expression/code generator for Plan 9 `qc`.

Key behavior:
- `cgen` lowers scalar expressions, assignments, bitfields, arithmetic/logical ops, compound assignments, calls, indirection, comparisons, boolean ops, comma, casts, struct field access, conditionals, and pre/post inc/dec.
- Chooses evaluation order based on expression complexity and function-call risk.
- Uses register allocators, address generators, and `gopcode`/`gmove` to emit target operations.
- Handles bitfield load/store through `bitload`/`bitstore`.
- `lcgen` and `reglcgen` produce l-values/addresses.
- `boolgen` and `bcgen` generate branch-based boolean evaluation and materialized boolean values.
- `sugen` copies/constructs structs/unions, rewrites struct literals, handles struct-return functions, and emits unrolled/looped long-word copies.
- `layout` emits small copy layouts using temporary registers.
- 64-bit support uses `isvdirect`, `isvconstable`, `vcgen`, `cmpv`, `testv`, and `cgen64` for `vlong` constants, casts, calls, and comparisons.

Dependencies and integration:
- Includes `gc.h`.
- Relies on compiler front-end node/type metadata, register allocation, instruction selection, branch patching, switch/bitfield helpers, and 64-bit helpers.

Risks and notes:
- Many comments identify old compromises, especially struct temporaries and vlong casts.
- 64-bit non-vlong conversion comments note typefd correctness gaps.
- Evaluation order is carefully tuned around function calls and side effects.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/qc/cgen.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/qc/enam.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/qc/enam.c

Purpose: Provides architecture instruction name strings for the PowerPC compiler/assembler toolchain.

Key contents:
- `anames[]` maps opcode enum indexes to printable mnemonics.
- Covers base integer, branch, compare, floating-point, move, condition-register, special, pseudo, embedded MAC, optional 32-bit floating, fp2, and final `LAST` entries.

Dependencies and integration:
- Referenced through `extern char *anames[]` in `gc.h`.
- Used by listing/formatting/debug output.

Risks and notes:
- Must stay exactly synchronized with opcode enum values in `q.out.h`.
- Pure data table; no control flow.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/qc/enam.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/qc/gc.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/qc/gc.h

Purpose: Central target-specific header for the Plan 9 PowerPC C compiler backend.

Key contents:
- Includes common C compiler definitions and PowerPC object definitions.
- Defines C type sizes for this target.
- Declares core backend structures: `Adr`, `Prog`, `Case`, `C1`, `Multab`, `Hintab`, `Var`, `Reg`, and `Rgn`.
- Defines instruction, register-allocation, data-flow, loop, and region globals.
- Declares helpers for code generation, text emission, register allocation, moves, addressing, constants, branches, switch lowering, bitfields, external data, listing formats, register optimization, peephole optimization, copying/substitution, register bit conversions, and 64-bit comparison lowering.
- Defines data-flow macros such as `BLOAD`, `BSTORE`, `LOAD`, and `STORE`.

Dependencies and integration:
- Included by target backend source files such as `cgen.c`.
- Interfaces with shared compiler frontend `../cc/cc.h` and target object format `../qc/q.out.h`.

Risks and notes:
- Header is both API and global-state declaration file using `EXTERN`.
- Constants like `NRGN`, register counts, and type sizes are baked into backend behavior.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/qc/gc.h -->