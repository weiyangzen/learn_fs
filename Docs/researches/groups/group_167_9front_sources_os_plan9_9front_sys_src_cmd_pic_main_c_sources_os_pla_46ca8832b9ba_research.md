# Group Research: group_167_9front_sources_os_plan9_9front_sys_src_cmd_pic_main_c_sources_os_pla_46ca8832b9ba

Scope: `Docs/research_subset_a.md` includes `sources/os/plan9/9front`, so all listed files are in scope. This grouped report covers Plan 9/9front command sources for `pic`, `plot`, `plumb`, `pipefile`, and PostScript utilities. These are mostly user-space document, graphics, and plumbing tools; the filesystem-relevant portion is strongest in `plumb/fsys.c`, which implements a user-space 9P service mounted at `/mnt/plumb`, and `pipefile.c`, which uses Plan 9 namespace binding around pipe devices.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/pic/main.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/pic/main.c

This is the top-level driver for the classic `pic` troff preprocessor. It owns global state for parsed objects, attributes, text strings, current drawing position, picture extents, errors, and default variable values.

Key behavior:
- Parses `-d` and `-V`, initializes default `pic` variables, object/text/attribute arrays, and a `pid` macro definition.
- `getdata()` streams troff input, copies ordinary lines, detects `.PS`, recursively handles `.PS < file`, invokes `yyparse()`, computes picture dimensions from bounding extrema and `scale`, emits `.PS`/drawing output/`.PE` only if parsing succeeded, and preserves `.lf` line directives.
- `reset()` frees per-picture object records, block symbol tables, and text strings, then restores parser/drawing state for the next picture.
- `setdefaults()`, `resetvar()`, and `checkscale()` manage built-in size variables such as `boxht`, `linewid`, `arrowht`, `maxpswid`, and `fillval`.

Important dependencies:
- Grammar and lexer tokens from `y.tab.h`.
- Object model and globals from `pic.h`.
- Output backend hooks `openpl`, `print`, `closepl`, and `printlf`.

Filesystem relevance:
- Reads input files and included `.PS < file` files with `fopen`.
- Emits transformed troff to standard output.
- No kernel/VFS logic, but it is part of Plan 9 user-space document tooling.

Implementation notes:
- Uses old-style C declarations and process-wide globals.
- Dynamic arrays grow with `grow()`.
- Fatal errors go through `ERROR ... FATAL`, which calls `yyerror` and exits.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/pic/main.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/pic/makefile -->
# File Research: sources/os/plan9/9front/sys/src/cmd/pic/makefile

This historical makefile builds the standalone `pic` preprocessor from yacc/lex output and C generator modules.

Key behavior:
- Defines object list including parser/lexer, object generators, input handling, loop handling, symbol table, and troff output backend.
- Uses `YFLAGS=-d` to generate token headers.
- Maintains `prevy.tab.h` by comparing and copying `y.tab.h`.
- Provides `bundle`, `bowell`, `clean`, and `install` targets.

Important details:
- Contains two `CC`/`CFLAGS` assignments, with the later `lcc` settings overriding the earlier generic `cc` settings.
- Installs `a.out` as `/usr/bin/pic` and strips it.

Filesystem relevance:
- Build/install script only.
- No runtime filesystem implementation.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/pic/makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/pic/misc.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/pic/misc.c

This file contains miscellaneous semantic helpers for `pic`: direction management, coordinate/component lookup, attribute construction, position arithmetic, object allocation, and bounding-box accumulation.

Key behavior:
- `setdir()` and `curdir()` translate between parser direction tokens and internal `hvmode`.
- `getcomp()` returns object properties such as x/y, width, height, and radius based on object type.
- Attribute helpers build typed `Attr` entries for numeric, object, integer, text, and variable attributes.
- Position helpers create places, interpolate between positions, offset/add/subtract positions, and resolve corners/anchors via `whatpos()`.
- `getlast()` and `getfirst()` locate previous or first objects of a requested type, skipping block internals appropriately.
- `getblk()`, `getblkvar()`, and `getblock()` access named entries inside block-local symbol tables.
- `makenode()` allocates variable-length `obj` records, assigns object indices and text ranges, and appends to `objlist`.
- `extreme()` updates global min/max picture coordinates.

Important dependencies:
- Object definitions and globals from `pic.h`.
- Token constants from `y.tab.h`.
- Symbol table layout from `pic.h` and `symtab.c`.

Implementation notes:
- `whatpos()` encodes geometric anchor semantics for boxes, blocks, text, arcs, circles, ellipses, lines, splines, arrows, moves, and places.
- `exprlist`/`sprintgen()` support `sprintf` expressions in the yacc grammar.
- Some diagnostics use old `%o` pointer formatting and old-style implicit-int functions.

Filesystem relevance:
- None directly; this is in-memory geometry and parser support.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/pic/misc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/pic/movegen.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/pic/movegen.c

This file implements generation of `MOVE` objects for `pic`.

Key behavior:
- Reads move-related attributes from the global `attr` list.
- Supports text attributes, `same`, directional moves, `to`, `by`, `from`, and `at`.
- Tracks previous move delta for `same`.
- Defaults movement to `movewid`/`moveht` in the current `hvmode`.
- Updates `curx`/`cury`, records extrema before and after the move, and creates a `MOVE` object.

Important dependencies:
- `getfval()` for default dimensions.
- `savetext()`, `extreme()`, and `makenode()`.
- Direction and token constants from `pic.h`/`y.tab.h`.

Filesystem relevance:
- None; pure in-memory object generation.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/pic/movegen.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/pic/pic.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/pic/pic.h

This is the central header for the `pic` preprocessor. It defines constants, object storage, yacc value types, symbol tables, input source stacks, argument stacks, parser globals, and function prototypes.

Key contents:
- Geometry and drawing constants: default dimensions, direction modes, arrow/fill/visibility bits, text alignment bits.
- `obj`: variable-length drawing object record with type, object index, mode, position, text range, attributes, block symbol table, dot/dash/fill values, and `o_val[]` payload.
- `YYSTYPE`: parser union carrying ints, strings, objects, doubles, or symbol table pointers.
- `symtab`: scoped variable/place/macro table.
- `Attr`, `Text`, `Src`, `Infile`, and `Arg` structures.
- Global declarations for object arrays, text arrays, attributes, current position, current direction, codegen state, extents, and parser stack state.
- Prototypes for generators, input/macro handling, symbol lookup, position math, attribute creation, output line directives, and math error wrappers.

Filesystem relevance:
- Defines `Infile` and input stack abstractions used by the parser and main driver.
- Otherwise no filesystem logic.

Implementation notes:
- Uses float storage (`ofloat`) for object payloads, even though many computations use double.
- Error macros expand into `sprintf` plus `yyerror`, with fatal paths calling `exit(1)`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/pic/pic.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/pic/picy.y -->
# File Research: sources/os/plan9/9front/sys/src/cmd/pic/picy.y

This yacc grammar defines the `pic` language syntax and semantic actions.

Key behavior:
- Declares tokens for drawing primitives, text/troff content, macros, variables, positions, directions, corners, attributes, comparisons, math functions, and statement terminators.
- Top-level grammar builds picture lists, primitive statements, assignments, direction changes, print/reset/copy/for/if statements, labels, and blocks.
- Attribute grammar converts parsed attributes into global `Attr` entries consumed by object generators.
- Position grammar supports named places, object corners, `here`, `last`, `nth`, block member references, coordinate pairs, arithmetic offsets, and interpolation.
- Expression grammar supports arithmetic, comparison, logical operators, assignment, dot-property access, block variable access, math functions, random, min/max, and int conversion.
- Text grammar supports quoted text, modifiers, and `sprintf`.

Important dependencies:
- Semantic routines from `misc.c`, `symtab.c`, `textgen.c`, `movegen.c`, and other object generator files.
- Global `codegen` flag is set when a primitive statement is seen.

Filesystem relevance:
- Grammar supports `copy` constructs that are implemented by input handling code outside this listed file.
- No direct filesystem operations in the grammar itself.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/pic/picy.y -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/pic/pltroff.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/pic/pltroff.c

This is the troff drawing backend for `pic`. It converts internal drawing coordinates to troff motions and `\D` drawing commands.

Key behavior:
- Maintains coordinate scaling from input extrema to requested output size.
- `openpl()` clamps output size to `maxpswid`/`maxpsht`, sets conversion state, emits diagnostic comments and `.PS`.
- `closepl()` returns position, emits spacing and `.PE`/`.PF` line, and restores fill mode.
- `move`, `hgoto`, `vgoto`, `hvflush`, and `flyback` manage troff horizontal/vertical positioning.
- Emits labels with alignment and vertical offsets.
- Draws lines, boxes, circles, ellipses, arcs, splines, dots, and arrowheads using troff device commands.
- `fillstart()`/`fillend()` emit PostScript escape hooks through troff `\X`.

Important dependencies:
- `getfval()` for output size constraints.
- `textshift`, `xscale`, `yscale`, and global extents.
- Math functions for arrow and rotation geometry.

Implementation notes:
- Defines a local `fabs()` despite including math.
- Some comments note device-specific assumptions and expensive flyback behavior.

Filesystem relevance:
- Writes troff/PostScript-compatible output to standard output only.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/pic/pltroff.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/pic/print.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/pic/print.c

This file walks parsed `pic` objects and calls backend drawing routines.

Key behavior:
- `print()` iterates `objlist` and dispatches by object type: troff, box, block, circle, ellipse, arc, line, arrow, spline, move, and text.
- Handles invisibility, fill, dotted/dashed styling, arrowheads, object text, and current backend position.
- `dotline()` renders dotted or dashed lines by subdividing geometry.
- `dotbox()` applies dotted/dashed line rendering to a rectangle.
- `dotext()` emits all text strings attached to an object with half-line vertical spacing.

Important dependencies:
- Backend functions from `pltroff.c`: `move`, `line`, `box`, `circle`, `ellipse`, `arc`, `spline`, `arrow`, `dot`, `troff`, `fillstart`, `fillend`, and `label`.
- Object attributes and flags from `pic.h`.

Implementation notes:
- Contains precedence-sensitive expressions such as `move(ox + isright(m) ? x1 : -x1, oy)` that reflect old code style and should be treated carefully if modified.
- Blocks are positioned and may carry text, but block body drawing is suppressed here.

Filesystem relevance:
- No filesystem operations; emits to backend.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/pic/print.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/pic/symtab.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/pic/symtab.c

This file implements scoped symbol table operations for `pic`.

Key behavior:
- `getvar()` looks up a variable/place and warns if absent.
- `getfval()` and `setfval()` read/write numeric variables.
- `makevar()` inserts or updates a name in the current parser stack frame.
- `lookup()` searches symbol tables from innermost stack frame outward.
- `freesymtab()` releases a symbol list and its names.
- `freedef()` removes a macro definition from the current scope.

Important dependencies:
- `stack[]` and `nstack` from parser/block context.
- `YYSTYPE` and `symtab` from `pic.h`.

Filesystem relevance:
- None; in-memory name binding only.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/pic/symtab.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/pic/textgen.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/pic/textgen.c

This file generates `TEXT` and `TROFF` objects and stores text payloads.

Key behavior:
- `textgen()` processes height, width, `with`, invisible, `at`, and text attributes.
- Computes text box size, default placement based on current direction, anchor adjustments, and extrema.
- Creates a `TEXT` object with width/height payload and updates current position after placement.
- `troffgen()` stores raw troff command strings as text and creates a `TROFF` object.
- `savetext()` appends text records to the global `text` array, growing it as needed.

Important dependencies:
- `attr`, `text`, `curx`, `cury`, and `hvmode` globals.
- `getfval()`, `extreme()`, `makenode()`, and `grow()`.

Implementation notes:
- `prevh` and `prevw` are assigned but not otherwise used in this file.
- Text string ownership is transferred to global `text[]` and later freed by `reset()`.

Filesystem relevance:
- None.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/pic/textgen.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/pipefile.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/pipefile.c

This Plan 9 utility overlays a file path with a pipe endpoint and connects read/write commands to the original file.

Key behavior:
- Usage: `pipefile [-d] [-r command] [-w command] file`.
- Opens the target file either as separate read/write descriptors or a duplicated `ORDWR` descriptor under `-d`.
- Binds a pipe device `#|` at `/n/temp`, then binds `/n/temp/data` over the target file path.
- Opens `/n/temp/data1` read/write ends and spawns rc commands:
  - write command receives pipe read end as stdin and original file write descriptor as stdout.
  - read command receives original file read descriptor as stdin and pipe write end as stdout.
- Unmounts the temporary binding after setup.

Filesystem relevance:
- Directly uses Plan 9 namespace operations: `bind`, `unmount`, `open`, and pipe device `#|`.
- Demonstrates per-process namespace manipulation to interpose a pipe-backed file.
- This is the most filesystem/namespace-focused small utility in this group.

Implementation notes:
- `connect()` forks with `rfork(RFPROC|RFFDG|RFREND|RFNOWAIT)`, redirects descriptors, and runs `/bin/rc -c`.
- Defaults missing read/write command to `/bin/cat`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/pipefile.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/plot/libplot/box.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/plot/libplot/box.c

This libplot primitive draws an outlined rectangle.

Key behavior:
- Moves to `(x0, y0)`.
- Draws vectors around the four corners and closes back at the start.

Dependencies:
- `move()` and `vec()` from libplot state/drawing code.
- `mplot.h` coordinate environment.

Filesystem relevance:
- None; drawing primitive only.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/plot/libplot/box.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/plot/libplot/cfill.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/plot/libplot/cfill.c

This libplot primitive sets the background/fill color.

Key behavior:
- Converts a color string with `bcolor()`.
- If conversion returns a non-negative color value, stores it in `e1->backgr`.

Filesystem relevance:
- None.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/plot/libplot/cfill.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/plot/libplot/circ.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/plot/libplot/circ.c

This libplot primitive draws an unfilled circle.

Key behavior:
- Converts center coordinates with `SCX`/`SCY`.
- Converts radius with `SCR`, accepting negative radius by negating it.
- Calls `m_circ()` with current foreground color.

Filesystem relevance:
- None.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/plot/libplot/circ.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/plot/libplot/closepl.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/plot/libplot/closepl.c

This primitive closes/finishes a plot session.

Key behavior:
- `closepl()` calls `m_finish()`, which swaps/flushed buffers in the machine-dependent draw backend.

Filesystem relevance:
- None.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/plot/libplot/closepl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/plot/libplot/color.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/plot/libplot/color.c

This primitive sets the foreground color.

Key behavior:
- Converts the input color string through `bcolor()`.
- Stores the result in `e1->foregr`.

Filesystem relevance:
- None.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/plot/libplot/color.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/plot/libplot/disk.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/plot/libplot/disk.c

This primitive draws a filled circle/disc.

Key behavior:
- Converts center and radius to device coordinates.
- Calls `m_disc()` with the current foreground color.

Filesystem relevance:
- None.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/plot/libplot/disk.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/plot/libplot/doublebuffer.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/plot/libplot/doublebuffer.c

This primitive enables double-buffered drawing.

Key behavior:
- Calls `m_dblbuf()`, which sets a backend buffer flag.

Filesystem relevance:
- None.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/plot/libplot/doublebuffer.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/plot/libplot/dpoint.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/plot/libplot/dpoint.c

This primitive draws a single point and updates current position.

Key behavior:
- Calls `m_dpt(x, y)` to draw a pixel at transformed coordinates.
- Calls `move(x, y)` so current plot position matches the point.

Filesystem relevance:
- None.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/plot/libplot/dpoint.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/plot/libplot/erase.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/plot/libplot/erase.c

This primitive clears the plotting window.

Key behavior:
- Swaps the buffer.
- Clears the clipping rectangle to `e1->backgr` using `m_clrwin()`.

Filesystem relevance:
- None.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/plot/libplot/erase.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/plot/libplot/fill.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/plot/libplot/fill.c

This file implements polygon filling for libplot.

Key behavior:
- Defines an edge table and scanline polygon fill algorithm.
- Supports winding rules internally, with exported `fill()` using odd winding.
- Converts input polygon coordinate lists through `SCX`/`SCY`.
- Builds active edge lists per screen scanline, clips to screen bounds, and draws horizontal spans using Plan 9 `line()` with the current foreground color.
- Handles horizontal edges, offscreen clipping, fractional x stepping, and winding transitions.

Important dependencies:
- `screen`, `getcolor()`, and Plan 9 draw primitives.
- `mplot.h` globals and coordinate macros.

Filesystem relevance:
- None; graphics rasterization only.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/plot/libplot/fill.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/plot/libplot/frame.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/plot/libplot/frame.c

This primitive sets a subframe within the plotting coordinate environment.

Key behavior:
- Computes `e1` frame left/bottom/side dimensions from `e0` and normalized frame coordinates.
- Adjusts scaling factors and drawing quantum based on new frame dimensions.
- Enforces a minimum quantum of `0.01`.

Filesystem relevance:
- None.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/plot/libplot/frame.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/plot/libplot/grade.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/plot/libplot/grade.c

This primitive sets curve approximation grade.

Key behavior:
- Assigns the provided value to `e1->grade`.
- Used by curve routines such as `parabola()` to control subdivision step size.

Filesystem relevance:
- None.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/plot/libplot/grade.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/plot/libplot/line.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/plot/libplot/line.c

This primitive draws a line segment.

Key behavior:
- Moves to the first endpoint.
- Draws a vector to the second endpoint.

Filesystem relevance:
- None.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/plot/libplot/line.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/plot/libplot/machdep.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/plot/libplot/machdep.c

This is the Plan 9 draw backend for libplot.

Key behavior:
- Maintains an offscreen image and optional double-buffer state.
- Provides backend functions to clear windows, draw circles/discs, draw text, draw points, draw vectors, initialize display/window state, finish/swap buffers, enable double buffering, and cache solid-color images.
- `m_initialize()` calls `initdraw`, allocates an inset offscreen image, sets clipping bounds, and chooses a centered square mapping area.
- `getcolor()` caches up to 32 single-pixel `Image` objects keyed by RGBA value.

Important dependencies:
- Plan 9 draw library: `Image`, `screen`, `display`, `draw`, `line`, `ellipse`, `fillellipse`, `stringn`, `allocimage`, `flushimage`.
- Coordinate state from `mplot.h`.

Filesystem relevance:
- Uses draw device initialization implicitly through Plan 9 graphics APIs, but no file/path logic except display attachment internals.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/plot/libplot/machdep.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/plot/libplot/move.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/plot/libplot/move.c

This primitive updates current plotting position.

Key behavior:
- Stores given x/y in `e1->copyx` and `e1->copyy`.
- Does not draw.

Filesystem relevance:
- None.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/plot/libplot/move.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/plot/libplot/mplot.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/plot/libplot/mplot.h

This is the internal header for Plan 9 libplot.

Key contents:
- Includes Plan 9 system, draw, and event headers.
- Coordinate conversion macros `SCX`, `SCY`, and `SCR`.
- `penvir` plotting environment structure with frame, scale, current point, quantum, grade, pen settings, and colors.
- Global clipping and mapping rectangle variables.
- Prototypes for public plot functions via `../plot.h` and backend functions in `machdep.c`.

Filesystem relevance:
- None directly.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/plot/libplot/mplot.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/plot/libplot/openpl.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/plot/libplot/openpl.c

This primitive initializes plotting.

Key behavior:
- Calls `m_initialize()`.
- Initializes base environment `e0` from map bounds.
- Copies `e0` to active environment `e1`.
- Moves current point to `(0, 0)`.

Filesystem relevance:
- None.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/plot/libplot/openpl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/plot/libplot/parabola.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/plot/libplot/parabola.c

This primitive approximates a parabolic curve segment.

Key behavior:
- Computes distances from endpoints to control point.
- If too small relative to drawing quantum, draws a straight line.
- Otherwise samples the quadratic in two stages using `e1->quantum` and `e1->grade`, emitting vectors between sample points.

Filesystem relevance:
- None.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/plot/libplot/parabola.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/plot/libplot/pen.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/plot/libplot/pen.c

This primitive is a no-op pen selector.

Key behavior:
- Accepts a string argument and marks it used.
- Comment notes older behavior may have treated pen as color.

Filesystem relevance:
- None.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/plot/libplot/pen.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/plot/libplot/poly.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/plot/libplot/poly.c

This primitive outlines one or more polylines/polygons.

Key behavior:
- Iterates vertex count array and point arrays.
- Moves to the first point of each list, then emits vectors through remaining vertices.

Filesystem relevance:
- None.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/plot/libplot/poly.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/plot/libplot/ppause.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/plot/libplot/ppause.c

This primitive pauses plot execution.

Key behavior:
- Reads four bytes from standard input.
- Calls `erase()` afterward.

Filesystem relevance:
- Reads stdin only.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/plot/libplot/ppause.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/plot/libplot/pprompt.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/plot/libplot/pprompt.c

This primitive emits an interactive prompt.

Key behavior:
- Writes `:` to stderr.

Filesystem relevance:
- Standard error only.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/plot/libplot/pprompt.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/plot/libplot/range.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/plot/libplot/range.c

This primitive sets the user-coordinate range.

Key behavior:
- Stores new minimum x/y.
- Computes x/y scale from frame side dimensions and requested coordinate extents.
- Recomputes drawing quantum and clamps it to `0.01`.

Filesystem relevance:
- None.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/plot/libplot/range.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/plot/libplot/rarc.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/plot/libplot/rarc.c

This primitive approximates circular arcs.

Key behavior:
- Computes radius and angular span from endpoints and center.
- Negative radius draws counterclockwise.
- Uses `e1->quantum` to choose angular step size, capped at about pi/4.
- Emits vectors by iterating a rotation difference equation.

Filesystem relevance:
- None.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/plot/libplot/rarc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/plot/libplot/restore.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/plot/libplot/restore.c

This primitive restores a saved plotting environment.

Key behavior:
- Decrements the environment pointer `e1`.
- Moves current position to the restored `copyx/copyy`.

Filesystem relevance:
- None.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/plot/libplot/restore.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/plot/libplot/rmove.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/plot/libplot/rmove.c

This primitive performs relative move.

Key behavior:
- Adds deltas to current copy position.
- Calls `move()` to update current position without drawing.

Filesystem relevance:
- None.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/plot/libplot/rmove.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/plot/libplot/rvec.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/plot/libplot/rvec.c

This primitive performs relative vector drawing.

Key behavior:
- Adds deltas to current copy position.
- Calls `vec()` to draw from old current point to the new point.

Filesystem relevance:
- None.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/plot/libplot/rvec.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/plot/libplot/save.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/plot/libplot/save.c

This primitive saves the current plotting environment.

Key behavior:
- Copies `e1` to `e1 + 1` with `sscpy()`.
- Advances `e1` to the saved environment slot.

Filesystem relevance:
- None.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/plot/libplot/save.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/plot/libplot/sbox.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/plot/libplot/sbox.c

This primitive clears/fills a rectangular screen box.

Key behavior:
- Converts endpoints to screen coordinates.
- Normalizes min/max ordering.
- Clips to current clipping rectangle.
- Calls `m_clrwin()` with background color if rectangle is non-empty.

Filesystem relevance:
- None.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/plot/libplot/sbox.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/plot/libplot/spline.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/plot/libplot/spline.c

This file implements spline drawing.

Key behavior:
- `splin()` handles one or more control-point lists.
- For fewer than three points, draws a straight line.
- For closed mode, connects endpoints with parabolic segments.
- For open modes, optionally doubles endpoints and draws midpoint-to-midpoint parabolic segments.
- Uses `parabola()` for each approximated segment.

Filesystem relevance:
- None.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/plot/libplot/spline.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/plot/libplot/subr.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/plot/libplot/subr.c

This file contains shared libplot environment data and color/string helpers.

Key behavior:
- Defines the `E` environment array and active pointers `e0`/`e1`.
- `bcolor()` parses color specifiers:
  - numeric color map indexes,
  - single-letter standard colors,
  - raw `R` values,
  - `G` pen gap and `A` pen slant side effects.
- `sscpy()` copies plotting environment fields.
- `idle()` and `ptype()` are stubs.

Filesystem relevance:
- None.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/plot/libplot/subr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/plot/libplot/text.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/plot/libplot/text.c

This primitive draws text at the current plotting point.

Key behavior:
- Parses leading alignment escapes `\C`, `\R`, `\L`, and line separator `\n`.
- Splits multiline text and draws each segment using `m_text()`.
- Updates current y position for following lines after text rendering.

Filesystem relevance:
- None.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/plot/libplot/text.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/plot/libplot/vec.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/plot/libplot/vec.c

This primitive draws a clipped vector from current point to a new point.

Key behavior:
- Converts current and target points to screen coordinates.
- Rejects huge transformed coordinates.
- Updates current copy position before clipping.
- Uses Cohen-Sutherland style clipping against the clip rectangle.
- Calls `m_vector()` for visible clipped segments.

Filesystem relevance:
- None.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/plot/libplot/vec.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/plot/libplot/whoami.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/plot/libplot/whoami.c

This file returns an identifier string for the plotting backend.

Key behavior:
- `whoami()` returns `"ramtek"`.

Filesystem relevance:
- None.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/plot/libplot/whoami.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/plot/plot.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/plot/plot.c

This is the Plan 9 `plot` command interpreter. It reads plot-language commands from files/stdin/server input and invokes libplot primitives.

Key behavior:
- Defines command table mapping textual command prefixes to enum operations.
- Maintains define/call libraries, input stack, numeric argument arrays, polygon point arrays, and string argument buffer.
- `threadmain()` opens the plot display, starts mouse/keyboard handling, parses command-line options, processes files or stdin, and keeps the window alive.
- Mouse/keyboard thread supports right-button menu exit and `q`, delete, or EOF quit.
- `process()` tokenizes commands, parses arguments, and dispatches to libplot functions.
- Supports comments, command abbreviations, numeric arguments, string arguments, polygon lists, macro definitions, `call`, and `include`.
- `server()` attempts to publish a pipe endpoint in `/srv/plot`.

Filesystem relevance:
- Opens input files with `Bopen`.
- Includes other plot files.
- Optional server mode creates `/srv/plot` and returns a pipe read fd.
- Uses Plan 9 draw/window device APIs through libplot.
- Not a filesystem implementation, but it interacts with `/srv` and file inputs.

Implementation notes:
- Defines local `isalpha`/`isdigit`/etc. helpers instead of relying on libc ctype.
- Uses a fixed define library size and fixed numeric/point buffers.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/plot/plot.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/plot/plot.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/plot/plot.h

This header declares the libplot public interface used by `plot.c` and included by `mplot.h`.

Key contents:
- Prototypes for primitives including arc, box, fill, circle, close/open, color, disk, point, erase, frame, grade, line, move, parabola, pen, poly, pause, range, restore, relative move/vector, save, sbox, spline, text, vector, backend identity, and double buffering.

Filesystem relevance:
- None.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/plot/plot.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/plumb/fsys.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/plumb/fsys.c

This is the user-space 9P filesystem server for `plumber`, mounted at `/mnt/plumb`.

Key behavior:
- Exposes directory entries:
  - `.`
  - `rules`
  - `send`
  - dynamically declared per-port files.
- Creates a pipe with close-on-exec behavior, publishes one end in `/srv/plumb.$user.$pid` or `/srv/$srvname`, and mounts the other end at `/mnt/plumb`.
- Implements 9P handlers for version, auth, attach, walk, open, create, read, write, clunk, remove, stat, wstat, and flush.
- Maintains fid table, open-fid lists per port, read queues, send queues, hold queues, and rule-writer refcount.
- `addport()` dynamically adds plumb ports and records them in `ports`.
- Writing `rules` incrementally parses/replaces rules through `writerules()`.
- Writing `send` accepts packed plumb messages, handles partial message assembly, applies rules, and dispatches messages to destination ports.
- Reading a port queues a read request and drains pending sends.
- If a destination port has no clients, `startup()` may launch a client and optionally hold the message until the port opens.

Filesystem/VFS relevance:
- Strongly relevant: implements a full user-space synthetic filesystem using 9P messages and Plan 9 mount service conventions.
- Demonstrates `/srv` publication, `/mnt/plumb` mount, synthetic directory walking, stat generation, per-fid state, queued reads/writes, and permission enforcement.
- Uses Plan 9 pipe device `#|` to create the mount channel.

Implementation notes:
- Serializes queue operations with `QLock queue`.
- Uses `readlock` and idle process count to allow multiple fsys server procs.
- `messagesize` is negotiated by 9P version and used for buffers.
- `Qrules` write open is single-writer via `rulesref`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/plumb/fsys.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/plumb/match.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/plumb/match.c

This file evaluates plumb rules against messages and starts clients/actions.

Key behavior:
- Implements rule verbs:
  - `is`
  - `matches`
  - `isfile`
  - `isdir`
  - `set`
  - `add`
  - `delete`
- Regex matches are full-string except click-based data matches, which find a regex span containing the clicked character offset.
- Captures regex submatches into `Exec.match[0..9]`.
- File tests resolve relative paths against message working directory.
- `rewrite()` removes click attributes and can replace data with matched text.
- `matchruleset()` applies all pattern rules, assigns destination port if missing, and returns an `Exec` context on success.
- `startup()` builds argv from a `plumb start` or `plumb client` action and launches it in a new proc.
- `execproc()` redirects stdin from `/dev/null`, tries the command directly, then `/bin/<cmd>`.

Filesystem relevance:
- Uses `dirstat` to test files/directories.
- Launches clients based on filesystem paths and message routing.
- Works with `fsys.c` dispatch but does not implement 9P itself.

Implementation notes:
- `buildargv()` expands blank-terminated arguments with quoting rules from `rules.c`.
- `stackargv()` copies argv strings to a fixed stack buffer before exec to avoid leaks across proc exec path.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/plumb/match.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/plumb/plumb.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/plumb/plumb.c

This is the command-line sender for plumb messages.

Key behavior:
- Builds a `Plumbmsg` from flags:
  - `-a` attributes
  - `-d` destination
  - `-i` read data from stdin
  - `-t`/`-k` type
  - `-p` explicit plumb file
  - `-s` source
  - `-w` working directory
- Defaults source to `plumb`, type to `text`, and working directory to `getwd`.
- Opens explicit plumb file or `/mnt/plumb/send` via `plumbopen("send", OWRITE)`.
- Sends stdin data as one message under `-i`, adding default `action=showdata` if missing.
- Otherwise sends each command-line argument as separate message data.

Filesystem relevance:
- Opens the plumb send file and writes packed plumb messages through libplumb.
- Uses current working directory in messages.

Implementation notes:
- `m.ndata = -1` for argv string data lets libplumb infer length.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/plumb/plumb.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/plumb/plumber.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/plumb/plumber.c

This is the main program for the `plumber` service.

Key behavior:
- Parses `-p plumbfile` and `-s srvname`.
- Reads `$user` and `$home`, defaulting rules file to `$home/lib/plumbing`.
- Opens and parses rules with `readrules()`.
- Starts a child proc that creates ports, starts the 9P filesystem, and signals readiness.
- Provides fatal error and parse error reporting.
- Provides allocation wrappers `emalloc`, `erealloc`, and `estrdup`.

Filesystem relevance:
- Reads plumbing rule file.
- Starts the mounted synthetic plumb filesystem through `startfsys()`.

Implementation notes:
- Uses `setjmp`/`longjmp` for parse error recovery.
- Main thread exits after launching service process so the command returns to user.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/plumb/plumber.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/plumb/plumber.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/plumb/plumber.h

This header defines plumber rule/action structures, enums, global service state, and cross-file prototypes.

Key contents:
- Object enum: `arg`, `attr`, `data`, `dst`, `plumb`, `src`, `type`, `wdir`.
- Verb enum: `add`, `client`, `delete`, `is`, `isdir`, `isfile`, `matches`, `set`, `start`, `to`.
- `Rule`: object, verb, raw argument, quote-expanded argument, optional compiled regex.
- `Ruleset`: pattern/action rule arrays and optional port.
- `Exec`: matched message, regex captures, click/match range state, client-hold flags, and derived file/dir variables.
- Prototypes for parsing, matching, startup, filesystem start, port management, expansion, and cleanup.
- Global declarations for rules, user, home, parse jump buffer, error string, ports, and service name.

Filesystem relevance:
- Defines cross-module API for the plumb synthetic filesystem and rule dispatch.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/plumb/plumber.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/plumb/rules.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/plumb/rules.c

This file parses, expands, prints, and incrementally updates plumber rule files.

Key behavior:
- Maintains an input stack for files or string fragments, with include-depth guard.
- Supports variable assignment, `include` statements, comments, blank-line separated rulesets, and port declarations.
- `expand()` handles quote processing and `$` variables such as regex captures, `src`, `dst`, `dir`, `attr`, `data`, `file`, `type`, and `wdir`.
- `parserule()` validates object/verb combinations and compiles regexes for `matches`.
- `readruleset()` groups pattern rules and plumb actions, handles `plumb to` port declarations, enforces one start/client action per ruleset, and registers declared ports.
- `readrules()` parses an entire rules file.
- `printrules()` serializes current variables, ports, and rules.
- `writerules()` supports incremental writes to `/mnt/plumb/rules`, parsing complete rules as they arrive and finalizing on close.

Filesystem relevance:
- Reads included rule files, including fallback under `/sys/lib/plumb`.
- Serves the contents of the synthetic `rules` file through `printrules()`/`writerules()`.
- Integral to the `plumb` 9P service behavior.

Implementation notes:
- Variables store both raw and quote-expanded values.
- `morerules()` uses a blank-line heuristic to parse complete rules during partial writes.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/plumb/rules.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/postscript/buildtables/buildtables.mk -->
# File Research: sources/os/plan9/9front/sys/src/cmd/postscript/buildtables/buildtables.mk

This makefile builds and installs the `buildtables` shell script for PostScript font table generation.

Key behavior:
- Substitutes configured `FONTDIR`, `POSTBIN`, and `POSTLIB` into `buildtables.sh`.
- Installs the generated script and man page.
- Provides `changes` target to rewrite makefile and man page defaults.

Filesystem relevance:
- Build/install file operations only.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/postscript/buildtables/buildtables.mk -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/postscript/buildtables/buildtables.sh -->
# File Research: sources/os/plan9/9front/sys/src/cmd/postscript/buildtables/buildtables.sh

This shell script builds troff font width tables or device descriptions by querying a PostScript printer.

Key behavior:
- Parses options for font dir, host, shell library, device, baud rate, line, and trofftable options.
- Requires either a device or shell library.
- If no table arguments are given, sources the shell library and uses `AllTables`.
- Runs `trofftable` to produce PostScript table programs.
- If a serial line is specified, sends the program to the printer through `postio` and captures output as the table.

Filesystem relevance:
- Reads shell library files and writes generated `.ps` and table files.
- No filesystem implementation.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/postscript/buildtables/buildtables.sh -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/postscript/common/bbox.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/postscript/common/bbox.c

This shared PostScript utility code tracks and writes bounding boxes.

Key behavior:
- Maintains current page `bbox`, document `docbbox`, and current transformation matrix `ctm`.
- `cover()` expands current bbox to include a user-space point.
- `writebbox()` transforms the bbox to default coordinates, adds slop, writes the DSC bounding-box comment, and updates/reset state.
- `resetbbox()` folds current page bbox into document bbox when output occurred.
- `scale()`, `translate()`, `rotate()`, and `concat()` update the transformation matrix.

Filesystem relevance:
- Writes to a provided `FILE *`.
- No filesystem-specific behavior.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/postscript/common/bbox.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/postscript/common/comments.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/postscript/common/comments.h

This header defines PostScript Document Structuring Convention comment strings and related non-standard comments.

Key contents:
- File headers such as `%!PS`, `%!PS-Adobe-2.0`, EPS, query, and exitserver forms.
- Header comments: title, creator, creation date, bounding box, pages, document fonts/files/procsets/paper requirements.
- Body comments: setup, documents, files, procsets, binary, paper size, features, trailer.
- Page comments: page, page fonts/files/bounding box, page setup, object begin/end.
- Resource comments: include font/procset/file, execute file, change font, paper/feature comments.
- Non-standard comments used by these tools: script/global/endpage/forms/version.

Filesystem relevance:
- None; constants only.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/postscript/common/comments.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/postscript/common/common.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/postscript/common/common.c

This Plan 9-flavored shared support file provides text escaping, page filtering, page lifecycle output, file copying, allocation, and error reporting for PostScript translators.

Key behavior:
- Defines `charcode[256]`, mapping byte values to PostScript string-safe encodings.
- `pagelist()` parses page selections into a bitmap.
- `pageon()` decides whether the current page should be emitted and temporarily suppresses debug output for skipped pages.
- `startstring()`/`endstring()` group emitted text into PostScript string commands at current h/v position.
- `startpage()` and `endpage()` emit DSC page markers and page setup/showpage/restore code.
- `cat()` copies a file to `Bstdout`.
- `galloc()` wraps realloc with fatal exit on failure.
- `error()` prints formatted diagnostics with program/input line context and exits on fatal.

Filesystem relevance:
- Reads files through `Bopen`/`Bread` in `cat()`.
- Shared translator utility, not a filesystem implementation.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/postscript/common/common.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/postscript/common/common.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/postscript/common/common.h

This header declares common Plan 9 PostScript translator state and helpers.

Key contents:
- Severity constants and Boolean values.
- Rune group/char extraction macros.
- Font table sizes.
- Extern declarations for program/input state, page counters, current font, h/v position, and Bio stdout/stderr.
- `strtab` structure and `charcode` table declaration.
- Prototypes for page filtering, string/page lifecycle, file copy, field parsing, allocation, and page-list parsing.

Filesystem relevance:
- Declares `cat()` helper for file copying.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/postscript/common/common.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/postscript/common/ext.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/postscript/common/ext.h

This header declares global variables shared by older PostScript translator tools.

Key contents:
- Global argc/argv.
- Exit/debug/ignore state.
- Line and byte position tracking.
- Program name, temp file, and font encoding.
- Bounding-box settings and page dimensions.
- Input/output encoding modes.
- `getopt` globals and `interrupt()`/`tempnam()` declarations.

Filesystem relevance:
- Declares `temp_file` and `tempnam()` used by tools that create temporary files.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/postscript/common/ext.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/postscript/common/gen.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/postscript/common/gen.h

This header defines general constants for the PostScript translator suite.

Key contents:
- Program version.
- Fatality/debug booleans.
- Byte masks, points-per-inch, pi, encoding constants.
- Default page geometry and resolution for bounding-box calculations.
- Utility macros `ABS`, `MIN`, and `MAX`.
- `DOROUND` setting for optional page rounding prologue inclusion.

Filesystem relevance:
- None.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/postscript/common/gen.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/postscript/common/getopt.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/postscript/common/getopt.c

This file provides a portable `getopt()` implementation for the older PostScript tools.

Key behavior:
- Maintains `opterr`, `optind`, `optopt`, and `optarg`.
- Parses grouped short options and options requiring arguments.
- Handles `--` end-of-options.
- Reports illegal options and missing arguments to stderr when `opterr` is enabled.

Filesystem relevance:
- None.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/postscript/common/getopt.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/postscript/common/glob.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/postscript/common/glob.c

This file defines global variables used by older PostScript translators.

Key contents:
- Global argc/argv.
- Exit/debug/ignore flags.
- Line and byte position counters.
- Program name, temporary file path, and font encoding pointer.
- Bounding-box enable flag and default page dimensions.
- Input/output encoding mode defaults.

Filesystem relevance:
- Provides `temp_file` global used by tools that create and clean up temporary files.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/postscript/common/glob.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/postscript/common/misc.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/postscript/common/misc.c

This shared utility file supports older PostScript translator programs.

Key behavior:
- `out_list()` parses nroff/troff-style page ranges into `olist`.
- `in_olist()` tests whether a page should be processed.
- `setencoding()` emits an encoding file from `ENCODINGDIR`.
- `cat()` copies a file to stdout with POSIX-style file descriptors.
- `str_convert()` parses integer substrings.
- `error()` prints diagnostics with line/byte context and handles fatal cleanup.
- `interrupt()` removes temp file and exits.

Filesystem relevance:
- Opens and reads encoding/prologue files.
- Removes temporary files on fatal errors or signals.
- Utility support only.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/postscript/common/misc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/postscript/common/path.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/postscript/common/path.h

This header centralizes Plan 9 pathnames for PostScript prologues, font directories, encoding files, request files, and temp directory.

Key contents:
- Prologue paths under `/sys/lib/postscript/prologues`.
- Troff font directory `/sys/lib/troff/font`.
- Host font directory `/sys/lib/postscript/font`.
- Encoding/prologue directory and `/tmp`.

Filesystem relevance:
- Important path configuration for all PostScript translator tools.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/postscript/common/path.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/postscript/common/request.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/postscript/common/request.c

This file implements special PostScript request insertion.

Key behavior:
- `saverequest()` parses request specs of the form `request`, `request:page`, or `request:page:file`.
- `writerequest()` emits all requests matching a page number.
- `dumprequest()` scans a request file for `@name` sections and copies associated PostScript lines until the next keyword.

Filesystem relevance:
- Reads request files, defaulting to `REQUESTFILE`.
- No filesystem implementation.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/postscript/common/request.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/postscript/common/request.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/postscript/common/request.h

This header defines the request table used by PostScript translators.

Key contents:
- `MAXREQUEST` set to 30.
- `Request` structure with wanted request name, page number, and lookup file.

Filesystem relevance:
- Request entries include file paths for lookup.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/postscript/common/request.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/postscript/common/tempnam.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/postscript/common/tempnam.c

This file provides a `tempnam()` implementation for V9/BSD/Plan 9 builds.

Key behavior:
- Validates directory access.
- Allocates a path string using directory, prefix, pid, and sequence counter.
- Loops until it finds a non-existing pathname or sequence limit.

Filesystem relevance:
- Uses `access()` and `stat()` to generate a temporary pathname.
- Contains a Plan 9-specific comment that write-access emulation has a race, so it checks only read/execute under `plan9`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/postscript/common/tempnam.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/postscript/config -->
# File Research: sources/os/plan9/9front/sys/src/cmd/postscript/config

This is a configuration file for the Plan 9 PostScript tool build.

Key contents:
- `SYSTEM=plan9`
- version setting
- root/bin path variables
- DK settings
- `ROUNDPAGE`
- font and PostScript library directories.

Filesystem relevance:
- Path/build configuration only.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/postscript/config -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/postscript/devpost.add/devpost.add.mk -->
# File Research: sources/os/plan9/9front/sys/src/cmd/postscript/devpost.add/devpost.add.mk

This makefile installs additional `devpost` font files.

Key behavior:
- Creates font directories if missing.
- Copies `FONTFILES` into `$(FONTDIR)/devpost`.
- Sets file modes, group, and owner.
- Provides `changes` target to rewrite embedded defaults.

Filesystem relevance:
- Install-time directory creation and file copying only.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/postscript/devpost.add/devpost.add.mk -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/postscript/download/download.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/postscript/download/download.c

This program prepends host-resident PostScript fonts requested by input documents.

Key behavior:
- Parses options for DSC comment name, forced full scan, map name, printer name, resident font list, host font directory, temp directory, debug, and ignore fatal errors.
- Reads a font map table mapping PostScript font names to host files.
- Optionally reads a resident-font list and marks those fonts already available.
- Scans input files for `%%DocumentFonts:` or configured comment plus continuation lines.
- Copies each mapped, not-yet-downloaded font file to stdout before copying input.
- For stdin, copies scanned input to a temp file so it can replay the complete input after font insertion.
- Handles `(atend)` by scanning farther.

Filesystem relevance:
- Opens map tables, resident font files, input files, font files, and temporary files.
- Cleans up temp files via shared interrupt/error handling.
- No filesystem implementation.

Implementation notes:
- `download.h` defines `Map` as font/file/downloaded state.
- Map comments begin with `%` and are stripped before tokenizing.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/postscript/download/download.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/postscript/download/download.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/postscript/download/download.h

This header defines the font map structure for `download.c`.

Key contents:
- `Map` holds:
  - requested PostScript font name,
  - host file path,
  - `downloaded` flag.
- Declares `Map *allocate()`.

Filesystem relevance:
- `file` field names host font files.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/postscript/download/download.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/postscript/g3p9bit/g3p9bit.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/postscript/g3p9bit/g3p9bit.c

This utility converts Group 3 fax data into Plan 9 bitmap format.

Key behavior:
- Supports `-g` simulated 2-bit gray horizontal compression and `-y` double scanlines.
- Reads input from file or stdin into memory.
- Recognizes several fax/container formats:
  - PC TIFF-like little-endian signature,
  - Digifax header,
  - textual header with `FDCS=`.
- Initializes white/black Huffman decode tables from included `wtab`/`btab` data.
- Synchronizes on EOL, decodes rows into a bitmap buffer, and writes a Plan 9 bitmap header plus raster data.
- Handles high-resolution mode by decoding twice as many lines and halving y count.

Filesystem relevance:
- Reads input file/stdin and writes bitmap to stdout.
- No filesystem implementation.

Implementation notes:
- Uses fixed maximum buffer sizes for input, lines, and dots.
- Bit reversal tables support differing bit order formats.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/postscript/g3p9bit/g3p9bit.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/postscript/mcolor/mcolor.mk -->
# File Research: sources/os/plan9/9front/sys/src/cmd/postscript/mcolor/mcolor.mk

This makefile installs a troff color macro package.

Key behavior:
- Copies `color.sr` to `tmac.color`.
- Installs `tmac.color` under `TMACDIR`.
- Provides clean/clobber and `changes` target to rewrite makefile/man defaults.

Filesystem relevance:
- Build/install file operations only.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/postscript/mcolor/mcolor.mk -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/postscript/misc/ibmfont.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/postscript/misc/ibmfont.c

This utility converts IBM PC downloadable PostScript font files into Unix-host usable form.

Key behavior:
- Parses options `-D` debug and `-I` ignore fatal.
- Processes stdin or listed files.
- Reads IBM font segments with marker byte 128, segment type, and 4-byte length.
- Type 1 segments are ASCII with CR converted to LF.
- Type 2 segments are binary data emitted as hex, line-wrapped.
- Type 3 ends the file.
- Other types are fatal.

Filesystem relevance:
- Opens input files and writes stdout.
- No filesystem implementation.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/postscript/misc/ibmfont.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/postscript/misc/laserbar.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/postscript/misc/laserbar.c

This utility emits PostScript for Code 39 barcodes.

Key behavior:
- Contains a Code 39 encoding table for ASCII characters.
- Optional standalone `main` parses rotation, offsets, scale, label, no-newpath, and showpage flags.
- `laserbar()` emits PostScript setup, font, bar drawing procedures, start/stop `*`, and encoded string bars.
- `barprt()` emits narrow/wide bar/space sequence and optional character labels.

Filesystem relevance:
- Writes PostScript to a `FILE *`/stdout.
- No filesystem implementation.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/postscript/misc/laserbar.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/postscript/misc/macfont.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/postscript/misc/macfont.c

This utility converts Macintosh downloadable PostScript font files into Unix-host usable form.

Key behavior:
- Parses `-D` debug and `-I` ignore fatal.
- Processes stdin or listed files.
- Reads blocks with 4-byte size, type byte, and null byte.
- Type 0 comment blocks are skipped.
- Type 1 ASCII text converts CR to LF.
- Type 2 binary data emits hex.
- Type 5 ends the file.
- Type 3/4 are unimplemented fatal cases.

Filesystem relevance:
- Opens input files and writes stdout.
- No filesystem implementation.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/postscript/misc/macfont.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/postscript/misc/pscrypt.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/postscript/misc/pscrypt.c

This utility implements Adobe Type 1/eexec and CharString encryption/decryption.

Key behavior:
- Defaults to decrypting hex eexec input to binary output, skipping first four decrypted bytes.
- `-e` switches to encryption with a supplied hex key.
- `-s` selects seed: eexec, show/CharString, or numeric.
- `-b`/`-x` choose binary/hex input; `-B`/`-X` choose binary/hex output.
- `-l` controls hex output line length; `-o` outputs all bytes.
- Implements the standard key update using constants 52845 and 22719.
- Reads stdin or listed files.

Filesystem relevance:
- Opens input files and writes stdout.
- No filesystem implementation.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/postscript/misc/pscrypt.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/postscript/p9bitpost/p9bitpost.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/postscript/p9bitpost/p9bitpost.c

This utility converts Plan 9 images to PostScript.

Key behavior:
- Parses options:
  - `-b dpi`
  - `-d` debug
  - `-m` x/y magnification
  - `-L` landscape
  - `-P` PostScript patch string
  - `-p` paper length/width in inches.
- Opens input image file or stdin.
- Initializes memimage support and reads a `Memimage`.
- Initializes PostScript library, applies options, and calls `image2psfile()`.

Filesystem relevance:
- Opens image file/stdin and writes PostScript to stdout.
- Uses Plan 9 image/memdraw libraries, not filesystem internals.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/postscript/p9bitpost/p9bitpost.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/postscript/p9bitpost/pslib.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/postscript/p9bitpost/pslib.c

This file implements the PostScript image-output library used by `p9bitpost`.

Key behavior:
- `psinit()` initializes output state.
- `preamble()` emits DSC header, prologue, image procedure, color space setup, ASCII85 image filter, magnification, rotation, and optional patch.
- `trailer()` emits page count and EOF.
- `printnewpage()` emits page/endpage wrappers.
- `cmap2ascii85()` converts four bytes to ASCII85, including `z` compression for zero groups.
- `imagebits()`:
  - handles sub-byte alignment by drawing into a temporary image if needed,
  - strips Plan 9 word-boundary padding,
  - inverts sample bytes,
  - emits ASCII85 image data with partial-group handling.
- `image2psfile()`:
  - converts unsupported high-depth image channels to 24-bit BGR,
  - computes scaling/placement for portrait or landscape and optional DPI,
  - emits page setup, image command, image bits, showpage, and trailer.
- `psopt()` sets magnification, landscape, and patch options by string name.

Filesystem relevance:
- Writes to a file descriptor wrapped by `Biobuf`.
- No filesystem implementation.

Implementation notes:
- Large sections of older Inferno/Tk text-printing code remain commented out.
- Supports grayscale, Plan 9 cmap8, and 24-bit color PostScript paths.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/postscript/p9bitpost/pslib.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/postscript/p9bitpost/pslib.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/postscript/p9bitpost/pslib.h

This header declares the p9bitpost PostScript image library API.

Key contents:
- `psinit()`
- `image2psfile()`
- `psopt()`
- External `paperlength` and `paperwidth`.

Filesystem relevance:
- None directly.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/postscript/p9bitpost/pslib.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/postscript/picpack/picpack.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/postscript/picpack/picpack.c

This utility packs external picture files inline into troff input for later `dpost` handling.

Key behavior:
- Recognizes picture inclusion macros at line starts, defaulting to `.BP` and `.PI`.
- `-k` replaces recognized key strings; `-q` suppresses missing-picture warnings; `-D`/`-I` set debug/ignore.
- Reads each input twice:
  - first pass finds picture references and emits each referenced picture once in transparent troff mode,
  - second pass copies original input.
- `inline()` emits `\!x X InlinePicture filename bytes` followed by escaped picture contents, prefixing each line with `\!`.
- Tracks already-inlined picture names in a temporary file to avoid duplicates.
- `copystdin()` copies stdin to an unlinked temp file because two passes are required.

Filesystem relevance:
- Opens input troff files, picture files, temporary files, and copies file descriptors.
- Uses temp-file bookkeeping to deduplicate inline assets.
- No filesystem implementation, but it is a file-packing preprocessor.

Implementation notes:
- Picture name parsing takes the second whitespace-separated string and strips at `(`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/postscript/picpack/picpack.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/postscript/picpack/picpack.mk -->
# File Research: sources/os/plan9/9front/sys/src/cmd/postscript/picpack/picpack.mk

This makefile builds and installs `picpack`.

Key behavior:
- Includes common PostScript support headers and objects from `../common`.
- Builds `picpack` from `picpack.o`, `glob.o`, `misc.o`, and `tempnam.o`.
- Installs binary and man page.
- Provides clean/clobber and `changes` targets.

Filesystem relevance:
- Build/install file operations only.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/postscript/picpack/picpack.mk -->