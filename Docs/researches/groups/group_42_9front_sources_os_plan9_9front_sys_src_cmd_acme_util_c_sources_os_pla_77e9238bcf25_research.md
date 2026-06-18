# Group Research: group_42_9front_sources_os_plan9_9front_sys_src_cmd_acme_util_c_sources_os_pla_77e9238bcf25

Scope checked against `Docs/research_subset_a.md`: `sources/os/plan9/9front` is in subset A. Every listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/acme/util.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/acme/util.c

Utility support for Acme. It covers UTF/Rune conversion, fatal error handling, warning buffering, error window creation, small Rune/string helpers, mouse-position save/restore, checked allocation wrappers, and the heuristic for placing new windows.

Important behavior:
- `cvttorunes` converts byte buffers into Rune buffers while detecting embedded NULs.
- `errorwin`, `errorwinforwin`, `warning`, and `flushwarnings` route diagnostics into per-directory `+Errors` windows.
- `makenewwindow` chooses the active column and either uses visible blank space or splits the largest suitable window.
- Allocation helpers abort through Acme’s `error` path, so callers generally assume success.

Dependencies are Acme globals and helpers from `dat.h`/`fns.h`, including `row`, `Column`, `Window`, `Text`, buffers, and the draw/thread libraries.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/acme/util.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/acme/wind.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/acme/wind.c

Implements Acme window lifecycle, rendering, locking, tag generation, dirty tracking, event queuing, and window metadata operations.

Important behavior:
- `wininit` creates tag/body `Text` objects, optionally cloning body state and tag contents.
- `winresize` recomputes tag/body rectangles, redraws buttons, and protects mouse placement during tag expansion.
- `winlock` locks all windows sharing the same file; `winunlock` releases in reverse order to avoid file/text mutation hazards.
- `winsettag1` reconstructs command tags including `Del`, `Snarf`, `Undo`, `Redo`, `Put`, `Get`, and the user-editable bar suffix.
- `winaddincl` validates include directories and stores them on the window.
- `winevent` appends Acme event protocol messages and wakes blocked event readers.

The file is tightly coupled to Acme’s shared `File`, `Text`, `Column`, draw-state, and event model.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/acme/wind.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/acme/xfid.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/acme/xfid.c

Handles Acme’s 9P request operations for window files and global files such as index/log/cons. It translates file operations on `/mnt/acme` into text edits, selections, control commands, and event traffic.

Important behavior:
- `xfidopen`, `xfidclose`, `xfidread`, and `xfidwrite` implement per-qid behavior for `addr`, `data`, `xdata`, `body`, `tag`, `ctl`, `event`, `rdsel`, `wrsel`, and edit output files.
- Writes to `addr` parse Acme address syntax and update `w->addr`; reads from `data` advance Rune positions.
- `fullrunewrite` preserves incomplete UTF-8 sequences across write calls.
- `xfidctlwrite` parses control commands such as `lock`, `unlock`, `clean`, `dirty`, `name`, `font`, `dump`, `delete`, `del`, `get`, `put`, `dot=addr`, `addr=dot`, `limit=addr`, `nomark`, `menu`, `noscroll`, `cleartag`, and `scratch`.
- `xfideventread` blocks until window events arrive or a flush/delete wakes it.
- `xfidindexread` synthesizes Acme’s global window index.

The critical invariants are window locking, Rune/UTF byte boundary handling, and preserving shared-file state across cloned windows.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/acme/xfid.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/alarm.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/alarm.c

Small command wrapper that runs another command and delivers an alarm note after a timeout.

Important behavior:
- Usage is `alarm time command [arg ...]`.
- Parses seconds with optional millisecond fraction and calls `alarm(t)` in milliseconds.
- Forks the target command in a new process sharing memory/render state as configured by `rfork`.
- The note handler reposts received notes to the process group, then uses default note handling.
- If direct `exec` fails, it retries under `/bin`.

The program is Plan 9 specific because it relies on notes, `rfork`, `postnote`, and `wait`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/alarm.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ar.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ar.c

Portable ASCII-format archive tool implementing Plan 9 `ar` operations: replace/update, delete, extract, table, print, move, and quick append.

Important behavior:
- Uses up to three logical temp streams: members before pivot, moved/inserted members, and members after pivot.
- Temp streams are kept in memory as member chains and spill to disk when allocation fails.
- Reads and writes archive headers field-by-field using the `HEADER_IO` macro.
- Regenerates `__.SYMDEF` for homogeneous object archives and detects duplicate text symbols.
- Supports pivot insertion with `a`, `b`, and `i`, verbose output, update-if-newer, and preserve-time extraction.

Key dependencies are Plan 9 `bio`, `ar.h`, and `mach` object-symbol parsing.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ar.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/archfs.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/archfs.c

A 9P filesystem that mounts mkfs-style archive files as a read-only tree.

Important behavior:
- `gethdr` parses archive header lines into file name, mode, uid, gid, mtime, and length.
- `createpath` creates intermediate directories and final files in an in-memory 9P tree.
- Each file’s aux pointer stores its archive offset and length.
- `fsread` seeks into the archive and serves requested bytes.
- `main` builds the tree from the archive, then `postmountsrv`s it, defaulting to `/mnt/arch`.

This is a compact example of Plan 9 lib9p file-server construction over an archive backing file.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/archfs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ascii.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/ascii.c

ASCII/Latin-1 table and conversion utility.

Important behavior:
- With no operands, prints a table of characters in the selected base.
- Supports 128 or 256 character tables via `-8`.
- Supports hex, octal, decimal, or arbitrary base 2-36.
- Converts numeric text to character names, or input characters to numeric values.
- `-c`/`-t` switch character-output modes, with `-t` stripping to raw bytes.

The file is self-contained except for Plan 9 `bio` output helpers.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/ascii.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/astro/astro.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/astro/astro.h

Shared declarations for the `astro` astronomical event program.

Important contents:
- Defines object samples (`Obj1`), object descriptors (`Obj2`), occultation interpolation state (`Occ`), event records, calendar time state, and lunar coefficient table entries.
- Declares global ephemeris state: observer location, time, nutation, Sun/Earth vectors, orbital elements, current object coordinates, and output/catalog variables.
- Declares all cross-module functions for date parsing, planet/moon/sun computation, coordinate transforms, event search, occultations, output formatting, and table summation.

The program is designed around shared globals rather than passing large state objects between modules.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/astro/astro.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/astro/comet.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/astro/comet.c

Computes the position for a hard-coded comet element set, currently C/2002 C1 Ikeya-Zhang, with older comet elements retained as commented alternatives.

Important behavior:
- Loads perihelion time, distance, eccentricity, inclination, argument of perihelion, and node into global orbital state.
- Caps eccentricity at `.999` because the solver does not handle hyperbolic orbits.
- Solves Kepler’s equation iteratively, derives true anomaly, radius, ecliptic longitude/latitude, magnitude, and motion.
- Finishes through common `helio()` and `geo()` transforms.

This is a special-case object provider in the same style as planet modules.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/astro/comet.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/astro/cosadd.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/astro/cosadd.c

Shared periodic-series evaluator for the astronomy modules.

Important behavior:
- `icosadd` selects the active coefficient and integer-multiplier tables.
- `cosadd` and `sinadd` iterate coefficient pairs until a zero sentinel and add cosine/sine terms.
- Variadic arguments are the base angular arguments multiplied by signed byte coefficients from `cacp`.

This supports compact encoded perturbation tables in the planet, Sun, and nutation modules.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/astro/cosadd.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/astro/dist.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/astro/dist.c

General helpers for angular distances, rise/set interpolation, event queueing, and small parsing/math utilities.

Important behavior:
- `dist` computes angular separation in arcseconds.
- `rise`, `set`, `solstice`, `betcross`, and `melong` locate events from sampled object points.
- `event` filters by darkness/light constraints and queues event messages.
- `evflush` sorts events, prints them, and supports significant-event wording.
- `rline`, `pyth`, and `skip` provide input and numerical helpers.

This file is central to turning sampled ephemeris data into human-readable event output.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/astro/dist.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/astro/geo.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/astro/geo.c

Converts geocentric equatorial coordinates into topocentric equatorial and horizon coordinates for the configured observer.

Important behavior:
- Uses `alpha`, `delta`, `hp`, and `semi`.
- Computes local hour angle, applies diurnal parallax using geocentric latitude and Earth radius, then sets `ra`, `decl2`, `semi2`, `az`, and `el`.
- Converts azimuth/elevation to degrees at the end.

This is the final observer-location transform used by Sun, Moon, planets, stars, and satellites.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/astro/geo.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/astro/helio.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/astro/helio.c

Converts heliocentric ecliptic object coordinates into geocentric equatorial coordinates.

Important behavior:
- Uses object `lambda`, `beta`, `rad`, `motion`, and the Sun/Earth vector globals.
- Applies light-time correction, annual parallax, approximate aberration, nutation, and obliquity transform.
- Sets `alpha`, `delta`, `rp`, `hp`, and adjusts `semi` and magnitude.

This is the shared bridge from orbital element calculations to apparent sky position.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/astro/helio.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/astro/init.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/astro/init.c

Initializes object tables and per-time astronomical state.

Important behavior:
- `objlst` lists Sun, Moon, shadow, planets, Pluto, and comet.
- `init` computes observer geocentric latitude/Earth radius corrections and assigns object names/functions.
- `setime` updates ephemeris time, longitude correction, nutation, Sun position, Earth/Sun vector, and Earth velocity approximation.
- `setobj` snapshots current globals into an `Obj1`.
- `fsun`, `fstar`, and `shad` provide special object computations.

This file wires together all object modules for sampling by `main.c`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/astro/init.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/astro/jup.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/astro/jup.c

Computes Jupiter’s apparent position.

Important behavior:
- Sets Jupiter mean orbital elements from `eday`/`capt`.
- Solves Kepler’s equation, reduces to ecliptic longitude/latitude, applies fixed empirical corrections, and sets angular semi-diameter and magnitude.
- Calls `helio()` and `geo()` for apparent topocentric output.

Perturbation terms are effectively zeroed except for fixed longitude/latitude adjustments.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/astro/jup.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/astro/main.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/astro/main.c

Program entry and command-line/date/location setup for `astro`.

Important behavior:
- Initializes constants, formatters, default period/sample interval, object table, and command-line options.
- Main loop samples all objects across `NPTS+2` time points unless point/distance modes short-circuit.
- `args` handles flags, date input, delta-T input, location input, and eclipse-object selection.
- Defaults location from `/lib/sky/here`, falling back to a hard-coded Bell Labs Murray Hill location.
- `readate`, `readdt`, `readlat`, and `etdate` provide user/date helpers.

This is the scheduler that drives all ephemeris modules and event search.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/astro/main.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/astro/mars.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/astro/mars.c

Computes Mars’s apparent position.

Important behavior:
- Sets Mars orbital elements and solves elliptic orbit.
- Converts to ecliptic coordinates, sets motion and semi-diameter.
- Computes phase-angle based magnitude correction from elongation relative to the Sun.
- Calls common `helio()` and `geo()` transforms.

The module has no perturbation table; perturbation variables are present but zero.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/astro/mars.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/astro/merc.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/astro/merc.c

Computes Mercury’s apparent position.

Important behavior:
- Uses mean orbital elements plus perturbation arguments for Venus, Earth, Jupiter, and Saturn.
- Uses `mercfp`/`merccp` through `cosadd` to compute longitude and radius perturbations.
- Solves Kepler’s equation, reduces to ecliptic coordinates, computes phase magnitude, then calls `helio()`/`geo()`.

This is one of the table-driven inner-planet modules.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/astro/merc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/astro/merct.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/astro/merct.c

Mercury perturbation data tables.

Important contents:
- `mercfp` stores coefficient/phase pairs separated by zero sentinels.
- `merccp` stores signed multipliers for the active base arguments.
- The tables feed `cosadd` calls in `merc.c` for longitude and radius corrections.

This is data-only support for Mercury ephemeris calculations.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/astro/merct.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/astro/moon.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/astro/moon.c

Computes the Moon’s apparent topocentric position and phase.

Important behavior:
- Builds fundamental lunar/solar elements from `eday` and `capt`.
- Applies long-period corrections, Brown-style scaling factors, and large lunar perturbation series from `moontab`.
- Computes longitude, latitude, horizontal parallax, semi-diameter, and phase proxy.
- Converts to equatorial coordinates with nutation/obliquity and then calls `geo()`.
- `sinx` and `cosx` evaluate lunar coefficient terms with eccentricity/inclination/parallax scaling.

This is the most numerically dense object computation in the group.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/astro/moon.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/astro/moont.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/astro/moont.c

Lunar perturbation coefficient table.

Important contents:
- `moontab` is a sequence of coefficient plus four integer argument multipliers.
- Zero rows separate longitude, latitude, node, and parallax term groups consumed by `moon.c`.
- Values are used by `sinx`/`cosx` with lunar argument globals.

This file is data-only and has no executable logic beyond table initialization.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/astro/moont.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/astro/nept.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/astro/nept.c

Computes Neptune’s apparent position using element table values and a generic outer-planet style routine.

Important behavior:
- Interpolates semi-major axis, eccentricity, inclination, node, perihelion longitude, and mean longitude from epoch coefficients.
- Solves elliptic orbit and reduces to ecliptic coordinates.
- Applies fixed longitude/latitude adjustments and computes magnitude using a Saturn-ring-derived block copied from the outer-planet style code.
- Calls `helio()` and `geo()`.

The magnitude comments still refer to Saturn, indicating shared/copied logic rather than Neptune-specific documentation.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/astro/nept.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/astro/nutate.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/astro/nutate.c

Computes nutation, obliquity, and Greenwich sidereal time.

Important behavior:
- Derives lunar and solar fundamental arguments from `eday`/`capt`.
- Uses `nutfp`/`nutcp` tables through `sinadd`/`cosadd`.
- Sets `phi`, `eps`, `dphi`, `deps`, `obliq`, `tobliq`, and `gst`.
- Applies nutation correction to sidereal time.

This state feeds coordinate transforms in `helio`, `moon`, and `geo`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/astro/nutate.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/astro/nutt.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/astro/nutt.c

Nutation coefficient tables.

Important contents:
- `nutfp` contains coefficient/phase pairs grouped by zero sentinels.
- `nutcp` contains integer multipliers for nutation arguments.
- Used by `nutate.c` to compute long and short period terms.

This is data-only support for Earth nutation calculations.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/astro/nutt.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/astro/occ.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/astro/occ.c

Occultation, eclipse, and transit timing helper.

Important behavior:
- `occult` finds local minima in angular separation between two sampled objects.
- Refines candidates first by minute-scale stepping, then by finer interpolation.
- Computes contact times `t1` through `t5` based on apparent semi-diameter sums/differences.
- `set3pt` builds quadratic interpolation coefficients for RA, declination, semi-diameter, and elevation.
- `setpt` evaluates the interpolation; `pinorm` normalizes angle deltas.

Used by `search.c` for Moon occultations, eclipses, and inner-planet transits.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/astro/occ.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/astro/output.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/astro/output.c

Formatting support for `astro` point output.

Important behavior:
- `output` prints object name/SAO id, right ascension, declination, azimuth, elevation, semi-diameter, and Sun/Moon phase magnitude.
- `Rconv` formats radians as hours/minutes/seconds.
- `Dconv` formats radians as signed degrees/minutes/seconds.

Registered by `main.c` with Plan 9 `fmtinstall`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/astro/output.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/astro/pdate.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/astro/pdate.c

Calendar conversion and date/time formatting for `astro`.

Important behavior:
- Converts between internal day count and year/month/day/hour/minute fields.
- Handles Julian/Gregorian transition logic and BCE year adjustment.
- Supports local “kitchen clock” correction via Plan 9 `localtime`/`gmtime`.
- Formats plain and speech-like date/time output.
- `pstime` prints apparent sky/time/location context.
- Contains month and number-word tables.

This file isolates user-facing temporal formatting and calendar arithmetic.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/astro/pdate.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/astro/plut.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/astro/plut.c

Computes Pluto’s apparent position from epoch element coefficients.

Important behavior:
- Interpolates orbital elements, solves elliptic orbit, and reduces to ecliptic coordinates.
- Applies fixed longitude/latitude adjustments.
- Reuses outer-planet magnitude code whose comments refer to Saturn.
- Calls `helio()` and `geo()`.

The file’s structure closely matches `nept.c` and `uran.c`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/astro/plut.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/astro/sat.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/astro/sat.c

Computes Saturn’s apparent position and ring-influenced magnitude.

Important behavior:
- Sets Saturn mean orbital elements and solves elliptic orbit.
- Applies fixed longitude/latitude adjustments.
- Computes Saturn ring geometry relative to Earth and Sun to derive magnitude.
- Calls common `helio()` and `geo()` transforms.

This module is the apparent source for copied ring-magnitude blocks in the outer planet files.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/astro/sat.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/astro/satel.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/astro/satel.c

Artificial satellite pass prediction support.

Important behavior:
- `satels` iterates configured satellite element files in `satlst`, parses element values, and samples passes during dark periods.
- `satel` computes a satellite’s position/elevation from orbital timing, inclination, eccentricity, rotation, and observer geometry.
- `vis` checks sunlight/visibility geometry.
- Generates event records for visible passes, marking significant named passes when configured.

`satlst` is empty in this source, so behavior depends on adding paths to that list.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/astro/satel.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/astro/search.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/astro/search.c

Searches sampled object positions for daily astronomical events.

Important behavior:
- Adds rise/set events for all sampled solar-system objects.
- Adds solstice/equinox and meteor-shower events based on Sun position.
- Detects twilight start/end, Moon phase crossings, Mercury/Venus elongations, Moon occultations, solar/lunar eclipses, and inner-planet transits.
- Optionally searches star occultations and satellite passes.
- Flushes sorted events at the end.

This is the main event synthesis layer over the sampled ephemeris points.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/astro/search.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/astro/star.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/astro/star.c

Transforms catalog star data to apparent current topocentric coordinates.

Important behavior:
- Removes E-terms of aberration, applies proper motion, and converts RA/declination into rectangular coordinates.
- Applies precession from catalog epoch to current epoch.
- Converts into mean ecliptic system, estimates distance from parallax, then calls `helio()` and `geo()`.

Used by `stars.c` when scanning the star catalog for lunar occultations.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/astro/star.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/astro/stars.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/astro/stars.c

Scans a star catalog for possible Moon occultations.

Important behavior:
- Opens `/lib/sky/estartab`.
- Restricts stars by right ascension near the Moon path.
- Parses SAO id, RA, declination, proper motion, parallax, and magnitude from fixed-width catalog lines.
- Calls `star()` and then `occult(&omoon, &ostar, 0)`.
- Emits occultation begin/end events, with darkness/significance flags based on magnitude.

This module is optional and triggered by the `-o` path in event search.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/astro/stars.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/astro/sun.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/astro/sun.c

Computes the Sun’s ecliptic position and apparent properties.

Important behavior:
- Computes Earth/Sun orbital elements and perturbation arguments for Moon and planets.
- Uses `sunfp`/`suncp` tables for anomaly, longitude, latitude, and radius corrections.
- Sets solar radius vector, motion, semi-diameter, and magnitude.
- Does not call `helio()`/`geo()` itself; wrappers such as `fsun` handle apparent transforms.

This provides the base Earth/Sun vector used by other object computations.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/astro/sun.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/astro/sunt.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/astro/sunt.c

Sun perturbation coefficient tables.

Important contents:
- `sunfp` stores coefficient/phase pairs grouped by zero sentinels.
- `suncp` stores corresponding signed argument multipliers.
- Used by `sun.c` through `cosadd` and `sinadd`.

This is data-only support for solar position corrections.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/astro/sunt.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/astro/uran.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/astro/uran.c

Computes Uranus’s apparent position from epoch element coefficients.

Important behavior:
- Interpolates orbital elements, solves Kepler’s equation, and reduces to ecliptic coordinates.
- Applies fixed longitude/latitude corrections.
- Uses the same outer-planet magnitude block as Saturn/Neptune/Pluto style code.
- Calls `helio()` and `geo()`.

The code structure is nearly identical to the Neptune and Pluto modules.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/astro/uran.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/astro/venus.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/astro/venus.c

Computes Venus’s apparent position.

Important behavior:
- Sets Venus mean orbital elements and perturbing planet anomalies.
- Applies long-period mean anomaly terms.
- Uses `venfp`/`vencp` through `cosadd` for longitude, latitude, and radius perturbations.
- Computes phase-angle magnitude and semi-diameter, then calls `helio()` and `geo()`.

This is the table-driven Venus counterpart to Mercury.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/astro/venus.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/astro/venust.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/astro/venust.c

Venus perturbation data tables.

Important contents:
- `venfp` stores coefficient/phase pairs separated into groups by zero sentinels.
- `vencp` stores signed multipliers for Venus/Earth/Mars/Jupiter arguments.
- Used by `venus.c` to compute perturbations.

This is data-only support for Venus ephemeris calculations.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/astro/venust.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/atazz/atazz.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/atazz/atazz.h

Shared declarations for the `atazz` ATA diagnostic/command shell.

Important contents:
- Defines command flavor flags, device state, request/reply command packets, and request execution state.
- Declares formatter functions for signatures, identify data, I/O dumps, SMART, SCT, and logs.
- Defines tables for bit names, text command names, feature-entry decoding, SCT pseudo-registers, and ATA command metadata.
- Declares endian helpers and device/probe entry points.

The header bridges Plan 9 `fis.h` ATA FIS definitions with the command interpreter.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/atazz/atazz.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/atazz/bit.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/atazz/bit.c

Small helper module for ATA diagnostic bit/table formatting and little-endian accessors.

Important behavior:
- `sebtab` appends names for set bits into a buffer.
- `pw`, `pdw`, and `pqw` store 16/32/64-bit little-endian values.
- `w`, `dw`, and `qw` read little-endian values.

Used by `atazz/main.c` and SCT/table command construction.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/atazz/bit.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/atazz/main.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/atazz/main.c

Interactive ATA command shell and diagnostic tool.

Important behavior:
- Opens `/dev/.../raw`, reads device signature and identify data, and stores geometry, sector size, flags, and WWN.
- `issueata`, `issuepkt`, and `issuesct` implement ordinary ATA passthrough, ATAPI inquiry, and SCT command sequencing.
- Provides formatting for identify data, raw I/O data, SMART data/status, SMART logs, SCT status, log page maps, SATA PHY events, and queued page counters.
- Command parser supports named ATA commands, register assignment, SCT feature tables, redirection, command tracing, open/close/probe/help/rfis/dev special commands, and interrupt handling.
- Maintains reusable `Req` state for LBA, sector count, data buffers, raw output, and redirection file descriptors.

This is low-level and can issue destructive ATA writes; command metadata in `tabs.h` determines protocols and formatting.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/atazz/main.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/atazz/probe.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/atazz/probe.c

Device discovery helper for `atazz`.

Important behavior:
- Reads `/dev/sdctl` to discover storage controller prefixes.
- Tries `/dev/<prefix><n>` paths for units 0-9.
- Uses `opendev` with squelched error output to identify ATA-compatible devices.
- Prints device path, sector count, sector size, and WWN.

This is a convenience probe layer over the main open/identify path.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/atazz/probe.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/atazz/tabs.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/atazz/tabs.h

Command and feature tables for `atazz`.

Important contents:
- Register name aliases for ATA FIS fields.
- SMART feature/register tables, SCT action tables, feature-control tables, error-recovery timer tables, write-same tables, and general log page names.
- Human-readable SCT error strings and ATA/SATA feature names.
- Large `atatab` array mapping ATA command codes to flags, packet flags, protocol, optional feature table, formatter, and command name.

This file is mostly declarative metadata consumed by the parser and issuer in `main.c`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/atazz/tabs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/config -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/config

One-line Plan 9 mk configuration fragment.

Important content:
- Sets `BIN=/$objtype/bin/audio`.

This places built audio commands under the architecture-specific audio binary directory.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/config -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/flacdec/flacdec.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/flacdec/flacdec.c

FLAC decoder front-end adapted for Plan 9 audio pipelines.

Important behavior:
- Uses libFLAC stream-decoder callbacks reading from standard input.
- Supports seeking with `-s seconds` by decoding enough metadata to obtain sample rate, then seeking by sample number.
- Converts decoded per-channel FLAC samples into interleaved PCM bytes.
- Starts `/bin/audio/pcmconv -i <fmt>` when sample format changes, piping PCM through it.
- Can suppress output during seek pre-roll.

It depends on the bundled/ported libFLAC API plus Plan 9 libc compatibility headers.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/flacdec/flacdec.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/flacenc/flacenc.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/flacenc/flacenc.c

FLAC encoder front-end for Plan 9 audio pipelines.

Important behavior:
- Reads raw PCM from stdin and writes FLAC to stdout through libFLAC stream encoder callbacks.
- Parses input format with `-i`, including sample rate, channels, sample bits, and endian choice.
- Supports compression level `-l`, padding metadata `-P`, and Vorbis comment tags `-T field=value`.
- Converts packed PCM bytes into signed `FLAC__int32` interleaved samples.
- Initializes encoder metadata and streams until stdin EOF.

This is a focused adapter between Plan 9 audio format strings and libFLAC encoding.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/flacenc/flacenc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/FLAC/all.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/FLAC/all.h

Top-level public libFLAC include and API overview documentation.

Important contents:
- Includes export, assert, callback, format, metadata, ordinal, stream decoder, and stream encoder headers.
- Documents the C and C++ API organization, metadata interface, dependency structure, embedded trimming notes, and porting guide summaries.
- Defines no runtime logic; it is an umbrella include and documentation entry point.

Within this tree, it supports the bundled FLAC decoder/encoder programs.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/FLAC/all.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/FLAC/assert.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/FLAC/assert.h

libFLAC assertion wrapper header.

Important contents:
- In non-`NDEBUG` builds, includes `<assert.h>` and maps `FLAC__ASSERT` to `assert`.
- In release builds, assertion macros compile away.
- `FLAC__ASSERT_DECLARATION` conditionally retains debug-only declarations.

This keeps libFLAC assertions independent of platform-specific assert conventions.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/FLAC/assert.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/FLAC/callback.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/FLAC/callback.h

Public libFLAC I/O callback type definitions.

Important contents:
- Defines opaque `FLAC__IOHandle`.
- Defines read, write, seek, tell, EOF, and close callback signatures.
- Defines `FLAC__IOCallbacks`, bundling those callback pointers.
- Documents 64-bit offset expectations for seek/tell callbacks.

Used by metadata and stream interfaces needing caller-supplied I/O.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/FLAC/callback.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/FLAC/export.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/FLAC/export.h

Public libFLAC export/version header.

Important contents:
- Defines `FLAC_API` for Windows DLL import/export, visibility attributes, or empty default.
- Defines libFLAC API version constants.
- Declares `FLAC_API_SUPPORTS_OGG_FLAC`.

This isolates platform symbol-export mechanics for public libFLAC headers.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/FLAC/export.h -->