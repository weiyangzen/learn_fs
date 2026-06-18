# Group Research: group_1532_plan9_sources_os_plan9_plan9_sys_src_cmd_gs_libpng_pngvcrd_c_source_1307361198b6

Scope checked against `Docs/research_subset_a.md`: all files are under the included `sources/os/plan9/plan9` source tree. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/libpng/pngvcrd.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/libpng/pngvcrd.c

## Summary

`pngvcrd.c` is the Microsoft Visual C++ inline-assembly x86/MMX read-side acceleration file from libpng 1.2.8, vendored under Plan 9's Ghostscript `libpng` copy. It implements CPU MMX detection plus optimized read helpers for row combining, Adam7 interlace expansion, and PNG filter reconstruction.

This is not filesystem or storage code. Its relevance in subset A is as bundled third-party image decoding code inside the Plan 9 source tree.

## Main Compile-Time Gates

The entire file is guarded by:

- `PNG_ASSEMBLER_CODE_SUPPORTED`
- `PNG_USE_PNGVCRD`

Additional feature gates affect individual regions:

- `PNG_READ_INTERLACING_SUPPORTED`: enables `png_do_read_interlace`.
- `PNG_READ_PACKSWAP_SUPPORTED`: changes packed-bit order handling for 1/2/4-bit rows.
- `PNG_1_0_X`: switches between old direct `mmx_supported` decisions and newer `png_ptr->asm_flags`.
- Various `PNG_ASM_FLAG_MMX_*` bits select individual accelerated paths in newer libpng builds.

## Public / Internal Entry Points

- `png_mmx_support(void)`: uses CPUID from MSVC inline assembly to detect MMX support and caches the result in file-scope `mmx_supported`.
- `png_combine_row(png_structp png_ptr, png_bytep row, int mask)`: combines the just-decoded row into the display/output row for interlaced or progressive reads.
- `png_do_read_interlace(png_structp png_ptr)`: expands a decoded Adam7 pass row in place to full pass spacing.
- `png_read_filter_row(png_structp png_ptr, png_row_infop row_info, png_bytep row, png_bytep prev_row, int filter)`: dispatches PNG row-filter reconstruction.
- `png_read_filter_row_mmx_avg`, `png_read_filter_row_mmx_paeth`, `png_read_filter_row_mmx_sub`, `png_read_filter_row_mmx_up`: MMX-specialized filter decoders.

## State and Constants

The file uses `static int mmx_supported = 2`, where `2` means unknown, `1` supported, and `0` unsupported.

It also defines file-scope aligned `union uAll` globals:

- `LBCarryMask`
- `HBClearMask`
- `ActiveMask`
- `ActiveMask2`
- `ActiveMaskEnd`
- `ShiftBpp`
- `ShiftRem`

These globals are written by the filter routines before entering inline assembly. That makes the accelerated code effectively non-reentrant and risky in multithreaded callers if multiple PNG rows are decoded concurrently through the same process.

## Row Combination

`png_combine_row` handles masked row composition.

Behavior:

- If MMX support is unknown, it calls `png_mmx_support()`.
- If `mask == 0xff`, it copies the full decoded row from `png_ptr->row_buf + 1`.
- For 1/2/4-bit pixels, it uses C bit extraction and insertion, honoring `PNG_PACKSWAP`.
- For byte-aligned pixel depths, it uses MMX where enabled and falls back to C Adam7 pass stepping otherwise.

Specialized MMX cases exist for 8, 16, 24, 32, and 48-bit pixel depths. Other depths fall through to generic byte-copy stepping based on the current Adam7 pass.

Risk notes:

- The 48-bit MMX tail path copies and advances by 4 bytes in its leftover loop even though 48-bit pixels are 6 bytes. This matches a historically fragile area also visible in sibling MMX code.
- The routine depends on exact pass offsets and row byte calculations; off-by-one changes can corrupt rows.
- The MSVC `_asm` syntax makes this file non-portable outside 32-bit x86 MSVC-style builds.

## Adam7 Interlace Expansion

`png_do_read_interlace` expands a decoded Adam7 pass row in place.

Behavior:

- Computes `final_width = row_info->width * png_pass_inc[pass]`.
- Handles packed 1/2/4-bit rows in C by walking backward through packed bits.
- Handles byte-aligned rows by walking backward from the last source pixel to the last destination pixel to avoid overwriting unread source bytes.
- Uses MMX specializations for 1, 2, 3, and 4-byte pixels for pass groups `0/1`, `2/3`, and `4/5`.
- Handles 6-byte and other uncommon pixel widths through C fallback loops.

After expansion it updates:

- `row_info->width`
- `row_info->rowbytes`

Risk notes:

- The in-place backward expansion is pointer-arithmetic heavy.
- The file comments mention historical sign fixes for cleanup code after MMX loops.
- Wider pixels and odd leftover widths are the highest-risk paths.

## PNG Filter Decoding

`png_read_filter_row` dispatches PNG filter reconstruction:

- `PNG_FILTER_VALUE_NONE`: no-op.
- `PNG_FILTER_VALUE_SUB`: reconstructs from left bytes.
- `PNG_FILTER_VALUE_UP`: reconstructs from previous-row bytes.
- `PNG_FILTER_VALUE_AVG`: reconstructs from the average of left and previous-row bytes.
- `PNG_FILTER_VALUE_PAETH`: reconstructs from the Paeth predictor.
- Unknown filter values warn and clear the first row byte.

For each filter, newer builds check `png_ptr->asm_flags`, `png_ptr->mmx_bitdepth_threshold`, and `png_ptr->mmx_rowbytes_threshold` before using MMX. Older `PNG_1_0_X` builds use only the cached MMX support result.

### MMX Sub

`png_read_filter_row_mmx_sub` reconstructs bytes by adding each byte to its left neighbor. It aligns to an 8-byte boundary, then uses bpp-specific MMX loops for common byte-per-pixel values, with scalar cleanup.

### MMX Up

`png_read_filter_row_mmx_up` adds each byte from `prev_row` to the current row. It uses an unrolled 64-byte MMX loop, then handles remaining 8-byte groups and final scalar bytes.

### MMX Average

`png_read_filter_row_mmx_avg` reconstructs using PNG Average filter rules. It handles the first `bpp` bytes separately, aligns to 8 bytes, and uses masks to emulate byte-wise average arithmetic without losing carry behavior.

### MMX Paeth

`png_read_filter_row_mmx_paeth` reconstructs with the Paeth predictor. It has complex bpp-specific vector logic for common pixel sizes and scalar fallback for small or uncommon cases.

## Dependencies

This file depends on internal libpng state and helpers from `png.h`:

- `png_struct`, `png_row_info`, row buffers, pass number, width, transformations, and assembler flags.
- `png_memcpy`, `png_warning`, `png_error`, and debug macros.
- PNG filter constants and transform flags.

It is initialized indirectly by `png_init_mmx_flags()` in `png.c`, which is called during read/write struct creation in other libpng files.

## Research Notes

This file is performance-oriented, architecture-specific third-party code. It should be treated as vendored libpng 1.2.8 code rather than native Plan 9 filesystem code. Maintenance risk is high because behavior is encoded in inline assembly, shared scratch globals, and subtle PNG row-layout invariants.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/libpng/pngvcrd.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/libpng/pngwio.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/libpng/pngwio.c

## Summary

`pngwio.c` contains libpng 1.2.8 write-side I/O glue. It routes encoded PNG bytes to user-provided callbacks or to default stdio-backed writers, and optionally flushes pending output.

This is not filesystem or storage code. It is third-party PNG library I/O abstraction code vendored in Plan 9's Ghostscript tree.

## Main Compile-Time Gates

The file is active under `PNG_WRITE_SUPPORTED`.

Other gates:

- `PNG_NO_STDIO`: removes default stdio write/flush implementations.
- `_WIN32_WCE`: uses `WriteFile` instead of `fwrite`.
- `USE_FAR_KEYWORD`: enables old segmented-memory handling for far buffers.
- `PNG_WRITE_FLUSH_SUPPORTED`: enables explicit flush support.

## Entry Points

- `png_write_data(png_structp png_ptr, png_bytep data, png_size_t length)`: private central output function. Calls `png_ptr->write_data_fn` or raises a fatal libpng error if no writer is set.
- `png_default_write_data(...)`: default writer using `fwrite` or Windows CE `WriteFile`.
- `png_flush(png_structp png_ptr)`: private flush dispatcher, when flush support is enabled.
- `png_default_flush(png_structp png_ptr)`: default stdio flush using `fflush`.
- `png_set_write_fn(png_structp png_ptr, png_voidp io_ptr, png_rw_ptr write_data_fn, png_flush_ptr output_flush_fn)`: public API for installing custom write and flush callbacks.
- `png_far_to_near(...)`: legacy segmented-memory conversion helper under `USE_FAR_KEYWORD`.

## I/O Model

`png_set_write_fn` stores the caller's `io_ptr`, chooses either the provided callbacks or default stdio callbacks, and clears any read callback already set on the same `png_struct`.

This is libpng's callback boundary between encoder logic and the embedding application. Higher-level chunk and row-writing routines call `png_write_data`; they do not write directly to files.

## Error Handling

Write failures are fatal libpng errors:

- If no writer is configured, `png_write_data` calls `png_error`.
- If `fwrite` or `WriteFile` writes fewer bytes than requested, `png_default_write_data` calls `png_error`.
- In far-buffer mode, failed pointer conversion or short writes are also fatal.

## Legacy / Portability Notes

The `USE_FAR_KEYWORD` branch supports old memory models where standard I/O cannot write far buffers directly. It copies data into a 1024-byte near stack buffer in chunks before writing.

The Windows CE path uses `WriteFile` because normal stdio support is unavailable or unsuitable there.

## Dependencies

This file depends on internal libpng fields:

- `png_ptr->io_ptr`
- `png_ptr->write_data_fn`
- `png_ptr->output_flush_fn`
- `png_ptr->read_data_fn`

It also uses `png_error`, `png_warning`, `png_memcpy`, and pointer-conversion macros from libpng.

## Research Notes

The file is small but important because it is the sole default write-output abstraction for this libpng copy. Behavior is straightforward: install callbacks, write bytes, flush when requested, and prevent accidental simultaneous read/write callback use in the same structure.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/libpng/pngwio.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/libpng/pngwrite.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/libpng/pngwrite.c

## Summary

`pngwrite.c` contains the main libpng 1.2.8 PNG encoder orchestration code. It writes PNG metadata chunks in the required order, creates and initializes write structs, writes image rows, handles interlaced passes, flushes zlib output, frees write-side resources, configures filters/compression, and provides the high-level `png_write_png` convenience API.

This is not filesystem or storage code. It is third-party PNG encoding code vendored under Plan 9's Ghostscript source tree.

## Main Compile-Time Gates

The file is active under `PNG_WRITE_SUPPORTED`.

Important optional gates include:

- Chunk writers: `PNG_WRITE_gAMA_SUPPORTED`, `PNG_WRITE_sRGB_SUPPORTED`, `PNG_WRITE_iCCP_SUPPORTED`, `PNG_WRITE_sBIT_SUPPORTED`, `PNG_WRITE_cHRM_SUPPORTED`, `PNG_WRITE_tRNS_SUPPORTED`, `PNG_WRITE_bKGD_SUPPORTED`, `PNG_WRITE_hIST_SUPPORTED`, `PNG_WRITE_oFFs_SUPPORTED`, `PNG_WRITE_pCAL_SUPPORTED`, `PNG_WRITE_sCAL_SUPPORTED`, `PNG_WRITE_pHYs_SUPPORTED`, `PNG_WRITE_tIME_SUPPORTED`, `PNG_WRITE_sPLT_SUPPORTED`, `PNG_WRITE_TEXT_SUPPORTED`, `PNG_WRITE_UNKNOWN_CHUNKS_SUPPORTED`.
- Transform and row handling: `PNG_WRITE_INTERLACING_SUPPORTED`, `PNG_WRITE_INVERT_ALPHA_SUPPORTED`, `PNG_WRITE_TRANSFORMS`, `PNG_MNG_FEATURES_SUPPORTED`.
- Runtime/system support: `PNG_USER_MEM_SUPPORTED`, `PNG_SETJMP_SUPPORTED`, `PNG_SET_USER_LIMITS_SUPPORTED`, `PNG_ASSEMBLER_CODE_SUPPORTED`.
- Filter tuning: `PNG_WRITE_WEIGHTED_FILTER_SUPPORTED`.
- Convenience API: `PNG_INFO_IMAGE_SUPPORTED`.

## Metadata Writing

`png_write_info_before_PLTE` writes the PNG signature and the chunks that must appear before `PLTE`.

It writes:

- PNG signature.
- `IHDR`.
- Optional pre-palette chunks such as `gAMA`, `sRGB`, `iCCP`, `sBIT`, `cHRM`.
- Unknown chunks whose recorded location is before `PLTE`.

It sets `PNG_WROTE_INFO_BEFORE_PLTE` to prevent duplicate header emission.

`png_write_info` then writes:

- `PLTE`, with a fatal error if a paletted image has no valid palette.
- `tRNS`, including optional alpha inversion for palette transparency.
- Other pre-IDAT chunks such as `bKGD`, `hIST`, `oFFs`, `pCAL`, `sCAL`, `pHYs`, `tIME`, `sPLT`.
- Header text chunks (`iTXt`, `zTXt`, `tEXt`) according to each text record's compression mode.
- Unknown chunks located after `PLTE` but before `IDAT`.

`png_write_end` writes trailer metadata after image data and then emits `IEND`. It requires that at least one IDAT has been written.

## Struct Creation and Initialization

`png_create_write_struct` and `png_create_write_struct_2` allocate and initialize a `png_struct` for writing.

Key setup steps:

- Allocate the structure through libpng's normal or user-memory allocator.
- Initialize MMX flags when assembler code is enabled.
- Set user width/height limits when supported.
- Establish error handling and `setjmp` fallback behavior.
- Check runtime libpng version compatibility against the application header version.
- Allocate the zlib output buffer `zbuf`.
- Install default write callbacks through `png_set_write_fn`.
- Initialize weighted filter heuristics when enabled.

Legacy entry points `png_write_init`, `png_write_init_2`, and `png_write_init_3` support applications compiled against older libpng APIs. They validate structure sizes, preserve the jump buffer, reset the structure, and then perform write initialization.

## Row and Image Writing

`png_write_rows` writes a caller-supplied sequence of rows by repeatedly calling `png_write_row`.

`png_write_image` writes a full image and handles Adam7 interlace pass repetition when `png_set_interlace_handling()` is active.

`png_write_row` is the core row pipeline:

1. On the first row/pass, verify header info was written and call `png_write_start_row`.
2. Warn about requested write transforms that were compiled out.
3. Skip rows not used by the current Adam7 pass.
4. Populate `png_ptr->row_info` from user-visible image parameters.
5. Copy the user row into `png_ptr->row_buf + 1`, leaving byte 0 for the PNG filter type.
6. Apply write interlace reduction through `png_do_write_interlace` when needed.
7. Apply configured row transformations through `png_do_write_transformations`.
8. Apply MNG intrapixel differencing when permitted.
9. Pick/filter/compress/write the row through `png_write_find_filter`.
10. Call the optional write status callback.

This function coordinates with `pngwtran.c` for transformations and `pngwutil.c` for row setup, interlace reduction, filter selection, and chunk emission.

## Flushing

When `PNG_WRITE_FLUSH_SUPPORTED` is enabled:

- `png_set_flush` sets the automatic flush interval.
- `png_write_flush` uses `deflate(..., Z_SYNC_FLUSH)` to push pending compressed data into IDAT chunks, resets zlib output pointers, clears `flush_rows`, and calls `png_flush`.

Compression errors are fatal.

## Destruction

`png_destroy_write_struct` frees the info struct and write struct, preserving user-memory allocator hooks when configured.

`png_write_destroy` releases write-side allocations:

- zlib stream state via `deflateEnd`.
- `zbuf`, `row_buf`, `prev_row`, and filter candidate rows.
- RFC1123 time buffer when present.
- Weighted filter heuristic arrays when present.

It then clears most of `png_struct` while preserving error/warning callbacks, error pointer, optional custom free function, and jump buffer.

## Filter and Compression Configuration

`png_set_filter` selects allowed PNG row filters for method `PNG_FILTER_TYPE_BASE`.

It supports:

- None
- Sub
- Up
- Average
- Paeth
- Bitmask combinations of the above

If filters are changed after row buffers have already been allocated, it lazily allocates missing filter buffers where possible. It refuses to add filters requiring `prev_row` if previous-row state is unavailable.

`png_set_filter_heuristics` configures weighted filter selection:

- Validates heuristic method.
- Allocates and initializes previous-filter history.
- Stores filter weights and inverse weights.
- Allocates per-filter costs and inverse costs.

Compression setter APIs store zlib preferences in `png_ptr` and mark corresponding custom flags:

- `png_set_compression_level`
- `png_set_compression_mem_level`
- `png_set_compression_strategy`
- `png_set_compression_window_bits`
- `png_set_compression_method`

The window-bits setter warns for PNG-incompatible sizes and may adjust an 8-bit window to 9 if `WBITS_8_OK` is not defined.

## High-Level Convenience API

`png_write_png` performs a complete write from a populated `png_info`:

1. Applies pre-info alpha inversion if requested.
2. Calls `png_write_info`.
3. Enables requested write transforms such as invert mono, shift, packing, swap alpha, strip filler, BGR, endian swap, and packswap.
4. Writes `info_ptr->row_pointers` if image data is present.
5. Calls `png_write_end`.

The `params` argument is unused except to quiet warnings in this vintage API.

## Dependencies

This file depends heavily on other libpng internals:

- `pngwio.c`: `png_set_write_fn`, `png_flush`.
- `pngwutil.c`: chunk writers, `png_write_start_row`, `png_do_write_interlace`, `png_write_find_filter`, `png_write_finish_row`.
- `pngwtran.c`: `png_do_write_transformations`.
- zlib: `deflate`, `deflateEnd`, output buffer management.
- Core allocation/error/version helpers from `png.c` and `pngmem.c`.

## Research Notes

`pngwrite.c` is the write-side control plane for this vendored libpng. It does not implement storage persistence itself; it emits bytes through callbacks configured in `pngwio.c`. The highest-risk areas are chunk ordering, row/interlace state transitions, legacy initialization compatibility, and zlib flush/finalization behavior.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/libpng/pngwrite.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/libpng/pngwtran.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/libpng/pngwtran.c

## Summary

`pngwtran.c` implements libpng 1.2.8 write-side row transformations. These transformations convert caller-provided row data into PNG-ready byte order, packing, alpha representation, channel order, and optional MNG intrapixel-differencing form before row filtering/compression.

This is not filesystem or storage code. It is third-party PNG encoder transform code vendored in Plan 9's Ghostscript `libpng` copy.

## Main Compile-Time Gates

The file is active under `PNG_WRITE_SUPPORTED`.

Individual transforms are gated by:

- `PNG_WRITE_USER_TRANSFORM_SUPPORTED`
- `PNG_WRITE_FILLER_SUPPORTED`
- `PNG_WRITE_PACKSWAP_SUPPORTED`
- `PNG_WRITE_PACK_SUPPORTED`
- `PNG_WRITE_SWAP_SUPPORTED`
- `PNG_WRITE_SHIFT_SUPPORTED`
- `PNG_WRITE_INVERT_ALPHA_SUPPORTED`
- `PNG_WRITE_SWAP_ALPHA_SUPPORTED`
- `PNG_WRITE_BGR_SUPPORTED`
- `PNG_WRITE_INVERT_SUPPORTED`
- `PNG_MNG_FEATURES_SUPPORTED`

## Main Dispatcher

`png_do_write_transformations(png_structp png_ptr)` applies transformations in a fixed order:

1. User write transform callback.
2. Strip filler bytes.
3. Pack bit order swap.
4. Pack 8-bit-per-pixel grayscale/palette samples down to 1/2/4 bits.
5. Swap 16-bit byte order.
6. Shift sample values to PNG bit depth.
7. Invert alpha.
8. Swap alpha position.
9. Swap BGR to RGB.
10. Invert monochrome pixels.

Order matters because each transform updates or depends on `png_ptr->row_info`.

## Packing

`png_do_pack(png_row_infop row_info, png_bytep row, png_uint_32 bit_depth)` packs one-channel 8-bit rows into PNG bit depths 1, 2, or 4.

Behavior:

- 1-bit: emits one bit per nonzero source byte.
- 2-bit: emits low two bits of each source byte.
- 4-bit: emits low four bits of each source byte.
- Updates `row_info->bit_depth`, `pixel_depth`, and `rowbytes`.

This path is used for grayscale and paletted images where callers supply unpacked one-byte pixels.

## Sample Shifting

`png_do_shift(png_row_infop row_info, png_bytep row, png_color_8p bit_depth)` scales significant sample bits into the full PNG sample width.

Behavior:

- Skips palette images.
- Determines per-channel shift starts and repeat widths from `png_color_8`.
- Handles sub-8-bit grayscale by expanding within packed bytes.
- Handles 8-bit rows byte by byte.
- Handles 16-bit rows by reconstructing two-byte samples, repeating significant bits into the output value, and writing big-endian sample bytes.

This is used when input samples have fewer significant bits than the PNG output bit depth.

## Alpha Position Swap

`png_do_write_swap_alpha(png_row_infop row_info, png_bytep row)` moves alpha from a leading position to PNG's trailing position.

Supported conversions:

- 8-bit RGBA: ARGB to RGBA.
- 16-bit RGBA: AARRGGBB to RRGGBBAA.
- 8-bit gray-alpha: AG to GA.
- 16-bit gray-alpha: AAGG to GGAA.

It operates in place by reading and writing through paired source/destination pointers.

## Alpha Inversion

`png_do_write_invert_alpha(png_row_infop row_info, png_bytep row)` converts alpha values by subtracting from 255 byte-wise.

Supported cases:

- 8-bit RGBA.
- 16-bit RGBA, inverting both alpha bytes independently.
- 8-bit gray-alpha.
- 16-bit gray-alpha, inverting both alpha bytes independently.

This supports APIs where alpha may represent transparency rather than opacity.

## MNG Intrapixel Differencing

`png_do_write_intrapixel(png_row_infop row_info, png_bytep row)` is enabled under `PNG_MNG_FEATURES_SUPPORTED`.

It applies MNG filter method 64 intrapixel differencing to color rows:

- For 8-bit RGB/RGBA, subtract green from red and blue bytes.
- For 16-bit RGB/RGBA, reconstruct 16-bit red/green/blue samples, subtract green from red and blue modulo 16 bits, and write results back as big-endian bytes.

It only applies to RGB or RGBA rows and returns for unsupported color layouts.

## Dependencies

This file relies on shared transform helpers declared elsewhere in libpng:

- `png_do_strip_filler`
- `png_do_packswap`
- `png_do_swap`
- `png_do_bgr`
- `png_do_invert`

It also depends on `png_struct` transformation flags, `png_row_info`, `png_color_8`, and `PNG_ROWBYTES`.

## Research Notes

`pngwtran.c` is the write-side transform layer called by `png_write_row` before filter selection and compression. It mutates row buffers in place and updates row metadata when packing changes the byte layout. The highest-risk behavior is transform ordering and exact row metadata maintenance after packing or shifting.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/libpng/pngwtran.c -->