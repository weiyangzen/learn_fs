# Group Research: group_94_9front_sources_os_plan9_9front_sys_src_cmd_gs_libpng_pngvcrd_c_source_8861d02b7529

Scope: `Docs/research_subset_a.md`, specifically the bundled libpng 1.2.8 writer/read-assembly support under `sources/os/plan9/9front/sys/src/cmd/gs/libpng`. I read all 4 listed source files completely. The supplied internal group report path was not present in the workspace, so this report is based on the source files themselves.

This group covers legacy libpng write orchestration, write I/O callbacks, writer-side row transformations, and the MSVC/x86 MMX-accelerated read/filter implementation.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/libpng/pngvcrd.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/libpng/pngvcrd.c

Implements a Microsoft Visual C++ inline-assembly, x86/MMX accelerated read-side helper set for libpng 1.2.8.

Key points:
- Compiles only when `PNG_ASSEMBLER_CODE_SUPPORTED` and `PNG_USE_PNGVCRD` are defined.
- `png_mmx_support()` probes CPUID/MMX support using MSVC `_asm`, caches the result in `mmx_supported`, and returns whether MMX is available.
- `png_combine_row()` combines an interlaced/progressive row into the destination row:
  - Fast-copies full rows when `mask == 0xff`.
  - Handles packed 1/2/4-bit pixels in C with optional `PNG_PACKSWAP`.
  - Uses MMX paths for common byte depths including 8, 16, 24, 32, and 48 bits, with C fallback paths keyed by Adam7 pass offsets.
- `png_do_read_interlace()` expands reduced Adam7 pass rows in-place:
  - Packed 1/2/4-bit rows are expanded bitwise.
  - Byte-oriented rows use MMX-specialized duplication loops for 1, 2, 3, and 4 bytes per pixel where possible.
  - 6-byte and uncommon pixel sizes fall back to C copy loops.
  - Updates `row_info->width` and `row_info->rowbytes` to the expanded final width.
- Defines aligned global masks used by filter decoders: `LBCarryMask`, `HBClearMask`, `ActiveMask`, `ActiveMask2`, `ActiveMaskEnd`, `ShiftBpp`, and `ShiftRem`.
- Provides MMX versions of PNG row filter reversal:
  - `png_read_filter_row_mmx_avg()`
  - `png_read_filter_row_mmx_paeth()`
  - `png_read_filter_row_mmx_sub()`
  - `png_read_filter_row_mmx_up()`
- `png_read_filter_row()` dispatches the five PNG filter types:
  - `NONE` leaves the row unchanged.
  - `SUB`, `UP`, `AVG`, and `PAETH` use MMX when enabled by `asm_flags`, bit-depth threshold, and rowbyte threshold; otherwise they use portable C implementations.
  - Unknown filter values generate a warning and clear the filter byte.
- The code preserves older `PNG_1_0_X` behavior with direct `mmx_supported` checks and newer 1.2-style `png_ptr->asm_flags`.

Dependencies and interactions:
- Depends on `png.h`, `png_struct` row state, row filter constants, transformation flags, and Adam7 pass metadata.
- Interacts with libpng read paths that call `png_combine_row`, `png_do_read_interlace`, and `png_read_filter_row`.
- Uses `png_warning`, `png_debug*`, `png_memcpy`, and row metadata macros such as `PNG_ROWBYTES`.

Research relevance:
- This is a legacy platform acceleration layer, not the portable baseline implementation.
- It is tightly coupled to x86, MSVC inline assembly, MMX register cleanup via `emms`, row alignment assumptions, and libpng 1.2 assembly feature flags.
- Notable risk area: some specialized MMX/tail loops are hand-written per pixel depth; the 48-bit combine-row leftover loop appears especially delicate because it operates with 32-bit moves/4-byte advances in a 6-byte-per-pixel case.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/libpng/pngvcrd.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/libpng/pngwio.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/libpng/pngwio.c

Provides libpng write-side output callback plumbing.

Key points:
- Compiles under `PNG_WRITE_SUPPORTED`.
- `png_write_data()` is the internal write dispatcher:
  - Calls `png_ptr->write_data_fn` when configured.
  - Raises `png_error` on a NULL write function.
- `png_default_write_data()` is available when stdio is enabled:
  - Uses `fwrite()` for normal C streams.
  - Uses `WriteFile()` on Windows CE.
  - Raises `png_error("Write Error")` if fewer bytes are written than requested.
- Under `USE_FAR_KEYWORD`, the default writer copies far buffers through a fixed near stack buffer before writing, supporting old segmented memory models.
- `png_flush()` calls `png_ptr->output_flush_fn` when flush support is enabled.
- `png_default_flush()` flushes the stdio stream with `fflush()` when not on Windows CE.
- `png_set_write_fn()` installs the output `io_ptr`, write callback, and optional flush callback:
  - Falls back to default stdio writer/flush functions when callbacks are NULL and stdio is available.
  - Clears any existing read callback and warns if the same `png_struct` was configured for both reading and writing.
- `png_far_to_near()` converts far pointers to near pointers for supported old compiler/memory-model combinations and can validate that the segment was not lost.

Dependencies and interactions:
- Uses `png_struct` callback fields: `io_ptr`, `write_data_fn`, `output_flush_fn`, and `read_data_fn`.
- Called by higher-level chunk and IDAT writers through `png_write_data`.
- Used by `png_create_write_struct()` / `png_write_init_*()` to establish default output behavior.

Research relevance:
- This file is the writer output abstraction boundary. Applications using non-stdio output replace behavior here via `png_set_write_fn()` rather than modifying chunk-writing code.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/libpng/pngwio.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/libpng/pngwrite.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/libpng/pngwrite.c

Implements the main libpng write lifecycle: header chunks, rows, compression flushing, teardown, filter selection, compression settings, and the simplified `png_write_png()` API.

Key points:
- Compiles under `PNG_WRITE_SUPPORTED`.
- `png_write_info_before_PLTE()` writes the PNG signature and pre-PLTE chunks:
  - IHDR is always written.
  - Optional chunks include `gAMA`, `sRGB`, `iCCP`, `sBIT`, `cHRM`, and pre-PLTE unknown chunks.
  - Guards MNG-only feature use in normal PNG datastreams.
- `png_write_info()` writes PLTE and other pre-IDAT metadata:
  - Requires a valid palette for paletted images.
  - Writes `tRNS`, `bKGD`, `hIST`, `oFFs`, `pCAL`, `sCAL`, `pHYs`, `tIME`, `sPLT`, text chunks, and location-appropriate unknown chunks.
  - Can invert palette alpha in `tRNS` when `PNG_INVERT_ALPHA` is active.
- `png_write_end()` finalizes the stream:
  - Requires that IDAT data was written.
  - Writes trailing `tIME`, text, and post-IDAT unknown chunks when present.
  - Sets `PNG_AFTER_IDAT` and writes IEND.
- Time helpers convert `struct tm` and `time_t` into `png_time`.
- `png_create_write_struct()` and `png_create_write_struct_2()` allocate and initialize `png_struct`:
  - Set error/memory callbacks.
  - Check library/header version compatibility.
  - Initialize MMX flags when assembler support is enabled.
  - Set user dimension limits.
  - Allocate the zlib output buffer.
  - Configure default write callbacks.
  - Initialize weighted filter heuristics when supported.
- Legacy `png_write_init()`, `png_write_init_2()`, and `png_write_init_3()` support old applications that allocated structs themselves.
- `png_write_rows()` and `png_write_image()` drive row writing, with multi-pass handling for interlaced images.
- `png_write_row()` is the central row pipeline:
  - Verifies `png_write_info` was called.
  - Initializes write state on the first row.
  - Skips rows not used by the current Adam7 pass.
  - Builds `row_info` from user-facing row format.
  - Copies the user row into `row_buf + 1`, preserving byte 0 for the filter type.
  - Applies write interlace reduction, configured write transformations, optional MNG intrapixel differencing, filter selection, compression/write, and row status callback.
- Flush support:
  - `png_set_flush()` configures automatic row flush distance.
  - `png_write_flush()` uses `deflate(..., Z_SYNC_FLUSH)`, writes pending IDAT chunks, resets zlib output state, and calls the output flush callback.
- Destruction:
  - `png_destroy_write_struct()` frees info data, unknown chunk lists, write buffers, zlib state, and structs.
  - `png_write_destroy()` releases write-side buffers while preserving error/jump callback state.
- `png_set_filter()` selects permitted PNG row filters and lazily allocates filter buffers if row writing already started.
- Weighted filter heuristics allocate and configure previous-filter history, filter weights, inverse weights, costs, and inverse costs.
- Compression setters store custom zlib settings on `png_ptr`: level, memory level, strategy, window bits, and method.
- `png_set_write_status_fn()` installs a per-row callback.
- `png_set_write_user_transform_fn()` enables and stores a user transform callback.
- `png_write_png()` is the high-level convenience API:
  - Applies requested transform flags.
  - Writes info, image rows from `info_ptr->row_pointers`, and end chunks.

Dependencies and interactions:
- Calls chunk writers from `pngwutil.c` such as `png_write_IHDR`, `png_write_PLTE`, `png_write_IDAT`, and ancillary chunk writers.
- Uses writer transforms from `pngwtran.c`, filter selection/compression helpers, zlib `deflate`, and output callbacks from `pngwio.c`.
- Relies on many compile-time feature flags for optional chunk types, transforms, stdio, user memory, setjmp, MNG behavior, and weighted filtering.

Research relevance:
- This is the main public write API implementation for the bundled libpng.
- It defines the required call ordering and state transitions for producing a PNG: create/init, configure callbacks/options, write info, write rows/image, write end, destroy.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/libpng/pngwrite.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/libpng/pngwtran.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/libpng/pngwtran.c

Implements writer-side row transformations applied before PNG filtering and compression.

Key points:
- Compiles under `PNG_WRITE_SUPPORTED`.
- `png_do_write_transformations()` applies transformations in a fixed order:
  - User transform callback.
  - Strip filler.
  - Pack-swap.
  - Pack 8-bit samples down to 1/2/4-bit rows.
  - Swap 16-bit byte order.
  - Shift sample values to declared significant-bit depth.
  - Invert alpha.
  - Swap alpha position.
  - BGR to RGB.
  - Invert monochrome.
- `png_do_pack()` packs one-channel 8-bit grayscale/palette-style samples into 1-, 2-, or 4-bit packed bytes and updates `row_info` bit depth, pixel depth, and rowbytes.
- `png_do_shift()` scales samples so stored PNG values use the full legal range implied by `sBIT`:
  - Handles packed low-bit-depth grayscale rows.
  - Handles 8-bit samples.
  - Handles 16-bit samples.
  - Skips palette color type.
- `png_do_write_swap_alpha()` changes alpha placement:
  - RGB alpha: ARGB to RGBA for 8-bit and AARRGGBB to RRGGBBAA for 16-bit.
  - Gray alpha: AG to GA for 8-bit and AAGG to GGAA for 16-bit.
- `png_do_write_invert_alpha()` converts alpha values by subtracting from 255:
  - Handles RGB-alpha and gray-alpha rows.
  - Handles both 8-bit and 16-bit channel storage, though 16-bit inversion is byte-wise in this legacy implementation.
- `png_do_write_intrapixel()` supports MNG filter method 64 intrapixel differencing:
  - For RGB/RGBA 8-bit rows, stores red and blue as differences from green.
  - For RGB/RGBA 16-bit rows, computes 16-bit red-green and blue-green differences and writes them back big-endian.
  - Applies only to color rows.

Dependencies and interactions:
- Called from `png_write_row()` in `pngwrite.c` after row copying and interlace handling, before filter selection.
- Uses shared transformation helpers from other libpng files for filler stripping, packswap, swap, BGR, and mono inversion.
- Driven by `png_ptr->transformations`, `png_ptr->flags`, `png_ptr->shift`, and `png_ptr->bit_depth`.

Research relevance:
- This file is the writer-side counterpart to read transforms. It mutates row buffers in-place and keeps `row_info` synchronized so subsequent filtering and IDAT compression see the final PNG storage format.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/libpng/pngwtran.c -->