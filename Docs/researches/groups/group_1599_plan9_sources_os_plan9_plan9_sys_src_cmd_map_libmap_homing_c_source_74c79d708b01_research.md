# Group Research: group_1599_plan9_sources_os_plan9_plan9_sys_src_cmd_map_libmap_homing_c_source_74c79d708b01

Scope: `Docs/research_subset_a.md`. All listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/map/libmap/homing.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/map/libmap/homing.c

Implements the `mecca` and `homing` map projections plus their limb iterators. Both projections use a configured standard parallel `p0` and compute an azimuth/distance from each input `struct place` to that reference.

Key functions:
- `mecca(double par)` validates `|par| <= 80`, initializes `p0`, and returns `Xmecca`.
- `homing(double par)` does the same and returns `Xhoming`.
- `azimuth()` computes spherical azimuth and angular distance using trigonometric clamps to avoid domain drift.
- `hlimb()` traces the visible limb for homing.
- `mlimb()` traces the Mecca projection boundary unless the standard parallel is effectively equatorial.

Behavior notes:
- Projection return values follow libmap convention: `1` drawable, `0` wrong sheet/hidden, `-1` unplottable.
- `first` is global, not static, and is reset by both projection factories for limb iteration.
- `Xmecca` rejects extreme `y` values and hides the far hemisphere using `rad.c < 0`.
- `Xhoming` uses azimuthal distance components and hides points where `place->wlon.c < 0`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/map/libmap/homing.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/map/libmap/lagrange.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/map/libmap/lagrange.c

Implements the Lagrange conformal projection as a `proj` factory returning `Xlagrange`.

Key flow:
- Copies the input `place`.
- Reflects southern latitudes into the northern hemisphere, then restores sign on output `y`.
- Uses `Xstereographic()` followed by complex square root and division helpers from libmap.
- Outputs `x = t2`, `y = -t1`.

Dependencies:
- `copyplace`, `Xstereographic`, `csqrt`, and `cdiv`.
- Always returns `1`; there is no explicit visibility rejection in this file.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/map/libmap/lagrange.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/map/libmap/lambert.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/map/libmap/lambert.c

Implements a Lambert conformal conic projection with two standard parallels.

Key functions:
- `lambert(double par0, double par1)` normalizes parallel order, validates polar limits, and computes cone constant `k`.
- Degenerate cases dispatch to other projections:
  - Near opposite parallels: `mercator()`.
  - Near equal parallels: `perspective(-1.)`, effectively stereographic.
- `Xlambert()` computes radial distance and angular displacement.

Behavior notes:
- Rejects latitudes below about `-80°`.
- Treats near north pole as `r = 0`.
- Negates radius for southern standard-parallel setup.
- Output is `x = -r*sin(k*lon)`, `y = -r*cos(k*lon)`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/map/libmap/lambert.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/map/libmap/laue.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/map/libmap/laue.c

Implements the Laue projection.

Key behavior:
- `laue()` returns `Xlaue`.
- `Xlaue()` only plots northern points above roughly `45°`.
- Computes `r = tan(PI - 2*lat)`.
- Rejects points when `r > 3`.
- Outputs circular coordinates using longitude sine/cosine: `x = -r*sin(lon)`, `y = -r*cos(lon)`.

This is a small bounded polar-style projection with hard cutoff behavior.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/map/libmap/laue.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/map/libmap/lune.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/map/libmap/lune.c

Implements a conformal lune projection.

Key functions:
- `lune(double lat, double theta)` initializes east/west pole reference points, checks stereographic symmetry, sets scale and exponent.
- `Xlune()` maps via stereographic projection and a complex power transform:
  `w = ((1+z)^A - (1-z)^A) / ((1+z)^A + (1-z)^A)`.

Behavior notes:
- Rejects points below the configured east-pole latitude cap.
- Uses `Xstereographic`, `cpow`, and `cdiv`.
- Comments document branch cuts from east/west poles to south pole; without a cut routine, the code rejects outside a polar cap.
- Uses old-style implicit `int` return for `static Xlune`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/map/libmap/lune.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/map/libmap/mercator.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/map/libmap/mercator.c

Implements spherical Mercator and spheroidal Mercator.

Key functions:
- `mercator()` returns `Xmercator`.
- `Xmercator()` rejects latitudes outside `±80°`, maps longitude linearly and latitude via logarithmic Mercator formula.
- `sp_mercator()` returns `Xspmercator`.
- `Xspmercator()` applies an ellipsoid eccentricity correction using `ECC`.

Dependencies:
- `ECC` comes from `map.h`.
- Output longitude sign convention is `x = -wlon`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/map/libmap/mercator.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/map/libmap/mollweide.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/map/libmap/mollweide.c

Implements the Mollweide equal-area projection.

Key behavior:
- `mollweide()` returns `Xmollweide`.
- Uses Newton iteration to solve `2z + sin(2z) = PI*sin(lat)`.
- Skips iteration near the poles.
- Outputs `y = sin(z)` and `x = -(2/PI)*cos(z)*lon`.
- Always returns `1`; no explicit clipping or sheet rejection is performed.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/map/libmap/mollweide.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/map/libmap/newyorker.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/map/libmap/newyorker.c

Implements the New Yorker projection.

Key behavior:
- `newyorker(double a0)` stores angular parameter `a = a0*RAD`.
- `Xnewyorker()` computes polar distance `r = PI/2 - lat`.
- Very small `r` maps to the center.
- Points with `r < a` are rejected.
- Otherwise scale is `log(r/a)`, applied in longitude polar coordinates.

This is a polar projection centered at the north pole with an excluded inner cap controlled by `a`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/map/libmap/newyorker.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/map/libmap/orthographic.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/map/libmap/orthographic.c

Implements orthographic projection and limb tracing.

Key functions:
- `orthographic()` returns `Xorthographic`.
- `Xorthographic()` maps visible hemisphere coordinates with `x = -cos(lat)*sin(lon)`, `y = -cos(lat)*cos(lon)`.
- Returns `0` for southern normalized latitudes and `1` otherwise.
- `olimb()` iterates the equatorial limb from longitude `-180` to `180`.

Notes:
- `olimb()` uses a static `first` state reset after completion.
- The projection is also reused by `perspective()` for very large viewpoint radii.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/map/libmap/orthographic.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/map/libmap/perspective.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/map/libmap/perspective.c

Implements perspective-family projections.

Key functions:
- `perspective(double radius)` returns `Xorthographic` for huge radius, rejects radius near `1`, otherwise returns `Xperspective`.
- `stereographic()` sets `viewpt = -1`.
- `gnomonic()` sets `viewpt = 0`.
- `Xstereographic()` temporarily forces `viewpt = -1` for callers needing stereographic math.
- `plimb()` traces the visible boundary, delegating to `olimb()` for orthographic.

Behavior notes:
- `Xperspective()` computes radial scale from `viewpt` and normalized latitude.
- Rejects overly large projected radii.
- Returns `0` for hidden side based on `viewpt`.
- The first guard contains suspicious old C expression shape: `fabs(place->nlat.s<=viewpt+.01)` applies `fabs` to a comparison result, but this is source behavior as read.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/map/libmap/perspective.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/map/libmap/polyconic.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/map/libmap/polyconic.c

Implements polyconic projection.

Key behavior:
- `polyconic()` returns `Xpolyconic`.
- For non-equatorial latitudes, computes `r = cos/sin`, `alpha = lon*sin(lat)`, then applies standard polyconic formulas.
- For near-equatorial latitudes, uses a series approximation to avoid singular division by small `sin(lat)`.
- Always returns `1`.

Dependencies:
- Uses `struct place` cached trigonometric fields from `zcoord.c`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/map/libmap/polyconic.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/map/libmap/rectangular.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/map/libmap/rectangular.c

Implements an equirectangular/rectangular projection with configurable standard parallel.

Key functions:
- `rectangular(double par)` stores `scale = cos(par*RAD)`.
- Rejects projections with `scale < .1`, avoiding near-polar standard parallels.
- `Xrectangular()` maps `x = -scale*lon`, `y = lat`.
- Always returns `1`.

This projection is also used as a fallback by conic projections in degenerate cases.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/map/libmap/rectangular.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/map/libmap/simpleconic.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/map/libmap/simpleconic.c

Implements a simple conic projection using one or two standard parallels.

Key behavior:
- `simpleconic(par0, par1)` converts parallels, then chooses parameters:
  - Opposite parallels nearly cancel: fallback to `rectangular(par0)`.
  - Nearly equal parallels: tangent cone formulas.
  - Otherwise: secant cone formulas.
- `Xsimpleconic()` maps by radius `r0 - lat` and angle `a*lon`.
- Always returns `1`.

State:
- Static `r0` and `a` hold projection parameters.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/map/libmap/simpleconic.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/map/libmap/sinusoidal.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/map/libmap/sinusoidal.c

Implements sinusoidal projection.

Key functions:
- `sinusoidal()` returns `Xsinusoidal`.
- `Xsinusoidal()` maps `x = -lon*cos(lat)`, `y = lat`.
- Always returns `1`.

This is a minimal equal-area projection implementation relying entirely on cached trigonometric values in `struct place`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/map/libmap/sinusoidal.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/map/libmap/tetra.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/map/libmap/tetra.c

Implements a conformal map of the earth onto an unfolded tetrahedron.

Major pieces:
- Static tetrahedral pole definitions and per-face projection table `tproj`.
- `tetra()` initializes constants, elliptic-integral scale factors, tetrahedral pole coordinates, and per-face orientation/twist rotations.
- `twhichp()` chooses the nearest and second-nearest tetrahedral poles for a point.
- `Xtetra()` normalizes a point into the selected face, stereographically projects, applies complex rational transforms and elliptic integral `elco2`, then rotates/translates into the unfolded tetrahedron.
- `tetracut()` handles seam crossing behavior for map line drawing.

Dependencies:
- Heavy use of libmap complex helpers, `Xstereographic`, `latlon`, `deg2rad`, and `norm`.
- `map.c` contains special grid handling for `projection == Xtetra`.

Behavior notes:
- Uses old K&R style `register i`.
- Mutates static `tx` and `ty` scale offsets during initialization, so repeated `tetra()` initialization would compound offsets if called more than once in the same process.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/map/libmap/tetra.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/map/libmap/trapezoidal.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/map/libmap/trapezoidal.c

Implements trapezoidal projection.

Key behavior:
- `trapezoidal(par0, par1)` falls back to `rectangular(par0)` when absolute standard parallels are nearly equal.
- Computes slope `k` either from sine for equal parallels or from cosine/latitude differences.
- Computes equator offset `yeq`.
- `Xtrapezoidal()` maps `y = yeq + lat`, `x = y*k*lon`.

Always returns `1`; no clipping is performed.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/map/libmap/trapezoidal.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/map/libmap/twocirc.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/map/libmap/twocirc.c

Implements two projections whose meridians and parallels are circular arcs.

Key pieces:
- `twocircles()` solves intersection of a meridian circle and a parallel circle, reflecting signs to handle quadrants and using fallback approximations near axes.
- `globular()` returns `Xglobular`, which scales longitude and latitude into the two-circle solver.
- `vandergrinten()` returns `Xvandergrinten`, using a transformed latitude parameter before solving.

Behavior notes:
- `quadratic()` returns `0` on negative discriminant rather than reporting projection failure.
- Both projection functions always return `1`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/map/libmap/twocirc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/map/libmap/zcoord.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/map/libmap/zcoord.c

Provides core spherical coordinate utilities for the map library.

Key functions:
- `orient(lat, lon, theta)` sets global map pole/twist and inverse transform.
- `latlon()` fills a `struct place` from degrees.
- `deg2rad()` normalizes degrees and fills radians/sin/cos.
- `normalize()` and `invert()` apply global forward/inverse orientation.
- `norm()` rotates a `struct place` into a pole/twist coordinate frame.
- `sincos()`, `copyplace()`, `printp()`, and a local `tan()` helper.

Behavior notes:
- `cirmod()` normalizes degrees into `[-180, 180)`.
- `latlon()` folds latitudes outside `±90°` and shifts longitude by `180°`.
- `norm()` handles the trivial north-pole orientation as a special case, then keeps longitude within `[-PI, PI]`.
- This file owns global orientation state used by `map.c`, `route.c`, and projections.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/map/libmap/zcoord.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/map/map.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/map/map.c

Main command driver for Plan 9 `map`.

Responsibilities:
- Parses projection name, projection parameters, and rendering options.
- Initializes projection function, cut handler, limb iterator, orientation, limits, clipping polygon, scale, and plot viewport.
- Draws grid, border/limb, map files, tracks, and symbols through `iplot`.
- Reads packed map data using `.x` index sidecar files and binary coordinate deltas.
- Handles map cuts, visible windows, clipping, and projection return-code recoding.

Important flow:
- `main()` resolves projection from external `index[]`, parses options such as `-m`, `-g`, `-o`, `-l`, `-k`, `-w`, `-p`, `-v`, `-C`, then computes bounds by sampling projected points.
- `fixproj()` recodes projection return values from `-1/0/1` into renderer semantics.
- `normproj()` converts lat/lon, normalizes orientation, checks window, and projects.
- `plotpt()` checks geographic limits, normalizes, handles cuts, and calls `doproj()`.
- `doproj()` applies projection, optional reflection, polygon clipping, centering, rotation, scaling, and integer conversion.
- `getdata()` reads indexed map patches in absolute or differential encoding.
- `dogrid()`, `dobounds()`, `dolimb()` draw graticules, boundaries, and projection limbs.

Cut handling:
- `picut()` and `ckcut()` handle longitude-PI seam crossing.
- `duple()` redraws near-cut segments on both sheets.
- `realcut()` disables cuts when the window does not actually include the seam.

Notable data:
- Global map file list, track list, color/style state, geographic limits/window, clipping polygon equations, scaling/centering state.
- `patch[18][36]` indexes 10-degree tiles.

Behavior notes:
- Uses Plan 9 plotting primitives from `iplot.h`.
- Assumes `sizeof(short) == 2` for binary map data.
- Long segment suppression prevents drawing lines across projection cuts.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/map/map.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/map/map.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/map/map.h

Shared interface for the map command and libmap projections.

Defines:
- Constants: `PI`, `TWOPI`, `RAD`, earth eccentricity constants, `FUZZ`, `UNUSED`.
- Coordinate types:
  - `struct coord`: radians plus cached sine/cosine.
  - `struct place`: normalized latitude and west longitude.
- Projection type: `typedef int (*proj)(struct place *, double *, double *)`.
- `struct index`: projection registry entry with name, factory, parameter count, cut handler, pole flags, spheroid flag, and limb iterator.

Declares:
- Projection factories and low-level `X...` projection functions.
- Limb/cut functions.
- Complex arithmetic helpers.
- Orientation/coordinate helpers.
- Renderer callbacks exported by `map.c`.
- Global `projection`.

Notes:
- `#pragma lib` and `#pragma src` wire Plan 9 build tooling to `libmap.a`.
- Several comments mark projections “not in library,” indicating command-local or unavailable projections in the wider source tree.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/map/map.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/map/route.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/map/route.c

Implements `route`, a helper that computes `map -o` orientation options for a great-circle route between two lat/lon points.

Behavior:
- Usage: `route [-t] [-i] lat lon lat lon`.
- Without `-t`, prints suggested `-o` and `-w` options to orient a standard projection so the two points lie on the equator around the prime meridian.
- With `-t`, prints intermediate great-circle track coordinates suitable for `map -t`.
- `-i` flips the route top-to-bottom via `inv`.

Key functions:
- `dorot()` wraps `deg2rad` and a transform callback.
- `rotate()` applies `normalize`.
- `rinvert()` applies `invert`.
- `doroute()` derives route pole and twist through repeated orientation/rotation steps.

Dependencies:
- Uses `orient`, `normalize`, and `invert` from `zcoord.c`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/map/route.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/map/sqrt.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/map/sqrt.c

Provides a local floating-point `sqrt()` implementation using Newton iteration.

Behavior:
- Returns `0` for negative or zero input.
- Uses `frexp()` to derive initial mantissa/exponent scaling.
- Adjusts exponent to be even, scales initial estimate with powers of `1L<<30`, then performs five Newton updates.

Notes:
- Comment says it will not work on one’s-complement machines.
- This is an old portability support file for environments lacking suitable math library behavior.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/map/sqrt.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/map/symbol.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/map/symbol.c

Loads and draws user-defined map symbols for the `map -y` option.

Key data:
- `struct symb` stores symbol point coordinates, name, and segment/end flags.
- Up to `NSYMBOL` symbol definitions are stored in `symbol[]`.
- `halfrange` controls scaling from symbol source coordinates to plot space.

Key functions:
- `getsyms()` opens and reads a symbol file.
- `getsymbol()` parses symbol definitions, ranges, moves, and vertices.
- `getrange()` parses range commands.
- `putsym()` projects anchor point, computes symbol rotation, and draws symbol vectors using `cpoint()`.
- `setrot()` aligns symbols upright, normal, or reversed relative to projected local north.
- `dorot()` applies the 2x2 rotation/scale matrix.

Dependencies:
- Calls `doproj`, `cpoint`, `projection`, and `hypot`.
- Uses `iplot` drawing through map’s renderer callbacks.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/map/symbol.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/mc.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/mc.c

Implements `mc`, a columnating command.

Behavior:
- Reads lines from stdin or files into a rune buffer.
- Computes display width of each line using either rune count or actual font metrics.
- Lays words/lines into columns within `linewidth`.
- Option `-` breaks/flushes on colon-newline patterns.
- Numeric `-WIDTH` sets output width.
- `-t` handling is present but initializes `tabflag` to `0`; tabs are enabled automatically only when display/font width is detected.

Key functions:
- `readbuf()` reads runes, expands tabs to spaces, and handles colon-triggered flushes.
- `scanwords()` splits buffered lines into null-terminated words.
- `columnate()` computes column count and emits formatted output.
- `getwidth()` discovers Acme/window font and width to use pixel widths.
- `morechars()` grows the rune buffer.

Dependencies:
- Plan 9 `Bio`, `draw`, font APIs, `/dev/acme`, `/dev/window`, and environment variables `font`/`tabstop`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/mc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/md5sum.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/md5sum.c

Implements an MD5 checksum command.

Key functions:
- `digestfmt()` installs `%M` formatting for MD5 byte arrays as lowercase hex.
- `sum()` streams an fd through Plan 9 `md5()`, reports read errors, and prints digest with optional filename.
- `main()` parses no options, installs formatter, and processes stdin or each named file.

Dependencies:
- `<libsec.h>` MD5 APIs.
- Plan 9 `Bio` is included but not materially used.

Output:
- Stdin: `<digest>`.
- Files: `<digest>\t<name>`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/md5sum.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/mk/arc.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/mk/arc.c

Manages `Arc` objects in the `mk` dependency graph.

Key functions:
- `newarc()` allocates and initializes an arc from a prerequisite node and rule, copying stem and regexp matches.
- `dumpa()` prints debug information for an arc and nested node.
- `nrep()` reads variable `NREP` to set allowed rule-repetition count, defaulting to at least `1`.

Dependencies:
- `Malloc`, `rcopy`, `symlook`, and debug output through `bout`.
- Arc fields are defined in `mk.h`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/mk/arc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/mk/archive.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/mk/archive.c

Implements archive member timestamp support for `mk` targets of the form `archive(member)`.

Key functions:
- `atimeof(force, name)` loads/caches member mtimes and returns the requested member time.
- `atouch(name)` opens or creates an archive and updates a member timestamp if known.
- `atimes(ar)` reads Plan 9 archive headers and installs `S_TIME` symbols for members.
- `type(file)` checks whether a file is an archive and warns once for missing archives.
- `split(name, &member)` parses `archive(member)` and validates archive type.

Behavior notes:
- Long member names are truncated to `SARNAME` for lookup.
- Member mtimes are clamped below aggregate archive mtime to avoid confusing dependency ordering.
- Archive creation writes `ARMAG`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/mk/archive.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/mk/bufblock.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/mk/bufblock.c

Provides reusable growable byte buffers for `mk`.

Key functions:
- `newbuf()` returns a buffer from freelist or allocates a new `QUANTA`-sized buffer.
- `freebuf()` puts a buffer on the freelist.
- `growbuf()` grows current capacity, optionally swapping with a larger freelist buffer.
- `bufcpy()` appends raw bytes.
- `insert()` appends one byte.
- `rinsert()` appends one UTF rune.

Behavior notes:
- `growbuf()` preserves existing contents and adjusts `current`.
- Buffers are not freed back to the OS during normal operation; they are pooled.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/mk/bufblock.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/mk/env.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/mk/env.c

Builds the environment passed to recipe commands.

Key data:
- `myenv[]` lists internal mk variables such as `target`, `stem`, `prereq`, `pid`, `nproc`, `newprereq`, `alltarget`, `newmember`, and `stem0` through `stem9`.
- Global `Envy *envy` stores name-to-word-list values.

Key functions:
- `initenv()` registers internal variables and imports OS environment via `readenv()`.
- `execinit()` rebuilds `envy` from internal variables plus exported mk variables.
- `buildenv(Job *j, int slot)` updates job-specific variables for a running recipe.
- `envinsert()`, `envupd()`, and `ecopy()` manage entries.

Behavior notes:
- `newmember` extracts archive member names from new prerequisites.
- Regex rules populate `stem0` through `stem9` from match captures.
- Variables marked `S_NOEXPORT` or internal variables are skipped during generic export copying.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/mk/env.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/mk/file.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/mk/file.c

Handles file and archive modification times for `mk`.

Key functions:
- `mtime(name)` delegates to `mkmtime(name, 1)`.
- `timeof(name, force)` handles archive member targets, cache lookup, and forced stat.
- `touch(name)` updates file/archive time unless `nflag` is set.
- `delete(name)` removes regular files and refuses archive members.
- `timeinit(s)` implements `mk -w` by assigning current time to listed targets.

Dependencies:
- Archive helpers `atimeof` and `atouch`.
- Plan 9-specific `mkmtime` and `chgtime` from `plan9.c`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/mk/file.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/mk/fns.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/mk/fns.h

Function prototype header for `mk`.

Coverage:
- Declares parser, rule, graph, job, environment, shell, word-list, symbol-table, archive, file-time, and platform functions.
- Exposes constructors like `newarc`, `newbuf`, `newjob`, `newword`.
- Exposes execution functions like `run`, `waitup`, `execsh`, `pipecmd`.
- Exposes utility functions like `Malloc`, `Realloc`, `charin`, `wtos`, `varsub`.

Role:
- Included at the end of `mk.h`, making it the central cross-module interface for the build system.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/mk/fns.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/mk/graph.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/mk/graph.c

Builds and validates the dependency graph for a target.

Key functions:
- `graph(target)` applies rules, checks cycles, prunes vacuous branches, rejects ambiguity, and applies attributes.
- `applyrules()` recursively matches explicit and meta rules, expands stems/regex substitutions, and creates arcs.
- `vacuous()` removes meta-rule paths that do not lead to probable targets.
- `cyclechk()` detects dependency cycles.
- `ambiguous()` rejects multiple conflicting recipes.
- `attribute()` propagates rule attributes into node flags.
- `newnode()` creates and caches a node with initial file time.
- `dumpn()` supports graph debugging.

Behavior notes:
- Rule recursion is bounded by per-rule counters from `rulecnt()` and `NREP`.
- Meta rules support both `%`/`&` patterns and regexp rules.
- Virtual nodes force time to `0`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/mk/graph.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/mk/job.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/mk/job.c

Constructs and dumps `Job` records.

Key functions:
- `newjob()` allocates a job, stores the rule, target node list, stem, regex matches, prerequisite lists, target lists, and initializes `nproc = -1`.
- `dumpj()` prints one or all jobs for debugging, including target, alltarget, prereq, and new prereq lists.

Role:
- Jobs are produced by `recipe.c` and consumed by `run.c`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/mk/job.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/mk/lex.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/mk/lex.c

Line assembly and lexical support for `mk` parser.

Key functions:
- `assline()` reads logical mkfile lines, skipping empty lines/comments and eliding escaped newlines.
- Handles quotes, backslashes, double quotes, and backquoted shell command substitutions.
- `bquote()` executes backquoted commands via `execsh()` and inserts output into the current buffer.
- `nextrune()` reads runes and treats escaped newlines either as elided or blank.

Behavior notes:
- Comments consume through newline; if the last char before newline was backslash, escaped-newline behavior is propagated.
- Backquote supports rc-style `` `{ ... } `` and sh-style `` `...` `` forms.
- Errors call `Exit()` after reporting syntax context.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/mk/lex.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/mk/main.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/mk/main.c

Main entry point for Plan 9 `mk`.

Responsibilities:
- Parses command-line flags and assignment arguments.
- Initializes symbol table, environment, mk variables, and parsed mkfiles.
- Determines default or explicit targets and invokes `mk()`.
- Supports profiling, debug dumping, what-if times, and usage accounting.

Important flags:
- `-a` force all, implies `-i`.
- `-d[peg]` debug parser/graph/exec.
- `-e` explain.
- `-f file` mkfile.
- `-i`, `-k`, `-n`, `-s`, `-t`, `-u`, `-w`.

Key variables:
- Global flags, `rules`, `metarules`, `target1`, `jobs`, `patrule`, and output `bout`.

Behavior notes:
- Assignment args are written into a temporary file and parsed as override assignments.
- `MKFLAGS` and `MKARGS` are synthesized.
- With multiple explicit targets and no `-s`, it creates a virtual aggregate rule.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/mk/main.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/mk/match.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/mk/match.c

Implements pattern matching and substitution for non-regexp meta rules.

Key functions:
- `match(name, template, stem)` matches templates containing `%` or `&`.
- `subst(stem, template, dest, dlen)` substitutes stem into templates at `%` or `&`.

Behavior notes:
- `&` is stricter than `%`: matched stem must not contain `.` or `/`.
- Matching checks literal prefix before wildcard and literal suffix after wildcard.
- Substitution is bounded by destination length and null-terminates output.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/mk/match.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/mk/mk.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/mk/mk.c

Core build algorithm for `mk`.

Key functions:
- `mk(target)` builds dependency graph, clears made flags, repeatedly schedules work, waits for children, and reports up-to-date status.
- `clrmade()` resets graph nodes to `NOTMADE`.
- `work(node, parent, parc)` recursively determines readiness/out-of-date status and invokes recipes.
- `update(fake, node)` updates node status/time after recipe completion or failure.
- `outofdate(node, arc, eval)` compares times or invokes custom `P` program comparator.
- `pcmp()` runs custom comparison program via `pipecmd()`.

Behavior notes:
- Supports “pretending” missing intermediate files are made when safe.
- Equal timestamps are treated as out-of-date to avoid races.
- `-k` allows continuing after errors by marking failed work as being made/fake.
- Archive missing members are considered out-of-date.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/mk/mk.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/mk/mk.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/mk/mk.h

Central definitions for Plan 9 `mk`.

Defines:
- `Bufblock`, `Word`, `Envy`, `Rule`, `Arc`, `Node`, `Job`, `Symtab`.
- Rule attribute bits: `META`, `UPD`, `QUIET`, `VIR`, `REGEXP`, `NOREC`, `DEL`, `NOVIRT`, etc.
- Node flag bits: `VIRTUAL`, `CYCLE`, `READY`, `CANPRETEND`, `PRETENDING`, `NOTMADE`, `BEINGMADE`, `MADE`, `PROBABLE`, `VACUOUS`, etc.
- Symbol-table spaces for variables, targets, file times, nodes, archive aggregates, exported variables, and internal variables.
- Debug flags and parser helpers.

Role:
- Brings in Plan 9 headers, regexp support, global variable declarations, macros, and `fns.h`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/mk/mk.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/mk/mkconv -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/mk/mkconv

An `rc` script for converting make-style files toward Plan 9 `mk` syntax.

Behavior:
- Writes input through `tee` to a temp file.
- Runs `sed` rewrites for:
  - Parenthesized make variables to mk/rc-style forms.
  - Leading recipe command markers.
  - Error-handling recipe prefixes.
  - Pattern variables such as `$%`, `$@`, `$^`, `$?`.
  - `:&` to `:`.
- Warns to stderr when recipes contain `cd` or `make`, since those need manual review.
- Cleans temp file on exit or interrupt.

Role:
- Migration helper, not part of the `mk` binary.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/mk/mkconv -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/mk/parse.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/mk/parse.c

Parses mkfiles into variables and rules.

Key functions:
- `parse(f, fd, varoverride)` reads logical lines and dispatches include, program include, rule, or assignment handling.
- `addrules()` installs rules and records first non-meta target as default target.
- `rhead()` parses a line head, separator, attributes, optional comparison program, head words, and tail words.
- `rbody()` reads indented recipe body lines.
- `ipush()` / `ipop()` track nested input file/line context.

Supported forms:
- `<` include file.
- `<|` include output of program.
- `:` rules with attributes like `D`, `E`, `n`, `N`, `P`, `Q`, `R`, `U`, `V`.
- `=` assignments, including `U` no-export assignment attribute.

Dependencies:
- `assline`, `stow`, `setvar`, `addrule`, `execsh`, `pipecmd`, and shell-specific `charin`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/mk/parse.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/mk/plan9.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/mk/plan9.c

Plan 9 platform support for `mk`.

Key areas:
- Environment import/export through `/env`.
- Process creation and shell execution with `rfork`, `fork`, pipes, and `/bin/rc`.
- Note/interrupt handling.
- File time operations and directory bulk mtime caching.
- Regex match capture copying.

Key functions:
- `readenv()` imports Plan 9 environment files as mk variables.
- `exportenv()` writes recipe environment values back to `/env`.
- `execsh()` runs shell recipes, optionally capturing output into a buffer.
- `pipecmd()` runs a shell command with optional output pipe.
- `Exit()` waits for children and exits with error.
- `catchnotes()` installs interrupt handling.
- `chgtime()` touches or creates files.
- `mkmtime()` stats files with directory-level cache warming via `bulkmtime()`.
- `rcopy()` copies regexp capture strings.

Notes:
- Shell defaults: `/bin/rc`, name `rc`.
- Uses `RFENVG` so environment changes are isolated to child copies.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/mk/plan9.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/mk/rc.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/mk/rc.c

Shell-syntax support for `mk` when using Plan 9 `rc`.

Key globals:
- `termchars = "'= \t"` for assignment parsing.
- `shflags = "-I"` for non-interactive rc.
- `IWS = '\1'`.

Key functions:
- `charin()` finds separator characters while respecting single quotes and `${...}` variable generators.
- `expandquote()` expands rc single-quoted strings.
- `escapetoken()` reads quoted tokens during lexical parsing.
- `copyq()` copies quoted and backquoted strings for shell-printing.

Behavior notes:
- Single quotes escape by doubling.
- Backslash and double-quote are not real rc escapes here; they are preserved.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/mk/rc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/mk/recipe.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/mk/recipe.c

Selects and prepares recipes for execution.

Key functions:
- `dorecipe(Node *node)` chooses the applicable rule recipe, handles no-recipe cases, builds target lists, gathers prerequisite and new-prerequisite lists, marks nodes `BEINGMADE`, and queues a `Job`.
- `addw()` appends unique word entries.

Behavior notes:
- For multi-target rules, builds a linked node list of targets needing the recipe.
- Regex rules use the current node as target/alltarget.
- Virtual or no-recipe nodes are updated without command execution.
- `-t` touches non-virtual targets instead of running recipes.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/mk/recipe.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/mk/rule.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/mk/rule.c

Stores and manages parsed build rules.

Key functions:
- `addrule()` creates or reuses a `Rule`, inserts it into target hash chain, and appends it to `rules` or `metarules`.
- Detects meta rules via regexp attribute or `%`/`&` in target.
- Compiles regexp rules with `regcomp`.
- `dumpr()` prints rule lists.
- `rcmp()` compares target and tail for rule reuse.
- `rulecnt()` allocates per-rule recursion counters.

Behavior notes:
- Each rule gets increasing `rule` index.
- Reused rules update fields but are not re-appended.
- Rule chains support multiple rules per explicit target.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/mk/rule.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/mk/run.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/mk/run.c

Schedules and monitors recipe jobs.

Key data:
- `events[]` maps process slots to active jobs.
- `jobs` queue stores pending jobs.
- `Process` list stores unexpected child statuses.
- `nproclimit` is controlled by `NPROC`.

Key functions:
- `run()` appends a job and schedules if slots are available.
- `sched()` builds environment, prints recipe, handles `-n`/`-t`, or executes shell command.
- `waitup()` waits for children, handles errors, updates targets, schedules more jobs.
- `nproc()`, `nextslot()`, `pidslot()` manage process slots.
- `killchildren()` posts notes to children on interrupt.
- `usage()` / `prusage()` track time spent at each concurrency level.

Behavior notes:
- Recipe failures delete targets marked `DELETE`.
- `-k` records errors and continues; otherwise exits.
- `NOMINUSE` suppresses `rc -e` behavior.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/mk/run.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/mk/shprint.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/mk/shprint.c

Expands selected mk variables into shell recipe text for printing and execution.

Key functions:
- `shprint()` scans recipe text, expanding `$name` and `${name}` via `vexpand()` while preserving quoted strings through `copyq()`.
- `mygetenv()` only expands internal variables and variables set in the mkfile.
- `front()` shortens a command string for error messages to a few fields.

Behavior notes:
- Variables not internal or mk-set are left intact for the shell.
- `wtos()` output is freed after insertion.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/mk/shprint.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/mk/symtab.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/mk/symtab.c

Implements `mk`’s hash-based symbol table.

Key functions:
- `syminit()` clears all hash buckets.
- `symlook(sym, space, install)` finds or optionally installs a symbol in a namespace.
- `symdel(sym, space)` removes matching symbols.
- `symtraverse(space, fn)` applies a callback to symbols in one namespace.
- `symstat()` prints bucket length distribution.

Behavior notes:
- Hash combines namespace and string bytes with multiplier `79`.
- Symbols are separated by `space`, allowing same name in different logical tables.
- Comments acknowledge memory leaks in deletion paths.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/mk/symtab.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/mk/var.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/mk/var.c

Small variable utilities for `mk`.

Key functions:
- `setvar(name, value)` installs a variable in `S_VAR` and marks it as `S_MAKEVAR`.
- `dumpv()` prints all variables.
- `print1()` formats one variable’s word list.
- `shname()` returns the first non-shell-word character in a name.

Role:
- Used by parser, environment import, and shell expansion code.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/mk/var.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/mk/varsub.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/mk/varsub.c

Implements mk variable substitution and pattern substitution.

Supported forms:
- `$name`
- `${name}`
- `${name: A%B=C%D}` style substitutions using `%` or `&`.

Key functions:
- `varsub()` dispatches braced or simple variable expansion.
- `varname()` parses variable names.
- `varmatch()` looks up non-empty variable values.
- `expandvar()` handles `${name}` and substitution forms.
- `extractpat()`, `subsub()`, and `submatch()` apply prefix/suffix pattern substitutions across word lists.

Behavior notes:
- Missing variables in substitution form produce the variable name as a word.
- Pattern substitution preserves unmatched words.
- Uses `charin()` so parsing respects rc quoting and `${...}` nesting.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/mk/varsub.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/mk/word.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/mk/word.c

Manages `Word` linked lists and parses strings into words.

Key functions:
- `newword()`, `wdup()`, `delword()` allocate/copy/free words.
- `stow()` splits a string into a word list.
- `wtos()` joins a word list with a separator.
- `nextword()` parses one word, handling whitespace, quotes, escapes, and `$` variable expansion.
- `dumpw()` prints word lists for debugging.

Behavior notes:
- Variable expansion can splice multiple words into the output list.
- If a variable expansion is empty at the start of a word, parsing restarts.
- Uses `Bufblock` for incremental UTF-aware construction.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/mk/word.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/mkdir.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/mkdir.c

Implements Plan 9 `mkdir`.

Behavior:
- Usage: `mkdir [-p] [-m mode] dir...`.
- Default mode is `0777`.
- `-m` parses octal mode and rejects values above `0777`.
- `-p` creates missing path components.

Key functions:
- `makedir()` checks existence, creates with `DMDIR | mode`, and records error state.
- `mkdirp()` walks slash-separated path prefixes and creates missing directories.
- `main()` parses flags and applies selected behavior.

Notes:
- Without `-p`, existing paths are reported as errors.
- Exit status is `"error"` if any create failed.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/mkdir.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/mntgen.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/mntgen.c

Implements `mntgen`, a synthetic 9P filesystem that dynamically creates empty directories when walked.

Behavior:
- Usage: `mntgen [-s srvname] [mtpt]`.
- Mounts a read-only directory service at `mtpt` or `/n`.
- Walking a non-existent name at root creates a new directory entry.
- Child directories are empty.
- Directories are removed from the table when the last fid referencing them is clunked.

Key structures:
- `Tab` stores name, qid path, creation time, and ref count.
- Qid paths are 48-bit MD5-derived hashes of names.

9P handlers:
- `fsattach`, `fsopen`, `fsread`, `fsstat`, `fswalk`, `fsclunk`.

Notes:
- Root qid path is `0`.
- Name hash collisions are rejected.
- Files are read-only; only directory reads/stat/walks are meaningful.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/mntgen.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/mount.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/mount.c

Implements Plan 9 `mount`.

Behavior:
- Usage: `mount [-a|-b] [-cnq] [-k keypattern] /srv/service dir [spec]`.
- Opens service file read-write, optionally authenticates with `p9any`, then calls `mount()`.
- Flags map to mount options: `MAFTER`, `MBEFORE`, `MCREATE`, `MCACHE`.
- `-n` disables authentication.
- `-q` suppresses errors and exits success on open/mount failure.
- Optional `spec` defaults to empty string when argc is 2.

Key functions:
- `amount0()` performs `fauth`, `auth_proxy`, and `mount`.
- `catch()` reports notes and exits.
- `usage()` prints syntax.

Notes:
- Rejects combining `-a` and `-b`.
- Uses global `keyspec`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/mount.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ms2html.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ms2html.c

Single-file converter from troff/ms input to HTML.

Major responsibilities:
- Reads input from stdin with nested `.so` include support.
- Expands troff strings, number registers, macros, macro arguments, and conditionals.
- Translates many ms/troff macros into old-style HTML tags.
- Converts special characters/entities and troff escapes.
- Generates auxiliary GIFs for equation/table/picture blocks via `troff2gif` and PostScript pictures via `ps2gif`.

Key data:
- Macro dispatch tables `gtab` and `gtabif`.
- Entity mapping table for HTML/numeric entities and Unicode runes.
- Troff special-character mapping table `tspec`.
- Font stack for `<B>`, `<I>`, `<TT>`, and mixed fonts.
- String/number-register/macro linked lists.
- Source stack for includes, string stack, and macro expansion stack.

Important functions:
- `doconvert()` main conversion loop, prints `<html>`, dispatches directives at line start, emits body text, closes open structures.
- `getrune()` and `getnext()` provide logical input with string/macro expansion and escape translation.
- `dodirective()` parses directive lines, invokes user macros, conditional handlers, or built-in macro handlers.
- `copyline`, `copyarg`, `parseargs` parse directive arguments.
- `g_PP`, `g_LP`, `g_IP`, `g_SH`, `g_NH`, `g_TL`, font handlers, list handlers, quote/display handlers map ms constructs to HTML.
- `g_de`/`g_rm` define/remove macros.
- `g_ds`/`g_as` define/append strings; `g_nr` sets number registers.
- `g_if`, `g_ie`, `g_el` evaluate conditional bodies.
- `g_startgif()` captures `EQ`, `TS`, `PS` blocks and invokes `troff2gif`.
- `g_BP()` embeds GIF/JPEG directly or converts other pictures through `ps2gif`.

Behavior notes:
- Uses old HTML tags such as `<DL>`, `<TT>`, `<PRE>`, `<center>`.
- `quiet` defaults to suppress ignored-macro warnings; `-q` turns warnings on by setting `quiet = 0`.
- Always appends an Alcatel-Lucent copyright footer.
- Conditional arithmetic supports simple integer operators and comparisons.
- Some handlers are intentionally ignored or “not yet supported.”
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ms2html.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/mtime.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/mtime.c

Prints file modification times.

Behavior:
- Usage: `mtime file...`.
- For each path, calls `dirstat()`.
- Prints `mtime` as an unsigned decimal field plus filename.
- Reports stat errors to stderr and exits with `"errors"` if any failed.

This is a small diagnostic command around Plan 9 `Dir.mtime`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/mtime.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/mug.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/mug.c

Interactive face/icon crop and tone-adjustment tool.

Purpose:
- Reads an image, lets the user select a square region, downsample it to a 48x48 grayscale face, adjust black/white/gamma/depth, save slots, undo, and write output.

Major data:
- `State` stores black/white/stretch/gamma/depth/gamma table/selection rectangle.
- `Face` stores saved thumbnails and their state.
- Global images for original, ramp, current small face, temp GREY8, colors, and saved faces.
- `rdata` stores gamma-corrected source luminance.

Key functions:
- `geometry()` lays out ramp, original image, current thumbnail, and saved face slots.
- `initramp()`, `initclamp()`, `initval2cmap()`, `setgtab()` prepare tone controls.
- `process()` box-filters a selected square into 48x48, applies black/white/gamma mapping, and dithers to target grayscale depth.
- `drawscreen()`, `drawface()`, `drawrampbar()`, `moveframe()` update UI.
- `move()` resizes/moves the square selection while preserving square shape.
- `dragface()` supports dragging thumbnails between slots.
- `saveface()`, `mark()`, `undo()`, `writeface()` manage state history, saved slots, and output.
- `main()` initializes draw/event systems and runs mouse/menu event loop.

UI:
- Button 3 menu: Reset, Depth, Undo, Write, Exit.
- Button 1 drags selection handles, tone ramp controls, and thumbnails.
- Custom cursors indicate selection region/handle.

Output:
- GREY1/GREY2 output is custom hex rows.
- GREY4/GREY8 output uses Plan 9 `writeimage()`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/mug.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/mv.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/mv.c

Implements Plan 9 `mv`.

Behavior:
- Supports `mv fromfile tofile` and `mv fromfile ... todir`.
- Cleans names before processing.
- If moving a single directory into an existing directory, treats it as rename of directory target.
- Same-directory moves attempt `dirwstat()` rename after removing any existing target.
- Cross-directory/file-server moves fall back to copy then remove for non-directories.

Key functions:
- `mv()` stats source and calls `mv1()`.
- `mv1()` resolves destination path, detects same file/dir, renames or copies, preserves mode and mtime where possible.
- `copy1()` copies file contents.
- `split()` splits a path into directory and final element, with special handling for `..`.
- `samefile()` compares qid/dev/type.
- `hardremove()` repeatedly removes a target, exiting on first failure.

Notes:
- Directories are not copied across directories; only renamed when possible.
- Append-only targets are removed before create because `create()` will not truncate them.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/mv.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ndb/convDNS2M.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ndb/convDNS2M.c

Serializes internal `DNSmsg`/`RR` structures into DNS wire-format messages.

Key data:
- `Dict` stores up to 64 domain-name compression entries plus unpacked-name buffer and message start pointer.

Primitive packers:
- `psym`/`pstr` length-prefixed strings.
- `pbytes`, `puchar`, `pushort`, `pulong`.
- `pv4addr`, `pv6addr`.
- `pname()` with DNS label encoding and compression-pointer dictionary.

RR serialization:
- `convRR2M()` writes owner, type, class, TTL, RDLENGTH, and type-specific RDATA.
- Supports HINFO, CNAME, mailbox types, NS, MINFO, MX, A, AAAA, PTR, SOA, SRV, TXT, NULL, RP, KEY, SIG, CERT.
- `convQ2M()` writes DNS question owner/type/class.
- `rrloop()` serializes RR lists and counts successful entries.

Top-level:
- `convDNS2M()` zeroes output, serializes question/answer/ns/additional sections, sets truncation flag if packet overflows, then writes DNS header and returns encoded length.

Behavior notes:
- TTL is absolute in cache for non-db records, converted to relative by subtracting `now`.
- SRV target uses string packing, with comment noting RFC 2782 says no compression.
- If compression offset is too large for DNS packet format, logs an error.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ndb/convDNS2M.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ndb/convM2DNS.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ndb/convM2DNS.c

Parses DNS wire-format messages into internal `DNSmsg`/`RR` structures.

Key data:
- `Scan` tracks base/current/end pointers, error text, response code, stop flag, and truncation flag.

Primitive readers:
- `gchar`, `gshort`, `glong`.
- `gv4addr`, `gv6addr`.
- `gsym`, `gstr`, `gbytes`.
- `gname()` decodes domain names with compression pointers and detects pointer loops/bad labels.

RR parsing:
- `convM2RR()` reads resource records, allocates by type, decodes RDATA for supported types, ignores unknown types, and validates consumed RDLENGTH.
- `convM2Q()` parses questions.
- `rrloop()` builds linked RR lists for question, answer, nameserver, and additional sections.

Top-level:
- `convM2DNS(buf, len, m, codep)` parses header counts and sections, records format/truncation conditions, sets `Ftrunc` when needed, and returns an error string when recoverable errors occurred.

Robustness behavior:
- `errtoolong()` treats full-sized UDP payloads as likely truncated even if `Ftrunc` was not set.
- Handles EDNS extended-label byte by stopping parse rather than continuing.
- Detects reserved labels, bad compression pointers, and pointer loops.
- `mstypehack()` compensates for byte-swapped type fields seen from Windows 2000 PTR behavior by setting format response code.
- Allows some known malformed Windows/hints cases without noisy logging.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ndb/convM2DNS.c -->