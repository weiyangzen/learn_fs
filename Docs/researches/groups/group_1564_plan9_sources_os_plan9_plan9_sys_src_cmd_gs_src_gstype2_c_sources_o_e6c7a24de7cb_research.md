# Group Research: group_1564_plan9_sources_os_plan9_plan9_sys_src_cmd_gs_src_gstype2_c_sources_o_e6c7a24de7cb

Scope checked against `Docs/research_subset_a.md`: all files are under `sources/os/plan9/plan9`, which is included in subset A. Every listed file was read completely. This grouped batch is Ghostscript graphics/font/rendering infrastructure vendored in the Plan 9 source tree, not Plan 9 kernel filesystem code.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gstype2.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gstype2.c

Purpose: Implements the Adobe Type 2 charstring interpreter for Ghostscript Type 1/CFF font execution.

Key entry point:
- `gs_type2_interpret(gs_type1_state *pcis, const gs_glyph_data_t *pgd, int *ignore_pindex)` continues or starts Type 2 charstring execution, returns normal completion, errors, or positive intervention codes.

Important internals:
- `type2_sbw()` handles initial side-bearing/width setup, including nominal/default CFF width logic and backing up the interpreter pointer so the current operator re-executes.
- `type2_vstem()` parses vertical stem hint operands and updates `pcis->num_hints`.
- `check_first_operator()` detects the first real operator and delegates width setup before continuing interpretation.

Behavior:
- Decodes Type 2 operand encodings, subroutine calls, global subroutines, masks, arithmetic/stack extended operators, moves, lines, curves, flex operators, blend, and `endchar`.
- Uses the Type 1 hinter API (`t1_hinter__*`) as the output consumer for outlines and hints.
- Handles Type 2 `endchar` with 4 or 5 operands as Type 1-style `seac` accented glyph composition.
- Parses `hintmask`/`cntrmask` bytes based on accumulated hint count; `cntrmask` is explicitly parsed but not implemented.

Dependencies:
- Depends on `gxfont1.h`, `gxtype1.h`, `gxhintn.h`, fixed arithmetic, current transformation state, and Ghostscript charstring decrypt/decode macros.

Notable risks:
- `random` and counter masks are marked not implemented.
- Registry support is faked as a single registry backed by `WeightVector`.
- Some invalid subroutine calls are intentionally ignored for Acrobat compatibility.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gstype2.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gstype42.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gstype42.c

Purpose: Implements Type 42 / TrueType font support: SFNT table parsing, glyph lookup, metrics, outline extraction, and conversion to Ghostscript paths.

Key entry points:
- `gs_type42_font_init()` parses TrueType tables and initializes font procedures.
- `gs_type42_glyph_outline()` appends a glyph outline and advances the current point.
- `gs_type42_glyph_info()` and `gs_type42_glyph_info_by_gid()` return widths, vertical vectors, pieces, and default glyph info.
- `gs_type42_append()` appends a glyph outline for imaging.
- `gs_type42_get_outline_from_TT_file()` reads glyph data directly from a TrueType stream.

Important internals:
- `get_glyph_offset()` reads `loca` entries in short or long format.
- `default_get_outline()` uses `loca`/`glyf` and can make a contiguous copy if the font string provider returns segmented data.
- `parse_component()` decodes composite glyph flags, component transforms, and point matching arguments.
- `total_points()`, `parse_pieces()`, `append_simple()`, `append_component()`, and `check_component()` implement simple/composite glyph handling.
- `append_outline_fitted()` delegates actual fitted TrueType outline production to `gx_ttf_outline()` through cached font/matrix state.

Behavior:
- Accepts TrueType version `0x00010000` and `"true"`.
- Caches glyph lengths in `pfont->data.len_glyphs`, with fallback logic for out-of-order `loca` tables.
- Computes a fallback `FontBBox` from the `head` table when the PostScript `FontBBox` looks invalid.
- Converts quadratic TrueType curves to cubic Beziers for Ghostscript paths.
- Handles composite glyph point matching by doing extra passes to collect component points.

Dependencies:
- Uses `gxttf.h`, `gxttfb.h`, `gxfcache.h`, font notification release hooks, stream helpers, matrix/fixed path APIs, and `gsutil.h` big-endian parsing.

Notable risks:
- Calls `abort()` if `unitsPerEm` is zero in `gs_type42_font_init()`/`recipunitsperem()`.
- Some older outline code remains in-file, but final fitted outline path goes through `gx_ttf_outline()`.
- Composite glyph recursion depends on valid glyph data and can be expensive for deeply nested components.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gstype42.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gstypes.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gstypes.h

Purpose: Defines common Ghostscript library scalar and geometry types used broadly by graphics, font, image, and memory code.

Key definitions:
- `gs_id` and `gs_no_id` for Ghostscript-generated unique IDs.
- `gs_string`, `gs_const_string`, and `gs_param_string` for sized byte strings.
- `gs_bytestring` and `gs_const_bytestring` for strings that may point inside a GC-visible byte object.
- `gs_point`, `gs_int_point`, `gs_log2_scale_point`, `gs_rect`, `gs_int_rect`, and `gs_range_t`.

Behavior:
- String types explicitly store `data` plus `size`, avoiding reliance on NUL termination.
- Bytestring variants preserve the owning byte allocation pointer for garbage collection.
- Rectangle comments define integer/real rectangle interval conventions: rectangles are half-open, ranges are closed.

Dependencies:
- Assumes basic Ghostscript primitive types such as `byte`, `uint`, `ulong`, and `bool` are already defined.

Notable risks:
- Many downstream structures rely on `data,size` being first for GC scanning consistency.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gstypes.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsuid.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsuid.h

Purpose: Defines Ghostscript font/object UID representation for PostScript `UniqueID` and Level 2 `XUID`.

Key definitions:
- `struct gs_uid_s` stores either a positive `UniqueID` in `id`, or an `XUID` encoded as negative length plus `xvalues`.
- `no_UniqueID` is `max_long`.
- Macros classify, initialize, invalidate, access, and free UIDs.

Declared functions:
- `uid_equal()` compares UIDs; implemented in `gsutil.c`.
- `uid_copy()` deep-copies XUID arrays when necessary; implemented in `gsutil.c`.

Behavior:
- Positive IDs represent simple `UniqueID`.
- Negative IDs represent XUID arrays of length `-id`.
- Invalid UID has `id == no_UniqueID` and `xvalues == 0`.

Dependencies:
- Requires `gs_memory_t`, `client_name_t`, and `max_long` definitions from broader Ghostscript headers.

Notable risks:
- `uid_free()` blindly frees `xvalues`; callers must only use it when ownership was established appropriately.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsuid.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsutil.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsutil.c

Purpose: Provides miscellaneous Ghostscript utility implementations for IDs, bit transposition, endian reads, string matching, UID operations, and integer rectangle difference.

Key functions:
- `gs_next_ids()` reserves a block of library-wide unique IDs from `mem->gs_lib_ctx`.
- `memflip8x8()` transposes an 8x8 bit block when assembly replacement is not enabled.
- `get_u32_msb()` reads an unsigned 32-bit big-endian integer.
- `bytes_compare()` lexicographically compares unsigned byte strings.
- `string_match()` performs wildcard matching with configurable `*`, `?`, quote, case-insensitive, and slash-equivalence behavior.
- `uid_equal()` and `uid_copy()` implement UID comparison/copying for `gsuid.h`.
- `int_rect_difference()` subtracts an inner rectangle from an outer rectangle, returning up to four difference rectangles.

Behavior:
- `memflip8x8()` includes a fast path for all-zero/all-one or identical rows and then uses register-level transpose steps.
- `string_match()` uses backtracking only around the most recent wildcard.
- `int_rect_difference()` mutates `outer` to the intersection-like remaining central rectangle while filling `diffs`.

Dependencies:
- Uses Ghostscript memory allocation APIs, debug fill conventions, `gstypes.h`, `gsrect.h`, `gsuid.h`, and `gsutil.h`.

Notable risks:
- `gs_next_ids()` is a simple increment with no local locking visible here.
- `string_match()` treats a trailing quote in the pattern as a successful match path, matching historical behavior.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsutil.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsutil.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsutil.h

Purpose: Declares utility APIs implemented mainly by `gsutil.c` and defines object-tagging enums.

Key declarations:
- ID generation: `gs_next_ids()`.
- Memory/bitmap helper: `memflip8x8()`.
- Endian helper: `get_u32_msb()`.
- String helpers: `bytes_compare()`, `string_match()`, and `string_match_params`.
- Object tagging: `gs_object_tag_type_t`, `gs_current_object_tag()`, `gs_set_object_tag()`, `gs_enable_object_tagging()`.

Behavior:
- `string_match_params_default` is declared externally.
- Object tags include unknown, text, image, path, untouched, and a device-does-not-support value.

Dependencies:
- Includes `gxstate.h` after defining tag types because setter APIs take `gs_state *`.

Notable risks:
- Header declares object-tag functions not implemented in `gsutil.c`; they are provided elsewhere in Ghostscript.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsutil.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gswts.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gswts.c

Purpose: Generates Well Tempered Screening halftone cells and threshold arrays.

Key entry points:
- `wts_pick_cell_size()` chooses WTS cell parameters from a halftone screen and device matrix.
- `gs_wts_screen_enum_new()`, `gs_wts_screen_enum_currentpoint()`, and `gs_wts_screen_enum_next()` enumerate sample points and collect spot-function values.
- `wts_sort_cell()` sorts sampled thresholds uniformly.
- `wts_sort_blue()` applies BlueDot-style bump-based ordering.
- `wts_screen_from_enum()` converts an enum into runtime `wts_screen_t`.
- `gs_wts_free_enum()` and `gs_wts_free_screen()` free wrapper allocations.

Important internals:
- `gx_wts_cell_params_j_t` represents general-angle Screen J parameters, including jumps and probabilities.
- `gx_wts_cell_params_h_t` represents optimized Screen H parameters for zero/45-degree cases.
- Vector helpers (`wts_vec_*`) implement a lattice/GCD-like minimization used by Screen J cell selection.
- `wts_pick_cell_size_h()` uses simpler cell sizing optimized for near multiples of 45 degrees.
- `wts_pick_cell_size_j()` searches plausible cell widths/heights and jump vectors for general angles.
- `wts_blue_bump()` generates the bump map used by `wts_sort_blue()`.

Behavior:
- Converts halftone angle/frequency and CTM scaling into fast/slow UV vectors.
- Chooses Screen H when angle reduced modulo 45 degrees is nearly zero; otherwise Screen J.
- Stores sampled spot values as 32-bit thresholds, then rescales to `WTS_SORTED_MAX`.
- Includes `UNIT_TEST` code that can emit a PGM threshold image.

Dependencies:
- Uses `gxwts.h`, `gswts.h`, halftone state, math functions, `malloc/free/qsort`, and Ghostscript debug logging.

Notable risks:
- Uses raw `malloc/free`, not Ghostscript memory allocators.
- `gs_wts_free_enum()` frees only the enum struct, not the separately allocated `cell` buffer; similarly screen freeing only frees the top-level screen, not `samples`.
- `VERBOSE` is defined unconditionally, so debug-print code is compiled in.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gswts.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gswts.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gswts.h

Purpose: Public/internal header for Well Tempered Screening generation.

Key definitions:
- Forward declares `gs_wts_screen_enum_t`.
- Defines `gx_wts_cell_params_t` with screen type, dimensions, and fast/slow UV vectors.

Declared API:
- `wts_pick_cell_size()`
- `gs_wts_screen_enum_new()`
- `gs_wts_screen_enum_currentpoint()`
- `gs_wts_screen_enum_next()`
- `wts_sort_blue()`
- `wts_sort_cell()`
- `wts_screen_from_enum()`
- `gs_wts_free_enum()`
- `gs_wts_free_screen()`

Dependencies:
- Relies on `wts_screen_type`, `wts_screen_t`, `gs_screen_halftone`, `gs_matrix`, `gs_point`, and `floatp` definitions from included users, especially `gxwts.h`/graphics headers.

Notable risks:
- Ownership rules are only implicit; callers must know allocations come from `malloc` in `gswts.c`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gswts.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsxfont.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsxfont.h

Purpose: Defines opaque external-font client types for Ghostscript.

Key definitions:
- `gx_xglyph` is an opaque external glyph identifier.
- `gx_no_xglyph` is the all-bits-set sentinel.
- Forward declarations for `gx_xfont_procs` and `gx_xfont`.

Behavior:
- Keeps external font implementation details opaque to core users.
- Used by character cache code to store and render platform/external font glyphs.

Dependencies:
- Requires `ulong`.

Notable risks:
- None local; this is a small type boundary header.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsxfont.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gx.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gx.h

Purpose: Common internal Ghostscript include wrapper.

Contents:
- Includes core internal headers: `stdio_.h`, `gserror.h`, `gsio.h`, `gstypes.h`, `gsmemory.h`, and `gdebug.h`.
- Forward-declares opaque `gs_imager_state` and `gs_state`.

Behavior:
- Centralizes pervasive internal definitions so lower-level files can include one stable core header.
- Avoids exposing graphics-state structure definitions at this level.

Dependencies:
- Pulls in broad Ghostscript base types and debug/error/memory APIs.

Notable risks:
- Because widely included, any changes here have large compile-time impact.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gx.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxacpath.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxacpath.c

Purpose: Implements a device-backed accumulator for clipping paths by collecting filled rectangles into a `gx_clip_list`.

Key entry points:
- `gx_cpath_accum_begin()` initializes an accumulator device.
- `gx_cpath_accum_set_cbox()` constrains accumulation to a clipping box.
- `gx_cpath_accum_end()` converts the accumulated rectangle list into a `gx_clip_path`.
- `gx_cpath_accum_discard()` frees accumulated list state after errors.
- `gx_cpath_intersect_path_slow()` intersects an existing clipping path with a path by rendering through the accumulator.

Important internals:
- `gs_cpath_accum_device` is a mostly-null device descriptor with `fill_rectangle` implemented.
- `accum_open()` initializes an empty list, bbox, and default infinite clip box.
- `accum_close()` finalizes list extrema and validates under debug.
- `accum_alloc_rect()` manages transition from single-rectangle storage to linked-list storage.
- `accum_fill_rectangle()` clips, merges, splits, and inserts rectangles into sorted non-overlapping bands.

Behavior:
- Maintains bounding box and list ordering by y-band then x.
- Optimizes for first rectangle and simple y-adjacent merging.
- Handles overlap by splitting existing and new bands, merging horizontal spans when possible.
- `gx_cpath_intersect_path_slow()` temporarily resets logical operation to default for fill-only clipping accumulation.

Dependencies:
- Uses Ghostscript device API, clipping path/list structures, fill path machinery, fixed/int conversion, device colors, and unique IDs from `gs_next_ids()`.

Notable risks:
- Rectangle-list manipulation is intricate and mutation-heavy; invariants are checked only in debug builds.
- Uses `goto top` for remaining band processing after splits.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxacpath.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxalloc.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxalloc.h

Purpose: Defines internal structures and macros for Ghostscript’s standard reference-aware allocator and chunk management.

Key definitions:
- `chunk_t` describes a memory chunk with bottom-up aligned object allocation and top-down string allocation.
- String GC constants and macros: `string_data_quantum`, `string_space_quantum`, `string_chunk_space()`, `STRING_FREELIST_SPACE()`.
- Chunk scanning macros: `SCAN_CHUNK_OBJECTS`, `DO_ALL`, `END_OBJECTS_SCAN`.
- Pointer-location macros and `chunk_locator_t`.
- `gs_ref_memory_t` extends `gs_memory_t` with chunk chain, freelists, save/restore state, GC roots, allocation accounting, stream/name pointers, and debug counters.
- Debug dump controls under `DEBUG`.

Declared functions:
- Chunk lifecycle: `alloc_init_chunk()`, `alloc_close_chunk()`, `alloc_open_chunk()`, `alloc_link_chunk()`, `alloc_unlink_chunk()`, `alloc_free_chunk()`.
- String free-list init: `alloc_init_free_strings()`.
- Pointer lookup: `chunk_locate_ptr()`.
- Debug printing/dumping APIs.

Behavior:
- Chunks may be nested for PostScript save/restore.
- Refs are grouped into `st_refs` objects with bounds to aid GC relocation scanning.
- String metadata includes mark and relocation tables stored near the top of chunks.
- Small and large free blocks are tracked with multiple freelists.

Dependencies:
- Requires `gsmemory.h`, `gsstruct.h`, `gsalloc.h`, `gxobj.h`, architecture alignment constants, and interpreter `ref`/`stream` forward declarations.

Notable risks:
- This header exposes allocator internals to save/restore and GC code; layout changes affect memory management correctness.
- Many macros assume object-header layout and alignment invariants.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxalloc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxalpha.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxalpha.h

Purpose: Documents and centralizes Ghostscript internal alpha-channel premultiplication policy.

Contents:
- Explains Porter-Duff-style premultiplication for alpha.
- States Ghostscript’s chosen convention: premultiply toward the native zero color value, usually black for DeviceGray/RGB and white for DeviceCMYK.
- Lists affected areas such as `alphaimage`, `readimage`, color mapping, images, and compositing code.
- Provides a disabled `PREMULTIPLY_TOWARDS_WHITE` preprocessor option.

Behavior:
- No active functions or data structures; this is a policy/configuration header.

Dependencies:
- None beyond normal include guard context.

Notable risks:
- Boundary inconsistency is acknowledged in comments because device color-space conventions differ.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxalpha.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxarith.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxarith.h

Purpose: Defines arithmetic helpers and declares integer arithmetic utilities.

Key definitions:
- `any_abs(x)` generic signed absolute macro.
- `fits_in_bits()` and `fits_in_ubits()` integer bit-fit tests.
- Floating comparison/fit macros: `is_fzero`, `is_fzero2`, `is_fneg`, `is_fge1`, `f_fits_in_bits`, `f_fits_in_ubits`.
- `small_exact_log2()` lookup macro for powers of two up to 128.

Declared functions:
- `imod()`, `igcd()`, `idivmod()`, and `ilog2()`.

Behavior:
- `imod()` promises non-negative modulo independent of implementation-defined negative `%` behavior.
- Comments document a quotient/remainder optimization for values modulo `2^n - 1`.

Dependencies:
- Assumes Ghostscript scalar typedefs and architecture constants are available.

Notable risks:
- Several macros evaluate expressions in arithmetic contexts and may overflow if called outside expected ranges.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxarith.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxband.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxband.h

Purpose: Defines band-list rendering parameters and saved-page bookkeeping for Ghostscript band processing.

Key definitions:
- `gx_band_params_t` stores transparency usage and optional band width, height, and buffer space.
- `gx_colors_used_t` tracks ORed color usage and slow raster-op usage per band group.
- `PAGE_INFO_NUM_COLORS_USED` is fixed at 50.
- `gx_band_page_info_t` stores command/block file names and handles, tile cache size, block file end position, actual band parameters, scan-line grouping for color use, and color-use entries.
- Convenience macros expose common `page_info` fields.

Behavior:
- Color-use precision is reduced when pages have more bands than 50 tracking entries.
- `PAGE_INFO_NULL_VALUES` provides initializer defaults.

Dependencies:
- Includes `gxclio.h` for command-list file pointer types and platform file-name sizes.

Notable risks:
- Fixed-size color-use array trades precision for bounded page-info size.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxband.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxbcache.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxbcache.c

Purpose: Implements generic bitmap cache chunk and entry allocation for Ghostscript cached bitmap data.

Key functions:
- `gx_bits_cache_init()` initializes a cache with a caller-provided first chunk.
- `gx_bits_cache_chunk_init()` initializes a chunk and marks its data as one free block.
- `gx_bits_cache_alloc()` attempts to allocate an entry, merging adjacent free blocks and asking the caller to evict occupied entries when needed.
- `gx_bits_cache_shorten()` shrinks an allocated entry and creates a free block from the tail.
- `gx_bits_cache_free()` marks an entry free and updates accounting.

Behavior:
- Cache chunks contain variable-sized blocks headed by `gx_cached_bits_head`.
- Allocation uses `bc->cnext` as a rover in the current chunk.
- If insufficient contiguous free space is found because a live entry is encountered, the function returns `-1` and points `*pcbh` at an entry the caller should free.
- Uses debug fill patterns for allocated/deleted blocks.

Dependencies:
- Depends on `gxbcache.h`, Ghostscript memory debug fill API, and debug logging.

Notable risks:
- `lsize` is cast down to `uint` through macros; callers must keep sizes representable.
- Free-block coalescing happens opportunistically during allocation, not globally.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxbcache.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxbcache.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxbcache.h

Purpose: Defines generic bitmap-cache structures used by higher-level caches such as character or tile caches.

Key definitions:
- `gx_cached_bits_head` stores block size and depth; `depth == 0` means free.
- `gx_cached_bits_common` embeds bitmap metadata: width, height, shift, raster, and bitmap ID.
- `align_cached_bits_mod` ensures cached bitmap payload alignment.
- `gx_bits_cache_chunk` stores chunk linkage, byte data, total size, and allocated bytes.
- `gx_bits_cache` stores current chunk, allocation rover, total bytes, and entry count.

Declared API:
- `gx_bits_cache_init()`
- `gx_bits_cache_chunk_init()`
- `gx_bits_cache_alloc()`
- `gx_bits_cache_shorten()`
- `gx_bits_cache_free()`

Dependencies:
- Includes `gxbitmap.h` for bitmap/raster ID and alignment definitions.

Notable risks:
- Header is intentionally key-agnostic; users must maintain hash/list structures and remove entries before freeing blocks.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxbcache.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxbitfmt.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxbitfmt.h

Purpose: Defines bitmask flags describing bitmap storage/transfer formats for procedures such as `get_bits_rectangle`.

Key definitions:
- `gx_bitmap_format_t` is a bitmask type.
- Color alternatives: native, Gray, RGB, CMYK.
- Alpha alternatives: none, first component, last component.
- Component depths: 1, 2, 4, 8, 12, 16.
- Packing alternatives: chunky, planar, bit-planar.
- Plane selection, return method, alignment, x-offset, and raster flags.
- Debug names aggregate via `GX_BITMAP_FORMAT_NAMES`.

Behavior:
- `GB_OPTIONS_MAX_DEPTH()` and `GB_OPTIONS_DEPTH()` extract depth information from masks.
- `GB_RETURN_POINTER` makes alignment, offset, and raster looseness meaningful; `GB_RETURN_COPY` generally requires caller-specified layout.

Dependencies:
- Requires `ulong`.

Notable risks:
- Some formats are explicitly only partially supported, especially planar and bit-planar packing.
- Bit assignments consume up to bit 30, so extension space in this mask is limited.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxbitfmt.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxbitmap.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxbitmap.h

Purpose: Defines Ghostscript internal bitmap, tile bitmap, and shifted-strip bitmap structures and alignment/raster rules.

Key definitions:
- `gx_bitmap_id` aliases `gs_bitmap_id`; `gx_no_bitmap_id` aliases `gs_no_bitmap_id`.
- `align_bitmap_mod` derives required scan-line alignment from long alignment.
- `bitmap_raster(width_bits)` rounds bit width up to aligned byte raster.
- `gx_bitmap`, `gx_const_bitmap`, `gx_tile_bitmap`, `gx_const_tile_bitmap`.
- `gx_strip_bitmap` and `gx_const_strip_bitmap` add `rep_shift` and `shift` for shifted halftone strips.
- Structure descriptor macro `public_st_gx_strip_bitmap()`.

Behavior:
- Documents that scan lines must start aligned and must have padding bytes available for chunk-based operations.
- Describes shifted strip halftones: each repeated strip may shift horizontally as Y advances.
- `shift` is an accelerator derived from repeated strip shift and stored bitmap height.

Dependencies:
- Includes `gstypes.h` and `gsbitmap.h`.

Notable risks:
- Many rendering routines assume padding bytes are addressable even beyond logical pixel data.
- Strip bitmap invariants must hold: `rep_shift < rep_width` and consistent derived `shift`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxbitmap.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxbitops.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxbitops.h

Purpose: Defines internal macros for efficient bitmap bit/chunk operations.

Key definitions:
- Chunk size/bit/alignment helpers: `cbytes`, `clog2_bytes`, `cbits`, `clog2_bits`, `cbit_mask`, `calign_bytes`, `calign_bit_mask`.
- Full-mask and high-bit mask helpers: `cmask`, `chi_bits`.
- `arch_cant_shift_full_chunk` for platforms unable to shift full-width longs.
- `inc_ptr()` byte-wise pointer arithmetic.
- Monobit mask setup macros: `set_mono_left_mask`, `set_mono_thin_mask`, `set_mono_right_mask`.
- `mono_copy_chunk` is `uint` on big-endian systems and `bits16` on little-endian systems.

Behavior:
- Assumes bits inside bytes and bytes in scanlines are stored big-endian for mono copy source data.
- Uses lookup tables on little-endian systems (`mono_copy_masks`, `mono_fill_masks`) and arithmetic masks on big-endian systems.
- Contains compiler-workaround macro definitions for older C compilers.

Dependencies:
- Includes `gsbitops.h` and relies on architecture macros.

Notable risks:
- Heavy macro use is sensitive to type width and shift semantics.
- Some macros only accept constrained argument ranges, as documented.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxbitops.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxblend.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxblend.c

Purpose: Implements PDF transparency blend and compositing functions for 8-bit and 16-bit channels.

Key entry points:
- `art_blend_pixel_8()` computes separable and selected non-separable blend modes for 8-bit pixels.
- `art_blend_pixel()` computes similar blend modes for 16-bit `ArtPixMaxDepth`.
- `art_pdf_union_8()` and `art_pdf_union_mul_8()` combine alpha values.
- `art_pdf_composite_pixel_alpha_8()` composites source-over with optional blend mode.
- `art_pdf_uncomposite_group_8()`, `art_pdf_recomposite_group_8()`, and `art_pdf_composite_group_8()` handle group uncompositing/recompositing.
- `art_pdf_composite_knockout_simple_8()`, `art_pdf_composite_knockout_isolated_8()`, and `art_pdf_composite_knockout_8()` handle knockout transparency cases.

Important internals:
- `art_blend_luminosity_rgb_8()` and CMYK variant implement luminosity behavior with clipping back into gamut.
- `art_blend_saturation_rgb_8()` and CMYK variant implement saturation behavior.
- Lookup tables `art_blend_sq_diff_8` and `art_blend_soft_light_8` support SoftLight.

Behavior:
- Implements Normal, Compatible-as-Normal, Multiply, Screen, Overlay, SoftLight for 8-bit, HardLight, ColorDodge, ColorBurn, Darken, Lighten, Difference, Exclusion, Luminosity, Color, Saturation, and Hue.
- For CMYK non-separable modes, comments state components are already complemented.
- DeviceGray Hue/Saturation/Color/Luminosity emit debug messages and do not implement meaningful transforms.
- Group operations use PDF alpha union math and 8-bit fixed-style rounding.

Dependencies:
- Depends on `gxblend.h`, `gstparam.h`, Ghostscript debug printing, `bits32`, and blend-mode enums.

Notable risks:
- In `art_blend_pixel()` the 16-bit `BLEND_MODE_ColorBurn` case falls through into `BLEND_MODE_Darken` because there is no `break`.
- Some 32-bit copy idioms rely on caller-guaranteed padding/alignment from `gxblend.h`.
- The disabled `art_pdf_composite_pixel_knockout_8()` block contains unfinished/reference code and is not compiled.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxblend.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxblend.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxblend.h

Purpose: Declares PDF transparency blending and compositing APIs implemented in `gxblend.c`.

Key definitions:
- `ArtPixMaxDepth` is `bits16`.
- `ART_MAX_CHAN` is 16.

Declared API:
- Pixel blending: `art_blend_pixel()`, `art_blend_pixel_8()`.
- Alpha union: `art_pdf_union_8()`, `art_pdf_union_mul_8()`.
- Basic compositing: `art_pdf_composite_pixel_alpha_8()`.
- Group operations: `art_pdf_uncomposite_group_8()`, `art_pdf_recomposite_group_8()`, `art_pdf_composite_group_8()`.
- Knockout operations: `art_pdf_composite_knockout_simple_8()`, `art_pdf_composite_knockout_isolated_8()`, `art_pdf_composite_knockout_8()`.

Behavior:
- Documents that implementations are reference-oriented rather than high performance.
- States that subtractive color spaces such as CMYK should pass complemented pixel values.
- Requires pixel buffers to be aligned/padded enough that 32-bit copying may access bytes through `[(n_chan + 3) & -4]`.

Dependencies:
- Requires `bits16`, `byte`, and `gs_blend_mode_t`.

Notable risks:
- API leaves Compatible blend mode semantically unresolved in comments.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxblend.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxccache.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxccache.c

Purpose: Implements fast-path character cache lookup and rendering routines for Ghostscript.

Key entry points:
- `gx_compute_char_matrix()` applies log2 oversampling scale to a character matrix.
- `gx_compute_ccache_key()` computes the font/matrix cache key, with special handling for design-grid TrueType.
- `gx_lookup_fm_pair()` finds or adds a cached font/matrix pair.
- `gx_lookup_cached_char()` finds a cached glyph bitmap by glyph, pair, subpixel origin, writing mode, and depth.
- `gx_lookup_xfont_char()` maps a glyph to an external font glyph and creates a cache entry.
- `gx_image_cached_char()` renders a cached character through fill-mask, copy-alpha, copy-mono, xfont, or imagemask paths.

Important internals:
- `scale_log2_1` is the default 1x scale.
- `compress_alpha_bits()` converts 2/4-bit alpha cached masks into 1-bit masks using high-order alpha bits.

Behavior:
- TrueType design-grid cache keys may be zero matrices because the TT interpreter cannot share one face instance for grid-fitted and non-grid-fitted outlines.
- Font/matrix lookup can use UID instead of font pointer for base fonts with valid UIDs.
- External xfont rendering is preferred when available and color conditions permit.
- If cached glyph bounds exceed the inner clip box, it wraps the target in a clipping device unless completely outside.
- For pure colors, tries `fill_mask`, `copy_alpha`, then `copy_mono`; otherwise falls back to imagemask rendering.

Dependencies:
- Uses font directory caches (`gxfcache.h`), xfont APIs, path/current point state, device procedures, memory devices, clipping, image enumeration, and bitmap raster helpers.

Notable risks:
- `compress_alpha_bits()` allocates temporary masks from non-GC memory and callers must free them on fallback paths.
- Several render paths return `1` as recoverable failure/VMerror-style fallback rather than hard error.
- Cache key and xfont behavior depend on subtle font type, UID, encoding, and writing-mode conditions.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxccache.c -->