# Group Research: group_90_9front_sources_os_plan9_9front_sys_src_cmd_gs_libpng_png_h_sources_os_3cbb926c4560

Scope: `Docs/research_subset_a.md`, source tree `sources/os/plan9/9front`.

Read completely:
- `sources/os/plan9/9front/sys/src/cmd/gs/libpng/png.h`
- `sources/os/plan9/9front/sys/src/cmd/gs/libpng/pngconf.h`
- `sources/os/plan9/9front/sys/src/cmd/gs/libpng/pngerror.c`

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/libpng/png.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/libpng/png.h

Primary libpng 1.2.8 public/internal API header vendored under the 9front Ghostscript `libpng` tree. It defines the PNG library version contract, public data structures, exported functions, constants, transformation flags, and private prototypes used when building libpng itself.

Key elements:
- Declares libpng version `1.2.8`, header version string, DLL number `13`, build status flags, and numeric version macro `PNG_LIBPNG_VER 10208`.
- Includes `zlib.h` for compression types and `pngconf.h` for platform configuration, feature switches, typedefs, linkage macros, and setjmp/stdio behavior.
- Defines libpng public data structures:
  - `png_color`, `png_color_16`, `png_color_8`
  - `png_sPLT_entry`, `png_sPLT_t`
  - `png_text`
  - `png_time`
  - `png_unknown_chunk`
  - `png_info`
  - `png_row_info`
  - `png_struct_def`
- `png_info` stores image metadata and ancillary chunk state, with many conditional fields controlled by `PNG_*_SUPPORTED` feature macros.
- `png_struct_def` stores active read/write state: error callbacks, I/O callbacks, zlib stream, dimensions, row buffers, chunk/CRC state, transform flags, gamma tables, progressive-read buffers, user chunk handlers, optional user memory callbacks, MMX/assembler thresholds, and user dimension limits.
- Defines PNG constants for color types, compression/filter/interlace methods, ancillary chunk units, sRGB intents, info-valid bit flags, transform masks, CRC actions, filter selection, MNG feature flags, unknown chunk policies, assembler/MMX flags, and internal mode/transform flags.
- Declares the main public lifecycle functions:
  - version/signature checks: `png_access_version_number`, `png_sig_cmp`, `png_check_sig`
  - allocation/init: `png_create_read_struct`, `png_create_write_struct`, `png_create_info_struct`, legacy `png_read_init_*`/`png_write_init_*`
  - read/write flow: `png_read_info`, `png_read_update_info`, `png_read_row(s)`, `png_read_image`, `png_read_end`, `png_write_info`, `png_write_row(s)`, `png_write_image`, `png_write_end`
  - teardown: `png_destroy_read_struct`, `png_destroy_write_struct`, `png_destroy_info_struct`
- Declares transform configuration APIs including expansion, palette-to-RGB, grayscale/RGB conversion, alpha/filler handling, byte swap, packing, interlace handling, background composition, dithering, gamma correction, filtering, compression parameters, and flush control.
- Declares callback override APIs for stdio I/O, custom read/write functions, error/warning handlers, row status callbacks, user memory allocation, user transforms, user chunks, and progressive reading.
- Declares `png_get_*`/`png_set_*` metadata accessors for IHDR, PLTE, bKGD, cHRM, gAMA, hIST, oFFs, pCAL, pHYs, sBIT, sRGB, iCCP, sPLT, text chunks, tIME, tRNS, sCAL, unknown chunks, row pointers, and convenience image fields.
- Under `PNG_INTERNAL`, declares private helpers for allocation, zlib allocation callbacks, default I/O callbacks, CRC handling, endian read/write helpers, chunk writers, row filtering, row transforms, chunk handlers, progressive reader internals, MNG intrapixel transforms, and assembler/MMX initialization.

Dependencies:
- Directly includes `zlib.h` unless `PNG_VERSION_INFO_ONLY` is defined.
- Directly includes `pngconf.h`.
- Relies on `pngconf.h` for `png_uint_32`, `png_size_t`, `png_byte`, `PNG_EXPORT`, `PNGAPI`, `PNGARG`, `PNG_SETJMP_SUPPORTED`, `PNG_FLOATING_POINT_SUPPORTED`, read/write feature macros, and platform calling conventions.
- Public declarations are implemented across the rest of libpng: `png.c`, `pngread.c`, `pngwrite.c`, `pngget.c`, `pngset.c`, `pngrio.c`, `pngwio.c`, `pngrutil.c`, `pngwutil.c`, `pngrtran.c`, `pngwtran.c`, `pngmem.c`, `pngerror.c`, and optional assembler sources.

Research notes:
- This old libpng header exposes the full `png_struct_def` and `png_info` layouts, so compile-time feature macros affect ABI size and binary compatibility. The comments repeatedly warn applications to prefer accessor functions over direct struct access.
- The header serves both applications and libpng internals. Public symbols use `PNG_EXPORT`, while private prototypes under `PNG_INTERNAL` use `PNG_EXTERN`.
- Many APIs are retained for legacy compatibility, including deprecated direct init macros and compatibility with libpng 1.0.x feature selection.
- The header supports both floating-point and fixed-point color/gamma APIs; fixed-point remains available unless explicitly disabled.
- Security/resource guardrails include `PNG_USER_WIDTH_MAX`, `PNG_USER_HEIGHT_MAX`, `png_set_user_limits`, bounded `PNG_UINT_31_MAX`, checked memcpy/memset declarations, and CRC policy controls.
- The bundled version predates modern libpng hardening and API opacity; consumers should treat it as a historical compatibility dependency rather than a current libpng API model.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/libpng/png.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/libpng/pngconf.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/libpng/pngconf.h

Machine and build configuration header for libpng 1.2.8. It selects supported libpng features, includes platform headers, defines core libpng scalar/pointer types, and normalizes export/calling-convention macros across C, Windows, Cygwin, OS/2, DOS memory models, and normal Unix-like builds.

Key elements:
- Defines `PNG_1_2_X`.
- Optionally includes `pngusr.h` when `PNG_USER_CONFIG` is supplied.
- Documents private DLL metadata macros such as `PNG_USER_PRIVATEBUILD`, `PNG_USER_DLLFNAME_POSTFIX`, and version-info strings.
- Sets default compression buffer size `PNG_ZBUF_SIZE 8192`.
- Enables read and write support by default unless `PNG_NO_READ_SUPPORTED` or `PNG_NO_WRITE_SUPPORTED` is defined.
- Enables MNG features, floating-point support, fixed-point support, free-me ownership tracking, easy accessors, user memory callbacks, user limits, error numbers, and most read/write transforms by default unless explicitly disabled.
- Handles platform headers and feature availability:
  - includes `stdio.h` unless `PNG_NO_STDIO` or Windows CE restrictions apply
  - includes `setjmp.h` when `PNG_SETJMP_SUPPORTED`
  - includes `string.h` or `strings.h`
  - includes `math.h`/Mac `fp.h` under internal floating-point builds
  - includes `time.h` when tIME support requires it
  - includes memory/model headers for older DOS/Windows compilers
- Defines feature-selection cascades for:
  - read transforms: expand, shift, pack, BGR, swap, packswap, invert, dither, background, 16-to-8, filler, gamma, gray-to-RGB, alpha operations, user transform, RGB-to-gray
  - write transforms: shift, pack, BGR, swap, packswap, invert, filler, alpha operations, user transform
  - progressive read and read/write interlacing
  - ancillary chunks: bKGD, cHRM, gAMA, hIST, iCCP, iTXt, oFFs, pCAL, pHYs, sBIT, sCAL, sPLT, sRGB, tEXt, tIME, tRNS, zTXt, unknown chunks, user chunks
- Defines `PNG_LEGACY_SUPPORTED` behavior that disables newer fields/features to preserve older structure sizes.
- Defines core libpng types:
  - `png_uint_32`, `png_int_32`, `png_uint_16`, `png_int_16`, `png_byte`
  - `png_size_t`
  - pointer typedefs such as `png_voidp`, `png_bytep`, `png_charp`, `png_const_charp`, `png_doublep`, pointer-to-pointer variants, and zlib aliases
  - `png_fixed_point`
  - `png_FILE_p`
- Defines `FAR`, `FARDATA`, and far/near memory helper macros for old segmented-memory compilers.
- Configures DLL/static linkage and symbol export macros:
  - `PNG_DLL`, `PNG_BUILD_DLL`, `PNG_USE_DLL`, `PNG_STATIC`
  - `PNGAPI`
  - `PNG_IMPEXP`
  - `PNG_EXPORT`
  - `PNG_EXPORT_VAR`
- Defines `png_jmpbuf`, `PNG_ABORT`, string/memory wrapper macros (`png_memcpy`, `png_strncpy`, etc.), and MMX threshold defaults for internal read builds.
- Caps `PNG_ZBUF_SIZE` at 64 KiB when `PNG_MAX_MALLOC_64K` is active.

Dependencies:
- May include user configuration file `pngusr.h`.
- Supplies definitions consumed by `png.h` and every libpng source file.
- Depends on standard headers according to feature/platform switches: `stdio.h`, `setjmp.h`, `string.h`/`strings.h`, `stdlib.h`, `math.h`, `time.h`, and platform-specific Windows/DOS/Mac headers.
- Depends on zlib typedefs already visible through `zlib.h` before the zlib alias typedef section.

Research notes:
- This file is the central compile-time ABI switchboard. Changing feature macros can add/remove fields from `png_info` and `png_struct_def`, which is unsafe for shared-library compatibility with applications compiled against different settings.
- The default configuration is broad: read/write support, transforms, ancillary chunks, progressive read, unknown chunks, user memory, and user limits are mostly enabled.
- `PNG_NO_STDIO` disables more than console messages; it also affects default file I/O APIs and some time/scale support paths.
- The Windows/Cygwin export handling is historical and complex, reflecting libpng’s cross-platform DLL/static build constraints in the 1.2 era.
- Plan 9/9front-specific logic is not present; this vendored header relies on the surrounding Ghostscript/libpng build to supply compatible C library and zlib behavior.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/libpng/pngconf.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/libpng/pngerror.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/libpng/pngerror.c

Implements libpng 1.2.8 error and warning dispatch. It provides the public `png_error`, `png_warning`, chunk-prefixed variants, default stderr/longjmp behavior, and registration/accessor functions for application-provided error handlers.

Key elements:
- Defines `PNG_INTERNAL` before including `png.h`, enabling private struct fields, internal flags, and private prototypes.
- Declares private defaults:
  - `png_default_error`
  - `png_default_warning`
- `png_error(png_ptr, error_message)` handles fatal errors:
  - optionally strips numeric prefixes and/or error text when `PNG_ERROR_NUMBERS_SUPPORTED` and strip flags are set
  - calls `png_ptr->error_fn` when provided
  - always falls back to `png_default_error` if the custom handler is absent or returns
- `png_warning(png_ptr, warning_message)` handles non-fatal warnings:
  - strips numeric prefixes when configured
  - calls `png_ptr->warning_fn` when provided
  - otherwise calls `png_default_warning`
- `png_format_buffer` prefixes diagnostics with the current `png_ptr->chunk_name`, escaping non-alphabetic chunk-name bytes as bracketed hex pairs and limiting appended message text.
- `png_chunk_error` and `png_chunk_warning` build chunk-prefixed messages and dispatch through `png_error`/`png_warning`.
- `png_default_error`:
  - prints to `stderr` unless `PNG_NO_CONSOLE_IO`
  - supports formatted numbered errors when `PNG_ERROR_NUMBERS_SUPPORTED`
  - calls `longjmp(png_ptr->jmpbuf, 1)` when setjmp support is enabled
  - otherwise calls `PNG_ABORT()` if `png_ptr` is present
- `png_default_warning` prints warning messages to `stderr` unless console I/O is disabled.
- `png_set_error_fn` stores application error pointer, fatal error callback, and warning callback in `png_struct`.
- `png_get_error_ptr` returns the stored application error pointer.
- `png_set_strip_error_numbers` exists when `PNG_ERROR_NUMBERS_SUPPORTED` is enabled and is intended to configure stripping of numbered error metadata.

Dependencies:
- Includes `png.h` with `PNG_INTERNAL`.
- Uses `png_struct` fields from `png.h`: `flags`, `error_fn`, `warning_fn`, `error_ptr`, `chunk_name`, and `jmpbuf`.
- Uses macros and functions from `pngconf.h`: `PNGAPI`, `PNGARG`, `PNG_CONST`, `png_strncpy`, `png_memcpy`, `png_sizeof`, `PNG_ABORT`, and `PNG_SETJMP_SUPPORTED`.
- Uses `fprintf(stderr, ...)` unless console I/O is disabled.
- Uses `longjmp` through setjmp support unless setjmp is disabled.

Research notes:
- Fatal error callbacks must not return. If they do return, libpng intentionally invokes the default fatal handler, which exits via longjmp or abort.
- `png_format_buffer` assumes `png_ptr` and its `chunk_name` are valid; callers use it for current-chunk diagnostics.
- Default warning behavior is non-fatal and only logs when console I/O is enabled.
- Potential defect: `png_set_strip_error_numbers` masks `png_ptr->flags` with `((~strip_flags) & strip_mode)`, which can clear unrelated flags and does not straightforwardly set the requested strip flags. This is worth checking before relying on that API in this vendored copy.
- Error handling depends on the application setting a valid setjmp target before libpng calls that may fail; otherwise the default fatal path may jump into uninitialized state or abort depending on build configuration.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/libpng/pngerror.c -->