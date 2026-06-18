# Group Research: group_1529_plan9_sources_os_plan9_plan9_sys_src_cmd_gs_libpng_pnggccrd_c_sourc_5f1c4c6c52d7

Scope checked against `Docs/research_subset_a.md`: both files are in the included `sources/os/plan9/plan9` source tree. Both listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/libpng/pnggccrd.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/libpng/pnggccrd.c

## Summary

`pnggccrd.c` is the GNU C / GNU assembler x86 MMX read-side acceleration file from libpng 1.2.8, vendored under Plan 9's Ghostscript `libpng` copy. It is compiled only when `PNG_USE_PNGGCCRD` is defined and provides optimized implementations for PNG row combination, Adam7 interlace expansion, PNG row filter decoding, and runtime MMX capability detection.

This file is not filesystem or storage logic. Its relevance in this subset is as bundled third-party image decoding code inside the Plan 9 source tree.

## Main Compile-Time Gates

The whole file is guarded by `PNG_USE_PNGGCCRD`.

Important feature gates include:

- `PNG_ASSEMBLER_CODE_SUPPORTED`: enables assembler constants and inline MMX paths.
- `PNG_HAVE_ASSEMBLER_COMBINE_ROW`: exposes `png_combine_row`.
- `PNG_READ_INTERLACING_SUPPORTED` and `PNG_HAVE_ASSEMBLER_READ_INTERLACE`: expose `png_do_read_interlace`.
- `PNG_HAVE_ASSEMBLER_READ_FILTER_ROW`: exposes `png_read_filter_row`.
- `PNG_THREAD_UNSAFE_OK`: enables several MMX filter/combine routines that rely on file-scope scratch globals.
- `PNG_MMX_CODE_SUPPORTED`: enables actual CPUID/MMX probing in `png_mmx_support`.

## Public / Internal Entry Points

- `png_combine_row(png_structp png_ptr, png_bytep row, int mask)`: private libpng read helper for progressive/interlaced row composition.
- `png_do_read_interlace(png_structp png_ptr)`: private helper that expands a decoded Adam7 pass row in place to its full row spacing.
- `png_read_filter_row(png_structp png_ptr, png_row_infop row_info, png_bytep row, png_bytep prev_row, int filter)`: private PNG filter decoder dispatcher.
- `png_mmx_support(void)`: exported with `PNGAPI`; tests CPU support and caches result in `_mmx_supported`.
- `png_squelch_warnings(void)`: private helper that self-assigns globals to suppress unused warnings in assembler builds.

Static MMX helpers under `PNG_THREAD_UNSAFE_OK`:

- `png_read_filter_row_mmx_avg`
- `png_read_filter_row_mmx_paeth`
- `png_read_filter_row_mmx_sub`

MMX helper independent of `PNG_THREAD_UNSAFE_OK` in this file:

- `png_read_filter_row_mmx_up`

## State and Constants

The file defines MMX mask constants for packed-pixel row combination:

- `_mask8_0`
- `_mask16_0`, `_mask16_1`
- `_mask24_0` through `_mask24_2`
- `_mask32_0` through `_mask32_3`
- `_mask48_0` through `_mask48_5`
- `_const4`, `_const6`

It also defines aligned `union uAll` globals for filter math masks and shift counts:

- `_LBCarryMask`
- `_HBClearMask`
- `_ActiveMask`
- `_ActiveMask2`
- `_ActiveMaskEnd`
- `_ShiftBpp`
- `_ShiftRem`

When `PNG_THREAD_UNSAFE_OK` is enabled, the file uses global scratch state:

- `_unmask`
- `_FullLength`
- `_MMXLength`
- `_dif`
- `_patemp`
- `_pbtemp`
- `_pctemp`

Those globals are the main reason many accelerated paths are explicitly thread-unsafe.

`_mmx_supported` starts at `2`, meaning "unknown"; `png_mmx_support()` changes it to `1` or `0`.

## `png_combine_row`

`png_combine_row` merges the newly decoded row in `png_ptr->row_buf + 1` into the destination `row` according to an 8-bit repeating pixel mask.

Control flow:

- If MMX support is still unknown, it calls `png_mmx_support()` and may warn that `asm_flags` were not initialized.
- If `mask == 0xff`, it copies the whole decoded row with `png_memcpy`.
- Otherwise it switches on `png_ptr->row_info.pixel_depth`.

Packed depths `1`, `2`, and `4` are handled in C with bit extraction and bit replacement. These paths honor `PNG_PACKSWAP` when enabled.

Byte-aligned depths use either MMX or C fallback:

- `8`, `16`, `24`, `32`, and `48` bits have MMX combine paths when assembler, thread-unsafe globals, and `PNG_ASM_FLAG_MMX_READ_COMBINE_ROW` allow it.
- `64` bits uses the C fallback only in the read code present here.
- C fallback uses Adam7 pass metadata (`png_pass_start`, `png_pass_inc`, `png_pass_width`) to copy only the active pixel spans and handles leftover pixels after rounding width down to a multiple of 8.

Risk notes:

- The MMX paths assume x86 GNU assembler syntax and careful register constraints.
- The C fallback contains historical bugfixes around final byte count and leftover pixels; changing loop bounds would be risky.
- The `48`-bit MMX leftover cleanup appears to copy only a 32-bit word per pixel in the assembly tail, while the C path handles 6 bytes; the file's own changelog says 48-bit MMX work was incomplete/untested historically.

## `png_do_read_interlace`

`png_do_read_interlace` expands a decoded Adam7 row in place after earlier transformations such as 16-to-8 conversion.

Control flow:

- Reads `row_info`, `row`, and current `pass` from `png_ptr`.
- Computes `final_width = row_info->width * png_pass_inc[pass]`.
- Switches on `row_info->pixel_depth`.

For packed `1`, `2`, and `4` bpp, it walks backward from the end of the packed row, replicating each source pixel into the expanded destination spacing. It accounts for `PNG_PACKSWAP`.

For byte-aligned pixels, it calculates `pixel_bytes = pixel_depth >> 3`, sets source and destination pointers to the last pixel positions, and expands backward to avoid overwriting unread data.

MMX specializations cover several cases:

- 1-byte pixels for pass groups `0/1`, `2/3`, and `4/5`.
- 2-byte pixels for pass groups `0/1`, `2/3`, and `4/5`.
- 3-byte pixels with separate logic for pass groups and a partial MMX cleanup.
- 4-byte pixels for pass groups.
- 8-byte pixels for pass groups.
- 6-byte pixels falls back to C.

After expansion, it updates:

- `row_info->width`
- `row_info->rowbytes`

Risk notes:

- The function operates in place, backward, and depends on exact source/destination pointer arithmetic.
- The file comments explicitly list still-open uncertainty around 24-bit pass `4/5` width handling and testing for 64-bit pixels.
- Debug-only bounds messages use pointer values formatted as integers, which reflects old C style and is not portable.

## PNG Filter Decoding

`png_read_filter_row` is the dispatcher for PNG filter types:

- `PNG_FILTER_VALUE_NONE`: no-op.
- `PNG_FILTER_VALUE_SUB`: reconstructs bytes using left byte.
- `PNG_FILTER_VALUE_UP`: reconstructs bytes using previous row byte.
- `PNG_FILTER_VALUE_AVG`: reconstructs using average of left and previous row.
- `PNG_FILTER_VALUE_PAETH`: reconstructs using Paeth predictor.
- Unknown filter: warns and clears first row byte.

It prefers MMX helpers when all of these are true:

- assembler support is enabled,
- corresponding `png_ptr->asm_flags` bit is set,
- row bit depth and row byte count meet `mmx_bitdepth_threshold` and `mmx_rowbytes_threshold`,
- and for Sub/Avg/Paeth, `PNG_THREAD_UNSAFE_OK` is enabled.

Fallback C implementations are present inline for all filters, so this file no longer depends on a separate C read-filter implementation.

### MMX Sub Filter

`png_read_filter_row_mmx_sub`:

- Computes bytes per pixel (`bpp`) and `_FullLength = rowbytes - bpp`.
- Handles initial bytes up to an 8-byte alignment boundary.
- Uses bpp-specific MMX loops for `1`, `2`, `3`, `4`, `6`, and `8` bytes per pixel.
- Finishes trailing bytes with scalar x86 code and emits `EMMS`.

### MMX Up Filter

`png_read_filter_row_mmx_up`:

- Adds `prev_row` bytes to `row` bytes.
- Aligns to 8 bytes, then uses a heavily unrolled 64-byte MMX loop.
- Handles remaining 8-byte groups and final scalar bytes.
- Saves/restores `ebx` under `__PIC__`.

This is the simplest MMX filter path because it has no left-neighbor dependency.

### MMX Average Filter

`png_read_filter_row_mmx_avg`:

- Handles first `bpp` bytes with prior-row-only averaging.
- Aligns to an 8-byte boundary.
- Uses bpp-specific vector logic for `1`, `2`, `3`, `4`, `6`, and `8` byte pixels.
- Uses `_LBCarryMask` and `_HBClearMask` to compute byte-wise divide-by-two with carry behavior.
- Uses scalar cleanup for trailing bytes.

Risk notes:

- Uses global `_dif`, `_FullLength`, `_MMXLength`, and shift/mask globals.
- Historical comments describe a fixed 16-bit grayscale bug in the `bpp == 2` case.

### MMX Paeth Filter

`png_read_filter_row_mmx_paeth`:

- Handles the first `bpp` bytes as `row += prev_row`.
- Aligns to an 8-byte boundary using scalar predictor logic.
- Uses bpp-specific MMX predictor calculations for `3`, `4`, `6`, and `8` byte pixels.
- Falls back to scalar predictor loops for `1`, `2`, and default bpp.
- Cleans up trailing bytes after MMX processing.

The Paeth MMX code implements vectorized predictor selection by computing absolute differences in word lanes, comparing `pa`, `pb`, and `pc`, and selecting `a`, `b`, or `c`.

Risk notes:

- This is the most complex block in the file.
- It relies on global scratch integers `_patemp`, `_pbtemp`, `_pctemp` in scalar alignment/cleanup paths.
- Correctness depends on exact unsigned byte wraparound behavior after adding predictor values.

## CPU Feature Detection

`png_mmx_support` uses inline assembly to:

- Save `ebx`, `ecx`, and `edx`.
- Test whether the CPU supports toggling the EFLAGS ID bit.
- Call `cpuid`.
- Check CPUID function availability.
- Check EDX bit 23 for MMX.
- Store `1` or `0` into `_mmx_supported`.

If `PNG_MMX_CODE_SUPPORTED` is not defined, it forces `_mmx_supported = 0`.

Risk notes:

- This assumes 32-bit x86 semantics (`pushfl`, `popfl`, `%eax`, `%ebx`, etc.).
- It is unsuitable for non-x86 or 64-bit-only compilers unless excluded by build flags.
- The file avoids declaring `ebx/ecx/edx` as clobbers in this function because it saves/restores them manually.

## Dependencies

Direct include:

- `png.h`

Important libpng data/functions/macros used:

- `png_struct`, `png_row_info`, row buffers and pass fields.
- `png_pass_start`, `png_pass_inc`, `png_pass_width` or local copies.
- `png_memcpy`, `png_warning`, `png_debug`, `png_debug1`, `png_debug2`.
- `PNG_ROWBYTES`.
- `PNG_ASM_FLAG_MMX_READ_*` flags.
- PNG filter constants and transform flags.

## Research Notes

This file is old vendored libpng optimization code. It is performance-oriented, platform-specific, and conditionally thread-unsafe. For maintenance, the safest stance is to treat it as third-party code and avoid local edits unless reproducing a known upstream libpng fix or disabling the assembly path for portability.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/libpng/pnggccrd.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/libpng/pngget.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/libpng/pngget.c

## Summary

`pngget.c` is libpng 1.2.8 getter API implementation for values stored in `png_info` and selected state stored in `png_struct`. It is a read-only accessor layer: most functions validate `png_ptr` / `info_ptr`, check a chunk-validity bit where appropriate, populate caller-provided output pointers, and return either a `PNG_INFO_*` bit, a count, or zero/null on absence.

This file is not filesystem logic. It is bundled third-party PNG metadata access code inside the Plan 9 Ghostscript tree.

## General Pattern

Most getters follow this shape:

- Return `0`, `NULL`, or equivalent if required pointers are missing.
- Check `info_ptr->valid & PNG_INFO_*` for chunk-backed metadata.
- Assign output pointer parameters only when non-null.
- Return the corresponding `PNG_INFO_*` flag, a boolean-like `1`, a byte/count value, or a pointer.

Debug logging uses `png_debug1` in many chunk getter paths.

## Basic Image Accessors

Always-available accessors:

- `png_get_valid`: returns `info_ptr->valid & flag`.
- `png_get_rowbytes`: returns `info_ptr->rowbytes`.
- `png_get_channels`: returns `info_ptr->channels`.
- `png_get_signature`: returns `info_ptr->signature`.

Conditional accessors:

- `png_get_rows` under `PNG_INFO_IMAGE_SUPPORTED`.
- Easy IHDR-style accessors under `PNG_EASY_ACCESS_SUPPORTED`:
  - `png_get_image_width`
  - `png_get_image_height`
  - `png_get_bit_depth`
  - `png_get_color_type`
  - `png_get_filter_type`
  - `png_get_interlace_type`
  - `png_get_compression_type`

These are direct field reads with null guards.

## Resolution and Offset Accessors

Resolution functions read `pHYs` metadata when `PNG_pHYs_SUPPORTED` is enabled:

- `png_get_x_pixels_per_meter`
- `png_get_y_pixels_per_meter`
- `png_get_pixels_per_meter`
- `png_get_pixel_aspect_ratio` under floating-point support
- inch conversion helpers under `PNG_INCH_CONVERSIONS && PNG_FLOATING_POINT_SUPPORTED`
- `png_get_pHYs`
- `png_get_pHYs_dpi`

Behavior details:

- Per-meter getters return `0` unless the `pHYs` chunk is valid and uses meter units.
- `png_get_pixels_per_meter` additionally requires equal x/y density.
- `png_get_pixel_aspect_ratio` returns `y_pixels_per_unit / x_pixels_per_unit`, guarding x density of zero.
- Inch conversion helpers call meter/micron getters and apply fixed conversion constants.
- `png_get_pHYs` returns `PNG_INFO_pHYs` bits for whichever output fields it actually fills.
- `png_get_pHYs_dpi` optionally converts meter units to DPI when `unit_type == 1`.

Offset functions read `oFFs` metadata when `PNG_oFFs_SUPPORTED` is enabled:

- `png_get_x_offset_microns`
- `png_get_y_offset_microns`
- `png_get_x_offset_pixels`
- `png_get_y_offset_pixels`
- `png_get_oFFs`

They require the corresponding offset unit type for the scalar convenience getters.

## Chunk Metadata Accessors

The file implements getters for common ancillary chunks:

- `png_get_bKGD`: returns pointer to `info_ptr->background`.
- `png_get_cHRM`: returns floating chromaticity values.
- `png_get_cHRM_fixed`: returns fixed-point chromaticity values.
- `png_get_gAMA`: returns floating gamma.
- `png_get_gAMA_fixed`: returns fixed-point gamma.
- `png_get_sRGB`: returns rendering intent.
- `png_get_iCCP`: returns profile name, compression type, profile pointer, and profile length.
- `png_get_sPLT`: returns suggested palette array and count.
- `png_get_hIST`: returns histogram pointer.
- `png_get_oFFs`: returns offset x/y/unit.
- `png_get_pCAL`: returns calibration purpose/range/type/units/params.
- `png_get_sCAL`: returns floating physical scale.
- `png_get_sCAL_s`: returns string/fixed build scale fields.
- `png_get_PLTE`: returns palette pointer and palette count.
- `png_get_sBIT`: returns significant bits structure.
- `png_get_text`: returns text array and count.
- `png_get_tIME`: returns modification time.
- `png_get_tRNS`: returns transparency data, with palette/non-palette behavior split.
- `png_get_unknown_chunks`: returns unknown chunk array and count.

Most return the chunk's `PNG_INFO_*` bit when valid and all mandatory output pointers are provided.

## IHDR Validation Getter

`png_get_IHDR` is more than a plain getter. It copies IHDR fields and validates basic sanity:

- Requires non-null `width`, `height`, `bit_depth`, and `color_type`.
- Calls `png_error` for invalid bit depth outside `1..16`.
- Calls `png_error` for invalid color type greater than `6`.
- Calls `png_error` for zero or too-large width/height.
- Warns when width is too large for libpng row processing calculations.
- Optionally returns compression, filter, and interlace type.

It returns `1` on successful field retrieval and `0` on missing required pointers.

## Runtime State Accessors

These read `png_struct` state rather than chunk metadata:

- `png_get_rgb_to_gray_status`
- `png_get_user_chunk_ptr`
- `png_get_compression_buffer_size`
- `png_get_asm_flags`
- `png_get_mmx_bitdepth_threshold`
- `png_get_mmx_rowbytes_threshold`
- `png_get_user_width_max`
- `png_get_user_height_max`

They use null-safe ternary patterns and return zero/null defaults.

## Assembly/MMX Capability Accessors

Under non-1.0 compatibility and assembler support:

- `png_get_asm_flags`: returns current `png_ptr->asm_flags`.
- `png_get_asm_flagmask`: returns theoretically settable read-side MMX flags for selected read operations.
- `png_get_mmx_flagmask`: same idea for MMX flags and optionally reports compiler ID:
  - `1` for MSVC path (`PNG_USE_PNGVCRD`)
  - `2` for gcc/gas path (`PNG_USE_PNGGCCRD`)
  - `-1` otherwise

The flags include:

- `PNG_ASM_FLAG_MMX_READ_COMBINE_ROW`
- `PNG_ASM_FLAG_MMX_READ_INTERLACE`
- `PNG_ASM_FLAG_MMX_READ_FILTER_SUB`
- `PNG_ASM_FLAG_MMX_READ_FILTER_UP`
- `PNG_ASM_FLAG_MMX_READ_FILTER_AVG`
- `PNG_ASM_FLAG_MMX_READ_FILTER_PAETH`

Write-side MMX flags are commented out as future/not implemented.

## Edge Cases and Risks

Most functions are defensive, but there are consistency risks typical of this older libpng code:

- `png_get_sPLT` returns `info_ptr->splt_palettes_num` even if `info_ptr` is null; only the optional output assignment is guarded.
- `png_get_unknown_chunks` similarly returns `info_ptr->unknown_chunks_num` even if `info_ptr` is null.
- `png_get_PLTE` checks `palette != NULL` but writes `*num_palette` without checking `num_palette`.
- Several getters require all output pointers to be non-null before returning data, while others allow partial output. Callers must follow each API's exact contract.
- Returned pointers generally alias storage owned by `png_info` or `png_struct`; callers must not free or outlive the owning libpng structs.

## Dependencies

Direct include:

- `png.h`

Core data dependencies:

- `png_structp`
- `png_infop`
- `png_info` chunk fields
- libpng feature macros for optional chunks and compatibility modes
- `png_debug1`, `png_error`, `png_warning`

## Research Notes

This file is a stable accessor layer for old libpng metadata. It has little algorithmic complexity except `png_get_IHDR` validation and unit conversion helpers. Maintenance should preserve libpng API compatibility, especially return semantics and conditional compilation around optional PNG chunks.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/libpng/pngget.c -->