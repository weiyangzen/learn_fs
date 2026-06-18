# Group Research: group_1499_plan9_sources_os_plan9_plan9_sys_src_cmd_aquarela_smbstring_c_sourc_c11edfc081cd

Scope: `Docs/research_subset_a.md`, source tree `sources/os/plan9/plan9`. Every listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aquarela/smbstring.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aquarela/smbstring.c

Implements SMB string sizing, decoding, duplication, formatting, and wire encoding helpers.

Key points:
- `smbruneconvert` applies SMB path slash conversion, uppercasing, and optional space/non-breaking-space mapping.
- `smbstringlen`, `smbucs2len`, and `smbstrlen` choose wire length by peer Unicode capability and global Unicode mode.
- `smbstringdup` reads either ASCII NUL-terminated strings or aligned UCS-2 strings from SMB byte data.
- `smbstrput`, `smbucs2put`, and `smbstringput` serialize strings with optional Unicode/ASCII forcing, alignment, termination, case conversion, and path conversion.
- `smbstringprint` owns and replaces dynamically formatted error/message strings.

Dependencies and interactions:
- Uses `SmbPeerInfo`, `SmbHeader`, SMB string flags, `smbglobals`, and Plan 9 rune conversion helpers.
- Central utility for Aquarela packet parsers and encoders.

Notable behavior:
- UCS-2 decode advances to even alignment relative to a base pointer.
- `smbucs2put` asserts writes remain within the caller-provided max length.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aquarela/smbstring.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aquarela/smbtime.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aquarela/smbtime.c

Provides conversion between Plan 9 Unix-like seconds, DOS packed date/time, NT FILETIME, and SMB UTC-like time values.

Key points:
- `smbplan9time2datetime` converts seconds plus timezone offset into DOS date/time bitfields.
- `smbdatetime2plan9time` converts DOS date/time back to seconds using a GMT `Tm`.
- `smbplan9time2time` and `smbtime2plan9time` convert to/from NT 100 ns ticks since 1601-01-01.
- `smbplan9time2utime` and `smbutime2plan9time` apply timezone offsets for SMB time fields.

Dependencies:
- Uses Plan 9 `Tm`, `gmtime`, `tm2sec`, and SMB logging.

Notable behavior:
- DOS seconds have 2-second granularity.
- Offset handling is explicit and sign-sensitive.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aquarela/smbtime.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aquarela/smbtrans2client.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aquarela/smbtrans2client.c

Implements client-side SMB TRANS2 request execution and a FIND_FIRST2 helper.

Key points:
- Defines a client transaction method table for `SMB_COM_TRANSACTION2`.
- `smbclienttrans2` fills an `SmbTransaction` from input/output buffers, copies the client protocol header, sets the tree id, and calls `smbtransactionexecute`.
- `smbclienttrans2findfirst2` builds a TRANS2 FIND_FIRST2 request for `SMB_FIND_FILE_BOTH_DIRECTORY_INFO`, sends it, parses returned search metadata, then iterates returned directory entries.

Dependencies:
- Uses `SmbClient`, `SmbTransaction`, transaction encoder/decoder helpers, and buffer APIs.

Notable behavior:
- Contains direct `print`/`smblogdata` debug output in the response parsing path.
- Error strings are produced with `smbstringprint`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aquarela/smbtrans2client.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aquarela/smbtrans2find.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aquarela/smbtrans2find.c

Implements server-side TRANS2 directory search operations and search handle lifecycle.

Key points:
- `smbsearchnew`, `smbsearchclose`, and related helpers manage `SmbSearch` handles in the session SID map.
- `standardflatten` emits `SMB_INFO_STANDARD` directory entries with DOS date/time fields.
- `findbothflatten` emits `SMB_FIND_FILE_BOTH_DIRECTORY_INFO` records with NT times, allocation size, attributes, name length, short-name fields, and alignment.
- `populate` walks cached directory entries, applies SMB wildcard matching, flattens records, and stops on count or output-buffer exhaustion.
- `smbtrans2findfirst2` parses search parameters, splits path/pattern, builds a directory cache, creates a search handle when needed, and returns SID/count/EOS/name offset.
- `smbtrans2findnext2` resumes a prior search, optionally repositions by filename, and closes the search on requested flags or end-of-search.

Dependencies:
- Uses `SmbDirCache`, `Reprog`, tree/fid/sid maps, SMB transaction buffers, and Plan 9 `Dir`.

Notable behavior:
- Supports only `SMB_INFO_STANDARD` and `SMB_FIND_FILE_BOTH_DIRECTORY_INFO`.
- Has `poolcheck(mainmem)` instrumentation.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aquarela/smbtrans2find.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aquarela/smbtrans2query.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aquarela/smbtrans2query.c

Implements server-side TRANS2 query handlers for path, file, and filesystem information.

Key points:
- Shared `query` emits responses for `SMB_QUERY_FILE_BASIC_INFO`, `ALL_INFO`, `STANDARD_INFO`, and `EA_INFO`.
- Path queries resolve `t->serv->path + path` and call `dirstat`.
- File queries resolve an FID, use `dirfstat` for open file descriptors, or `dirstat` for path-only file state.
- Filesystem queries support allocation, volume, size, and attribute information levels with mostly synthetic values.

Dependencies:
- Uses `SmbTree`, `SmbFile`, Plan 9 `Dir`, SMB buffer serialization, DOS attribute conversion, and time conversion helpers.

Notable behavior:
- `SMB_QUERY_FILE_STREAM_INFO` is intentionally unsupported.
- Several fields are placeholders, such as serial `0xdeadbeef`, hard link count, and free space values.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aquarela/smbtrans2query.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aquarela/smbtrans2set.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aquarela/smbtrans2set.c

Implements server-side TRANS2 set-file and set-path information operations.

Key points:
- `smbtrans2setfileinformation` handles allocation/EOF truncation, basic timestamps/attributes, and delete-on-close disposition.
- `smbtrans2setpathinformation` handles `SMB_INFO_STANDARD`, translating DOS packed dates/times and attributes to Plan 9 `Dir` updates.
- Uses `dirfwstat` for FID-based updates and `dirwstat` for path-based updates.

Dependencies:
- Uses tree and FID maps, SMB transaction input buffers, Plan 9 `Dir`, `smbtruncatefile`, and DOS attribute conversion.

Notable behavior:
- Unsupported info levels return `ERRunknownlevel`.
- Size updates in path standard info are applied when nonzero; commented code shows uncertainty around zero-size handling.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aquarela/smbtrans2set.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aquarela/smbtransaction.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aquarela/smbtransaction.c

Provides generic SMB transaction and transaction2 decode, encode, response, datagram send, and client execution machinery.

Key points:
- `_smbtransactiondecodeprimary` parses primary transaction requests, validates counts/offsets, copies parameter and data fragments, and returns whether the transaction is complete.
- `decoderesponse`, `smbtransactiondecoderesponse`, and `smbtransactiondecoderesponse2` assemble multi-fragment transaction responses into output buffers.
- `_transactionencodeprimary` constructs primary transaction requests and packs as much parameter/data payload as fits.
- `_transactionencoderesponse` constructs one response fragment and advances output buffer read positions.
- `smbtransactionrespond` sends one or more response fragments.
- `smbtransactionexecute` sends a request, optionally handles secondary requests, receives response fragments, validates headers/errors, and decodes results.

Dependencies:
- Uses `SmbTransaction`, `SmbHeader`, `SmbPeerInfo`, `SmbBuffer`, and pluggable `SmbTransactionMethod` callbacks.

Notable behavior:
- Secondary transaction support is required only when the primary packet cannot carry all parameters/data.
- There is a defective `goto toosmall` loop in `_transactionencoderesponse` where the error label jumps to itself after setting the error string.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aquarela/smbtransaction.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aquarela/smbtree.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aquarela/smbtree.c

Manages SMB tree connections within a session.

Key points:
- `smbtreeconnect` creates the session TID map if needed, allocates a tree, inserts it, references the service, and logs the new TID.
- `smbtreedisconnect` logs, releases the service reference, closes all searches and files attached to the tree, removes the TID, and frees the tree.
- `smbtreedisconnectbyid` finds by TID then delegates.

Dependencies:
- Uses `SmbSession`, `SmbTree`, service reference management, SID/FID/TID maps, and search/file close helpers.

Notable behavior:
- Disconnect cleanup is map-wide and filters entries by owning tree.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aquarela/smbtree.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aquarela/testconnect.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aquarela/testconnect.c

Diagnostic SMB client program.

Key points:
- Connects to a target server and optional share with `smbconnect`.
- Runs RAP `smbnetserverenum2` for server and domain enumeration.
- Runs a TRANS2 `FIND_FIRST2` request for `\LICENSE` and prints SID/search count/end-of-search on success.
- Frees RAP results and the SMB client.

Dependencies:
- Uses Aquarela client, RAP, and TRANS2 client APIs.

Notable behavior:
- Intended as an interactive/manual test utility, not production code.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aquarela/testconnect.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aquarela/testnbdgram.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aquarela/testnbdgram.c

NetBIOS datagram browsing test tool.

Key points:
- Listens for datagrams addressed to the primary domain browser name.
- `deliver` parses SMB transaction datagrams, filters for `\MAILSLOT\BROWSE`, and decodes host announcement fields.
- Prints server name, announcement period, version, type, browser version, and comment.
- Main loop periodically sends a host announcement.

Dependencies:
- Uses NetBIOS datagram APIs, SMB header parsing, transaction decoding, and browser announcement helpers.

Notable behavior:
- Deliberately avoids validating the high half of the browser signature because some devices send nonstandard values.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aquarela/testnbdgram.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aquarela/testtime.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/aquarela/testtime.c

Small test program for SMB/NT time conversion.

Key points:
- With an argument, treats it as NT FILETIME and prints converted Plan 9 seconds and `ctime`.
- Without arguments, converts a fixed Plan 9 timestamp to NT time and back, printing both.

Dependencies:
- Uses `smbplan9time2time` and `smbtime2plan9time`.

Notable behavior:
- Hardcoded default timestamp is `1032615845`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/aquarela/testtime.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ar.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ar.c

Portable ASCII archive tool implementation.

Key points:
- Supports `r/u`, `d`, `x`, `t`, `p`, `m`, and `q` archive commands with option parsing for pivot insertion/move, verbose, update, create, local temp files, and timestamp preservation.
- Uses up to three logical temp files: archive start, moved/inserted middle, and archive end.
- Parses and writes portable `ar` headers through the `HEADER_IO` macro.
- Rebuilds archives through `install`, optionally generating `__.SYMDEF` when all members are compatible object files.
- `scanobj`, `objsym`, and `wrsym` collect text/data symbols using `mach` object readers.
- Temp-file subsystem stores member images in memory, spilling to disk if allocation fails.

Dependencies:
- Uses Plan 9 `bio`, `mach`, and `ar.h`.

Notable behavior:
- Duplicate text symbols prevent archive replacement when generating symbol definitions.
- GNU-produced trailing slashes in member names are stripped when reading headers.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ar.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/archfs.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/archfs.c

9P filesystem server that mounts mkfs-style archives.

Key points:
- Reads archive headers containing name, mode, uid, gid, mtime, and length.
- Builds an in-memory 9P file tree with `createpath`.
- Stores archive byte offset/length in per-file `Arch` aux data.
- `fsread` seeks into the archive and reads file contents on demand.
- Main mounts the server at `/mnt/arch` by default, with mount flags from `-a`, `-b`, `-c`, and `-C`.

Dependencies:
- Uses Plan 9 `thread`, `9p`, `bio`, and `Dir` metadata.

Notable behavior:
- Archive parsing stops on literal `end of archive`.
- Directory creation assumes no concurrent tree mutation.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/archfs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ascii.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/ascii.c

ASCII/Latin-1 table and converter utility.

Key points:
- Prints an ASCII table by default, 128 or 256 entries with `-8`.
- Supports numeric bases via `-x`, `-o`, `-d`, or `-b n`.
- Converts numeric input to named/text characters, or text input to numeric values depending on mode.
- `-n` forces numeric output from text; `-c`/`-t` selects character conversion, with `-t` stripping to raw bytes.

Dependencies:
- Uses Plan 9 `bio`.

Notable behavior:
- Base range is 2 through 36.
- Table strings include extended Latin-1 labels for bytes 0xa1 through 0xff.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/ascii.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/astro/astro.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/astro/astro.h

Shared header and global state definition for the `astro` program.

Key points:
- Defines object point structures, event records, occultation interpolation structures, time conversion state, and lunar coefficient table entries.
- Declares the large global state used throughout the program: observer location, epoch variables, nutation, heliocentric/geocentric coordinates, object instances, and star input fields.
- Declares all cross-file routines for planet solvers, date conversion, event search, output, and helper math.

Dependencies:
- Uses Plan 9 libc and custom `Fmt` conversions for right ascension and declination.

Notable behavior:
- This program is global-state driven; object routines communicate through shared variables rather than explicit structs.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/astro/astro.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/astro/comet.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/astro/comet.c

Computes a hardcoded comet ephemeris.

Key points:
- Contains several commented comet element sets; active elements are for C/2002 C1 Ikeya-Zhang.
- Solves Kepler’s equation for an eccentric orbit capped at `MAXE = .999`.
- Computes true anomaly, radius, ecliptic longitude/latitude, motion, semi-diameter, and magnitude.
- Calls `helio` and `geo` to produce observable coordinates.

Dependencies:
- Uses shared `astro.h` globals and `etdate`.

Notable behavior:
- Hyperbolic or near-hyperbolic eccentricity is clamped.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/astro/comet.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/astro/cosadd.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/astro/cosadd.c

Helper for compact trigonometric perturbation series evaluation.

Key points:
- `icosadd` initializes global coefficient and argument-multiplier streams.
- `cosadd` and `sinadd` consume coefficient pairs and signed char multipliers until a zero coefficient sentinel.
- Each term evaluates a base angle plus a linear combination of passed coefficients.

Dependencies:
- Used by Sun, Mercury, Venus, and nutation coefficient tables.

Notable behavior:
- Advances global `cafp` and `cacp` as series terms are consumed.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/astro/cosadd.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/astro/dist.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/astro/dist.c

General astronomical utilities for angular distance, event collection, rise/set interpolation, line reading, and token skipping.

Key points:
- `dist` computes angular separation in arcseconds.
- `rise`, `set`, `solstice`, `betcross`, and `melong` find crossings/extrema over sampled object points.
- `event` records filtered events; `evflush` sorts and prints them.
- `rline` reads one line from a file descriptor into global `line`.
- `skip` advances to field `n` in global `line`.

Dependencies:
- Uses global object sample arrays and event flags.

Notable behavior:
- Significant events sort before ordinary events by subtracting a large offset during comparison.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/astro/dist.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/astro/geo.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/astro/geo.c

Converts geocentric equatorial coordinates to topocentric equatorial and horizon coordinates.

Key points:
- Uses `alpha`, `delta`, `rp`, `hp`, and observer location globals.
- Computes local hour angle, topocentric declination, adjusted semidiameter, right ascension, azimuth, and elevation.
- Applies diurnal parallax using Earth radius and geocentric latitude.

Dependencies:
- Consumed by all object solvers after heliocentric/geocentric position computation.

Notable behavior:
- Outputs azimuth/elevation in degrees while many internal angles remain radians.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/astro/geo.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/astro/helio.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/astro/helio.c

Converts ecliptic heliocentric coordinates to equatorial geocentric coordinates.

Key points:
- Computes geocentric distance and light-time correction.
- Adds Earth/Sun position vector for annual parallax.
- Applies an approximate annual aberration correction.
- Applies nutation through longitude adjustment and true obliquity.
- Sets `alpha`, `delta`, horizontal parallax, semidiameter scaling, and magnitude distance correction.

Dependencies:
- Uses current Sun/Earth vectors from `setime`.

Notable behavior:
- Comment explicitly notes the stellar aberration method is incorrect.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/astro/helio.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/astro/init.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/astro/init.c

Initializes object registry, observer Earth parameters, and time-dependent solar/nutation state.

Key points:
- `objlst` orders all supported bodies: Sun, Moon, shadow, planets, Pluto, and comet.
- `init` computes geocentric latitude and Earth radius factor from observer location and elevation.
- `setime` sets ephemeris date, longitude correction, nutation, Sun vectors, and Earth velocity approximation.
- `setobj` copies current global observable coordinates into an object sample point.
- `fsun` and `shad` compute Sun and Earth shadow pseudo-object positions.

Dependencies:
- Uses global object structs and planetary routines.

Notable behavior:
- `init` is called before and after argument parsing because arguments can change location.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/astro/init.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/astro/jup.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/astro/jup.c

Computes Jupiter ephemeris.

Key points:
- Sets mean orbital elements from `capt` and `eday`.
- Solves Kepler’s equation.
- Reduces orbital coordinates to the ecliptic.
- Applies fixed longitude/latitude offsets, semidiameter, and magnitude.
- Calls `helio` and `geo`.

Dependencies:
- Uses shared orbital globals and convergence threshold.

Notable behavior:
- Perturbation variables are present but set to zero.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/astro/jup.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/astro/main.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/astro/main.c

Main driver and argument parser for `astro`.

Key points:
- Initializes constants, formatters, object table, arguments, and observer location.
- For each requested period, samples every object at `NPTS+2` times unless point/distance mode is requested.
- Supports direct position printing, object distance mode, event search mode, date input, local timezone correction, comet-only display, and custom periods.
- Reads default location from `/lib/sky/here`, with fallback coordinates.

Dependencies:
- Coordinates all `astro` modules.

Notable behavior:
- `deltat` is heuristically derived from date unless explicitly read with `-t`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/astro/main.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/astro/mars.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/astro/mars.c

Computes Mars ephemeris.

Key points:
- Builds Mars orbital elements as functions of epoch.
- Solves Kepler’s equation and reduces to ecliptic coordinates.
- Computes motion, apparent semidiameter, and phase-dependent magnitude.
- Calls `helio` and `geo`.

Dependencies:
- Uses global Sun longitude approximation for elongation/magnitude.

Notable behavior:
- Perturbation terms are stubbed as zero.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/astro/mars.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/astro/merc.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/astro/merc.c

Computes Mercury ephemeris with perturbation series.

Key points:
- Sets Mercury orbital elements and perturbing planet mean anomalies.
- Solves Kepler’s equation.
- Uses `mercfp`/`merccp` through `cosadd` for longitude and radius perturbations.
- Computes ecliptic position, motion, semidiameter, and phase magnitude.
- Calls `helio` and `geo`.

Dependencies:
- Uses coefficient table in `merct.c`.

Notable behavior:
- Latitude perturbation is not applied beyond inclination reduction.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/astro/merc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/astro/merct.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/astro/merct.c

Mercury perturbation coefficient data.

Key points:
- Defines `mercfp[]`, a sequence of coefficient/phase pairs split into zero-terminated subseries.
- Defines `merccp[]`, signed argument multiplier bytes consumed by `cosadd`/`sinadd`.
- Used by `merc.c` to compute longitude and log-radius perturbations.

Dependencies:
- Data format is tightly coupled to `cosadd.c`.

Notable behavior:
- Contains no executable logic beyond static data definitions.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/astro/merct.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/astro/moon.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/astro/moon.c

Computes Moon ephemeris using Brown-style lunar perturbation series.

Key points:
- Computes fundamental lunar and solar elements from epoch.
- Applies long-period corrections and scale factors for eccentricity, solar eccentricity, inclination, and parallax.
- Sums longitude, latitude, node, and parallax terms from `moontab[]`, plus explicit planetary terms.
- Converts lunar longitude/latitude/parallax to equatorial coordinates and then topocentric coordinates.
- Sets Moon phase fraction in `mag`, horizontal parallax, and semidiameter.

Dependencies:
- Uses coefficient table in `moont.c`, `sinx`, `cosx`, `geo`, and nutation globals.

Notable behavior:
- `flags['o']` applies an observational latitude adjustment.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/astro/moon.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/astro/moont.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/astro/moont.c

Lunar perturbation coefficient table.

Key points:
- Defines `moontab[]`, a sequence of coefficient and integer multiplier records.
- The table is divided into zero-terminated sections consumed by `moon.c` for longitude, latitude sine terms, latitude cosine terms, node terms, and parallax terms.

Dependencies:
- Data format is coupled to `Moontab` and `moon.c`’s sequential section parsing.

Notable behavior:
- Contains no control logic; the zero rows delimit subseries.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/astro/moont.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/astro/nept.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/astro/nept.c

Computes Neptune ephemeris from tabulated orbital elements.

Key points:
- Uses a local `elem[]` array for epoch, orbital elements, and century rates.
- Solves Kepler’s equation, reduces to ecliptic coordinates, applies fixed offsets, and computes motion/semidiameter.
- Contains a Saturn-ring-style magnitude computation block copied into this outer-planet routine.
- Calls `helio` and `geo`.

Dependencies:
- Uses shared ephemeris globals.

Notable behavior:
- Comments in the magnitude block refer to Saturn even though this file is Neptune.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/astro/nept.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/astro/nutate.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/astro/nutate.c

Computes nutation, obliquity, and Greenwich sidereal time.

Key points:
- Computes lunar/solar arguments and ascending node.
- Uses `nutfp`/`nutcp` coefficient tables through `sinadd`/`cosadd`.
- Sets long-period and short-period nutation terms: `phi`, `eps`, `dphi`, and `deps`.
- Computes mean obliquity, true obliquity, and sidereal time corrected by nutation.

Dependencies:
- Uses coefficient data from `nutt.c`.

Notable behavior:
- Comments describe coefficients as from the Explanatory Supplement.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/astro/nutate.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/astro/nutt.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/astro/nutt.c

Nutation coefficient data.

Key points:
- Defines `nutfp[]`, coefficient/phase-pair series for nutation longitude and obliquity terms.
- Defines `nutcp[]`, compact signed multiplier data used by `cosadd`/`sinadd`.

Dependencies:
- Consumed only by `nutate.c` through `icosadd`.

Notable behavior:
- Contains no executable functions.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/astro/nutt.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/astro/occ.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/astro/occ.c

Detects and refines occultation/eclipse/transit contact times.

Key points:
- `occult` finds a sampled minimum angular separation between two objects, refines it at minute and sub-minute resolution, then records contact times.
- `set3pt` builds a quadratic interpolation model from three sampled points.
- `setpt` evaluates the interpolated active point.
- `pinorm` normalizes angular differences across wraparound.

Dependencies:
- Uses `dist`, `setime`, object functions, and object point arrays.

Notable behavior:
- Contact times `t1` through `t5` are initialized to sentinel `-100`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/astro/occ.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/astro/output.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/astro/output.c

Formats object coordinates and custom angle conversions.

Key points:
- `output` prints object or SAO star label, right ascension, declination, azimuth, elevation, semidiameter, and Sun/Moon magnitude/phase field.
- `Rconv` formats radians as hours/minutes/seconds.
- `Dconv` formats radians as signed degrees/minutes/seconds.

Dependencies:
- Installed by `main.c` as `%R` and `%D` formatters.

Notable behavior:
- Declination formatter folds values above 180 degrees into negative equivalents.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/astro/output.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/astro/pdate.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/astro/pdate.c

Date/time conversion and printing utilities for `astro`.

Key points:
- Converts between internal day counts and calendar fields with `convdate`, `dtsetup`, and `dsrc`.
- Prints numeric or speech-like dates/times depending on `flags['s']`.
- `pstime` prints sidereal/location-related position context.
- `tzone` adjusts for local timezone using Plan 9 `localtime`/`gmtime`.
- Handles Gregorian calendar correction and BC year adjustment.

Dependencies:
- Uses global flags, observer location, and `helio`/`geo` for `pstime`.

Notable behavior:
- Internal epoch is relative to 1900-style astronomical day counts.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/astro/pdate.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/astro/plut.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/astro/plut.c

Computes Pluto ephemeris from tabulated orbital elements.

Key points:
- Uses a local element/rate table.
- Solves Kepler’s equation and reduces to ecliptic coordinates.
- Applies fixed longitude/latitude offsets and computes motion/semidiameter.
- Contains a Saturn-ring-style magnitude computation block copied into this Pluto routine.
- Calls `helio` and `geo`.

Dependencies:
- Uses global ephemeris state.

Notable behavior:
- Comments in the magnitude block refer to Saturn even though this file is Pluto.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/astro/plut.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/astro/sat.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/astro/sat.c

Computes Saturn ephemeris and ring-influenced magnitude.

Key points:
- Builds Saturn orbital elements from epoch, solves Kepler’s equation, and reduces coordinates.
- Applies fixed longitude/latitude offsets and semidiameter.
- Computes geocentric equatorial coordinates and Saturn ring plane geometry to estimate magnitude.
- Calls `helio` and `geo`.

Dependencies:
- Uses shared Sun vector and obliquity globals.

Notable behavior:
- Ring geometry constants are taken from comments citing the Explanatory Supplement.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/astro/sat.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/astro/satel.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/astro/satel.c

Artificial satellite pass prediction support.

Key points:
- `satels` reads satellite element files from `satlst`, currently an empty list.
- Parses epoch/orbital parameters, precomputes trig constants, and scans the day in five-minute steps.
- `satel` propagates satellite position, solves eccentric anomaly, checks visibility, and sets elevation.
- `vis` checks sunlight/geometry constraints for satellite and observer.

Dependencies:
- Uses global observer location, date utilities, `sunel`, and event queue.

Notable behavior:
- Because `satlst` contains only `0`, no satellite files are processed unless the table is changed.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/astro/satel.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/astro/search.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/astro/search.c

Searches sampled object positions for astronomical events.

Key points:
- Adds rise/set events for all objects.
- Adds solar solstice/equinox, twilight, and meteor shower events.
- Adds Moon phase events.
- Detects Mercury/Venus elongations, Moon occultations, eclipses, solar transits, and close “house” events.
- Optionally searches star occultations and satellite passes.
- Flushes sorted events at the end.

Dependencies:
- Uses `dist.c` event helpers, `occult`, `stars`, and `satels`.

Notable behavior:
- Contains visible typo text `meeteeor shouwer` in meteor event format.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/astro/search.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/astro/star.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/astro/star.c

Converts catalog star positions to current apparent coordinates.

Key points:
- Applies E-term aberration removal, proper motion, precession, ecliptic conversion, parallax distance estimate, and then `helio`/`geo`.
- Uses global catalog fields populated by `stars.c`.

Dependencies:
- Uses shared epoch/time globals and observer coordinate conversion pipeline.

Notable behavior:
- Assumes input right ascension is in hours and converts to radians after proper motion.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/astro/star.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/astro/stars.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/astro/stars.c

Searches SAO star table for lunar occultations.

Key points:
- Opens `/lib/sky/estartab`.
- Limits candidates by right ascension range around Moon path.
- Parses fixed-column star data: SAO number, RA, declination, proper motion, parallax, and magnitude.
- Converts each candidate via `star`, copies it into the star object sample array, and runs `occult`.
- Emits occultation begin/end events with dark/significant flags based on magnitude.

Dependencies:
- Uses `rline`, `star`, `occult`, and event queue.

Notable behavior:
- Handles RA wraparound when Moon path crosses zero hours.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/astro/stars.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/astro/sun.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/astro/sun.c

Computes solar apparent ecliptic position.

Key points:
- Computes Earth/Sun orbital elements and lunar/planetary arguments.
- Uses `sunfp`/`suncp` coefficient tables for anomaly, longitude, latitude, and radius perturbations.
- Computes longitude, latitude, radius, motion, semidiameter, and magnitude.
- Does not call `helio`/`geo`; caller `fsun` handles that for the apparent Sun pseudo-object.

Dependencies:
- Uses `sunt.c` coefficient data.

Notable behavior:
- `flags['o']` changes the solar semidiameter constant.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/astro/sun.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/astro/sunt.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/astro/sunt.c

Solar perturbation coefficient data.

Key points:
- Defines `sunfp[]`, zero-delimited coefficient/phase subseries.
- Defines `suncp[]`, compact multiplier bytes for the trigonometric series.
- Used by `sun.c` through `icosadd`, `cosadd`, and `sinadd`.

Dependencies:
- Data format is tied to `cosadd.c`.

Notable behavior:
- Contains no functions.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/astro/sunt.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/astro/uran.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/astro/uran.c

Computes Uranus ephemeris from tabulated orbital elements.

Key points:
- Uses local element/rate table.
- Solves Kepler’s equation and reduces to ecliptic coordinates.
- Applies fixed offsets and computes motion/semidiameter.
- Contains a Saturn-ring-style magnitude computation block copied into this Uranus routine.
- Calls `helio` and `geo`.

Dependencies:
- Uses shared ephemeris globals.

Notable behavior:
- Comments in the magnitude block refer to Saturn even though this file is Uranus.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/astro/uran.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/astro/venus.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/astro/venus.c

Computes Venus ephemeris with perturbation series.

Key points:
- Builds Venus orbital elements and mean anomalies for perturbing planets.
- Applies long-period anomaly terms.
- Solves Kepler’s equation.
- Uses `venfp`/`vencp` for longitude, latitude, and log-radius perturbations.
- Computes phase magnitude and semidiameter, then calls `helio` and `geo`.

Dependencies:
- Uses coefficient table in `venust.c`.

Notable behavior:
- Magnitude includes a cubic phase-angle term.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/astro/venus.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/astro/venust.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/astro/venust.c

Venus perturbation coefficient data.

Key points:
- Defines `venfp[]`, zero-delimited coefficient/phase subseries.
- Defines `vencp[]`, signed argument multiplier bytes.
- Used by `venus.c` with the shared trigonometric series helpers.

Dependencies:
- Data format is coupled to `cosadd.c`.

Notable behavior:
- Contains no executable logic.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/astro/venust.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/auth/as.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/auth/as.c

Runs a command as another user on a CPU server.

Key points:
- Opens `#¤/caphash` early and generates a kernel change-uid capability.
- `mkcap` builds `from@to@random`, hashes it with HMAC-SHA1, writes the hash to `caphash`, and returns the capability string.
- `usecap` writes the capability to `#¤/capuse`.
- `becomeuser` switches namespace with `newns`.
- `runas` execs `/bin/rc -lc <cmd>` with `service=rx`.

Dependencies:
- Uses Plan 9 capability device and auth command helpers.

Notable behavior:
- Usage text says `[-c]`, but actual option parsed is `-d`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/auth/as.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/auth/asn12dsa.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/auth/asn12dsa.c

Converts ASN.1 DSA private keys to Plan 9 factotum key text.

Key points:
- Reads all input from a file or stdin.
- Parses with `asn1toDSApriv`.
- Prints a `key proto=dsa` line with optional tag, public parameters, public key, and private secret.

Dependencies:
- Uses `mp`, `libsec`, and `%B` multiprecision formatting.

Notable behavior:
- Optional `-t` prepends arbitrary key attributes.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/auth/asn12dsa.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/auth/asn12rsa.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/auth/asn12rsa.c

Converts ASN.1 RSA private keys to Plan 9 factotum key text.

Key points:
- Reads all input from a file or default `#d/0`.
- Parses with `asn1toRSApriv`.
- Prints `key proto=rsa` with size, public exponent, private exponent, modulus, primes, CRT exponents, and coefficient.
- Supports optional `-t` tag attributes.

Dependencies:
- Uses `mp` and `libsec`.

Notable behavior:
- Private fields are printed with `!` attribute names for factotum secrecy convention.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/auth/asn12rsa.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/auth/authcmdlib.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/auth/authcmdlib.h

Shared declarations for Plan 9 auth command utilities.

Key points:
- Defines constants for key database paths, password length, SecureNet challenge limits, and account bio fields.
- Defines `Acctbio` and `Fs` structs.
- Declares helpers for key lookup, secret lookup/update, password input/validation, net response checking, account bio parsing/writing, file IO, logging, and formatting.

Dependencies:
- Used by many files in `cmd/auth`.

Notable behavior:
- Declares `#pragma lib "./lib.$O.a"` to link local auth command library.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/auth/authcmdlib.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/auth/authsrv.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/auth/authsrv.c

Main Plan 9 authentication server request handler.

Key points:
- Reads fixed-size ticket requests and dispatches by request type.
- Supports ticket requests, challenge/response, password changes, APOP, CRAM, CHAP, MS-CHAP, HTTP passwords, and VNC.
- Issues encrypted tickets and authenticators using Plan 9 auth structures.
- Uses key databases `/mnt/keys` and `/mnt/netkeys`.
- Checks host/user delegation with `/lib/ndb/auth` `hostid` and `uid` entries.
- Implements LM/NT password hashes and MS-CHAP responses.
- Logs failures and optionally debug successes.

Dependencies:
- Uses `authsrv.h`, `libsec`, `ndb`, and shared auth command library.

Notable behavior:
- For unknown users/hosts, random keys are generated to avoid revealing account existence.
- VNC reverses bits in password bytes before DES use, matching VNC convention.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/auth/authsrv.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/auth/challenge.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/auth/challenge.c

Interactive factotum challenge/response test utility.

Key points:
- Opens `/mnt/factotum/rpc`.
- Creates a challenge using `auth_challenge`.
- Prompts for user and response.
- Calls `auth_response` and prints client/server user IDs from returned `AuthInfo`.

Dependencies:
- Uses Plan 9 auth RPC/factotum APIs.

Notable behavior:
- Argument is passed as auth challenge parameters.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/auth/challenge.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/auth/changeuser.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/auth/changeuser.c

Creates or updates Plan 9 and SecureNet user credentials.

Key points:
- Options select Plan 9 (`-p`) and/or SecureNet (`-n`); default is Plan 9.
- Prompts before replacing existing keys.
- For Plan 9, collects password, updates key and optional secret, and updates account bio.
- For SecureNet, generates random DES key, writes it, prints key and checksum.
- `install` creates user directories, writes key files, and preserves/updates expiration.

Dependencies:
- Uses auth command library functions, key database paths, and `authsrv.h`.

Notable behavior:
- Validates username by `ANAMELEN`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/auth/changeuser.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/auth/convbio.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/auth/convbio.c

Converts old account bio records to pipe-delimited format.

Key points:
- `ordbio` parses one legacy bio line into username, name, department, and up to 10 email addresses.
- `nwrbio` writes `user|user|name|dept|email...`.
- Main streams stdin to stdout.

Dependencies:
- Uses `Acctbio` from `authcmdlib.h`.

Notable behavior:
- Email addresses are extracted from `<...>` spans.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/auth/convbio.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/auth/convkeys.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/auth/convkeys.c

Re-encrypts a current-format Plan 9 key database file.

Key points:
- Gets original key from auth key or password with `-p`.
- In verbose mode `-v`, decrypts and prints usernames without rewriting.
- Otherwise prompts for a new password, decrypts with old DES-CBC wrapper, validates UTF-8-like names, randomizes header bytes, re-encrypts, and writes back.
- Uses `/dev/random` with `rand` fallback.

Dependencies:
- Uses `authsrv.h` key database record sizes and DES helpers.

Notable behavior:
- Truncates odd trailing bytes that do not fit full key records.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/auth/convkeys.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/auth/convkeys2.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/auth/convkeys2.c

Converts old key database records to the newer encrypted key database format.

Key points:
- Reads old fixed-size records, decrypts each with the old auth key, copies into new record layout, and clears the secret field.
- Adds random header bytes and encrypts the new database with DES-CBC under a new password.
- Verbose mode prints usernames.

Dependencies:
- Uses `OKEYDBLEN`, `KEYDBLEN`, `KEYDBOFF`, and `SECRETLEN` from `authsrv.h`.

Notable behavior:
- Warns but still processes only full old-format records when file length is odd.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/auth/convkeys2.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/auth/cron.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/auth/cron.c

Plan 9 cron daemon with per-user schedules and local/remote execution.

Key points:
- Maintains `/cron/lock` as an exclusive lock.
- Reloads `/cron/<user>/cron` files when qids change.
- Parses classic five-field cron time specs plus host and command.
- Rounds schedule processing to minutes and handles clock jumps.
- `rexec` forks jobs, switches user through kernel capabilities, and runs locally or over `rexexec` with `p9any` auth.
- `-c` creates the current user’s cron directory and file; `-d` prints parsed jobs.

Dependencies:
- Uses Plan 9 auth capability code duplicated from `as.c`, `auth_proxy`, and remote dial helpers.

Notable behavior:
- Commands are wrapped as `exec rc -c '...'` with quote escaping and redirected I/O.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/auth/cron.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/auth/debug.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/auth/debug.c

Authentication setup diagnostic tool.

Key points:
- Scans `/mnt/factotum/ctl` for `proto=p9sk1` keys.
- For each key, attempts to dial the auth server for the domain and reports name-service lookup details.
- Optionally prompts for passwords and tests ticket requests using the user key and CPU server owner key.
- Verifies decrypted ticket numbers and challenge echoes to detect key mismatches or rogue auth servers.

Dependencies:
- Uses auth server ticket protocol, factotum attribute parsing, `csgetvalue`, and Plan 9 auth helpers.

Notable behavior:
- Contains placeholders/comments for further p9sk1 exchange tests that are not implemented.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/auth/debug.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/auth/disable -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/auth/disable

Shell script to disable a user in both auth key databases.

Key points:
- If `/mnt/keys/$1` exists, writes `disabled` to its `status`.
- If `/mnt/netkeys/$1` exists, writes `disabled` to its `status`.

Dependencies:
- Plan 9 `rc` shell and mounted key databases.

Notable behavior:
- Does not validate arguments or report missing users.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/auth/disable -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/auth/dsa2pub.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/auth/dsa2pub.c

Extracts a public DSA factotum key.

Key points:
- Reads a DSA key using `getdsakey`.
- Preserves parsed public attributes.
- Prints `key ... p= q= alpha= key=` without the private secret.

Dependencies:
- Uses helper definitions from `rsa2any.h`, multiprecision formatting, and auth attribute formatting.

Notable behavior:
- Accepts zero or one input file.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/auth/dsa2pub.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/auth/dsa2ssh.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/auth/dsa2ssh.c

Converts a DSA key to OpenSSH public key format.

Key points:
- Reads a DSA private key with `getdsakey`.
- Serializes SSH wire fields: algorithm name `ssh-dss`, p, q, alpha, and public key.
- Prints base64-encoded public key and optional comment.

Dependencies:
- Uses `rsa2any.h` helpers `put4`, `putn`, and `putmp2`.

Notable behavior:
- Supports `-c comment`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/auth/dsa2ssh.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/auth/dsagen.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/auth/dsagen.c

Generates a DSA private key for factotum.

Key points:
- Calls `dsagen(nil)`.
- Prints `key proto=dsa` with optional tag attributes and all public/private DSA fields.

Dependencies:
- Uses `libsec` and multiprecision formatting.

Notable behavior:
- Supports `-t 'attr=value ...'`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/auth/dsagen.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/auth/enable -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/auth/enable

Shell script to enable a user in both auth key databases.

Key points:
- If `/mnt/keys/$1` exists, writes `ok` to its `status`.
- If `/mnt/netkeys/$1` exists, writes `ok` to its `status`.

Dependencies:
- Plan 9 `rc` shell and mounted key databases.

Notable behavior:
- Does not validate arguments or report missing users.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/auth/enable -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/auth/factotum/apop.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/auth/factotum/apop.c

Factotum protocol implementation for APOP and CRAM-MD5.

Key points:
- Implements both client and server roles through phase states.
- Client role receives a challenge, finds a key with `!password`, computes MD5 or HMAC-MD5 response, and returns it.
- Server role obtains a challenge from the auth server, sends it to the peer, receives user/response, and forwards validation to the auth server.
- On success, validates returned ticket/authenticator and fills `AuthInfo`.

Dependencies:
- Uses factotum `Proto`, `Fsstate`, key lookup, Plan 9 auth server ticket protocol, and `libsec` MD5/HMAC.

Notable behavior:
- APOP uses `MD5(challenge || password)`, while CRAM uses HMAC-MD5.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/auth/factotum/apop.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/auth/factotum/chap.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/auth/factotum/chap.c

Factotum protocol implementation for CHAP and MS-CHAP.

Key points:
- Client role receives a binary challenge, finds a password key, and computes CHAP or MS-CHAP response structures.
- Server role gets a challenge from the auth server, passes it to the peer, collects user and response, and forwards the response to the auth server.
- Validates returned ticket/authenticator and exposes optional MS-CHAP secret bytes in `AuthInfo`.
- Implements local helpers for MD5 CHAP, LM response, NT response, and DES block hashing.

Dependencies:
- Uses factotum protocol framework, auth server protocol, MD4/MD5, and DES block cipher helpers.

Notable behavior:
- LM response is zeroed for passwords longer than 14 characters to avoid the LM vulnerability and buffer overflow.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/auth/factotum/chap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/auth/factotum/confirm.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/auth/factotum/confirm.c

Factotum confirmation and need-key queue support.

Key points:
- `confirmread`/`confirmflush` expose confirmation log messages.
- `confirmqueue` queues RPC reads waiting for user confirmation and logs `confirm tag=...` messages.
- `confirmwrite` parses `tag` and `answer=yes/no`, finds the waiting RPC, records the decision, and resumes it.
- `needkeyread`/`needkeyflush`, `needkeyqueue`, and `needkeywrite` implement the parallel “need key” notification queue.

Dependencies:
- Uses `Logbuf`, `Req`, `Fsstate`, attribute parsing, and `rpcread`.

Notable behavior:
- Source explicitly notes the need-key code is a copy of the confirmation queue code.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/auth/factotum/confirm.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/auth/factotum/dat.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/auth/factotum/dat.h

Shared factotum internal declarations and protocol interfaces.

Key points:
- Defines RPC phases, return codes, and core structs: `Fsstate`, `Key`, `Keyinfo`, `Keyring`, `Logbuf`, and `Proto`.
- `Fsstate` tracks per-RPC transient buffers, persistent auth attributes, phase state, protocol private state, pending confirmations, and `AuthInfo`.
- `Key` stores public/private attributes, protocol pointer, parsed protocol-private key data, and success count.
- Declares functions across confirm, filesystem, log, RPC, secstore, and utility modules.
- Declares available protocol implementations including APOP, CRAM, p9sk, CHAP, MSCHAP, p9cr, VNC, pass, RSA, WEP, and HTTP digest.

Dependencies:
- Includes Plan 9 auth, authsrv, libsec, mp, String, thread, fcall, and 9p headers.

Notable behavior:
- Uses an incomplete `State` type for protocol-private state.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/auth/factotum/dat.h -->