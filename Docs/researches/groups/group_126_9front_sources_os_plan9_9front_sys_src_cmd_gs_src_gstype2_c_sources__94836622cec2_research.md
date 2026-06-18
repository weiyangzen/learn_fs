# Group Research: group_126_9front_sources_os_plan9_9front_sys_src_cmd_gs_src_gstype2_c_sources__94836622cec2

Scope checked against `Docs/research_subset_a.md`: `sources/os/plan9/9front` is included in subset A. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gstype2.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gstype2.c

Implements Ghostscript's Adobe Type 2 charstring interpreter on top of the Type 1 font/hinting machinery.

Key behavior:
- Initializes Type 1 hinter state for Type 2 charstrings, including CTM/font-matrix mapping, font data, grid-fitting flags, and delayed width/origin setup.
- Parses encrypted or unencrypted Type 2 charstring bytes into fixed-point operand-stack values, including 1-byte, 2-byte, 4-byte, and `shortint` encodings.
- Handles Type 2 drawing operators: moves, lines, alternating horizontal/vertical lines, cubic curves, curve-line/line-curve forms, flex operators, and `endchar`.
- Handles hints through `hstem`, `vstem`, `hstemhm`, `vstemhm`, `hintmask`, and `cntrmask`; hint masks are parsed according to the accumulated stem count.
- Implements local/global subroutine calls with Type 2 biasing, saving interpreter state across subroutine frames and freeing glyph data on `return`.
- Supports Type 2 stack/arithmetic/storage operators such as `blend`, `store`, `load`, boolean operators, arithmetic, `put/get`, `ifelse`, `roll`, and transient-array access.
- Implements Type 2 `endchar` seac compatibility for 4/5 operand accented-character charstrings.

Dependencies:
- Depends on Type 1 state, path, hinting, fixed-point arithmetic, matrix/coordinate, and font data structures from `gxfont1.h`, `gxtype1.h`, `gxhintn.h`, `gxpath.h`, and related Ghostscript headers.
- Uses `gs_type1_*` helpers for side bearings, seac handling, initialization, and finalization.
- Uses `t1_hinter__*` calls for all path construction and hint-aware geometry emission.

Research notes:
- Registry support is effectively limited to a single fake registry item backed by `WeightVector`.
- Counter masks are parsed, but the `cntrmask` action is marked `NYI`.
- The Type 2 `random` operator is present but marked `NYI`.
- Out-of-range subroutine calls are deliberately ignored for Adobe PDF Library compatibility.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gstype2.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gstype42.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gstype42.c

Implements Ghostscript Type 42/TrueType font support: font-table discovery, glyph lookup, metrics, glyph enumeration, and outline extraction/rendering helpers.

Key behavior:
- `gs_type42_font_init` validates the TrueType version, scans the table directory, records offsets for `cmap`, `glyf`, `head`, `hhea/hmtx`, `vhea/vmtx`, `loca`, and `maxp`, and installs Type 42 font procedure callbacks.
- Builds `len_glyphs` from the `loca` table and includes a slower fallback for fonts with out-of-order `loca` entries.
- Computes a replacement `FontBBox` from the `head` table when the supplied PostScript bounding box looks invalid.
- Provides default glyph-index mapping for CID/GID-like glyphs and default outline access through `loca`/`glyf`.
- Handles segmented `sfnts` glyph access by copying pieces into a contiguous glyph buffer when needed.
- Supports direct TrueType-file outline extraction through a stream-based helper.
- Parses composite glyph components, component transforms, point-matching arguments, and component metrics inheritance.
- Provides glyph-info APIs for widths, vertical vectors, composite pieces, and glyph enumeration.
- Contains legacy simple-glyph outline parsing from flags/coordinate streams, including quadratic-to-cubic conversion, though the fitted outline path delegates to `gx_ttf_outline`.

Dependencies:
- Uses TrueType constants and interpreter support from `gxttf.h`, `gxttfb.h`, `gxfont42.h`, and font-cache helpers from `gxfcache.h`.
- Uses `gsutil.c`'s `get_u32_msb` for big-endian table parsing.
- Uses path and matrix APIs for outline construction and coordinate transforms.

Research notes:
- Name glyph lookup is not implemented in the default glyph-index callback.
- `parse_component` contains an explicit fixed-matrix layout hack for transformed component translations.
- Stream-based outline extraction notes repeated per-glyph reads and suggests caching.
- `gs_type42_glyph_outline` notes that subpixel scale cannot pass through the `font_proc_glyph_outline` interface, so it applies design-grid behavior for current callers.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gstype42.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gstypes.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gstypes.h

Defines common Ghostscript library scalar and geometry types used throughout the graphics core.

Key definitions:
- `gs_id` and `gs_no_id` for internally generated unique IDs, especially for cached bitmap-like objects.
- Mutable and const string records with explicit `data` and `size`, avoiding C string limitations for binary data and substrings.
- Parameter strings with a `persistent` lifetime flag.
- Mutable and const byte-string wrappers that can either reference raw strings or byte objects for garbage-collection tracking.
- Point, integer point, log2 scale point, rectangle, integer rectangle, and closed floating range structures.

Research notes:
- Rectangle comments explicitly define `gs_rect` and `gs_int_rect` as half-open intervals.
- `gs_range_t` is explicitly closed, unlike the rectangle interval types.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gstypes.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsuid.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsuid.h

Declares Ghostscript font/object unique identifier representation and helper macros.

Key definitions:
- `gs_uid` stores either a positive 24-bit-style `UniqueID` or a negative-size XUID vector.
- `no_UniqueID` uses `max_long` to represent absence of an identifier.
- Macros test validity, UniqueID/XUID form, initialize UniqueID or XUID values, and expose XUID size/data.
- Declares `uid_equal` and `uid_copy`, implemented in `gsutil.c`.
- `uid_free` frees the XUID array when present.

Research notes:
- A valid UniqueID is constrained by `uid_is_UniqueID` to values whose high bits outside `0xffffff` are clear.
- XUID storage ownership is external until `uid_copy` duplicates it.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsuid.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsutil.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsutil.c

Implements miscellaneous Ghostscript library utilities for IDs, bit transposition, byte parsing, string matching, UID handling, and rectangle subtraction.

Key behavior:
- `gs_next_ids` reserves a contiguous block from the library context's monotonically increasing ID counter.
- `memflip8x8` transposes an 8-by-8 bit block, including fast paths for all-identical bytes and all-zero/all-one inputs.
- `get_u32_msb` parses a big-endian 32-bit unsigned value.
- `bytes_compare` compares arbitrary byte strings lexicographically with unsigned byte semantics.
- `string_match` implements wildcard matching with configurable any-substring, any-char, quote, case-insensitive, and slash-equivalence behavior.
- `uid_equal` compares UniqueIDs or XUID vectors; `uid_copy` deep-copies XUID arrays into Ghostscript memory.
- `int_rect_difference` mutates an outer rectangle to its intersection with an inner rectangle and emits up to four difference rectangles.

Dependencies:
- Uses Ghostscript memory allocation/error conventions and UID/type definitions from `gsmemory.h`, `gsuid.h`, and `gstypes.h`.
- Rectangle utility prototypes are tied to `gsrect.h`.

Research notes:
- `string_match` uses a single backtracking point for `*` and includes special Windows path slash equivalence when requested.
- `int_rect_difference` assumes rectangle interval semantics from the common type definitions.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsutil.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsutil.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsutil.h

Declares the utility functions implemented in `gsutil.c` and defines the string-match parameter and object-tag interfaces.

Key definitions:
- ID generation API: `gs_next_ids`.
- Memory/byte helpers: `memflip8x8` and `get_u32_msb`.
- String helpers: `bytes_compare`, `string_match_params`, `string_match_params_default`, and `string_match`.
- `gs_object_tag_type_t` enum for device/object tagging values such as text, image, path, unknown, and untouched.
- Object-tag accessors: `gs_current_object_tag`, `gs_set_object_tag`, and `gs_enable_object_tagging`.

Dependencies:
- Includes `gxstate.h` for `gs_state` once object tagging APIs are declared.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsutil.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gswts.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gswts.c

Implements Well Tempered Screening cell selection, screen enumeration, threshold sorting, and screen conversion.

Key behavior:
- Defines two internal cell-parameter variants: Screen H for near-axis/45-degree optimized cells and Screen J for general-angle cells with probabilistic jumps.
- Uses integer-vector arithmetic, a 3-vector GCD-like reduction, cross products, and modular normalization to find compact repeating screen bases.
- Converts requested halftone frequency/angle and device matrix into `ufast/vfast/uslow/vslow` screen-space increments.
- Chooses Screen H cell dimensions with rational approximation and split-cell probabilities.
- Chooses Screen J dimensions by scanning candidate widths/heights, scoring geometric error, jump probabilities, memory usage, and cache penalties.
- Builds enumerators that expose current points in normalized `[-1,1]` spot-function coordinates and accept sampled spot values.
- Provides `wts_sort_cell`, a simple threshold-value sort, and `wts_sort_blue`, a BlueDot-inspired sort using a Gaussian bump to reduce clustering.
- Converts completed enumerators into runtime `wts_screen_t` structures for Screen H or Screen J.
- Includes a `UNIT_TEST` mode that emits a PGM threshold image from a square-dot spot function.

Dependencies:
- Uses Ghostscript halftone state (`gsht.h`), matrix/state types, fractional constants, and WTS runtime structures from `gxwts.h`.
- Uses standard `malloc/free/qsort` rather than Ghostscript GC memory for its working structures.

Research notes:
- Landscape and mirrored coordinate systems are explicitly listed as a todo in cell-size selection.
- Blue bump generation notes that anisotropic scaling could be handled more intelligently.
- `gs_wts_free_enum` and `gs_wts_free_screen` free only the outer structure, while allocations for cell/sample buffers are owned by fields inside those structures; this is notable for lifetime review.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gswts.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gswts.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gswts.h

Declares the Well Tempered Screening public interface used by Ghostscript halftone code.

Key definitions:
- Opaque `gs_wts_screen_enum_t` and concrete `gx_wts_cell_params_t`.
- `gx_wts_cell_params_t` records screen type, cell width/height, and fast/slow UV basis increments.
- `wts_pick_cell_size` chooses screen cell parameters from halftone and device-matrix inputs.
- Screen-enumerator APIs expose the next spot-function point, accept a sampled value, sort the cell, convert to a `wts_screen_t`, and free enum/screen objects.

Dependencies:
- Expects `wts_screen_type`, `wts_screen_t`, `gs_screen_halftone`, `gs_matrix`, and `gs_point` to be available from including context and WTS/Ghostscript headers.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gswts.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsxfont.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsxfont.h

Declares opaque external-font client types for Ghostscript.

Key definitions:
- `gx_xglyph` is an opaque external-font glyph identifier, represented as `ulong`.
- `gx_no_xglyph` is the all-ones sentinel for no external glyph.
- Forward-declares `gx_xfont_procs` and `gx_xfont` as opaque structures.

Research notes:
- This header intentionally does not expose external-font procedure layout; implementation consumers include deeper headers such as `gxxfont.h`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gsxfont.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gx.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gx.h

Provides common internal Ghostscript library includes and pervasive opaque graphics-state type declarations.

Key definitions:
- Includes core error, I/O, common type, memory, and debugging headers for internal graphics code.
- Forward-declares `gs_imager_state` and `gs_state`.

Research notes:
- The comment notes that these opaque types are defined here because they are used pervasively, even though a higher-level header might be architecturally cleaner.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gx.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxacpath.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxacpath.c

Implements a clipping-path accumulation device that converts filled geometry into a clip-list representation.

Key behavior:
- Defines a `gx_device_cpath_accum` device descriptor whose important operations are open, close, fill-rectangle, and default path/trapezoid/triangle rendering fallbacks.
- `gx_cpath_accum_begin` initializes the stack/device object and opens it.
- `gx_cpath_accum_set_cbox` installs an integer clipping box for rectangle accumulation.
- `gx_cpath_accum_end` closes the device, wraps the accumulated list into a temporary clip path, sets bounding/inner/outer boxes, assigns a new ID, and transfers ownership to the destination clip path.
- `gx_cpath_accum_discard` frees accumulated rectangles after an error.
- `gx_cpath_intersect_path_slow` fills an input path through the accumulation device to intersect it with an existing clip path, temporarily forcing default logical operation.
- `accum_fill_rectangle` clips incoming rectangles, updates the aggregate bounding box, appends or merges simple ordered rectangles, and otherwise splits/merges bands to maintain an ordered non-overlapping clip list.

Dependencies:
- Integrates with Ghostscript device, path fill, clip path, logical operation, and memory systems through `gxdevice.h`, `gxpaint.h`, `gzcpath.h`, and `gzacpath.h`.
- Uses `gs_next_ids` from `gsutil.c` to mark clip-path identity changes.

Research notes:
- The file has DEBUG-only validation for clip-list ordering and linked-list consistency.
- The accumulation logic is explicitly defensive because the fill loop may emit approximately ordered, slightly overlapping rectangles.
- The single-rectangle case is optimized and later promoted to a full list with sentinel head/tail nodes when needed.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxacpath.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxalloc.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxalloc.h

Defines the internal structures, macros, and exported hooks for Ghostscript's standard reference allocator.

Key definitions:
- Documents chunk allocation layout: aligned objects and refs grow upward, strings grow downward, and string mark/relocation tables live at the top of chunks.
- Defines string mark units, relocation quanta, string-space calculations, and string free-list storage.
- Defines `chunk_t`, including object/string allocation pointers, ref object tracking, ordered chunk links, inner-chunk save/restore relationships, string free lists, and GC relocation/rescan fields.
- Provides GC structure descriptor macros for chunks and allocator state.
- Defines macros for scanning objects inside a chunk and chunks inside an allocator.
- Declares allocator chunk operations: initialize, close/open, locate, link/unlink, free, and initialize string freelists.
- Defines `gs_ref_memory_t`, a `gs_memory_t` subclass with chunk sizing, VM space, GC status, save-level state, root list, change/save lists, allocation counters, and freelists.
- Declares debug dump/find APIs under `DEBUG`.

Dependencies:
- Requires `gsmemory.h`, `gsstruct.h`, `gsalloc.h`, and `gxobj.h` definitions.
- References interpreter-level `stream` and `ref` types because allocator state tracks streams and name arrays.

Research notes:
- The comments are operationally important: inner chunks must not be freed by restore, and ref objects include dummy refs for GC relocation.
- The allocator keeps freelists last in `gs_ref_memory_t` to keep scalar offsets small.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxalloc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxalpha.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxalpha.h

Documents Ghostscript's internal alpha-channel premultiplication policy.

Key behavior:
- Establishes that alpha compositing uses premultiplication toward the native zero color: black for DeviceGray/DeviceRGB and white for DeviceCMYK.
- Records expected effects on `alphaimage`, `readimage`, color mapping, image operators, and compositing.
- Documents current interpretation that `readimage` returns device-stored premultiplied pixels, `alphaimage` expects premultiplied input, and image/colorimage treat input as opaque.

Research notes:
- The file is mostly policy documentation with one optional compile-time switch, `PREMULTIPLY_TOWARDS_WHITE`, left commented out.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxalpha.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxarith.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxarith.h

Declares integer arithmetic helpers and defines portable arithmetic/test macros used by Ghostscript graphics code.

Key definitions:
- `any_abs` works for signed numeric types.
- Declares `imod`, `igcd`, `idivmod`, and `ilog2`.
- Provides bit-fit tests for signed/unsigned integral values.
- Provides floating-point constant comparisons and range-fit tests.
- Defines `small_exact_log2` for powers of two from 1 through 128 using a compact constant expression.
- Notes a quotient/remainder trick for modulus by `2^n - 1`.

Research notes:
- Several macros are written to accommodate older compilers and no-floating-point variants referenced through `gxfarith.h`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxarith.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxband.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxband.h

Defines banding and saved-page metadata structures for Ghostscript band-list rendering.

Key definitions:
- `gx_band_params_t` carries transparency usage and optional band width, height, and buffer-space parameters.
- `gx_colors_used_t` summarizes colors seen in a band range, including an aggregate OR value and a slow-RasterOp flag.
- `gx_band_page_info_t` records command/block file names and handles, tile-cache size, block-file end position, actual band parameters, color-summary granularity, and a fixed-size color-use array.
- `PAGE_INFO_NUM_COLORS_USED` is fixed at 50 to bound page-info size while allowing reduced precision for many bands.
- Provides null initializer values and shorthand member aliases for conventional embedding.

Dependencies:
- Includes `gxclio.h` for command-list file pointer and file-name sizing definitions.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxband.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxbcache.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxbcache.c

Implements the generic bitmap-cache block allocator used by higher-level bitmap caches.

Key behavior:
- `gx_bits_cache_init` initializes an entire cache with a caller-provided first chunk and resets cache counters/rover.
- `gx_bits_cache_chunk_init` initializes a chunk and, when data is present, marks the full data range as one free block.
- `gx_bits_cache_alloc` tries to allocate a block from the current chunk, merging adjacent free blocks as it scans; when a live entry blocks allocation, it returns that entry for caller eviction.
- Splits oversize free space into an allocated block and a following free block.
- Tracks total allocated bytes, entry count, current allocation rover, and per-chunk allocated bytes.
- `gx_bits_cache_shorten` shrinks an allocated block and creates a following free block.
- `gx_bits_cache_free` marks a block free and updates counters; callers must remove any external references first.

Dependencies:
- Uses bitmap cache structures from `gxbcache.h` and Ghostscript debug/fill helpers.

Research notes:
- The allocator does not own chunk memory; callers allocate chunks and their backing data.
- Allocation failure is cooperative: the caller is expected to evict the returned live entry and retry.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxbcache.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxbcache.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxbcache.h

Defines generic bitmap-cache entry, chunk, and cache structures.

Key definitions:
- `gx_cached_bits_head` stores total block size and depth; depth zero marks a free block.
- `gx_cached_bits_common` embeds the block head plus bitmap metadata: dimensions, shift, raster, and bitmap ID.
- `align_cached_bits_mod` ensures bitmap data following a cached-bits record satisfies bitmap, pointer, and long alignment requirements.
- `gx_bits_cache_chunk` stores a linked backing chunk with data pointer, size, and allocated byte count.
- `gx_bits_cache` stores the current chunk, allocation rover, total allocated bytes, and live entry count.
- Declares cache/chunk initialization, allocation, shortening, and free APIs.

Dependencies:
- Includes `gxbitmap.h` for bitmap IDs and alignment/raster concepts.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxbcache.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxbitfmt.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxbitfmt.h

Defines bit-mask descriptors for flexible bitmap storage and transfer formats.

Key definitions:
- `gx_bitmap_format_t` is an option bitmask.
- Color alternatives include native device pixels, DeviceGray, DeviceRGB, and DeviceCMYK.
- Alpha alternatives include none, first component, and last component.
- Supported per-component depths are 1, 2, 4, 8, 12, and 16 bits, with macros to derive maximum or exact depth from an option mask.
- Packing alternatives include chunky, planar, and bit-planar forms.
- Options describe plane selection, return by copy or pointer, alignment requirements, X offset constraints, and raster constraints.
- Provides string-name macro lists for debug output.

Research notes:
- Comments note planar and especially bit-planar formats are only partially supported.
- Several options only make sense for `GB_RETURN_POINTER`; copy callers must know offsets/rasters to size buffers correctly.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxbitfmt.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxbitmap.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxbitmap.h

Defines internal bitmap, tile bitmap, and shifted strip bitmap types and alignment/raster rules.

Key definitions:
- `gx_bitmap_id` aliases `gs_bitmap_id`; `gx_no_bitmap_id` aliases the public no-ID value.
- `align_bitmap_mod` is derived from platform long alignment, and `bitmap_raster(width_bits)` rounds scanline storage up to required alignment.
- Defines mutable and const `gx_bitmap` structures using the public bitmap common layout.
- Defines mutable and const tile bitmap structures.
- Defines strip bitmap structures for halftones at arbitrary angles, with `rep_shift` and cached aggregate `shift`.
- Documents how shifted strip halftones map device `(X,Y)` into repeated/shifted bitmap coordinates.
- Provides GC structure descriptor macros for `gx_strip_bitmap`.

Research notes:
- The header emphasizes both alignment and padding requirements: code may legally access bytes past the last meaningful byte up to alignment padding.
- Shifted strip requirements restrict `rep_shift`, effective shift, and stored height to avoid ambiguous full-tile cases.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxbitmap.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxbitops.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxbitops.h

Defines internal macros for portable chunk-based bitmap bit operations.

Key definitions:
- Establishes that bitmap bits and bytes are processed in big-endian order for source data used by `copy_mono`.
- Defines chunk size, byte count, bit count, log2 size, masks, alignment, and all-bits/high-bits macros.
- Includes compiler-workaround definitions for full-width masks and high-bit masks.
- Provides `inc_ptr` for byte-wise pointer arithmetic.
- Defines mono-bit left/right/thin masks differently for big-endian and little-endian architectures.
- Externally declares mask tables used by little-endian mono copy/fill paths.

Dependencies:
- Includes `gsbitops.h` for lower-level bit operation definitions and `mono_fill_chunk_bytes` context.

Research notes:
- The macros are intentionally conservative around old compiler bugs and architectures that cannot shift a full-width long.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxbitops.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxblend.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxblend.c

Implements reference PDF 1.4/1.5 blend and transparency compositing routines for 8-bit and 16-bit channel data.

Key behavior:
- Implements 8-bit blend modes: Normal/Compatible, Multiply, Screen, Overlay, SoftLight, HardLight, ColorDodge, ColorBurn, Darken, Lighten, Difference, Exclusion, Luminosity, Color, Saturation, and Hue.
- Provides RGB luminosity/saturation helpers with luminance-preserving gamut clipping and CMYK variants that operate on complemented CMY values while treating K specially.
- Provides 16-bit `ArtPixMaxDepth` blending for a subset of blend modes.
- Uses lookup tables for SoftLight support and squared-difference terms.
- Implements alpha union helpers for plain and mask-scaled alpha.
- Implements source-over alpha compositing with optional blending in `art_pdf_composite_pixel_alpha_8`.
- Implements group uncompositing/recompositing for non-isolated transparency groups.
- Implements isolated group compositing with optional group alpha tracking.
- Implements simple, isolated, and general knockout compositing paths, including shape/alpha-mask handling.

Dependencies:
- Uses Ghostscript blend-mode enum definitions from included parameter/state headers and the public prototypes in `gxblend.h`.
- Uses 32-bit arithmetic for scaled 8-bit compositing and assumes aligned pixel buffers in several copy fast paths.

Research notes:
- This is explicitly a reference implementation, not a high-performance pixel pipeline.
- Compatible blend mode is treated as Normal.
- DeviceGray Hue/Saturation/Color/Luminosity 8-bit cases only log that they are not implemented.
- The 16-bit `BLEND_MODE_ColorBurn` case lacks a `break` before `BLEND_MODE_Darken`, so it falls through into Darken behavior.
- Some knockout/compositing comments flag missing optimization and possible clamp concerns.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxblend.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxblend.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxblend.h

Declares PDF transparency blending and compositing routines.

Key definitions:
- `ArtPixMaxDepth` is a 16-bit channel type; `ART_MAX_CHAN` limits stack blend buffers to 16 channels.
- Declares 16-bit and 8-bit blend functions over arbitrary channel counts.
- Declares alpha-union helpers for plain and mask-scaled union.
- Declares 8-bit source-over alpha compositing, group uncompositing/recompositing, isolated-group compositing, and knockout compositing variants.

Research notes:
- The API documentation states that subtractive spaces such as CMYK must be represented as complemented values before blending.
- Several functions assume a single alpha channel and 32-bit-aligned pixel buffers, with bytes beyond channel count potentially accessed by fast copies.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxblend.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxccache.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxccache.c

Implements fast character-cache lookup, external-font character lookup, cached-character imaging, and alpha-mask compression.

Key behavior:
- Computes font/matrix cache keys from character transformation matrices and log2 oversampling scales.
- Special-cases TrueType design-grid cache keys to zero matrix values because a single TrueType face cannot generate grid-fitted and non-grid-fitted outlines from the same face instance.
- `gx_lookup_fm_pair` searches the font/matrix cache by font pointer or stable UID plus matrix/design-grid state, then adds a pair on miss.
- `gx_lookup_cached_char` hashes glyph/pair and matches subpixel origin, writing mode, and depth.
- `gx_lookup_xfont_char` queries external fonts for glyph names, external glyph IDs, metrics, and creates a cache entry for externally renderable glyphs.
- `gx_image_cached_char` renders cached characters through several paths: direct xfont rendering, xfont-to-cache bitmap rendering, device `fill_mask`, `copy_alpha`, `copy_mono`, or fallback imagemask rendering.
- Handles clipping by installing a temporary clipping device when a glyph falls outside the show enumerator's inner box but intersects the outer box.
- Converts multi-bit alpha character masks to monobit masks when the target path cannot consume alpha directly.
- `compress_alpha_bits` maps 2-bit/4-bit-ish cached alpha depth to a one-bit mask using the high-order alpha bit.

Dependencies:
- Integrates with Ghostscript show enumerators, font directories, font matrix cache, external font procs, devices, memory devices, clipping paths, image masks, halftone/device colors, and logical operations.
- Uses bitmap raster/alignment helpers from `gxbitmap.h` and cache structures from font-cache headers.

Research notes:
- `cc_depth` value 3 is treated as 2-bit alpha for a 4-by-2 text-antialiasing scale case.
- `gx_image_cached_char` treats VM allocation failure for temporary masks/image enums as recoverable by returning `1`.
- Direct xfont rendering is preferred when pure color output is possible, even over multi-bit cached bitmap rendering.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxccache.c -->