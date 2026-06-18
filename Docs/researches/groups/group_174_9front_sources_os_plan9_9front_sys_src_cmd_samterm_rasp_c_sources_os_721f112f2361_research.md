# Group Research: group_174_9front_sources_os_plan9_9front_sys_src_cmd_samterm_rasp_c_sources_os_721f112f2361

Scope: `Docs/research_subset_a.md` / `sources/os/plan9/9front`. All listed source files were read completely and researched individually.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/samterm/rasp.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/samterm/rasp.c

Purpose: Implements samterm's `Rasp` sparse text cache. A rasp is a linked list of `Section` records, each either holding actual runes or representing a missing span whose contents must be requested from the host editor.

Key routines:
- `rinit`, `rclear`: initialize and free a rasp section list.
- `rsinsert`, `rsdelete`, `splitsect`, `findsect`: maintain section boundaries and linked-list structure.
- `rresize`: updates cached document shape after insert/delete by removing old span sections and inserting a missing span for new text.
- `rdata`: replaces missing sections with actual rune data received from the host.
- `rclean`: coalesces adjacent sections with the same known/missing state, bounded by `TBLOCKSIZE` for text sections.
- `rload`: copies available cached runes from a range into global `scratch`; intentionally skips missing spans.
- `rmissing`, `rcontig`: measure missing or contiguous known/missing coverage.
- `Strgrow`: reallocates scratch rune storage.

Integration: Depends on `samterm.h` globals such as `scratch`, `nscralloc`, `alloc`, and `panic`, plus frame/text behavior elsewhere in samterm. Host protocol handlers use this file to decide when screen data is locally available versus missing.

Risks and invariants:
- The linked list is expected to be internally consistent; bad boundaries panic.
- Missing sections have `text == 0`, while known sections own allocated rune buffers.
- `rdata` panics if asked to overwrite already-known text, enforcing host/cache sequencing.
- `rload` returns a global scratch buffer, so callers must treat the result as transient.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/samterm/rasp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/samterm/samterm.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/samterm/samterm.h

Purpose: Central header for samterm, declaring editor-terminal data structures, process-wide globals, and cross-file function prototypes.

Key definitions:
- `Section`: one rasp span, with rune count, optional cached text, and next pointer.
- `Rasp`: sparse per-text document cache.
- `Text`: a samterm file/window model with rasp, tag, lock state, and `Flayer` screen layers.
- `Readbuf`: fixed-size host/plumb communication buffer.
- `Resource`: host, keyboard, mouse, plumb, and resize event resource IDs.

Exports and globals: Declares text/name/tag tables, cursor state, current layer pointers, command text, host/plumb channels, input controls, configuration flags, and host protocol output functions.

Integration: Includes `mesg.h` and ties together UI, host communication, text editing, scrolling, menu handling, rasp cache management, and display flushing.

Risks and invariants:
- Many globals are shared mutable state, so call ordering is part of the contract.
- `MAXFILES`, `READBUFSIZE`, and `NL` bound major runtime resources.
- `Untagged` uses `65535` as a sentinel tag value.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/samterm/samterm.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/samterm/scroll.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/samterm/scroll.c

Purpose: Implements samterm scrollbar drawing and mouse-driven scrolling.

Key routines:
- `scrtemps`: lazily allocates a temporary narrow image for drawing scrollbars when the layer is fully visible.
- `scrpos`: maps document positions `p0..p1` within `tot` into a scrollbar rectangle, ensuring at least a 2-pixel thumb.
- `scrdraw`: redraws the scrollbar only when its rectangle changes.
- `scrsleep`: sleeps in millisecond increments while polling mouse state, ending early on button changes.
- `scroll`: handles button 1/4 upward, button 5 downward, and button 2 absolute scroll positioning.

Integration: Uses `Flayer`, frame metrics, global `mousectl`, `mousep`, `display`, and helpers `screensize`, `scrtotal`, `forcenter`, `flushdisplay`, and `panic`.

Risks and behavior:
- Uses integer scaling with a shift fallback for documents larger than 1 MiB of runes.
- Wheel buttons return after one movement; mouse buttons auto-repeat with delay.
- Panics if mouse reads fail or if asked to draw without a backing frame image.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/samterm/scroll.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/sat.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/sat.c

Purpose: Command-line SAT front end that parses symbolic clauses and cardinality ranges, feeds them into Plan 9's `libsat`, and prints satisfying assignments.

Key structures:
- `Trie`: hash-trie node keyed by 64-bit FNV-like variable-name hash.
- `Var`: trie leaf with variable name, SAT variable number, and insertion-order list link.

Key routines:
- `hash`, `ctz`, `trieget`, `varget`: intern variable names and assign stable positive SAT IDs.
- `lex`: tokenizes variables, comments, brackets, punctuation, and newlines.
- `clause`: parses a clause line. Plain variable lists become OR clauses through `satadd1`; `[min,max]` prefixes become cardinality constraints through `satrange1`.
- `main`: handles `-1` for one positive-name model, `-m` for all models through `satmore`, or default output of each variable's signed value.

Integration: Depends on `<sat.h>` APIs `satnew`, `satadd1`, `satrange1`, `satsolve`, `satmore`, and `satval`.

Risks and limits:
- `lexbuf` truncates variable tokens beyond 511 bytes.
- Hash collisions are resolved by chaining off the trie leaf.
- Cardinality syntax is strict; malformed ranges call `sysfatal`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/sat.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/scat/bitinput.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/scat/bitinput.c

Purpose: Bitstream decoder support for DSS compressed image input used by `scat`.

Key routines:
- `start_inputing_bits`: resets bit-buffer state.
- `input_huffman`: reads enough bits to index a 6-bit Huffman table, consumes the table-specified bit length, and returns the decoded 4-bit value.
- `input_nybble`: reads a raw 4-bit nybble.

Data: `hufvals` and `huflens` define a compact Huffman decode table.

Integration: Called by `qtree.c` and `dssread.c` during DSS q-tree bit-plane decoding.

Risks:
- Uses file-static `buffer` and `bits_to_go`, so decoding is single-stream and stateful.
- Unexpected EOF exits with `"format"`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/scat/bitinput.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/scat/desc.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/scat/desc.c

Purpose: Static Dreyer/NGC description abbreviation dictionary for `scat`.

Content: `desctab` maps abbreviations and tokens such as object quality marks, brightness terms, compass directions, object morphology, Greek names, and catalog shorthand to prose strings.

Integration: Used by `prose.c` and `scat.c` via `prdesc` to expand compact NGC description strings when printing catalog records.

Risks:
- Table order matters because `prose.c` builds an index by first character and searches adjacent entries with the same initial byte.
- Contains UTF-8 strings for symbols like Greek letters and degrees.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/scat/desc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/scat/display.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/scat/display.c

Purpose: Sends generated DSS pictures or Plan 9 draw images to `/bin/page -w` for display.

Key routines:
- `displaypic`: forks page, writes a raw `k8` image header plus `Picture` bytes through a pipe, frees page-aligned segments with `segfree` as data is handed off, and frees the `Picture`.
- `displayimage`: forks page, writes a Plan 9 image using `writeimage`, then frees it.

Integration: Used by `image.c`/`scat.c` for DSS plate display and by `plot.c` for generated sky maps.

Risks:
- Relies on Plan 9 image pipe formats and `/bin/page`.
- Child process inherits a narrowed file descriptor group through `rfork`.
- `displaypic` has careful memory release behavior for large image buffers.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/scat/display.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/scat/dssread.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/scat/dssread.c

Purpose: Reads and decompresses a DSS image tile into an `Img`.

Format handling:
- Expects a 21-byte header starting with `0xdd 0x99`.
- Reads big-endian `nx`, `ny`, `scale`, and total-sum fields.
- Last three header bytes carry quadrant bit-plane counts.

Key routines:
- `dssread`: opens a tile, validates header, allocates `Img`, decodes data, applies scale, runs inverse H-transform, and returns pixels.
- `dodecode`: initializes bit input, decodes four q-tree quadrants, checks EOF nybble, then reads sign bits.
- `getlong`: big-endian 32-bit helper.

Integration: Calls `qtree_decode`, `input_nybble`, `start_inputing_bits`, and `hinv`.

Risks:
- Allocation size is `sizeof(Img) + (nx*ny-1)*sizeof(int)`; malformed dimensions could overflow.
- Fatal exits on unexpected compressed-data errors.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/scat/dssread.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/scat/header.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/scat/header.c

Purpose: Reads DSS plate headers and plate inventory, and mounts jukebox-backed DSS media when local files are unavailable.

Key routines:
- `getheader`: finds `<region>.hhh` locally or through DSS jukebox paths, parses FITS-like header fields into `Header.param`, computes plate RA/Dec in radians, and detects AMD coefficient availability.
- `getplates`: reads `lo_comp.lis`, fills global `plate[]` with region, center coordinates, and disk number.
- `dssmount`: mounts the jukebox service and 9660 filesystem for a requested DSS disk, caching the currently mounted disk number.

Integration: Used by `image.c` to choose and read the best DSS plate for a requested sky coordinate. Depends on `Hproto` mapping from header keyword to `Header.param` index.

Risks:
- Hard-coded paths `/lib/sky/dssheaders`, `/n/juke`, `/n/dss`, `/srv/tcp!jukefs`, and `/srv/9660`.
- Header parsing lowercases token names through `getword`.
- `getplates` caps global storage at `plate[2000]` and warns if too small.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/scat/header.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/scat/hinv.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/scat/hinv.c

Purpose: Performs inverse H-transform expansion for DSS image tiles.

Key routines:
- `hinv`: calculates rounded-up transform depth, repeatedly unshuffles coefficients in both dimensions, then reconstructs pixel values from H-transform components.
- `unshuffle`: interleaves half-array coefficients for strided 2D access.
- `unshuffle1`: optimized 1D unshuffle.

Integration: Called after q-tree and sign-bit decoding in `dssread.c`.

Risks:
- Uses integer shift/rounding assumptions from the DSS compression format.
- Allocates temporary storage sized by the larger image dimension and exits on allocation failure.
- Handles odd row/column dimensions explicitly.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/scat/hinv.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/scat/image.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/scat/image.c

Purpose: Builds an 8-bit grayscale DSS picture for a sky coordinate and requested angular size.

Flow:
- Initializes gamma defaults and derived gamma scaling.
- Loads plate inventory if needed.
- Chooses the closest DSS plate by angular distance.
- Converts requested RA/Dec to plate pixel coordinates through `getheader` and `xypos`.
- Computes target plate rectangle, clamps it to `0..14000`.
- Reads all 500x500 subplate tiles intersecting the rectangle through `dssmount` and `dssread`.
- Gamma maps pixels with `dogamma` and assembles a `Picture`.

Integration: Uses `plate[]`, `getplates`, `getheader`, `xypos`, `dssmount`, `dssread`, and global `gam`.

Risks:
- Subplate index uses `rad28`; out-of-range subplates abort the image request.
- The pixel indexing uses DSS tile layout assumptions with `ny` as fast-varying dimension.
- Returns `nil` on allocation/read failures after printing diagnostics.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/scat/image.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/scat/patch.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/scat/patch.c

Purpose: Converts between sky coordinates and `scat` patch IDs, where each patch is roughly one square degree and RA granularity decreases near the poles.

Key routines:
- `radec`: decodes a patch ID into RA hour/minute and declination degree.
- `patcha`: converts angular RA/Dec into patch ID.
- `patch`: validates RA/Dec, adjusts declination boundaries, quantizes RA by declination-dependent `round[]`, and packs RA/Dec into a long.

Integration: Used by `scat.c` for coordinate lookup, constellation expansion, and nearby-object expansion.

Risks:
- Invalid input prints diagnostics and calls `abort`.
- Patch packing is old-format dependent: high bits carry RA index, low byte carries shifted declination.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/scat/patch.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/scat/plate.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/scat/plate.h

Purpose: Older or alternate header declaring DSS plate/image structures and prototypes.

Content:
- Plate parameter enum equivalent to the `sky.h` plate parameter block.
- `Plate`, `Header`, and `Image` structures.
- Global plate/gamma/debug variables.
- Prototypes for plate conversion, DSS reading, q-tree decoding, image generation, and gamma mapping.

Integration: This header overlaps heavily with `sky.h`; the active scat files include `sky.h`, not this file.

Risks:
- Contains stale type declarations: for example `Image* dssread` and `Bitmap* image` differ from the active `Img*` and `Picture*` declarations in `sky.h`.
- If included in new code, it can conflict with current definitions.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/scat/plate.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/scat/plot.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/scat/plot.c

Purpose: Generates graphical sky charts from the current `scat` record set and obtains planet positions from `/bin/astro`.

Major areas:
- Display setup: `plotopen` initializes draw display, colors, stipples, and font.
- Projection math: vector helpers and `heavens` implement Doug McIlroy's observer-upright stereographic sky projection.
- Mapping: `setmap`, `maptoxy`, and `map` convert milliarcsecond RA/Dec to screen points.
- Bounds: `bbox`, `inbbox`, and `gridra` compute chart bounds and grid spacing.
- Rendering: `plot` draws coordinate grid, labels, stars, Abell clusters, galaxies, nebulae, clusters, and planets.
- Planet support: `runcommand`, `parseplanet`, and `astro` invoke `/bin/astro -p`, parse output, and store `Planetrec` values.

Integration: Depends on `map.h`, `draw`, global `rec/nrec`, `flatten`, `nameof`, and coordinate helpers from `scat.c`/`util.c`.

Risks:
- Uses global projection and map state.
- `parseplanet` assumes fixed-width astro output and mutates the input line at byte 10.
- Some drawing paths assume `font` is available; `plotopen` only warns if it cannot open the font.
- Planet sorting mutates the record array to render planets and shadow in front.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/scat/plot.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/scat/posn.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/scat/posn.c

Purpose: Converts celestial coordinates into DSS plate pixel positions.

Key routines:
- `traneqstd`: converts RA/Dec to standard tangent-plane coordinates `xi` and `eta`.
- `ppoinv`: applies linear PPO plate solution and converts microns to pixels.
- `amdinv`: applies AMD polynomial plate model using Newton iteration to invert from standard coordinates to plate coordinates.
- `xypos`: dispatches to AMD or PPO based on `Header.amdflag`.

Integration: Used by `image.c` after `getheader` to locate requested RA/Dec on a selected DSS plate.

Risks:
- `amdinv` uses fixed 50-iteration Newton solve and does not explicitly report non-convergence.
- Polynomial terms depend on header coefficients and plate scale units.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/scat/posn.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/scat/prose.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/scat/prose.c

Purpose: Expands compact catalog description strings into readable prose.

Key routines:
- `append`, `matchlen`: local string helpers.
- `prose`: walks an encoded description, translates known abbreviations through a descriptor table, handles punctuation, Messier tags, star-count shorthand, and magnitude notation.
- `prdesc`: lazily builds first-character indexes into the descriptor table and prints expanded prose plus original bracketed text.

Integration: Used by `scat.c` for NGC record descriptions, with `desctab` from `desc.c`.

Risks:
- Uses a static 512-byte output buffer and aborts if exceeded.
- Descriptor table must be sorted/grouped by first character for index lookup.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/scat/prose.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/scat/qtree.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/scat/qtree.c

Purpose: Decodes DSS q-tree compressed bit planes into pixel coefficient arrays.

Key routines:
- `qtree_decode`: loops through bit planes, handling direct bitmap or q-tree/Huffman-coded formats.
- `qtree_expand`: expands one quadtree level and reads new Huffman values for nonzero nodes.
- `qtree_copy`: expands 4-bit node values into 2x2 child bits.
- `qtree_bitins`: inserts decoded bit-plane bits into `Pix` output.
- `read_bdirect`: handles directly encoded nybble-packed bitmaps.

Integration: Called by `dssread.c`; uses `input_nybble` and `input_huffman` from `bitinput.c`.

Risks:
- Assumes output image array was zero-initialized.
- Exits on bad format code or memory failure.
- Has special handling for odd image dimensions.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/scat/qtree.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/scat/scat.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/scat/scat.c

Purpose: Main interactive astronomy catalog command. It loads binary sky catalogs, parses user commands, prints records, filters record sets, expands sky regions, plots charts, and displays DSS plates.

Major components:
- Catalog globals: SAO, NGC/IC, Messier index, names, Bayer entries, constellations, patch indexes.
- Startup: initializes `bin`/`bout`, optionally changes catalog directory, runs initial `astro`, then reads commands from stdin.
- Loaders: `loadsao`, `loadngc`, `loadabell`, `loadpatch`, `loadtype`, plus `nameopen`, `patchopen`, `mopen`, `constelopen`.
- Endian helpers: `Long` and `Short` convert little-endian on-disk fields.
- Record processing: `flatten` expands patch, named, and type records into concrete records; `sort` deduplicates non-planet records.
- Filtering: `cull` keeps or drops by magnitude, catalog, and object type.
- Lookup command parser: supports `sao`, `ngc`, `ic`, `abell`, `m`, constellations, coordinates, named stars, `expand`, `plot`, `astro`, `plate`, `gamma`, `keep`, `drop`, `flat`, and `print`.
- Printing: `prrec`, `nameof`, `printnames`, `ngcstring`, `dist_grp`, `rich_grp`.
- Star-name handling: `togreek`, `fromgreek`, `parsename`.

Integration: Central module for `scat`; calls support code in every other scat file.

Risks:
- Many fixed-size catalog constants and arrays are baked in.
- Binary catalog layout and little-endian fields must match `sky.h` packed structures.
- Some checks have old C idioms and subtle bugs, for example `if(j == 0)` in name lookup compares against absolute count after `j = nrec`.
- `#include "strings.c"` embeds data definitions directly into this translation unit.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/scat/scat.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/scat/sky.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/scat/sky.h

Purpose: Primary shared header for `scat`, defining catalog formats, record types, image/plate structures, globals, and prototypes.

Key content:
- Type enum for planets, patches, SAO, NGC/IC, Messier, named records, Abell, NGC object categories, and internal expansion types.
- Packed on-disk record structs: `NGCrec`, `Abellrec`, `Planetrec`, `SAOrec`, `Mindexrec`, `Bayerec`.
- Runtime `Record` union and `Patchrec`.
- Plate and DSS image structs: `Plate`, `Header`, `Img`, `Picture`.
- Unit macros for radians/degrees/arcseconds/milliarcseconds.
- Global declarations for catalog records, plate inventory, display state, gamma, bbox, and output.

Integration: Included by nearly every scat source file. It is the source of truth for binary catalog layout and cross-module function signatures.

Risks:
- Header defines non-extern globals (`nplate`, `plate`, `PI_180`, `gam`, etc.), which works only under Plan 9's build/link expectations or single-definition discipline.
- Packed structures are layout-critical.
- `Key` is explicitly assumed to be 4 bytes.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/scat/sky.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/scat/strings.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/scat/strings.c

Purpose: Static name tables for `scat`.

Content:
- `greek`: 1-indexed Greek-letter names.
- `greeklet`: corresponding Unicode rune values.
- `constel`: 1-indexed constellation abbreviations.
- `names`: accepted object-type aliases mapped to `sky.h` type enum values.

Integration: Included directly by `scat.c`, and used by name parsing, display labels, command parsing, and record filtering.

Risks:
- Index values are semantically significant, especially star-name encoding and constellation IDs.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/scat/strings.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/scat/util.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/scat/util.c

Purpose: Utility functions for angles, formatting, parsing, distance, and gamma mapping in `scat`.

Key routines:
- Constants: `PI_180`, `TWOPI`, `LN2`.
- `dangle`/`angle`: convert between radians and milliarcsecond disk angles.
- `hms`, `dms`, `ms`, `hm`, `hm5`, `dm`, `deg`: angle formatters.
- `getword`: parses lowercased header words and quoted strings.
- `getra`: parses mixed-unit RA/Dec angle strings.
- `dist`: angular distance on the sphere.
- `dogamma`: maps pixel intensity through configured gamma and inversion.

Integration: Used throughout `scat` for catalog parsing, display output, DSS image contrast, and coordinate math.

Risks:
- Most formatters return static buffers, so multiple calls in one expression can overwrite earlier results.
- `getra` accepts both RA-style and degree-style units, relying on caller context.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/scat/util.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/screenlock.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/screenlock.c

Purpose: Locks a Plan 9 terminal by covering the display, grabbing input focus/mouse, blanking after inactivity, and requiring user authentication to unlock.

Key routines:
- `readline`: raw password input with delete/backspace/control-U handling and inactivity timestamp updates.
- `checkpassword`: loops until `auth_userpasswd(getuser(), password)` succeeds or key acquisition is needed.
- `blanker`: writes `blank` to `/dev/mousectl` after 5 seconds of no input.
- `grabmouse`: keeps the pointer centered by writing mouse reposition commands.
- `top`: watches `/dev/wctl` and makes the lock window current.
- `lockscreen`: opens a full-screen window, switches console to raw, draws `/lib/bunny.bit` and user/time text, starts helper procs, and clears cursor.
- `threadmain`: parses `-d`, locks, authenticates, exits all threads.

Integration: Uses Plan 9 draw/thread/auth/newwindow devices and `/dev/cons`, `/dev/mouse`, `/dev/wctl`.

Risks:
- Security depends on maintaining current window and mouse grab behavior.
- Password buffer is zeroed after use, but `AuthInfo` handling breaks out on `needkey`.
- Debug mode disables mouse recentering.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/screenlock.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/scuzz/cdaudio.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/scuzz/cdaudio.c

Purpose: Implements MMC CD audio and mechanism helper commands for the scuzz SCSI shell.

Key routines:
- `SRcdpause`, `SRcdstop`: pause/resume and stop playback.
- `_SRcdplay`: raw play by LBA and length.
- `SRcdplay`: optionally maps a track number to LBA/length by reading TOC before calling `_SRcdplay`.
- `SRcdload`: load/eject media or changer slot.
- `SRcdstatus`: read mechanism status.
- `SRgetconf`: read MMC configuration.

Integration: Uses `ScsiReq` and `SRrequest` from `scsireq.c`, constants from `scsireq.h`, and `SRTOC` from `cdr.c`.

Risks:
- Static `tracks[100]` assumes TOC fits.
- Stack command buffers are safe only because `SRrequest` is synchronous.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/scuzz/cdaudio.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/scuzz/cdr.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/scuzz/cdr.c

Purpose: Builds MMC and older vendor-specific CD-R/CD-RW SCSI commands.

Key routines:
- MMC: `SRblank`, `SRsynccache`, `SRTOC`, `SRrdiscinfo`, `SRrtrackinfo`.
- Older/vendor-specific: `SRfwaddr`, `SRtreserve`, `SRtinfo`, `SRwtrack`, `SRmload`, `SRfixation`.

Integration: Called by `scuzz.c` command handlers.

Risks:
- `SRtreserve` and `SRwtrack` validate transfer sizes against `rp->lbsize` and `maxiosize`.
- Command encodings are a mix of standard MMC and old device-specific opcodes.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/scuzz/cdr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/scuzz/changer.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/scuzz/changer.c

Purpose: Implements SCSI medium changer commands.

Key routines:
- `SReinitialise`: initialize element status.
- `SRmmove`: move medium from source to destination with optional invert bit.
- `SRestatus`: read element status for a type and requested allocation length.

Integration: Invoked by `scuzz.c` handlers `einit`, `mmove`, and `estatus`.

Risks:
- Minimal validation; caller parses and bounds arguments.
- Command buffers assume synchronous request lifetime.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/scuzz/changer.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/scuzz/scsireq.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/scuzz/scsireq.c

Purpose: Core SCSI request library used by scuzz and related tools.

Major functions:
- Basic commands: `SRready`, `SRrewind`, `SRreqsense`, `SRformat`, `SRrblimits`, `SRseek`, `SRfilemark`, `SRspace`, `SRinquiry`, mode select/sense, `SRstart`, `SRrcapacity`.
- I/O: `SRread` and `SRwrite` choose 6-byte or 10-byte direct-access commands, or sequential tape commands, validate block alignment, update offsets, and handle tape short reads/filemarks.
- Transport: `request` writes command bytes to `/dev/sdXX/raw`, transfers data, and reads status text.
- `SRrequest`: wraps transport, retries busy status, converts CHECK CONDITION into sense data, and supports USB through `umsrequest`.
- Open/close: `SRopenraw`, `SRopen`, `SRclose`; device-specific open helpers configure direct, sequential, WORM, printer, or changer devices.

Integration: Shared by `scuzz.c`, CD helpers, changer helpers, USB mass storage users, and `cdfs` per header comment.

Risks:
- Explicit comments note incomplete LUN support.
- Exabyte and forced 6-byte command flags alter behavior globally.
- Sequential-device short-record handling relies on sense fields.
- Raw device protocol expects Plan 9 `/dev/sdXX/raw` behavior: write CDB, transfer data, read status.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/scuzz/scsireq.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/scuzz/scsireq.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/scuzz/scsireq.h

Purpose: Shared SCSI request interface and constants.

Key definitions:
- `ScsiPtr`: pointer/count/write tuple for command or data transfer.
- `ScsiReq`: open target state including flags, unit path, LUN, block size, offset, fd, USB state, command/data buffers, status, sense, inquiry, and read-block flag.
- Device flags for open, sequential, read-only, WORM, changer, 6-byte mode select, 10-byte read/write, USB.
- Status constants and software status values.
- SCSI command opcode enum covering basic SCSI, MMC CD, changer, DVD, and vendor-specific commands.
- Big-endian get/put macros.

Integration: Included by all `scuzz` implementation files and referenced by USB disk/cdfs code.

Risks:
- `Umsc` is incomplete here; USB users must provide implementation.
- `GETBELONG`/`PUTBELONG` macros assume byte pointer arguments and no side effects.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/scuzz/scsireq.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/scuzz/scuzz.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/scuzz/scuzz.c

Purpose: Interactive SCSI command shell and utility.

Major areas:
- Global transfer buffer and options: `maxiosize`, `exabyte`, `force6bytecmds`, `verbose`.
- File/pipeline I/O: `mkfile` supports direct files or `|command` pipes for read/write commands.
- Command handlers: readiness, rewind, request sense, format, read/write, seek, filemark/space, inquiry, mode sense/select, start/stop/eject/ingest, capacity, CD-R/MMC commands, CD audio, changer commands, probe/open/close/help.
- Decoders: prints mode pages, TOC/PMA/session data, disc info, track info, CD mechanism status, changer element status.
- Parser: `tokenise` and `parse` support shell-like single quotes with doubled embedded quotes.
- Main loop: optionally opens an initial target, reads commands from stdin, dispatches through `scsicmd[]`, prints `ok` or status/sense diagnostics.

Integration: Command table calls all `SR*` helpers across `scsireq.c`, `cdr.c`, `cdaudio.c`, `changer.c`, and `sense.c`.

Risks:
- Many decoders assume response buffers contain enough bytes for the fields printed.
- Some older CD-R commands are compiled but commented out of the command table.
- `cmdmodesense10` leaks `list` if `SRmodesense10` fails before `free`.
- Destructive commands are available interactively with limited safeguards.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/scuzz/scuzz.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/scuzz/sense.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/scuzz/sense.c

Purpose: Formats SCSI sense data for scuzz output.

Key routine:
- `makesense`: prints sense key text, optional decoded ASC/ASCQ text through `scsierror`, and raw sense bytes.

Integration: Uses libdisk's `/sys/lib/scsicodes` mapping and global `bout`.

Risks:
- Assumes `rp->sense[7]` length is trustworthy when printing `8 + sense[7]` bytes.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/scuzz/sense.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/seconds.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/seconds.c

Purpose: Converts absolute date/time strings to seconds since the epoch.

Behavior:
- Optional `-f fmt` parses using a user-supplied `tmparse` format.
- Without `-f`, tries known asctime/RFC3339 forms, then combinations of date, time, and zone formats.
- Loads local timezone via `tzload("local")`.
- Rejects trailing non-space junk.
- Prints `tmnorm(&tm)` per input argument.

Integration: Uses Plan 9 time parsing formats and `Tm`/`Tzone`.

Risks:
- Inputs are per argv item, so shell quoting is required for dates with spaces.
- On first unparseable input, calls `sysfatal`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/seconds.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/sed.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/sed.c

Purpose: Plan 9 stream editor implementation.

Major components:
- Fixed command storage `pspace[MAXCMDS]`, text buffer `addspace`, line/hold buffers, label table, file cache, and output file table.
- Address model supports none, `$`, line number, regexp, and last regexp.
- `main`: parses `-e`, `-f`, `-g`, `-n`, `-u`, and ignores Unix compatibility `-E`/`-r`; compiles scripts; enrolls input files; executes.
- `fcomp`: compiles sed commands, addresses, blocks, labels, branches, substitutions, transliterations, append/change/insert text, read/write files.
- Regex support: `compile`, `match`, and Plan 9 `regexp.h`.
- Execution: `execute`, `executable`, and `command` apply commands to pattern/hold space.
- Substitution: `substitute`, `dosub`, `place` handle global substitutions, zero-length matches, `&`, and back references.
- I/O: `gline` concatenates enrolled input streams, supports implicit final newline, `$` detection, and unbuffered flush callback.
- Pending output: `arout` processes append/read queues after each cycle.

Integration: Standalone command using Plan 9 Bio, rune, and regexp APIs.

Risks:
- Fixed-size limits include command count, line size, append buffer, labels, files, and subexpressions.
- Uses global mutable interpreter state.
- `ycomp` allocation size depends on highest rune in source set.
- `putline` always appends newline, matching sed pattern-space semantics.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/sed.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/seg.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/seg.c

Purpose: Reads or writes a named Plan 9 shared segment at a given offset.

Behavior:
- Flags: `-r` read, `-w` write, `-W` 2-byte access, `-L` 4-byte access; default size is 1 byte.
- Arguments: segment name, segment size, offset, and optional data for writes.
- Uses `segattach` to map the segment.
- Reads little-endian byte/word/long manually; writes by casting into mapped memory.

Risks:
- No explicit bounds check for `port + size <= segsize`.
- Write path may perform unaligned stores depending on offset.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/seg.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/seq.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/seq.c

Purpose: Prints numeric sequences.

Behavior:
- Usage: `seq [-fformat] [-w] [first [incr]] last`.
- Defaults: first 1, increment 1.
- `-f` supplies a `sprint` format, with newline appended if missing.
- `-w` builds constant-width decimal output and zero-fills leading spaces.
- Supports positive and negative increments, rejects zero increment.

Risks:
- Floating-point loop accumulation can drift for fractional increments.
- Format buffer for `-f` is 4096 bytes but user format is not otherwise validated.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/seq.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/sha1sum.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/sha1sum.c

Purpose: Computes SHA-1 by default or SHA-2 digests with `-2 bits`.

Behavior:
- Supported SHA-2 widths: 224, 256, 384, 512.
- Installs `%M` formatter to print digest bytes as lowercase hex.
- Reads stdin if no files are given; otherwise prints digest and filename per file.
- Tracks first error text in `exitstr` and exits with that string if any error occurred.

Integration: Uses `libsec` digest functions.

Risks:
- Continue-on-error for files; exit status carries last stored error string.
- Digest buffer sized for SHA-512 maximum.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/sha1sum.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/size.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/size.c

Purpose: Prints text, data, bss, and total sizes for Plan 9 executable files.

Behavior:
- Uses `crackhdr` from `<mach.h>` to parse headers.
- Default file is `8.out` when no args are given.
- Output format: `<txt>t + <data>d + <bss>b = <total>\t<file>`.

Risks:
- Only handles files recognized by `crackhdr`.
- Exits `"error"` if any input fails.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/size.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/skelfs.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/skelfs.c

Purpose: Minimal synthetic 9P filesystem that presents a dynamically named skeleton file or directory.

Model:
- Per-fid `Skel` holds selected name and mode.
- Qid path encodes session and one of root, intermediate dir, or skeleton node.
- First walk from root captures the walked name unless mode is `'e'`.
- `step` computes qids and stat data for root, directory, and skeleton entries.
- `dirgen` exposes at most one child.
- Read-only opens only; reads are directory reads.

Options:
- `-D` chatty 9P.
- `-s service` post service.
- `-i` serve on stdio.
- `-t mode` default skeleton mode: file, directory, or empty-like behavior.
- Optional mount point defaults to `/mnt/skel`.

Integration: Uses lib9p helpers `walkandclone`, `postmountsrv`, and `srv`.

Risks:
- Per-fid name state means different walks can produce different skeleton names.
- File contents are always empty.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/skelfs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/sleep.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/sleep.c

Purpose: Sleeps for a requested number of seconds, with optional millisecond fraction.

Behavior:
- Avoids floating point for bootstrap usefulness.
- Sleeps in chunks no larger than `MAXSEC` to avoid millisecond overflow.
- Parses fractional part to three decimal digits and sleeps remaining milliseconds.
- No argument exits immediately.

Risks:
- Fraction parsing truncates beyond three digits by mutating `p[3]`.
- Negative or malformed inputs mostly result in no sleep or integer parser behavior.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/sleep.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/snap/read.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/snap/read.c

Purpose: Reads serialized process snapshot files into in-memory `Proc`, `Seg`, `Page`, and `Data` structures.

Key routines:
- `findpid`: locates a process in the loaded list.
- `findpage`: resolves a page reference by pid, memory/text type, and aligned offset.
- `Breadnumber`, `Breadulong`, `Breaduvlong`: parse fixed-width decimal fields with space padding.
- `readdata`: reads a length-prefixed proc metadata section.
- `readseg`: reads segment offset/length and page records. Page records can be zero (`z`), raw (`r`), or references to earlier memory/text pages (`m`/`t`).
- `readsnap`: validates header, iterates process sections, reads known proc files, memory segments, and text segments.

Integration: Used by `snapfs.c` to replay a snapshot as a 9P `/proc`-like tree.

Risks:
- The file format is custom, positional, and fatal on malformed references.
- Page references can only point to already loaded process/page data.
- Alignment to `Pagesize` is enforced for referenced pages.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/snap/read.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/snap/snap.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/snap/snap.c

Purpose: CLI entry point for taking process snapshots.

Behavior:
- Usage: `snap [-d] [-o snapfile] pid...`.
- Opens output, writes a snapshot header containing time, user, system, architecture, kernel root mtime, and terminal.
- Skips snapshotting its own pid.
- Calls `snap(pid, 1)` for each requested process and serializes with `writesnap`.

Integration: Uses `take.c` for capture, `write.c` for serialization, and `util.c` allocation helpers.

Risks:
- Requires readable `/proc/<pid>` files.
- Snapshot output defaults to stdout.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/snap/snap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/snap/snap.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/snap/snap.h

Purpose: Shared data model and prototypes for the `snap` tools.

Key definitions:
- Proc file enum: segment, fd, fpregs, kregs, noteid, ns, proc, regs, status.
- `Pagesize = 1024`, independent of kernel page size.
- `Data`: captured proc-file byte blob.
- `Seg`: memory/text segment with offset, length, page pointers.
- `Page`: deduplicated page data plus serialization reference metadata.
- `Proc`: process snapshot with proc-file data, memory segments, and text segment.

Integration: Included by capture, read, write, snapfs, and utility files.

Risks:
- `debug` is defined in the header, creating a shared global under Plan 9 build assumptions.
- `Data.data[1]` uses variable trailing allocation idiom.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/snap/snap.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/snap/snapfs.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/snap/snapfs.c

Purpose: Mounts a snapshot file as a read-only `/proc`-like 9P filesystem.

Behavior:
- Reads snapshot with `readsnap`.
- Builds a lib9p tree with one directory per process.
- Creates `ctl`, `mem`, optional `text`, and captured proc-file entries.
- `fsread` dispatches to `memread` for `mem`/`text` virtual files or `dataread` for captured metadata.
- Default mount point is `/proc`; `-a` mounts after existing contents; `-m` changes mount point.

Integration: Uses lib9p file tree APIs and `findpage` from `read.c`.

Risks:
- `memread` reads only within one 1024-byte snapshot page per request.
- `ctl` is created but has no special behavior.
- Mounting over `/proc` changes process namespace semantics for clients.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/snap/snapfs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/snap/take.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/snap/take.c

Purpose: Captures live Plan 9 process state into snapshot data structures, with page deduplication.

Key routines:
- `sumr`: small 16-bit rolling checksum used for page hash buckets.
- `datapage`: interns page data by checksum and full comparison; marks all-zero pages specially.
- `readsection`: reads `/proc/<pid>/<section>` into a `Data` blob.
- `readseg`: reads memory/text bytes from an fd into 1024-byte deduplicated pages.
- `stackptr`: reads executable header and register data to locate the architecture's stack pointer.
- `snap`: reads proc metadata, optional text file, segment table, memory segments, and a reduced stack region around the stack pointer.

Integration: Called by `snap.c`; writes are handled by `write.c`.

Risks:
- Deduplication hash is weak but protected by full `memcmp`.
- Segment parsing depends on `/proc/<pid>/segment` textual layout.
- Stack capture intentionally trims the stack instead of reading the entire segment.
- Some segment array entries can remain nil if reading fails.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/snap/take.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/snap/util.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/snap/util.c

Purpose: Allocation helpers for `snap`.

Functions:
- `emalloc`: malloc plus zero-fill, fatal on failure.
- `erealloc`: realloc, fatal on failure except zero-size.
- `estrdup`: strdup, fatal on failure.

Integration: Used across snapshot capture, read, write, and filesystem replay.

Risks: Fatal-on-OOM behavior simplifies callers but makes partial recovery impossible.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/snap/util.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/snap/write.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/snap/write.c

Purpose: Serializes captured `Proc` snapshots into the custom snapshot file format.

Key data:
- `pfile[]`: maps proc-file enum entries to `/proc` file names.

Key routines:
- `writeseg`: writes segment offset/length followed by per-page records. Already-written pages become references (`m` or `t` plus pid/offset), zero pages become `z`, and new pages become raw `r` followed by bytes.
- `writesnap`: writes all captured proc-file data, optional text segment, and memory segment list for one process.

Integration: Paired with `read.c`; deduplication metadata set here is later used for page references.

Risks:
- Serialization mutates `Page` objects by marking them written and setting type/pid/offset.
- Output format relies on fixed-width decimal fields and single-character page tags.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/snap/write.c -->