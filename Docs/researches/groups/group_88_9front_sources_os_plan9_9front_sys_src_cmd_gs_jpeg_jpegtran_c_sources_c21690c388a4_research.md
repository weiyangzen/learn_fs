# Group Research: group_88_9front_sources_os_plan9_9front_sys_src_cmd_gs_jpeg_jpegtran_c_sources_c21690c388a4

Scope: `Docs/research_subset_a.md`

All listed files were read completely. These files are part of 9front's vendored IJG JPEG 6b code: JPEG transcoding CLI, one-pass and two-pass color quantizers, utility routines, version metadata, old libtool/autoconf build support, makefile template, and input/map readers used by the sample applications.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/jpegtran.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/jpegtran.c

Purpose: command-line frontend for lossless JPEG transcoding and optional lossless or mostly-lossless coefficient-domain transformations.

Key contents:
- Includes `cdjpeg.h`, `transupp.h`, and `jversion.h`.
- Global command state: `progname`, `outfilename`, `copyoption`, and `transformoption`.
- `usage()` prints supported switches and exits.
- `select_transform()` enforces at most one image transform.
- `parse_switches()` handles command-line options for marker copying, arithmetic coding, optimization, progressive output, scan scripts, restart intervals, memory limit, output file, debug output, grayscale conversion, and transforms.
- `main()` wires decompressor/compressor objects, file IO, marker copy setup, coefficient reading/writing, transform workspace, transform execution, and cleanup.

Important behavior:
- Performs a dummy switch parse before opening/reading the source, then reparses after `jpeg_copy_critical_parameters()` so destination options apply to initialized compression parameters.
- Reads source image as DCT coefficient arrays with `jpeg_read_coefficients()` and writes with `jpeg_write_coefficients()`.
- Uses `jcopy_markers_setup()` and `jcopy_markers_execute()` to preserve comments or all extra markers depending on `-copy`.
- Transform support is conditional on `TRANSFORMS_SUPPORTED`; unsupported transform requests exit with an error.
- `-progressive` and `-scans` are deferred until enough output context is available.
- Exit status is warning-aware: warning count returns `EXIT_WARNING`, otherwise `EXIT_SUCCESS`.

Dependencies:
- IJG app support (`cdjpeg.h`), transform support (`transupp.h`), libjpeg compression/decompression APIs, stdio helpers such as `read_stdin()` and `write_stdout()`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/jpegtran.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/jquant1.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/jquant1.c

Purpose: one-pass color quantizer for fast mapping to a preselected, equally spaced colormap, with optional ordered or Floyd-Steinberg dithering.

Key contents:
- Compiled only when `QUANT_1PASS_SUPPORTED` is enabled.
- Defines ordered dithering constants and a 16x16 Bayer base dither matrix.
- Defines Floyd-Steinberg error types and per-component error arrays.
- `my_cquantizer` stores the public quantizer vtable, saved colormap, precomputed `colorindex`, component color counts, ordered dither tables, and F-S state.
- Policy helpers: `select_ncolors()`, `output_value()`, and `largest_input_value()`.
- Setup helpers: `create_colormap()`, `create_colorindex()`, `make_odither_array()`, `create_odither_tables()`, `alloc_fs_workspace()`.
- Quantization routines: `color_quantize()`, `color_quantize3()`, `quantize_ord_dither()`, `quantize3_ord_dither()`, and `quantize_fs_dither()`.
- Public init entry: `jinit_1pass_quantizer()`.

Important behavior:
- Builds an orthogonal colormap using the product of per-component color counts, keeping total colors at or below `desired_number_of_colors`.
- For RGB output, allocation favors green, then red, then blue.
- `colorindex[component][sample]` stores premultiplied colormap-index contributions so pixel mapping is a sum of component lookups.
- Ordered dithering pads `colorindex` in both directions so dithered sample values can be indexed without explicit range checks.
- Components with the same number of representative values share ordered-dither tables.
- Floyd-Steinberg dithering alternates scan direction by row and propagates 7/16, 3/16, 5/16, and 1/16 errors using per-component FAR-memory arrays.
- `start_pass_1_quant()` selects the active quantization method based on `dither_mode`.
- External colormap changes are rejected via `JERR_MODE_CHANGE`.

Dependencies:
- `jinclude.h`, `jpeglib.h`, IJG memory manager, `jzero_far()`, error macros, sample range-limit tables.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/jquant1.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/jquant2.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/jquant2.c

Purpose: two-pass color quantizer using Heckbert-style median cut to build an image-specific colormap, then map pixels to that map with optional Floyd-Steinberg dithering.

Key contents:
- Compiled only when `QUANT_2PASS_SUPPORTED` is enabled.
- RGB distance scale factors: `R_SCALE = 2`, `G_SCALE = 3`, `B_SCALE = 1`.
- Histogram precision: 5 bits for C0, 6 bits for C1, 5 bits for C2.
- `my_cquantizer` stores public methods, saved colormap, desired color count, histogram/inverse-cache storage, zeroing flag, F-S workspace, and error limiter.
- `prescan_quantize()` accumulates the reduced-precision histogram.
- Median-cut machinery: `box`, `find_biggest_color_pop()`, `find_biggest_volume()`, `update_box()`, `median_cut()`, `compute_color()`, `select_colors()`.
- Inverse colormap cache machinery: `find_nearby_colors()`, `find_best_colors()`, `fill_inverse_cmap()`.
- Mapping routines: `pass2_no_dither()` and `pass2_fs_dither()`.
- Error limiting: `init_error_limit()`.
- Pass lifecycle: `start_pass_2_quant()`, `finish_pass1()`, `finish_pass2()`, `new_color_map_2_quant()`.
- Public init entry: `jinit_2pass_quantizer()`.

Important behavior:
- Only supports three output color components; other cases call `JERR_NOTIMPL`.
- First pass records histogram cells, clamping 16-bit cell overflow.
- Color selection starts from one box covering the color cube, shrinks boxes to nonempty cells, splits by population first and by volume later, then uses pixel-weighted means for representative colors.
- Reuses histogram storage during pass 2 as a lazy inverse colormap cache; zero means uncached, stored values are colormap index plus one.
- Nearest-color searches fill small update boxes rather than the full histogram, using locality filtering and incremental distance computation.
- Ordered dithering is not supported; any non-none dither mode becomes Floyd-Steinberg.
- Floyd-Steinberg path limits applied error through a transfer table to reduce visual artifacts.
- `new_color_map_2_quant()` marks the inverse cache for zeroing before reuse.

Dependencies:
- `jinclude.h`, `jpeglib.h`, IJG memory manager, `jzero_far()`, sample range-limit table, error/trace macros.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/jquant2.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/jutils.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/jutils.c

Purpose: shared JPEG library utility tables and small helper routines used by compression and decompression.

Key contents:
- Defines `JPEG_INTERNALS`, includes `jinclude.h` and `jpeglib.h`.
- Disabled `jpeg_zigzag_order` table under `#if 0`.
- Active `jpeg_natural_order[DCTSIZE2+16]` table maps zigzag positions to natural DCT block positions.
- Arithmetic helpers: `jdiv_round_up()` and `jround_up()`.
- FAR-memory aware copy/zero helpers: `jcopy_sample_rows()`, `jcopy_block_row()`, `jzero_far()`.

Important behavior:
- `jpeg_natural_order` includes 16 extra entries set to 63 to contain out-of-range coefficient writes from corrupted entropy data without adding an inner-loop bounds check.
- FAR pointer handling supports old segmented-memory DOS compilers; normal builds map to `MEMCOPY` and `MEMZERO`.
- Sample row copying allows overlapping source/destination rows for row duplication.
- Block row copying moves coefficient blocks as raw `JCOEF` sequences when far-memory bulk copy is unavailable.

Dependencies:
- Memory macros from `jinclude.h`, JPEG sample/coefficient types from `jpeglib.h`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/jutils.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/jversion.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/jversion.h

Purpose: IJG JPEG library version and copyright identification.

Key contents:
- `JVERSION` is `"6b  27-Mar-1998"`.
- `JCOPYRIGHT` is `"Copyright (C) 1998, Thomas G. Lane"`.

Important behavior:
- Used by command-line tools and error/version reporting to identify the bundled IJG code version.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/jversion.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/ltconfig -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/ltconfig

Purpose: GNU libtool 1.2 configure-time generator that probes the host toolchain and creates a system-specific `libtool` script.

Key contents:
- Shell script with GPL/libtool exception header.
- Parses options such as `--disable-shared`, `--disable-static`, `--srcdir`, `--no-verify`, `--with-gcc`, `--with-gnu-ld`, and `--silent`.
- Locates and uses `config.guess`/`config.sub` unless host verification is disabled.
- Detects `ranlib`, C compiler, GCC status, PIC flags, static-link flags, symlink support, linker path, GNU ld status, `nm`, and global-symbol parsing pipeline.
- Contains per-OS linker/shared-library rules for AIX, AmigaOS, FreeBSD, HP-UX, IRIX, NetBSD, OpenBSD, OS/2, OSF, SCO, Solaris, SunOS, UnixWare, UTS, Linux ELF, and related variants.
- Computes shared library naming, soname, runtime path variables, install finish commands, archive commands, hardcoding behavior, and object directory.
- Writes a configured `libtool` script containing discovered variables, then appends `ltmain.sh`.

Important behavior:
- Defaults to static archive support and shared-library support when possible.
- Falls back to static-only behavior if compiler/linker/PIC/dynamic-linker tests fail.
- Stores probe output in `config.log`.
- Quotes generated shell variables carefully before embedding them in the generated script.
- Does not build JPEG code directly; it supports `makefile.cfg` when libtool builds are requested.

Dependencies:
- POSIX shell utilities, compiler/linker tools, `config.guess`, `config.sub`, and `ltmain.sh`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/ltconfig -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/ltmain.sh -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/ltmain.sh

Purpose: GNU libtool 1.2 runtime script fragment appended by `ltconfig` to implement generalized compile, link, install, execute, finish, and uninstall operations.

Key contents:
- Validates `LTCONFIG_VERSION` against `VERSION`.
- Parses common options such as `--mode`, `--dry-run`, `--features`, `--finish`, `--silent`, `--version`, and `-dlopen`.
- Infers mode from the command when `--mode` is not supplied.
- `compile` mode builds `.lo` libtool objects and optional `.o` old-style objects, using PIC flags when shared libraries are enabled.
- `link` mode handles ordinary objects, `.lo`, `.la`, `-L`, `-l`, `-rpath`, `-version-info`, `-release`, `-static`, `-all-static`, `-dlopen`, `-dlpreopen`, and `-export-dynamic`.
- Creates shared libraries, static archives, reloadable objects, executable wrappers, `.la` metadata files, and symlinks as needed.
- `install` mode installs `.la`, `.a`, `.lo`, and wrapped executables, relinking when the configured platform requires it.
- `finish` mode runs post-install shared-library cache/path commands and prints runtime-linking guidance.
- `execute` mode adjusts shared-library path variables and runs programs, translating wrapper scripts to real uninstalled binaries.
- `uninstall` mode removes libtool archives and associated shared/static library files.
- Ends with mode-specific help text.

Important behavior:
- The generated `libtool` script depends on variables emitted by `ltconfig`, such as `build_libtool_libs`, `build_old_libs`, `objdir`, `archive_cmds`, `hardcode_action`, and library path variable names.
- Executables linked against uninstalled libtool libraries are wrapped by shell scripts that locate the real binary under the object directory and set the library path.
- `.la` files record dlopen name, library names, static archive name, dependency libraries, version info, and install directory.
- Supports dry-run operation by printing commands without executing them.
- This is build-system infrastructure only; it has no JPEG image-processing logic.

Dependencies:
- Shell, compiler/linker/archive commands configured by `ltconfig`, `sed`, `egrep`, `sort`, `uniq`, `nm`, install/copy/remove tools.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/ltmain.sh -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/makefile.cfg -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/makefile.cfg

Purpose: autoconf-substituted makefile template for building and installing the IJG JPEG library and sample command-line programs.

Key contents:
- Configurable variables for source directory, install prefix, compiler, flags, libraries, libtool, object/archive suffixes, JPEG library version, memory manager backend, shell tools, installer, archiver, and ranlib.
- Source lists for library files, system-dependent memory manager backends, sample apps, headers, docs, makefiles, configuration files, configure support files, other support files, and tests.
- Object lists for common, compression, decompression, full library, and app-specific objects.
- Targets: `all`, `ansi2knr`, `libjpeg.a`, `libjpeg.la`, `cjpeg`, `djpeg`, `jpegtran`, `rdjpgcom`, `wrjpgcom`, `install`, `install-lib`, `install-headers`, `clean`, `distclean`, `test`, `check`, and `jconfig.h` mistake-catcher.
- Explicit dependency lines for all library and application objects.

Important behavior:
- `configure` replaces `@...@` placeholders to produce a concrete Makefile.
- Supports plain `.o`/`.a` builds and libtool `.lo`/`.la` builds.
- Supports optional `ansi2knr` conversion for K&R compilers.
- Builds sample apps against `libjpeg.$(A)`.
- `test` performs encode/decode/transcode regression checks against bundled test images with `cmp`.
- `jconfig.h` target deliberately fails with installation instructions if configuration was not prepared.

Dependencies:
- IJG source tree, configured `jconfig.h`, system memory manager selection, optional libtool, optional `ansi2knr`, POSIX make tools.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/makefile.cfg -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/rdbmp.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/rdbmp.c

Purpose: `cjpeg` input module for reading Microsoft/OS/2 BMP files and presenting them as RGB sample rows to the JPEG compressor.

Key contents:
- Compiled only when `BMP_SUPPORTED` is enabled.
- Defines unsigned-byte helper type/macros and `ReadOK`.
- `bmp_source_struct` extends `cjpeg_source_struct` with compressor back link, BMP colormap, virtual image array, row counters, physical row width, and bit depth.
- `read_byte()` reads one byte or raises `JERR_INPUT_EOF`.
- `read_colormap()` reads OS/2 BGR or Windows BGR0 palette entries into RGB colormap arrays.
- Row readers: `get_8bit_row()` expands palette indexes to RGB; `get_24bit_row()` converts file BGR bytes to RGB.
- `preload_image()` reads the BMP pixel data into a virtual array before row output.
- `start_input_bmp()` parses BMP headers, validates format, reads colormap, skips padding, configures virtual storage and compressor image parameters.
- Public init entry: `jinit_read_bmp()`.

Important behavior:
- Supports 8-bit colormapped and 24-bit BMP only.
- Supports OS/2 1.x 12-byte headers, Windows 40-byte headers, and OS/2 2.x 64-byte headers.
- Rejects 1-bit, 4-bit, unsupported depths, multiple planes, compressed BMPs, invalid headers, and bad colormaps.
- BMP rows are stored bottom-up in files; this module preloads the entire image into a virtual array and emits rows top-down.
- Computes physical row width including 4-byte BMP scanline padding.
- For Windows/OS2 headers with positive pels-per-meter values, sets JFIF density as dots/cm.
- Sets compressor input as 8-bit `JCS_RGB` with three components.

Dependencies:
- `cdjpeg.h`, IJG memory manager virtual sample arrays, progress monitor hooks, BMP/JPEG error codes.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/rdbmp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/rdcolmap.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/rdcolmap.c

Purpose: implements `djpeg -map file` by reading an external color map from GIF or PPM and installing it into the decompressor.

Key contents:
- Compiled only when `QUANT_2PASS_SUPPORTED` is enabled.
- `add_map_entry()` deduplicates RGB colors and appends them to `cinfo->colormap`.
- `read_gif_map()` reads a GIF global color table from the header/logical screen descriptor.
- PPM helpers: `pbm_getc()` skips comments and `read_pbm_integer()` parses decimal header/sample values.
- `read_ppm_map()` reads text PPM (`P3`) or raw PPM (`P6`) and adds each unique pixel color.
- Public entry: `read_color_map()` allocates maximum colormap storage, dispatches by first byte, and fills `actual_number_of_colors`.

Important behavior:
- GIF support here only reads the global color table for mapping; it is separate from GIF image decoding.
- GIF samples are shifted to match `BITS_IN_JSAMPLE`.
- PPM rescaling is not implemented; `maxval` must equal `MAXJSAMPLE`.
- Duplicate colors are ignored.
- Colormap size is capped at `MAXJSAMPLE + 1`; overflow raises `JERR_QUANT_MANY_COLORS`.
- Bad or unsupported map files raise `JERR_BAD_CMAP_FILE`.

Dependencies:
- `cdjpeg.h`, decompressor memory manager, two-pass quantization support, JPEG error macros.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/rdcolmap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/rdgif.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/rdgif.c

Purpose: placeholder `cjpeg` GIF input module.

Key contents:
- Includes `cdjpeg.h`.
- Compiled only when `GIF_SUPPORTED` is enabled.
- Exports `jinit_read_gif()`.

Important behavior:
- Actual GIF image reading was removed from the IJG distribution for LZW patent concerns.
- If compiled and selected, `jinit_read_gif()` prints an unsupported message and exits with failure.
- Returns `NULL` only to satisfy compilers; normal control flow exits.

Dependencies:
- `cdjpeg.h`, stdio, application exit constants.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/rdgif.c -->