# Group Research: group_162_9front_sources_os_plan9_9front_sys_src_cmd_map_map_c_sources_os_plan_8af000ea1769

Scope: `Docs/research_subset_a.md` includes `sources/os/plan9/9front`. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/map/map.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/map/map.c

Implements the `map` command front end: parses projection/options, sets geographic limits/windows/orientation, computes plot scaling, draws grid/borders, reads map datasets, and plots tracks/symbols through the selected projection.

Key behavior:
- Selects a projection from the global `index[]` table, validates projection parameters, and installs projection/cut/limb handlers.
- Handles options for map files, tracks, clipping polygons, grid/window/limit bounds, orientation, colors/styles, reverse x-axis, thinning, and symbol files.
- Reads map data through `.x` patch indexes and packed absolute/differential coordinate records, skipping unseen 10-degree patches.
- Normalizes geographic points, applies windows/limits/cut handling, projects to x/y, clips to optional convex polygon, scales to plot coordinates, and emits `iplot` drawing commands.
- Draws projection limbs, borders, latitude/longitude grids, tracks, text labels, and named symbols.

Important dependencies: `map.h`, `iplot.h`, projection functions from `libmap`, Plan 9 libc/stdio, global `index[]`, `colorcode`, and plot primitives like `openpl`, `vec`, `point`, `text`.

Notable risks:
- Heavy global state means option ordering and projection state interact closely.
- `getshort()` assumes 16-bit little-endian encoded map records and aborts if `short` is not 2 bytes.
- Cut logic and line-length suppression prevent false lines across map discontinuities; small changes can create visual artifacts.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/map/map.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/map/map.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/map/map.h

Defines the shared map projection API and common geographic data structures used by `map`, `route`, symbol rendering, and the projection library.

Key behavior:
- Defines radians/constants, earth eccentricity constants, and `coord`/`place` structures with angle plus cached sine/cosine.
- Defines `proj` as a projection callback taking a `place` and returning projected x/y.
- Defines `struct index`, the projection registry entry with name, constructor, parameter count, cut handler, pole behavior, spheroid flag, and limb iterator.
- Declares projection constructors, special projection functions, cut handlers, complex math helpers, orientation/normalization helpers, symbol helpers, plotting helpers, and the global `projection`.

Important dependencies: Plan 9 map projection library archive via `#pragma lib`/`#pragma src`.

Notable risks:
- Projection functions use integer return conventions shared across many files; callers depend on `-1/0/1` meanings.
- Many declarations are old-style Plan 9 C interfaces with global state coupling.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/map/map.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/map/route.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/map/route.c

Implements `route`, a helper that computes a `map -o` orientation placing two latitude/longitude points on the equator of a standard projection, optionally emitting a great-circle track.

Key behavior:
- Parses `route [-t] [-i] lat lon lat lon`.
- Uses `orient`, `normalize`, and `invert` to rotate coordinate systems and solve for a pole/twist placing endpoints symmetrically.
- Without `-t`, prints a suggested `-o ... -w ...` argument line.
- With `-t`, emits interpolated coordinates along the great-circle route and terminates with `"`, suitable for `map -t`.
- `-i` flips the orientation by using `dir = +90` instead of the default `-90`.

Important dependencies: `map.h`, `orient`, `deg2rad`, `normalize`, `invert`, and `lat/lon` rotation helpers.

Notable risks:
- Uses degrees at the command interface but internal radians in `struct place`; helper conversion is essential.
- The margin/window suggestion is heuristic and based on transformed longitude separation.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/map/route.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/map/sqrt.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/map/sqrt.c

Provides a local `sqrt(double)` implementation using `frexp()` scaling and Newton iteration.

Key behavior:
- Returns `0` for zero and negative inputs.
- Normalizes the input exponent, builds an initial estimate, rescales in chunks to avoid large shifts, and applies five Newton iterations.
- Contains an explicit note that the exponent parity trick does not work on ones-complement machines.

Important dependencies: Plan 9 libc `frexp`.

Notable risks:
- Negative inputs silently return `0` rather than setting domain errors.
- Integer shifts and old floating-point assumptions are portability-sensitive.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/map/sqrt.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/map/symbol.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/map/symbol.c

Parses and draws named vector symbols for the `map -y` option.

Key behavior:
- Reads a symbol file containing range commands, symbol starts, move commands, and vertex records.
- Stores up to `NSYMBOL` named symbol paths as arrays of `symb` points with segment/end flags.
- Scales symbol coordinates relative to global `halfwidth` and the last parsed range.
- `putsym()` finds a named symbol, projects the geographic position, computes local rotation/upright orientation, and plots the vector points with `cpoint`.
- Supports upright, normal, and reverse rotation modes.

Important dependencies: `map.h`, `iplot.h`, global `halfwidth`, `vflag`, `projection`, `doproj`, and `cpoint`.

Notable risks:
- Symbol names are limited to 10 bytes and the symbol table is fixed at 20 entries.
- Parser is minimal; malformed files call `error()` or can leave empty symbols.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/map/symbol.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/mc.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/mc.c

Implements `mc`, a columnation utility that reads lines from files/stdin and prints them in multiple columns sized to the output width.

Key behavior:
- Supports `-` for colon-sensitive breaks, `-LINEWIDTH` to force width, and `-t` in the option table though `tabflag` is effectively controlled by display probing.
- Reads input into a dynamically grown Rune buffer, expands tabs to spaces, and splits words at newlines.
- Computes column count from maximum word width and line width, using pixel widths when a display font is available.
- Auto-detects Acme/window text width and tab stop using `/dev/acme/ctl`, `$font`, `/dev/window`, and `$tabstop`.
- Emits columns row-wise, padding with tabs or spaces.

Important dependencies: Plan 9 `bio`, `draw`, fonts, `/dev/acme`, `/dev/window`.

Notable risks:
- Input is fully buffered before columnation except colon-triggered flushes.
- `morechars()` depends on `nchars` to restore `cbufp` after realloc.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/mc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/md5sum.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/md5sum.c

Implements a Plan 9 `md5sum` command compatible with file-list or stdin usage.

Key behavior:
- Installs `%M` formatter to print `MD5dlen` bytes as lowercase hexadecimal.
- Streams each file through `md5()` using `IOUNIT` reads.
- Prints just the digest for stdin, or digest plus tab plus filename for files.
- Accumulates an exit string on read/open errors and exits with that status.

Important dependencies: `libsec` MD5 API, Plan 9 `Fmt`, `IOUNIT`, `ERRMAX`.

Notable risks:
- Continues after open/read failures but final exit status is the last recorded error string.
- Uses MD5 only; this is checksum compatibility, not cryptographic integrity guidance.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/md5sum.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/mk/arc.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/mk/arc.c

Implements `Arc` allocation/freeing/debugging and updates the recursion limit used by rule application.

Key behavior:
- `newarc()` binds a prerequisite node, rule, stem, regexp matches, and optional out-of-date program into an `Arc`.
- `freearc()` frees the duplicated stem and arc object.
- `dumpa()` recursively dumps arc/node information for graph debugging.
- `nrep()` reads `NREP` from mk variables and clamps it to at least 1.

Important dependencies: `mk.h`, `rcopy`, `getvar`, `empty`, debug output through `bout`.

Notable risks:
- `freearc()` does not free regexp match strings copied by `rcopy`, so ownership is intentionally shallow/limited.
- `NREP` changes graph expansion behavior dynamically.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/mk/arc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/mk/archive.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/mk/archive.c

Handles archive-member targets of the form `archive(member)` for `mk`.

Key behavior:
- `atimeof()` splits archive/member names, caches aggregate archive scan times, refreshes member timestamps when the archive changes, and truncates long member names to archive header size.
- `atouch()` creates missing archives with `ARMAG` or updates an existing member timestamp in-place.
- `atimes()` scans Plan 9 ar headers, normalizes member mtimes, and stores `archive(member)` timestamps in the symbol table.
- `type()` recognizes archive files and warns once when a missing file is assumed to become an archive.
- `split()` parses and validates archive/member syntax.

Important dependencies: `mk.h`, `<ar.h>`, `SARMAG`, `SAR_HDR`, `SARNAME`, `S_TIME`, `S_AGG`, `S_BITCH`.

Notable risks:
- Only classic fixed-name archive headers are handled; long names are truncated.
- Direct header timestamp rewriting uses archive layout constants and seeks.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/mk/archive.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/mk/bufblock.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/mk/bufblock.c

Provides reusable growable buffers for parser, shell, and formatting code.

Key behavior:
- `newbuf()` allocates or reuses a `Bufblock` with a 4096-byte quantum.
- `freebuf()` puts buffers on a freelist.
- `growbuf()` either swaps backing storage with a suitably large free buffer or reallocates the current buffer.
- Provides byte/rune/string insertion and copy helpers.

Important dependencies: `mk.h`, `Malloc`, `Realloc`, Plan 9 Rune conversion.

Notable risks:
- `freebuf()` does not free memory; buffers persist for reuse.
- Callers must insert NUL terminators explicitly when needed.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/mk/bufblock.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/mk/env.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/mk/env.c

Manages mk’s variable environment for recipe execution.

Key behavior:
- Registers internal variables such as `target`, `stem`, `prereq`, `pid`, `nproc`, `newprereq`, `alltarget`, `newmember`, and `stem0` through `stem9`.
- `initenv()` marks internal variables and imports the OS environment.
- `execinit()` resets internal variables and builds an export list from non-internal, exportable mk variables.
- `buildenv()` fills internal variables for a job, extracts archive member names into `newmember`, and populates regexp stem captures.

Important dependencies: `mk.h`, symbol-table spaces `S_INTERNAL`, `S_VAR`, `S_NOEXPORT`.

Notable risks:
- Internal variables are mutable global symbols reused per job.
- `newmember` mutates duplicated prerequisite word strings while extracting text between parentheses.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/mk/env.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/mk/file.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/mk/file.c

Wraps file/archive time lookup, touch/delete operations, and `-w` what-if timestamp initialization.

Key behavior:
- `timeof()` consults archive handling for names containing `(`, otherwise uses cached `S_TIME` entries unless forced.
- `touch()` updates files or archive members, respecting `nflag`.
- `delete()` removes regular files but refuses archive member deletion.
- `timeinit()` marks comma/space/newline-separated names as having the current time.

Important dependencies: `mk.h`, `mkmtime`, `atimeof`, `atouch`, `chgtime`, `S_TIME`.

Notable risks:
- Any name containing `(` is treated as archive syntax.
- `delete()` cannot remove archive members, so failed recipe cleanup is incomplete for such targets.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/mk/file.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/mk/fns.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/mk/fns.h

Declares mk’s cross-file function interface.

Key behavior:
- Covers rule parsing/storage, variable substitution, word lists, graph construction, job scheduling, archive/file times, Plan 9 execution, environment export, shell quoting, and debug dumps.
- Exposes OS-dependent hooks such as `readenv`, `execsh`, `pipecmd`, `waitfor`, `chgtime`, and `mkmtime`.
- Exposes core data constructors like `newarc`, `newjob`, `newword`, and `newbuf`.

Important dependencies: `mk.h` types `Word`, `Rule`, `Node`, `Arc`, `Job`, `Bufblock`, `Symtab`.

Notable risks:
- The header encodes broad global coupling; changing one signature affects most of mk.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/mk/fns.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/mk/graph.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/mk/graph.c

Builds and validates the dependency graph for a target.

Key behavior:
- `graph()` applies explicit and meta rules, detects cycles, prunes vacuous arcs, checks ambiguous recipes, and applies node attributes.
- `applyrules()` recursively creates/reuses `Node`s, expands normal `%/&` meta rules and regexp rules, and tracks rule recursion counts with `NREP`.
- `vacuous()` removes meta-rule arcs that lead only to non-probable targets.
- `ambiguous()` rejects multiple incompatible recipes, preferring explicit over meta recipes where possible.
- `attribute()` propagates rule attributes like virtual, no-recipe, and delete to nodes.

Important dependencies: `mk.h`, `match`, `subst`, Plan 9 regexp `regexec/regsub`, `symlook`, `newarc`, `timeof`.

Notable risks:
- Recursive rule expansion is limited by rule counters; bad `NREP` values can change graph completeness.
- Ambiguity checks compare recipe pointer identity, not text equality.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/mk/graph.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/mk/job.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/mk/job.c

Allocates, frees, and dumps `Job` objects representing runnable recipes.

Key behavior:
- `newjob()` stores rule, node list, stem/matches, prerequisite lists, target lists, and initializes scheduling fields.
- `freejob()` frees word-list fields after a job completes.
- `dumpj()` prints job internals for execution debugging.

Important dependencies: `mk.h`, `Word` ownership helpers, `wtos`.

Notable risks:
- `stem` and `match` are borrowed from arcs, not freed by `freejob()`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/mk/job.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/mk/lex.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/mk/lex.c

Assembles logical mkfile lines and evaluates backquoted commands during lexical input.

Key behavior:
- `assline()` skips blank lines/comments, strips carriage returns, handles escaped newlines, quoted strings, and backquotes.
- `bquote()` supports rc-style `` `{...}` `` and sh-style backquotes, runs the command with `execsh`, and replaces the source text with command output.
- `nextrune()` centralizes escaped-newline handling and line counting.

Important dependencies: `mk.h`, `Biobuf`, `escapetoken`, `execsh`, `execinit`.

Notable risks:
- Backquote evaluation happens during parsing and can execute arbitrary commands from mkfiles.
- Missing quote/backquote errors terminate mk.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/mk/lex.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/mk/main.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/mk/main.c

Implements the `mk` command entry point, option parsing, environment setup, mkfile parsing, and target dispatch.

Key behavior:
- Parses flags for always-build, debug, explain, mkfile path, ignore/keep-going/no-execute/touch/usage, and what-if timestamps.
- Imports environment, handles command-line variable overrides, sets `MKFLAGS` and `MKARGS`.
- Parses default `mkfile` or each `-f` file.
- Chooses default targets, explicit targets, serial mode, or creates a virtual aggregate target for multiple arguments.
- Initializes execution, catches notes, runs `mk()` for targets, and exits.

Important dependencies: all mk modules, `Binit`, `parse`, `setvar`, `addrules`, `mk`, `timeinit`, `execinit`.

Notable risks:
- Command-line assignments mutate `argv[i][0]` to remove them from target args.
- Multiple explicit targets can become a synthetic virtual rule unless `-s` is used.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/mk/main.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/mk/match.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/mk/match.c

Implements mk’s simple `%` and `&` meta-rule matching and substitution.

Key behavior:
- `match()` checks literal prefix/suffix around the first `%` or `&`, extracts the stem, and rejects `&` stems containing `.` or `/`.
- `subst()` copies a template to a destination buffer, replacing `%` or `&` with the stem.

Important dependencies: `mk.h`, `PERCENT`, UTF rune scanning.

Notable risks:
- Only one meta marker is effectively supported.
- `subst()` truncates silently to `dlen - 1`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/mk/match.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/mk/mk.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/mk/mk.c

Drives target building and freshness decisions.

Key behavior:
- `mk()` builds a graph, clears made flags, repeatedly calls `work()`, waits for jobs, and reports up-to-date targets.
- `work()` recursively builds prerequisites, determines readiness/out-of-date status, supports pretend-made behavior, and schedules recipes with `dorecipe()`.
- `update()` records target completion and recomputes timestamps, including virtual targets and programmatic out-of-date checks.
- `outofdate()` compares timestamps or runs rule `P` programs, caching command results in `S_OUTOFDATE`.

Important dependencies: `graph`, `dorecipe`, `waitup`, `timeof`, `pipecmd`, `symlook`.

Notable risks:
- Equal timestamps are treated as out-of-date by design to avoid races.
- Pretend/unpretend logic is subtle and depends on parent freshness.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/mk/mk.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/mk/mk.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/mk/mk.h

Defines mk’s core data structures, flags, globals, debug masks, and utility macros.

Key behavior:
- Defines `Bufblock`, `Word`, `Symtab`, `Rule`, `Arc`, `Node`, and `Job`.
- Enumerates symbol-table spaces for variables, targets, times, nodes, aggregates, export controls, overrides, cached out-of-date checks, and internal state.
- Defines rule attributes (`META`, `UPD`, `QUIET`, `VIR`, `REGEXP`, `NOREC`, `DEL`, etc.) and node state flags.
- Defines parsing helpers, debug masks, and `PERCENT()` meta marker logic.

Important dependencies: Plan 9 `<u.h>`, `<libc.h>`, `<bio.h>`, `<regexp.h>`, and `fns.h`.

Notable risks:
- Flag bits are shared across modules; mismatches affect graph, scheduling, and cleanup behavior.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/mk/mk.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/mk/mkconv -->
# File Research: sources/os/plan9/9front/sys/src/cmd/mk/mkconv

An rc script that converts older make/mk-style syntax into newer Plan 9 `mk` variable and recipe conventions.

Key behavior:
- Copies input through `tee` to a temporary file and transforms output through `sed`.
- Rewrites `$%`, `$@`, `$^`, `$?`, and `$((...))`-style variable references to mk internal variables like `${stem}`, `${target}`, `${prereq}`, and `${newprereq}`.
- Converts some leading recipe control syntax and `:&` rule syntax.
- Warns to stderr if recipes contain `cd` or `make`, since these need manual attention.
- Cleans up the temp file on exit/interruption.

Important dependencies: rc shell, `tee`, `sed`, `grep`, `$pid`.

Notable risks:
- This is heuristic text conversion, not a parser.
- Recipes with shell structure, `cd`, or recursive make need review after conversion.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/mk/mkconv -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/mk/parse.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/mk/parse.c

Parses mkfiles into variables and rules.

Key behavior:
- `parse()` reads logical lines, supports include files (`<`) and include programs (`<|`), handles assignments, and stores rules with recipe bodies.
- `rhead()` splits rule/assignment heads, parses assignment attributes and rule attributes (`D`, `E`, `n`, `N`, `P`, `Q`, `R`, `U`, `V`).
- `rbody()` captures indented recipe lines after a rule.
- `addrules()` records the first non-meta rule as default target candidates.
- Maintains include file/line stack with `ipush`/`ipop`.

Important dependencies: `mk.h`, `assline`, `stow`, `addrule`, `pipecmd`, `waitup`, `execinit`.

Notable risks:
- Include programs execute during parsing.
- Assignment override semantics depend on `S_OVERRIDE` and `S_WESET`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/mk/parse.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/mk/plan9.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/mk/plan9.c

Provides Plan 9 OS integration for mk: environment import/export, process execution, waiting, notes, file timestamp cache, and shell setup.

Key behavior:
- Uses `/bin/rc` and shell name `rc`.
- `readenv()` copies `/env` into mk variables while excluding invalid shell names and internal variables.
- `exportenv()` writes selected variables back into a copied `/env`.
- `pipecmd()` runs commands under rc with optional stdout pipe and exported environment.
- `execsh()` optionally captures command output into a buffer.
- Handles waits, process termination notes, interrupt/hangup cleanup, file touch via `dirwstat`, and directory bulk mtime caching.

Important dependencies: Plan 9 rfork/env model, `/env`, `Waitmsg`, `Dir`, rc shell, `dirread`, `dirstat`.

Notable risks:
- Environment export mutates child `/env` files, not POSIX-style env arrays.
- Directory mtime caching depends on `S_BULKED` and can serve cached values unless forced.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/mk/plan9.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/mk/rc.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/mk/rc.c

Contains rc-shell-specific quoting, token scanning, and shell-name parsing.

Key behavior:
- Defines `termchars` used by assignment parsing.
- `charin()` searches for delimiters while skipping single-quoted strings and `${...}` variable generators.
- `expandquote()` and `escapetoken()` implement rc single-quote handling.
- `copyq()` preserves quoted/backquoted fragments while printing shell recipes.
- `bufcpyq()` appends strings with rc quoting when needed.

Important dependencies: `mk.h`, Plan 9 rune APIs, `needsrcquote`.

Notable risks:
- Only rc single quotes are true escapes; double quotes/backslashes are mostly preserved.
- Parser correctness depends on matching rc quoting rules.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/mk/rc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/mk/recipe.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/mk/recipe.c

Selects and schedules the recipe for an out-of-date node.

Key behavior:
- Chooses the applicable recipe arc from a node’s prerequisites.
- Handles no-recipe virtual/no-recipe targets and optional touch mode.
- Builds job target lists for all targets of a rule, expanding meta-rule stems.
- Collects all prerequisites and newly out-of-date prerequisites.
- Marks targets `BEINGMADE` and queues a `Job` with `run()`.

Important dependencies: `mk.h`, `outofdate`, `symlook`, `subst`, `wadd`, `newjob`, `run`.

Notable risks:
- Multi-target rule behavior depends on node lookup and readiness of all related targets.
- A missing recipe for a non-virtual/non-NORECIPE target is fatal.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/mk/recipe.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/mk/rule.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/mk/rule.c

Stores parsed rules and maintains explicit/meta rule lists.

Key behavior:
- `addrule()` reuses a rule with the same target/tail when possible, otherwise allocates a new `Rule`.
- Adds explicit rules to `rules` and meta/regexp rules to `metarules`.
- Compiles regexp rule targets with `regcomp`.
- Maintains per-target chains through `S_TARGET`.
- `rulecnt()` allocates the per-rule recursion counter array.

Important dependencies: `mk.h`, `symlook`, `wcmp`, `regcomp`, global `patrule`.

Notable risks:
- Reused rules overwrite fields like recipe/body/line while retaining target chain identity.
- Rule numbering drives recursion-limit bookkeeping.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/mk/rule.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/mk/run.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/mk/run.c

Schedules and waits for recipe jobs with configurable parallelism.

Key behavior:
- Maintains a pending job list and an event table of running jobs keyed by slot/pid.
- `nproc()` reads `NPROC`, clamps to at least 1, and resizes event slots.
- `sched()` builds job environment, prints commands unless quiet/no-exec/touch, runs rc, or simulates/touches targets.
- `waitup()` handles completed children, rogue processes, errors, delete-on-error targets, keep-going mode, target updates, and scheduling more jobs.
- Tracks concurrency usage by running job count.

Important dependencies: `mk.h`, `buildenv`, `shprint`, `execsh`, `waitfor`, `update`, `delete`.

Notable risks:
- Unexpected child processes are saved in a side list and can later satisfy explicit waits.
- Error handling differs sharply under `-k`; failed targets become fake `BEINGMADE`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/mk/run.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/mk/shprint.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/mk/shprint.c

Expands mk-controlled variables inside recipe text before shell execution or printing.

Key behavior:
- `shprint()` copies recipe text, expanding `$name` and `${name}` through `vexpand()`, while preserving quoted strings.
- Only expands internal variables and variables set by mkfiles/command line (`S_WESET`); inherited untouched environment variables remain `$name`.
- `front()` shortens long commands for error messages by keeping first fields and the last field.

Important dependencies: `mk.h`, `copyq`, `bufcpyw`, `symlook`, `shname`.

Notable risks:
- Expansion policy intentionally avoids expanding all environment variables; changing it would alter recipe shell behavior.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/mk/shprint.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/mk/symtab.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/mk/symtab.c

Implements mk’s multi-namespace hash table.

Key behavior:
- Uses a fixed 4099-bucket hash table and `HASHMUL` rolling hash seeded by symbol space.
- `symlook()` finds or optionally installs a symbol in a given namespace.
- `symtraverse()` calls a function for each symbol in a namespace.

Important dependencies: `mk.h`, `Malloc`.

Notable risks:
- Symbol storage is process-lifetime; there is no deletion path.
- Different logical namespaces share the same hash table but are separated by `space`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/mk/symtab.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/mk/var.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/mk/var.c

Provides variable get/set/dump helpers and shell variable-name scanning.

Key behavior:
- `getvar()` and `setvar()` read/write `S_VAR` symbol entries, freeing old word lists on set.
- `dumpv()` prints all variables for parse debugging.
- `shname()` returns the end of a shell/mk variable name according to `WORDCHR`.

Important dependencies: `mk.h`, `symlook`, `symtraverse`, `delword`.

Notable risks:
- Variable values are `Word` lists, so callers must honor ownership when setting.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/mk/var.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/mk/varsub.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/mk/varsub.c

Implements mk variable substitution, including `${name: A%B=C%D}` pattern substitutions.

Key behavior:
- `varsub()` handles `$name`, `${name}`, and substitution forms.
- `varname()` extracts variable names with mk word-character rules.
- `expandvar()` parses braced variables and locates substitution expressions.
- `subsub()` applies prefix/suffix match-and-rewrite across each word of a variable value.
- `submatch()` tests optional prefix/suffix word lists and returns the middle span for `%` substitutions.

Important dependencies: `mk.h`, `getvar`, `stow`, `charin`, `Word` helpers.

Notable risks:
- Substitution syntax is compact and delimiter-sensitive.
- Word-list ownership and temporary buffer reuse are subtle inside `subsub()`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/mk/varsub.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/mk/word.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/mk/word.c

Implements mk word-list creation, parsing, duplication, formatting, and deletion.

Key behavior:
- `newword`, `popword`, `delword`, `wdup`, `wcmp`, and `wadd` manage linked `Word` lists.
- `stow()` parses a string into words, handling whitespace, quotes, command expansions already present in input, and `$` variable substitutions.
- `nextword()` combines literal buffer content with substituted word lists, preserving mk list expansion semantics.
- `wtos()` and `bufcpyw()` convert word lists back to rc-quoted strings.

Important dependencies: `mk.h`, `expandquote`, `varsub`, `bufcpyq`.

Notable risks:
- Variable expansion can restart token parsing when empty at word start.
- Concatenating literal prefixes/suffixes with multi-word variable expansion is behaviorally important.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/mk/word.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/mkdir.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/mkdir.c

Implements Plan 9 `mkdir` with `-p` and `-m mode`.

Key behavior:
- `makedir()` checks for existing paths and creates directories with `DMDIR | mode`.
- `mkdirp()` walks slash-separated prefixes, creating missing components.
- Parses octal modes up to `0777`.

Important dependencies: Plan 9 `create`, `access`, `DMDIR`.

Notable risks:
- `mkdir -p` silently succeeds for already-existing final paths, while non-`-p` reports existing path as an error.
- `mkdirp()` temporarily writes NULs into the argument string.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/mkdir.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/mntgen.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/mntgen.c

Implements `mntgen`, a small dynamic 9P server that creates ephemeral directory entries on walk.

Key behavior:
- Serves read-only directories under a mount point or service name.
- Root directory dynamically creates a child directory when a new name is walked.
- Child directories are empty; walking `..` returns to root.
- Tracks entries in `Tab` records keyed by a 48-bit MD5-derived qid path and reference counts.
- Removes entries when their final fid is clunked.
- Supports `-s srvname` and `-D` chatty 9P mode.

Important dependencies: Plan 9 `thread`, `9p`, `fcall`, `libsec` MD5, `postmountsrv`.

Notable risks:
- Hash collisions are detected but make the walked name fail.
- Entries exist only while referenced; clients relying on stable listing need open fids.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/mntgen.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/mothra/forms.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/mothra/forms.c

Implements Mothra HTML form parsing, widget construction, form interaction, encoding, submission, and cleanup.

Key behavior:
- Defines `Form`, `Field`, and `Option` structures for HTML forms and controls.
- `rdform()` handles `form`, `input`, `button`, `select`, `option`, `textarea`, and `isindex` tags, creating fields and output placeholders.
- `mkfieldpanel()` converts parsed fields into libpanel widgets: entries, password entries, check/radio buttons, submit/reset buttons, file picker buttons, select pulldowns, text windows, and index fields.
- Handles checkbox/radio/select state changes, reset behavior, file upload path prompting, and Enter-to-submit behavior for single text fields.
- Encodes submissions as URL-encoded GET/POST or multipart form-data with a fixed boundary.
- `h_submitinput()` dispatches GET via a generated URL and POST via `urlpost()`/`geturl()`.
- `freeform()` releases forms, fields, options, and panels.

Important dependencies: Mothra browser types/functions, `html.h`, `rtext.h`, libpanel widgets, `geturl`, `urlpost`, `filetype`, global display state.

Notable risks:
- Multipart boundary is a fixed constant.
- Form controls directly own panels and interact with global `screen`, `text`, `mouse`, `font`, and `chrwidth`.
- File inputs deliberately clear HTML-provided default paths.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/mothra/forms.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/mothra/getpix.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/mothra/getpix.c

Loads, decodes, optionally resizes, caches, and frees images for Mothra rich text.

Key behavior:
- Keeps per-page `Pix` cache entries keyed by image URL string plus requested width/height.
- Resolves image URLs relative to the page URL, fetches them, detects type, pipes through format decoders (`gif`, `jpg`, `png`, `bmp`, `ico`), and optionally through `resize`.
- Reads decoded images with `readimage()` and stores them on the matching `Rtext`.
- `getpix()` forks worker processes with shared memory to fetch/decode multiple images concurrently, limited by `NXPROC`.
- Provides byte-size counting and cache cleanup.

Important dependencies: Mothra URL/pipeline helpers, Plan 9 image decoders, `draw`, `RFMEM` shared-memory rfork.

Notable risks:
- Parallel workers mutate shared `Www`/`Rtext` state under `RFMEM` without explicit locks.
- Unknown image types become textual `[img: ...]` errors.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/mothra/getpix.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/mothra/html.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/mothra/html.h

Defines Mothra’s HTML parser limits, token/tag model, parser state, and form integration interface.

Key behavior:
- Defines limits for stack depth, input buffer, lookahead, token length, and attributes.
- Defines `Pair`, `Entity`, `Tag`, `Stack`, `Hglob`, and incomplete `Form`/`Field`.
- `Stack` stores current tag formatting state including font, size, margins, image/link/name fields, script/pre flags, and image dimensions.
- `Hglob` stores parser input buffers, token/attribute buffers, parse stack, output state, current form, and destination page.
- Enumerates token types, special input sentinels, font/size constants, length direction, and all recognized HTML tag ids.
- Declares `tag[]`, form hooks, attribute helpers, and `pl_htmloutput`.

Important dependencies: Mothra `Www` type, form code, HTML parser implementation elsewhere.

Notable risks:
- Static token/attribute buffers impose hard limits.
- Tag enum order must match `html.syntax.c` table.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/mothra/html.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/mothra/html.syntax.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/mothra/html.syntax.c

Defines the HTML tag syntax/action table for Mothra.

Key behavior:
- Populates `tag[]` entries mapping tag enum values to lowercase tag names and end-tag policy.
- Marks tags as `END`, `NOEND`, `OPTEND`, or `ERR`.
- Includes older and newer tags, including media tags and table/form elements.

Important dependencies: `html.h` tag enum values.

Notable risks:
- The designated initializers depend on tag enum stability.
- Several HTML optional-end tags are treated as `NOEND` or `END` based on Mothra’s simplified parser behavior.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/mothra/html.syntax.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/mothra/libpanel/button.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/mothra/libpanel/button.c

Implements libpanel buttons, check buttons, radio buttons, menu buttons, and menus.

Key behavior:
- Draws button variants with relief boxes, optional check/radio marks, and centered icons/text.
- Mouse handling tracks down/up/out state and invokes callbacks on release.
- Radio buttons clear sibling radio buttons in the same parent.
- `plmenu()` builds a group of menu buttons from an icon array and callback.
- `plsetbutton()` programmatically sets check/radio state.

Important dependencies: `panel.h`, `pldefs.h`, drawing primitives from `draw.c`.

Notable risks:
- Radio grouping is implicit by parent and widget type.
- Callback signatures differ between normal buttons, check/radio buttons, and menu items.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/mothra/libpanel/button.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/mothra/libpanel/canvas.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/mothra/libpanel/canvas.c

Implements a generic leaf panel that delegates drawing and mouse handling to caller callbacks.

Key behavior:
- Stores optional draw and hit callbacks.
- Size request is zero; layout sizing comes from parent flags or external constraints.
- Ignores keyboard input.

Important dependencies: libpanel core `pl_newpanel`.

Notable risks:
- Caller-owned callbacks must know the panel rectangle and draw target.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/mothra/libpanel/canvas.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/mothra/libpanel/draw.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/mothra/libpanel/draw.c

Provides libpanel color/image initialization and common drawing primitives.

Key behavior:
- Allocates reusable solid images for white/light/dark/scroll/black/blue/highlight and a caret tick image.
- Draws boxes/outlines for panel states, computes box sizes/interiors, and draws icons/text/bitmaps with clipping.
- Draws check/radio controls, slider/scrollbar fills, highlights, ticks, clears/fills, and self-copy operations.
- Implements recursive panel drawing with invisibility/ignore checks.

Important dependencies: Plan 9 draw library, global `display`, `screen`, `font`.

Notable risks:
- `pl_drawinit()` calls `sysfatal` if any image allocation fails.
- Drawing style constants from `pldefs.h` must stay aligned with widget expectations.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/mothra/libpanel/draw.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/mothra/libpanel/edit.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/mothra/libpanel/edit.c

Implements a multi-line editable text panel on top of `Textwin`.

Key behavior:
- Lazily creates a `Textwin`, reshapes/redraws it, and updates vertical scrollbars.
- Supports snarf/paste, mouse selection, cut/paste chord handling, scrolling, and keyboard editing.
- Keyboard commands handle clear, backspace, line erase, word erase, and normal Rune insertion.
- Exposes edit APIs: scroll, get text/length/selection, set selection, paste, and move.

Important dependencies: `textwin.c`, `snarf.c`, `keyboard.h`, libpanel scroll callbacks.

Notable risks:
- Selection indices initialize to `-1`; callers rely on drawing/interaction to establish sensible values.
- Editing redraws through `Textwin`, whose replacement code has a documented incomplete optimized path.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/mothra/libpanel/edit.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/mothra/libpanel/entry.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/mothra/libpanel/entry.c

Implements a single-line text entry widget, including password mode.

Key behavior:
- Stores entry text as Runes with selection/cursor indices.
- Draws clipped text, caret, and selection highlight; password entries display `*`.
- Mouse handling supports focus, selection dragging, snarf/cut/paste chords.
- Keyboard handling supports movement, home/end, clear, line/word erase, backspace, insertion, and submit callback on newline.
- Exposes `plentryval()` as UTF string conversion.

Important dependencies: `keyboard.h`, snarf helpers, draw/font APIs.

Notable risks:
- Password entries suppress snarfing but still store cleartext in memory.
- Reinitialization reallocates existing entry storage through `pl_erealloc`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/mothra/libpanel/entry.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/mothra/libpanel/event.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/mothra/libpanel/event.c

Routes keyboard and mouse events through a panel tree.

Key behavior:
- `plgrabkb()` changes keyboard focus and redraws the old focus owner.
- `plkeyboard()` sends Runes to the focused panel.
- `pl_ptinpanel()` finds the most leafward, highest-priority panel containing a point.
- `plmouse()` sends mouse events, synthesizes `OUT` when leaving a previous panel, and supports `REMOUSE` capture.

Important dependencies: panel priority functions and widget `hit` handlers.

Notable risks:
- Hit dispatch depends on panel rectangles being current from `plpack`.
- `REMOUSE` capture is controlled by widget hit return values.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/mothra/libpanel/event.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/mothra/libpanel/frame.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/mothra/libpanel/frame.c

Implements a framed container panel.

Key behavior:
- Draws a filled frame box.
- Sizes itself as its child size plus frame interior.
- Provides child-space inset based on frame geometry.
- Does not handle mouse or keyboard events itself.

Important dependencies: `pl_box`, `pl_boxsize`, `pl_interior`.

Notable risks:
- Child layout depends on `pl_childspaceframe()` matching draw geometry.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/mothra/libpanel/frame.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/mothra/libpanel/group.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/mothra/libpanel/group.c

Implements a grouped container panel.

Key behavior:
- Draws a frame outline rather than a filled frame.
- Sizes and insets children like a frame.
- Does not directly process input.

Important dependencies: `pl_outline`, `pl_boxsize`, `pl_interior`.

Notable risks:
- Visual difference from `frame` is only draw behavior; layout behavior remains frame-like.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/mothra/libpanel/group.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/mothra/libpanel/init.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/mothra/libpanel/init.c

Provides libpanel initialization wrapper.

Key behavior:
- `plinit()` calls `pl_drawinit()` and returns success/failure.

Important dependencies: `draw.c`.

Notable risks:
- Actual initialization failure behavior is mostly in `pl_drawinit()`, which can `sysfatal`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/mothra/libpanel/init.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/mothra/libpanel/label.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/mothra/libpanel/label.c

Implements passive text/bitmap labels.

Key behavior:
- Stores icon/text plus placement.
- Draws inside a passive box.
- Computes size from icon/text size.
- Provides `plplacelabel()` to change placement.

Important dependencies: `pl_drawicon`, `pl_iconsize`, `pl_box`.

Notable risks:
- Label icon/text pointer is borrowed; lifetime is caller-managed.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/mothra/libpanel/label.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/mothra/libpanel/list.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/mothra/libpanel/list.c

Implements a scrollable selectable text list.

Key behavior:
- Uses a generator callback to enumerate item strings and a hit callback for selection.
- Draws visible rows and highlights current selection.
- Mouse handling tracks row under cursor and invokes callback on release.
- Vertical scrolling updates `lo`, uses pixel copying for partial redraws, and updates attached scrollbars.
- Computes requested size from item widths unless fill/expand flags allow width flexibility.

Important dependencies: font/draw helpers, scrollbar linkage, generator callback.

Notable risks:
- List length is determined by repeatedly calling `gen` until nil.
- `sel` can be outside visible range and is only drawn when visible.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/mothra/libpanel/list.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/mothra/libpanel/mem.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/mothra/libpanel/mem.c

Provides libpanel allocation helpers, default error callbacks, panel construction, and recursive free.

Key behavior:
- `pl_emalloc`/`pl_erealloc` allocate zeroed/reallocated memory or exit on failure.
- Default draw/hit/type/size/scroll callbacks abort if a panel kind has not installed behavior.
- `pl_newpanel()` initializes panel fields, appends to parent child list, assigns defaults, and allocates kind-specific data.
- `plfree()` recursively frees children, widget data, and widget-specific resources.

Important dependencies: `panel.h`, `pldefs.h`.

Notable risks:
- Creating children under panels marked `LEAF` is fatal.
- `plfree()` does not detach a freed panel from a live parent list.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/mothra/libpanel/mem.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/mothra/libpanel/message.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/mothra/libpanel/message.c

Implements a passive word-wrapped message panel.

Key behavior:
- `pl_textmsg()` draws text folded to a rectangle width.
- `pl_foldsize()` computes wrapped size for a target width.
- Message panels draw inside a passive box and request size based on folded text.
- Ignores input.

Important dependencies: UTF helpers `pl_nextrune`, `pl_runewidth`, font/draw primitives.

Notable risks:
- Wraps only at spaces; very long words are forced onto a line.
- Message text pointer is borrowed, not duplicated.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/mothra/libpanel/message.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/mothra/libpanel/pack.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/mothra/libpanel/pack.c

Implements libpanel layout calculation.

Key behavior:
- Recursively computes children’s requested sizes, applies `MAXX/MAXY`, and derives each panel’s `sizereq`.
- Honors fixed-size, fill, expand, pad, ipad, pack side, and placement flags.
- Distributes slack among `EXPAND` children along the relevant axis.
- Assigns rectangles recursively and computes child spaces through widget callbacks.
- `plmove()` translates an already-packed panel tree and calls `plemove()` for edit panels.

Important dependencies: widget `getsize`/`childspace` methods, panel flags.

Notable risks:
- Layout mutates `sizereq` during slack distribution.
- `plmove()` special-cases edit widgets because text locations are absolute.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/mothra/libpanel/pack.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/mothra/libpanel/panel.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/mothra/libpanel/panel.h

Public libpanel API and data model.

Key behavior:
- Defines `Scroll`, `Rtext`, `Panel`, and `Idol`.
- `Panel` includes public layout fields and private tree, draw target, flags, state, scroll links, kind-specific data, and method callbacks.
- Defines layout flags (`PACK`, `FILL`, `PLACE`, `EXPAND`, `FIXED`, `MAX`, `BITMAP`, `IGNORE`, `USERFL`), priorities, mouse `OUT`, and rich-text flags.
- Declares core lifecycle/layout/draw/input/scroll/snarf APIs and constructors for all widgets.
- Declares rich-text, idol-list, and snarf helper APIs.

Important dependencies: Plan 9 `draw` and event types.

Notable risks:
- Struct fields marked private are still visible and used by implementation and callers.
- Header declares broad APIs; implementation files assume global `font`, `screen`, and `display`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/mothra/libpanel/panel.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/mothra/libpanel/pldefs.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/mothra/libpanel/pldefs.h

Internal libpanel definitions and helper declarations.

Key behavior:
- Declares rich-text formatting/drawing/hit internals.
- Defines internal flags (`HITME`, `LEAF`, `INVIS`, `REMOUSE`) and widget state/style constants.
- Defines scroll command constants and scrollbar/slider orientation constants.
- Declares drawing primitives, panel allocation/printing/hit helpers, UTF helpers, and `Textwin` internals.

Important dependencies: `panel.h` and implementation files.

Notable risks:
- Internal flag ranges must not collide with public panel flags.
- `Textwin` location coordinates are absolute, causing special move handling.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/mothra/libpanel/pldefs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/mothra/libpanel/popup.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/mothra/libpanel/popup.c

Implements a popup container that temporarily displays one of three panels based on mouse button.

Key behavior:
- On button press, selects a popup panel, packs it, positions it near the pointer within bounds, saves covered pixels, makes it visible, and draws it.
- Routes mouse events into the selected popup panel while active.
- On release, restores saved pixels and hides the popup.
- Uses popup priority so it can win hit testing.

Important dependencies: `plpack`, `plmove`, `pl_invis`, `plmouse`, draw image save/restore.

Notable risks:
- Save image allocation failure leaves restoration unavailable.
- Popup state is button-specific (`DOWN1/2/3`) and tied to mouse button bitmasks.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/mothra/libpanel/popup.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/mothra/libpanel/print.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/mothra/libpanel/print.c

Debug-prints a panel tree.

Key behavior:
- Prints panel kind, pointer, rectangle, placement/fill/expand/fixed flags, padding, size, and requested size.
- Recurses through children with tab indentation.

Important dependencies: `panel.h`, flag constants.

Notable risks:
- Uses raw pointer formatting and writes directly to fd 1.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/mothra/libpanel/print.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/mothra/libpanel/pulldown.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/mothra/libpanel/pulldown.c

Implements pulldown buttons and menubars.

Key behavior:
- Draws a button label/icon and, on press, packs a supplied panel on a chosen side.
- Saves covered pixels, shows the pulldown panel, routes events into it, then restores and hides it when closed.
- Supports side placement north/south/east/west/center.
- `plmenubar()` builds a group of pulldown buttons from varargs.

Important dependencies: `plpack`, `plmove`, `pl_invis`, `plmouse`, draw save/restore.

Notable risks:
- Pull panel is external; caller manages its lifetime and content.
- Varargs API requires icon/panel pairs terminated by nil.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/mothra/libpanel/pulldown.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/mothra/libpanel/rtext.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/mothra/libpanel/rtext.c

Implements rich-text construction, layout, drawing, scrolling redraws, hit testing, selection, and text snarfing.

Key behavior:
- `pl_rtnew` and wrappers build linked `Rtext` runs containing text, bitmaps, or embedded panels.
- `pl_rtfmt()` formats runs into lines within a galley width, computing rectangles, line links, widths, and total size.
- `pl_rtdraw()` draws visible runs, embedded panels, images, links, selection highlight, and strike-through using an optional backup image.
- `pl_rtredraw()` supports efficient vertical/horizontal scroll redraw by copying existing pixels and drawing exposed regions.
- `pl_rthit()` maps a mouse point to a hot rich-text run.
- Provides selection marking and selected-text extraction.

Important dependencies: libpanel draw/layout primitives, `rtext.h` tab encoding, embedded `Panel` layout.

Notable risks:
- Embedded panels are moved during draw/scroll; their bitmap pointers need correction when a backup bitmap is used.
- Long unbreakable runs are force-fit if line breaking makes no progress.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/mothra/libpanel/rtext.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/mothra/libpanel/rtext.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/mothra/libpanel/rtext.h

Defines rich-text special spacing encodings.

Key behavior:
- Defines bit layout for negative special spacing values.
- Provides macros to create/decode special values and their arguments.
- Defines `PL_TAB` as tab-stop spacing before text.
- Declares `pltabsize()`.

Important dependencies: `rtext.c`.

Notable risks:
- Special spacing values are encoded into signed integers; callers must use macros consistently.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/mothra/libpanel/rtext.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/mothra/libpanel/scrltest.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/mothra/libpanel/scrltest.c

A small test/demo program for libpanel list scrolling.

Key behavior:
- Builds a root group with a scrollable generated list, a message label, and save/revert/done buttons.
- `save` captures the list scroll position; `revert` restores it.
- `ereshaped()` repacks and redraws the panel tree on window reshape.
- Main event loop sends mouse events to the root panel.

Important dependencies: libpanel, old Plan 9 draw/event APIs.

Notable risks:
- Uses older draw API names (`binit`, `bitblt`, `screen.ldepth`) that may be compatibility-specific.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/mothra/libpanel/scrltest.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/mothra/libpanel/scroll.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/mothra/libpanel/scroll.c

Provides generic scroll linkage and scroll-state helpers.

Key behavior:
- `plscroll()` links a scrollee panel to optional x/y scroller panels and back-links scrollers to their scrollee.
- `plgetscroll()` returns a panel’s `Scroll` state.
- `plsetscroll()` drives a panel’s scroll callback to restore x/y positions.

Important dependencies: panel scroll callback methods.

Notable risks:
- `plsetscroll()` only scrolls axes with nonzero saved size.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/mothra/libpanel/scroll.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/mothra/libpanel/scrollbar.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/mothra/libpanel/scrollbar.c

Implements horizontal and vertical scrollbar panels.

Key behavior:
- Orientation is inferred from pack side.
- Draws scrollbar trough and thumb via `pl_scrollupd`.
- Mouse buttons map to relative up/page, absolute, and relative down/page scroll semantics.
- Calls the linked scrollee’s `scroll` method with direction, button, position, and length.
- Converts scrollee natural coordinates into screen-coordinate thumb positions.

Important dependencies: `plscroll` linkage, draw helpers, panel priority.

Notable risks:
- For vertical/horizontal conversion, scrollbar geometry must match current packed rectangle.
- `USERFL` changes out-of-rect handling for mouse capture.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/mothra/libpanel/scrollbar.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/mothra/libpanel/slider.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/mothra/libpanel/slider.c

Implements a simple horizontal or vertical slider widget.

Key behavior:
- Orientation is chosen by comparing requested width and height.
- Draws filled slider range from zero to current value.
- Mouse drag updates `val`, redraws, and invokes callback with button mask, value, and range.
- `plsetslider()` sets value programmatically in screen coordinates from logical value/range.

Important dependencies: `pl_sliderupd`, draw/layout helpers.

Notable risks:
- `plsetslider()` divides by `range`; callers must avoid zero range.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/mothra/libpanel/slider.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/mothra/libpanel/snarf.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/mothra/libpanel/snarf.c

Connects panels to the Plan 9 snarf buffer.

Key behavior:
- `plputsnarf()` writes non-empty strings to `/dev/snarf`.
- `plgetsnarf()` reads all available snarf data into a NUL-terminated buffer.
- `plsnarf()` invokes a panel’s `snarf` method and writes the result.
- `plpaste()` reads snarf data and passes it to a panel’s `paste` method.

Important dependencies: `/dev/snarf`, panel snarf/paste callbacks.

Notable risks:
- Snarf data is treated as byte strings; panel-specific paste methods handle UTF conversion.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/mothra/libpanel/snarf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/mothra/libpanel/textview.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/mothra/libpanel/textview.c

Implements a scrollable rich-text viewer panel.

Key behavior:
- Formats rich text with `pl_rtfmt()` when the visible width changes.
- Draws rich text with current x/y offsets and updates attached scrollbars.
- Mouse handling selects hot rich-text ranges, passes events into embedded panel runs, and invokes hit callbacks for single hot items.
- Supports vertical and horizontal scrolling through `pl_rtredraw()`.
- Exposes get/set vertical position and snarfing selected rich text.

Important dependencies: `rtext.c`, scrollbars, panel hit priority.

Notable risks:
- Embedded panels inside rich text can capture mouse state through `REMOUSE`.
- Reformatting is tied to width changes, so text metrics and panel sizes must be stable.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/mothra/libpanel/textview.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/mothra/libpanel/textwin.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/mothra/libpanel/textwin.c

Implements fixed-font editable text-window mechanics used by the edit panel.

Key behavior:
- Maintains Rune text, visible top/bottom indices, selection, and absolute screen locations for visible runes.
- Maps points to rune indices, computes rune positions with wrapping, draws text, highlights selections, and clears trailing areas.
- Supports mouse selection, text replacement, scrolling to a top line, reshape redraws, construction/free, and moving absolute locations.
- Replacement inserts/deletes text and redraws the visible region.

Important dependencies: libpanel draw helpers, font metrics, `Mouse`.

Notable risks:
- Comments note linear search should be binary search and optimized replacement below visible text is incomplete (`if(1 || ...)` path).
- Location coordinates are absolute, requiring `twmove()` on panel movement.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/mothra/libpanel/textwin.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/mothra/libpanel/utf.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/mothra/libpanel/utf.c

Provides small UTF/rune helpers for libpanel text code.

Key behavior:
- `pl_idchar()` classifies identifier characters using whitespace/control/punctuation exclusions.
- `pl_rune1st()` detects the first byte of a UTF-8 rune.
- `pl_nextrune()` advances a char pointer to the next rune boundary.
- `pl_runewidth()` extracts one UTF-8 rune and returns its font width.

Important dependencies: Plan 9 UTF routines and font string measurement.

Notable risks:
- `pl_nextrune()` assumes valid UTF-8-like byte sequences and advances until a non-continuation byte.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/mothra/libpanel/utf.c -->