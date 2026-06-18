# Group Research: group_127_9front_sources_os_plan9_9front_sys_src_cmd_gs_src_gxccman_c_sources__e17fcc2fdd51

Scope: `Docs/research_subset_a.md`, source tree `sources/os/plan9/9front`. All listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxccman.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxccman.c

Implements Ghostscript character-cache management for font/matrix pairs, xfont lookup, cached glyph bitmap allocation, bitmap post-processing, and cache purging.

Key behavior:
- Allocates the font directory's font/matrix cache and open-addressed cached-character hash table, rounding the table to a power-of-two size with extra slack.
- Initializes cache chunks through the generic bits-cache layer and resets all `cached_fm_pair` entries, including TrueType reader/font pointers.
- Adds font/matrix pairs using `gx_compute_ccache_key`; when full, prefers evicting a pair with no cached characters and otherwise purges the selected pair.
- For Type 42/CID TrueType fonts without FAPI, creates a TrueType reader and helper font object tied to the scaled character matrix.
- Looks up xfonts through the current device's xfont device/procs, trying key name, font name, and original fonts with matching UID; stroked fonts are excluded.
- Purges selected cached characters by scanning the hash table, removing matching entries, freeing their bits, and preserving open-addressing lookup correctness by relocating following entries.
- Allocates character bitmap storage for mono or alpha-buffer cache devices, checking scaled-down size against cache limits and setting up memory devices in-place while preserving reference-count metadata.
- Adds rendered character bits by finding the non-white bounding box, trimming whitespace, compressing oversampled bitmaps to the requested alpha depth, adjusting offsets, shortening the bits-cache block, and assigning a fresh bitmap id.
- Frees and shortens cached characters through the shared bits-cache chunk machinery; chunk cycling can evict older entries to make room.
- Purges all cache references to a font, retaining UID-valid font/matrix entries by clearing their font pointer and fully purging others.

Dependencies:
- Uses Ghostscript memory/GC descriptors, font-directory and character-cache structures from `gxfcache.h`, memory devices from `gxdevmem.h`, font internals from `gxfont*.h`, xfont hooks from `gxxfont.h`, and TrueType helpers from `gxttfb.h`/`gxfont42.h`.
- Uses `gs_next_ids` for cached bitmap ids and generic bits-cache allocation/free/shorten operations.

Research notes:
- Cache correctness depends on keeping the character hash table and `cached_fm_pair::num_chars` synchronized during eviction and purge.
- `gx_add_char_bits` mutates bitmap dimensions and offsets after rendering, so callers must not assume the cache device's temporary dimensions survive unchanged.
- The xfont path stores the graphics state's memory in the pair because xfonts can outlive a single lookup and must be released on purge.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxccman.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxcdevn.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxcdevn.h

Internal DeviceN color-space support header.

Key behavior:
- Defines `gs_device_n_map`, a reference-counted one-entry cache for DeviceN tint transforms.
- Stores the tint transform callback, callback data, cache-valid flag, last tint component values, and concrete device component fractions.
- Provides the private GC descriptor macro for relocating `tint_transform_data`.
- Declares allocation/initialization through `alloc_device_n_map`.
- Declares `using_alt_color_space`, which reports whether the current graphics state is using the alternate color space.

Dependencies:
- Includes Ghostscript reference-count support and `gxcindex.h` for `GX_DEVICE_COLOR_MAX_COMPONENTS`.
- Depends on `GS_CLIENT_COLOR_MAX_COMPONENTS`, `gs_imager_state`, `gs_state`, and Ghostscript client-name/memory types from surrounding headers.

Research notes:
- The cache is explicitly a single-entry optimization, not a general tint-transform memo table.
- This header only defines the internal data contract; implementation lives in DeviceN color-space code outside this group.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxcdevn.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxchar.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxchar.c

Default Ghostscript text rendering implementation. It drives show/stringwidth/charpath processing, cached glyph lookup and creation, xfont fallback, text positioning, and BuildChar/BuildGlyph continuation.

Key behavior:
- Defines the GC-visible `gs_show_enum` descriptor and default `gs_text_enum_procs` for resync, process, width-only query, current-width query, cache setup, retry, and release.
- `gx_default_text_begin` validates that the imager state is a full `gs_state`, initializes the text enumerator, derives charpath/cache policy from the requested text operation, prepares state, and installs a null device for stringwidth.
- `gx_hld_stringwidth_begin` gives pdfwrite a helper path/current-point setup for Type 3 stringwidth handling.
- `gx_show_text_set_cache` handles `setcharwidth`, `setcachedevice`, and `setcachedevice2`, including WMode 1 origin adjustment and retry rewinding.
- `set_char_width` transforms character advance to device coordinates and has special CID encrypted font handling to avoid applying a leaf FontMatrix to CDevProc widths.
- Computes raster parameters from device text alpha bits, font PaintType, pure-color status, FAPI-provided scale, current origin, and pixel-alignment mode.
- `set_cache_device` decides whether a glyph can be cached, transforms the font bounding box to device space, rejects very large or invalid entries, allocates cache memory devices, clips user-defined fonts when needed, and redirects rendering into the cache device.
- The continuation pipeline uses `show_proceed`, `show_update`, and `show_move` to alternate between cache hits, direct BuildChar calls, intervention returns for cshow/kshow, and final movement.
- Cache-hit handling can image cached glyphs, append cached bounding boxes for charboxpath, or short-circuit charwidth/stringwidth.
- Cache-miss handling saves graphics state, switches to the descendant font when needed, sets charpath mode, adjusts the CTM/current origin into character space, then calls the font's build procedure.
- `show_update` finishes a cached render by adding the cached character to the font cache, restoring graphics state levels, loading color, and optionally imaging the just-created cache entry.
- `gx_show_text_retry` discards a partially cached glyph and restores state so character rendering can be retried.
- `show_state_setup` refreshes current font/matrix state after start, font changes, and kshow callbacks; it records clipping boxes, transformed font translation, and cache eligibility.
- `show_set_scale` selects oversampling for small non-skewed outline characters, scaling both axes when oversampling is used.
- Releases retained cache and null devices before delegating to the default text-enum release path.

Dependencies:
- Uses graphics state internals, matrix/path operations, memory and null devices, font stacks/composite fonts, font cache APIs from `gxchar.h`/`gxfcache.h`, and CID font helpers.
- Calls cache-manager functions from `gxccman.c` and cache lookup/imaging routines implemented elsewhere.

Research notes:
- This file is continuation-oriented: many public text operations return intermediate statuses rather than rendering an entire string in one call.
- Cache decisions are deliberately conservative around charpath modes, modified CTMs, non-pure colors, stroked fonts, alpha, clipping, and oversized glyphs.
- Correct graphics-state level accounting is central: BuildChar procedures may save/restore, and `show_update` validates the resulting save depth.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxchar.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxchar.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxchar.h

Internal character and text-show declarations for Ghostscript.

Key definitions:
- Forward-declares cached characters, cached font/matrix pairs, fonts, text enumerators, memory devices, and null devices.
- Defines `show_width_status` values used while BuildChar communicates width and cache-device choices.
- Defines `gs_show_enum_s`, a subclass of `gs_text_enum_common`, with graphics state pointers, charpath mode, cache permissions, clipping boxes, transformed font translation, encoding callback, FAPI scaling data, cache/null devices, current width/origin, active cached character, and continuation callback.
- Provides the public structure descriptor macro for `gs_show_enum`.

Key declarations:
- Text accessors: `gx_current_char`, `gx_compute_text_oversampling`, `set_char_width`, `gx_default_text_restore_state`, and `gx_hld_stringwidth_begin`.
- Cached-character lifecycle and lookup APIs: allocate/open/free/add bits, add cache entry, lookup cached glyph, lookup xfont glyph, and image cached glyph.

Dependencies:
- Requires `gschar.h` and `gxtext.h`; comments note that matrix and fixed-point definitions must already be visible.

Research notes:
- The struct layout is part of the internal text-rendering contract; BuildChar and cache code rely on fields such as `width_status`, `cc`, `pair`, `log2_scale`, and `continue_proc`.
- `can_cache` distinguishes no cache use, read-only cache use, and full read/write cache use.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxchar.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxchrout.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxchrout.c

Implements the shared outline-character flatness heuristic.

Key behavior:
- `gs_char_flatness` inspects the absolute CTM scale/skew terms and chooses the smallest non-zero effective scale component.
- Corrects the scale by the font's default scale, using 0.001 as the Type 1 baseline.
- Caps the result at the imager state's current flatness so character rendering is never coarser than requested.
- Forces flatness to zero for tiny characters below the 0.2 threshold, yielding more accurate curves.

Dependencies:
- Uses math helpers, fixed-arithmetic helpers, `gxistate.h`, and the declaration in `gxchrout.h`.

Research notes:
- This is a quality heuristic: small glyphs get extra curve accuracy, while larger glyphs remain bounded by graphics-state flatness.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxchrout.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxchrout.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxchrout.h

Shared header for outline character rendering helpers.

Key declarations:
- Forward-declares `gs_imager_state`.
- Declares `double gs_char_flatness(const gs_imager_state *pis, floatp default_scale);`.

Behavior contract:
- The helper returns a character-specific flatness that may be lower than the imager state's flatness.
- `default_scale` is expected to be 0.001 for Type 1 fonts and 1.0 for TrueType fonts.

Research notes:
- The header intentionally exposes only the flatness computation, keeping outline rasterization details elsewhere.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxchrout.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxcht.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxcht.c

Implements colored halftone device colors: serialization/deserialization, equality/saved-state support, nonzero-component reporting, color table setup, and raster composition for halftoned rectangle fills.

Key behavior:
- Defines `gx_dc_type_ht_colored`, including save, device-halftone access, load, fill-rectangle, equality, write/read, and nonzero-component procedures.
- Saves and compares colored halftone device colors by halftone pointer, alpha, phase, component count, base component values, and halftone level values.
- Serializes colored halftone device colors using flag bits for base values, level values, and alpha; omits unchanged fields by comparing against the previous saved device color.
- Optimizes serialization for 1-bit-per-component devices by packing base component bits into bytes.
- Serializes level values using `plane_mask` so only nonzero halftoned components are transmitted; supports component masks wider than a native `uint`.
- Reconstructs colored halftone device colors from serialized data, using the current imager state's device halftone and screen phase.
- Reports nonzero components as the union of `plane_mask` and components with nonzero base values.
- Fills rectangles by clipping to the device box, clearing transparent RasterOp texture semantics, loading per-plane halftone caches, choosing optimized color and tile-composition procedures, and then either tiling an LCM-sized cell or generating smaller chunks.
- Supports no-source copy paths through `copy_color`/`strip_tile_rectangle`, and RasterOp paths through `strip_copy_rop`.
- Builds color lookup tables differently for <=4 planes, special 1-bit CMYK, and >4 planes.
- For subtractive color models, inverts color pairs and halftone levels so additive halftone orders can drive subtractive devices.
- Uses a special 1-bit CMYK path that reverses planes and computes packed pixels through Boolean masks rather than per-pixel lookup.
- For >4 components, assumes separable device color indices and combines per-plane encoded values with bitwise OR.
- Renders halftone tiles through per-plane `tile_cursor_t` objects that handle X offset, wrapping, shifted tiles, row stepping, and packed output for 4/8/16/24/32-bit depths.

Dependencies:
- Uses device color interfaces from `gxdcolor.h`, halftone internals from `gzht.h`, device color mapping from `gxcmap.h`, device procedures, fixed/matrix helpers, and `gs_next_ids`.

Research notes:
- The implementation has multiple explicit optimization tiers: small component-count lookup tables, 1-bit CMYK bit masks, and a separable fallback for DeviceN-like cases.
- Several comments mark limitations for DeviceN, alpha, and extra planes; these paths should be treated as pragmatic support for the command-list era rather than a fully general color architecture.
- The fill path assumes colored halftones are opaque texture for RasterOp by clearing `lop_T_transparent`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxcht.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxcid.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxcid.h

Common CID/CMap metadata definitions.

Key definitions:
- Defines `gs_cid_system_info_t` with `Registry`, `Ordering`, and `Supplement`.
- Provides structure descriptor macros for a single CIDSystemInfo value and arrays of CIDSystemInfo values, with two const-string pointer fields.
- Declares `cid_system_info_set_null` and `cid_system_info_is_null`.

Behavior contract:
- A null CMap CIDSystemInfo is represented by empty `Registry` and `Ordering` strings plus `Supplement == 0`.

Dependencies:
- Includes `gsstype.h` for Ghostscript string and structure-descriptor support.

Research notes:
- This header is small but important for CID-keyed font identity; it gives shared representation to CMap and CID font code.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxcid.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxcie.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxcie.h

Internal CIE color implementation declarations.

Key behavior:
- Declares CIE color-space init, restrict, install, concretize, remap, and concrete-space procedures used by Ghostscript color-space type tables.
- Provides `gx_cie_to_xyz_alloc`/`gx_cie_to_xyz_free`, a semi-special imager-state setup for PDF writer CIE-to-XYZ concretization.
- Defines `CIE_CHECK_RENDERING`, which returns black if no CIE rendering is installed and otherwise completes joint caches before remapping.
- Declares generic and concrete CIE remap-finish procedures, including real rendering and XYZ-only variants.
- Exposes GC descriptors for common CIE data structures.
- Declares helpers to set common defaults, load common caches, complete common CIE caches, install indirect CIE color spaces, and build common CIE color-space storage.

Dependencies:
- Includes `gscie.h` and depends on Ghostscript color-space procedure declaration macros, `gs_imager_state`, `gs_color_space`, `gs_state`, and CIE cache types.

Research notes:
- Comments document historical external-name length constraints, which explain the shorter `CIExxx` naming.
- The rendering check macro has control-flow effects via the caller-provided `do_exit`, so callers must read it as more than a pure predicate.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxcie.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxcindex.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxcindex.h

Defines the internal device color index type and scan-line accumulation macros.

Key behavior:
- Sets `GX_DEVICE_COLOR_MAX_COMPONENTS` to 16, bounded by the available bits in `gx_color_index`.
- Defines `gx_color_index_data` from `GX_COLOR_INDEX_TYPE` or `ulong`, with disabled test variants for pointer or struct color indices.
- Defines `gx_color_index`, `arch_sizeof_color_index`, and the transparent/undefined `gx_no_color_index` value.
- Provides `DECLARE_LINE_ACCUM`, `LINE_ACCUM`, `LINE_ACCUM_SKIP`, and `LINE_ACCUM_STORE` wrappers over sample-store macros for packing colored image pixels into a scan line.
- Provides `DECLARE_LINE_ACCUM_COPY` and `LINE_ACCUM_COPY` to flush accumulated pixels to a device's `copy_color` procedure.

Dependencies:
- Includes `gsbitops.h` for sample-store helpers.
- Depends on device procedure macros when using the copy macros.

Research notes:
- The file preserves old experimental alternate representations, but the active build uses a scalar color-index value.
- The scan-line macros assume a local block scope because they declare helper variables.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxcindex.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxclbits.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxclbits.c

Implements command-list bitmap, tile, and transfer-map writing support.

Key behavior:
- `clist_bitmap_bytes` computes written bitmap size and row width after selective raster-padding removal; compressed data keeps full raster, while small/one-line/spread bitmaps can drop padding.
- `cmd_put_bits` writes bitmap payloads into clist command buffers, optionally trying CCITTFax or RLE compression when worthwhile and legal for the reader buffer.
- Falls back to uncompressed short-row data when compression fails or is not beneficial; returns `limitcheck` if a bitmap cannot fit in the reading buffer and cannot be decompressed elsewhere.
- Emits tile-parameter commands with encoded depth, replication dimensions, optional repetition factors, and optional shift.
- Emits tile-index commands either as small deltas from the previous band state or as absolute indices.
- Emits color-map commands for none, identity, or explicit transfer-map values, using IDs to suppress redundant output.
- Maintains a clist tile/bitmap cache keyed by bitmap id using an open-addressed hash table and the generic bits-cache allocator.
- Deletes cache entries by freeing the bits-cache block, clearing the hash slot, and deleting later entries that would otherwise require relocation incompatible with band-list references.
- Adds tile slots with per-band known masks, cached bitmap metadata, and copied source bits.
- Chooses replicated tile parameters to improve playback efficiency while respecting cache size, max repetitions, shift constraints, and tile byte caps.
- `clist_change_tile` ensures tile parameters and bits are known in a band before tile-rectangle operations, writing parameter and bit commands when needed.
- `clist_change_bits` performs similar per-band caching for copy operations and can promote frequently seen character bitmaps to all bands when the configured threshold is reached.

Dependencies:
- Uses `gxcldev.h` command encodings and writer helpers, `gxdevmem.h`, compression stream states, bits-cache support, and transfer-map structures.

Research notes:
- The cache is coupled to band-list state: per-band masks track which bands know a cached tile, while hash slots may be deleted independently.
- Compression is opportunistic and bounded by `cbuf_size`; the code prioritizes playback buffer constraints over maximum compression ratio.
- `CHAR_ALL_BANDS_COUNT` is set to `max_ushort`, so this build never automatically broadcasts character bitmaps to all bands based on reuse count.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxclbits.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxcldev.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxcldev.h

Central internal header for Ghostscript command-list writer/reader support.

Key definitions:
- Defines bitmap compression mode constants for RLE and CCITTFax encoding plus initialization functions for encoder/decoder stream states.
- Defines the primary command bytecode enum: misc commands, tile setup, bitmap setup, color changes, rectangle fills/tiles, mono/color/alpha copies, and tile-index deltas.
- Defines debug opcode-name tables when `DEBUG` is enabled.
- Defines variable-size integer sizing and writing macros used throughout command-list emitters.
- Defines rectangle operand structures, short/tiny rectangle ranges, and encoded tile-depth conversion supporting depths above 32 bits.
- Documents and declares `clist_bitmap_bytes`.
- Defines `cmd_block` entries for band-file positions.
- Defines `gx_clist_state_s`, the per-band state cache for colors, saved device color, tile id/index/phase/colors, last rectangle, RasterOp, clip/logical-op flags, alpha-copy mode, known-state bitmask, command list, rendering cost, and colors-used accounting.
- Provides `cls_initial_values` for band-state initialization and `cbuf_size` for reader command buffer sizing.
- Declares clist device procedures implemented by rectangle, image/compositor, and reader modules.
- Declares writer-side VM-error recovery functions for asynchronous rendering and documents the two-stage recovery process.
- Defines command-allocation macros for per-band, range, and all-band commands plus command shortening.
- Declares color, tile, logical-op, clip, rectangle, bitmap, color-map, color-mapping, halftone, and playback helpers.
- Defines `FOR_RECTS`, `TRY_RECT`, `HANDLE_RECT`, and related macros that split drawing operations by band and coordinate retry/flush recovery.

Dependencies:
- Includes command-list device structures, RasterOp types, halftone/transfer-map/device-halftone headers, compression stream internals, and drawing-color definitions.

Research notes:
- This header is effectively the ABI for command-list bytecode writers and readers; small encoding changes affect many implementation files.
- The recovery macros are deliberately not transparent: callers must keep writer state idempotent until successful command emission.
- `known` flags are partitioned with path code; this header allocates high bits for tile and image state.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxcldev.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxclfile.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxclfile.c

Filesystem-backed implementation of the command-list I/O abstraction.

Key behavior:
- `clist_fopen` creates scratch files when passed an empty name for write modes, opens existing files otherwise, and rejects read mode with no filename.
- Uses Ghostscript platform wrappers for scratch-file and normal file opens.
- `clist_fclose` closes a file and optionally deletes it via `clist_unlink`.
- `clist_space_available` reports all requested space as available for file-backed storage.
- `clist_fwrite_chars` writes raw bytes with `fwrite`.
- `clist_fread_chars` uses direct `getc` fall-through for reads of 1 to 8 bytes to avoid inefficient tiny `fread` calls; larger reads use `fread`.
- Memory-warning threshold is a no-op in this implementation.
- `clist_ferror_code`, `clist_ftell`, `clist_rewind`, and `clist_fseek` wrap stdio status and positioning.
- `clist_rewind` can discard file data by reopening with write mode and then reopening with `w+` binary mode, working around the lack of portable stdio truncation.

Dependencies:
- Uses stdio, string, unlink wrappers, Ghostscript error/memory/platform headers, and the API contract from `gxclio.h`.

Research notes:
- The same `gxclio.h` interface can be backed by RAM storage on embedded systems; this file is the external filesystem variant.
- Return values from read/write are byte counts rather than normalized Ghostscript success/error codes, matching the clist I/O interface.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxclfile.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxclimag.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxclimag.c

Implements higher-level command-list image operations: mask filling, high-level image command emission, image-data banding, compositor command emission, halftone serialization, and color-mapping state emission.

Key behavior:
- `clist_fill_mask` turns suitable mask fills into cached clist copy commands, with copy-alpha translation for multi-bit masks, per-band clipping/color/RasterOp state, bitmap-cache lookup, and fallback to `gx_default_fill_mask` for unsupported cases.
- Rejects optimized mask handling for nontrivial clipping when complex clipping is disabled, debug fallback, uncached bitmap ids, non-default RasterOp, or non-pure alpha colors.
- Defines `clist_image_enum`, extending the common image enumerator with original image parameters, drawing color, source rectangle, imager/clip state, format, interpolation support pixels, bits-per-plane, image-to-device matrix, color-space metadata, conservative device Y range, prebuilt begin-image command, and dynamic row/color-map state.
- `clist_begin_typed_image` supports a restricted high-level path for ImageType 1 and 4; it falls back for nested images, disabled high-level images, CIE/non-basic color spaces, non-pure CombineWithColor, alpha images, varying plane depths, bad matrices, unsupported transforms, excessive row size, or complex clipping restrictions.
- Builds a serialized begin-image command using the image type table and the image type's `sput` procedure.
- Computes conservative colors-used information, exactly enumerating simple low-bit single-component images when feasible and otherwise assuming all device colors.
- Clears known clist state so CTM, color space, clip, alpha/opacity/shape, blend/overprint/text-knockout, and begin-image state are emitted before image data.
- `clist_image_plane_data` maps source rows to affected page bands, computes exact or conservative source subrectangles per band, writes begin-image commands once per band, and streams interleaved plane data in chunks sized for `cbuf_size`.
- Handles VM-error recovery by writing image-end commands, updating state, and forcing image-related state to be re-emitted after recovery.
- `clist_image_end_image` writes EOD image-data commands into all bands that saw a begin-image command, with local recovery and hard-flush fallback.
- `clist_create_compositor` serializes compositor creation, optionally emits CTM first for PDF 1.4 transparency compositors, and writes the compositor as an all-band extended command.
- `cmd_put_halftone` serializes full device halftones, writing a total-length command and splitting large serialized halftones into extended segment commands.
- `cmd_put_color_mapping` emits changed device halftone, black generation, undercolor removal, and transfer maps while suppressing redundant maps by ID.
- `image_band_box` computes the image-source rectangle intersecting a device band, using a fast axis-aligned inverse transform path and a general parallelogram/image-rectangle intersection path for rotated/skewed cases.
- `check_rect_for_trivial_clip` accepts null clips, clips that include the rectangle, or rectangular clips that intersect the rectangle.

Dependencies:
- Uses image type serialization, color-space helpers, clist writer/path command support, image parameter structures, streams, interpolation constants, compositor serialization, and device-halftone serialization.
- Depends on `gxcldev.h` for command opcodes, band macros, bitmap/cache helpers, and color-mapping declarations.

Research notes:
- The high-level image path is intentionally conservative and optimized for rectangular or near-axis-aligned banding; unsupported cases fall back to lower-level default image decomposition.
- `begin_image_command` has a comment warning that its static size computation is tied to image/matrix serialization internals.
- Halftone segments are not recovered transactionally after partial segment submission; the reader discards partial halftones when a new total-length command appears.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxclimag.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxclio.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxclio.h

Defines the command-list I/O abstraction used by both filesystem-backed and RAM-backed clist storage implementations.

Key behavior:
- Defines opaque `clist_file_ptr`.
- Declares open/close/unlink operations; empty filename on write mode requests generated scratch storage, while empty filename on read mode is invalid.
- Declares `clist_space_available`, raw byte write/read functions, memory-warning threshold setup, error-code reporting, tell, rewind, and seek.
- Documents that `clist_ferror_code` returns Ghostscript-style error codes, with `0` for no error and `1` for low-memory warning.
- Passes filenames to rewind/seek because some implementations may need to close and reopen storage.

Dependencies:
- Includes `gp.h` for `gp_file_name_sizeof`; uses Ghostscript memory, bool, and integer types from surrounding common headers.

Research notes:
- Compile/link selection chooses the concrete implementation, allowing the same command-list code to target embedded RAM storage or external files.
- The API exposes low-memory warning semantics even though the filesystem implementation treats them as no-ops.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxclio.h -->