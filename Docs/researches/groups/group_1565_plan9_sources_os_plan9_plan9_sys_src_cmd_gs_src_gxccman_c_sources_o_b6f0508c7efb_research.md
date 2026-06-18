# Group Research: group_1565_plan9_sources_os_plan9_plan9_sys_src_cmd_gs_src_gxccman_c_sources_o_b6f0508c7efb

Scope checked against `Docs/research_subset_a.md`: `sources/os/plan9/plan9` is included in subset A. All listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxccman.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxccman.c

Character cache manager for Ghostscript. It allocates and initializes font-directory cache state, including font/matrix pair storage, an open-addressed cached-character hash table, and bits-cache chunks (`gx_char_cache_alloc`, `gx_char_cache_init`). It also owns purge paths for selected cached characters, whole font/matrix pairs, xfont-only entries, and font-wide invalidation.

The file’s core data flow is: allocate or locate a `cached_fm_pair`, optionally attach native xfont/TrueType helper state, allocate bitmap storage for a glyph, render into memory/alpha devices, crop or oversampling-compress the bits, then link the result into the hash table. `gx_alloc_char_bits` enforces cache size limits, initializes mono or alpha-buffer memory devices, and handles xfont-only entries. `gx_add_char_bits` scans the bitmap bounding box, removes whitespace, compresses oversampled bits, adjusts offsets, shortens the backing bits-cache block, and assigns a bitmap id.

Cache replacement is chunk-based. `alloc_char` adds chunks until the byte budget is reached, then cycles existing chunks and frees old cached characters as needed. `hash_remove_cached_char` preserves open-addressed lookup correctness by relocating later entries after deletion. Important dependencies are `gxfcache.h` for cached structures/macros, `gxdevmem.h` for memory devices, `gxxfont.h` for xfont integration, and TrueType helper state for Type 42/CID TrueType fonts.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxccman.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxcdevn.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxcdevn.h

Internal DeviceN color-space support header. It defines `gs_device_n_map`, a reference-counted one-entry cache for DeviceN tint conversion. The structure stores a tint-transform callback, callback data, a validity flag, the last input tint array, and cached concrete component values sized by `GX_DEVICE_COLOR_MAX_COMPONENTS`.

The header exports the GC descriptor macro `private_st_device_n_map`, allocation API `alloc_device_n_map`, and `using_alt_color_space`, which tells callers whether rendering is using the alternate color space. It depends on `gsrefct.h` for `rc_header` and `gxcindex.h` for the maximum device component count. This is a narrow shared interface used by DeviceN color implementation code rather than a standalone algorithm.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxcdevn.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxchar.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxchar.c

Default Ghostscript text/show implementation. It builds the `gs_show_enum` state machine used for show, stringwidth, charpath, cshow/kshow-style intervention, cached glyph display, xfont fallback, and BuildChar/BuildGlyph rendering. `gx_default_text_begin` initializes the enumerator, derives charpath behavior from `gs_text_params_t`, sets cache eligibility, and creates a null device for stringwidth. `gx_show_text_process` dispatches through continuation procedures.

The main loop is `show_proceed`. It fetches characters/glyphs, handles descendant font changes, computes raster parameters, looks up font/matrix pairs, searches the cached glyph/xfont cache, and either images a cached glyph or calls the font’s `build_char` procedure under a saved graphics state. `show_update` finalizes width/cached-char state after BuildChar, installs successful cache entries with `gx_add_cached_char`, handles charpath and image-from-cache behavior, and restores state. `show_move` applies widthshow/ashow/kshow width adjustments and advances the current point.

The cache setup path computes oversampling based on device alpha bits, font paint type, pure-color rendering, matrix shape, and glyph size. `set_cache_device` validates cacheability, transforms setcachedevice boxes, allocates cache devices, sets clipping, adjusts CTM/origin, and marks `pgs->in_cachedevice`. The file is tightly coupled to `gxchar.h`, `gxfcache.h`, font procs, path/clip state, and memory devices. Notable edge cases are CID encrypted width compensation, WMode 1 origin adjustment, retry after bad FontBBox, and conservative avoidance of skewed/unsupported cache cases.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxchar.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxchar.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxchar.h

Internal text/show and cached-character interface. It forward-declares opaque cached character, cached font/matrix pair, font, text enumerator, memory device, and null device types. It defines `show_width_status`, distinguishing unset width, setcachedevice caching, setcharwidth non-cache, xfont width-only, and retry states.

The central structure is `gs_show_enum_s`, which subclasses `gs_text_enum_common` and stores show-time graphics state, charpath mode, cache eligibility, clip quick-check boxes, transformed font translation, current font encoding proc, FAPI oversampling hints, cache/null devices, current width/origin, cached character under construction, and continuation procedure. The header exports the public structure descriptor macro and key routines implemented in `gxchar.c`, `gxccman.c`, and cache lookup/image modules: current character access, char bitmap allocation/free/add, cached/xfont lookup, cached character imaging, oversampling computation, width setting, text-state restore, and pdfwrite stringwidth helper.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxchar.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxchrout.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxchrout.c

Small shared outline-character utility. `gs_char_flatness` derives a rendering flatness for outline fonts from the current CTM and a font default scale. It chooses the smallest meaningful CTM component, including off-diagonal terms for rotated/skewed matrices, rescales by `0.001 / default_scale`, clamps to the imager state’s flatness, and forces exact curve flattening for tiny characters by returning zero when the effective scale is below `0.2`.

This routine is used to make character outline rasterization quality less dependent on the current graphics-state flatness while preserving an upper bound. It depends on matrix-shape helpers from `gxfarith.h` and imager state definitions from `gxistate.h`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxchrout.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxchrout.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxchrout.h

Header for shared outline character rendering helpers. It forward-declares `gs_imager_state` and declares `gs_char_flatness(const gs_imager_state *, floatp)`. The comments document the key contract: the returned flatness may be smaller than the imager state flatness, and the caller supplies the font’s default scaling, typically `0.001` for Type 1 fonts or `1.0` for TrueType fonts.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxchrout.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxcht.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxcht.c

Color halftone rendering implementation. It defines the `gx_dc_type_ht_colored` device-color type, including save, halftone lookup, load, fill-rectangle, equality, serialization, deserialization, and nonzero-component reporting. Serialization writes only changed base/level/alpha fields relative to a saved color, uses compact masks for 1-bit/component devices, and omits the halftone itself because it lives in imager state.

`gx_dc_ht_colored_fill_rectangle` is the main renderer. It clips large rectangles, treats colored halftones as opaque textures for RasterOp, selects per-plane caches, prepares color lookup tables, and either creates a reusable LCM-sized tile or renders chunks that fit the stack tile buffer. It supports direct `copy_color`, `strip_tile_rectangle`, and `strip_copy_rop` paths.

The second half builds per-plane color pairs and halftone bitmaps. There are optimized paths for up to four planes, a special 1-bit CMYK case, and a separable-color assumption for more than four planes. Tile cursor logic walks shifted halftone bitmaps row by row. `set_color_ht_le_4` expands plane bits into packed color indices for 4/8/16/24/32-bit targets, while `set_color_ht_gt_4` ORs separable component color indices. Important limitations are explicitly noted in comments for some DeviceN/>4-plane color mapping and alpha handling.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxcht.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxcid.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxcid.h

Common CID/CMap data header. It defines `gs_cid_system_info_t` with `Registry`, `Ordering`, and `Supplement`, plus public GC descriptor macros for individual values and arrays. It also documents and declares null-CIDSystemInfo handling: a null value is represented by empty Registry/Ordering strings and Supplement zero, with helpers `cid_system_info_set_null` and `cid_system_info_is_null`.

This file is a small shared type contract used by CID-keyed font and CMap code. It depends on `gsstype.h` for `gs_const_string`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxcid.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxcie.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxcie.h

Internal CIE color implementation header. It declares CIE color-space procedures used by the color-space structures: initialization, restriction, installation, concretization/remapping, and concrete-space resolution for CIEA, CIEABC, CIEDEF, and CIEDEFG forms. It also exposes a CIE-to-XYZ imager-state helper used by pdfwrite.

The key macro is `CIE_CHECK_RENDERING`, which handles the no-rendering case by returning black and ensures joint CIE caches are completed before remapping. The header also declares remap finish implementations, common CIE GC descriptors, default initialization, common cache loading/completion, indirect installation, and construction of common CIE color-space storage. This is a declaration hub; implementations are in `gscie.c`, `gsciemap.c`, and `gscscie.c`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxcie.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxcindex.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxcindex.h

Device color-index type and scan-line accumulation macros. It sets `GX_DEVICE_COLOR_MAX_COMPONENTS` to 16 and defines `gx_color_index_data`/`gx_color_index`, normally as an unsigned long-like opaque pixel value but with disabled pointer/struct test modes for portability analysis. `gx_no_color_index` is the transparent/undefined color sentinel.

The header also provides macros for accumulating packed scan lines at 1, 2, 4, or byte-multiple bits per pixel using `sample_store` helpers. `DECLARE_LINE_ACCUM`, `LINE_ACCUM`, `LINE_ACCUM_SKIP`, and `LINE_ACCUM_STORE` are for building a line buffer; the `_COPY` variants additionally copy accumulated spans to a device with `copy_color`. These macros are used by image/color rendering code that must pack device-specific color indices efficiently.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxcindex.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxclbits.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxclbits.c

Command-list bitmap, transfer-map, and tile-cache writer support. `clist_bitmap_bytes` implements the command-list padding policy: compressed bitmaps keep full raster padding, narrow/one-line/spread bitmaps drop padding, and other uncompressed bitmaps drop padding only on the last scan line. `cmd_put_bits` allocates command buffer space, optionally tries CCITTFax or RLE compression, shortens commands when compression or padding choices reduce size, and returns the selected compression code or a limit error.

The tile-cache section hashes bitmap ids into the writer’s tile table, deletes cache entries with conservative dependent-entry deletion, and allocates tile slots from a bits cache. `clist_new_tile_params` chooses replicated tile dimensions under size/count constraints. `clist_change_tile` emits tile parameter and tile-bit commands per band, marking which bands know a cached tile. `clist_change_bits` does the analogous path for copy operations and can promote frequently reused character bitmaps to all bands, though the current threshold disables that by default.

The file is tightly bound to the bytecode and band-state definitions in `gxcldev.h`, plus compression streams from `scfx.h` and `srlx.h`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxclbits.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxcldev.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxcldev.h

Internal command-list protocol and writer/reader support header. It defines bitmap compression modes, the command bytecode enum, command operand conventions, rectangle encodings, tile-depth encoding, bitmap padding policy, block-file entries, and per-band `gx_clist_state_s`.

The per-band state tracks current colors, saved device color, tile index/id/phase/colors, previous rectangle, logical operation, clipping, alpha-copy mode, known-state flags, command list, rendering cost, and colors used. The `known` flags integrate with path flags and include tile-parameter and begin-image knowledge. `cbuf_size` is fixed at 4096 and constrains bitmap/image command splitting.

The header declares clist driver procedures for rectangles, bitmap copy, masks/images, compositors, and band readback. It also exposes writer primitives for command allocation, command shortening, buffer flushing, variable-length integer encoding, color emission, tile colors/phase, logical operation, clipping, rectangle emission, bitmap emission, color maps, tile changes, halftone/color mapping, and band playback. The `FOR_RECTS`, `TRY_RECT`, and `HANDLE_RECT` macros encode per-band iteration plus two-stage VMerror recovery, making idempotent command emission a key invariant for callers.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxcldev.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxclfile.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxclfile.c

Filesystem-backed implementation of the command-list I/O interface. `clist_fopen` opens an existing file or creates a scratch file when the name buffer is empty; reading with an empty name is rejected. `clist_fclose` closes and optionally unlinks the file, while `clist_unlink` wraps `unlink`.

The write/read API is thin stdio: `clist_space_available` reports the requested amount, `clist_fwrite_chars` writes bytes with `fwrite`, and `clist_fread_chars` uses an optimized fall-through `getc` path for reads of 1 to 8 bytes to avoid small `fread` overhead. Status and positioning wrappers expose memory-warning no-op behavior, `ferror`, `ftell`, rewind, truncating rewind via `freopen`, and `fseek`. This is the portable file-system counterpart to any RAM-backed clist I/O implementation.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxclfile.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxclimag.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxclimag.c

High-level mask, image, compositor, halftone, and color-mapping command-list writer. `clist_fill_mask` converts eligible masks into cached bitmap/tile commands, falling back to the default fill-mask path for complex clipping, uncached ids, non-default RasterOp, disabled alpha copy, or non-pure alpha colors. It updates per-band lop, clipping, drawing color, and tile state before emitting copy commands.

The high-level image path uses `clist_image_enum`. `clist_begin_typed_image` accepts only supported image types/color spaces/depths/matrices, rejects nested images and unsupported alpha/CIE/complex cases, serializes a begin-image command, computes conservative colors-used and Y band bounds, and clears relevant known-state flags. `clist_image_plane_data` maps source rows to affected bands, computes per-band image subrectangles, emits begin-image state/preamble as needed, and writes image data in chunks constrained by the command buffer. `clist_image_end_image` emits EOD markers to bands with active begin-image state and handles retryable memory errors.

Utilities serialize compositors, data_x changes, full halftones split into segments when needed, transfer/black-generation/undercolor maps, and image-band bounding boxes for rectangular or general transforms. `check_rect_for_trivial_clip` allows optimized paths when clipping is absent, contains the rectangle, or is rectangular and intersecting. This file is one of the main producers of the command bytecode defined in `gxcldev.h`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxclimag.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxclio.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxclio.h

Command-list I/O abstraction header. It defines `clist_file_ptr` as an opaque pointer and documents the two interchangeable implementations: external filesystem storage and embedded RAM-backed storage, selected at compile/link time.

The API covers opening/creating scratch files, closing with optional deletion, unlinking, space-availability queries, byte writes, byte reads, low-memory warning thresholds, error-code status, current position, rewind with optional data discard, and seek. The interface deliberately passes file names to rewind/seek so implementations that must close/reopen backing storage can do so.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxclio.h -->