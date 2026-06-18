# Group Research: group_1526_plan9_sources_os_plan9_plan9_sys_src_cmd_gs_jpeg_jquant1_c_sources__a24fdefadad6

Scope checked against `Docs/research_subset_a.md`: all files are within `sources/os/plan9/plan9`, under the Plan 9 Ghostscript bundled IJG JPEG source tree. Every listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jquant1.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jquant1.c

This is the Independent JPEG Group one-pass color quantizer, compiled only when `QUANT_1PASS_SUPPORTED` is enabled. It implements fast indexed-color output by creating an orthogonal, preselected colormap before seeing image pixels.

The module chooses per-component color counts from `cinfo->desired_number_of_colors`, biased for RGB by trying green, then red, then blue. `create_colormap()` builds all component-value combinations, while `create_colorindex()` precomputes pixel-value-to-colormap-index contributions so row conversion is mostly table lookup and addition.

It supports three output modes: no dithering, ordered dithering with a 16x16 Bayer matrix, and Floyd-Steinberg dithering. There are specialized 3-component fast paths for no dithering and ordered dithering, plus general paths for other component counts up to `MAX_Q_COMPS` 4.

Floyd-Steinberg state is stored as per-component error arrays allocated through libjpeg's memory manager. Rows alternate left-to-right and right-to-left, using the standard 7/16, 3/16, 5/16, 1/16 distribution. Ordered dithering pads the color index table so dithered values outside `0..MAXJSAMPLE` clamp via table lookup.

Integration points are the `jpeg_color_quantizer` methods installed by `jinit_1pass_quantizer()`: `start_pass`, `finish_pass`, `new_color_map`, and the selected `color_quantize` callback. The code depends on `jinclude.h`, `jpeglib.h`, libjpeg memory pools, error macros, `sample_range_limit`, and the decompressor fields for output size, color space, dithering mode, and colormap reporting.

Important constraints: external colormap switching is rejected with `JERR_MODE_CHANGE`; requested colors must fit in `JSAMPLE`; component count over four is rejected; and ordered dither table creation is lazy. This is performance-oriented image code, not filesystem logic, but it is part of the Plan 9 source snapshot through Ghostscript's vendored JPEG library.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jquant1.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jquant2.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jquant2.c

This is the IJG two-pass color quantizer, compiled when `QUANT_2PASS_SUPPORTED` is enabled. It selects an image-specific colormap during a prescan and then maps pixels to that colormap, optionally with Floyd-Steinberg dithering.

The first pass builds a reduced-precision RGB histogram: 5 bits for component 0, 6 for component 1, and 5 for component 2. Histogram cells are `UINT16`, with overflow clamped. The code is hard-wired to three output color components and uses scaled distance weights of 2 for red, 3 for green, and 1 for blue, respecting the configured RGB order.

Color selection follows a Heckbert-style median-cut workflow. It starts with one box covering the used color space, shrinks boxes to nonzero histogram cells, splits by population for the first half of the requested colors and by scaled volume after that, then computes a pixel-count-weighted mean color for each final box.

The second pass reuses the histogram as an inverse colormap cache. Empty cache cells trigger `fill_inverse_cmap()`, which fills a small histogram subbox by selecting nearby colormap candidates and using incremental squared-distance calculations to choose nearest colors. This avoids full colormap searches for every pixel.

Dithering support is limited to none or Floyd-Steinberg; requested ordered dither is coerced to F-S. The F-S path uses one row of three-component error storage, alternates scan direction by row, applies an error limiter table to reduce artifacts, clamps through `sample_range_limit`, then emits cached nearest-colormap indexes.

`jinit_2pass_quantizer()` allocates the quantizer object, histogram rows, optional saved colormap, and optional F-S workspace. `start_pass_2_quant()` switches between prescan and output pass behavior, validates color counts, zeroes histogram/cache state when needed, and handles external colormap remapping via `new_color_map_2_quant()`.

Key constraints: only 3-component output is implemented; desired colors must be between 8 and `MAXJSAMPLE+1` for self-generated maps; external maps must have 1 to `MAXNUMCOLORS` colors; and the algorithm is memory-conscious for old segmented-memory systems. This is image quantization infrastructure within the vendored JPEG library.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jquant2.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jutils.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jutils.c

This file provides shared IJG utility data and routines used by compression and decompression code.

Its main exported table is `jpeg_natural_order[DCTSIZE2+16]`, mapping zigzag coefficient order back to natural 8x8 block order. The trailing sixteen entries are all `63`, intentionally preventing wild stores if corrupted Huffman data produces a run past the end of a block.

The arithmetic helpers `jdiv_round_up()` and `jround_up()` implement ceiling division and rounding to a multiple, assuming nonnegative input and positive divisor.

The memory helpers are `jcopy_sample_rows()`, `jcopy_block_row()`, and `jzero_far()`. They abstract ordinary memory copying/zeroing versus FAR-pointer memory models, using `FMEMCOPY`/`FMEMZERO` when available and byte/element loops otherwise.

Dependencies are `jinclude.h`, `jpeglib.h`, compile-time memory model macros, and core libjpeg typedefs such as `JSAMPARRAY`, `JBLOCKROW`, `JCOEF`, and `JDIMENSION`. This is low-level portability support, not Plan 9 filesystem code.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jutils.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jversion.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jversion.h

This header contains IJG version identity macros.

It defines `JVERSION` as `6b  27-Mar-1998` and `JCOPYRIGHT` as `Copyright (C) 1998, Thomas G. Lane`.

It has no includes, functions, data structures, or conditional logic. Other JPEG files use it to report library/application version and copyright text.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jversion.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/ltconfig -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/ltconfig

This is GNU libtool 1.2's `ltconfig` generator script. It creates a host-specific `libtool` script by probing compiler, linker, archive, symbol, shared-library, and runtime-linker behavior, then appending `ltmain.sh`.

The script parses options such as `--disable-shared`, `--disable-static`, `--srcdir`, `--no-verify`, `--with-gcc`, and `--with-gnu-ld`. It verifies or guesses the host through `config.guess` and `config.sub`, sets up logging in `config.log`, and normalizes shell behavior for echo, locale, and quoting.

Compiler probing discovers `gcc` or `cc`, detects whether the compiler is GNU C, selects PIC flags, checks static-link flags, and tests whether the chosen PIC flag actually compiles. It also finds `ranlib`, `ld`, `nm`, and `ln -s` behavior.

Linker probing determines whether shared libraries can be built and fills platform-specific command templates for AIX, AmigaOS, FreeBSD, HP-UX, IRIX, NetBSD, OpenBSD, OS/2, OSF, SCO, Solaris, SunOS, UnixWare, UTS, GNU/Linux, and related systems. It computes hardcoding behavior for library paths and dynamic linker characteristics such as library naming, soname patterns, runtime path variables, and install finishing commands.

The script tests an `nm` symbol extraction pipeline by compiling and linking a small program. If successful, the generated libtool can support symbol preloading/dlpreopen features.

At the end, it quotes all discovered variables, writes the generated `libtool` shell script with configuration variables such as `build_libtool_libs`, `archive_cmds`, `library_names_spec`, `shlibpath_var`, and `hardcode_action`, then appends `ltmain.sh`.

This file is build infrastructure for the bundled JPEG package. Its security-sensitive surface is shell execution during configure/build time: it creates and runs compiler/linker test commands and writes `libtool`.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/ltconfig -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/ltmain.sh -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/ltmain.sh

This is GNU libtool 1.2's main driver body. `ltconfig` appends it to generated configuration variables to form an executable `libtool` script.

The top-level parser handles `--mode`, `--dry-run`, `--features`, `--finish`, `--quiet`, `--version`, `--help`, and `-dlopen`. If no mode is explicit, it infers compile, link, execute, install, or uninstall from the command name and arguments.

Compile mode transforms compiler invocations into libtool objects. It rejects user-specified `-o`, derives `.lo` and `.o` names from source suffixes, builds PIC objects when shared libraries are enabled, builds ordinary objects when static libraries are enabled, and creates a placeholder `.lo` when shared objects are disabled.

Link mode is the largest section. It parses compiler/linker arguments, `.lo`, `.o`, `.a`, `.la`, `-L`, `-l`, `-rpath`, `-version-info`, `-release`, `-dlopen`, `-dlpreopen`, `-export-dynamic`, and static-link switches. It reads libtool archive metadata, resolves dependency libraries, constructs compile and finalize commands, handles hardcoded runtime paths, creates shared libraries, static archives, reloadable objects, wrapper scripts for uninstalled executables, and `.la` metadata files.

For dynamic symbol preloading, link mode can use `nm` plus `global_symbol_pipe` to generate a C source file containing `dld_preloaded_symbols`, compile it, and link it into the executable.

Install mode wraps install/cp behavior for `.la` libraries, `.lo` objects, static archives, and libtool wrapper scripts. It installs shared library real names and symlinks, pseudo-library `.la` files, optional static archives, and may relink wrapper executables on platforms requiring installation-time hardcoding.

Finish mode runs platform-specific post-install commands such as `ldconfig` and prints instructions for runtime library paths. Execute mode sets the configured shared-library path variable, resolves wrapper scripts to uninstalled binaries, and runs a command. Uninstall mode removes `.la`-associated shared libraries, symlinks, dynamic-load names, and static archives.

The script depends on variables supplied by `ltconfig`: compiler/linker commands, object directory, archive commands, install hooks, naming specs, hardcode settings, runtime path variables, and build mode flags. It is portable shell build machinery and not runtime JPEG or filesystem code.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/ltmain.sh -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/makefile.cfg -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/makefile.cfg

This is the configurable makefile template for IJG JPEG. `configure` substitutes `@...@` variables to produce the actual `Makefile`.

It defines installation directories, compiler and linker settings, libtool controls, library versioning, memory-manager backend selection, and basic tool commands. `LIBTOOL`, `O`, and `A` switch object/archive suffixes between libtool and ordinary builds.

The file enumerates source groups: JPEG library sources, system-dependent memory backends, application sources, headers, documentation, make/config files, configure support files, miscellaneous support files, and test images. The listed files in this research group appear in these source/object sets: `jquant1.c`, `jquant2.c`, `jutils.c`, `jversion.h`, `rdcolmap.c`, `rdgif.c`, `rdbmp.c`, `rdjpgcom.c`, `ltconfig`, and `ltmain.sh`.

Build targets include `all`, `ansi2knr`, `libjpeg.a`, `libjpeg.la`, `cjpeg`, `djpeg`, `jpegtran`, `rdjpgcom`, and `wrjpgcom`. Installation targets install programs, man pages, the library, and public headers. Cleaning targets remove objects, generated libraries, tools, config outputs, and libtool directories.

The `test` target performs round-trip and transform checks with the sample images, comparing generated outputs to expected files. The `jconfig.h` target is a deliberate failure path reminding users to prepare system-dependent configuration if configure has not produced it.

The bottom section is explicit dependency metadata for every object file. This makefile is build orchestration for the vendored JPEG distribution.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/makefile.cfg -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/rdbmp.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/rdbmp.c

This file implements BMP input support for IJG's `cjpeg` application when `BMP_SUPPORTED` is enabled. It reads Microsoft Windows and OS/2 BMP variants from a stdio stream and supplies RGB scanlines to the JPEG compressor source interface.

The private source object stores the public `cjpeg_source_struct`, a compressor back pointer, an optional BMP colormap, a virtual sample array containing the entire source image, row state, padded file row width, and bit depth.

`start_input_bmp()` parses the BMP file header and info header. It supports OS/2 1.x 12-byte headers and Windows/OS2 40/64-byte headers, accepts only 8-bit indexed and 24-bit RGB BMPs, rejects unsupported depths, bad planes, compressed BMPs, bad headers, and bad colormaps, and imports density from pixels-per-meter when available.

For indexed BMPs, `read_colormap()` reads either OS/2 BGR triples or Windows BGR0 quads and stores them in RGB component planes. The code assumes up to 256 palette entries.

BMP rows are bottom-up and padded to a 4-byte boundary, so `preload_image()` reads the entire image into a libjpeg virtual array in file order. Subsequent row callbacks decrement `source_row` to return scanlines top-to-bottom. `get_8bit_row()` expands palette indexes to RGB, and `get_24bit_row()` converts file BGR byte order to RGB.

`jinit_read_bmp()` allocates the source object and installs `start_input` and `finish_input`. Dependencies include `cdjpeg.h`, libjpeg memory managers, `JFREAD`, progress callbacks, and cjpeg source contracts.

Constraints: no 1-bit/4-bit BMP, no RLE compression, no top-down BMP handling is evident, and input is assumed to begin at the file start. This is image import code only.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/rdbmp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/rdcolmap.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/rdcolmap.c

This file implements `djpeg`'s `-map file` option when `QUANT_2PASS_SUPPORTED` is enabled. It reads an external color map and stores it in `cinfo->colormap` for decompression quantization.

`read_color_map()` allocates a maximum-size 3-component colormap of `MAXJSAMPLE+1` entries, initializes `actual_number_of_colors` to zero, reads the first byte, and dispatches to GIF or PPM parsing.

GIF map handling reads the GIF header and logical screen descriptor after the initial `G`, verifies the `GIF` signature and presence of a global color table, computes its size, then imports RGB triples into the map. Pixel data is not decoded; only the global palette is used.

PPM map handling supports text P3 and raw P6 formats. It reads width, height, and maxval with PBM-style comment skipping, requires `maxval == MAXJSAMPLE`, then reads every pixel and adds unique colors to the map. Duplicate colors are ignored by linear scan.

`add_map_entry()` enforces uniqueness and rejects maps larger than `MAXJSAMPLE+1` colors. Error handling uses libjpeg `ERREXIT` macros with `JERR_BAD_CMAP_FILE` or `JERR_QUANT_MANY_COLORS`.

The file depends on `cdjpeg.h`, stdio input, libjpeg decompressor structures, and two-pass quantization support. It does no filesystem-specific work beyond reading the supplied stdio file.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/rdcolmap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/rdgif.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/rdgif.c

This file is a stub GIF input module for `cjpeg`, compiled only if `GIF_SUPPORTED` is defined.

The original GIF reader was removed from the IJG distribution to avoid LZW patent issues. The only exported function, `jinit_read_gif()`, prints an unsupported message to stderr, exits with `EXIT_FAILURE`, and returns `NULL` only to satisfy the compiler.

It includes `cdjpeg.h` for application declarations but performs no image parsing. GIF palette reading for `djpeg -map` is separate and remains in `rdcolmap.c` because it does not decode LZW image data.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/rdgif.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/rdjpgcom.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/rdjpgcom.c

This is a standalone IJG utility that prints textual JPEG COM markers, with optional verbose frame information. It is intentionally a small example of marker parsing rather than a full decoder.

The program reads from one optional input file or stdin in binary mode. It defines JPEG marker constants, low-level byte readers, `first_marker()` for SOI validation, `next_marker()` for scanning marker boundaries before compressed data, and `skip_variable()` for uninteresting variable-length marker payloads.

`process_COM()` reads a COM-like marker segment, validates its length, normalizes CR/LF newline variants, escapes backslash, prints printable characters directly, and emits nonprintable bytes as octal escapes. In verbose mode, APP12 marker contents are also printed through this same routine.

`process_SOFn()` parses SOF markers to print image dimensions, component count, sample precision, and process type such as Baseline, Progressive, Lossless, or arithmetic-coded variants. It validates the SOF payload length and consumes per-component metadata.

`scan_JPEG_header()` walks markers from SOI until SOS or EOI. It handles SOF markers, COM, APP12, SOS, EOI, and skips everything else as variable-length marker data. It deliberately stops before compressed entropy-coded data because byte-stuffed `FF/00` sequences require different parsing.

Command-line parsing supports `-verbose` with abbreviation matching through `keymatch()`. `usage()` reports syntax and exits. Portability conditionals handle Macintosh command-line acquisition, binary stdin reopening, setmode, VMS binary modes, and exit-code definitions.

This file depends only on `jinclude.h`, stdio, ctype, and small platform conditionals; it does not link through the libjpeg decompressor API. Its main risks are typical standalone parser constraints: it assumes unknown pre-SOS markers have length fields and is designed for comment extraction, not full JPEG validation.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/rdjpgcom.c -->