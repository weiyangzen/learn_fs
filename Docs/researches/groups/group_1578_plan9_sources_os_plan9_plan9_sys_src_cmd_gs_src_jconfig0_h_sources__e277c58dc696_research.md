# Group Research: group_1578_plan9_sources_os_plan9_plan9_sys_src_cmd_gs_src_jconfig0_h_sources__e277c58dc696

Scope checked against `Docs/research_subset_a.md`: all files are under `sources/os/plan9/plan9`, which is included in subset A. All listed files were read completely. These files are Ghostscript’s vendored/build-adapted Independent JPEG Group v6b interface/configuration files inside the Plan 9 source tree, not filesystem code.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/jconfig0.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/jconfig0.h

## Identity

- Lines/bytes: 571 lines, 19,233 bytes.
- SHA-256: `22e46945a19903137379d8460420bb3de098d9e846bc1388dddd513bd177979a`.
- Role: generated-style Ghostscript `jconfig.h` source for IJG JPEG builds when Ghostscript compiles its private JPEG copy.

## Contents

This file is a concatenation of three Ghostscript headers:

- `stdpn.h`: deprecated `P0` through `P16` prototype-list macros retained for old Ghostscript source compatibility.
- `stdpre.h`: Ghostscript portability prelude defining compiler/platform feature macros, `inline`/`extern_inline`, `DISCARD`, `size_of`, `countof`, pointer comparison macros, unsigned short-name typedefs, `bool`/`true`/`false`, `BEGIN`/`END`, `public`/`private`, exit status macros, and inclusion of `stdpn.h`.
- `gsjconf.h`: Ghostscript’s IJG `jconfig.h` configuration, including `arch.h`, prototype support, unsigned type availability, standard-header availability under `__STDC__`, allocation chunk handling for small `int`, and right-shift behavior for JPEG internals.

## Dependencies

- Includes `sys/types.h` through the `stdpre.h` section.
- Includes `stdpn.h` through the `stdpre.h` section, although the file already contains a copy of `stdpn.h` at the front.
- Includes `arch.h` in the `gsjconf.h` section.
- Build rule in `jpeg.mak` constructs this from `stdpn.h`, `stdpre.h`, and `gsjconf.h`.

## Behavior And Integration

- Controls how IJG code sees compiler capabilities and platform details.
- Defines `HAVE_PROTOTYPES`, `HAVE_UNSIGNED_CHAR`, `HAVE_UNSIGNED_SHORT`, `HAVE_STDDEF_H`, and `HAVE_STDLIB_H`.
- Leaves BSD strings, sys/types need, far pointers, short external names, and incomplete-type workaround disabled.
- Defines `RIGHT_SHIFT_IS_UNSIGNED` only when `JPEG_INTERNALS` is set and `ARCH_ARITH_RSHIFT == 0`.
- On 16-bit or smaller `int`, lowers `MAX_ALLOC_CHUNK` to `0xfff0`.

## Research Notes

- This is infrastructure for Ghostscript’s bundled JPEG library, not Plan 9 kernel/VFS code.
- It is important because downstream IJG headers and sources rely on the generated `jconfig.h` for ABI-visible type and feature choices.
- The file’s concatenated structure exists because Ghostscript’s JPEG build copies/generated headers into an intermediate directory to force IJG sources to include Ghostscript’s configuration.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/jconfig0.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/jerror_.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/jerror_.h

## Identity

- Lines/bytes: 29 lines, 903 bytes.
- SHA-256: `40bc4f4073f2f63b9fc7e2b2dc477cdad06b85dee462f452d6ba7a29a17b4ec8`.
- Role: Ghostscript wrapper for IJG `jerror.h`.

## Contents

The file has a single include guard, `jerror__INCLUDED`, and chooses between:

- `<jerror.h>` when `SHARE_JPEG` is true.
- `"jerror.h"` when Ghostscript builds or uses its private JPEG headers.

## Dependencies

- Depends on build-time macro `SHARE_JPEG`.
- External/shared mode requires system JPEG headers.
- Private mode requires local IJG `jerror.h`.

## Behavior And Integration

This wrapper allows Ghostscript code to include a stable wrapper name while switching between shared-system JPEG and bundled JPEG builds.

## Research Notes

- No algorithms or state are defined here.
- Its main significance is build isolation and avoiding ambiguous header selection.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/jerror_.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/jinclude.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/jinclude.h

## Identity

- Lines/bytes: 91 lines, 3,250 bytes.
- SHA-256: `a6433e5ea0030f4bffd41bcc2f064008afd79de4270cf28494bd43d2fbc5da06`.
- Role: IJG internal include-normalization header.

## Contents

The file:

- Includes `jconfig.h` and sets `JCONFIG_INCLUDED`.
- Pulls in standard headers based on `HAVE_STDDEF_H`, `HAVE_STDLIB_H`, and `NEED_SYS_TYPES_H`.
- Always includes `stdio.h` because public IJG API declarations reference `FILE`.
- Provides `MEMZERO` and `MEMCOPY` using either BSD `bzero`/`bcopy` or ANSI/SysV `memset`/`memcpy`.
- Defines `SIZEOF(object)` as a `size_t` casted `sizeof`.
- Defines `JFREAD` and `JFWRITE` wrappers around `fread`/`fwrite`.

## Dependencies

- Requires `jconfig.h`.
- May include `stddef.h`, `stdlib.h`, `sys/types.h`, `stdio.h`, `strings.h`, or `string.h` depending on configuration macros.

## Behavior And Integration

- Used by IJG implementation files, not intended for JPEG library applications.
- Centralizes portability decisions around memory, file I/O, `NULL`, and `size_t`.

## Research Notes

- Ghostscript’s `jpeg.mak` copies this header into the generated directory so IJG sources pick up Ghostscript’s generated `jconfig.h`.
- No filesystem-specific behavior is present.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/jinclude.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/jmcorig.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/jmcorig.h

## Identity

- Lines/bytes: 363 lines, 12,458 bytes.
- SHA-256: `262138c3433e81e84e9f6811b38b5dc63e6f161e9b952afb0ff61b4a39b697a9`.
- Role: original IJG `jmorecfg.h` configuration copied as `jmcorig.h`.

## Contents

This is the IJG v6-era secondary configuration header. It defines:

- JPEG sample precision: `BITS_IN_JSAMPLE 8`.
- Maximum image components: `MAX_COMPONENTS 10`.
- Core JPEG data types: `JSAMPLE`, `JCOEF`, `JOCTET`, `UINT8`, `UINT16`, `INT16`, `INT32`, `JDIMENSION`.
- JPEG dimension limit: `JPEG_MAX_DIMENSION 65500L`.
- Linkage/function declaration macros: `METHODDEF`, `LOCAL`, `GLOBAL`, `EXTERN`, `JMETHOD`, `FAR`.
- Boolean type and `FALSE`/`TRUE` when not already supplied.
- Optional internal capabilities when `JPEG_INTERNALS` or `JPEG_INTERNAL_OPTIONS` is defined.

## JPEG Capabilities

Enabled in the original configuration:

- DCT methods: slow integer, fast integer, and floating point.
- Encoder: multi-scan, progressive, entropy optimization, input smoothing.
- Decoder: multi-scan, progressive, marker saving, block smoothing, IDCT scaling, upsample merging, one-pass and two-pass quantization.
- RGB memory layout: `RGB_RED 0`, `RGB_GREEN 1`, `RGB_BLUE 2`, `RGB_PIXELSIZE 3`.

Disabled:

- Arithmetic coding for both compression and decompression.
- Upsample-stage scaling.

## Dependencies

- Consumed by `jmorecf0.h` and `jmorecfg.h`.
- Relies on symbols from `jconfig.h`, such as `HAVE_UNSIGNED_CHAR`, `HAVE_UNSIGNED_SHORT`, `CHAR_IS_UNSIGNED`, `HAVE_PROTOTYPES`, and `NEED_FAR_POINTERS`.

## Behavior And Integration

- Establishes public ABI-visible IJG types used by `jpeglib.h`.
- Acts as the baseline before Ghostscript’s wrapper disables unneeded features.

## Research Notes

- This is third-party IJG configuration preserved inside Ghostscript.
- Ghostscript keeps it separate as `jmcorig.h` so its wrapper can include the original and then override selected features.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/jmcorig.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/jmorecf0.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/jmorecf0.h

## Identity

- Lines/bytes: 52 lines, 1,647 bytes.
- SHA-256: `1441dbd7262a998ee4034cdc09e9d50d805a288d4c5e03eb73b69e8953e76b99`.
- Role: Ghostscript wrapper for IJG `jmorecfg.h`.
- Duplicate note: byte-identical to `jmorecfg.h`.

## Contents

The file includes `jmcorig.h`, then disables JPEG features Ghostscript does not want or need:

- Disables `DCT_IFAST_SUPPORTED`.
- Disables `DCT_FLOAT_SUPPORTED` when `FPU_TYPE <= 0`.
- Disables compression multi-scan/progressive support, entropy optimization, and input smoothing.
- Keeps decompression multi-scan/progressive support because progressive JPEG is required for PDF 1.3.
- Disables block smoothing, IDCT scaling, upsample scaling, upsample merging, and both color quantizers.
- Defines `D_MAX_BLOCKS_IN_MCU 64` for Adobe compatibility.

## Dependencies

- Includes `jmcorig.h`.
- Uses `FPU_TYPE`, expected from Ghostscript architecture configuration.

## Behavior And Integration

This is the private JPEG feature policy for Ghostscript’s bundled IJG build. It narrows encoder capability while preserving decoder support needed by PDF workflows and nonstandard Adobe-produced JPEGs.

## Research Notes

- The Adobe compatibility setting increases decompressor MCU block tolerance beyond the IJG default.
- No unique behavior versus `jmorecfg.h`; both files are identical copies in this tree.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/jmorecf0.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/jmorecfg.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/jmorecfg.h

## Identity

- Lines/bytes: 52 lines, 1,647 bytes.
- SHA-256: `1441dbd7262a998ee4034cdc09e9d50d805a288d4c5e03eb73b69e8953e76b99`.
- Role: active Ghostscript wrapper installed as IJG `jmorecfg.h`.
- Duplicate note: byte-identical to `jmorecf0.h`.

## Contents

The file includes `jmcorig.h`, then applies Ghostscript-specific feature reductions:

- Removes fast integer DCT.
- Removes floating DCT on systems without FPU support.
- Removes progressive/multiscan compression, entropy optimization, and input smoothing.
- Preserves progressive decompression for PDF 1.3 compatibility.
- Removes decoder smoothing, scaling, upsample merging, and color quantization features.
- Sets `D_MAX_BLOCKS_IN_MCU` to `64`.

## Dependencies

- Includes `jmcorig.h`.
- Uses `FPU_TYPE` from Ghostscript architecture configuration.

## Behavior And Integration

This is the filename IJG consumers include directly via `jpeglib.h`. In Ghostscript’s build flow, `jpeg.mak` creates/copies this wrapper so bundled IJG sources see Ghostscript’s reduced feature set.

## Research Notes

- This header determines which IJG source modules are useful in Ghostscript’s private build.
- It is a build/configuration artifact, not Plan 9 OS or filesystem logic.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/jmorecfg.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/jpeg.mak -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/jpeg.mak

## Identity

- Lines/bytes: 389 lines, 15,307 bytes.
- SHA-256: `9370e13f9264ac848912d90782e5fbe8ba602227e376e255cea300d9e00c8f68`.
- Role: Ghostscript makefile fragment for building or sharing the IJG JPEG library.

## Inputs And Build Variables

Callers must define:

- `GSSRCDIR`, `JSRCDIR`, `JGENDIR`, `JOBJDIR`.
- `JVERSION`.
- `SHARE_JPEG`: `0` for private build, `1` for shared library use.
- `JPEG_NAME` for shared JPEG library mode.

Derived paths include `JSRC`, `JGEN`, `JOBJ`, `JO_`, and `JPEG_MAK`.

## Header Generation

The makefile creates Ghostscript-controlled JPEG headers:

- `jconfig0.h` from `stdpn.h`, `stdpre.h`, and `gsjconf.h`.
- `jconfig1.h` as a wrapper that includes system `jconfig.h`.
- `jconfig_.h` selected from `jconfig$(SHARE_JPEG).h`.
- `jmorecf0.h` from `gsjmorec.h`.
- `jmorecf1.h` as a wrapper that includes system `jmorecfg.h`.
- `jmorecfg.h` from `jmorecf0.h`.
- `jmcorig.h` from IJG’s original `jmorecfg.h`.
- `jpeglib0.h` from IJG’s `jpeglib.h`.
- `jpeglib1.h` as a wrapper around system `jpeglib.h`.
- `jpeglib_.h` selected from `jpeglib$(SHARE_JPEG).h`.

## Build Strategy

The makefile copies IJG `.c` files into Ghostscript’s generated directory before compiling them, then deletes the temporary copies. The comments explain the reason: C compilers disagree on whether quoted includes search the source file’s directory before `-I` paths, so copying ensures IJG files include Ghostscript’s modified headers.

## Modules Built

Common module:

- `jpegc0.dev`: `jcomapi`, `jutils`, `jmemmgr`, `jerror`.

Compression module:

- `jpege.dev` chooses shared or private mode.
- Private `jpege6.dev` includes common code and encoder objects such as `jcapimin`, `jcapistd`, `jcinit`, `jccoefct`, `jccolor`, `jcdctmgr`, `jchuff`, `jcmainct`, `jcmarker`, `jcmaster`, `jcparam`, `jcprepct`, `jcsample`, and `jfdctint`.

Decompression module:

- `jpegd.dev` chooses shared or private mode.
- Private `jpegd6.dev` includes common code and decoder objects such as `jdapimin`, `jdapistd`, `jdinput`, `jdphuff`, `jdcoefct`, `jdcolor`, `jddctmgr`, `jdhuff`, `jdmainct`, `jdmarker`, `jdmaster`, `jdpostct`, `jdsample`, and `jidctint`.

## Behavior And Integration

- Supports IJG versions 6, 6a, and 6b, with version 6b treated as current in the comments.
- In shared mode, generated `.dev` files refer to `JPEG_NAME` as a library.
- In private mode, Ghostscript compiles selected IJG source files with modified headers.
- Cleaning removes JPEG object files and generated `jpeg*.dev` files.

## Research Notes

- This is the central explanation for why several duplicate/generated-looking JPEG headers exist in this directory.
- The build is conservative: all IJG objects depend on the few headers Ghostscript may alter.
- No Plan 9 filesystem behavior is implemented here; this is application build plumbing for Ghostscript.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/jpeg.mak -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/jpeglib.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/jpeglib.h

## Identity

- Lines/bytes: 1,096 lines, 46,205 bytes.
- SHA-256: `b34b3d9897820302cc23ba60217157f75e03db8c537a7d4703ff0bc8c9fc048b`.
- Role: IJG v6b public JPEG library API header.
- Duplicate note: byte-identical to `jpeglib0.h` and `jpeglib_.h`.

## Public API Surface

The header defines:

- Version: `JPEG_LIB_VERSION 62`.
- JPEG constants: DCT block size, table counts, scan component limits, sampling limits, compressor/decompressor MCU block limits.
- Core image/coefficient array pointer types: `JSAMPROW`, `JSAMPARRAY`, `JSAMPIMAGE`, `JBLOCK`, `JBLOCKROW`, `JBLOCKARRAY`, `JBLOCKIMAGE`, `JCOEFPTR`.
- Quantization and Huffman table structs: `JQUANT_TBL`, `JHUFF_TBL`.
- Component metadata: `jpeg_component_info`.
- Progressive/multiscan script entries: `jpeg_scan_info`.
- Saved marker list nodes: `jpeg_marker_struct`.
- Color spaces, DCT methods, and dithering modes.

## Master Structures

Defines the common, compression, and decompression objects:

- `jpeg_common_struct`: shared error, memory, progress, client data, object kind, and state fields.
- `jpeg_compress_struct`: destination manager, source image description, compression parameters, quant/Huffman tables, scan script, marker flags, progress state, computed MCU state, and compressor subobject pointers.
- `jpeg_decompress_struct`: source manager, input image description, decompression parameters, output dimensions, quantization/color map state, progress state, saved marker metadata, computed MCU state, unread marker, and decompressor subobject pointers.

## Managers And Callbacks

Defines public “object” interfaces for:

- `jpeg_error_mgr`.
- `jpeg_progress_mgr`.
- `jpeg_destination_mgr`.
- `jpeg_source_mgr`.
- `jpeg_memory_mgr`.
- `jpeg_marker_parser_method`.

The memory manager uses permanent and image pools and supports virtual sample/block arrays.

## Exported Functions

Compression lifecycle and configuration:

- `jpeg_create_compress`, `jpeg_CreateCompress`, `jpeg_destroy_compress`.
- `jpeg_stdio_dest`.
- `jpeg_set_defaults`, `jpeg_set_colorspace`, `jpeg_default_colorspace`.
- `jpeg_set_quality`, `jpeg_set_linear_quality`, `jpeg_add_quant_table`, `jpeg_quality_scaling`.
- `jpeg_simple_progression`, `jpeg_suppress_tables`.
- `jpeg_start_compress`, `jpeg_write_scanlines`, `jpeg_write_raw_data`, `jpeg_finish_compress`.
- Marker and table writing APIs.

Decompression lifecycle and processing:

- `jpeg_create_decompress`, `jpeg_CreateDecompress`, `jpeg_destroy_decompress`.
- `jpeg_stdio_src`.
- `jpeg_read_header`, `jpeg_start_decompress`, `jpeg_read_scanlines`, `jpeg_read_raw_data`, `jpeg_finish_decompress`.
- Buffered-image/progressive APIs.
- Marker saving/processing APIs.
- Raw coefficient read/write/copy APIs.

Generic cleanup:

- `jpeg_abort_compress`, `jpeg_abort_decompress`, `jpeg_abort`, `jpeg_destroy`.
- `jpeg_resync_to_restart`.

## Dependencies

- Includes `jconfig.h` unless `JCONFIG_INCLUDED` is already set.
- Includes `jmorecfg.h`.
- References `FILE`, so users normally get this through `jinclude.h` or include standard I/O context.
- Includes `jpegint.h` and `jerror.h` only when `JPEG_INTERNALS` is defined.

## Research Notes

- Ghostscript’s `jmorecfg.h` can raise `D_MAX_BLOCKS_IN_MCU` before this header defines the decompressor default.
- The public ABI depends on configuration types from `jmorecfg.h`.
- This is third-party JPEG library API surface embedded in the Plan 9 Ghostscript source tree.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/jpeglib.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/jpeglib0.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/jpeglib0.h

## Identity

- Lines/bytes: 1,096 lines, 46,205 bytes.
- SHA-256: `b34b3d9897820302cc23ba60217157f75e03db8c537a7d4703ff0bc8c9fc048b`.
- Role: private-build copy of IJG v6b `jpeglib.h`.
- Duplicate note: byte-identical to `jpeglib.h` and `jpeglib_.h`.

## Contents And API

This file contains the same public IJG JPEG API as `jpeglib.h`:

- JPEG v6b version and standard constants.
- Image sample and coefficient array types.
- Quantization/Huffman/component/scan/marker structures.
- Compression and decompression master structs.
- Error, progress, source, destination, and memory manager interfaces.
- Compression, decompression, marker, coefficient, abort, destroy, and restart-resync function declarations.

## Build Role

According to `jpeg.mak`, `jpeglib0.h` is produced from the IJG source `jpeglib.h` for `SHARE_JPEG=0`, when Ghostscript builds its private JPEG library. It is then selected into `jpeglib_.h` depending on the share/private mode.

## Dependencies

- Includes `jconfig.h` unless already included.
- Includes `jmorecfg.h`.
- May include private `jpegint.h` and `jerror.h` under `JPEG_INTERNALS`.

## Research Notes

- No semantic differences from `jpeglib.h` were found.
- The `0` suffix is a build-mode convention: private/bundled JPEG rather than shared-system JPEG.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/jpeglib0.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/jpeglib_.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/jpeglib_.h

## Identity

- Lines/bytes: 1,096 lines, 46,205 bytes.
- SHA-256: `b34b3d9897820302cc23ba60217157f75e03db8c537a7d4703ff0bc8c9fc048b`.
- Role: selected Ghostscript wrapper/copy for the active JPEG API header.
- Duplicate note: byte-identical to `jpeglib.h` and `jpeglib0.h`.

## Contents And API

This file exposes the IJG v6b application API:

- Public constants and JPEG data structures.
- Compression and decompression state objects.
- Manager callback structs for error handling, progress, memory, I/O source, and I/O destination.
- Public functions for JPEG object creation/destruction, compression, decompression, marker handling, coefficient access, buffered-image mode, and cleanup.

## Build Role

`jpeg.mak` builds `jpeglib_.h` by copying either:

- `jpeglib0.h` for bundled/private JPEG builds.
- `jpeglib1.h` for shared-system JPEG builds.

In this checked-in tree, the file content matches the private IJG header.

## Dependencies

- Includes `jconfig.h` and `jmorecfg.h`.
- Uses configuration-controlled type definitions from `jmorecfg.h`.
- Includes internal declarations only under `JPEG_INTERNALS`.

## Research Notes

- This is the stable include target Ghostscript can depend on while switching JPEG build modes.
- The checked-in copy represents the bundled IJG API path and contains no Plan 9 filesystem logic.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/jpeglib_.h -->