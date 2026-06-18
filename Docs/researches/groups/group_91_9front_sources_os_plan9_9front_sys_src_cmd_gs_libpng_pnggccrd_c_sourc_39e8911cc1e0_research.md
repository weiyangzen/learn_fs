# Group Research: group_91_9front_sources_os_plan9_9front_sys_src_cmd_gs_libpng_pnggccrd_c_sourc_39e8911cc1e0

Scope: `Docs/research_subset_a.md`, covering `sources/os/plan9/9front`.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/libpng/pnggccrd.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/libpng/pnggccrd.c

## Purpose

`pnggccrd.c` is libpng 1.2.8's x86 GNU C/GAS MMX read-path implementation. It is compiled only when `PNG_USE_PNGGCCRD` is defined and provides accelerated versions of row combining, Adam7 interlace expansion, PNG row-filter decoding, and runtime MMX detection for the Ghostscript-bundled libpng copy in the 9front tree.

The file is architecture-specific and heavily conditional. Most optimized paths require combinations of:

- `PNG_USE_PNGGCCRD`
- `PNG_ASSEMBLER_CODE_SUPPORTED`
- `PNG_MMX_CODE_SUPPORTED`
- `PNG_THREAD_UNSAFE_OK`
- `PNG_HAVE_ASSEMBLER_COMBINE_ROW`
- `PNG_HAVE_ASSEMBLER_READ_INTERLACE`
- `PNG_HAVE_ASSEMBLER_READ_FILTER_ROW`

## Main Entry Points

- `png_squelch_warnings(void)`: references static assembler constants and globals to silence unused-variable warnings.
- `png_combine_row(png_structp png_ptr, png_bytep row, int mask)`: combines an interlaced/progressive source row from `png_ptr->row_buf + 1` into the caller row according to an 8-bit pixel mask.
- `png_do_read_interlace(png_structp png_ptr)`: expands Adam7 interlaced rows in place after earlier read transforms.
- `png_read_filter_row(png_structp png_ptr, png_row_infop row_info, png_bytep row, png_bytep prev_row, int filter)`: dispatches PNG filter reconstruction for `None`, `Sub`, `Up`, `Avg`, and `Paeth`, selecting MMX helpers when permitted.
- `png_mmx_support(void)`: probes CPU support for CPUID/MMX and caches the answer in `_mmx_supported`.

Private MMX helpers:

- `png_read_filter_row_mmx_avg(...)`
- `png_read_filter_row_mmx_paeth(...)`
- `png_read_filter_row_mmx_sub(...)`
- `png_read_filter_row_mmx_up(...)`

## Data And Constants

The file defines local Adam7 pass tables when `PNG_USE_LOCAL_ARRAYS` is set:

- `png_pass_start[7] = {0, 4, 0, 2, 0, 1, 0}`
- `png_pass_inc[7] = {8, 8, 4, 4, 2, 2, 1}`
- `png_pass_width[7] = {8, 4, 4, 2, 2, 1, 1}`

It also defines many 64-bit masks used by inline MMX routines, including masks for 8/16/24/32/48-bit row combining and filter masks such as `_LBCarryMask`, `_HBClearMask`, `_ActiveMask`, `_ShiftBpp`, and `_ShiftRem`.

When `PNG_THREAD_UNSAFE_OK` is enabled, several globals are used as scratch state for inline assembly:

- `_unmask`
- `_FullLength`
- `_MMXLength`
- `_dif`
- `_patemp`
- `_pbtemp`
- `_pctemp`

The file explicitly warns that these globals can defeat libpng thread safety.

## Row Combining Behavior

`png_combine_row()` first lazily initializes MMX support if `_mmx_supported == 2`. If `mask == 0xff`, it performs a straight `png_memcpy()` from `row_buf + 1` to the output row using `PNG_ROWBYTES()`.

For partial masks, it switches on `png_ptr->row_info.pixel_depth`:

- 1, 2, 4 bits: C bit-manipulation paths that honor `PNG_PACKSWAP`.
- 8, 16, 24, 32, 48 bits: optional MMX paths under assembler/thread-unsafe conditions, with C fallbacks.
- 64 bits: C path only.
- default: emits `png_warning(..., "Invalid row_info.pixel_depth in pnggccrd")`.

The MMX paths operate in groups of eight pixels using precomputed byte masks and then handle leftover pixels. The C fallbacks compute pass-dependent `initial_val`, `stride`, and `rep_bytes` from the Adam7 pass tables.

## Interlace Expansion Behavior

`png_do_read_interlace()` expands the current interlace pass in place inside `png_ptr->row_buf + 1` and updates:

- `row_info->width = final_width`
- `row_info->rowbytes = PNG_ROWBYTES(row_info->pixel_depth, final_width)`

For sub-byte depths 1, 2, and 4, it walks backward through packed pixels, replicating values according to `png_pass_inc[pass]` while honoring `PNG_PACKSWAP`.

For byte-aligned pixels, it calculates `pixel_bytes = row_info->pixel_depth >> 3`, points `sptr` at the last pre-expanded pixel and `dp` at the last expanded pixel position, then expands backward. MMX paths exist for pixel sizes 1, 2, 3, 4, and 8 bytes, with C handling for 6-byte pixels and generic fallback cases.

## Filter Reconstruction Behavior

`png_read_filter_row()` handles standard PNG filters:

- `PNG_FILTER_VALUE_NONE`: no-op.
- `PNG_FILTER_VALUE_SUB`: reconstructs each byte by adding the byte `bpp` positions to the left.
- `PNG_FILTER_VALUE_UP`: adds the corresponding byte from `prev_row`.
- `PNG_FILTER_VALUE_AVG`: adds the floor average of left and prior bytes.
- `PNG_FILTER_VALUE_PAETH`: computes the Paeth predictor from left, above, and upper-left bytes.

For each filter except `None`, the dispatcher uses MMX only when the relevant `png_ptr->asm_flags` bit is set and the row meets `mmx_bitdepth_threshold` and `mmx_rowbytes_threshold`. Otherwise, it uses straightforward C loops.

The MMX helpers perform alignment prologues, 8-byte or 64-byte vector loops, and scalar cleanup loops, ending with `EMMS` before returning to normal code.

## CPU Feature Detection

`png_mmx_support()` uses inline assembly to:

1. Save `ebx`, `ecx`, and `edx`.
2. Test whether the EFLAGS ID bit can be toggled.
3. Use `cpuid` to verify feature leaf availability.
4. Check EDX bit 23 for MMX.
5. Store the result in `_mmx_supported`.

If `PNG_MMX_CODE_SUPPORTED` is not defined, it sets `_mmx_supported = 0`.

## Dependencies

Internal libpng structures and APIs used here include:

- `png_structp`, `png_row_infop`, `png_bytep`
- `png_ptr->row_buf`, `row_info`, `width`, `pass`, `transformations`
- `png_ptr->asm_flags`, `mmx_bitdepth_threshold`, `mmx_rowbytes_threshold`
- `PNG_ROWBYTES`, `png_memcpy`, `png_warning`, `png_debug`

The code assumes 32-bit x86 GCC inline assembly syntax and uses registers such as `eax`, `ebx`, `ecx`, `edx`, `esi`, `edi`, plus MMX registers `mm0` through `mm7`.

## Notable Risks

- The optimized paths are not thread-safe when `PNG_THREAD_UNSAFE_OK` is enabled because global scratch variables are shared.
- The inline assembly is 32-bit x86-specific and relies on old GCC/GAS behavior.
- The file has extensive comments documenting historical PIC/`ebx` issues, GCC operand-limit problems, and partially tested paths.
- Several comments mark untested or incomplete areas, including 64-bit interlace cases and missing 48-bit MMX interlace support.
- The code predates modern compiler, sanitizer, and CPU feature-dispatch practices, so portability risk is high.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/libpng/pnggccrd.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/libpng/pngget.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/libpng/pngget.c

## Purpose

`pngget.c` implements libpng 1.2.8 getter APIs for reading fields from `png_struct` and `png_info`. It exposes image metadata, ancillary chunk data, user limits, unknown chunks, text chunks, MMX/assembler capability flags, and simple convenience conversions.

The file is almost entirely API glue: validate pointers and `info_ptr->valid` flags, copy internal fields into caller-provided outputs, and return either `0`, `1`, a chunk-validity flag, or a count.

## Basic Getters

Always-present or broadly enabled getters include:

- `png_get_valid(...)`: returns `info_ptr->valid & flag`.
- `png_get_rowbytes(...)`: returns `info_ptr->rowbytes`.
- `png_get_channels(...)`: returns `info_ptr->channels`.
- `png_get_signature(...)`: returns `info_ptr->signature`.
- `png_get_IHDR(...)`: returns core IHDR fields and validates bit depth, color type, width, and height.

Under `PNG_INFO_IMAGE_SUPPORTED`, `png_get_rows(...)` returns `info_ptr->row_pointers`.

Under `PNG_EASY_ACCESS_SUPPORTED`, easy-access getters return width, height, bit depth, color type, filter type, interlace type, compression type, physical resolution, pixel aspect ratio, offsets, and inch-based conversions.

## Chunk Getters

The file provides getters for common PNG chunks, each guarded by its feature macro:

- `bKGD`: `png_get_bKGD`
- `cHRM`: `png_get_cHRM`, `png_get_cHRM_fixed`
- `gAMA`: `png_get_gAMA`, `png_get_gAMA_fixed`
- `sRGB`: `png_get_sRGB`
- `iCCP`: `png_get_iCCP`
- `sPLT`: `png_get_sPLT`
- `hIST`: `png_get_hIST`
- `oFFs`: `png_get_oFFs`
- `pCAL`: `png_get_pCAL`
- `sCAL`: `png_get_sCAL` or `png_get_sCAL_s`
- `pHYs`: `png_get_pHYs`, plus `png_get_pHYs_dpi` when inch conversions and floating point are enabled
- `PLTE`: `png_get_PLTE`
- `sBIT`: `png_get_sBIT`
- `tEXt`/text family: `png_get_text`
- `tIME`: `png_get_tIME`
- `tRNS`: `png_get_tRNS`
- unknown chunks: `png_get_unknown_chunks`

Most chunk getters check both `png_ptr` and `info_ptr`, verify the corresponding `PNG_INFO_*` valid bit, then populate output pointers if supplied.

## Convenience Conversions

Resolution and offset helpers include:

- pixels per meter getters for X/Y/both
- pixels per inch getters using `pixels_per_meter * .0254 + .5`
- micron-to-inch offset getters using `microns * .00003937`
- `png_get_pixel_aspect_ratio(...)`, returning Y pixels per unit divided by X pixels per unit

These helpers return zero when the relevant chunk is missing, the unit is not the expected meter/micrometer unit, or input pointers are null.

## Runtime/Configuration Getters

The tail of the file exposes runtime and configuration state:

- `png_get_rgb_to_gray_status(...)`
- `png_get_user_chunk_ptr(...)`
- `png_get_compression_buffer_size(...)`
- `png_get_asm_flags(...)`
- `png_get_asm_flagmask(...)`
- `png_get_mmx_flagmask(...)`
- `png_get_mmx_bitdepth_threshold(...)`
- `png_get_mmx_rowbytes_threshold(...)`
- `png_get_user_width_max(...)`
- `png_get_user_height_max(...)`

`png_get_asm_flagmask()` and `png_get_mmx_flagmask()` report theoretically settable read-side MMX flags for combine row, interlace, and the four row filters. `png_get_mmx_flagmask()` can also identify the compiled assembler backend: MSVC, GCC/GAS, or unknown.

## Error And Validation Behavior

`png_get_IHDR()` is stricter than most getters. It calls `png_error()` for invalid bit depth, invalid color type, zero/oversized image dimensions, and warns if the width is too large for libpng row processing.

Most other getters return `0` or `NULL` for missing data. Some return the chunk flag only when they actually wrote at least one caller output.

## Dependencies

This file depends on `png.h` with `PNG_INTERNAL` defined and directly reads fields from `png_struct` and `png_info`, including:

- dimensions and row layout fields
- palette and transparency storage
- color-management chunk values
- physical resolution and offset values
- text and unknown chunk arrays
- assembler/MMX configuration fields
- user width/height limits

## Notable Risks

- `png_get_sPLT()` and `png_get_unknown_chunks()` return counts from `info_ptr` even if `info_ptr` is null, so callers must not pass null there despite the partial guard.
- `png_get_PLTE()` checks `palette != NULL` but writes `*num_palette` without checking `num_palette`.
- Several getters expose internal pointers rather than copies, which matches libpng 1.2 API style but means callers observe libpng-owned storage.
- The assembler/MMX getters are tied to the older libpng 1.2 runtime flag model used by `pnggccrd.c`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/libpng/pngget.c -->