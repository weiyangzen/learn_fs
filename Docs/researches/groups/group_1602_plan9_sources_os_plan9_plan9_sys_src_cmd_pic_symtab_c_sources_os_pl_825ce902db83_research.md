# Group Research: group_1602_plan9_sources_os_plan9_plan9_sys_src_cmd_pic_symtab_c_sources_os_pl_825ce902db83

Scope checked against `Docs/research_subset_a.md`: all files are under `sources/os/plan9/plan9`, which is included in subset A. Every listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/pic/symtab.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/pic/symtab.c

Symbol-table support for the Plan 9 `pic` preprocessor.

Key responsibilities:
- Looks up variables/place names across the active block stack.
- Gets and sets numeric variable values stored in `YYSTYPE`.
- Creates or updates symbols in the current stack frame.
- Frees entire symbol tables and individual macro definitions.

Important behavior:
- `lookup()` searches from innermost stack frame down to global scope.
- `makevar()` assumes names are static or allocated by `tostring()`, then stores the pointer directly.
- `freedef()` only removes symbols of type `DEFNAME`.

Dependencies:
- Uses `pic.h`, `y.tab.h`, parser globals `stack` and `nstack`, and `ERROR` diagnostics.

Notable risks:
- Ownership is implicit: `freesymtab()` always frees `s_name`, so callers must not pass unowned transient strings.
- `getvar()` returns a static zero-ish fallback after warning, which can hide missing variable errors.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/pic/symtab.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/pic/textgen.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/pic/textgen.c

Text-object generation for Plan 9 `pic`.

Key responsibilities:
- Builds `TEXT` objects from accumulated attributes and text strings.
- Applies height, width, invisibility, placement, and `with` anchoring attributes.
- Updates current drawing position according to text size and global direction.
- Stores text fragments in the growing global `text` array.
- Wraps raw troff command strings as `TROFF` nodes.

Important behavior:
- Default height is `textht * number_of_text_strings` unless height is explicitly set.
- `WITH` adjusts current position so the requested anchor lies at the current point.
- Text extents are reported through `extreme()` before returning the node.
- Isolated text modifiers rewrite the last saved text item’s type.

Dependencies:
- Uses parser globals `attr`, `nattr`, `text`, `ntext`, `curx`, `cury`, `hvmode`, and helpers such as `getfval`, `grow`, `makenode`, `isright`, `isleft`, and `isup`.

Notable risks:
- Assumes isolated `TEXTATTR` modifiers have a previous text entry to modify.
- Static `prevh` and `prevw` are assigned but unused in this file.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/pic/textgen.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/pipefile.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/pipefile.c

Plan 9 utility that interposes read and write commands on a file through a pipe device bind.

Key responsibilities:
- Parses `pipefile [-d] [-r command] [-w command] file`.
- Opens the target file for independent read/write streams, or duplicates one `ORDWR` fd with `-d`.
- Binds a pipe device under `/n/temp`, then binds one pipe endpoint over the target file path.
- Starts writer and reader shell commands connected to pipe/file fds.

Important behavior:
- Defaults missing read or write command to `/bin/cat`.
- `connect()` forks a detached process, duping provided fds to stdin/stdout and executing `rc -c`.
- Uses `RFNOTEG` to avoid note propagation to the command itself.
- Leaves child command lifetime independent via `RFNOWAIT`.

Dependencies:
- Uses Plan 9 namespace operations `bind`, `unmount`, pipe device `#|`, `rfork`, and `/bin/rc`.

Notable risks:
- Hard-coded mount point `/n/temp` can collide with concurrent uses.
- Command strings are interpreted by `rc`, so arguments are shell syntax rather than direct argv.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/pipefile.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/plot/libplot/box.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/plot/libplot/box.c

Draws an outlined rectangle in plot coordinates.

Key responsibilities:
- Moves to `(x0, y0)`.
- Draws four vector segments through the remaining corners and back to the start.

Dependencies:
- Uses `move()` and `vec()` from libplot.

Notable risks:
- It does not normalize or clip itself; clipping is delegated to `vec()`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/plot/libplot/box.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/plot/libplot/cfill.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/plot/libplot/cfill.c

Sets the plot background/fill color.

Key responsibilities:
- Converts a color string with `bcolor()`.
- Stores successful colors in `e1->backgr`.

Notable behavior:
- Negative `bcolor()` results are ignored, because those strings may encode side effects such as pattern or slant settings.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/plot/libplot/cfill.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/plot/libplot/circ.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/plot/libplot/circ.c

Draws an unfilled circle.

Key responsibilities:
- Converts center and radius from plot coordinates to screen coordinates.
- Calls Plan 9 draw `ellipse()` with current foreground color.

Notable behavior:
- Negative radius is accepted by taking its absolute value.
- Radius scaling uses `SCR()`, which depends on the x scale only.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/plot/libplot/circ.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/plot/libplot/closepl.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/plot/libplot/closepl.c

Closes a plot session.

Key responsibilities:
- Calls `m_finish()` to flush/swap the backing image to the display.

Dependencies:
- Actual cleanup is handled in `machdep.c`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/plot/libplot/closepl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/plot/libplot/color.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/plot/libplot/color.c

Sets the plot foreground color.

Key responsibilities:
- Converts the supplied color string with `bcolor()`.
- Stores the result in `e1->foregr`.

Notable risks:
- Unlike `cfill()`, it stores negative side-effect return values, which can later be passed to `getcolor()`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/plot/libplot/color.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/plot/libplot/disk.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/plot/libplot/disk.c

Draws a filled circle.

Key responsibilities:
- Converts center and radius into screen coordinates.
- Calls `fillellipse()` using the current foreground color.

Notable behavior:
- Negative radius is treated as positive.
- Radius uses x-axis scaling through `SCR()`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/plot/libplot/disk.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/plot/libplot/doublebuffer.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/plot/libplot/doublebuffer.c

Enables libplot double buffering.

Key responsibilities:
- Calls `m_dblbuf()` to allocate and use an offscreen image when possible.

Dependencies:
- Buffer allocation and swap behavior live in `machdep.c`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/plot/libplot/doublebuffer.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/plot/libplot/dpoint.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/plot/libplot/dpoint.c

Draws a one-pixel point and moves the current plot position.

Key responsibilities:
- Draws a 1x1 rectangle at the scaled coordinate.
- Uses current foreground color.
- Calls `move()` to update `e1->copyx/copyy`.

Notable behavior:
- Does not explicitly clip; draw clipping is handled by the image rectangle.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/plot/libplot/dpoint.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/plot/libplot/erase.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/plot/libplot/erase.c

Clears the current plot window.

Key responsibilities:
- Swaps/flushes any current buffer.
- Clears the clipping rectangle to `e1->backgr`.

Dependencies:
- Uses `m_swapbuf()` and `m_clrwin()` from `machdep.c`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/plot/libplot/erase.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/plot/libplot/fill.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/plot/libplot/fill.c

Scanline polygon filler for libplot.

Key responsibilities:
- Converts lists of polygon vertices to screen-space active edges.
- Clips vertical extents to the screen rectangle.
- Fills scanline spans using an odd winding rule.
- Maintains incremental edge x positions using integer Bresenham-style fractions.
- Draws horizontal filled spans with Plan 9 draw `line()`.

Important behavior:
- Supports multiple contours through `cnt[]` and `pts[]`.
- Ignores horizontal edges.
- Uses `screen->r` bounds rather than libplot’s `clipmin` rectangle.
- `fill()` always calls the internal polygon routine with `Odd` and current foreground color.

Dependencies:
- Uses `SCX`, `SCY`, `getcolor()`, `screen`, and Plan 9 `Point` helpers.

Notable risks:
- Allocation size is based on total vertex count; malformed counts could stress memory.
- The declared `Nonzero` winding rule is unused.
- Filling is screen-rectangle clipped, not the libplot clipping rectangle used by `vec()`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/plot/libplot/fill.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/plot/libplot/frame.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/plot/libplot/frame.c

Changes the active plotting frame within the base frame.

Key responsibilities:
- Computes new `left`, `bottom`, `sidex`, and `sidey` from fractional frame coordinates.
- Adjusts current scales according to the frame-size change.
- Recomputes `quantum` from the base environment.

Notable behavior:
- Uses `e0` as the immutable base frame and modifies `e1`.
- Enforces a minimum `quantum` of `.01`.

Notable risks:
- Does not validate `xf > xs` or `yf > ys`; inverted or zero frames can produce odd scaling.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/plot/libplot/frame.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/plot/libplot/grade.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/plot/libplot/grade.c

Sets curve subdivision grade.

Key responsibilities:
- Stores the supplied value in `e1->grade`.

Dependencies:
- Used by curve approximators such as `parabola()`.

Notable risks:
- No validation; zero or negative grade can break subdivision math.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/plot/libplot/grade.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/plot/libplot/line.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/plot/libplot/line.c

Draws a straight line segment.

Key responsibilities:
- Moves to the start coordinate.
- Draws a vector to the end coordinate.

Dependencies:
- Uses `move()` and `vec()`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/plot/libplot/line.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/plot/libplot/machdep.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/plot/libplot/machdep.c

Plan 9 draw/event backend for libplot.

Key responsibilities:
- Initializes the draw display and mouse event handling.
- Sets clipping and square mapping bounds from the screen rectangle.
- Maintains the active drawing target, either `screen` or an offscreen image.
- Draws lines, text, clears rectangles, swaps buffers, and finishes output.
- Parses integer window arguments for older `-W` handling.
- Caches 1x1 color images for repeated draw operations.

Important behavior:
- `m_initialize()` runs draw setup once, then maps the plot square into the window inset by a few pixels.
- `m_dblbuf()` switches `offscreen` to an allocated inset image if possible.
- `m_swapbuf()` copies the offscreen image to the screen and flushes.
- `getcolor()` allocates RGB24 solid images and caches up to 32 entries.

Dependencies:
- Uses Plan 9 `draw`, `event`, `Image`, `screen`, `display`, `font`, `initdraw`, and `flushimage`.

Notable risks:
- `m_text()` measures with `stringsize(font, p)` even when rendering only `p..q`, so multi-line substring sizing can be wrong.
- Color cache never frees images and stops caching after 32 colors.
- Double buffer allocation failure silently falls back to direct screen drawing.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/plot/libplot/machdep.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/plot/libplot/move.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/plot/libplot/move.c

Updates current plot position without drawing.

Key responsibilities:
- Stores the supplied coordinates in `e1->copyx` and `e1->copyy`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/plot/libplot/move.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/plot/libplot/mplot.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/plot/libplot/mplot.h

Internal header for the Plan 9 draw-backed plot library.

Key responsibilities:
- Includes Plan 9, libc, stdio, draw, and event headers.
- Defines coordinate scaling macros `SCX`, `SCY`, and `SCR`.
- Declares the `penvir` plotting environment and global pointers `e0`, `e1`, `esave`.
- Declares clipping/map rectangles and backend helper prototypes.
- Includes public libplot prototypes from `../plot.h`.

Important state:
- `penvir` stores plot bounds, scale, current position, curve quantum, grade, pen mode/slant/gap, and foreground/background colors.
- `clip*` bounds control line clipping and clear regions.
- `map*` bounds describe the square plotting area inside the screen.

Notable risks:
- Scaling macros assume `e1` is valid and can overflow before the later `BIGINT` checks in some callers.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/plot/libplot/mplot.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/plot/libplot/openpl.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/plot/libplot/openpl.c

Initializes a plot session.

Key responsibilities:
- Calls backend initialization.
- Seeds base environment `e0` from the computed map rectangle.
- Copies `e0` into active environment `e1`.
- Moves current plot position to `(0, 0)`.

Important behavior:
- `sidey` and `scaley` are negative because screen y increases downward.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/plot/libplot/openpl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/plot/libplot/parabola.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/plot/libplot/parabola.c

Approximates a quadratic curve using line segments.

Key responsibilities:
- Takes start, end, and bend/control point coordinates.
- Computes quadratic coefficients.
- Subdivides based on distances to the control point, `e1->quantum`, and `e1->grade`.
- Emits vectors from start to end through sampled points.

Important behavior:
- Falls back to a straight line when either endpoint is within `quantum` of the control point.

Notable risks:
- `e1->grade` is used as a divisor without validation.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/plot/libplot/parabola.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/plot/libplot/pen.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/plot/libplot/pen.c

Stub for plot pen selection.

Key responsibilities:
- Accepts a pen string and intentionally does nothing.

Important behavior:
- Comment notes it used to call `color(s)` but is now a no-op.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/plot/libplot/pen.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/plot/libplot/poly.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/plot/libplot/poly.c

Draws one or more open polylines.

Key responsibilities:
- Iterates `num[]` counts and matching point arrays.
- Moves to each polygon/polyline start.
- Draws vectors through each subsequent point.

Notable behavior:
- Stops when it reaches a zero count sentinel.
- Does not close the path unless the input repeats the first point.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/plot/libplot/poly.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/plot/libplot/ppause.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/plot/libplot/ppause.c

Interactive pause helper for plot.

Key responsibilities:
- Flushes stdout.
- Reads up to four bytes from stdin.
- Clears the plot window with `erase()`.

Notable behavior:
- Input contents are ignored; any read wakes the plot.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/plot/libplot/ppause.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/plot/libplot/pprompt.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/plot/libplot/pprompt.c

Prompt helper for interactive plot use.

Key responsibilities:
- Prints `:` to stderr.

Notable behavior:
- It is not declared in `plot.h` and is not used by `plot.c` in this group.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/plot/libplot/pprompt.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/plot/libplot/range.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/plot/libplot/range.c

Sets user-coordinate range for the active plot environment.

Key responsibilities:
- Sets `xmin` and `ymin`.
- Computes `scalex` and `scaley` from current frame size and requested range.
- Recomputes drawing `quantum`.

Notable risks:
- No divide-by-zero guard for `x1 == x0` or `y1 == y0`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/plot/libplot/range.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/plot/libplot/rarc.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/plot/libplot/rarc.c

Approximates circular arcs with line segments.

Key responsibilities:
- Computes radius from start point to center.
- Chooses angular step from `e1->quantum`, capped at roughly pi/4.
- Draws clockwise or counterclockwise depending on sign of `rr`.
- Emits line segments by iterative rotation.

Important behavior:
- If radius is tiny relative to `quantum`, draws a degenerate point at the center.
- If arc angle is smaller than one step, draws a straight line.

Notable risks:
- Uses fixed approximations `PI4` and `6.2832`.
- Does not validate that the supplied end point lies on the radius.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/plot/libplot/rarc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/plot/libplot/restore.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/plot/libplot/restore.c

Restores the previous plotting environment.

Key responsibilities:
- Decrements `e1`.
- Restores current point by calling `move()` with the restored environment’s saved coordinates.

Notable risks:
- No underflow guard; unmatched `restore()` can move before the environment stack.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/plot/libplot/restore.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/plot/libplot/rmove.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/plot/libplot/rmove.c

Relative move operation.

Key responsibilities:
- Adds deltas to current `copyx/copyy`.
- Calls `move()` with the updated absolute position.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/plot/libplot/rmove.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/plot/libplot/rvec.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/plot/libplot/rvec.c

Relative vector operation.

Key responsibilities:
- Adds deltas to current `copyx/copyy`.
- Draws a vector to the updated absolute position.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/plot/libplot/rvec.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/plot/libplot/save.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/plot/libplot/save.c

Saves the active plotting environment.

Key responsibilities:
- Copies `e1` into the next environment slot.
- Advances `e1`.

Notable risks:
- The environment array has finite size in `subr.c`, but `save()` performs no overflow check.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/plot/libplot/save.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/plot/libplot/sbox.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/plot/libplot/sbox.c

Clears a rectangular region in plot coordinates.

Key responsibilities:
- Converts rectangle corners to screen coordinates.
- Normalizes corner order.
- Clips to libplot clipping bounds.
- Clears the rectangle using current background color.

Important behavior:
- Empty clipped rectangles are ignored.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/plot/libplot/sbox.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/plot/libplot/spline.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/plot/libplot/spline.c

Uniform quadratic spline renderer.

Key responsibilities:
- Iterates point-list groups from `num[]` and `ff[]`.
- Handles open and closed spline modes.
- Converts adjacent guide points into midpoint-to-midpoint parabolic spans.
- Uses `parabola()` and occasional `plotline()` to render the result.

Important behavior:
- `mode == 4` draws a closed curve.
- Odd modes draw a doubled first endpoint.
- Modes `>= 2` except closed mode draw the final endpoint segment.

Notable risks:
- For `n < 3`, it draws a line using the first two points; malformed counts under 2 would read past input.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/plot/libplot/spline.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/plot/libplot/subr.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/plot/libplot/subr.c

Global libplot environment state and color parsing.

Key responsibilities:
- Defines the `E[9]` environment stack and pointers `e0`, `e1`, `esave`.
- Parses color/style strings through `bcolor()`.
- Copies plotting environments with `sscpy()`.
- Provides stub `idle()` and `ptype()`.

Important behavior:
- Numeric color strings are mapped through `cmap2rgba()`.
- Letter colors map to Plan 9 draw constants: black, red, green, blue, magenta, yellow, cyan, white.
- `R` returns a raw integer color.
- `G` and `A` set pen gap/slant side effects and return `-1`.

Notable risks:
- `E` is initialized with eight explicit elements despite size nine; the last is zero-initialized.
- `sscpy()` does not copy `pgap` or `pslant`, so some side-effect state is not saved/restored.
- `bcolor()` has implicit `int` return style.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/plot/libplot/subr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/plot/libplot/text.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/plot/libplot/text.c

Draws text at the current plot position.

Key responsibilities:
- Parses leading text alignment escapes `\C`, `\R`, `\L`.
- Splits `\n` sequences into multiple displayed lines.
- Converts current plot position to screen coordinates.
- Calls backend `m_text()` and advances current y position for following lines.

Important behavior:
- Default text placement centers the first character at the current point.
- `\R` right-aligns, `\C` centers, and `\L` consumes the marker without special alignment.
- Multiline text updates `copyy` from the backend’s returned screen y coordinate.

Notable risks:
- Relies on backend string sizing behavior; substring sizing in `m_text()` is imperfect.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/plot/libplot/text.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/plot/libplot/vec.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/plot/libplot/vec.c

Draws a clipped vector from current position to a target point.

Key responsibilities:
- Converts current and target plot coordinates to screen coordinates.
- Updates current plot position to the target.
- Performs Cohen-Sutherland-style clipping against `clipmin/clipmax`.
- Calls backend `m_vector()` for visible clipped segments.

Important behavior:
- Drops vectors with coordinates beyond `BIGINT`.
- Even fully clipped segments still update the logical current point.

Notable risks:
- Integer divisions in clipping branches assume nonzero denominators implied by the selected clip edge.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/plot/libplot/vec.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/plot/libplot/whoami.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/plot/libplot/whoami.c

Identifies the plot device/backend.

Key responsibilities:
- Returns the literal string `"ramtek"`.

Notable behavior:
- Historical backend identity does not match the current Plan 9 draw implementation.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/plot/libplot/whoami.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/plot/plot.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/plot/plot.c

Interactive/file-driven plot command interpreter.

Key responsibilities:
- Initializes libplot and dispatches abbreviated plot commands to libplot functions.
- Parses numeric arguments, string arguments, polygon point lists, macro definitions, macro calls, and include files.
- Maintains a nested input stack for files and in-memory macro bodies.
- Supports command-line drawing options such as erase, color, fill color, grade, double buffering, and server mode.
- Keeps the window open after drawing, with a mouse menu item to exit.

Important behavior:
- Command names are matched by prefix length from the `plots[]` table.
- Numeric arguments are scaled by the current macro call scale.
- `define` stores macro bodies between braces; `call` pushes the stored string onto the input stack.
- `include` pushes a new `Biobuf` onto the same input stack.
- Lines beginning with `:` are comments.
- `server()` publishes a pipe in `/srv/plot`, but the source comment says it does not work.

Dependencies:
- Uses Plan 9 `bio`, `draw`, `event`, and libplot functions from `plot.h`.

Notable risks:
- Many functions use old implicit-int style.
- Fixed buffers and arrays (`argstr`, `x`, `cnt`, `pts`, macro library) impose hard limits.
- `define()` grows `bstash` with `realloc()` after freeing it first, which is a bug: freeing before `realloc` loses existing contents and can corrupt stored macro bodies.
- Macro name storage has a fixed 512-byte allocation and no growth after first allocation.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/plot/plot.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/plot/plot.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/plot/plot.h

Public function prototypes for the Plan 9 plot library.

Key responsibilities:
- Declares drawing primitives, state operations, spline/fill/poly routines, text, color, buffering, and device identity functions.

Notable behavior:
- Uses legacy C prototype style but with typed arguments.
- Function names include Plan 9-specific alternatives such as `plotdisc`, `plotline`, and `plotpoly`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/plot/plot.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/plumb/fsys.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/plumb/fsys.c

Synthetic 9P filesystem for the Plan 9 plumber service.

Key responsibilities:
- Publishes and mounts `/mnt/plumb` through `/srv/plumb.$user.$pid`.
- Exposes `rules`, `send`, and per-port files.
- Handles 9P version, attach, walk, open, read, write, clunk, stat, and flush operations.
- Queues plumb messages for all fids open on a destination port.
- Holds messages for ports whose client is being started.
- Parses writes to `send`, matches rules, starts clients, or delivers to ports.
- Supports live rules updates through writes to the `rules` file.

Important behavior:
- `addport()` dynamically appends readable port files and records them in `ports`.
- `queuesend()` snapshots currently open fids so each reader gets the message once.
- `drainqueue()` pairs queued read requests with queued send requests and handles partial reads using per-fid offsets.
- Opening a port queues any held startup messages.
- Opening `rules` for write is serialized by `rulesref`.
- Truncating `rules` clears current rules before accepting new rule text.

Dependencies:
- Uses Plan 9 threads, 9P `Fcall`, `plumbpack/unpack`, `/dev/time`, `/srv`, and global rule/matching functions.

Notable risks:
- Global queue state is complex and depends on `queue` locking discipline.
- Per-message delivery to every open fid can retain queued messages until all recipients read or close.
- Rules write finalization on clunk can lose parse errors for incomplete final rules.
- `NDIR` caps total ports at 50.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/plumb/fsys.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/plumb/match.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/plumb/match.c

Rule matching and action startup for plumber messages.

Key responsibilities:
- Implements verbs `is`, `matches`, `isfile`, `isdir`, `set`, `add`, and `delete`.
- Tracks regex capture variables `$0` through `$9`.
- Handles click-aware matching on message data.
- Rewrites clicked messages by removing `click` and optionally replacing data with matched text.
- Builds argv vectors from expanded action strings.
- Starts external clients/actions with `proccreate()` and `procexec()`.
- Determines when messages should be held for a client port.

Important behavior:
- `matches` requires full-string matches except click matching, where the regex match must span the clicked character.
- `isfile`/`isdir` resolve relative paths against message `wdir`.
- If a ruleset has a port and the message has no destination, matching assigns that port.
- `plumb client` actions set `holdforclient`.

Dependencies:
- Uses Plan 9 regexp, plumb attributes, `expand()` from `rules.c`, and filesystem `dirstat`.

Notable risks:
- `verbis()` calls `strcmp()` on fields that are expected non-nil; malformed messages could crash if fields are nil.
- `buildargv()` uses whitespace tokenization plus single-quote processing from `expand()`, not full shell parsing.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/plumb/match.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/plumb/plumb.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/plumb/plumb.c

Command-line sender for plumber messages.

Key responsibilities:
- Builds a `Plumbmsg` from command-line options and arguments or stdin.
- Sends messages to `/mnt/plumb/send` or a supplied plumb file.
- Supports attributes, source, destination, type, working directory, and stdin data.

Important behavior:
- `-i` gathers all stdin into `m.data` and defaults `action=showdata` if no action attribute exists.
- Without `-i`, each positional argument becomes one message with `ndata = -1`.
- Default source is `"plumb"` and default type is `"text"`.

Dependencies:
- Uses Plan 9 `plumbopen`, `plumbsend`, `plumbaddattr`, and `plumbunpackattr`.

Notable risks:
- Stdin collection grows with `realloc()` and has no size limit.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/plumb/plumb.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/plumb/plumber.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/plumb/plumber.c

Main entry point and common allocation/error helpers for the plumber daemon.

Key responsibilities:
- Parses `-p` alternate rules file.
- Initializes `$user`, `$home`, and default `$home/lib/plumbing` rule path.
- Reads and parses rules.
- Starts the filesystem service in a separate proc so the main thread can return.
- Provides `error`, `parseerror`, `emalloc`, `erealloc`, and `estrdup`.

Important behavior:
- `parseerror()` prints input stack context, unwinds parser input, stores `lasterror`, and longjmps to `parsejmp`.
- `makeports()` declares ports from parsed rules before mounting the filesystem.

Dependencies:
- Uses Plan 9 threads, auth/fcall/plumb libraries, and globals declared in `plumber.h`.

Notable risks:
- Environment variables `user` and `home` are mandatory.
- Errors call `threadexitsall`, terminating all plumber activity.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/plumb/plumber.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/plumb/plumber.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/plumb/plumber.h

Shared plumber rule, execution, and global declarations.

Key responsibilities:
- Defines rule objects (`data`, `dst`, `src`, `type`, `wdir`, `attr`, `arg`, `plumb`).
- Defines verbs (`is`, `matches`, `isfile`, `isdir`, `set`, `add`, `delete`, `to`, `start`, `client`).
- Declares `Rule`, `Ruleset`, and `Exec`.
- Declares cross-file functions for parsing, matching, expansion, startup, filesystem service, and rule writing.
- Declares global rule/user/home/port state.

Important behavior:
- `Exec` stores regex matches, clicked-span state, derived file/dir paths, and hold-for-client state.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/plumb/plumber.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/plumb/rules.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/plumb/rules.c

Parser, printer, variable expander, and incremental updater for plumber rules.

Key responsibilities:
- Maintains a nested input stack for rule files and string updates.
- Parses variables, includes, rules, rulesets, and port declarations.
- Validates object/verb combinations and compiles regex rules.
- Expands `$0`-style regex matches, message fields, variables, `$file`, and `$dir`.
- Serializes rules back to text for reading `/mnt/plumb/rules`.
- Incrementally accepts rule text written to the mounted `rules` file.

Important behavior:
- Include stack depth is capped at 10.
- Include paths that are not absolute or relative are searched under `/sys/lib/plumb`.
- Rulesets must have patterns and an action, except bare `plumb to` declarations, which declare ports.
- Only one `start` or `client` action is allowed per ruleset.
- `writerules()` parses complete rules as blank-line-delimited chunks during writes and finalizes on close.

Dependencies:
- Uses regexp compilation, plumb attribute packing, and globals from `plumber.h`.

Notable risks:
- `expand()` uses a fixed 4096-byte static buffer.
- `dollar()` has a likely typo checking `n == 4` but comparing `"wdir"` with length 3.
- Incremental parsing uses heuristics; malformed partial writes may report at write or close time depending on blank lines.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/plumb/rules.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/postscript/buildtables/buildtables.mk -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/postscript/buildtables/buildtables.mk

Makefile for installing and regenerating the PostScript `buildtables` helper.

Key responsibilities:
- Defines platform/install variables for V9-style build.
- Generates executable `buildtables` by substituting path variables into `buildtables.sh`.
- Installs the script and man page.
- Provides `changes` target to rewrite makefile and man page path defaults.

Notable behavior:
- Install steps create target directories and set owner/group/mode.
- Uses legacy `/bin/make` style and shell `sed` substitutions.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/postscript/buildtables/buildtables.mk -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/postscript/buildtables/buildtables.sh -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/postscript/buildtables/buildtables.sh

Shell helper for building PostScript troff font width tables.

Key responsibilities:
- Parses options for font directory, device, shell library, serial line, baud rate, and trofftable options.
- Loads a shell library and expands default table list with `AllTables` when no table names are supplied.
- Runs `trofftable` to generate PostScript table programs.
- Optionally sends them to a printer line via `postio` and saves returned tables.

Important behavior:
- Requires either `-T device` or `-S library`.
- Builds library path as `$FONTDIR/dev$DEVICE/shell.lib` by default.
- Each table argument is split into short and long names by `awk`.

Notable risks:
- Uses legacy shell syntax and unquoted expansions in several places.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/postscript/buildtables/buildtables.sh -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/postscript/common/bbox.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/postscript/common/bbox.c

Bounding-box accumulation and transformation utilities for PostScript translators.

Key responsibilities:
- Maintains per-page `bbox` and whole-document `docbbox`.
- Tracks a current transformation matrix.
- Adds covered points, transforms boxes, writes DSC bounding-box comments, and resets page state.
- Provides `scale`, `translate`, `rotate`, and `concat`.

Important behavior:
- `writebbox()` transforms all four user-space corners through `ctm`, expands by `slop + .5`, writes integer bounds, then updates/reset document state.
- Whole-document `%%BoundingBox:` output uses saved `docbbox`.
- `resetbbox()` only updates document bounds when output went to stdout.

Dependencies:
- Uses `comments.h`, `gen.h`, and `ext.h`.

Notable risks:
- Global matrix/bbox state is not reentrant.
- Integer truncation after slop may under/overestimate for negative coordinates.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/postscript/common/bbox.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/postscript/common/comments.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/postscript/common/comments.h

Definitions for Adobe Document Structuring Convention comments.

Key responsibilities:
- Defines PostScript document classification strings.
- Defines header, body, page-level, resource, trailer, continuation, and non-standard comment constants.
- Defines `NONE`, `WARNING`, and `FATAL` severity constants used by some translators.

Notable details:
- Includes historical typos preserved in constants such as `DOCUMENTPRINTERREQUIRED`, `BEGINPAPERSIZE`, and `PAPERFORM`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/postscript/common/comments.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/postscript/common/common.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/postscript/common/common.c

Plan 9-specific shared PostScript translator helpers.

Key responsibilities:
- Defines PostScript string escaping table `charcode`.
- Tracks page, line, character, and output-string state.
- Parses selected page lists.
- Emits page start/end PostScript scaffolding.
- Copies files to `Bstdout`.
- Provides allocation and diagnostic helpers.

Important behavior:
- `pagelist()` stores selected pages in a bitmap.
- `pageon()` suppresses output and temporarily disables debug for unselected pages.
- `startstring()`/`endstring()` coalesce text into PostScript strings at current `hpos/vpos`.
- `startpage()` and `endpage()` emit DSC page comments, save/restore, setup, showpage, and end-page comments.

Dependencies:
- Uses Plan 9 `Biobuf`, `Bstdout`, `Bstderr`, and globals declared in `common.h`.

Notable risks:
- Page bitmap grows by page number and never shrinks.
- `pagelist()` has permissive parsing and no validation of malformed ranges.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/postscript/common/common.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/postscript/common/common.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/postscript/common/common.h

Plan 9-oriented shared declarations for PostScript translators.

Key responsibilities:
- Defines rune helper macros, `BOOLEAN`, and true/false constants.
- Declares common translator globals such as `programname`, `inputfilename`, page counters, current font, and position.
- Declares `Biobufhdr` stdout/stderr handles.
- Defines `strtab` and declares `charcode`.
- Prototypes page/string/output helpers, allocation, field parsing, and page-list handling.

Notable behavior:
- This header overlaps conceptually with `gen.h`/`ext.h` but is for the Plan 9/Bio-based translator path.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/postscript/common/common.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/postscript/common/ext.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/postscript/common/ext.h

External global and helper declarations for portable PostScript translator code.

Key responsibilities:
- Declares process globals `argc`, `argv`, exit/debug/ignore flags, line/byte position, program name, temp file, and font encoding.
- Declares bounding-box and encoding globals.
- Declares getopt globals.
- Prototypes common helpers such as `cat`, `error`, `out_list`, `setencoding`, `interrupt`, and `tempnam`.

Notable behavior:
- Designed for older C code shared across multiple PostScript tools.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/postscript/common/ext.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/postscript/common/gen.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/postscript/common/gen.h

General constants and macros for the PostScript translator suite.

Key responsibilities:
- Defines program version, fatality constants, boolean constants, byte masks, points-per-inch, pi, encoding modes, page defaults, and simple `ABS/MIN/MAX` macros.
- Enables `DOROUND` by default for translators that include page-rounding prologue code.
- Sets default page dimensions used in bounding-box calculations.

Notable risks:
- Macro names such as `FATAL`, `TRUE`, and `FALSE` overlap with other headers.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/postscript/common/gen.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/postscript/common/getopt.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/postscript/common/getopt.c

Portable getopt implementation used by legacy PostScript tools.

Key responsibilities:
- Implements option parsing with global `opterr`, `optind`, `optopt`, and `optarg`.
- Supports grouped short options, option arguments, and `--`.

Important behavior:
- Returns `EOF` when options are exhausted.
- Prints diagnostics when `opterr` is set.

Notable risks:
- K&R-style signature omits the explicit `argc` parameter name in the function header, relying on old C conventions.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/postscript/common/getopt.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/postscript/common/glob.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/postscript/common/glob.c

Shared global variable definitions for portable PostScript tools.

Key responsibilities:
- Defines `argc`, `argv`, exit/debug/ignore flags, current line/byte position, program name, temp file, font encoding, bounding-box settings, page dimensions, and input/output encoding modes.

Important behavior:
- Defaults `reading` to UTF encoding and `writing` to `WRITING` from `gen.h`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/postscript/common/glob.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/postscript/common/misc.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/postscript/common/misc.c

General helper routines for portable PostScript translators.

Key responsibilities:
- Parses output page ranges into `olist`.
- Tests whether a page number should be output.
- Includes font encoding files.
- Copies files to stdout.
- Parses integers from strings.
- Reports errors and handles interrupt cleanup.

Important behavior:
- `out_list()` accepts troff-style ranges, with missing range end defaulting to 9999.
- `setencoding()` emits an encoding file from `ENCODINGDIR`; if `cat()` fails it toggles `writing` based on whether name starts with `UTF`.
- Fatal errors unlink `temp_file` unless `ignore` is enabled.

Notable risks:
- Several functions use implicit-int K&R style.
- `cat()` ignores short write errors.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/postscript/common/misc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/postscript/common/path.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/postscript/common/path.h

Path constants for PostScript prologues, fonts, requests, and temporary files.

Key responsibilities:
- Defines absolute Plan 9 paths for translator prologues such as `dpost.ps`, `postbgi.ps`, `postprint.ps`, and related support files.
- Defines font, encoding, host font, PostScript library, request, and temp directories.

Notable behavior:
- Path values are compile-time defaults consumed by multiple tools and makefiles.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/postscript/common/path.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/postscript/common/request.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/postscript/common/request.c

Special PostScript request handling for translators.

Key responsibilities:
- Saves `-R` requests for global or per-page insertion.
- Writes matching requests at setup/page time.
- Looks up request bodies in request files and copies the selected body to output.

Important behavior:
- Request syntax is `request`, `request:page`, or `request:page:file`.
- Page `0` means global setup.
- Request file entries begin with `@name`; copied lines continue until the next `@` entry.
- Lines beginning with `#` or `%` in request bodies are skipped.

Dependencies:
- Uses `request.h`, `path.h`, `gen.h`, and `ext.h`.

Notable risks:
- Uses `strtok()` destructively on the option string.
- Keyword matching uses prefix length of `want`, so partial names can match longer request keys.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/postscript/common/request.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/postscript/common/request.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/postscript/common/request.h

Definitions for special PostScript request support.

Key responsibilities:
- Documents `-R` request syntax.
- Defines `MAXREQUEST`.
- Defines `Request` with wanted keyword, page number, and file path.

Usage:
- Included by `request.c` and translators that accept request insertion.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/postscript/common/request.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/postscript/common/tempnam.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/postscript/common/tempnam.c

Compatibility implementation of `tempnam()` for V9/BSD/Plan 9 builds.

Key responsibilities:
- Checks candidate directory accessibility.
- Allocates a unique-ish path of the form `dir/pfx.pid.seq`.
- Loops while the path exists and sequence is below 256.

Important behavior:
- On Plan 9 it avoids write-access checking because access emulation has a race.

Notable risks:
- Name generation is inherently race-prone; caller must still create safely.
- If all 256 names exist, it returns the last allocated candidate without explicit failure.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/postscript/common/tempnam.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/postscript/config -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/postscript/config

Configuration defaults for the Plan 9 PostScript package.

Key responsibilities:
- Sets `SYSTEM=plan9`, version, root, binary/library/font paths, Datakit flags, page rounding flag, make command, and makefile name.

Important behavior:
- `POSTBIN` derives from `$ROOT/$objtype/bin/aux`.
- Plan 9 font/prologue directories are `/sys/lib/troff/font` and `/sys/lib/postscript/prologues`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/postscript/config -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/postscript/devpost.add/devpost.add.mk -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/postscript/devpost.add/devpost.add.mk

Makefile for installing additional `devpost` font files.

Key responsibilities:
- Defines install ownership, group, and font directory.
- Creates `$(FONTDIR)` and `$(FONTDIR)/devpost` if needed.
- Copies `FONTFILES` into `devpost`.
- Provides a `changes` target to rewrite makefile defaults.

Notable behavior:
- `FONTFILES` defaults to `??`, expecting caller/site customization.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/postscript/devpost.add/devpost.add.mk -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/postscript/download/download.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/postscript/download/download.c

Host-resident PostScript font downloader/filter.

Key responsibilities:
- Reads a font map table mapping PostScript font names to host files.
- Optionally reads resident-font lists and marks those fonts already present.
- Scans input PostScript for `%%DocumentFonts:` and continuation comments.
- Copies required mapped font files to stdout before the input file.
- Handles stdin through a temporary copy when scanning ahead.
- Supports options for comment name, forced full scan, map name, printer/resident list, host font directory, temp directory, debug, and ignore-fatal mode.

Important behavior:
- Map-file comments begin with `%`.
- Relative font file paths are resolved under `hostfontdir`.
- Fonts are downloaded only once per process.
- `(atend)` causes full scanning.

Dependencies:
- Uses common `comments.h`, `gen.h`, `path.h`, `ext.h`, and `download.h`.

Notable risks:
- It assumes PostScript files in one invocation are part of a single job.
- Temporary-file handling uses `tempnam()`.
- Map parser relies on `strtok()` over a full in-memory file.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/postscript/download/download.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/postscript/download/download.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/postscript/download/download.h

Shared definitions for the `download` font downloader.

Key responsibilities:
- Defines `Map`, which maps a PostScript font name to a host file and tracks whether it has already been downloaded.
- Declares `allocate()` for growing map arrays.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/postscript/download/download.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/postscript/g3p9bit/g3p9bit.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/postscript/g3p9bit/g3p9bit.c

Group 3 fax decoder to Plan 9 bitmap format.

Key responsibilities:
- Reads Group 3 modified Huffman fax data from several container/header variants.
- Builds white and black code lookup tables from included `wtab` and `btab`.
- Decodes fax rows into a 1728-pixel-wide bitmap.
- Writes a Plan 9 bitmap header and raster bytes.
- Supports simulated 2-bit gray horizontal compression (`-g`) and scanline doubling (`-y`).

Important behavior:
- Recognizes a PC/TIFF-like `II*` offset, a “PC Research, Inc” digifax format, and text headers with `FDCS=`.
- Only supports width code 0 and 1-D modified Huffman compression.
- High vertical resolution halves output row count after decoding.
- `sync()` skips to the next EOL code.

Dependencies:
- Includes generated Huffman tables `btab` and `wtab`.

Notable risks:
- Reads the entire input into a fixed 1 MiB buffer.
- Uses fixed maximum page dimensions: 1728 dots and 1410 lines.
- Error handling may emit a valid-looking partial bitmap before reporting a trailing decode error.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/postscript/g3p9bit/g3p9bit.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/postscript/mcolor/mcolor.mk -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/postscript/mcolor/mcolor.mk

Makefile for installing troff color macro support.

Key responsibilities:
- Copies `color.sr` to `tmac.color`.
- Installs `tmac.color` into `TMACDIR`.
- Provides clean, clobber, and `changes` targets.

Important behavior:
- `changes` rewrites makefile defaults and updates path strings in `mcolor.5`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/postscript/mcolor/mcolor.mk -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/postscript/misc/ibmfont.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/postscript/misc/ibmfont.c

IBM PC downloadable PostScript font converter.

Key responsibilities:
- Converts IBM PC segmented font files to Unix-readable font files.
- Parses segments with leading byte 128, type, and 4-byte little-endian length.
- Emits ASCII segments with CR converted to newline.
- Emits binary segments as uppercase hex, wrapping every 40 bytes.
- Stops on EOF segment type 3.

Options:
- `-D` enables debug segment prints.
- `-I` ignores fatal errors.

Notable risks:
- Old K&R C style with minimal validation.
- Reads bytes with `getc()` without checking EOF inside fixed-size segment loops.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/postscript/misc/ibmfont.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/postscript/misc/laserbar.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/postscript/misc/laserbar.c

Code 39 barcode generator for PostScript output.

Key responsibilities:
- Maps supported characters to Code 39 wide/narrow bar patterns.
- Parses rotation, offsets, scaling, label, newpath, and showpage options.
- Emits PostScript definitions for wide bars, narrow bars, and labels.
- Wraps the requested string with start/stop `*`.

Important behavior:
- Lowercase letters are accepted and labeled uppercase.
- Offsets are specified in inches and converted to points.
- Unsupported characters are skipped.

Notable risks:
- Uses global `right` state reset after each barcode.
- Command-line build depends on `MAIN` being defined in this file.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/postscript/misc/laserbar.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/postscript/misc/macfont.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/postscript/misc/macfont.c

Macintosh downloadable PostScript font converter.

Key responsibilities:
- Converts Macintosh font resource blocks to Unix-readable font files.
- Reads big-endian block length, block type, and a following unused byte.
- Skips comment blocks.
- Emits ASCII blocks with CR converted to newline.
- Emits binary blocks as uppercase hex, wrapping every 40 bytes.
- Stops on type 5.

Options:
- `-D` enables debug output.
- `-I` ignores fatal errors.

Notable risks:
- Types 3 and 4 are explicitly unimplemented fatal cases.
- Uses old K&R style and sparse EOF validation.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/postscript/misc/macfont.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/postscript/misc/pscrypt.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/postscript/misc/pscrypt.c

Adobe Type 1 eexec/CharString encryption and decryption tool.

Key responsibilities:
- Implements the Adobe cipher with seeds for eexec and show/CharString.
- Supports encrypt and decrypt modes.
- Reads hex or binary input and writes hex or binary output.
- Injects an encryption key for encrypt mode or strips initial decrypted key bytes for decrypt mode.
- Supports custom seed and hex line length.

Important behavior:
- Default decrypt mode expects hex input and binary output, omitting the first four output bytes.
- Default encrypt mode expects binary input and hex output, prepending four key bytes.
- Cipher update uses constants `MAGIC1=52845` and `MAGIC2=22719`.

Notable risks:
- `nexthexchar()` does not robustly handle odd or truncated hex input before combining nibbles.
- Global `lastchar` controls loop termination across multiple input files.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/postscript/misc/pscrypt.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/postscript/p9bitpost/p9bitpost.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/postscript/p9bitpost/p9bitpost.c

Plan 9 bitmap-to-PostScript command-line frontend.

Key responsibilities:
- Parses DPI, debug, magnification, landscape, patch string, and paper-size options.
- Reads a Plan 9 image into a `Memimage`.
- Initializes `pslib`, applies options, and writes PostScript image output.

Important behavior:
- Defaults to stdin and file label `<stdin>`.
- `-m` can set x and y magnification separately.
- `-P` passes a raw PostScript patch string through to `pslib`.

Dependencies:
- Uses Plan 9 `draw`, `memdraw`, and `pslib`.

Notable risks:
- Option parsing manually indexes `argv[++i]` for some options and can fall into usage on missing values.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/postscript/p9bitpost/p9bitpost.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/postscript/p9bitpost/pslib.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/postscript/p9bitpost/pslib.c

PostScript image output library for Plan 9 `Memimage` objects.

Key responsibilities:
- Emits DSC headers, a PostScript image prologue, page wrapper, image data, and trailer.
- Supports indexed Plan 9 colormap, grayscale, and 24-bit RGB image output.
- Converts image data to ASCII85.
- Removes line padding and aligns sub-byte images to byte boundaries.
- Computes fit-to-page dimensions for portrait or landscape output.
- Supports x/y magnification, landscape mode, and raw PostScript patch injection.

Important behavior:
- For non-CMAP/GREY images with depth >= 8, converts to `b8g8r8`.
- Image bytes are inverted (`255 - src`) before encoding.
- ASCII85 zero groups are compressed as `z`, except partial final groups.
- If DPI is supplied, output size is based on pixel dimensions and DPI; otherwise it fits within 0.5-inch margins.

Dependencies:
- Uses Plan 9 `Memimage`, `Biobuf`, `bytesperline`, `byteaddr`, `memimagedraw`, and `allocmemimage`.

Notable risks:
- Large PostScript colormap is embedded for every output file.
- Commented-out Inferno/Tk text code remains in the file but is inactive.
- `imagebits()` allocates a compacted full image buffer in memory.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/postscript/p9bitpost/pslib.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/postscript/p9bitpost/pslib.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/postscript/p9bitpost/pslib.h

Minimal interface for `p9bitpost` PostScript output library.

Key responsibilities:
- Declares `psinit()`, `image2psfile()`, and `psopt()`.
- Declares external paper dimensions.

Usage:
- Included by both the frontend and implementation.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/postscript/p9bitpost/pslib.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/postscript/picpack/picpack.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/postscript/picpack/picpack.c

Troff preprocessor that packs referenced picture files inline.

Key responsibilities:
- Scans input for picture request macros, default `.BP` and `.PI`.
- Copies each referenced picture file once into troff transparent mode output.
- Emits `x X InlinePicture filename bytes` device-control records.
- Performs a second pass to copy the original input after inline picture payloads.
- Supports custom key strings, quiet mode, debug, and ignore-fatal flags.
- Copies stdin to a temporary file so it can be scanned twice.

Important behavior:
- Picture names are parsed as the second token and truncated at `(`.
- Transparent output prefixes lines with `\!` and escapes backslashes.
- A temp file records already-added picture filenames.

Dependencies:
- Uses common `gen.h`, `ext.h`, `path.h`, and `tempnam()`.

Notable risks:
- Fixed line/name buffers can truncate long input lines or pathnames.
- Duplicate tracking repeatedly opens the temp file.
- `tempnam()`-style temp creation is race-prone.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/postscript/picpack/picpack.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/postscript/picpack/picpack.mk -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/postscript/picpack/picpack.mk

Makefile for the `picpack` PostScript/troff preprocessor.

Key responsibilities:
- Defines build/install variables and common include directory.
- Builds `picpack` from `picpack.o` plus common `glob`, `misc`, and `tempnam` objects.
- Installs binary and man page with ownership/mode setup.
- Delegates common object builds to `../common/common.mk`.

Notable behavior:
- `changes` rewrites defaults in the makefile using `sed`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/postscript/picpack/picpack.mk -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/postscript/postbgi/postbgi.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/postscript/postbgi/postbgi.c

BGI (Basic Graphical Instructions) to PostScript translator.

Key responsibilities:
- Emits DSC headers, copies the PostScript prologue, handles setup, translates BGI input streams, emits trailer/accounting.
- Parses options for aspect ratio, copies, font, magnification, forms-per-page, page ranges, orientation, line width, offsets, accounting, extra files, encoding, prologue, raw PostScript patches, special requests, debug, and ignore-fatal mode.
- Decodes BGI opcodes for text modes, graph mode, pages, coordinates, points, vectors, rectangles, arcs, filled rectangles/trapezoids, line styles, colors, patterns, character size, subroutines, and calls.
- Manages current BGI position, page counters, subroutine displacement tracking, and output redirection for selected pages.

Important behavior:
- `header()` pre-scans `-L` to choose the prologue before writing DSC/prologue output.
- `formfeed()` closes the current page, skips nulls, chooses stdout or `/dev/null` for the next page, emits setup, and resets size/position.
- Subroutines become PostScript procedures `S<num>` inside `%%BeginGlobal`/`%%EndGlobal`.
- Vectors accumulate relative displacements on the stack, then call prologue procedure `v`.
- Colors convert BGI cyan/yellow/magenta-style bytes into RGB triples.
- Patterns are approximated by averaging four BGI color bytes.
- Repeats and raster rectangles are not implemented.

Dependencies:
- Uses shared PostScript common files and prologues: `comments.h`, `gen.h`, `path.h`, `ext.h`, `request.c`, and `postbgi.h`.

Notable risks:
- Old K&R style with many implicit-int functions.
- Several unimplemented BGI features are fatal.
- `arc(FILL)` ignores fill mode and emits stroked `arcn`.
- Page counting/output routing is subtle because skipped pages write to `/dev/null`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/postscript/postbgi/postbgi.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/postscript/postbgi/postbgi.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/postscript/postbgi/postbgi.h

BGI opcode and helper definitions for `postbgi`.

Key responsibilities:
- Defines BGI command opcodes and data masks.
- Defines character size, vector modes, visibility modes, fill/outline modes, line-style constants, color component constants, and helper macros.
- Defines `Disp` for subroutine displacement tracking.
- Defines `Fontmap` and default font-name aliases.
- Declares `get_font()`.

Important behavior:
- `MAG()` decodes sign-magnitude BGI integer bytes.
- `LINESPACE()` derives text line spacing from BGI character grid size.
- `STYLES` maps BGI line styles to PostScript dash arrays.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/postscript/postbgi/postbgi.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/postscript/postbgi/postbgi.mk -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/postscript/postbgi/postbgi.mk

Makefile for the `postbgi` translator.

Key responsibilities:
- Defines build/install variables for binary, prologue library, and man page.
- Builds `postbgi` from `postbgi.o` and common `glob`, `misc`, and `request` objects, linking math library.
- Installs binary, `postbgi.ps` prologue, and man page.
- Delegates common object builds to `../common/common.mk`.
- Provides a `changes` target to rewrite defaults and update man-page prologue path.

Notable behavior:
- Creates both `POSTBIN` and `POSTLIB` directories during install if needed.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/postscript/postbgi/postbgi.mk -->