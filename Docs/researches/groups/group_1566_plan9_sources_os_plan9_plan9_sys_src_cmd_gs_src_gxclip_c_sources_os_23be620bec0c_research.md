# Group Research: group_1566_plan9_sources_os_plan9_plan9_sys_src_cmd_gs_src_gxclip_c_sources_os_23be620bec0c

Scope checked against `Docs/research_subset_a.md`: this group is within `sources/os/plan9/plan9`. I read every listed source file completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxclip.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxclip.c

## Purpose
Implements Ghostscript’s rectangle-list clipping device. It wraps a target `gx_device` and intercepts drawing operations, forwarding only the portions that intersect the current `gx_clip_list`.

## Main Responsibilities
- Defines the `"clipper"` device descriptor `gs_clip_device`.
- Builds clipping devices via `gx_make_clip_translate_device` and `gx_make_clip_path_device`.
- Enumerates intersections between requested drawing rectangles and a sorted list of clip rectangles.
- Forwards clipped fragments to target device procedures for:
  - `fill_rectangle`
  - `copy_mono`
  - `copy_color`
  - `copy_alpha`
  - `fill_mask`
  - `strip_tile_rectangle`
  - `strip_copy_rop`
- Implements clipping-box calculation and translated `get_bits_rectangle`.

## Key Implementation Details
- `clip_enumerate` translates client coordinates by `rdev->translation` before clipping.
- `clip_enumerate_rest` keeps a mutable cursor `rdev->current` into the clip list for locality.
- Fast paths avoid full enumeration when the operation lies inside the current clip rectangle.
- `CHECK_VERTICAL_CLIPPING` enables lookahead to coalesce vertically adjacent full-width spans.
- Multi-rectangle operations use shared callbacks declared in `gxclip.h`.

## Important Data Flow
Input drawing op -> translate coordinates -> test current clip rect -> enumerate intersecting spans -> callback forwards span to target device.

## Notable Edge Cases
- Zero or negative width/height returns success without forwarding.
- Single-rectangle clip lists are optimized separately from list-head/list-tail dummy structures.
- `fill_mask` delegates to `gx_default_fill_mask` when an additional `pcpath` is supplied.
- `clip_get_clipping_box` caches the computed box and reverses translation for client coordinates.

## Dependencies
- `gxclip.h` for callback payloads and callbacks.
- `gxcpath.h` / `gxpath.h` for clip path/list conversion.
- Target device procedure table for all forwarded drawing operations.

## Research Notes
This is a core clipping adapter: it does not render itself, but slices drawing calls into clipped target calls. The correctness of coordinate translation and `rdev->current` cursor maintenance is central to avoiding missed or duplicated drawing spans.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxclip.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxclip.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxclip.h

## Purpose
Defines shared internal callback state for clipping devices and declares rectangle-processing callback procedures used by rectangle-list and mask clipping implementations.

## Main Responsibilities
- Defines `clip_callback_data_t`, a common closure object for clipped span callbacks.
- Declares callback functions implemented in `gxclip.c`.
- Provides a shared ABI between rectangle clipping and mask clipping paths.

## Key Structures
`clip_callback_data_t` stores:
- Target device pointer.
- Original operation rectangle.
- Bitmap source data, raster, and source X offset.
- Color or drawing-color payloads.
- Alpha depth and logical operation.
- Tile/texture state and phase values.
- Strip-copy RasterOp color arrays.

## Dependencies
- Requires Ghostscript core types such as `gx_device`, `gx_color_index`, `gx_drawing_color`, `gx_clip_path`, and `gx_strip_bitmap`.

## Research Notes
This header intentionally uses one broad callback structure instead of operation-specific structures. That reduces boilerplate but means each callback must know which fields are valid for its operation.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxclip.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxclip2.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxclip2.c

## Purpose
Implements tiled mask clipping for patterns. It adapts the general mask clipping infrastructure to repeated tile masks with explicit phase handling.

## Main Responsibilities
- Defines the `"tile clipper"` device descriptor.
- Initializes tiled clip devices with `tile_clip_initialize`.
- Stores and updates tile phase with `tile_clip_set_phase`.
- Clips fill/copy operations through a repeated mask tile.
- Scans tile bits into runs for non-monochrome operations.

## Key Implementation Details
- `tile_clip_initialize` delegates base setup to `gx_mask_clip_initialize`, then records tile metadata and phase.
- `x_offset` accounts for tile phase and `rep_shift` across repeated tile rows.
- `tile_clip_fill_rectangle` forwards directly as `strip_tile_rectangle`.
- `tile_clip_copy_mono` intersects source bits with tile mask in a memory device buffer, then forwards the combined mask.
- `FOR_RUNS` macro scans repeated tile rows for runs of set bits and forwards those runs.

## Forwarded Operations
- `copy_color`
- `copy_alpha`
- `strip_copy_rop`
- `copy_mono` through a temporary mask intersection path
- `fill_rectangle` through strip tiling

## Dependencies
- `gxclip2.h` for type/interface.
- `gxmclip.h` via header for shared mask clip state.
- `gxdevmem.h` for memory device buffering.

## Research Notes
This file is specialized for repeated pattern masks. It trades generic clip-list enumeration for bit-run scanning over the tile bitmap and phase-adjusted repetition.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxclip2.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxclip2.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxclip2.h

## Purpose
Declares the tiled mask clipping device interface.

## Main Responsibilities
- Aliases `gx_device_tile_clip` to `gx_device_mask_clip`.
- Provides the tile-clip structure descriptor macro.
- Declares initialization and phase-setting procedures.

## Key API
- `tile_clip_initialize(...)`: creates a tile clipping wrapper from a `gx_strip_bitmap`, target device, phase, and allocator.
- `tile_clip_set_phase(...)`: updates the tile phase used by repeated tile clipping.

## Dependencies
- Includes `gxmclip.h`, since tiled clipping reuses the generic mask clip structure.

## Research Notes
The header makes explicit that tile clipping is structurally identical to mask clipping. The distinction is behavioral and lives in the device procedure table from `gxclip2.c`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxclip2.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxclipm.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxclipm.c

## Purpose
Implements the general bitmap-mask clipping device. It forwards drawing operations only where a finite mask bitmap has set bits.

## Main Responsibilities
- Defines exported `gs_mask_clip_device`.
- Clips rectangle fills by painting through the mask with `copy_mono`.
- Clips bitmap copy operations by intersecting source data with the mask.
- Enumerates mask runs for color, alpha, strip-tile, and RasterOp operations.
- Computes a clipping box adjusted by mask phase.

## Key Implementation Details
- `FIT_MASK_COPY` maps requested target coordinates into mask coordinates and clips them to the mask bitmap extent.
- `mask_clip_copy_mono` uses a memory-device buffer to combine the source bitmap and mask bitmap.
- `clip_runs_enumerate` scans mask bytes using `byte_bit_run_length` tables.
- Consecutive identical horizontal runs on adjacent scanlines are coalesced into vertical rectangles before callback forwarding.
- Callback forwarding reuses `clip_call_*` functions from `gxclip.c`.

## Important Edge Cases
- Operations outside the mask bounds are clipped to empty by `FIT_MASK_COPY`.
- `copy_mono` uses color inversion choices from `setup_mask_copy_mono`.
- `mask_clip_get_clipping_box` forwards the target clipping box and subtracts mask phase.

## Dependencies
- `gxclipm.h` for exported device declaration.
- `gxclip.h` callback routines indirectly through `gxmclip.h`.
- `gsbittab.h` for bit-run lookup tables.
- `gxdevmem.h` for temporary mask intersection buffers.

## Research Notes
This is the finite-mask counterpart to `gxclip2.c`. It scans actual mask rows once rather than repeating a tile pattern.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxclipm.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxclipm.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxclipm.h

## Purpose
Declares the exported mask clipping device descriptor.

## Main Responsibilities
- Includes `gxmclip.h`.
- Exposes `extern const gx_device_mask_clip gs_mask_clip_device`.

## Dependencies
Requires the mask clipping structure definitions from `gxmclip.h`.

## Research Notes
This is a narrow public/internal bridge: users instantiate or reference the mask clipping device implemented in `gxclipm.c`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxclipm.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxclipsr.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxclipsr.h

## Purpose
Defines internals for clip save/restore stack management.

## Main Responsibilities
- Forward-declares `gx_clip_path` and `gx_clip_stack_t`.
- Defines `gx_clip_stack_s`, a reference-counted linked stack node.
- Provides GC structure descriptor macro `private_st_clip_stack`.

## Key Structure
`gx_clip_stack_s` contains:
- Reference-count header.
- Pointer to saved `gx_clip_path`.
- Pointer to next stack node.

## Dependencies
- Includes `gsrefct.h` for reference-counting support.

## Research Notes
The file explains that clipping paths are stacked separately from graphics-state objects because off-stack graphics states may share them. Reference counting is therefore required.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxclipsr.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxclist.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxclist.c

## Purpose
Implements command-list device document/page lifecycle code and shared command-list setup for Ghostscript band rendering.

## Main Responsibilities
- Defines GC enumeration/relocation for `gx_device_clist`.
- Defines `gs_clist_device_procs`, the command-list device procedure table.
- Initializes tile cache, band layout, command buffers, and per-band state.
- Opens, closes, rewinds, and finalizes clist band files.
- Ends pages by flushing command buffers and writing terminal band-block entries.
- Computes per-page colors-used metadata.
- Provides VM-error recovery paths for memory-backed band lists.
- Implements `get_band`.

## Key Implementation Details
- A clist device records drawing commands first, then later replays them by band.
- `clist_init_data` partitions one buffer among tile cache, rendering buffer needs, and writer state.
- Band height is either supplied or computed from available buffer space.
- `clist_reset` initializes all per-band `gx_clist_state` records and marks imager/tile parameters unknown.
- `clist_reinit_output_file` sets low-memory warning reserves for command and block files.
- `clist_emit_page_header` writes pass-through target parameters when required by async/partial rendering behavior.
- `clist_end_page` writes `cmd_opv_end_page` and a terminating `cmd_block`.

## Error and Memory Handling
- `permanent_error` blocks future writing after unrecoverable setup/write failures.
- `error_is_retryable` distinguishes recoverable VM warnings from hard VM errors.
- `clist_VMerror_recover` can render/free partial band-list memory without flushing the current page.
- `clist_VMerror_recover_flush` performs a hard flush and resets writer state.

## Dependencies
- `gxclist.h` for core structures.
- `gxcldev.h` and `gxclpath.h` for command-writing helpers and drawing procedure declarations.
- `gxdevmem.h` for buffer device sizing.
- `gsparams.h` for serialized target parameter pass-through.

## Research Notes
This file is the page-level coordinator for banded rendering. The lower-level command encoding and replay logic lives elsewhere, but this file owns allocation geometry, scratch files, page boundaries, and recoverable low-memory behavior.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxclist.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxclist.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxclist.h

## Purpose
Defines the main Ghostscript command-list data structures and public clist APIs.

## Main Responsibilities
- Documents the two-phase command-list model:
  - record drawing commands sorted by bands
  - replay commands band-by-band to render output
- Defines saved-page and placed-page structures.
- Defines tile cache structures used during write/read phases.
- Defines shared, writer, reader, and union forms of `gx_device_clist`.
- Provides initialization macro `clist_init_params`.
- Declares lifecycle and rendering APIs.

## Key Structures
- `gx_saved_page`: snapshot of a device plus band page metadata and copy count.
- `gx_placed_page`: saved page plus placement offset.
- `tile_hash`, `tile_slot`: bitmap/tile cache entries with per-band definition masks.
- `cmd_prefix`, `cmd_list`: buffered command-run list infrastructure.
- `gx_device_clist_writer`: write-phase state, including command buffer, band states, current imager state, tile cache state, retry policy, and disable mask.
- `gx_device_clist_reader`: read-phase state, including render plane and optional placed-page list.
- `gx_device_clist`: union over common/writer/reader views.

## Important Flags
`disable_mask` can disable specific clist behavior such as path fills, path strokes, high-level images, complex clips, pass-through params, and `copy_alpha`.

## Public APIs
- `clist_finish_page`
- `clist_close_output_file`
- `clist_close_page_info`
- `clist_compute_colors_used`
- `clist_setup_params`
- `clist_render_rectangle`

## Dependencies
Includes command-list I/O, banding, buffering, raster-plane, imager-state, and bitmap-cache headers.

## Research Notes
This header is the command-list contract. It is heavily stateful, and correctness depends on distinguishing fields valid in writer mode from fields valid in reader mode.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxclist.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxcllzw.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxcllzw.c

## Purpose
Provides LZW compressor/decompressor prototype states for RAM-backed command-list files.

## Main Responsibilities
- Defines static LZW encode/decode state prototypes.
- Initializes them in `gs_cl_lzw_init`.
- Exposes prototype pointers through:
  - `clist_compressor_state`
  - `clist_decompressor_state`

## Key Implementation Details
- Uses `s_LZW_set_defaults` for both states.
- Assigns `s_LZWE_template` to the compressor and `s_LZWD_template` to the decompressor.
- The `mem` argument to `gs_cl_lzw_init` is unused in this file.

## Dependencies
- `gxclmem.h` declares the compressor/decompressor accessors.
- `slzwx.h` supplies LZW stream templates.

## Research Notes
This file is deliberately small. It decouples `gxclmem.c` from direct static construction of LZW stream states.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxcllzw.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxclmem.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxclmem.c

## Purpose
Implements RAM-backed command-list “files” with optional LZW compression, reserve memory, seeking, reading, and writing.

## Main Responsibilities
- Implements `memfile_fopen`, `memfile_fclose`, `memfile_fwrite_chars`, `memfile_fread_chars`, `memfile_fseek`, `memfile_rewind`, and status helpers.
- Maintains logical blocks mapped to physical data blocks.
- Starts compression after a threshold of allocated data.
- Caches decompressed blocks in an LRU raw-buffer list.
- Provides reserve-block behavior so clist writes can complete after low-memory warnings.

## Data Model
- `LOG_MEMFILE_BLK`: logical file block used for file-position indexing.
- `PHYS_MEMFILE_BLK`: physical storage block holding raw or compressed data.
- `RAW_BUFFER`: decompression cache entry.
- `MEMFILE`: full memory file state, including allocators, logical position, compression streams, reserves, and read/write cursors.

## Key Implementation Details
- Uncompressed mode uses one physical block per logical block.
- When `NEED_TO_COMPRESS` becomes true, earlier full logical blocks are compressed into chained physical blocks.
- The last block remains raw while writing.
- Compressed logical blocks remember their physical block and byte pointer.
- Decompression uses a lazily allocated raw-buffer pool sized roughly one buffer per 32 logical blocks, with a minimum of 8.
- `memfile_get_pdata` resolves the current logical block into readable raw bytes, using the decompression cache when necessary.
- Backward seeks restart traversal from the logical head; forward seeks traverse from current state.

## Memory-Pressure Behavior
- `memfile_set_memory_warning` preallocates reserve logical and physical blocks.
- `allocateWithReserve` falls back to reserve chains and returns positive status for low-memory warning success.
- `memfile_fwrite_chars` stores positive warning status in `error_code` but can still report full byte count written.

## Limitations
- Reopening existing memory files is not implemented.
- Closing without deletion is rejected.
- `unlink` is not representable because memfiles are only identified by pointer.
- Writing after seeking to non-start positions is not properly supported; the code expects clist usage patterns.

## Dependencies
- `gxclmem.h` for structure declarations and API aliases.
- LZW prototypes from `gxcllzw.c`.
- Ghostscript stream templates and memory allocators.

## Research Notes
This is a custom in-memory file layer for band-list storage. It is optimized around sequential writes, mostly increasing-position reads, and bounded low-memory recovery rather than general file semantics.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxclmem.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxclmem.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxclmem.h

## Purpose
Declares structures and aliases for the memory-backed command-list file implementation.

## Main Responsibilities
- Defines block size `MEMFILE_DATA_SIZE`.
- Declares raw, physical, logical, and top-level memory-file structures.
- Defines GC descriptor macro for `MEMFILE`.
- Aliases `memfile_*` operations to generic `clist_*` I/O names.
- Declares compressor/decompressor prototype accessors.

## Key Structures
- `RAW_BUFFER`: doubly linked decompression cache block.
- `PHYS_MEMFILE_BLK`: allocated data block, raw or compressed.
- `LOG_MEMFILE_BLK`: logical block index entry pointing into physical storage.
- `MEMFILE`: state object for logical/physical file content, reserves, cursor position, stream state, and compression status.

## Important Design Notes
- Most helper structures are allocated on the C heap, while `MEMFILE` and stream states are GC-compatible.
- Reserve chains are part of the low-memory write guarantee used by command-list banding.
- `pdata` always points into raw bytes, whether original raw storage or decompressed cache storage.

## Dependencies
- `gxclio.h` for generic clist I/O interface.
- `strimpl.h` for stream state/cursor structures.

## Research Notes
This header exposes the full internal data model, so it is tightly coupled to `gxclmem.c`. The generic `clist_*` macro aliases let the same command-list code use memory-backed files transparently.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxclmem.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxclpage.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxclpage.c

## Purpose
Implements saved-page management for banding printer devices.

## Main Responsibilities
- Saves the current banded page into a `gx_saved_page`.
- Renders an array of saved pages at specified offsets.
- Validates saved-page compatibility with the rendering printer device.
- Deletes temporary clist files after rendering placed pages.

## Key Implementation Details
- `gdev_prn_save_page` requires banding (`pdev->buffer_space` nonzero).
- Saving a page ends the clist page, closes command/block files without deleting them, copies device metadata, and reopens the printer device.
- `gdev_prn_render_pages` checks device name, color info, Y offset, buffer space, band width, and band height compatibility.
- Rendering works by setting placed-page data into the clist reader and invoking the printer’s `output_page`.

## Limitations
- Y translation is currently rejected; only X offsets are allowed.
- Saved pages must come from the same device type and compatible band parameters.
- Color representation checking is only partial.

## Dependencies
- `gdevprn.h` for printer device type.
- `gxcldev.h` for clist internals.
- `gxclpage.h` for saved-page declarations.

## Research Notes
This file lets command-list pages become composable page objects. It is separate from normal clist page finalization because it preserves temporary band files for later rendering.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxclpage.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxclpage.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxclpage.h

## Purpose
Declares saved-page APIs for command-list printer devices.

## Main Responsibilities
- Documents how clients save a banded page object.
- Documents how clients render multiple saved pages with offsets.
- Declares:
  - `gdev_prn_save_page`
  - `gdev_prn_render_pages`

## Dependencies
- Requires `gdevprn.h` and `gxclist.h`.
- Includes `gxclio.h`.

## Research Notes
The header clarifies ownership: clients provide/free saved and placed page storage, while the rendering routine consumes compatible clist temporary files.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxclpage.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxclpath.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxclpath.c

## Purpose
Implements higher-level path and drawing-color command encoding for command-list banding.

## Main Responsibilities
- Serializes fill/stroke paths into compact clist path commands.
- Tracks and writes imager-state changes needed per band.
- Serializes drawing colors and device halftones when required.
- Handles clip-path command emission.
- Implements clist device procedures for:
  - `fill_path`
  - `stroke_path`
  - `fill_parallelogram`
  - `fill_triangle`

## Key Implementation Details
- `cmd_put_drawing_color` serializes device colors with `cmd_opv_ext_put_drawing_color` and inserts halftones as needed.
- `cmd_drawing_colors_used` estimates colors touched by pure, binary halftone, colored halftone, or general colors.
- `cmd_clear_known` invalidates per-band known-state flags.
- `cmd_write_unknown` emits missing imager parameters for each band, including misc parameters, fill adjust, CTM, dash, clip path, and color space.
- Clip paths may be emitted as:
  - a rectangle
  - a serialized filled path
  - a list of rectangles
  - outer box fallback when complex clips are disabled
- `clist_fill_path` and `clist_stroke_path` compute Y coverage, update required state, emit color/logical-op state, and serialize path commands for each affected band.
- Long dash patterns fall back to default stroke rendering.
- `clist_fill_parallelogram` fast-paths rectangular parallelograms to rectangle fill; otherwise it builds a temporary path.
- `cmd_put_path` encodes paths with relative fixed-point deltas, band-Y omission of fully outside segments, implicit close handling, and compact segment opcode choices.

## Path Encoding
- Relative fixed-point operands are encoded in variable-length forms.
- Line segments are shortened to horizontal/vertical variants when possible.
- Multiple line commands can merge into compact multi-line commands.
- Curves are specialized into variants such as `hvcurveto`, `vhcurveto`, `nrcurveto`, `rncurveto`, quadratic-like shortcuts, or symmetric `scurveto`.
- Segment notes are emitted through `cmd_opv_set_misc2` when they change and are requested.

## Fallback Conditions
- Debug flag disables path-based banding.
- Explicit disable-mask bits force default fill/stroke handling.
- Too-long dash patterns fall back.
- Drawing-color serialization failures can fall back to default path rendering.

## Dependencies
- `gxclpath.h` for opcodes, known-state flags, and exported helpers.
- `gxcldev.h` for base command writing macros/procedures.
- Path and clip internals from `gzpath.h` and `gzcpath.h`.
- Drawing color, paint, stream, and serialization helpers.

## Research Notes
This file is the central high-level drawing encoder for clists. It balances compactness, per-band state caching, and safe fallback to default rendering when operations are too complex or disabled.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxclpath.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxclpath.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxclpath.h

## Purpose
Defines extended command-list opcodes, state-known flags, and exported helpers for path-level command-list writing.

## Main Responsibilities
- Defines per-band known-state bit flags.
- Defines drawing-color classification enum `cmd_dc_type`.
- Extends the command set for imager state, clipping, images, path segments, path painting, and extension commands.
- Documents compact path operand encoding.
- Declares clist path driver procedures and support helpers.

## Key Definitions
Known-state flags include:
- line cap/join
- curve/stroke adjustment
- flatness
- line width
- miter limit
- overprint/blend/text-knockout
- opacity and shape alpha
- fill adjustment
- CTM
- dash
- clip path
- color space

Extended command opcodes include:
- `cmd_opv_set_fill_adjust`
- `cmd_opv_set_ctm`
- `cmd_opv_set_color_space`
- `cmd_opv_set_misc2`
- `cmd_opv_set_dash`
- clip enable/disable/begin/end
- image begin/data commands
- path segment commands
- fill/eofill/stroke/polyfill commands

Further extension opcodes include:
- serialized parameter list
- compositor creation
- halftone data
- drawing-color serialization

## Exported Helpers
- `cmd_drawing_colors_used`
- `cmd_slow_rop`
- `cmd_put_drawing_color`
- `cmd_clear_known`
- `cmd_write_ctm_return_length`
- `cmd_write_ctm`
- `cmd_write_unknown`
- `cmd_check_clip_path`

## Dependencies
- Extends `gxcldev.h`.
- Relies on command-buffer sizing and encoding helpers from lower-level clist infrastructure.

## Research Notes
This header is the opcode/state contract for `gxclpath.c` and related command-list image/path writers. The comments encode the wire format, making this file essential for reader/writer compatibility.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxclpath.h -->