# Group Research: group_1624_plan9_sources_os_plan9_plan9_sys_src_cmd_unix_drawterm_libdraw_allo_3f8b7851d1d0

Scope validated against `Docs/research_subset_a.md`: all paths are under `sources/os/plan9/plan9`. Each listed file was read completely for this grouped report.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libdraw/alloc.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libdraw/alloc.c

Implements client-side `Image` allocation, lookup by devdraw name, naming, and freeing for drawterm’s libdraw interface. It serializes draw protocol messages (`b`, `n`, `N`, `f`) into the display buffer with `bufimage`, `BPLONG`, and `flushimage`.

Key functions:
- `allocimage` and `_allocimage`: validate channel descriptors, allocate a server-side image id, send allocation metadata, create or initialize an `Image`.
- `namedimage`: requests an existing named devdraw image and reads its geometry/channel metadata from `ctlfd`.
- `nameimage`: binds or unbinds an image name in devdraw.
- `_freeimage1` and `freeimage`: send free messages and unlink window images from the display window list.

Important behavior:
- Replicated images receive a huge finite clipping rectangle to avoid overflow while behaving practically infinite.
- Allocation failures after server-side creation attempt to send an `f` free message to avoid leaking server resources.
- Channel parsing depends on `chantodepth` and `strtochan` from libdraw channel helpers.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libdraw/alloc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libdraw/arith.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libdraw/arith.c

Provides foundational Plan 9 geometry and color helpers used throughout drawterm drawing code.

Key functions:
- Constructors: `Pt`, `Rect`, `Rpt`.
- Point/rectangle arithmetic: `addpt`, `subpt`, `insetrect`, `divpt`, `mulpt`, `rectsubpt`, `rectaddpt`.
- Predicates: `eqpt`, `eqrect`, `rectXrect`, `rectinrect`, `ptinrect`.
- Normalization/combination: `canonrect`, `combinerect`.
- `setalpha`: premultiplies RGB channels by an alpha byte and writes the new RGBA value.
- `Rfmt`, `Pfmt`: `Fmt` printers for rectangles and points.

Global data:
- `drawld2chan[]` maps old ldepth values to channel descriptors.
- `log2[]`, `ZP`, and `ZR` provide compatibility utilities and zero geometry constants.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libdraw/arith.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libdraw/bytesperline.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libdraw/bytesperline.c

Computes storage width for image scan lines.

Key functions:
- `unitsperline`: shared implementation for rounding rectangle pixel spans to a target unit size.
- `wordsperline`: returns scan-line length in `ulong` units.
- `bytesperline`: returns scan-line length in bytes.

Important behavior:
- Handles negative `r.min.x` carefully by making the division domain positive before rounding.
- Aborts if called with an invalid image depth outside `1..32`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libdraw/bytesperline.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libdraw/chan.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libdraw/chan.c

Converts between Plan 9 draw channel descriptors and textual channel strings.

Key functions:
- `chantostr`: validates a descriptor with `chantodepth`, reverses descriptor byte order, and emits strings like `r8g8b8`.
- `strtochan`: parses channel strings into packed descriptors using channel names `rgbkamx`.
- `chantodepth`: validates per-channel bit counts and aggregate depth rules, then returns total depth.

Important behavior:
- Avoids `ctype` by using a local whitespace helper.
- Rejects invalid channel types, bit counts greater than 8, zero-bit channels, and aggregate depths that do not align to Plan 9 image rules.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libdraw/chan.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libdraw/defont.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libdraw/defont.c

Embeds the default Plan 9 bitmap font data for drawterm. The large `defontdata[]` array contains an uncompressed `lucm/latin1.9` font image plus packed font metrics.

Key data/functions:
- `defontdata[]`: byte representation of the default font image and fontchar records.
- `sizeofdefont`: size of embedded font data.
- `_unpackinfo`: converts packed 6-byte fontchar records into `Fontchar` structures.

Important behavior:
- This file is mostly static data; runtime interpretation is performed by libmemdraw’s default-font loader.
- `_unpackinfo` decodes `x`, `top`, `bottom`, `left`, and `width` for `n+1` entries, preserving the Plan 9 subfont convention.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libdraw/defont.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libdraw/drawrepl.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libdraw/drawrepl.c

Implements coordinate wrapping for replicated images.

Key functions:
- `drawreplxy`: maps a coordinate into `[min, max)` using modulo arithmetic corrected for negative inputs.
- `drawrepl`: applies `drawreplxy` to both axes of a `Point` within a `Rectangle`.

Used by clipping, repeated image reads, and raster operations that need source or mask tiling.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libdraw/drawrepl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libdraw/icossin.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libdraw/icossin.c

Provides integer sine/cosine lookup for degree angles.

Key data/function:
- `sinus[91]`: quarter-wave sine table scaled to `1024`.
- `icossin`: normalizes degrees to `0..359`, maps to the correct quadrant, and returns scaled cosine and sine.

Used by arc and geometry code where deterministic integer math is preferred over floating point.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libdraw/icossin.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libdraw/icossin2.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libdraw/icossin2.c

Computes scaled sine/cosine for a vector `(x, y)` using tangent lookup tables and interpolation.

Key data/function:
- `sinus[]` and `cosinus[]`: values for `sin(atan(t))` and `cos(atan(t))`, scaled to `1024`.
- `icossin2`: handles axis-aligned vectors, sign correction, slope selection, table lookup, and linear interpolation.

Used by wide line rendering to compute perpendicular offsets and arrowhead geometry.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libdraw/icossin2.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libdraw/rectclip.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libdraw/rectclip.c

Provides in-place rectangle intersection.

Key function:
- `rectclip`: checks overlap, then clamps the first rectangle to the bounds of the second.

Important behavior:
- Expands the overlap test inline rather than calling `rectXrect`, explicitly for speed.
- Returns `0` when the rectangles do not overlap and `1` after successful clipping.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libdraw/rectclip.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libdraw/rgb.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libdraw/rgb.c

Implements Plan 9 color map conversion helpers.

Key functions:
- `rgb2cmap`: chooses the nearest 8-bit color-map entry by Euclidean RGB distance.
- `cmap2rgb`: decodes Plan 9 CMAP8 indices into 24-bit RGB.
- `cmap2rgba`: extends `cmap2rgb` with opaque alpha.

Important behavior:
- The original direct inverse mapping is retained in comments but replaced by slower nearest-color search for better visual output on arbitrary RGB triples.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libdraw/rgb.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libip/Makefile -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libip/Makefile

Builds `libip.a` for drawterm.

Key content:
- Includes `../Make.config`.
- Archives `eipfmt`, `parseip`, `classmask`, `bo`, and `ipaux` object files.
- Uses standard `$(CC) $(CFLAGS)` compile rule, `$(AR)`, and `$(RANLIB)`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libip/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libip/bo.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libip/bo.c

Provides host/network byte-order helpers independent of platform endianness.

Key functions:
- Writers: `hnputv`, `hnputl`, `hnputs` for 64-, 32-, and 16-bit big-endian storage.
- Readers: `nhgetv`, `nhgetl`, `nhgets` for big-endian byte arrays.

Important behavior:
- Operates on `uchar*` byte buffers directly and avoids alignment assumptions.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libip/bo.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libip/classmask.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libip/classmask.c

Computes default IP network masks.

Key functions/data:
- `classmask`: default classful IPv4 masks stored in IPv6-mapped form.
- IPv6 special masks for loopback, link-local, multicast, and solicited-node multicast.
- `defmask`: returns an appropriate default mask for IPv4-mapped or IPv6 addresses.
- `maskip`: applies a mask bytewise.

Important behavior:
- IPv4 detection depends on `isv4`.
- IPv6 defaults are prefix based, with all-bits mask as the fallback.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libip/classmask.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libip/eipfmt.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libip/eipfmt.c

Implements Plan 9 `Fmt` conversions for Ethernet and IP addresses.

Key function:
- `eipfmt`: handles `%E`, `%I`, `%i`, `%V`, and `%M`.

Important behavior:
- IPv4-mapped IPv6 addresses print as dotted quad.
- IPv6 formatting performs longest zero-run elision.
- Masks print as `/prefix` only when the mask is a valid contiguous prefix; otherwise they fall back to full IP formatting.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libip/eipfmt.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libip/ipaux.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libip/ipaux.c

Defines common IP address constants and IPv4/IPv6 conversion helpers.

Key globals:
- `IPv4bcast`, `IPv4allsys`, `IPv4allrouter`, `IPallbits`, `IPnoaddr`, `v4prefix`.

Key functions:
- `isv4`: detects IPv4-mapped IPv6 addresses.
- `v4tov6`: maps a 4-byte IPv4 address to 16-byte IPv4-mapped IPv6 form.
- `v6tov4`: extracts IPv4 bytes from mapped addresses and handles all-zero no-address specially.

Important behavior:
- Conversion code is manually unrolled for speed and to avoid library calls in common paths.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libip/ipaux.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libip/parseip.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libip/parseip.c

Parses IPv4, IPv6, masks, and IPv4 CIDR notation.

Key functions:
- `v4parseip`: parses classful IPv4 shorthand and dotted forms.
- `parseip`: parses IPv4 or IPv6 into 16-byte representation, including `::` elision and IPv4 tails.
- `parseipmask`: accepts `/bits` or address-style masks, including old IPv4 mask style.
- `v4parsecidr`: parses IPv4 address plus optional `/prefix`, defaulting via `defmask`.

Important behavior:
- On parse error, clears `to` to a distinctive zero address and returns `-1`.
- Delimiter logic prevents accidental partial parsing such as interpreting `delete` as `de::`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libip/parseip.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmemdraw/Makefile -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmemdraw/Makefile

Builds `libmemdraw.a`, the in-memory raster drawing library.

Key content:
- Includes `../Make.config`.
- Archives image allocation, drawing, shape, font, IO, color-map, and stub hardware-draw objects.
- Does not include test/generator programs such as `drawtest.c`, `arctest.c`, or `mkcmap.c` in the library object list.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmemdraw/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmemdraw/alloc.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmemdraw/alloc.c

Implements allocation and addressing for `Memimage`.

Key functions:
- `memimagemove`: updates `Memdata` after compaction-style movement.
- `allocmemimaged`: wraps existing `Memdata` with a `Memimage`.
- `_allocmemimage`: allocates backing memory and metadata.
- `_freememimage`: reference-counted release of backing data.
- `wordaddr`, `byteaddr`: convert image points to backing-memory addresses.
- `memsetchan`: parses channel descriptors into depth, flags, shifts, masks, and channel counts.

Important behavior:
- Computes `zero` so arbitrary rectangle origins, including negative x, map correctly into backing storage.
- Uses `memdefcmap` automatically for color-mapped images.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmemdraw/alloc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmemdraw/arc.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmemdraw/arc.c

Draws elliptical arc sectors using temporary masks.

Key function:
- `memarc`: creates a wedge mask for angular bounds, creates a full ellipse mask, intersects them, then draws source through the resulting mask.

Important behavior:
- Handles negative radii by absolute value.
- Converts Plan 9 screen-coordinate orientation by negating angles.
- If the arc span is at least 360 degrees, delegates to `memellipse`.
- Uses `icossin`, `memfillpoly`, `memellipse`, and `memimagedraw`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmemdraw/arc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmemdraw/arctest.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmemdraw/arctest.c

Small timing/test program for `memarc`.

Key behavior:
- Initializes memdraw, allocates a `CMAP8` image, and repeatedly draws an arc based on `argv[1]`.
- Measures elapsed nanoseconds with a small timing overhead subtraction.
- Provides local `drawdebug`, `rdb`, and `iprint` stubs for standalone testing.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmemdraw/arctest.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmemdraw/cload.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmemdraw/cload.c

Loads compressed image data into a `Memimage`.

Key function:
- `_cloadmemimage`: decodes the Plan 9 image compression format into the target rectangle.

Important behavior:
- Uses a circular history buffer of `NMEM` bytes.
- Bytes with high bit set encode literal runs; other bytes encode back-reference offset and match length.
- Validates rectangle containment, buffer length, and scan-line phase consistency.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmemdraw/cload.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmemdraw/cmap.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmemdraw/cmap.c

Generated default `Memcmap` table.

Key content:
- Static `Memcmap def` containing:
  - `cmap2rgb[3*256]`: CMAP8 index to RGB triples.
  - `rgb2cmap[16*16*16]`: 4-bit-per-channel RGB cube to nearest CMAP8 index.
- `memdefcmap`: global pointer to the default table.
- `_memmkcmap`: no-op because the table is pre-generated.

Used by color-mapped image conversion in `draw.c` and allocation/channel setup.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmemdraw/cmap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmemdraw/cread.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmemdraw/cread.c

Reads compressed Plan 9 image files into `Memimage`.

Key function:
- `creadmemimage`: parses compressed-image headers, allocates a destination image, reads compressed blocks, and calls `cloadmemimage`.

Important behavior:
- Supports both new textual channel descriptors and old ldepth headers.
- Uses `_compblocksize` to bound compressed block allocation.
- Old image data is bit-twiddled before decompression.
- Validates rectangle and per-block `maxy`/byte-count fields.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmemdraw/cread.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmemdraw/defont.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmemdraw/defont.c

Builds a `Memsubfont` from embedded default font data.

Key function:
- `getmemdefont`: aligns `defontdata`, parses image header, wraps bitmap data in `Memdata`, creates a `Memimage`, decodes fontchar records, and returns an allocated subfont.

Important behavior:
- `Memdata.base` is set so the embedded byte array is not freed as allocated pixel memory.
- Uses `_unpackinfo` from libdraw default font support.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmemdraw/defont.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmemdraw/draw.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmemdraw/draw.c

Core in-memory draw engine for Plan 9 image compositing.

Main responsibilities:
- Initializes global solid images (`memwhite`, `memblack`, `memopaque`, `memtransparent`) in `_memimageinit`.
- Clips and normalizes draw parameters in `_memimagedrawsetup` and `drawclip`.
- Dispatches draw operations through `_memimagedraw`: hardware hook, optimized memory paths, character drawing, then general alpha compositing.
- Implements pixel readers/writers for sub-byte greyscale, CMAP8, byte-aligned RGB/alpha formats, and conversion buffers.
- Implements alpha and boolean Porter-Duff-style composition for Plan 9 draw operators.
- Provides fast paths for solid fills, same-channel copies, 1-bit boolean copies, and glyph masks.
- Converts between image pixel encodings and RGBA with `_imgtorgba`, `_rgbatoimg`, and `_pixelbits`.
- Provides `_memfillcolor`.

Important internal structures:
- `Memdrawparam`: draw setup contract shared by callers.
- `Buffer` and `Param`: scan-line channel buffers and reader/writer state.
- Precomputed bit replication/unpacking tables for 1/2/4-bit image depths.

Important behavior:
- Handles replicated sources/masks by coordinate wrapping and optional scan-line caching.
- Detects source/destination overlap and chooses reverse scan direction or buffering.
- Uses integer rounded division approximations for alpha math.
- Supports fallback-only hardware acceleration via `hwdraw`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmemdraw/draw.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmemdraw/drawtest.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmemdraw/drawtest.c

Stochastic test program for `memimagedraw`.

Key behavior:
- Allocates destination, source, mask, and temporary images with configurable channel descriptors.
- Randomizes image contents, including alpha-respecting random pixels.
- Verifies one-pixel, line, rectangle, replicated-source, replicated-mask, and combined replicated cases.
- Compares bulk `memimagedraw` output against repeated one-pixel reference drawing.
- Includes helpers for dumping images, reading/writing pixels in arbitrary channel formats, mask extraction, greyscale conversion, and replication simulation.

Important scope:
- Tests compositing correctness extensively for disjoint source/destination/mask images.
- Explicitly notes it does not test overlapping image behavior.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmemdraw/drawtest.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmemdraw/ellipse.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmemdraw/ellipse.c

Rasterizes filled and stroked ellipses.

Key functions:
- `newstate`, `step`: integer ellipse stepping state based on residual error.
- `memellipse`: main ellipse drawing routine.
- `bellipse`: draws very thick skinny ellipses by brushing with a circular mask.
- `erect`, `epoint`, `eline`: draw horizontal spans, brushed points, and brushed lines.

Important behavior:
- Supports filled ellipses when thickness `t < 0`.
- For normal thickness, fills between outer and inner ellipses.
- Uses `memdraw` with `memopaque` masks and source point adjustment.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmemdraw/ellipse.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmemdraw/fillpoly.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmemdraw/fillpoly.c

Fills polygons using scan conversion.

Key functions:
- `memfillpoly`: public wrapper.
- `_memfillpolysc`: builds segment tables and runs scan conversion.
- `xscan`: primary horizontal scan-line filling with winding count.
- `yscan`: optional detail pass for thin/edge cases.
- `zsort`, `ycompare`, `xcompare`, `zcompare`: active-edge ordering helpers.
- `sdiv`, `mod`, `smuldivmod`: signed arithmetic helpers for fixed-point edge stepping.

Important behavior:
- Vertices are shifted to fixed-point form when needed.
- Uses winding mask `w` to decide filled intervals.
- Filling delegates to `memdraw` spans or points with `memopaque`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmemdraw/fillpoly.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmemdraw/hwdraw.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmemdraw/hwdraw.c

Stub hardware draw hook.

Key function:
- `hwdraw`: accepts a `Memdrawparam*`, marks it used, and returns `0`.

Meaning:
- No hardware-accelerated drawing is provided in this drawterm build; the core draw engine always falls through to software paths.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmemdraw/hwdraw.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmemdraw/iprint.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmemdraw/iprint.c

Stub internal print function.

Key function:
- `iprint`: marks its format argument used and returns `-1`.

Meaning:
- Provides a link-time placeholder for debug print calls in the library when no real kernel-style `iprint` is available.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmemdraw/iprint.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmemdraw/line.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmemdraw/line.c

Draws thick lines, endpoints, and arrowheads.

Key functions:
- `membrush`, `discend`: create and use circular endpoint masks.
- `arrowend`: computes arrowhead polygon points from line direction.
- `_memimageline`: main line rasterization routine.
- `memimageline`: public wrapper using destination clipr.
- `memlineendsize`, `memlinebbox`: bounding-box helpers for layer clipping.

Important behavior:
- Fast path for axis-aligned square-ended lines draws a rectangle.
- General thick lines are converted into polygons and filled through `_memfillpolysc`.
- Disc and arrow endpoints are drawn as masks/polygons.
- Uses `icossin2` for scaled vector direction.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmemdraw/line.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmemdraw/load.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmemdraw/load.c

Loads raw uncompressed pixel bytes into a `Memimage`.

Key function:
- `_loadmemimage`: validates rectangle and byte count, then copies scan lines into image storage.

Important behavior:
- Handles sub-byte image depths with bit insertion masks at left and right rectangle edges.
- Uses direct `memmove` for byte-aligned full-line middle regions.
- Returns the consumed byte count or `-1` on invalid input.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmemdraw/load.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmemdraw/mkcmap.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmemdraw/mkcmap.c

Generator for `cmap.c`.

Key functions:
- `mkcmap`: builds `cmap2rgb` and `rgb2cmap` tables using libdraw conversion functions.
- `main`: prints C source for a static `Memcmap`, with an Inferno include variant under `-i`.

Important behavior:
- Calls `memimageinit` before generating tables.
- Output format matches the checked-in generated `cmap.c`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmemdraw/mkcmap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmemdraw/openmemsubfont.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmemdraw/openmemsubfont.c

Loads a subfont file into memory.

Key function:
- `openmemsubfont`: opens a file, reads its image with `readmemimage`, parses font header and packed fontchar records, unpacks metrics, and returns a `Memsubfont`.

Important behavior:
- Cleans up image and packed buffer on error.
- Uses `_unpackinfo` and `allocmemsubfont`.
- The success path returns without closing the file explicitly in this source, matching the original minimal implementation pattern.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmemdraw/openmemsubfont.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmemdraw/poly.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmemdraw/poly.c

Draws polylines by drawing each segment with `memline`.

Key function:
- `mempoly`: iterates adjacent vertex pairs, applies requested end styles to only the first and last segment, and uses disc joins for internal segment ends.

Important behavior:
- Source point is tracked relative to the first vertex so texture/source alignment stays consistent across segments.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmemdraw/poly.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmemdraw/read.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmemdraw/read.c

Reads raw or compressed Plan 9 image files.

Key function:
- `readmemimage`: detects `compressed\n`, delegates to `creadmemimage` when present, otherwise parses raw image headers and loads image chunks.

Important behavior:
- Supports old ldepth and new channel-descriptor headers.
- Reads in chunks of at least 32 KiB or one scan line.
- Old image data is bit-inverted before loading.
- Uses `loadmemimage` for each chunk.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmemdraw/read.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmemdraw/string.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmemdraw/string.c

Draws and measures strings using memory subfonts.

Key functions:
- `memimagestring`: decodes UTF-8 runes, looks up `Fontchar` metrics, and draws glyph masks from `f->bits` with `memdraw`.
- `memsubfontwidth`: returns width and height for a string in a subfont.

Important behavior:
- Skips runes outside the subfont range.
- Source color point advances by glyph width to keep patterned colors aligned.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmemdraw/string.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmemdraw/subfont.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmemdraw/subfont.c

Allocates and frees `Memsubfont` structures.

Key functions:
- `allocmemsubfont`: stores metadata, fontchar array, bitmap image, and optional duplicated name.
- `freememsubfont`: frees fontchar data, backing image, and the subfont object.

Important note:
- `freememsubfont` does not free `f->name` in this file, even though allocation uses `strdup`; that is an ownership/leak behavior present in this source.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmemdraw/subfont.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmemdraw/unload.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmemdraw/unload.c

Copies raw pixels out of a `Memimage`.

Key function:
- `unloadmemimage`: validates rectangle and destination byte count, then copies each scan line to caller-provided storage.

Important behavior:
- Uses `bytesperline` for packed-image scan width.
- Does not do bit extraction beyond byte-range copying from `byteaddr`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmemdraw/unload.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmemdraw/write.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmemdraw/write.c

Writes a `Memimage` in compressed Plan 9 image format.

Key function:
- `writememimage`: unloads image data, emits a `compressed\n` header, compresses scan lines, and writes compressed blocks.

Compression behavior:
- Uses a sliding window of `NMEM` bytes and a hash table over `NMATCH` bytes.
- Emits literal dump runs and back-reference runs.
- Splits output into bounded compressed blocks with per-block `maxy` and byte count headers.

Important dependencies:
- Uses `unloadmemimage`, `chantostr`, `_compblocksize`, `write`, and Plan 9 image compression constants.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmemdraw/write.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmemlayer/Makefile -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmemlayer/Makefile

Builds `libmemlayer.a`, the memory layer/window compositing support library.

Key content:
- Includes `../Make.config`.
- Archives drawing, allocation, layer subdivision, hide/expose, line/load/unload, origin, refresh, front/rear ordering, and deletion objects.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmemlayer/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmemlayer/draw.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmemlayer/draw.c

Layer-aware wrapper for `memdraw`.

Key functions:
- `memdraw`: handles direct images, layered destinations, layered sources, clear layers, obscured layers, save areas, and same-layer moves.
- `ldrawop`: callback used by `_memlayerop` to draw either onto the screen image or a layer save image.

Important behavior:
- Layered masks are rejected as too hard.
- Converts between logical layer coordinates and screen coordinates using `Memlayer.delta`.
- Same-layer overlapping draws hide/expose affected regions and draw in backing store when possible.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmemlayer/draw.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmemlayer/lalloc.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmemlayer/lalloc.c

Allocates a new layer image on a `Memscreen`.

Key function:
- `memlalloc`: creates a `Memimage` sharing the screen’s backing data, allocates `Memlayer`, optional save image, links it into the screen stack, moves it to front, and paints initial fill.

Important behavior:
- Layers with refresh functions do not allocate save backing.
- Starts new layers behind existing ones, then pulls them to the front to handle exposure correctly.
- Uses a static replicated `paint` image for fill color drawing.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmemlayer/lalloc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmemlayer/layerop.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmemlayer/layerop.c

Subdivides operations over visible and obscured layer regions.

Key functions:
- `_layerop`: recursively splits a screen rectangle around front layers; visible portions call the callback on the screen, obscured portions call it on save backing.
- `_memlayerop`: clips to layer screen rectangle and screen clip rectangle, then handles onscreen and offscreen pieces.

Important behavior:
- Assumes input rectangles were already clipped to logical layer bounds.
- If a layer is marked clear, operations go directly to the screen image.
- Offscreen portions are routed to save backing.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmemlayer/layerop.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmemlayer/ldelete.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmemlayer/ldelete.c

Deletes or frees layers.

Key functions:
- `memldelete`: frees backing store/refresh state, pushes layer to rear, repaints exposed background if needed, unlinks screen stack, and frees image/layer.
- `memlfree`: frees structures without graphical updates.
- `_memlsetclear`: recomputes whether each layer is fully visible and unobscured within the screen clip rectangle.

Important behavior:
- Uses `memltorear` to expose layers above before final unlinking.
- `clear` is invalidated when any front layer overlaps.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmemlayer/ldelete.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmemlayer/lhide.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmemlayer/lhide.c

Moves pixel data between screen and layer save areas during obscuring/exposure.

Key functions:
- `memlhide`: copies visible screen pixels for a layer region into its save area.
- `memlexpose`: restores from save area or calls the layer refresh function.
- `lhideop`, `lexposeop`: callbacks for `_memlayerop`.

Important behavior:
- Hide is skipped if no save area exists.
- Expose on refresh-backed layers invokes `refreshfn` instead of copying from save backing.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmemlayer/lhide.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmemlayer/line.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmemlayer/line.c

Layer-aware wrapper for line drawing.

Key functions:
- `_memline`: handles direct image lines or subdivides layered destination lines by bounding box.
- `llineop`: callback that remaps coordinates for save areas and recursively draws clipped line pieces.
- `memline`: public wrapper using destination clipr.

Important behavior:
- Layered sources are unsupported for line drawing.
- Clips source constraints once before converting destination coordinates to screen space.
- Uses `memlinebbox` to choose the subdivision region because wide lines cannot be simple Cohen-Sutherland clipped.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmemlayer/line.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmemlayer/load.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmemlayer/load.c

Layer-aware wrapper for loading image bytes.

Key function:
- `memload`: selects raw or compressed load function, then loads into direct images, clear layers, save backing, or a temporary image followed by `memdraw`.

Important behavior:
- Direct-to-screen clear-layer loading requires bit alignment from layer delta.
- If save backing exists and alignment is compatible, loads backing then exposes the changed region.
- Uses a temporary image when obscured/unaligned loading cannot be done directly.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmemlayer/load.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmemlayer/lorigin.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmemlayer/lorigin.c

Moves a layer’s logical and/or screen origin.

Key functions:
- `memlorigin`: changes logical rectangle origin and screen position, preserving content and exposure behavior.
- `memlnorefresh`: no-op refresh function used for temporary shadow layers.

Important behavior:
- Brings the layer to front before moving.
- Reallocates save backing if logical coordinates change.
- Uses a temporary shadow layer at the old screen rectangle to restore background/expose other layers during movement.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmemlayer/lorigin.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmemlayer/lsetrefresh.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmemlayer/lsetrefresh.c

Switches a layer between refresh-function and backing-store modes.

Key function:
- `memlsetrefresh`: updates an existing refresh function, drops save backing when switching to refresh mode, or allocates save backing and populates it when switching to backup mode.

Important behavior:
- When moving from refresh to save-backed mode, calls the old refresh function over the full layer rectangle to initialize the new save image.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmemlayer/lsetrefresh.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmemlayer/ltofront.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmemlayer/ltofront.c

Moves layers toward the front of the screen stack.

Key functions:
- `_memltofront`: swaps a layer forward until it reaches the requested front marker, hiding overlapped front layers and optionally exposing the moved layer.
- `_memltofrontfill`: internal front move with optional exposure fill.
- `memltofront`: public single-layer move.
- `memltofrontn`: moves multiple layers while preserving caller-specified relative order.

Important behavior:
- Updates `frontmost`/`rearmost` and neighboring `front`/`rear` links during each swap.
- Recomputes clear flags after ordering changes.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmemlayer/ltofront.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmemlayer/ltorear.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmemlayer/ltorear.c

Moves layers toward the rear of the screen stack.

Key functions:
- `_memltorear`: swaps a layer backward until it reaches the requested rear marker, hiding the moved layer where overlapped and exposing layers moved above it.
- `memltorear`: public single-layer move.
- `memltorearn`: moves multiple layers while preserving relative order.

Important behavior:
- Maintains doubly linked layer stack pointers and screen `frontmost`/`rearmost`.
- Recomputes clear flags after ordering changes.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmemlayer/ltorear.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmemlayer/unload.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmemlayer/unload.c

Layer-aware wrapper for unloading image bytes.

Key function:
- `memunload`: unloads from direct images, clear layers, save backing, or a temporary composited image.

Important behavior:
- Cannot unload refresh-backed obscured layers because there is no reliable saved pixel data.
- Uses `memlhide` before reading from save backing to make sure backing store contains current screen contents.
- Falls back to drawing the layer into a temporary image when unaligned or otherwise indirect.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmemlayer/unload.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmp/Makefile -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmp/Makefile

Builds drawterm’s multiprecision integer library `libmp.a`.

Key content:
- Notes that the library is used only for `secstore` and need not be fast.
- Archives conversion, arithmetic, division, modular arithmetic, CRT, formatting, random, vector, and string-conversion objects.
- Includes more objects than this group covers, such as `mptobe`, `mpvecadd`, `strtomp`, and integer conversion files.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmp/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmp/betomp.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmp/betomp.c

Converts big-endian byte arrays to `mpint`.

Key function:
- `betomp`: optionally allocates output, skips leading zeros, sizes the target, and packs bytes into `mpdigit` limbs from most significant byte first.

Important behavior:
- Sets `top` based on requested bits before filling digits.
- Does not call `mpnorm`; leading zeros are stripped before packing.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmp/betomp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmp/crt.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmp/crt.c

Implements Chinese Remainder Theorem preprocessing and conversion.

Key functions:
- `crtpre`: copies moduli, computes cumulative products, and precomputes Garner coefficients.
- `crtprefree`: releases precomputed state.
- `crtin`: converts an integer to residues modulo each modulus.
- `crtout`: reconstructs an integer from residues using Garner’s algorithm.
- `crtresfree`: frees residue sets.

Important behavior:
- Uses `mpinvert`, `mpmul`, `mpmod`, `mpadd`, and `mpsub`.
- Based on Handbook of Applied Cryptography references in comments.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmp/crt.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmp/crttest.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmp/crttest.c

Standalone CRT test program.

Key functions:
- `testcrt`: forms a product modulus, tests residue conversion and reconstruction, and prints both values.
- `main`: generates DSA primes repeatedly, runs the CRT test, and reports elapsed seconds.

Dependencies:
- Uses `DSAprimes`, `mpconv`, and libmp arithmetic.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmp/crttest.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmp/dat.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmp/dat.h

Internal constants/macros for libmp.

Key content:
- `mpdighi`: high bit mask for an `mpdigit`.
- `DIGITS(x)`: converts bit count to limb count.
- Integer limit macros for `uint`, `int`, `uvlong`, and `vlong` conversion helpers.

Used by most libmp implementation files.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmp/dat.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmp/letomp.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmp/letomp.c

Converts little-endian byte arrays to `mpint`.

Key function:
- `letomp`: optionally allocates output, sizes it, packs bytes into low-to-high `mpdigit` limbs, and sets final `top`.

Important behavior:
- Unlike `betomp`, it preserves packing order directly from least significant byte first.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmp/letomp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmp/mpadd.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmp/mpadd.c

Implements multiprecision addition.

Key functions:
- `mpmagadd`: adds absolute values, handling zero and operand size ordering.
- `mpadd`: signed addition; delegates to magnitude subtraction when signs differ.

Important behavior:
- Uses low-level `mpvecadd`.
- Normalizes result and restores sign only when result is nonzero.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmp/mpadd.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmp/mpaux.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmp/mpaux.c

Core allocation and utility support for libmp.

Key globals:
- Static constants `mpzero`, `mpone`, and `mptwo`.
- `mpmindigits`: minimum allocation size.

Key functions:
- `mpsetminbits`, `mpnew`, `mpbits`, `mpfree`.
- `mpnorm`, `mpcopy`, `mpassign`.
- `mpsignif`: significant bit count.
- `mplowbits0`: count trailing zero bits.

Important behavior:
- `mpfree` zeroes limb data before freeing and refuses to free static constants.
- `mpbits` expands storage and zero-fills new limbs.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmp/mpaux.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmp/mpcmp.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmp/mpcmp.c

Compares multiprecision integers.

Key functions:
- `mpmagcmp`: compares magnitudes by limb count then limb values.
- `mpcmp`: signed comparison, reversing magnitude order for negative values.

Dependency:
- Uses low-level `mpveccmp`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmp/mpcmp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmp/mpdigdiv.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmp/mpdigdiv.c

Divides a two-limb dividend by a one-limb divisor to estimate a quotient digit.

Key function:
- `mpdigdiv`: returns saturated all-ones quotient if overflow/divide-by-zero would occur; otherwise uses shifting/subtraction and final low division.

Used by Knuth-style long division in `mpdiv.c`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmp/mpdigdiv.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmp/mpdiv.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmp/mpdiv.c

Implements multiprecision division using Knuth Algorithm D.

Key function:
- `mpdiv`: computes optional quotient and remainder.

Important behavior:
- Aborts on division by zero.
- Handles dividend smaller than divisor as a quick case.
- Normalizes divisor/dividend by left-shifting until divisor high bit is set.
- Estimates quotient digits with `mpdigdiv`, corrects overestimates, subtracts `v*qd`, and adds back if necessary.
- Restores quotient sign and remainder sign.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmp/mpdiv.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmp/mpeuclid.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmp/mpeuclid.c

Classic extended Euclidean algorithm.

Key function:
- `mpeuclid`: computes `d = gcd(a,b)` plus coefficients `x`, `y` such that `ax + by = d`.

Important behavior:
- Swaps inputs and output coefficient targets if needed so `a >= b`.
- Iteratively divides and rotates coefficient state.
- Copies inputs before mutation and frees temporaries at the end.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmp/mpeuclid.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmp/mpexp.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmp/mpexp.c

Exponentiation by repeated squaring, optionally modular.

Key function:
- `mpexp`: computes `b**e`, reducing modulo `m` when `m` is non-nil.

Important behavior:
- Handles output aliasing with base, exponent, or modulus by copying aliased operands.
- Skips the first high exponent bit before the main square/multiply loop.
- Periodically reduces intermediate values when larger than modulus.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmp/mpexp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmp/mpextendedgcd.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmp/mpextendedgcd.c

Binary extended GCD algorithm.

Key function:
- `mpextendedgcd`: computes `v = gcd(a,b)` and coefficients `x`, `y`.

Important behavior:
- Removes common factors of two first, tracked in `g`.
- Maintains coefficient pairs `(A,B)` and `(C,D)` while repeatedly halving even values and subtracting larger from smaller.
- Restores common power-of-two factor at the end.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmp/mpextendedgcd.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmp/mpfmt.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmp/mpfmt.c

Formats multiprecision integers as strings.

Key functions:
- `to64`, `to32`, `to16`, `to10`: base-specific conversion helpers.
- `mpfmt`: `Fmt` callback using precision as base selector.
- `mptoa`: public conversion to allocated or caller-provided string buffer.

Important behavior:
- Base 64/32 rely on libsec encoders after big-endian conversion.
- Base 10 repeatedly divides by one billion and emits zero-padded chunks.
- Default base is 16.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmp/mpfmt.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmp/mpinvert.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmp/mpinvert.c

Computes modular multiplicative inverses.

Key function:
- `mpinvert`: uses `mpextendedgcd` to find inverse of `b mod m`, aborts if gcd is not one, then normalizes result with `mpmod`.

Important behavior:
- Allocates temporary throwaway gcd/coefficient values and frees them.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmp/mpinvert.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmp/mpleft.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmp/mpleft.c

Left-shifts an `mpint`.

Key function:
- `mpleft`: computes `res = b << shift`.

Important behavior:
- Negative left shifts delegate to `mpright`.
- Handles in-place shifts by saving original top.
- Supports whole-limb and partial-limb shifts, zero-fills lower limbs, and normalizes top.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmp/mpleft.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmp/mpmod.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmp/mpmod.c

Computes positive modular remainder.

Key function:
- `mpmod`: calls `mpdiv` for remainder, then adds modulus back if the remainder is negative.

Used by modular exponentiation, CRT, inverse, and related arithmetic.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmp/mpmod.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmp/mpmul.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmp/mpmul.c

Implements multiprecision multiplication.

Key functions:
- `mpkaratsuba`: recursive Karatsuba-like vector multiplication for large operands.
- `mpvecmul`: chooses Karatsuba above threshold or quadratic digit multiply-add.
- `mpmul`: signed `mpint` multiplication with alias handling and normalization.

Important behavior:
- `KARATSUBAMIN` is 32 limbs.
- Low-level multiplication depends on `mpvecdigmuladd`, `mpvecadd`, and `mpvecsub`.
- Product sign is the product of operand signs.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmp/mpmul.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmp/mprand.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmp/mprand.c

Creates random multiprecision integers.

Key function:
- `mprand`: fills random bytes using caller-supplied generator, converts via `betomp`, masks excess high bits, normalizes top, and sets positive sign.

Important behavior:
- The generator callback has signature `void (*gen)(uchar*, int)`.
- Allocates a byte buffer sized to the digit count for the requested bit length.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmp/mprand.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmp/mpright.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmp/mpright.c

Right-shifts an `mpint`.

Key function:
- `mpright`: computes `res = b >> shift`.

Important behavior:
- Negative right shifts delegate to `mpleft`.
- Supports whole-limb and partial-limb shifts.
- Handles in-place operation and trims leading zero limbs.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmp/mpright.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmp/mpsub.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmp/mpsub.c

Implements multiprecision subtraction.

Key functions:
- `mpmagsub`: subtracts magnitudes, swapping operands and sign if needed.
- `mpsub`: signed subtraction; delegates to magnitude addition when signs differ.

Important behavior:
- Uses low-level `mpvecsub`.
- Normalizes result and adjusts sign only for nonzero differences.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmp/mpsub.c -->