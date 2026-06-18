# Group Research: group_128_9front_sources_os_plan9_9front_sys_src_cmd_gs_src_gxclip_c_sources_o_6bc2476f123a

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxclip.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxclip.c

Implements Ghostscript’s rectangle-list clipping proxy device. It wraps a target `gx_device`, intercepts drawing procedures, intersects requested output with a `gx_clip_list`, and forwards only visible rectangles to the target.

Key entry points:
- `gx_make_clip_translate_device()` initializes a clipping device from a clip rectangle list plus translation.
- `gx_make_clip_path_device()` derives the list from a `gx_clip_path`.
- `clip_open()` copies target geometry/color state and initializes the current clip rectangle cursor.
- Drawing methods include `clip_fill_rectangle`, `clip_copy_mono`, `clip_copy_color`, `clip_copy_alpha`, `clip_fill_mask`, `clip_strip_tile_rectangle`, and `clip_strip_copy_rop`.
- `clip_get_clipping_box()` returns the target clipping box intersected with the clip list, translated back to client coordinates.
- `clip_get_bits_rectangle()` forwards readback requests with translation adjustment.

The central algorithm is `clip_enumerate_rest()`, which walks the sorted clip rectangle list, keeps a mutable `current` cursor, intersects each matching row/run with the requested rectangle, and invokes a callback from `clip_callback_data_t`. It has fast paths in `clip_enumerate()` and `clip_fill_rectangle()` for the common case where a draw falls entirely inside the current clip rectangle.

Important details:
- `CHECK_VERTICAL_CLIPPING` enables a lookahead optimization that merges vertically adjacent full-width spans.
- Source-backed operations adjust data pointers and `sourcex` based on clipped offsets.
- `fill_mask` delegates to `gx_default_fill_mask` if an additional `pcpath` is supplied, avoiding nested clip handling in this device.
- The `current` cursor optimization assumes clip rectangles are ordered and include stopper behavior described in comments.

Filesystem relevance: indirect. This is graphics clipping infrastructure, but it participates in the band-list rendering pipeline used by printer/device output, which is backed elsewhere by clist files or memory files.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxclip.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxclip.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxclip.h

Internal shared definitions for rectangle-list and mask clipping.

Defines:
- `clip_callback_data_t`, a shared closure structure carrying target device, original rectangle, source bitmap data, colors, raster, alpha/mask parameters, tiling phase, textures, and RasterOp state.
- Callback declarations used by both `gxclip.c` and mask/tile clippers:
  `clip_call_fill_rectangle`, `clip_call_copy_mono`, `clip_call_copy_color`, `clip_call_copy_alpha`, `clip_call_fill_mask`, `clip_call_strip_tile_rectangle`, and `clip_call_strip_copy_rop`.

The structure is intentionally broad rather than specialized per callback, reducing boilerplate across the clipping implementations.

Filesystem relevance: none directly. It supports graphics-device clipping operations that may later be serialized into clist band files.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxclip.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxclip2.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxclip2.c

Implements the tiled-mask clipping device used for patterns. It reuses the mask-clip device layout (`gx_device_tile_clip` aliases `gx_device_mask_clip`) but applies a repeating tile mask with phase and replication shift.

Key entry points:
- `tile_clip_initialize()` initializes from a `gx_strip_bitmap`, target device, and explicit phase.
- `tile_clip_set_phase()` updates the tile phase.
- Device methods intercept fill/copy operations and forward visible tile-mask runs to the target.

Important algorithms:
- `tile_clip_fill_rectangle()` maps a fill into the target’s `strip_tile_rectangle`.
- `tile_clip_copy_mono()` breaks the source into chunks aligned with the tile, copies tile bits into an internal memory-device buffer, intersects them with the source monochrome bitmap, then forwards the combined mask to the target.
- `FOR_RUNS` scans tile rows for runs of 1 bits and dispatches color, alpha, and RasterOp copy operations one run at a time.
- `x_offset()` accounts for tile phase, repeat height, and repeat shift.

Operational notes:
- The file favors correctness and simple run scanning over aggressive bit-blit optimization for non-mono operations.
- All forwarded source offsets are adjusted to the clipped run’s `txrun`.
- Uses `gx_no_bitmap_id` when slices no longer correspond to the original bitmap identity.

Filesystem relevance: none directly. It is rendering support for pattern clipping within the Ghostscript banding device stack.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxclip2.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxclip2.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxclip2.h

Header for the tiled mask clipping device.

Defines:
- `gx_device_tile_clip` as a typedef alias for `gx_device_mask_clip`.
- `st_device_tile_clip` as the same structure descriptor as the mask clip device.
- `private_st_device_tile_clip()` as a dummy top-level declaration macro to satisfy Ghostscript’s structure descriptor conventions.

Declares:
- `tile_clip_initialize()` for constructing a tile clipper from a strip bitmap and target device.
- `tile_clip_set_phase()` for changing tile phase during tiling loops.

Filesystem relevance: none directly.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxclip2.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxclipm.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxclipm.c

Implements a mask clipping proxy device. Unlike `gxclip.c`, which clips against rectangle lists, this file clips against a bitmap mask stored in `cdev->tiles`.

Key elements:
- Exports `gs_mask_clip_device`, a `gx_device_mask_clip` descriptor.
- Implements fill, mono/color/alpha copy, strip tile rectangle, strip copy RasterOp, and clipping-box forwarding.
- Uses shared callback functions from `gxclip.c` through `clip_callback_data_t`.

Important algorithms:
- `mask_clip_fill_rectangle()` clips the fill rectangle to mask bounds and forwards it as `copy_mono` through the mask data.
- `FIT_MASK_COPY` computes the intersection between requested device coordinates and the mask coordinate system while adjusting source pointer and `sourcex`.
- `mask_clip_copy_mono()` intersects the source mono bitmap and mask into an internal memory-device buffer, then copies color through the combined mask.
- `clip_runs_enumerate()` scans mask bytes using `byte_bit_run_length` tables, groups adjacent 1-bit runs, and coalesces vertical rectangles with identical X extents before invoking callbacks.

Operational notes:
- The clipping box method subtracts mask phase from the target box but does not intersect with actual mask extents.
- The run enumerator is tuned for compact callback dispatch and avoids per-pixel forwarding.
- The code assumes the mask/tile bitmap and memory buffer are already initialized by `gx_mask_clip_initialize`.

Filesystem relevance: none directly; this is rendering mask infrastructure used by the larger clist/printer path.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxclipm.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxclipm.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxclipm.h

Minimal header for mask clip device definitions.

Includes `gxmclip.h` and declares:
- `extern const gx_device_mask_clip gs_mask_clip_device;`

The actual mask clip structure and initialization helpers live outside this header; this file exposes the device template implemented in `gxclipm.c`.

Filesystem relevance: none directly.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxclipm.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxclipsr.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxclipsr.h

Internal header for clipsave/cliprestore state.

Defines:
- Forward declarations for `gx_clip_path` and `gx_clip_stack_t`.
- `struct gx_clip_stack_s`, containing a reference-count header, a `gx_clip_path *`, and a `next` pointer.
- `private_st_clip_stack()` GC descriptor macro using `gs_private_st_ptrs2`.

Design notes:
- Clip stacks are separate small objects rather than being threaded through graphics-state objects.
- They are reference-counted because off-stack graphics states may share them.

Filesystem relevance: none directly.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxclipsr.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxclist.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxclist.c

Implements document/page-level Ghostscript command-list device logic. A clist records graphics driver calls by band, then later replays them to render banded output for memory-constrained printers/devices.

Key responsibilities:
- Defines `gs_clist_device_procs`, wiring drawing operations to clist writers/readers.
- Provides GC enumeration/relocation for writer-only pointers such as active image clip path, color space, and imager state.
- Initializes buffer partitioning for tile cache, command buffer, band states, and render bands.
- Opens/closes temporary command and block files through the `clist_*` file abstraction.
- Handles page finalization, reset, color-used aggregation, and VM-error recovery.

Important functions:
- `clist_tile_cache_size()` estimates cache space, smaller when halftoning is unnecessary.
- `clist_init_tile_cache()` partitions cache hash table and bitmap chunk.
- `clist_init_bands()` validates render buffer size and computes band count.
- `clist_init_states()` lays out per-band state and command buffer.
- `clist_init_data()`, `clist_reset()`, and `clist_init()` assemble the writer state.
- `clist_open_output_file()` creates command/block clist files and reserves enough low-memory write margin.
- `clist_end_page()` writes end-page command, terminating block entry, computes colors used, and releases reserve memory.
- `clist_VMerror_recover()` and `clist_VMerror_recover_flush()` support partial rendering to free band-list memory.
- `clist_put_current_params()` serializes target device parameters into the clist when pass-through params are disabled.
- `clist_get_band()` reports the band range for a Y coordinate.

Notable behavior:
- `CLIST_IS_WRITER` uses `ymin < 0` to distinguish writer from reader state.
- `clist_output_page()` is fatal; clist output is driven by printer/device code, not by calling the clist device directly.
- `clist_end_page()` accumulates `ecode` internally but returns `0` at the end in this version, so warnings/errors after certain points may not propagate as the comment suggests.
- Low-memory support relies on `free_up_bandlist_memory` and `clist_set_memory_warning`.

Filesystem relevance: high within this group. It is the lifecycle manager for Ghostscript’s temporary band-list “files,” though those may be memory-backed via `gxclmem.c` or real-file-backed via the clist I/O layer.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxclist.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxclist.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxclist.h

Core command-list definitions for Ghostscript banding.

Major concepts:
- A command list is a compressed list of driver calls sorted by affected bands.
- Recording phase writes commands per band; reading phase replays commands band-by-band into bitmap buffers.
- Band-range commands must precede specific-band commands in the write buffer.

Important types:
- `gx_saved_page`: snapshot of device info, page band info, and copy count.
- `gx_placed_page`: saved page plus render offset.
- `tile_hash` and `tile_slot`: bitmap/tile cache metadata, including per-band definition masks.
- `cmd_prefix` and `cmd_list`: buffered command-run linked lists.
- `gx_device_clist_common`: shared writer/reader fields including target, buffer procs, bandlist memory allocator, buffer, tile cache, current band, and page info.
- `gx_device_clist_writer`: writer-only state, including per-band states, command buffer, tile params, imager state, current clip/color space IDs, error recovery fields, and disable mask.
- `gx_device_clist_reader`: reader-only render-plane/page-list state.
- `gx_device_clist`: union of common, writer, and reader views.

Key macros/API:
- `clist_init_params()` initializes a clist device before open.
- Disable flags control path banding, image handling, complex clipping, parameter pass-through, and `copy_alpha`.
- Declares `clist_finish_page`, `clist_close_output_file`, `clist_close_page_info`, `clist_compute_colors_used`, `clist_setup_params`, and `clist_render_rectangle`.

Filesystem relevance: high. It defines the in-memory metadata and public interface for band-list files (`cfname/cfile`, `bfname/bfile`) and page snapshots that can be saved and later rendered.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxclist.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxcllzw.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxcllzw.c

Provides LZW filter prototypes for RAM-based command-list compression.

Key elements:
- Static `stream_LZW_state` instances: `cl_LZWE_state` and `cl_LZWD_state`.
- `gs_cl_lzw_init()` initializes default LZW encode/decode stream states and assigns `s_LZWE_template` / `s_LZWD_template`.
- `clist_compressor_state()` returns the encoder prototype.
- `clist_decompressor_state()` returns the decoder prototype.

These prototypes are copied by `gxclmem.c` when opening memory-backed clist files.

Filesystem relevance: moderate. It supplies compression/decompression state for the memory-file implementation backing band-list data.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxcllzw.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxclmem.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxclmem.c

Implements a RAM-backed file abstraction for Ghostscript command lists. It presents clist file operations over linked memory blocks, with optional LZW compression and decompression caching.

Core data model:
- `LOG_MEMFILE_BLK` is the logical file index block.
- `PHYS_MEMFILE_BLK` stores raw or compressed bytes.
- `RAW_BUFFER` caches decompressed logical blocks.
- `MEMFILE` tracks logical position/length, current block, physical compression state, raw-cache LRU list, reserve blocks for low-memory writes, and stream states.

Main operations:
- `memfile_fopen()` creates a new write-only scratch memory file, initializes logical/physical blocks, allocates compressor/decompressor states, and marks compression enabled.
- `memfile_fclose()` only supports close-with-delete; it frees file blocks, reserves, stream states, and the `MEMFILE`.
- `memfile_unlink()` is unsupported because files have no external name-to-pointer mapping.
- `memfile_set_memory_warning()` preallocates reserve logical/physical blocks so a future write of `bytes_left` can complete after memory becomes low.
- `memfile_fwrite_chars()` writes bytes at the current position, reinitializing the file when writing from offset 0.
- `memfile_fread_chars()` reads bytes from current position, calling `memfile_get_pdata()` when crossing logical blocks.
- `memfile_fseek()`, `memfile_rewind()`, `memfile_ftell()`, and `memfile_ferror_code()` implement positioning/status.

Compression behavior:
- Compression begins after `total_space > COMPRESSION_THRESHOLD` and `ok_to_compress` is true.
- `compress_log_blk()` compresses one full logical block into current physical output, allocating a continuation block if one output block is insufficient.
- `memfile_next_blk()` allocates the next logical block and either starts compression for previous blocks or continues compressing old raw blocks.
- The last logical block remains uncompressed while writing.
- `memfile_get_pdata()` returns raw block data directly or decompresses compressed blocks into an LRU raw-buffer cache.

Memory/error notes:
- `allocateWithReserve()` returns positive status when allocation succeeds from reserve, allowing low-memory warnings.
- Several fatal assumptions are explicit: compression/decompression should not require more than one extra full block.
- `memfile_free_mem()` contains commentary about prior buggy freeing algorithms and uses a corrected two-phase approach for compressed physical chains.
- `memfile_fwrite_chars()` logs but does not implement general truncate-after-middle-write; the comments state clist usage avoids that pattern.
- `FREE` subtracts `sizeof(*(obj))`, which is approximate when reserve physical blocks may be allocated at `max(sizeof(PHYS_MEMFILE_BLK), sizeof(RAW_BUFFER))`.

Filesystem relevance: high. This is a memory-backed substitute for temporary clist files, including seek/read/write semantics, logical block indexing, compression, low-memory reserve handling, and cleanup.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxclmem.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxclmem.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxclmem.h

Defines the RAM-backed clist file structures and maps `memfile_*` APIs to the generic `clist_*` interface.

Key definitions:
- `MEMFILE_DATA_SIZE` is `16384 - 160`, chosen to fit allocator size classes efficiently.
- `RAW_BUFFER`: doubly linked decompression cache entry with one data block.
- `PHYS_MEMFILE_BLK`: allocated physical storage block, raw or compressed.
- `LOG_MEMFILE_BLK`: logical block pointing into physical data and optionally an active raw cache buffer.
- `MEMFILE`: full memory-file state, including allocators, compression flag, reserve block chains/counts, logical position/length, current data pointers, raw-cache list, error code, stream cursors, and compression/decompression stream states.

Macros:
- `private_st_MEMFILE()` declares the GC descriptor for `MEMFILE`, tracing only `compress_state` and `decompress_state`.
- `memfile_fopen`, `memfile_fclose`, `memfile_unlink`, `memfile_fwrite_chars`, `memfile_fread_chars`, etc. alias to the clist file operation names.
- Declares `clist_compressor_state()` and `clist_decompressor_state()`.

Filesystem relevance: high. This header defines the in-memory “file” representation and exposes it through the clist file abstraction.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxclmem.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxclpage.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxclpage.c

Implements saved-page management for banding printer devices.

Key functions:
- `gdev_prn_save_page()` finalizes the current clist page, closes command/block files without deleting them, copies device identity and page info into `gx_saved_page`, clears live file pointers in the saved info, records copy count, then reopens the clist device for a new page.
- `gdev_prn_render_pages()` validates an array of saved pages against the current printer device, attaches the page list to the clist reader, invokes normal `output_page`, and unlinks saved temporary files afterward.

Compatibility checks:
- Device name and `color_info` must match.
- Y offset must currently be zero.
- Saved `BandBufferSpace` must match printer `buffer_space`.
- Saved `BandWidth` must match printer width.
- All pages must share the same `BandHeight`.

Filesystem relevance: high. This file preserves and later deletes temporary clist backing files associated with saved pages.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxclpage.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxclpage.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxclpage.h

Header for command-list saved-page operations.

Declares:
- `gdev_prn_save_page()` to package the current page in a banding device into caller-provided `gx_saved_page` storage.
- `gdev_prn_render_pages()` to render an array of saved/placed pages through a compatible printer device.

Important documented constraints:
- Current page buffers are lost when rendering saved pages.
- Each saved page can be translated to an X/Y offset, but Y offset must currently be zero.
- Rendering device must be the same device type and have compatible buffer size, band width, and band height.

Filesystem relevance: moderate to high. It defines the saved-page API around clist temporary files and page metadata.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxclpage.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxclpath.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxclpath.c

Implements higher-level path operations for Ghostscript command lists: fill paths, stroke paths, polygon fills, CTM/state serialization, drawing-color serialization, clip path serialization, and compact path segment encoding.

Key exported/support functions:
- `cmd_drawing_colors_used()` computes approximate colors-used masks for pure, binary halftone, colored halftone, and other drawing colors.
- `cmd_slow_rop()` determines whether a RasterOp needs full-pixel slow handling.
- `cmd_put_drawing_color()` serializes device colors into extended clist commands, inserting halftones and tile phase updates when needed.
- `cmd_clear_known()` clears per-band known-state flags.
- `cmd_check_clip_path()` tracks clip path identity and updates current pointer.
- `cmd_write_ctm_return_length()` and `cmd_write_ctm()` serialize CTMs through Ghostscript stream matrix helpers.
- `cmd_write_unknown()` emits any imager/clip/color-space state required by a band before a drawing command.
- Device procedures: `clist_fill_path`, `clist_stroke_path`, `clist_fill_parallelogram`, and `clist_fill_triangle`.

State serialization:
- Uses per-band `known` flags from `gxclpath.h` to avoid writing unchanged imager state.
- Serializes miscellaneous parameters through `cmd_opv_set_misc2`, fill adjust, CTM, dash pattern, clip path, and color space.
- Clip paths may be emitted as a rectangle, as a full filled path, as rectangle-list fills, or as the outer box if complex clipping is disabled.
- `end_clip` has special low-memory handling to avoid leaving a dangling `begin_clip`.

Path writing:
- `cmd_put_path()` enumerates path segments and emits compact relative path commands.
- It skips segments wholly outside the current band’s Y range when safe.
- It tracks actual versus emitted path state to preserve closepath behavior after skipped segments.
- It encodes line/curve operands in variable-length fixed-point forms and merges common sequences.
- `cmd_put_segment()` shortens horizontal/vertical lines, merges move+line sequences, detects symmetric curve continuations, and emits segment notes when needed.

Device behavior:
- `clist_fill_path()` computes path Y bounds, updates fill-related state, ensures clipping/logical operation/color are current, then emits per-band path commands.
- `clist_stroke_path()` computes stroke expansion, handles dash pattern limits (`cmd_max_dash`), updates stroke state, and avoids segment skipping when dashes or unknown expansion would make it unsafe.
- Parallelogram/triangle fills build temporary paths; rectangular parallelograms use the faster rectangle path.

Potential hazards:
- `cmd_write_unknown()` returns `0` instead of `code` for one `set_cmd_put_op` failure in the misc2 block, which may mask an error in that branch.
- Complex clipping can be deliberately degraded to the outer box when `clist_disable_complex_clip` is set.
- Dash patterns longer than `cmd_max_dash` fall back to default rendering instead of clist path serialization.

Filesystem relevance: indirect. It defines the high-level serialized commands written into clist command files; those files are managed by `gxclist.c` and backed by file/memory I/O layers.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxclpath.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxclpath.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxclpath.h

Defines command-list extensions and support declarations for higher-level path, image, clipping, and graphics-state commands.

Key flag groups:
- Per-band known-state flags for cap/join, curve/stroke adjustment, flatness, line width, miter limit, operation/blend/text knockout, alpha, fill adjust, CTM, dash, clip path, and color space.
- `misc2_all_known` and `stroke_all_known` aggregate common subsets.

Command definitions:
- `gx_cmd_xop` extends clist command bytes from `0xd0` upward for misc state, color space, dash, clip begin/end, image commands, path segments, fill/stroke/polyfill operations, and extended commands.
- `gx_cmd_ext_op` defines second-byte extended commands for parameter lists, compositor creation, halftones, halftone segments, and serialized drawing colors.
- Segment command names and operand counts are encoded in macros for debug/reader use.

Encoding model:
- Path coordinates are relative `fixed` values with several variable-length encodings.
- `is_bits()` checks whether a fixed value fits in a given signed bit width.
- `cbuf_ht_seg_max_size` reserves command-buffer headroom for halftone segments.

Declared procedures:
- Driver procedures implemented in `gxclpath.c`: `clist_fill_path`, `clist_stroke_path`, `clist_fill_parallelogram`, and `clist_fill_triangle`.
- Support procedures for drawing colors, slow RasterOp detection, known-state clearing, CTM serialization, unknown-state emission, and clip-path checks.

Filesystem relevance: indirect. It defines the serialized command vocabulary written into clist backing storage.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/gxclpath.h -->