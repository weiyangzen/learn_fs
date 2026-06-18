# Group Research: group_140_9front_sources_os_plan9_9front_sys_src_cmd_gs_src_jconfig0_h_sources_6b72bc1cbbd9

Scope: `Docs/research_subset_a.md`, source tree `sources/os/plan9/9front`.

This group covers Ghostscript's bundled Independent JPEG Group integration headers and make rules under `sys/src/cmd/gs/src`. The files are portability/configuration glue plus the IJG v6b public API surface used by Ghostscript's local JPEG build or by optional shared-system JPEG headers.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/jconfig0.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/jconfig0.h

Generated-style Ghostscript JPEG configuration header used when `SHARE_JPEG=0`. It is not only IJG `jconfig.h`; it is a concatenation of Ghostscript portability headers (`stdpn.h`, `stdpre.h`) and `gsjconf.h`, arranged this way because `jpeg.mak` builds IJG sources in a directory layout where the normal Ghostscript include order is not available.

The first section defines deprecated `P0` through `P16` prototype-list macros. They now expand directly to ANSI prototype lists and exist only for old Ghostscript source compatibility.

The `stdpre` portion normalizes compiler and platform feature macros, including `__MSDOS__`, `__OSF__`, `SYSV`, `__SVR3`, and `__PROTOTYPES__`. It provides fallback `__FILE__`/`__LINE__`, manages `const`, `volatile`, and `inline`, defines `extern_inline` support for GCC, and supplies generic portability macros such as `DISCARD`, `size_of`, `countof`, `offset_of`, `ALIGNMENT_MOD`, pointer-order comparisons, `min`, `max`, `ROUND_UP`, and `ROUND_DOWN`.

It also establishes Ghostscript common scalar types and conventions: `byte`, `uchar`, `ushort`, `uint`, `ulong`, `bool`, `true`, `false`, `floatp`, `client_name_t`, `public`, `private`, `BEGIN`, `END`, `DO_NOTHING`, and portable `exit_OK`/`exit_FAILED`. The header temporarily renames `bool` and unsigned typedef names before including `<sys/types.h>` to avoid conflicts.

The final `gsjconf.h` portion is the actual IJG configuration. It includes `arch.h`, maps Ghostscript prototype detection to IJG `HAVE_PROTOTYPES`, enables `HAVE_UNSIGNED_CHAR` and `HAVE_UNSIGNED_SHORT`, conditionally enables `HAVE_STDDEF_H` and `HAVE_STDLIB_H`, and undefines `CHAR_IS_UNSIGNED`, `NEED_BSD_STRINGS`, `NEED_SYS_TYPES_H`, `NEED_FAR_POINTERS`, `NEED_SHORT_EXTERNAL_NAMES`, and `INCOMPLETE_TYPES_BROKEN`.

JPEG-internal settings depend on Ghostscript architecture macros: `MAX_ALLOC_CHUNK` is reduced on systems with 16-bit-or-smaller `int`, and `RIGHT_SHIFT_IS_UNSIGNED` is set only when `ARCH_ARITH_RSHIFT == 0`.

Notable dependencies:
- Includes `<sys/types.h>` inside the portability section.
- Includes `arch.h` for Ghostscript architecture sizing and arithmetic-shift configuration.
- Expected to be generated/copied as `jconfig.h` by `jpeg.mak`.

Filesystem relevance: indirect. This is part of the Plan 9/9front Ghostscript userland build, specifically image codec configuration for PostScript/PDF processing, not kernel filesystem logic.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/jconfig0.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/jerror_.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/jerror_.h

Small Ghostscript wrapper for IJG `jerror.h`. It exists to make the include target depend on the build choice represented by `SHARE_JPEG`.

Behavior:
- If `SHARE_JPEG` is true, it includes the system/shared JPEG header with `<jerror.h>`.
- Otherwise, it includes the local vendored header with `"jerror.h"`.
- The include guard is `jerror__INCLUDED`.

The wrapper lets other Ghostscript makefile/header rules depend on `jerror_.h` without hardcoding whether JPEG is built locally or supplied externally.

Filesystem relevance: none directly. It is build-time codec plumbing in the 9front Ghostscript source tree.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/jerror_.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/jinclude.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/jinclude.h

IJG internal support header that centralizes system includes and standard-library compatibility macros for the JPEG implementation. It is intended for JPEG library source files, not for applications, which should include `jpeglib.h`.

The header starts by including `jconfig.h` and defining `JCONFIG_INCLUDED` so `jpeglib.h` does not include configuration a second time. Based on `jconfig.h`, it optionally includes `<stddef.h>`, `<stdlib.h>`, and `<sys/types.h>`, then unconditionally includes `<stdio.h>` because the public API exposes `FILE *` in the stdio source/destination managers.

It selects memory helper macros from either BSD or ANSI/System V string APIs:
- With `NEED_BSD_STRINGS`, includes `<strings.h>` and maps `MEMZERO` to `bzero`, `MEMCOPY` to `bcopy`.
- Otherwise, includes `<string.h>` and maps `MEMZERO` to `memset`, `MEMCOPY` to `memcpy`.

It defines `SIZEOF(object)` as a `size_t`-cast wrapper around `sizeof`, and wraps stdio byte I/O as `JFREAD(file, buf, sizeofbuf)` and `JFWRITE(file, buf, sizeofbuf)`, preserving IJG's argument order while casting counts and pointers consistently.

Notable dependencies:
- `jconfig.h`, generated from `jconfig0.h` or a shared-JPEG stub by `jpeg.mak`.
- Standard C headers selected by the generated configuration.

Filesystem relevance: none directly. It affects JPEG file stream I/O through `FILE *`, but not Plan 9 filesystem internals.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/jinclude.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/jmcorig.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/jmcorig.h

Original IJG `jmorecfg.h` configuration body for JPEG library data types and compile-time feature switches. Ghostscript keeps this as the upstream baseline and then wraps it with `jmorecf0.h`/`jmorecfg.h` to disable or adjust selected features.

Core image/data type settings:
- `BITS_IN_JSAMPLE` is set to `8`, selecting 8-bit JPEG sample values.
- `MAX_COMPONENTS` is set to `10`.
- `JSAMPLE`, `JOCTET`, `UINT8`, `UINT16`, `INT16`, `INT32`, and `JDIMENSION` are selected from C scalar types based on `HAVE_UNSIGNED_CHAR`, `CHAR_IS_UNSIGNED`, and `HAVE_UNSIGNED_SHORT`.
- `JCOEF` is `short`, `JPEG_MAX_DIMENSION` is `65500L`, and `GETJSAMPLE`/`GETJOCTET` mask signed chars when needed.

It defines IJG linkage and declaration macros:
- `METHODDEF`, `LOCAL`, `GLOBAL`, and `EXTERN` for static/global linkage.
- `JMETHOD` for function-pointer methods with or without prototypes.
- `FAR` for old 80x86 far-pointer builds, controlled by `NEED_FAR_POINTERS`.
- `boolean`, `FALSE`, and `TRUE` unless already supplied by the including application.

When `JPEG_INTERNALS` or `JPEG_INTERNAL_OPTIONS` is defined, it exposes library feature switches. The baseline enables integer and floating DCT variants, progressive and multiscanner encoder/decoder support, entropy optimization, input smoothing, marker saving, block smoothing, IDCT scaling, upsample merging, and one/two-pass quantization. Arithmetic coding and upsample-stage scaling are disabled. RGB scanline ordering is standard `R,G,B` with `RGB_PIXELSIZE=3`.

Speed/portability knobs include `INLINE`, `MULTIPLIER`, and `FAST_FLOAT`, with GCC inline support and `float` selected when prototypes are available.

Ghostscript's wrapper later changes this baseline by undefining several encoder and decoder options and by increasing `D_MAX_BLOCKS_IN_MCU` for Adobe-compatible DCT filter input.

Filesystem relevance: none directly. It is codec compile-time configuration for the Ghostscript userland application.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/jmcorig.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/jmorecf0.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/jmorecf0.h

Ghostscript wrapper around the original IJG `jmorecfg.h` body. It includes `jmcorig.h`, then removes unneeded JPEG library features to reduce the local Ghostscript JPEG build and align it with Ghostscript's requirements.

Feature changes after including `jmcorig.h`:
- Undefines `DCT_IFAST_SUPPORTED`.
- Undefines `DCT_FLOAT_SUPPORTED` when `FPU_TYPE <= 0`.
- Undefines encoder multiscanner/progressive support, entropy optimization, and input smoothing.
- Keeps decoder multiscanner/progressive support because progressive JPEG is needed for PDF 1.3.
- Undefines block smoothing, IDCT scaling, upsample scaling, upsample merging, and both one-pass and two-pass color quantization.
- Defines `D_MAX_BLOCKS_IN_MCU` as `64` to read nonstandard Adobe-generated JPEG/DCT streams with more blocks per MCU than the default IJG limit.

The include guard is `gsjmorec_INCLUDED`. In this source snapshot, `jmorecf0.h` and `jmorecfg.h` are byte-identical.

Filesystem relevance: none directly. This is JPEG decoder/encoder feature trimming for Ghostscript.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/jmorecf0.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/jmorecfg.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/jmorecfg.h

Generated/copied Ghostscript wrapper for IJG `jmorecfg.h`. It is byte-identical to `jmorecf0.h` in this tree and has the same `gsjmorec_INCLUDED` include guard.

It includes `jmcorig.h`, then customizes the local JPEG build by disabling selected optional features and preserving only the decoder capabilities Ghostscript needs for PDF/PostScript input. The key retained behavior is progressive/multiscan decode support; the key Ghostscript-specific compatibility change is `D_MAX_BLOCKS_IN_MCU 64` for Adobe DCT streams.

Because it has the canonical name `jmorecfg.h`, public `jpeglib.h` includes this file directly. `jpeg.mak` produces it from `jmorecf0.h` when building with the local JPEG library.

Filesystem relevance: none directly. It is a generated/copied codec configuration header in userland Ghostscript.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/jmorecfg.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/jpeg.mak -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/jpeg.mak

Ghostscript makefile fragment for integrating the Independent JPEG Group library. It supports IJG versions `6`, `6a`, and `6b`, with `JVERSION` documented as the major/subversion selector and `SHARE_JPEG` choosing local compilation versus use of a shared JPEG library.

Required make variables are documented at the top: `GSSRCDIR`, `JSRCDIR`, `JGENDIR`, `JOBJDIR`, `JVERSION`, `SHARE_JPEG`, and `JPEG_NAME` when sharing. It defines source/generated/object prefixes `JSRC`, `JGEN`, `JOBJ`, `JO_`, names itself as `JPEG_MAK`, and defines `JCC` with include paths for generated Ghostscript headers and JPEG include flags.

The header-generation section is the important part for this group:
- `jconfig_.h` is copied from either `jconfig0.h` or `jconfig1.h` depending on `SHARE_JPEG`.
- `jconfig0.h` is generated by concatenating `stdpn.h`, `stdpre.h`, and `gsjconf.h`.
- `jconfig1.h` is a small shared-JPEG configuration stub generated by `echogs`.
- `jconfig.h` is copied from `jconfig0.h` for the local build.
- `jmorecf_.h` selects local/shared wrapper content.
- `jmorecf0.h` is generated by concatenating `gsjmorec.h` and the copied original `jmcorig.h`.
- `jmorecfg.h` is copied from `jmorecf0.h`.
- `jmcorig.h` is copied from the upstream JPEG source `jmorecfg.h`.
- `jinclude.h` and `jpeglib.h` are copied into the generated directory so IJG source files include Ghostscript-modified generated headers consistently.
- `jpeglib_.h` selects local/shared public API include behavior; `jpeglib0.h`/`jpeglib.h` copy the vendored header, and `jpeglib1.h` is a shared-header stub.

The comments explain why copying source/header files is necessary: different C compilers search the source file directory and `-I` paths in different orders, so Ghostscript forces IJG compilation to see its modified `jconfig.h` and `jmorecfg.h`.

Build outputs:
- `jpegc0.dev` contains common JPEG objects (`jcomapi`, `jutils`, `jmemmgr`, `jerror`).
- `jpege.dev` selects either shared JPEG or local encoder objects.
- `jpege6.dev` emits encoder object groups for IJG v6-like builds, including `jcapimin`, `jcapistd`, `jcinit`, `jccoefct`, `jccolor`, `jcdctmgr`, `jchuff`, `jcmainct`, `jcmarker`, `jcmaster`, `jcparam`, `jcprepct`, `jcsample`, and `jfdctint`.
- `jpegd.dev` selects shared JPEG or local decoder objects.
- `jpegd6.dev` emits decoder object groups including `jdapimin`, `jdapistd`, `jdcoefct`, `jdcolor`, `jddctmgr`, `jdhuff`, `jdinput`, `jdmainct`, `jdmarker`, `jdmaster`, `jdphuff`, `jdpostct`, `jdsample`, and `jidctint`.

`JDEP` intentionally over-approximates dependencies on generated config headers and copied headers, trading extra rebuilds for simpler maintenance. The clean targets are placeholders, with `jpeg.clean-not-config-clean` explicitly marked as needing selective generated/object deletion.

Filesystem relevance: indirect. It is userland build orchestration in the Plan 9/9front Ghostscript tree, not filesystem implementation.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/jpeg.mak -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/jpeglib.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/jpeglib.h

IJG v6b public application interface header for the JPEG library. It includes `jconfig.h` unless `JCONFIG_INCLUDED` was already set by `jinclude.h`, then includes `jmorecfg.h`. In this repository, `jpeglib.h`, `jpeglib0.h`, and `jpeglib_.h` are byte-identical.

The header declares JPEG standard constants and table limits, including `JPEG_LIB_VERSION 62`, `DCTSIZE`, quantization/Huffman table counts, arithmetic table count, scan component limits, sampling factor limits, `C_MAX_BLOCKS_IN_MCU`, and `D_MAX_BLOCKS_IN_MCU` with an override path from `jmorecfg.h`.

It defines public sample/coefficient array types:
- `JSAMPROW`, `JSAMPARRAY`, and `JSAMPIMAGE` for image samples.
- `JBLOCK`, `JBLOCKROW`, `JBLOCKARRAY`, and `JBLOCKIMAGE` for DCT coefficient blocks.
- `JCOEFPTR` for coefficient pointers.

It defines public JPEG data structures:
- `JQUANT_TBL` and `JHUFF_TBL` for quantization and Huffman tables.
- `jpeg_component_info` for per-component sampling, table selectors, computed dimensions, MCU layout, quantization table pointer, and DCT private storage.
- `jpeg_scan_info` for multiscanner/progressive scan scripts.
- `jpeg_marker_struct` and `jpeg_saved_marker_ptr` for saved APPn/COM markers.
- `J_COLOR_SPACE`, `J_DCT_METHOD`, and `J_DITHER_MODE` enums.

The main state records are `jpeg_common_struct`, `jpeg_compress_struct`, and `jpeg_decompress_struct`. `jpeg_common_fields` must remain prefix-identical across common, compressor, and decompressor records. The compressor struct contains destination manager, source image description, compression parameters, tables, scan script, restart settings, marker settings, progress state, computed MCU state, and module pointers. The decompressor struct contains source manager, image metadata, output parameters, quantization options, output dimensions, output progress, progressive status, tables, marker metadata, computed MCU state, unread marker state, and module pointers.

It declares application-visible module objects:
- `jpeg_error_mgr` for fatal error exit, warnings/tracing, formatting, reset, message tables, and warning counts.
- `jpeg_progress_mgr` for progress callback state.
- `jpeg_destination_mgr` and `jpeg_source_mgr` for buffered output/input callbacks.
- `jpeg_memory_mgr` for pooled allocation, virtual sample/block arrays, pool freeing, object destruction, memory limits, and allocation chunk limits.

The public API prototypes cover:
- Error setup: `jpeg_std_error`.
- Object creation/destruction: `jpeg_create_compress`, `jpeg_create_decompress`, `jpeg_CreateCompress`, `jpeg_CreateDecompress`, `jpeg_destroy_compress`, `jpeg_destroy_decompress`.
- Stdio source/destination managers.
- Compression parameter setup: defaults, colorspace, quality scaling, quantization table setup, progression, table suppression, table allocation.
- Compression execution: start, write scanlines/raw data, finish, marker writing, table-only output.
- Decompression execution: read header, start/read/finish scanlines, raw data, buffered-image mode, input consumption, output-dimension calculation.
- Marker save/processor hooks.
- Coefficient read/write and critical-parameter copying for transcoding.
- Abort/destroy common helpers and restart-marker resynchronization.

It exports JPEG marker codes `JPEG_RST0`, `JPEG_EOI`, `JPEG_APP0`, and `JPEG_COM`, result constants for header/input processing, optional short external-name remaps for limited linkers, and dummy incomplete-type definitions when `INCOMPLETE_TYPES_BROKEN` is set. If `JPEG_INTERNALS` is defined, it also includes `jpegint.h` and `jerror.h`.

Filesystem relevance: indirect. The API can read/write JPEG streams through `FILE *` managers, but this file is an image-codec API header for Ghostscript, not an OS/filesystem component.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/jpeglib.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/jpeglib0.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/jpeglib0.h

Local-build copy of the IJG v6b public application interface header. It is byte-identical to `jpeglib.h` and `jpeglib_.h` in this source tree. `jpeg.mak` uses this naming convention to distinguish the local vendored JPEG API (`0`) from a shared-system JPEG wrapper (`1`) before copying/selecting the final generated include target.

Semantically, this file exposes the same API as `jpeglib.h`: JPEG library version `62`, JPEG constants, sample and coefficient array types, quantization/Huffman tables, component and scan descriptors, saved marker structures, colorspace/DCT/dither enums, compressor/decompressor master structs, error/progress/source/destination/memory manager objects, public compression/decompression/transcoding functions, marker constants, and optional internal includes under `JPEG_INTERNALS`.

Important integration details:
- Includes `jconfig.h` and `jmorecfg.h`, so Ghostscript's generated configuration and wrapper feature choices control the public types and enabled code paths.
- `D_MAX_BLOCKS_IN_MCU` can be overridden by Ghostscript's `jmorecfg.h`, where this tree sets it to `64` for Adobe-compatible decoding.
- Stdio source/destination manager prototypes expose `FILE *`, tying this API to C stdio when those helpers are used.

Filesystem relevance: indirect only through stdio stream managers. The file is codec API surface, not filesystem code.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/jpeglib0.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/jpeglib_.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/jpeglib_.h

Selected/wrapper-name copy of the IJG v6b public application interface header. It is byte-identical to `jpeglib.h` and `jpeglib0.h` in this snapshot. The underscore name is part of Ghostscript's generated-header convention: `jpeg.mak` builds `jpeglib_.h` from either the local vendored header path or a shared-system JPEG include wrapper depending on `SHARE_JPEG`.

Because the content is the full local IJG public header here, it defines the complete libjpeg v6b API surface: configuration includes, version and JPEG constants, public sample/coefficient/table types, component/scan/marker structures, compressor and decompressor state records, manager callback structs, public entry points for compression, decompression, marker handling, raw coefficient I/O, lifecycle cleanup, and restart resynchronization.

The header is sensitive to Ghostscript-generated configuration:
- `jconfig.h` supplies portability and type feature macros.
- `jmorecfg.h` supplies datatype definitions and trims optional JPEG features.
- `JPEG_INTERNALS` switches the tail of the header from application-only declarations to include `jpegint.h` and `jerror.h` for JPEG library implementation files.

Filesystem relevance: indirect. It declares stdio-based source/destination setup functions but otherwise belongs to Ghostscript's embedded JPEG codec integration.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/jpeglib_.h -->