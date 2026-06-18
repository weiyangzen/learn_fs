# Group Research: group_1528_plan9_sources_os_plan9_plan9_sys_src_cmd_gs_libpng_png_h_sources_os_282fb11013e5

Scope checked against `Docs/research_subset_a.md`. All three listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/libpng/png.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/libpng/png.h

## Role

`png.h` is the main libpng 1.2.8 header bundled under Plan 9 Ghostscript’s `libpng` directory. It is not filesystem code; it is third-party image codec API and internal declaration surface used by Ghostscript’s PNG support.

The file combines public API declarations, public data structures, compile-time feature gates, and, when `PNG_INTERNAL` is defined, private libpng declarations used by the implementation `.c` files.

## Version And Build Identity

The header identifies libpng version `1.2.8`, dated December 3, 2004. Important version macros include:

- `PNG_LIBPNG_VER_STRING "1.2.8"`
- `PNG_HEADER_VERSION_STRING`
- `PNG_LIBPNG_VER_MAJOR 1`
- `PNG_LIBPNG_VER_MINOR 2`
- `PNG_LIBPNG_VER_RELEASE 8`
- `PNG_LIBPNG_VER 10208`
- `PNG_LIBPNG_VER_DLLNUM 13`

The top of the file contains a long compatibility history for libpng version numbers and shared-library numbering. This matters because later code exposes `png_access_version_number()`, `png_get_header_ver()`, `png_get_libpng_ver()`, and uses a typedef `version_1_2_8` to catch mismatches between `png.c` and `png.h`.

## Dependencies

`png.h` includes `zlib.h` unless `PNG_VERSION_INFO_ONLY` is defined, then includes `pngconf.h`. Almost every type, export macro, calling convention, optional feature macro, and portability typedef visible in this file comes from `pngconf.h`.

The header has `extern "C"` guards for C++ consumers.

## Public Data Types

The file defines the canonical libpng public types:

- `png_color`: 8-bit RGB palette entry.
- `png_color_16`: 16-bit/indexed color container used for transparency and background.
- `png_color_8`: significant-bit information per channel.
- `png_sPLT_entry` and `png_sPLT_t`: suggested palette chunk storage.
- `png_text`: text/zTXt/iTXt metadata, conditional on text support.
- `png_time`: PNG tIME chunk representation.
- `png_unknown_chunk`: private/unknown chunk retention structure.
- `png_info`: image metadata and optional ancillary chunk state.
- `png_row_info`: row transformation metadata.
- `png_struct`: opaque public handle typedef, with the actual `struct png_struct_def` exposed in this older libpng header.

The `png_info` structure records IHDR metadata, valid-chunk bit flags, palette, row byte count, optional chunk state, text, transparency, gamma/chromaticity, physical dimensions, ICC/sPLT/sCAL data, unknown chunks, and optionally full image row pointers.

The exposed `png_struct_def` is large and carries runtime state: error/warning callbacks, I/O callbacks, transform callbacks, zlib stream and compression settings, image dimensions, row buffers, CRC/chunk state, palette/transparency state, gamma tables, progressive-read buffers, dithering/filter state, optional user memory callbacks, MNG feature flags, assembler/MMX flags, and user width/height limits.

Because this old libpng version exposes struct layouts, binary compatibility depends on the exact feature macros used when building both the library and application.

## Constants And Flags

The header defines PNG format constants and libpng state flags, including:

- Color types: grayscale, palette, RGB, RGB+alpha, grayscale+alpha.
- Compression/filter/interlace constants.
- Ancillary chunk validity flags such as `PNG_INFO_gAMA`, `PNG_INFO_PLTE`, `PNG_INFO_tRNS`, `PNG_INFO_iCCP`, `PNG_INFO_sPLT`, `PNG_INFO_IDAT`.
- Transform masks such as `PNG_TRANSFORM_STRIP_16`, `PNG_TRANSFORM_EXPAND`, `PNG_TRANSFORM_BGR`, `PNG_TRANSFORM_SWAP_ENDIAN`.
- CRC handling modes for `png_set_crc_action()`.
- Filter constants and filter heuristic constants.
- Memory-free ownership flags such as `PNG_FREE_TEXT`, `PNG_FREE_PLTE`, `PNG_FREE_ALL`.
- Unknown chunk handling modes.
- Internal mode and transformation flags under `PNG_INTERNAL`.
- Internal row sizing macro `PNG_ROWBYTES(pixel_bits, width)`.

Chunk type names are defined as byte arrays under `PNG_INTERNAL`, including `IHDR`, `IDAT`, `IEND`, `PLTE`, `bKGD`, `cHRM`, `gAMA`, `iCCP`, `iTXt`, `pHYs`, `sRGB`, `tEXt`, `tIME`, `tRNS`, and `zTXt`.

## Public API Surface

The file declares the main libpng API families:

- Version and signature checks: `png_access_version_number()`, `png_sig_cmp()`, `png_check_sig()`.
- Object creation/destruction: `png_create_read_struct()`, `png_create_write_struct()`, `png_create_info_struct()`, destroy functions.
- Read/write setup: `png_init_io()`, `png_set_read_fn()`, `png_set_write_fn()`.
- Error handling: `png_set_error_fn()`, `png_get_error_ptr()`, `png_error()`, `png_warning()`, chunk-prefixed variants.
- Compression and filtering control: `png_set_filter()`, zlib level/method/window/memory/strategy setters.
- Transform setup: expand, BGR, gray/RGB conversion, strip alpha/16-bit, swap bytes, packing, gamma, background, filler, interlace handling, dithering.
- Sequential reading/writing: `png_read_info()`, `png_read_row(s)`, `png_read_image()`, `png_read_end()`, `png_write_info()`, `png_write_row(s)`, `png_write_image()`, `png_write_end()`.
- Progressive reading: callback registration and `png_process_data()`.
- Memory management: `png_malloc()`, `png_malloc_warn()`, `png_free()`, `png_free_data()`, optional custom allocators.
- Chunk get/set APIs for IHDR, PLTE, bKGD, cHRM, gAMA, hIST, iCCP, oFFs, pCAL, pHYs, sBIT, sCAL, sPLT, sRGB, text, tIME, tRNS, unknown chunks.
- High-level whole-image helpers: `png_read_png()` and `png_write_png()` when `PNG_INFO_IMAGE_SUPPORTED`.

## Internal API Surface

When `PNG_INTERNAL` is defined, this file also declares internal functions used across libpng implementation files:

- Struct allocation/init helpers.
- Default read/write callbacks and zlib allocator callbacks.
- CRC helpers.
- PNG integer load/store helpers.
- Chunk writers for core and ancillary chunks.
- Row lifecycle helpers.
- Read/write transformation functions.
- Chunk handlers for known chunks.
- Progressive-read internal state-machine functions.
- Optional MNG intrapixel and MMX/assembler hooks.

This means `.c` files such as `pngerror.c` include this header with `PNG_INTERNAL` to gain private flags like `PNG_FLAG_STRIP_ERROR_NUMBERS` and private structure visibility.

## Research Notes

For this repository’s filesystem research scope, the important conclusion is negative: this header does not implement storage, VFS, block I/O, or Plan 9 kernel behavior. Its relevance is as a vendored library dependency inside Plan 9’s Ghostscript tree. Any security or maintenance review should treat it as old libpng 1.2.8 API surface, with legacy exposed structs and feature macro ABI sensitivity.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/libpng/png.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/libpng/pngconf.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/libpng/pngconf.h

## Role

`pngconf.h` is libpng’s machine and build configuration header. It decides platform portability settings, feature availability, public typedefs, calling conventions, export macros, memory model macros, and default limits before `png.h` exposes the API.

This file is also not filesystem code. It is infrastructure for building the vendored libpng copy consistently on many C environments, including older DOS/Windows, Cygwin, Mac, OS/2, and generic Unix-like targets.

## Configuration Entry Points

The file defines `PNG_1_2_X` and optionally includes `pngusr.h` if `PNG_USER_CONFIG` is set. That allows downstream builds to override or disable libpng features without editing this file.

It supports `PNG_VERSION_INFO_ONLY`, which bypasses most typedefs and feature setup when only version metadata is needed.

Default core settings include:

- `PNG_ZBUF_SIZE 8192`
- `PNG_READ_SUPPORTED` unless `PNG_NO_READ_SUPPORTED`
- `PNG_WRITE_SUPPORTED` unless `PNG_NO_WRITE_SUPPORTED`
- `PNG_MNG_FEATURES_SUPPORTED` by default for non-1.0 builds
- `PNG_FLOATING_POINT_SUPPORTED` unless explicitly disabled
- `PNG_SETJMP_SUPPORTED` unless disabled
- `PNG_USER_WIDTH_MAX 1000000L`
- `PNG_USER_HEIGHT_MAX 1000000L`

## Platform And Library Includes

The header conditionally includes:

- `stdio.h` unless `PNG_NO_STDIO` or Windows CE limitations apply.
- `sys/types.h` on most non-Mac, non-RISCOS, non-Windows CE platforms.
- `setjmp.h` for libpng fatal error recovery.
- `string.h` or `strings.h`.
- `stdlib.h` and `math.h`/Mac `fp.h` only under `PNG_INTERNAL`.
- `time.h` if `PNG_tIME_SUPPORTED`.

For Linux with `_BSD_SOURCE`, it temporarily undefines `_BSD_SOURCE` around `setjmp.h` to force the desired setjmp behavior.

## Feature Matrix

The bulk of the file maps `PNG_NO_*` and `*_NOT_SUPPORTED` macros into positive `*_SUPPORTED` macros. Important default behavior:

- Read transforms are enabled by default: expand, shift, pack, BGR, swap, packswap, invert, dither, background, 16-to-8, filler, gamma, gray-to-RGB, alpha swaps/inversion/strip, user transform, RGB-to-gray.
- Progressive read support is enabled by default.
- Read interlacing support is always defined for PNG-compliant decoders.
- Write transforms are enabled by default: shift, pack, BGR, swap, packswap, invert, filler, alpha swaps/inversion, user transform.
- Write interlacing and flush support are enabled by default.
- Weighted filtering is enabled when floating point is available.
- Error-number support is enabled for non-1.0 builds.
- User memory callbacks and user limits are enabled for non-1.0 builds.

Ancillary chunk support is also enabled by default for read and write unless disabled as a group or per chunk. Supported chunk families include bKGD, cHRM, gAMA, hIST, iCCP, iTXt, oFFs, pCAL, sCAL, pHYs, sBIT, sPLT, sRGB, tEXt, tIME, tRNS, zTXt, unknown chunks, and user chunks.

`PNG_INFO_IMAGE_SUPPORTED` enables the `png_read_png()`/`png_write_png()` high-level helpers and `row_pointers` member in `png_info`.

## Public Typedefs

The file defines libpng’s base integer and pointer types:

- `png_uint_32` as `unsigned long`
- `png_int_32` as `long`
- `png_uint_16` as `unsigned short`
- `png_int_16` as `short`
- `png_byte` as `unsigned char`
- `png_size_t` as either configured `PNG_SIZE_T` or `size_t`
- `png_fixed_point` as `png_int_32`

It also defines `png_voidp`, byte/int/string pointer aliases, double pointer aliases, and `png_FILE_p` as `FILE *` or Windows CE `HANDLE`.

These typedefs are consumed throughout `png.h` and all implementation files.

## Export And Calling Convention Logic

The header defines `PNGAPI`, `PNG_IMPEXP`, `PNG_EXPORT`, and `PNG_EXPORT_VAR` across static, DLL, Windows, Cygwin, Borland/Microsoft, MinGW, and symbol-generation builds.

For ordinary non-Windows/non-DLL builds, `PNGAPI` and `PNG_IMPEXP` collapse to empty macros, so exported prototypes become normal C declarations.

The file also chooses between `PNG_USE_GLOBAL_ARRAYS` and `PNG_USE_LOCAL_ARRAYS`, with special behavior for Cygwin and DLL builds.

## Error And Memory Macros

`PNG_ABORT()` defaults to `abort()`.

If setjmp is supported, `png_jmpbuf(png_ptr)` maps to `png_ptr->jmpbuf`; otherwise it expands to an intentional compile-time failure marker.

The file abstracts string and memory operations through `png_strcpy`, `png_strncpy`, `png_strlen`, `png_memcmp`, `png_memcpy`, and `png_memset`. In normal builds these map to standard C functions; in far-memory builds they map to `_f*` variants.

It also defines `FAR`, `FARDATA`, and far pointer conversion macros for legacy segmented memory models.

## Internal/Assembler Configuration

Under `PNG_INTERNAL`, the file defines tunables for dithering and gamma:

- `PNG_DITHER_RED_BITS`, `PNG_DITHER_GREEN_BITS`, `PNG_DITHER_BLUE_BITS` default to `5`.
- `PNG_MAX_GAMMA_8` defaults to `11`.
- `PNG_GAMMA_THRESHOLD` defaults to `0.05`.

Read-side assembler support is enabled by default unless disabled. MMX code is enabled by default when assembler code is enabled. Default MMX thresholds are:

- `PNG_MMX_ROWBYTES_THRESHOLD_DEFAULT 128`
- `PNG_MMX_BITDEPTH_THRESHOLD_DEFAULT 9`

Actual assembler routines require build-specific defines such as `PNG_USE_PNGVCRD` or `PNG_USE_PNGGCCRD`.

## Research Notes

This file is the reason `png.h` has such a large conditional API and ABI surface. For any build/debugging work in this subtree, check `pngconf.h` and compile flags before assuming a symbol, structure field, or chunk handler exists.

For filesystem subset research, this is vendored codec configuration only. Its risk profile is portability and ABI drift, not filesystem semantics.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/libpng/pngconf.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/libpng/pngerror.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/libpng/pngerror.c

## Role

`pngerror.c` implements libpng’s error and warning handling. It defines `PNG_INTERNAL` before including `png.h`, so it can access internal `png_struct` fields and flags.

Despite the file comment saying “stub functions for i/o and memory allocation,” this file specifically centralizes fatal error dispatch, non-fatal warning dispatch, chunk-prefixed message formatting, default stderr reporting, setjmp/longjmp escape behavior, and error callback registration.

## Main Functions

`png_error(png_structp png_ptr, png_const_charp error_message)` handles fatal errors.

Its behavior is:

- Optionally strips libpng error numbers and/or text when `PNG_ERROR_NUMBERS_SUPPORTED` is enabled and `png_ptr->flags` contains `PNG_FLAG_STRIP_ERROR_NUMBERS` or `PNG_FLAG_STRIP_ERROR_TEXT`.
- Calls the user-supplied `png_ptr->error_fn` if present.
- Falls back to `png_default_error()` if no custom handler exists or if the custom handler returns.
- The default handler is expected not to return.

`png_warning(png_structp png_ptr, png_const_charp warning_message)` handles non-fatal warnings.

Its behavior is:

- Optionally skips a leading `#nnn ` warning number.
- Calls `png_ptr->warning_fn` if present.
- Otherwise calls `png_default_warning()`.

`png_chunk_error()` and `png_chunk_warning()` prepend the current chunk name from `png_ptr->chunk_name` before dispatching to the normal fatal/non-fatal handlers.

`png_set_error_fn()` installs user error and warning callbacks plus an opaque `error_ptr`.

`png_get_error_ptr()` returns that opaque pointer.

`png_set_strip_error_numbers()` is compiled when `PNG_ERROR_NUMBERS_SUPPORTED` is enabled and is intended to update strip-mode flags on `png_ptr`.

## Chunk Message Formatting

The private helper `png_format_buffer()` builds chunk-prefixed messages.

It reads four bytes from `png_ptr->chunk_name`. Alphabetic bytes are copied directly. Non-alphabetic bytes are encoded as hex in bracket form, using the local `png_digit` table. It then appends `": "` and up to 63 bytes of the supplied message via `png_strncpy`, forcing a terminator at `buffer[iout+63]`.

The local `isnonalpha(c)` macro treats ASCII `A-Z` and `a-z` as valid chunk-name characters.

This protects diagnostics from raw binary chunk-name bytes while preserving useful chunk context.

## Default Fatal Error Path

`png_default_error()` prints to `stderr` unless `PNG_NO_CONSOLE_IO` is defined.

If error-number support is enabled and the message begins with `#`, it attempts to parse a numeric prefix and prints either:

- `libpng error no. <number>: <message>`
- or a fallback malformed-prefix message.

Otherwise it prints:

- `libpng error: <message>`

For control flow:

- If `PNG_SETJMP_SUPPORTED` is enabled, it calls `longjmp(png_ptr->jmpbuf, 1)`.
- If `USE_FAR_KEYWORD` is enabled, it copies the jump buffer first, then longjmps through the copy.
- If setjmp support is disabled, it calls `PNG_ABORT()` when `png_ptr` is non-null.

Because libpng’s public pattern relies on callers setting `setjmp(png_jmpbuf(png_ptr))`, a fatal error normally unwinds back to application code rather than returning through the failed libpng call.

## Default Warning Path

`png_default_warning()` prints to `stderr` unless `PNG_NO_CONSOLE_IO` is defined.

With error-number support, it parses leading `#nnn ` warning prefixes similarly to fatal errors and prints a numbered warning when possible. Otherwise it prints a normal warning line.

Warnings return to the caller; they do not longjmp.

## Callback Contract

The file’s comments emphasize that replacement fatal error functions must not return. A custom error handler is expected to perform a longjmp or equivalent non-local exit. If it returns, `png_error()` intentionally invokes the default fatal handler afterward.

Replacement warning functions may return normally and may ignore messages.

## Notable Edge Case

`png_set_strip_error_numbers()` uses:

`png_ptr->flags &= ((~(PNG_FLAG_STRIP_ERROR_NUMBERS|PNG_FLAG_STRIP_ERROR_TEXT))&strip_mode);`

This expression clears flags through an AND operation rather than the more typical “clear then OR selected strip flags” pattern. As written, it can only preserve bits already present in both the inverted mask and `strip_mode`; it does not appear to set strip flags. This may be inherited upstream behavior or a bug in this bundled libpng version, but it is worth noting if diagnostics stripping is expected to work.

## Research Notes

This file has no filesystem behavior. Its main relevance to the broader source tree is failure control flow: libpng decode/encode errors can escape via `longjmp`, so callers in Ghostscript must establish the expected setjmp recovery path before invoking libpng operations.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/libpng/pngerror.c -->