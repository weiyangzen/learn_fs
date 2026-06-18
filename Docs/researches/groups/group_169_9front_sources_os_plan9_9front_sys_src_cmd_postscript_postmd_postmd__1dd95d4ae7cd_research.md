# Group Research: group_169_9front_sources_os_plan9_9front_sys_src_cmd_postscript_postmd_postmd__1dd95d4ae7cd

Scope checked against `Docs/research_subset_a.md`: `sources/os/plan9/9front` is included. All listed source files were read from the working tree. Local note: `sources/os/plan9/9front/sys/src/cmd/proof/proof.h` is 44 lines in the checked-out tree, while the prompt metadata says 45.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/postscript/postmd/postmd.mk -->
# File Research: sources/os/plan9/9front/sys/src/cmd/postscript/postmd/postmd.mk

Build/install makefile for the `postmd` PostScript support program. It sets package defaults (`SYSTEM=V9`, `VERSION=3.3.2`, owner/group, install paths), compiles `postmd.o` plus shared objects from `../common`, links `postmd` with `-lm`, and installs the executable, `postmd.ps`, and `postmd.1`.

Integration points:
- Depends on `../common/common.mk` targets for `glob.o`, `misc.o`, `request.o`, and `tempnam.o`.
- Installs binaries under `POSTBIN` and prologue/support files under `POSTLIB`.
- `changes` rewrites this makefile and the manpage with current path/version variables using `sed`.

Risks:
- Install paths default to real system directories except `MAN1DIR=/tmp`; running `install` as root mutates system locations.
- Recursive common-object builds rely on basename target passing and local directory layout.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/postscript/postmd/postmd.mk -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/postscript/postprint/postprint.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/postscript/postprint/postprint.c

ASCII-to-PostScript translator. It emits DSC comments, copies a prologue, applies command-line PostScript setup options, translates text into PostScript strings/operators, handles tabs/backspaces/spaces efficiently, paginates by line count, optionally filters output pages, and writes simple accounting records.

Key behavior:
- `main` runs signal setup, header/prologue emission, option parsing, setup, input processing, trailer/accounting.
- `header` pre-scans `-L` so the chosen prologue appears before setup.
- `options` supports layout, font, copies, forms-per-page, page list, offsets, font encoding, arbitrary `-P` PostScript passthrough, and common debug/ignore flags.
- `text`, `newline`, `formfeed`, `spaces`, `oput` implement the translation loop.
- `redirect` sends unselected pages to `/dev/null` based on shared `out_list`/`in_olist` helpers.

Integration points:
- Uses shared PostScript comment/path/common headers: `comments.h`, `gen.h`, `path.h`, `ext.h`.
- Requires prologue procedures `setup`, `pagesetup`, `l`, `L`, `LL`, and `done`.
- Uses shared request handling via `saverequest` and `writerequest`.

Risks:
- Classic K&R-style implicit int function definitions make portability dependent on old compiler behavior.
- `spaces` uses assignment in a `while` condition and pushes back the first non-space; NUL bytes terminate the loop path unusually.
- Page counting relies on whether `fp_out == stdout`; page filtering affects accounting semantics.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/postscript/postprint/postprint.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/postscript/postprint/postprint.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/postscript/postprint/postprint.h

Header for `postprint.c`. It defines default page/text settings (`LINESPP=66`, `TABSTOPS=8`, `POINTSIZE=10`), the `Fontmap` mapping type, and `FONTMAP`, which maps troff-like and short names such as `R`, `I`, `B`, `CW`, `courier` to Courier PostScript fonts.

Integration points:
- Included only by `postprint.c`.
- `FONTMAP` must end with `{NULL, NULL}` for `get_font`.

Risks:
- Declares only `char *get_font();`, using old-style prototypes.
- Defaults assume constant-width fonts; proportional fonts are allowed but documented as unreliable for layout.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/postscript/postprint/postprint.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/postscript/postreverse/postreverse.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/postscript/postreverse/postreverse.c

PostScript page-order reverser for DSC-structured documents. It copies the prologue/setup, records page byte offsets, moves `%%BeginGlobal`/`%%EndGlobal` sections into the prologue/setup, writes pages in reverse physical-sheet order, handles multiple forms per page, and copies the trailer.

Key behavior:
- Accepts one file or copies stdin to a temporary file.
- Recognizes `%%EndProlog`, optional setup comments, `%%Page:`, `%%EndPage:`, `%%Trailer`, and package-specific `%%BeginGlobal` comments.
- `-r` disables reversal but still extracts globals; `-n` controls forms-per-page; `-o` selects output pages; `-v` ignores old forms prologue compatibility.
- Uses fixed `Pages pages[1000]` for page ranges and dummy pages needed by forms-per-page reversal.

Integration points:
- Uses shared DSC constants and helpers from `comments.h`, `gen.h`, `path.h`, `ext.h`.
- Uses `tempnam`/`temp_file` from the shared support layer.

Risks:
- Hard page cap of 1000 can overflow for larger documents; no bounds check before `pages[next_page++]`.
- Stdin path reads the input three times via a temporary file.
- Correctness depends on page independence except for recognized global blocks.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/postscript/postreverse/postreverse.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/postscript/postreverse/postreverse.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/postscript/postreverse/postreverse.h

Small header for `postreverse.c`. It defines `Pages`, storing start/stop byte offsets and an `empty` flag for dummy forms-per-page pages, and declares `char *copystdin();`.

Integration points:
- Used by `postreverse.c` to type the global `pages[1000]` array.

Risks:
- Old-style function declaration only.
- `long` offsets mirror legacy `ftell` use and may be limiting on very large files.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/postscript/postreverse/postreverse.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/postscript/postscript.mk -->
# File Research: sources/os/plan9/9front/sys/src/cmd/postscript/postscript.mk

Top-level makefile for the DWB/PostScript package. It documents configuration variables, exports install/build settings, and recursively builds, installs, cleans, clobbers, or rewrites subdirectories named in `TARGETS`.

Key behavior:
- Default targets include common libraries, translators, prologues, font tools, printer I/O tools, and `trofftable`.
- `install` and `changes` export path/version variables to sub-makes.
- Per-target rule clears inherited object/header/link variables and runs `$@/$@.mk` when present.
- `changes` is intended to synchronize low-level makefiles, manpages, and source definitions after config edits.

Integration points:
- Coordinates all sibling postscript package directories.
- Shared settings include `FONTDIR`, `HOSTDIR`, `POSTBIN`, `POSTLIB`, `TMACDIR`, `DKHOST`, `DKSTREAMS`, and `ROUNDPAGE`.

Risks:
- Recursive make assumes each target directory makefile follows the same naming convention.
- Install defaults target system paths under `/usr`; `ROOT` can redirect but defaults empty.
- Comments mention typo `dpsot`; behavior unaffected.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/postscript/postscript.mk -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/postscript/posttek/posttek.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/postscript/posttek/posttek.c

Tektronix 4014-to-PostScript translator. It implements a terminal-state emulator for alpha, graph, point, special point, GIN, and incremental plot modes, emitting PostScript calls defined by the `posttek` prologue.

Key behavior:
- Emits DSC header/prologue/setup, parses layout/font/accounting options, processes each input file through `statemachine`, then writes trailer/accounting.
- `alpha` prints text using Tek character size tables and wraps/margins.
- `graph` decodes Tek 4014 packed coordinate bytes into vectors.
- `point` and `incremental` handle point plotting/intensity and relative pen movement.
- `control` and `esc` implement Tek control/escape mode changes, line styles, defocus/line width, formfeed, and font size commands.
- `formfeed` closes current page, filters pages with `redirect`, and initializes the next page.

Integration points:
- Uses shared PostScript DSC/request helpers and path constants.
- `posttek.h` supplies control-code constants, state IDs, font maps, intensity table, style arrays, and coordinate limits.
- Requires prologue procedures `setup`, `pagesetup`, `v`, `t`, `p`, `i`, `l`, `w`, `f`, and `done`.

Risks:
- Parser relies on legacy terminal byte semantics; malformed streams can cause odd state transitions.
- Fixed stack batching limit for vectors (`points > 100`) is manual and prologue-dependent.
- Old-style declarations and global state limit reentrancy and portability.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/postscript/posttek/posttek.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/postscript/posttek/posttek.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/postscript/posttek/posttek.h

Header for `posttek.c`. It defines Tektronix 4014 ASCII/control constants, display state constants, pen states, screen coordinate maxima, special point intensity table, character size tables, line-style arrays, a `Point` struct, and the same Courier-centric `Fontmap` mapping style used by other translators.

Integration points:
- `CHARHEIGHT`, `CHARWIDTH`, `TEKFONT`, `INTENSITY`, and `STYLES` initialize global arrays in `posttek.c`.
- `OUTMODED` is a sentinel returned by parser/control helpers.

Risks:
- Style arrays are string PostScript snippets embedded in C; comments note they belong in the prologue.
- Fixed coordinate assumptions approximate but do not exactly model the real terminal dimensions.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/postscript/posttek/posttek.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/postscript/tcpostio/dial.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/postscript/tcpostio/dial.c

Non-Plan 9 compatibility implementation of Plan 9-style `dial` for `tcpostio`. It parses destinations like `tcp!host!service` or `udp!host!service`, resolves the host/service, creates a socket or reserved-port socket, connects with a 30-second alarm timeout, and returns the connected fd.

Integration points:
- Used by `tcpostio.c` through `extern int dial(char*, char*, char*, int*)`.
- Supports optional debug logging through global `dial_debug`.

Risks:
- Several early error returns leak `tdest`.
- `sin.sin_port = htons(sp==0 ? atoi(servname) : sp->s_port)` appears wrong for `getservbyname`, whose `s_port` is already network byte order.
- SO_KEEPALIVE path checks the option but calls `setsockopt` with the current false value, so it likely does not enable keepalive.
- Uses IPv4-only legacy resolver APIs and `alarm`, which is process-global.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/postscript/tcpostio/dial.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/postscript/tcpostio/tcpostio.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/postscript/tcpostio/tcpostio.c

TCP printer I/O program. It connects to a network PostScript printer, forks into sender and reader halves, uses a socketpair protocol to coordinate status polling and data transmission, sends job data in throttled blocks, and waits for end-of-job/status responses.

Key behavior:
- `parsmesg` recognizes printer status strings inside `%[ ... ]%`.
- `readprinter` repeatedly asks `sendfile` to request status, reads printer/status data, handles timeouts/errors, and commands the sender to send data or stop.
- `sendfile` waits for protocol commands, sends input blocks, sends control-D at start/end, and sends control-T on status requests.
- `main` parses baud-derived block size/debug, dials printer, creates `socketpair`, forks, and combines parent/child exit statuses.

Integration points:
- Uses `dial.c` compatibility function.
- Protocol bytes are single-character constants shared inside the file.

Risks:
- Uses global `fd_set` and timeout structs with `select`; `select` may mutate timeout values on some systems.
- `fprintf(stderr, buf)` treats printer output as a format string, a format-string vulnerability if untrusted printer data is hostile.
- Exit status combines `rprv|sprv`, but `sprv` is a wait status, not just child return code.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/postscript/tcpostio/tcpostio.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/postscript/text2post/text2post.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/postscript/text2post/text2post.c

Plan 9 `bio`-based text-to-PostScript translator, adapted from `postprint` but supporting encoded runes where high byte selects a Lucida/Courier font slot. It emits DSC/prologue/setup, translates input into PostScript `show`, spacing, and tab operations, tracks used fonts, supports page selection, and writes trailer font/page summaries.

Key behavior:
- Large `charcode[256]` table escapes all byte values for PostScript strings.
- `fontname[]` maps font byte slots to LucidaSansUnicode blocks and Courier fallback.
- `prologues` emits `postprint` prologue, tab/space helpers, encoding setup, forms setup, and unknown-character prologue.
- `txt2post` reads runes, separates low-byte character and high-byte font id, handles spaces/tabs/backspaces/newlines/formfeeds, changes fonts, and uses `pw` for unknown font slots.
- `pagelist` builds a bitmap of pages to print.

Integration points:
- Uses Plan 9 `<u.h>`, `<libc.h>`, `<bio.h>`, and shared `comments.h`/`path.h`.
- Depends on `POSTPRINT`, `ROUNDPAGE`, `FORMFILE`, `ENCODINGDIR`, and `/sys/lib/postscript/prologues/pjw.char.ps`.

Risks:
- `pagelist` grows `pplist` with `realloc` but does not zero newly allocated bytes before OR-ing page bits.
- `cat` opens the file twice and assigns globals unnecessarily; one handle is not closed.
- String/font memory allocated from options is not freed, acceptable for short process lifetime.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/postscript/text2post/text2post.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/postscript/tr2post/Bgetfield.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/postscript/tr2post/Bgetfield.c

Field scanner helpers for `tr2post`. It defines a local whitespace predicate, skips whitespace while tracking `inputlineno`, converts ASCII digits for bases 8/10/16, and implements `Bgetfield` for decimal ints, unsigned ints, strings, and runes.

Integration points:
- Used throughout `tr2post` parsing: DESC/font tables, troff command stream, picture/device-control args.
- Relies on Plan 9 `Bgetrune`, `Bungetrune`, and rune conversion functions.

Risks:
- The unsigned case checks `*c` even though `c` is an uninitialized local byte buffer, and accumulates `u = dig + (n * base)` instead of using `u`; this looks like a real parsing bug.
- Numeric parsing returns `-1` on EOF even after partial data in some paths.
- Local `isspace(Rune)` shadows libc-style names.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/postscript/tr2post/Bgetfield.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/postscript/tr2post/chartab.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/postscript/tr2post/chartab.c

Font and character mapping layer for `tr2post`. It maps troff mounted font names to troff font entries, reads troff metric files and PostScript font description files, builds glyph lookup tables, switches PostScript fonts, and emits document trailer font lists.

Key behavior:
- Maintains PostScript font name table (`pfnafontmtab`) and troff font table (`troffontab`).
- `mountfont` sets a troff font name at a mount position.
- `settrfont` resolves current troff mount position to a font table index.
- `setpsfont` emits PostScript font changes and optional slant/height transformations.
- `readpsfontdesc` reads `/sys/lib/postscript/troff/<font>` mapping ranges.
- `readtroffmetric` reads `/sys/lib/troff/font/dev<devname>/<font>` metrics and character mappings.
- `findtfn` lazily creates and loads font entries.

Integration points:
- Uses `Bgetfield`, `galloc`, global state from `tr2post.h`, and charcode output from common tables.
- `finish` reports only used PostScript fonts in the DSC trailer.

Risks:
- Several parser paths warn and continue on malformed font data, so downstream output may be partial.
- Quote-reuse support in troff metrics is marked “need some code here” and jumps to `flush`.
- Fixed path globals make font location assumptions explicit and not option-driven in this file.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/postscript/tr2post/chartab.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/postscript/tr2post/conv.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/postscript/tr2post/conv.c

Main parser for troff device-independent output in `tr2post`. It reads command bytes from a `Biobufhdr` and dispatches to font, motion, drawing, device-control, page, and glyph output handlers.

Key behavior:
- Handles `s`, `f`, `c`, `C`, `H`, `V`, `h`, `v`, two-digit motion-plus-character forms, `p`, `n`, `w`, `D`, `x`, comments, and newlines.
- Calls `endpage()` before `startpage()` on `p`.
- Ignores numeric character command `N` after reading its value; no output path is implemented there.

Integration points:
- Central driver used by `tr2post.c` for stdin and each input file.
- Depends on motion/glyph/device/draw functions declared in `tr2post.h`.

Risks:
- `N` command is parsed but not emitted.
- Unknown troff functions only warn, which can hide unsupported input.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/postscript/tr2post/conv.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/postscript/tr2post/devcntl.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/postscript/tr2post/devcntl.c

Device-control command handler for `tr2post`, especially `x` and `x X` commands. It mounts fonts, initializes device resolution/name, applies character height/slant, and routes troff `\X` extensions for pictures, paths, raw PostScript, and unimplemented features.

Integration points:
- Invoked from `conv.c` on `x`.
- Calls `initialize`, `mountfont`, `t_charht`, `t_slant`, `picture`, `beginpath`, `drawpath`.
- Uses globals `devname`, `resolution`, `minx`, `miny`.

Risks:
- Several `x X` commands are fatal “not implemented yet” paths.
- Uses fixed-size buffers for command fragments.
- `Bungetc(inp)` after reading a line is subtle; it only pushes back one byte after copying the line buffer.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/postscript/tr2post/devcntl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/postscript/tr2post/draw.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/postscript/tr2post/draw.c

Drawing support for `tr2post`. It translates troff drawing functions into PostScript procedures for lines, circles, ellipses, arcs, and splines, and supports grouped path construction via `BeginPath`/`DrawPath`.

Key behavior:
- `draw` handles `D l`, `D c`, `D e`, `D a`, `D q`, and `D ~`.
- `drawspline` converts troff spline points into PostScript-friendly control data emitted as `Ds`.
- `beginpath` emits `gsave`, `newpath`, current move, and `/inpath true`.
- `drawpath` finalizes a path and either copies raw PostScript or parses simplified tokens.
- `parsebuf` recognizes stroke/fill variants, gray/color/line settings, reversepath, and quoted raw PostScript.

Integration points:
- Sets `drawflag`, which causes `tr2post.c` to include the draw prologue.
- Called from `conv.c` and `devcntl.c`.

Risks:
- `parsebuf` declares `char *p` but enters `for(; p != nil; p = q)` without initializing `p = buf`; this appears to be a real latent bug.
- Fixed arrays in spline parsing cap point count at 100 without explicit overflow reporting.
- Path parser mutates the input buffer and silently ignores unknown tokens.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/postscript/tr2post/draw.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/postscript/tr2post/pictures.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/postscript/tr2post/pictures.c

Picture inclusion support for `tr2post`. It parses `x X PI`/`PictureInclusion` arguments, opens the referenced PostScript picture, computes frame size/position/rotation/alignment flags, restores the current page save state, calls `ps_include`, then restores page state.

Integration points:
- Called from `devcntl.c`.
- Calls `ps_include` from `ps_include.c`.
- Uses `devres`, `hpos`, `vpos`, and global `picflag`.
- Contains disabled `#ifdef UNDEF` code for inline picture packing/copying.

Risks:
- Inline picture support is documented but disabled.
- `picopen` calls `error(FATAL)` on open failure despite caller also checking for `NULL`, so warning recovery path is mostly unreachable.
- Fixed-size `name`, `hwo`, and `flags` buffers can truncate long picture arguments.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/postscript/tr2post/pictures.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/postscript/tr2post/ps_include.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/postscript/tr2post/ps_include.c

PostScript inclusion engine for embedded picture pages. It scans a PostScript file for DSC sections, bounding boxes, globals, the requested page, and trailer, then emits wrapper PostScript from `ps_include.h` plus copied sections transformed/clipped/scaled into a target frame.

Key behavior:
- `copy` copies byte ranges line-by-line and prefixes `%` lines with a space so included DSC comments do not affect the outer document.
- `ps_include` scans for `%%Page`, `%%EndPage`, `%%PageBoundingBox`, `%%BoundingBox`, `%%EndProlog`, setup end comments, `%%Trailer`, and global blocks.
- Emits variables for bounding box, whiteout/outline/scale flags, center, size, adjustment, and rotation.
- Resets `curpostfontid`/`curfontsize` afterward to force state reestablishment.

Integration points:
- Used by `pictures.c`.
- Includes PostScript wrapper arrays from `ps_include.h`.

Risks:
- `global` pointer is only initialized through `grab` when globals are found; safe in normal flow but tightly coupled to `nglobal`.
- Page-bounding-box handling tests `i == page_no`, where `i` is last page number parsed, so ordering assumptions matter.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/postscript/tr2post/ps_include.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/postscript/tr2post/ps_include.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/postscript/tr2post/ps_include.h

Static PostScript wrapper fragments for `ps_include.c`. `PS_head` saves state, disables page operators, creates an inclusion dictionary, and captures the operand stack. `PS_setup` computes bounding box transforms, clipping, scaling, rotation, whiteout, and outline variables. `PS_tail` restores graphics/interpreter state and optionally outlines the included box.

Integration points:
- Included directly by `ps_include.c`.
- Arrays are null-terminated and emitted string-by-string.

Risks:
- PostScript code is embedded as C string arrays, making syntax validation manual.
- Wrapper intentionally neutralizes page operators, which may affect unusual included PostScript that depends on them.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/postscript/tr2post/ps_include.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/postscript/tr2post/readDESC.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/postscript/tr2post/readDESC.c

Reads troff device `DESC` files for `tr2post`. It extracts printer description language, encoding, font mount table, device resolution, unit width, and ignores size/horizontal/vertical/special-character lists as needed.

Integration points:
- Called by `tr2post.c` before conversion.
- Uses `FONTDIR`, `devname`, `Bgetfield`, `mountfont`, and `findtfn`.
- Initializes globals `fontmnt`, `fontmtab`, `devres`, `unitwidth`, `printdesclang`, `encoding`.

Risks:
- State-machine parser depends on token ordering from DESC files.
- `descfilename` allocation length omits some separator/null slack but format string length likely over-allocates enough in practice.
- Special character list is ignored here; actual glyph availability depends on font metric loading.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/postscript/tr2post/readDESC.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/postscript/tr2post/tr2post.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/postscript/tr2post/tr2post.c

Main program for troff-to-PostScript translation. It parses options, loads device/font descriptions, converts input into a temporary PostScript body, then emits prologues/setup/font build snippets followed by the temporary body and trailer.

Key behavior:
- Option handling covers aspect ratio, copies, debug, magnification, forms-per-page, page list, landscape, offsets, and passthrough PostScript.
- Uses a temporary output file first so it can discover used draw support and build characters before writing final prologue.
- `prologues` emits DPOST prologue, optional draw prologue, rounded-page support, setup variables, Latin1 encoding, forms setup, and required charlib build procedures.
- Final phase copies temp body to stdout and calls `finish`.

Integration points:
- Calls `readDESC`, `conv`, `cat`, `finish`.
- Depends on global `drawflag` and `build_char_list` populated during conversion.

Risks:
- Uses `tmpnam`, which is race-prone in general.
- Temporary file cleanup is registered with `atexit`; abrupt termination can leave files.
- Many global state dependencies make conversion order important.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/postscript/tr2post/tr2post.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/postscript/tr2post/tr2post.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/postscript/tr2post/tr2post.h

Shared declarations and data structures for `tr2post`. It defines limits, charlib path, global renderer/font state, glyph/font mapping structs, and prototypes for parsing, drawing, picture inclusion, page/font/string output, and utility functions.

Integration points:
- Included across `tr2post` implementation files.
- Defines `struct charent`, `struct psfent`, `struct troffont`, and `struct pfnament`, which are central to mapping troff glyphs to PostScript fonts.

Risks:
- Large global surface area makes hidden coupling easy.
- Fixed constants such as `MAXSPECHARS`, `MAXTOKENSIZE`, and `CHARLIB` constrain inputs and install layout.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/postscript/tr2post/tr2post.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/postscript/tr2post/utils.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/postscript/tr2post/utils.c

Positioning and glyph output utilities for `tr2post`. It tracks current horizontal/vertical position, font size/position, expected horizontal motion, resolves glyphs through current/special/fallback fonts, emits strings or build-character calls, and provides stubs for unimplemented helpers.

Key behavior:
- `hgoto`, `vgoto`, `hmot`, `vmot` update troff positions and flush strings when needed.
- `glyphout` resolves the current troff font, searches current and special fonts, falls back to a `pw` placeholder, maps to PostScript font ranges, and emits either string bytes or charlib build calls.
- `runeout` and `specialout` convert input to glyph tokens.
- `notavail` prints unavailable feature messages.

Integration points:
- Called by `conv.c`, `draw.c`, and font mapping code.
- Uses `charcode`, `troffontab`, `fontmtab`, `setpsfont`, `pageon`, `startstring`, `endstring`.

Risks:
- Some fallback paths use variables (`mi`) whose initialization depends on earlier special-character branches.
- `initialize`, `graphfunc`, and `nametorune` are stubs.
- Missing glyph fallback relies on finding `pw` in a special font.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/postscript/tr2post/utils.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/postscript/trofftable/trofftable.mk -->
# File Research: sources/os/plan9/9front/sys/src/cmd/postscript/trofftable/trofftable.mk

Makefile that generates and installs the `trofftable` shell script and its PostScript support/manpage. It substitutes configured `FONTDIR`, `POSTBIN`, and `POSTLIB` into `trofftable.sh`, installs `trofftable`, `trofftable.ps`, and `trofftable.1`, and supports `changes` for propagating config into the makefile/manpage.

Integration points:
- Part of top-level `postscript.mk` target list.
- Installs into the same PostScript bin/lib directory scheme as other tools.

Risks:
- `clean` is empty; generated script remains until `clobber`.
- Install target assumes `MAN1DIR` exists.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/postscript/trofftable/trofftable.mk -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/postscript/trofftable/trofftable.sh -->
# File Research: sources/os/plan9/9front/sys/src/cmd/postscript/trofftable/trofftable.sh

Shell script that emits a PostScript program for building troff width tables or typesetter description files on a printer. It sources a device/library shell file, finds the built-in table command for a template/font, then concatenates prologues, optional host font/copy files, setup parameters, the generated command, and trailer.

Key behavior:
- Supports options for copy files, font directory, host font directory, prologue, shell library, device, start comments, octal escapes, slowdown, and template.
- Requires either `-T device` or `-S library`.
- Sources `${LIBRARY:-${FONTDIR}/dev${DEVICE}/shell.lib}` and calls `BuiltinTables`.

Integration points:
- Uses `trofftable.ps` and `dpost.ps`.
- Intended to communicate generated table output over a printer’s serial channel.

Risks:
- Sourcing device/library scripts executes local shell code.
- Command construction depends on shell library output format and `awk`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/postscript/trofftable/trofftable.sh -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/pr.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/pr.c

Plan 9 `pr` implementation: paginates files with headings, columns, line numbering, margins, tabs, optional multi-file columns, balancing, and odd-page padding.

Key behavior:
- `findopt` parses classic `pr` options such as columns, starting page, double spacing, tab handling, formfeed, headings, length, merge/across modes, offset, separator, width, numbering, balancing, and padding.
- `pr` opens a file/stdin, loops pages, prints headings from file mtime/current time, and calls `putpage`.
- `nexbuf` buffers page content for multi-column layout.
- `balance` redistributes final-page buffered lines.
- `get` abstracts reading from current file/column/buffer and updates input position.
- `put` and `putspace` emit output while respecting width, tabs, backspaces, and page filtering.

Integration points:
- Uses Plan 9 `Biobuf`, `Dir`, `dirstat`, `Bgetrune`, `Bputrune`.

Risks:
- Many globals encode formatter state; option interactions are subtle.
- Buffer size calculation multiplies by `sizeof(char)` before allocating `Rune` storage, resulting in larger-than-needed allocation rather than under-allocation on common builds.
- Deferred open errors are partially implemented via an error list type, but current `mustopen` prints directly rather than linking `Err` nodes.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/pr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/primes.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/primes.c

Prime number generator. It accepts optional start and finish bounds, or reads a start from stdin, prints small primes from a table, then repeatedly sieves odd ranges using a wheel pattern and a 1000-byte bit table.

Key behavior:
- Bounds are stored as `double`, with a max near `2^53`.
- `mark` marks multiples of a prime in the current range.
- Uses small-prime table through 229 and wheel increments for candidate factors.

Integration points:
- Standalone command using Plan 9 `Biobuf` and `print`.

Risks:
- Floating-point arithmetic is used for integer-like bounds; valid range is capped to exact integer representation.
- `mark` uses a long index derived from double math; behavior depends on staying within supported limits.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/primes.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/prof.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/prof.c

Profiler report reader for Plan 9 profiling output. It reads symbols from an executable via `libmach`, reads a binary `prof.out`-style data file, and prints either a call graph (`-d`) or flat time/call summary.

Key behavior:
- `datas` validates magic `pr\x0f`, reads cycle frequency, and decodes big-endian records into `Data`.
- `graph` recursively prints call tree entries with recursion suppression unless `-r`.
- `plot` builds a text-symbol accumulator table, calls `sum`, sorts by ticks, and prints percentage/time/calls/name.
- `sum` subtracts child time to compute self time.

Integration points:
- Uses `<mach.h>` symbol APIs: `crackhdr`, `syminit`, `textsym`, `findsym`.
- Expects profiling data record layout matching `Datasz = 20`.

Risks:
- Assumes data file endianness/layout exactly.
- Recursive traversal can be deep; malformed indexes are checked but only print diagnostics.
- `static indent;` in `sum` relies on implicit `int`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/prof.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/proof/font.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/proof/font.c

Font and character mapping support for the `proof` troff previewer. It reads a font map file, maps troff font names to bitmap font prefixes and character maps, lazily loads bitmap fonts/subfonts by size, and draws mapped characters on the screen.

Key behavior:
- `dochar` maps current rune/name through current font, special font, and optional fallback, then draws using `string`.
- `loadfont` searches `.font` files and subfont files under `libfont`, scaling troff size by magnification and map xheight.
- `readmapfile` parses `xheight`, `map`, `special`, and `troff` blocks.
- `buildmap` fills fast `quick` rune map for low values and linked-list map for compound/high names.
- `buildtroff` records troff-name to bitmap-prefix/map/fallback rows.
- `loadfontname` remaps a mounted font slot and frees cached fonts.

Integration points:
- Uses Plan 9 draw/event/font APIs.
- Called by `htroff.c` device-control font commands and character output.
- Shared globals declared in `proof.h`.

Risks:
- Fixed limits: `NMAP=5`, `NFONT`, `NSIZE`, `QUICK`, and static font map table size.
- `fontlookup` silently leaves previous/default state if a troff font is absent.
- Custom `log2` table is depth-specific and includes a noted “BUG” entry copied from libdraw.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/proof/font.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/proof/htroff.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/proof/htroff.c

Troff device-independent output interpreter for the interactive `proof` previewer. It parses troff output, draws text and graphics into a Plan 9 window, manages pages/views/magnification, and supports navigation by buffering input offsets.

Key behavior:
- `readpage` interprets page, character, special character, numeric character, draw, font, size, motion, comment, and device-control commands.
- Draws lines, circles, ellipses, arcs, and splines with Plan 9 drawing primitives.
- `devcntrl` handles device name, resolution, and mounted fonts.
- `skipto` replays/skips input to reach requested pages while preserving font-loading side effects.
- `botpage` handles command strings for page navigation, magnification, view splitting, and offsets.

Integration points:
- Uses input buffering from `main.c`, UI commands from `screen.c`, and font drawing from `font.c`.
- Shares `offset`, `xyoffset`, `DIV`, `res`, `curfont`, `cursize`.

Risks:
- Page index cache fixed at 200 pages.
- Spline point array fixed at 300 points without explicit bounds guard.
- Parser exits on unknown input character, making preview brittle for unsupported troff extensions.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/proof/htroff.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/proof/main.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/proof/main.c

Entry point and input buffering layer for `proof`. It parses UI/font/magnification/map options, opens the input file or stdin, loads map/fonts, initializes the screen, and starts page reading. It also implements a circular input buffer so the viewer can seek backward within recently read troff output.

Key behavior:
- Options: map file, font directory, debug, magnification, file tracking, x/y offsets, and number of views.
- `getc`, `getrune`, `ungetc`, `seekc`, `offsetc`, and `rdlinec` provide buffered byte/rune/line access.
- `track` mode watches input file modification time via screen event loop.

Integration points:
- Calls `readmapfile`, `loadfontname`, `mapscreen`, `clearscreen`, `readpage`.
- Shares buffer functions declared in `proof.h`.

Risks:
- Circular buffer is fixed at 100000 bytes; seeking older pages can fail.
- `strncpy(libfont, ...)` may leave `libfont` unterminated if option is too long.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/proof/main.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/proof/proof.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/proof/proof.h

Shared header for the `proof` previewer. It defines page/font/view constants, default magnification, shared renderer state, cursor declarations, font/screen/input function prototypes, and debug macro.

Integration points:
- Included by `font.c`, `htroff.c`, `main.c`, and `screen.c`.
- Declares the custom input API implemented in `main.c`.

Risks:
- Declares `extern int getc(void);`/`ungetc(void);`, intentionally shadowing standard names.
- Fixed constants constrain maximum fonts, sizes, pages, and views.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/proof/proof.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/proof/screen.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/proof/screen.c

Window, mouse, keyboard, menu, pan, resize, and confirmation handling for `proof`. It initializes draw/event, clears the screen, reads command strings from keyboard or mouse menus, supports tracking input-file changes, and defines cursors.

Key behavior:
- `getcmdstr` waits for mouse, keyboard, resize, or tracking timer events.
- Button 3 menu supports next, previous, page n, repaint, zoom, pan, and quit.
- `pan` moves screen contents interactively and updates `xyoffset`.
- `confirm` uses a special cursor and matching mouse button for dangerous menu entries.

Integration points:
- Uses Plan 9 `draw`, `event`, `cursor`, and `Dir` APIs.
- Returns command strings consumed by `htroff.c::botpage`.

Risks:
- Keyboard command buffer is fixed at 100 chars.
- `screenprint` draws black text on screen without clearing its previous text area, so prompts can overpaint.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/proof/screen.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ps.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ps.c

Plan 9 process status command. It reads `/proc`, sorts process directories numerically, reads each `status` file, and prints user, pid, optional note id/runtime/priority fields, CPU times, memory, state, and command or full args.

Key behavior:
- Options: `-a` full args, `-p` priorities, `-n` note id, `-r` real runtime.
- `ps` reads `/proc/<pid>/status` and optionally `/proc/<pid>/noteid` and `/proc/<pid>/args`.
- `cmp` sorts by numeric process id.

Integration points:
- Depends on Plan 9 `/proc` file formats and `tokenize`.
- Uses `Biobuf` for stdout.

Risks:
- Status parsing assumes at least 12 tokens and exact field positions.
- Reads args into a fixed 256-byte buffer and truncates long command lines.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ps.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ptrap.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ptrap.c

9P filter filesystem for plumber ports. It mounts over `/mnt/plumb`, proxies underlying plumb files, and filters read messages by port regex and optional attribute regexes. Matching plumb messages are repacked and returned; nonmatching messages are consumed.

Key behavior:
- Parses arguments as `port regex [ +attr regex ... ] ...`, with `!` prefix for inversion.
- `ptrapwalk1/open/stat/wstat` proxy the underlying `/mnt/plumb/<port>` files.
- `ptrapread/write` delegate blocking I/O to reusable IO processes so the 9P server remains responsive.
- `filterread` reads partial plumb messages, unpacks them, applies filters, and buffers packed matching messages across reads.
- `flush` interrupts the IO process handling an old request.

Integration points:
- Uses Plan 9 `thread`, `9p`, `plumb`, and `regexp` libraries.
- Mounts via `threadpostmountsrv(..., "/mnt/plumb", MREPL | MCREATE)`.

Risks:
- Attribute filter inversion uses `f->attr->invert` instead of the current `a->invert`, so multiple attribute filters may apply the wrong invert flag.
- `fname` uses a static allocated path; safe for sequential use but not inherently thread-safe.
- Filtering consumes nonmatching plumb messages, which is intended but operationally significant.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ptrap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/pump.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/pump.c

Buffered copy tool using a shared-memory circular buffer between an input process and output process. It can write to stdout or a file, tune buffer/read/write sizes, prefill before output, sleep between output polls, and stop after a time-derived byte limit.

Key behavior:
- Allocates `kilo` KB ring buffer.
- `rfork(RFPROC|RFNOWAIT|RFNAMEG|RFMEM)` creates a shared-memory child for input.
- `doinput` reads files/stdin into the ring while respecting free space.
- `dooutput` writes available data while respecting output block size and optional limit.
- `arithlock` protects 64-bit counters `nin`/`nout`.

Integration points:
- Plan 9-specific `rfork`, `Lock`, and shared memory semantics.

Risks:
- Parent sets `done = 1` after `dooutput`, but with shared-memory concurrency, lifecycle ordering is subtle.
- The `-t` option multiplies by a hard-coded `10584000` “minutes” constant; semantics are not obvious.
- No condition variables; sleeps poll for progress.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/pump.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/pwd.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/pwd.c

Minimal print-working-directory command. It calls `getwd` into a 512-byte buffer, prints the path, and exits with `"getwd"` on failure.

Integration points:
- Standalone Plan 9 libc command.

Risks:
- Fixed 512-byte path buffer; very long paths fail through `getwd`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/pwd.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/qa/a.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/qa/a.h

Shared header for the `qa` assembler frontend, a Plan 9-style assembler targeting the architecture described by `../qc/q.out.h` with PowerPC-like registers/instructions. It defines symbol, input, address, and history structures plus global parser/lexer/output state.

Key contents:
- Constants for symbol table, include depth, IO buffers, macro state, hash size, and string sizes.
- `Sym`, `Io`, `Gen`, and `Hist` model symbols/macros, stacked input, generic operands, and file history.
- Global declarations include symbol hash, include paths, IO stacks, pc/pass state, output buffer, and assembler flags.
- Prototypes cover lexical input, macro handling, parser, symbol setup, output encoding, history emission, and top-level assembly.

Integration points:
- Included by `a.y` and companion assembler implementation files in `qa`.
- Depends on generated/architecture constants from `../qc/q.out.h`.

Risks:
- Heavy use of globals and `EXTERN` convention mirrors old Plan 9 compiler code.
- Fixed buffer/include/macro limits constrain accepted assembly.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/qa/a.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/qa/a.y -->
# File Research: sources/os/plan9/9front/sys/src/cmd/qa/a.y

Yacc grammar for the `qa` assembler. It parses labels, assignments, scheduler directives, instructions, operands, constants, expressions, and addressing modes, then emits encoded instructions through `outcode` or `outgcode`.

Key behavior:
- Supports integer/byte moves, floating load/store/convert/compare/add/MA, condition-register moves/ops, segment/MSR/SPR moves, branches, traps, rotate-and-mask, indexed load/store, NOP, WORD, END, TEXT/GLOBL, DATA, and RETURN forms.
- Builds `Gen` operands for registers, FP registers, condition registers, FPSCR, special registers, segment registers, immediates, string/floating constants, branches, names, and register-offset addresses.
- Resolves labels/variables and reports undefined labels on pass 2.
- Expression grammar supports unary signs/complement, arithmetic, shifts, bitwise ops, and parentheses.
- `mask` converts rotate-mask start/end fields into a 32-bit mask constant.

Integration points:
- Uses token values and operand constants from `a.h`/`q.out.h`.
- Output path is delegated to `outcode`/`outgcode`; lexical tokens come from the assembler lexer.

Risks:
- In `sreg: LR '(' con ')'`, the range check tests `$$` before assigning `$3`, so invalid-register diagnostics may be unreliable.
- Grammar is architecture-specific and tightly coupled to token classification from the lexer.
- Several optional comma productions accept legacy syntax that can make parse errors less explicit.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/qa/a.y -->