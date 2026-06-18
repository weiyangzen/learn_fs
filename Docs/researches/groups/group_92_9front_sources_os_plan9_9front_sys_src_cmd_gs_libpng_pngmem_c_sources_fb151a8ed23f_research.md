# Group Research: group_92_9front_sources_os_plan9_9front_sys_src_cmd_gs_libpng_pngmem_c_sources_fb151a8ed23f

Scope checked against `Docs/research_subset_a.md`: all files are under `sources/os/plan9/9front`, which is included in subset A. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/libpng/pngmem.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/libpng/pngmem.c

## Role

`pngmem.c` centralizes libpng 1.2.8 memory allocation for the bundled Ghostscript/libpng copy in the 9front source tree. It provides allocation, deallocation, overflow-checked memory helper wrappers, and optional user-provided allocator hooks.

## Main APIs and Behavior

- `png_create_struct()` / `png_create_struct_2()` allocate and zero either `png_struct` or `png_info`.
- `png_destroy_struct()` / `png_destroy_struct_2()` free structs allocated by the create helpers.
- `png_malloc()` delegates to a custom allocator when `PNG_USER_MEM_SUPPORTED` is enabled, otherwise falls back to `png_malloc_default()`.
- `png_malloc_default()` handles standard allocation and platform-specific variants:
  - Borland DOS `farmalloc` / `farfree`.
  - MSVC `halloc` / `hfree` under `MAXSEG_64K`.
  - normal `malloc` / `free`.
- `png_free()` delegates to custom `free_fn` when present.
- `png_malloc_warn()` temporarily allows allocation failure to return `NULL` with warning behavior instead of fatal `png_error`.
- `png_memcpy_check()` and `png_memset_check()` guard 32-bit `png_uint_32` lengths against truncation to `png_size_t`.
- `png_set_mem_fn()` and `png_get_mem_ptr()` expose user allocator state when enabled.

## Notable Implementation Details

This file has a large legacy Borland 16-bit DOS branch. It special-cases exact 64 KiB allocation because old segmented memory allocators could return non-normalized pointers that zlib could not use. That branch maintains an `offset_table` inside `png_struct` and hands out fixed 64 KiB blocks from it.

The normal branch is much simpler: it validates `png_ptr`, rejects zero-size allocation, checks representability of `png_uint_32 size` in the platform allocation type, allocates memory, and raises `png_error` unless `PNG_FLAG_MALLOC_NULL_MEM_OK` is set.

## Dependencies

- Public/internal libpng declarations from `png.h`.
- C runtime allocation APIs.
- Platform-specific memory APIs controlled by compile-time macros.
- `png_error()` / `png_warning()` for fatal and nonfatal allocator failures.

## State Mutated

- `png_ptr->mem_ptr`, `malloc_fn`, `free_fn` for custom allocation.
- `png_ptr->flags` temporarily in `png_malloc_warn()`.
- Borland branch fields: `offset_table`, `offset_table_ptr`, `offset_table_number`, `offset_table_count`, `offset_table_count_free`.

## Risks and Maintenance Notes

- This is old libpng 1.2.8 allocation code with many legacy platform branches that are likely irrelevant on Plan 9/9front but still affect portability if macros change.
- The `PNG_MAX_MALLOC_64K` path in the normal branch contains a suspicious conditional spelling: `if(png_ptr->flags&PNG_FLAG_MALLOC_NULL_MEM_OK) == 0)`. If that preprocessor path is enabled, it appears syntactically invalid as read.
- User allocator hooks must match libpng’s expectations exactly; allocation failure can be fatal depending on flags.
- `png_malloc_warn()` assumes `png_ptr` is valid and directly reads/writes `png_ptr->flags`.

## Research Summary

This file is the allocator substrate for all read/transform files in this group. The rest of the reader relies on these wrappers for row buffers, zlib buffers, text chunks, gamma tables, palette lookup tables, and progressive-save buffers.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/libpng/pngmem.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/libpng/pngpread.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/libpng/pngpread.c

## Role

`pngpread.c` implements progressive, push-mode PNG reading for libpng 1.2.8. Instead of pulling from a file stream, callers feed arbitrary byte buffers via `png_process_data()`, and this file preserves partial state across calls until enough data exists to parse signatures, chunks, IDAT streams, rows, text chunks, and end markers.

## Main APIs and Behavior

- `png_process_data()` appends/restores the caller-provided input buffer and repeatedly processes available data.
- `png_process_some_data()` dispatches by `png_ptr->process_mode`.
- `png_push_read_sig()` reads and validates the PNG signature incrementally.
- `png_push_read_chunk()` parses chunk headers and dispatches known chunks:
  - Critical: `IHDR`, `PLTE`, `IDAT`, `IEND`.
  - Ancillary: `gAMA`, `sBIT`, `cHRM`, `sRGB`, `iCCP`, `sPLT`, `tRNS`, `bKGD`, `hIST`, `pHYs`, `oFFs`, `pCAL`, `sCAL`, `tIME`, `tEXt`, `zTXt`, `iTXt`, plus unknown chunks.
- `png_push_read_IDAT()` consumes IDAT chunk data progressively, calculates CRC, and feeds compressed bytes to zlib.
- `png_process_IDAT_data()` runs `inflate()` and emits complete rows.
- `png_push_process_row()` filters, copies, transforms, interlace-expands, and emits row callbacks.
- `png_read_push_finish_row()` advances row/pass counters for Adam7 interlacing.
- `png_push_handle_tEXt()`, `png_push_read_tEXt()`, `png_push_handle_zTXt()`, `png_push_read_zTXt()`, `png_push_handle_iTXt()`, and `png_push_read_iTXt()` handle progressive text chunks.
- `png_push_handle_unknown()` handles unknown critical/ancillary chunks and optional user callbacks.
- `png_set_progressive_read_fn()` installs progressive info, row, and end callbacks.
- `png_progressive_combine_row()` lets applications combine interlaced rows into an existing output row.

## Progressive Buffer Model

The file maintains two input regions:

- `current_buffer`: bytes from the most recent caller buffer.
- `save_buffer`: previously received bytes that were insufficient to finish a parse step.

Core helpers:

- `png_push_fill_buffer()` copies requested bytes from saved/current buffers and advances buffer pointers.
- `png_push_save_buffer()` compacts saved bytes, grows `save_buffer` when needed, copies remaining current bytes into it, and marks current input consumed.
- `png_push_restore_buffer()` initializes buffer pointers for a new `png_process_data()` call.

This is the core mechanism that lets chunk headers, CRC tails, and text payloads span caller buffer boundaries.

## IDAT and Row Flow

Once `IDAT` is found:

1. `png_push_read_chunk()` validates `IHDR`/`PLTE` ordering.
2. It sets `idat_size`, marks `PNG_HAVE_IDAT`, switches to `PNG_READ_IDAT_MODE`, calls the info callback, and primes zlib output to `row_buf`.
3. `png_push_read_IDAT()` consumes compressed data from saved/current buffers, updates CRC, and calls `png_process_IDAT_data()`.
4. `png_process_IDAT_data()` inflates until a row is complete or input is exhausted.
5. `png_push_process_row()` applies PNG filtering, copies `row_buf` to `prev_row`, applies read transformations, handles interlace expansion, and invokes the row callback.

## Dependencies

- Chunk handlers from the broader libpng reader (`png_handle_IHDR`, `png_handle_PLTE`, etc.).
- CRC helpers: `png_reset_crc`, `png_crc_read`, `png_crc_finish`, `png_calculate_crc`.
- zlib `inflate()` and `inflateReset()`.
- Transform helpers from `pngrtran.c`, especially `png_do_read_transformations()` and `png_do_read_interlace()`.
- User callback fields in `png_struct`.

## State Mutated

- `process_mode`, `mode`, `flags`.
- `buffer_size`, `current_buffer_*`, `save_buffer_*`.
- `push_length`, `skip_length`, `idat_size`.
- zlib stream fields.
- row state: `row_number`, `pass`, `iwidth`, `irowbytes`, `num_rows`, `row_info`.
- text state: `current_text`, `current_text_ptr`, `current_text_size`, `current_text_left`.

## Risks and Maintenance Notes

- The push parser is stateful and sensitive to exact buffer accounting. Any change to `buffer_size`, `save_buffer_size`, or `current_buffer_size` must preserve all three invariants.
- `png_push_save_buffer()` grows the saved buffer with overflow protection against `PNG_SIZE_MAX`, which is important for adversarial chunk boundaries.
- Signature validation contains a legacy branch using `num_to_check - 4`; behavior should be reviewed carefully if extremely small progressive buffers are expected.
- Text chunk handling allocates full chunk buffers before parsing. Large text chunks are only constrained under `PNG_MAX_MALLOC_64K`.
- `zTXt` decompression repeatedly reallocates and copies accumulated text, which is simple but can be expensive for large compressed text.
- Unknown critical chunks are fatal unless configured/user-handled.

## Research Summary

This file is the asynchronous counterpart to `pngread.c`. It implements the same PNG parse semantics but breaks every operation into resumable states, with callbacks for info, rows, and end-of-image.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/libpng/pngpread.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/libpng/pngread.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/libpng/pngread.c

## Role

`pngread.c` implements the public sequential PNG read API for libpng 1.2.8. It creates and initializes read structs, reads metadata chunks, reads image rows from IDAT data, reads trailing chunks, and destroys read-side allocations.

## Main APIs and Behavior

- `png_create_read_struct()` / `png_create_read_struct_2()` allocate `png_struct`, set error/memory hooks, check libpng version compatibility, allocate the zlib buffer, initialize inflate state, and install default read I/O.
- Deprecated initialization compatibility:
  - `png_read_init()`
  - `png_read_init_2()`
  - `png_read_init_3()`
- `png_read_info()` validates the PNG signature and reads chunks until the first `IDAT`.
- `png_read_update_info()` initializes rows if needed and updates `info_ptr` to reflect configured transformations.
- `png_start_read_image()` ensures row state is initialized before row reads.
- `png_read_row()` reads one image row:
  - Handles interlace skip/combine behavior.
  - Pulls IDAT data into `zbuf`.
  - Runs `inflate()`.
  - Applies PNG row filters.
  - Copies current row to `prev_row`.
  - Applies optional MNG intrapixel differencing.
  - Applies read transformations.
  - Combines interlaced rows into caller buffers.
  - Calls optional row status callback.
- `png_read_rows()` reads multiple rows.
- `png_read_image()` reads the full image, including all interlace passes if enabled.
- `png_read_end()` consumes chunks after image data through `IEND`.
- `png_destroy_read_struct()` frees `png_struct`, `info_ptr`, and optional end-info.
- `png_read_destroy()` frees read-side internal allocations and resets preserved error/jump state.
- `png_set_read_status_fn()` installs a per-row status callback.
- `png_read_png()` is a convenience wrapper that reads the whole PNG into `info_ptr->row_pointers` after applying selected simple transforms.

## Chunk Flow

`png_read_info()` reads the signature, then loops over chunk length/name pairs. It dispatches known chunks by linear name comparison and stops at the first `IDAT`, after validating required ordering:

- `IHDR` must precede `IDAT`.
- Palette images require `PLTE` before `IDAT`.
- Unknown chunks are delegated to unknown-chunk handling, including user callbacks when enabled.

`png_read_end()` finishes the last IDAT CRC, then reads trailing chunks until `IEND`. Nonzero IDAT data after image completion is rejected.

## Row Decode Flow

`png_read_row()` is the sequential row pipeline:

1. Ensure row buffers are initialized.
2. Skip or combine Adam7 rows that do not need fresh compressed data.
3. Ensure current chunk is IDAT.
4. Read compressed bytes into `zbuf`, with CRC accounting.
5. Inflate into `row_buf`.
6. Decode PNG row filter using `prev_row`.
7. Save current row as previous row.
8. Apply MNG intrapixel reversal if configured.
9. Apply read transformations from `pngrtran.c`.
10. Interlace-combine into caller buffers.
11. Advance row/pass state.

## Dependencies

- `pngrio.c` for `png_read_data()` and default/custom read callbacks.
- `pngmem.c` allocation wrappers.
- zlib inflate APIs.
- Chunk handlers from other libpng files.
- Row filtering and interlace helpers.
- Transform implementation from `pngrtran.c`.
- Error handling with `setjmp` when enabled.

## State Mutated

- `png_ptr` lifecycle fields, error handlers, memory handlers, jump buffer.
- zlib state: `zstream`, `zbuf`, `zbuf_size`.
- read flags/modes: `PNG_HAVE_IDAT`, `PNG_AFTER_IDAT`, `PNG_HAVE_IEND`, etc.
- row state: `row_buf`, `big_row_buf`, `prev_row`, `row_number`, `pass`, `num_rows`.
- transform-related state via calls to transform setup/update functions.
- `info_ptr` metadata and row pointers in `png_read_png()`.

## Cleanup Coverage

`png_read_destroy()` frees:

- zlib buffer.
- big row buffer and previous row.
- dither lookup/index tables.
- gamma tables.
- background gamma tables.
- owned palette, transparency, histogram.
- RFC1123 time buffer.
- progressive save buffer and current text.
- zlib inflate state.

It then zeroes `png_struct` while preserving error functions, warning functions, error pointer, free function, and jump buffer.

## Risks and Maintenance Notes

- The API relies on longjmp-style fatal error handling when `PNG_SETJMP_SUPPORTED` is enabled.
- `png_destroy_read_struct()` stores `png_ptr->free_fn` and `png_ptr->mem_ptr` under `PNG_USER_MEM_SUPPORTED`, so callers must not pass a null `png_ptr` through that path.
- Chunk dispatch is intentionally linear and old-style; comments note a hash or binary search would be better.
- The row path is tightly coupled to transform order and row buffer sizing initialized elsewhere.
- `png_read_png()` allocates all rows and can reject very tall images only with a height * pointer-size overflow check; memory pressure is otherwise handled by allocator failure paths.

## Research Summary

This file is the normal pull-mode reader. It wires together I/O, chunk parsing, zlib decompression, row filtering, transformation, interlace handling, full-image convenience loading, and read-side cleanup.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/libpng/pngread.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/libpng/pngrio.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/libpng/pngrio.c

## Role

`pngrio.c` implements libpng’s read I/O abstraction. It provides the internal read dispatcher, default stdio-based reading, and the public hook for applications to install custom input callbacks.

## Main APIs and Behavior

- `png_read_data()` is the internal read entry point. It calls `png_ptr->read_data_fn` and raises `png_error()` if no read function is installed.
- `png_default_read_data()` is compiled when stdio support is present:
  - Uses `fread()` for normal platforms.
  - Uses `ReadFile()` on `_WIN32_WCE`.
  - Has a `USE_FAR_KEYWORD` variant that stages reads through a near buffer for old memory models.
- `png_set_read_fn()` installs a caller-provided `io_ptr` and read callback.
  - If stdio is enabled and `read_data_fn` is `NULL`, it installs `png_default_read_data`.
  - If stdio is disabled, it accepts the supplied callback directly.
  - It clears any write callback because a single `png_struct` cannot be both read and write configured.
  - It clears the flush callback when write flushing support exists.

## Dependencies

- `png.h` internal declarations.
- C stdio unless `PNG_NO_STDIO` is defined.
- Windows CE `ReadFile()` under `_WIN32_WCE`.
- libpng error/warning helpers.

## State Mutated

- `png_ptr->io_ptr`.
- `png_ptr->read_data_fn`.
- `png_ptr->write_data_fn` cleared when conflicting.
- `png_ptr->output_flush_fn` cleared when applicable.

## Risks and Maintenance Notes

- The default reader treats short reads as fatal `png_error("Read Error")`.
- Custom read callbacks must exactly fill the requested length or report errors through `png_error()`.
- `png_read_data()` can be called with small lengths, so unbuffered custom readers may perform poorly unless they add buffering.
- The file deliberately keeps I/O policy isolated from parsing logic in `pngread.c` and `pngpread.c`.

## Research Summary

This is a small but central indirection layer. All sequential parsing ultimately reads through this callback path, while progressive mode installs `png_push_fill_buffer()` as a synthetic read function.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/libpng/pngrio.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/libpng/pngrtran.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/libpng/pngrtran.c

## Role

`pngrtran.c` implements read-side PNG transformation setup and row mutation for libpng 1.2.8. Applications call public setters before reading rows; this file records requested transformations, updates metadata, builds lookup tables, and applies in-place transformations to each decoded row.

## Public Transform Setters

- `png_set_crc_action()` configures CRC behavior for critical and ancillary chunks.
- `png_set_background()` configures alpha/tRNS compositing against a background color.
- `png_set_strip_16()` requests 16-bit samples be reduced to 8-bit.
- `png_set_strip_alpha()` requests alpha removal.
- `png_set_dither()` configures palette reduction or RGB-to-palette lookup tables.
- `png_set_gamma()` configures screen/file gamma correction.
- `png_set_expand()`, `png_set_palette_to_rgb()`, `png_set_gray_1_2_4_to_8()`, and `png_set_tRNS_to_alpha()` all set expansion behavior.
- `png_set_gray_to_rgb()` requests grayscale expansion to RGB.
- `png_set_rgb_to_gray()` / `png_set_rgb_to_gray_fixed()` configure RGB-to-gray conversion and coefficients.
- `png_set_read_user_transform_fn()` installs an application-defined row transform.

## Initialization and Metadata

- `png_init_read_transformations()` prepares transformation state before row decoding:
  - Expands background colors for low-bit-depth gray or palette inputs.
  - Optionally inverts tRNS alpha before expansion.
  - Builds gamma tables when needed.
  - Applies background/gamma corrections to palettes.
  - Shifts palette entries according to significant-bit metadata.
- `png_read_transform_info()` mutates `info_ptr` to match post-transform row format:
  - Color type changes.
  - Bit depth changes.
  - Channel count changes.
  - Pixel depth and rowbytes recalculation.
  - User transform depth/channel overrides.

## Per-Row Transform Pipeline

`png_do_read_transformations()` applies transformations in a carefully ordered sequence:

1. Expand palette/low-bit-depth/tRNS.
2. Strip alpha.
3. RGB-to-gray.
4. Gray-to-RGB before background only when background is non-gray.
5. Background compositing.
6. Gamma correction when not already handled by background.
7. 16-to-8 reduction.
8. Dithering.
9. Monochrome inversion.
10. Significant-bit unshift.
11. Packed-pixel unpacking.
12. BGR conversion.
13. Pack bit-order swap.
14. Gray-to-RGB after background when background is gray.
15. Filler channel insertion.
16. Alpha inversion.
17. Alpha-position swap.
18. Byte swap.
19. User transform callback and row metadata update.

The comments emphasize that this ordering is significant and fragile.

## Internal Row Helpers

- `png_do_unpack()` expands 1/2/4-bit samples into one byte per pixel.
- `png_do_unshift()` shifts samples down to significant bits.
- `png_do_chop()` converts 16-bit samples to 8-bit, optionally with accurate scaling.
- `png_do_read_swap_alpha()` converts RGBA/GA layout to ARGB/AG-style ordering.
- `png_do_read_invert_alpha()` inverts alpha values.
- `png_do_read_filler()` inserts filler bytes/words before or after gray/RGB samples.
- `png_do_gray_to_rgb()` expands gray or gray-alpha rows to RGB/RGBA.
- `png_do_rgb_to_gray()` collapses RGB/RGBA to gray/gray-alpha using configured coefficients, optionally in linear gamma space.
- `png_build_grayscale_palette()` builds synthetic gray palettes.
- `png_correct_palette()` conditionally applies gamma/background correction to palettes.
- `png_do_background()` composites transparency/alpha against configured background for gray, RGB, gray-alpha, and RGBA rows.
- `png_do_gamma()` applies gamma lookup tables to non-alpha samples.
- `png_do_expand_palette()` expands indexed rows to RGB or RGBA.
- `png_do_expand()` expands low-bit-depth gray and converts tRNS to alpha.
- `png_do_dither()` maps RGB/RGBA/palette rows to a reduced palette.
- `png_build_gamma_table()` builds 8-bit or segmented 16-bit gamma lookup tables.
- `png_do_read_intrapixel()` reverses MNG intrapixel differencing for RGB/RGBA rows.

## Memory and Lookup Tables

This file can allocate several substantial structures through `png_malloc()`:

- Dither index arrays.
- Dither sort arrays and temporary hash lists.
- Palette lookup cubes.
- Gamma tables:
  - 8-bit `gamma_table`, `gamma_to_1`, `gamma_from_1`.
  - Segmented 16-bit `gamma_16_table`, `gamma_16_to_1`, `gamma_16_from_1`.

The 16-bit gamma tables are segmented to avoid allocations larger than 64 KiB, matching old libpng portability constraints.

## Dependencies

- Transform flags and structs from `png.h`.
- Allocation wrappers from `pngmem.c`.
- Row buffers initialized by read startup code.
- Math library functions `pow()`, `fabs()` when floating point gamma/background support is enabled.
- PNG macros such as `PNG_ROWBYTES`, `png_composite`, and `png_composite_16`.

## State Mutated

- `png_ptr->transformations`, `flags`, `mode`.
- Background/gamma state: `background`, `background_1`, `gamma`, `screen_gamma`, gamma tables.
- Palette and transparency data.
- Dither lookup/index state.
- RGB-to-gray coefficients/status.
- `row_info` and row buffer contents on every transformed row.
- `info_ptr` metadata during `png_read_transform_info()`.

## Risks and Maintenance Notes

- Most transforms mutate rows in place and often expand from the end backward. Correct row-buffer sizing before transformation is mandatory.
- Transform order is semantically important; moving steps can change alpha compositing, gamma correctness, or row layout.
- Many paths are conditionally compiled, so behavior can differ sharply by build configuration.
- `png_do_rgb_to_gray()` checks warning/error modes using equality against the full `transformations` bitmask in places; combined transform flags may affect whether warning/error actions trigger.
- Dithering without histograms uses a complex nearest-color elimination algorithm with many temporary allocations.
- Gamma correction requires floating-point support in this version; the file notes a missing integer implementation.
- The MNG intrapixel path only applies when MNG feature flags and color row types are enabled.

## Research Summary

This is the main read-transform engine. `pngread.c` and `pngpread.c` decode filtered rows, then call into this file to produce the application-requested row format. It owns the highest-risk pixel mutation logic in this group because it combines pointer arithmetic, in-place buffer expansion/shrinking, gamma/background math, palette handling, and compile-time feature variation.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/libpng/pngrtran.c -->