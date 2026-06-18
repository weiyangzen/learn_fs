# Group Research: group_1530_plan9_sources_os_plan9_plan9_sys_src_cmd_gs_libpng_pngmem_c_sources_e6c4261fe326

Scope: `Docs/research_subset_a.md`, source tree `sources/os/plan9/plan9`.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/libpng/pngmem.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/libpng/pngmem.c

## Purpose

`pngmem.c` is libpng 1.2.8's centralized memory allocation layer. It provides allocation and free entry points for `png_struct`, `png_info`, generic libpng buffers, overflow-checked memory operations, and optional application-provided allocator hooks.

This is vendored third-party libpng code inside Plan 9's Ghostscript tree, not Plan 9 filesystem logic.

## Main Responsibilities

- Allocate zeroed `png_struct` and `png_info` objects via `png_create_struct()` / `png_create_struct_2()`.
- Free those objects via `png_destroy_struct()` / `png_destroy_struct_2()`.
- Allocate and free generic libpng memory via `png_malloc()`, `png_malloc_default()`, `png_malloc_warn()`, `png_free()`, and `png_free_default()`.
- Support user-defined allocation callbacks when `PNG_USER_MEM_SUPPORTED` is enabled.
- Support legacy 16-bit Borland/DOS memory models, including special handling for 64K zlib allocations.
- Provide overflow-checking wrappers `png_memcpy_check()` and `png_memset_check()`.
- Expose `png_set_mem_fn()` and `png_get_mem_ptr()` for application allocator state.

## Key Control Flow

The file has two major compile-time branches:

- Borland DOS special handler: active for `__TURBOC__ && !defined(_Windows) && !defined(__FLAT__)`.
- Normal handler: used by modern/flat builds, including the expected Plan 9 build path unless these legacy macros are set.

In the normal path:

- `png_create_struct()` delegates to `png_create_struct_2()` when user memory is enabled.
- `png_create_struct_2()` chooses the allocation size from `PNG_STRUCT_INFO` or `PNG_STRUCT_PNG`, then allocates with user malloc, `farmalloc`, `halloc`, or `malloc`, depending on compile-time platform macros.
- `png_malloc()` validates `png_ptr` and size, dispatches to user malloc if present, otherwise calls `png_malloc_default()`.
- `png_malloc_default()` rejects null pointers and zero-size requests, optionally rejects allocations over 64K, checks whether `png_uint_32 size` can fit into the platform allocation type, then allocates.
- `png_free()` dispatches to a user free callback if present, otherwise to `png_free_default()`.
- `png_malloc_warn()` temporarily sets `PNG_FLAG_MALLOC_NULL_MEM_OK` so allocation failure returns `NULL` instead of raising a fatal libpng error.

## Legacy 64K Handling

The Borland-specific path handles a historical zlib issue where exactly 64K allocations may not be returned on a segment boundary. If a 64K allocation cannot be used directly, it allocates a larger table, aligns it, and hands out fixed 64K blocks through `png_ptr->offset_table_ptr`.

This path tracks:

- `offset_table`
- `offset_table_ptr`
- `offset_table_number`
- `offset_table_count`
- `offset_table_count_free`

Freeing one of these special blocks increments the free count; when all handed-out blocks are freed, the backing table and pointer table are released.

## Important Data and Dependencies

Depends on definitions from `png.h`, especially:

- `png_struct`, `png_info`
- `png_malloc_ptr`, `png_free_ptr`
- `PNG_FLAG_MALLOC_NULL_MEM_OK`
- `PNG_MAX_MALLOC_64K`
- `PNG_USER_MEM_SUPPORTED`
- `png_error()`, `png_warning()`
- `png_memset`, `png_memcpy`

The allocator is shared across libpng read, write, transform, chunk, and metadata paths.

## Error Handling

Allocation failures usually call `png_error()` unless `PNG_FLAG_MALLOC_NULL_MEM_OK` is set. `png_malloc_warn()` is the non-fatal allocation helper used by callers that can degrade gracefully.

`png_memcpy_check()` and `png_memset_check()` convert `png_uint_32` lengths to `png_size_t` and raise `png_error()` if the cast truncates, preventing overflow on platforms where `png_size_t` is narrower.

## Notable Observations

- The file is heavily portability-oriented and includes obsolete DOS/Windows memory model support.
- Under the normal `PNG_MAX_MALLOC_64K` / no-user-memory branch, the source contains a syntactically suspicious condition:
  `if(png_ptr->flags&PNG_FLAG_MALLOC_NULL_MEM_OK) == 0)`.
  If that compile-time branch is enabled as-is, it appears malformed.
- The normal allocation path does not zero buffers returned by `png_malloc()`, only structures allocated by `png_create_struct*()`.
- User memory callbacks receive a dummy `png_struct` carrying `mem_ptr` during initial structure creation/destruction before a real `png_struct` exists.

## Research Notes

For callers, the important contract is that all libpng-owned allocations should flow through this file so custom allocators, fatal/nonfatal allocation policy, and platform-specific allocation limits remain consistent.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/libpng/pngmem.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/libpng/pngpread.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/libpng/pngpread.c

## Purpose

`pngpread.c` implements libpng's progressive, push-mode PNG reader. Instead of reading from a blocking stream in one call sequence, the application feeds arbitrary input buffers to libpng with `png_process_data()`, and libpng resumes parsing from its saved state.

This is vendored libpng reader infrastructure inside the Plan 9 Ghostscript source tree.

## Main Responsibilities

- Maintain a push-mode parse state machine.
- Validate the PNG signature incrementally.
- Parse chunk headers only when enough bytes are available.
- Dispatch known PNG chunks to the same handlers used by the sequential reader.
- Buffer incomplete input across application calls.
- Stream IDAT data through zlib and emit rows through callbacks.
- Support progressive callbacks for info, row, and end events.
- Handle progressive text chunks (`tEXt`, `zTXt`, `iTXt`) and unknown chunks.

## State Machine

The file defines push-mode process states:

- `PNG_READ_SIG_MODE`
- `PNG_READ_CHUNK_MODE`
- `PNG_READ_IDAT_MODE`
- `PNG_SKIP_MODE`
- `PNG_READ_tEXt_MODE`
- `PNG_READ_zTXt_MODE`
- `PNG_READ_iTXt_MODE`
- `PNG_READ_DONE_MODE`
- `PNG_ERROR_MODE`

`png_process_data()` restores the current input buffer and repeatedly calls `png_process_some_data()` until no buffered bytes remain.

`png_process_some_data()` dispatches based on `png_ptr->process_mode`.

## Signature and Chunk Parsing

`png_push_read_sig()` accumulates the 8-byte PNG signature in `info_ptr->signature`, comparing only the newly available bytes. It distinguishes non-PNG input from likely ASCII-converted PNG corruption.

`png_push_read_chunk()` reads chunk length and type once at least 8 bytes are available, then dispatches:

- Core chunks: `IHDR`, `PLTE`, `IDAT`, `IEND`
- Ancillary chunks: `gAMA`, `sBIT`, `cHRM`, `sRGB`, `iCCP`, `sPLT`, `tRNS`, `bKGD`, `hIST`, `pHYs`, `oFFs`, `pCAL`, `sCAL`, `tIME`
- Text chunks: `tEXt`, `zTXt`, `iTXt`
- Unknown chunks via `png_push_handle_unknown()`

Before handling most chunks, it checks that chunk payload plus CRC are already buffered; otherwise it saves the buffer and returns.

## IDAT Processing

When `IDAT` is encountered:

- The reader verifies `IHDR` exists.
- Palette images must already have `PLTE`.
- `png_ptr->idat_size` is set from the chunk length.
- `png_ptr->process_mode` switches to `PNG_READ_IDAT_MODE`.
- `png_push_have_info()` invokes the application info callback.
- zlib output is set to the row buffer.

`png_push_read_IDAT()` then consumes IDAT payload from either the saved buffer or the current buffer, updates CRC, and feeds bytes to `png_process_IDAT_data()`.

`png_process_IDAT_data()` inflates with `Z_PARTIAL_FLUSH`, emits complete rows when `avail_out` reaches zero, detects extra compressed data, marks zlib completion, and reports decompression errors.

## Buffer Management

Progressive reading is built around three buffer fields:

- Saved bytes from previous incomplete calls.
- Current application-supplied bytes.
- Combined logical `buffer_size`.

Important helpers:

- `png_push_fill_buffer()` copies requested bytes from saved data first, then current data.
- `png_push_save_buffer()` compacts or grows `save_buffer` and appends any unconsumed current bytes.
- `png_push_restore_buffer()` installs the newest caller-provided buffer.

The save-buffer growth path checks for potential overflow before adding `current_buffer_size + 256`.

## Row Emission and Interlace Handling

`png_push_process_row()` builds `row_info`, applies PNG row filters, copies the row to `prev_row`, applies read transformations, and emits rows through `png_push_have_row()`.

For interlaced images with `PNG_INTERLACE` transformation enabled, the code expands sparse Adam7 pass rows into full display rows and emits `NULL` rows for generated/skipped display positions. `png_read_push_finish_row()` advances row/pass state and recomputes interlace pass width, row byte counts, and number of rows.

## Progressive Text Handling

Text chunks are handled as multi-step progressive modes:

- `png_push_handle_tEXt()` allocates `current_text`, then `png_push_read_tEXt()` fills it across input calls, validates CRC, splits key/text, and calls `png_set_text_2()`.
- `png_push_handle_zTXt()` and `png_push_read_zTXt()` read compressed text, validate compression marker, inflate into a dynamically grown buffer, and then store text metadata.
- `png_push_handle_iTXt()` and `png_push_read_iTXt()` parse international text fields: keyword, compression flag/type, language, translated keyword, and text.

For `PNG_MAX_MALLOC_64K`, large text chunks are either truncated/skipped or rejected depending on chunk type.

## Unknown Chunk Handling

`png_push_handle_unknown()` validates the chunk name, errors on unhandled unknown critical chunks, optionally stores unknown chunks when configured, invokes user unknown-chunk callbacks, then skips remaining bytes through `png_push_crc_skip()`.

`png_push_crc_finish()` consumes skipped data while updating CRC and returns to chunk mode after CRC validation.

## Callback API

- `png_set_progressive_read_fn()` sets `info_fn`, `row_fn`, and `end_fn`, then routes read I/O through `png_push_fill_buffer`.
- `png_get_progressive_ptr()` returns `png_ptr->io_ptr`.
- `png_progressive_combine_row()` combines an incoming interlace row into an old row using the pass display mask.

## Research Notes

The file mirrors much of the sequential reader logic but adds explicit resumability. The core invariant is that chunk handlers are called only after the complete chunk body plus CRC is present, except IDAT and progressive text modes, which have dedicated incremental paths.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/libpng/pngpread.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/libpng/pngread.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/libpng/pngread.c

## Purpose

`pngread.c` implements libpng's normal sequential read API. It creates and initializes read structures, reads PNG metadata and image rows, reads trailing chunks, and destroys read-time state.

This is third-party libpng 1.2.8 code vendored in the Plan 9 Ghostscript source tree.

## Main Responsibilities

- Create and initialize `png_struct` for reading.
- Validate application/libpng version compatibility.
- Initialize zlib inflate state and read function pointers.
- Read PNG signature and pre-IDAT metadata chunks.
- Read individual rows, row arrays, or full images.
- Read trailing post-IDAT chunks through `png_read_end()`.
- Free all read-side allocations and reset state.
- Provide convenience API `png_read_png()`.

## Construction and Initialization

`png_create_read_struct()` optionally delegates to `png_create_read_struct_2()` when custom memory callbacks are enabled.

Initialization flow:

- Allocate `png_struct`.
- Initialize optional MMX flags.
- Set user width/height limits when configured.
- Set error and warning handlers.
- Compare `user_png_ver` with `png_libpng_ver`.
- Allocate `zbuf`.
- Set zlib alloc/free callbacks to `png_zalloc` and `png_zfree`.
- Call `inflateInit()`.
- Initialize `zstream.next_out` and `zstream.avail_out`.
- Set default read function via `png_set_read_fn()`.

Deprecated initialization entry points `png_read_init()`, `png_read_init_2()`, and `png_read_init_3()` exist for old applications. They preserve the jump buffer, reset the struct, rebuild zlib state, and warn/error on incompatible struct sizes.

## Metadata Read Path

`png_read_info()`:

- Reads any remaining PNG signature bytes.
- Validates signature and ASCII-conversion corruption.
- Loops over chunks until it reaches `IDAT`.
- Reads chunk length and type, resets CRC, then dispatches to chunk handlers.
- Enforces `IHDR` before `IDAT` and `PLTE` before `IDAT` for palette images.
- Supports known ancillary chunks and unknown-chunk policy.
- Stores first IDAT length in `png_ptr->idat_size` and marks `PNG_HAVE_IDAT`.

Chunk dispatch is a linear chain of `png_memcmp()` checks.

## Row Read Path

`png_read_row()` is the core sequential image decoder.

Key steps:

- Lazily initializes row buffers with `png_read_start_row()`.
- Warns if transformations were requested but not compiled in.
- Handles interlace display rows that do not require a new compressed row.
- Validates that IDAT has been reached.
- Refills zlib input from IDAT chunks into `zbuf`.
- Validates each IDAT CRC before moving to the next chunk.
- Inflates until a full row is available.
- Detects extra compressed data or decompression errors.
- Builds `row_info`.
- Applies PNG row filters if needed.
- Copies current row to `prev_row`.
- Applies optional MNG intrapixel differencing.
- Applies read transformations through `png_do_read_transformations()`.
- Combines rows for interlaced or non-interlaced output.
- Calls `png_read_finish_row()` and optional row status callback.

`png_read_rows()` iterates `png_read_row()` over caller-supplied row/display-row pointer arrays.

`png_read_image()` reads an entire image, calling `png_set_interlace_handling()` when available and looping over passes and rows.

## End Chunk Handling

`png_read_end()` finishes the last IDAT CRC and scans chunks until `IEND`.

It handles:

- `IEND`
- zero-length trailing IDAT legality
- duplicate/nonzero IDAT errors after image data
- known ancillary chunks
- unknown chunks according to configured policy

This function is required by the higher-level `png_read_png()` path to collect trailing metadata.

## Destruction

`png_destroy_read_struct()` coordinates teardown for `png_struct`, `info_ptr`, and `end_info_ptr`, preserving custom memory free callbacks long enough to destroy all objects.

`png_read_destroy()` frees:

- zlib buffer
- row buffers
- previous row
- dithering lookup tables
- gamma tables
- background gamma tables
- palette/transparency/histogram allocations depending on ownership flags
- RFC1123 time buffer
- progressive save buffer and current text state
- zlib inflate state

It then preserves error/warning callbacks and jump buffer, clears `png_struct`, and restores those preserved fields.

## Convenience API

`png_read_png()` performs an all-in-one read:

- Calls `png_read_info()`.
- Applies requested transform flags.
- Updates info through `png_read_update_info()`.
- Allocates `info_ptr->row_pointers` and row buffers if absent.
- Reads the full image.
- Marks `PNG_INFO_IDAT`.
- Calls `png_read_end()`.

It explicitly does not handle background color, gamma transformation, dithering, or filler insertion in the simplified transform switch.

## Research Notes

This file is the sequential counterpart to `pngpread.c`. It owns the blocking stream-oriented read lifecycle and relies on other libpng modules for chunk-specific handling, transformations, row setup, row finishing, filtering, CRC, and I/O.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/libpng/pngread.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/libpng/pngrio.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/libpng/pngrio.c

## Purpose

`pngrio.c` centralizes libpng read input. It provides the internal `png_read_data()` dispatcher, the default stdio/WinCE read implementation, legacy far-buffer support, and the public `png_set_read_fn()` hook for custom input sources.

This is vendored libpng I/O glue inside Plan 9 Ghostscript sources.

## Main Responsibilities

- Route all read requests through `png_ptr->read_data_fn`.
- Provide a default reader based on `fread()` or WinCE `ReadFile()`.
- Fail with `png_error()` on short reads or missing read callbacks.
- Support old memory models where far buffers must be copied through a near temporary buffer.
- Install custom read callbacks and clear conflicting write callbacks.

## Key Functions

`png_read_data(png_ptr, data, length)`:

- Logs a debug read size.
- Calls `png_ptr->read_data_fn`.
- Raises `png_error()` if the callback is `NULL`.

`png_default_read_data()`:

- When stdio is enabled, reads from `png_ptr->io_ptr`.
- Uses `ReadFile()` on `_WIN32_WCE`.
- Uses `fread()` otherwise.
- Requires the exact requested byte count.
- Raises `png_error()` on short read.

Legacy `USE_FAR_KEYWORD` variant:

- Converts far pointers when possible.
- If the target data pointer cannot be used directly by stdio, reads chunks into a 1024-byte near stack buffer and copies into the target.
- Checks total bytes read against requested length.

`png_set_read_fn(png_ptr, io_ptr, read_data_fn)`:

- Stores caller I/O state in `png_ptr->io_ptr`.
- Installs caller read callback, or default stdio reader when available and callback is `NULL`.
- If a write callback was already set on the same structure, clears it and warns because a `png_struct` must not be both read and write I/O.
- Clears output flush callback when write flush support is compiled.

## Dependencies

Uses definitions and callbacks from `png.h`:

- `png_structp`
- `png_rw_ptr`
- `png_FILE_p`
- `png_error()`
- `png_warning()`
- `png_memcpy()`
- platform conversion macros for far pointers

## Error Handling

Read failure is fatal. Callers using custom read functions are expected to call `png_error()` themselves when they cannot satisfy a read. The default implementation enforces exact-length reads.

## Research Notes

This file is intentionally narrow. Higher-level readers (`pngread.c` and `pngpread.c`) rely on this file so that libpng can be used over files, memory buffers, network streams, or application-specific stream abstractions without changing decode logic.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/libpng/pngrio.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/libpng/pngrtran.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/libpng/pngrtran.c

## Purpose

`pngrtran.c` implements libpng reader-side transformations. Applications configure desired output behavior before reading image rows, and this file updates metadata, precomputes tables, and rewrites decompressed rows in place.

This is libpng 1.2.8 third-party image transformation code vendored under Plan 9's Ghostscript tree.

## Main Responsibilities

- Configure read transformations requested by applications.
- Configure CRC handling policy.
- Initialize background, gamma, palette, and dithering state before row reads.
- Update `png_info` to reflect transformed output format.
- Apply transformation pipeline to each decoded row.
- Implement individual pixel/row transformations for packing, expansion, alpha, gamma, background, color conversion, dithering, and MNG intrapixel undo.

## Public Configuration Functions

Important API entry points include:

- `png_set_crc_action()`: selects behavior for critical and ancillary CRC errors.
- `png_set_background()`: enables alpha/tRNS compositing over a supplied background and records background gamma type.
- `png_set_strip_16()`: converts 16-bit samples to 8-bit.
- `png_set_strip_alpha()`: drops alpha channels.
- `png_set_dither()`: configures palette reduction/dither lookup tables.
- `png_set_gamma()`: enables gamma correction when file/screen gamma require it.
- `png_set_expand()`, `png_set_palette_to_rgb()`, `png_set_gray_1_2_4_to_8()`, `png_set_tRNS_to_alpha()`: enable expansion transformations.
- `png_set_gray_to_rgb()`: expands grayscale to RGB.
- `png_set_rgb_to_gray()` / `_fixed()`: converts RGB to grayscale with configurable coefficients and warning/error behavior.
- `png_set_read_user_transform_fn()`: registers a user row transform callback when compiled in.
- `png_build_grayscale_palette()`: builds a grayscale palette for a given bit depth.

## Initialization

`png_init_read_transformations()` prepares transform state before row decoding.

It can:

- Expand background colors from low-bit grayscale or palette index form.
- Invert palette transparency if alpha inversion is requested before expansion.
- Preserve `background_1` for linear-gamma compositing.
- Disable gamma transformation for palette images with only fully transparent/opaque tRNS entries when file and screen gamma are effectively reciprocal.
- Build gamma tables.
- Pre-apply gamma/background transformations to palette entries.
- Shift palette entries according to significant-bit metadata.

`png_read_transform_info()` updates `info_ptr` metadata so callers see the transformed output layout. It adjusts color type, bit depth, alpha presence, channels, pixel depth, and rowbytes after requested transforms.

## Row Transformation Pipeline

`png_do_read_transformations()` applies row operations in a deliberately ordered sequence:

1. Expand palette/low-bit/tRNS data.
2. Strip alpha if requested.
3. Convert RGB to grayscale.
4. Convert grayscale to RGB early if needed for non-gray background compositing.
5. Composite alpha or transparency against background.
6. Apply gamma correction when not already handled during background compositing.
7. Chop 16-bit samples to 8-bit.
8. Dither to palette.
9. Invert monochrome.
10. Unshift significant bits.
11. Unpack low-bit samples.
12. Convert RGB byte order to BGR.
13. Swap packed bit order.
14. Convert grayscale to RGB late when background is gray.
15. Add filler bytes.
16. Invert alpha.
17. Swap alpha channel position.
18. Swap byte order for 16-bit samples.
19. Run a user transform callback and update row metadata.

The comments warn that this order is sensitive.

## Individual Transform Implementations

The file implements many in-place row transforms:

- `png_do_unpack()`: expands 1/2/4-bit packed samples into one byte per pixel.
- `png_do_unshift()`: shifts samples back to significant-bit ranges.
- `png_do_chop()`: reduces 16-bit samples to 8-bit, optionally using an accurate scale approximation.
- `png_do_read_swap_alpha()`: converts RGBA to ARGB and GA to AG for 8-bit and 16-bit rows.
- `png_do_read_invert_alpha()`: changes alpha convention by subtracting alpha bytes from max.
- `png_do_read_filler()`: inserts filler before or after grayscale/RGB samples.
- `png_do_gray_to_rgb()`: expands gray/gray-alpha rows to RGB/RGBA.
- `png_do_rgb_to_gray()`: computes grayscale from RGB/RGBA using integer coefficients, optionally with gamma tables.
- `png_do_background()`: composites tRNS or alpha over a background for grayscale, RGB, gray-alpha, and RGBA at multiple bit depths.
- `png_do_gamma()`: applies gamma tables to color channels while skipping alpha.
- `png_do_expand_palette()`: expands palette indices to RGB/RGBA using palette and tRNS arrays.
- `png_do_expand()`: expands low-bit grayscale to 8-bit and expands tRNS into alpha for gray/RGB rows.
- `png_do_dither()`: maps RGB/RGBA rows to palette indices or remaps existing palette indices.
- `png_do_read_intrapixel()`: undoes MNG intrapixel differencing for RGB/RGBA rows.

## Dithering and Palette Reduction

`png_set_dither()` has two paths:

- With histogram data, it removes least-used palette entries and builds remapping tables.
- Without histogram data, it repeatedly finds close color pairs and eliminates colors until the palette fits `maximum_colors`.

For full RGB dithering, it builds a reduced color-cube lookup table using `PNG_DITHER_RED_BITS`, `PNG_DITHER_GREEN_BITS`, and `PNG_DITHER_BLUE_BITS`.

Temporary structures include `dither_sort`, `dither_index`, `palette_lookup`, `index_to_palette`, and `palette_to_index`.

## Gamma Tables

`png_build_gamma_table()` builds 8-bit or segmented 16-bit lookup tables.

For 8-bit input it can allocate:

- `gamma_table`
- `gamma_to_1`
- `gamma_from_1`

For 16-bit input it segments tables by `gamma_shift` so each allocation stays below historical 64K constraints:

- `gamma_16_table`
- `gamma_16_to_1`
- `gamma_16_from_1`

The function accounts for significant bits and for future 16-to-8 reduction to reduce table size.

## Background Compositing

`png_do_background()` is one of the largest routines in the file. It handles:

- Low-bit grayscale tRNS replacement.
- 8-bit and 16-bit grayscale tRNS replacement.
- 8-bit and 16-bit RGB tRNS replacement.
- Gray-alpha compositing to gray.
- RGBA compositing to RGB.
- Optional gamma-aware compositing using linearized gamma tables.

After compositing alpha-bearing rows, it removes the alpha channel and updates row metadata.

## Notable Observations

- The code is very compile-time-feature driven; many functions only exist when corresponding `PNG_READ_*_SUPPORTED` macros are enabled.
- Most transforms mutate the row buffer in place and update `row_info` immediately.
- Many operations work backwards from the end of the row when expanding data to avoid overwriting unread source bytes.
- The transform code assumes row buffers have already been allocated large enough for the maximum transformed row size by row setup logic elsewhere.
- `png_correct_palette()` is marked as currently unused but remains available under `PNG_READ_DITHER_SUPPORTED && PNG_CORRECT_PALETTE_SUPPORTED`.

## Research Notes

This file is the main reader-side pixel conversion engine. Sequential and progressive readers both call into it after row filtering, so behavioral changes here affect all libpng read modes in this vendored tree.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/libpng/pngrtran.c -->