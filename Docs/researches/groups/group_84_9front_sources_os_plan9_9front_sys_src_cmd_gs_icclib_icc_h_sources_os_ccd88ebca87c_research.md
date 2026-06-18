# Group Research: group_84_9front_sources_os_plan9_9front_sys_src_cmd_gs_icclib_icc_h_sources_os_ccd88ebca87c

Scope: `Docs/research_subset_a.md`, specifically `sources/os/plan9/9front` under the bundled Ghostscript `gs` source tree. I read all 12 listed files completely. This group covers icclib ICC profile declarations plus Independent JPEG Group command-line/helper/configuration files embedded in the 9front Ghostscript tree.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/icclib/icc.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/icclib/icc.h

Primary public header for Graeme Gill's `icclib` ICC profile library.

Key points:
- Defines platform-sized signed/unsigned integer aliases (`INR8/16/32`, `ORD8/16/32`) and includes `icc9809.h`, which supplies the raw ICC.1:1998-09 on-disk constants and structures.
- Provides object-like C interfaces with function pointers for file access (`icmFile`), standard-file backing (`icmFileStd`), memory-image backing (`icmFileMem`), heap allocation (`icmAlloc`), and the top-level `icc` profile object.
- Uses `ICM_BASE_MEMBERS` as a common tag-object method layout: tag type, owning profile pointer, touched/refcount bookkeeping, size/read/write/delete methods, dump, and allocate.
- Defines in-memory/native forms of ICC tag data: numeric arrays, `icmXYZNumber`, response curves, transfer curves with reverse lookup cache (`icmRevTable`), data/text/date tags, LUTs, measurements, named colors, text descriptions, profile sequence descriptions, screening, UCR/BG, viewing conditions, CRD info, and Apple/ColorSync video-card gamma.
- Defines `icmLut` and lookup object families (`icmLuMono`, `icmLuMatrix`, `icmLuLut`) with component operations for curves, matrices, CLUT interpolation, normalization/denormalization, absolute/relative conversion, and range/query helpers.
- The top-level `icc` object exposes profile lifecycle and tag-table APIs: `get_size`, `read`, `write`, `dump`, `del`, `find_tag`, `read_tag`, `add_tag`, `rename_tag`, `link_tag`, `unread_tag`, `read_all_tags`, `delete_tag`, and `get_luobj`.
- Public utilities include signature/string conversion, enum description, XYZ/Lab conversion, standard illuminants (`icmD50`, `icmD65`, `icmBlack`), pseudo-Hilbert grid iteration, chromatic adaptation matrix generation, and Delta-E helpers.

Dependencies and interactions:
- Depends on standard C headers plus `icc9809.h`.
- Implementations are expected in the surrounding icclib C files; this header establishes the ABI-style contract used by Ghostscript color-management code.
- `new_icc()` and `new_icc_a()` create profile objects with default or caller-supplied allocators; all object internals route through the allocator and file abstractions declared here.

Risk notes:
- Assumes native machine sizes compatible with the typedef defaults unless callers override `INR*`/`ORD*`; this matters on platforms where `long` is not 32 bits.
- The API is pointer-heavy and manually reference-counted for tag sharing, so callers must respect `unread_tag`, `delete_tag`, object `del`, and allocator ownership rules.
- `MAX_CHAN` is 15, and LUT helper arrays include `1 << MAX_CHAN` entries; malformed profiles or unsupported channel counts need validation in implementation code.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/icclib/icc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/icclib/icc9809.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/icclib/icc9809.h

Raw ICC.1:1998-09 profile-format header, modified for icclib.

Key points:
- Defines ICC magic/version constants, flags, device attributes, screening encodings, ASCII/binary data flags, phosphor/colorant set IDs, ColorSync video-card gamma format IDs, and `icAny` for variable-length trailing arrays.
- Maps machine-sized integer aliases into ICC fixed-width types when `ORD32`/`INR32` are available; otherwise falls back to SGI-specific or default C typedefs.
- Enumerates public tag signatures such as `A2B0`, `B2A0`, `bXYZ`, `rTRC`, `desc`, `wtpt`, `bkpt`, `ncl2`, `vcgt`, and profile sequence/viewing/screening/measurement tags.
- Enumerates technology signatures, tag type signatures, color spaces, profile classes, platforms, measurement geometry/flare, rendering intents, spot shapes, observers, illuminants, device media/dither settings, and response measurement units.
- Defines on-disk structures for primitive arrays, date/time, XYZ, curves, data tags, LUT8/LUT16 payloads, measurements, named colors, profile sequence descriptions, text descriptions, screening, UCR/BG, viewing conditions, CRD info, device settings, response curves, and all tag-type wrappers.
- Defines the on-disk profile header (`icHeader`), tag table (`icTag`, `icTagList`), full profile layout (`icProfile`), and obsolete named-color types.
- The file comments document variable-length trailing-array layout conventions and explain icclib-specific modifications: guard rename, `icMaxTagVal`, extended color spaces, chromaticity/video gamma additions, and attribute bits.

Dependencies and interactions:
- Included by `icc.h`; `icc.h` wraps these on-disk structures with native, allocator-owned, double-precision in-memory structures and object methods.
- This header does not implement parsing or byte swapping. It supplies constants and packed logical layouts consumed by icclib read/write code.

Risk notes:
- The default fallback uses `long`/`unsigned long` for 32-bit ICC fields, which is unsafe on LP64 platforms unless the formal `ORD32`/`INR32` definitions from `icc.h` are in effect.
- Variable-length arrays use the historical `data[icAny]` idiom; consumers must size allocations from file lengths/counts, not `sizeof` the wrapper alone.
- Several comments mark historical or vendor-specific extensions and one questionable enum (`icMeasurementFlare` as enum despite being conceptually u16.16), so compatibility depends on implementation interpretation.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/icclib/icc9809.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/ansi2knr.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/ansi2knr.c

Standalone converter from ANSI C function definitions to traditional K&R syntax.

Key points:
- Carries the historical Ghostscript GPL/COPYLEFT text and an explicit note that using the converter during a build does not impose that license on the invoking program.
- Supports `ansi2knr input_file [output_file]`, writing to stdout when no output file is supplied.
- Handles configured and non-configured builds with conditional includes for `config.h`, string headers, `stdlib.h`, `malloc`, VMS/MS-DOS/BSD behavior, and ctype portability.
- Main processing loop reads into a fixed 5000-byte buffer, emits an initial `#line`, identifies possible function definitions with `test1`, and converts recognized definitions with `convert1`.
- `test1` recognizes a non-keyword identifier at the left margin followed by a parenthesized parameter list and either a completed header or a possible multi-line header.
- `skipspace` skips whitespace and block comments in either direction; `writeblanks` erases source spans while preserving line endings.
- `convert1` parses argument declarations, handles function-pointer/array declarator cases, erases embedded prototype parameters, converts `void` argument lists to empty K&R lists, and maps varargs `...` to `va_alist`/`va_dcl`.

Dependencies and interactions:
- Used by old IJG/Ghostscript build flows when the compiler lacks ANSI prototypes; `configure` sets `A2K_DEPS` and `COM_A2K` based on prototype support.
- Its output is a source-level compatibility transform, not part of libjpeg runtime.

Risk notes:
- The function recognizer is intentionally heuristic and comments list constructs that can confuse it, including left-margin macro/function-call lookalikes and macros that alter function-header syntax.
- Uses a fixed buffer and restarts parsing when a multi-line candidate overflows; very long declarations can be emitted unchanged.
- It rewrites C text without a real parser, so modern C constructs beyond the era it targets are not safe inputs.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/ansi2knr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/cderror.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/cderror.h

Application-specific error/message catalog for IJG sample programs `cjpeg`, `djpeg`, and related helpers.

Key points:
- Uses the IJG `JMESSAGE(code,string)` pattern: first inclusion without `JMESSAGE` creates an enum; later inclusion with a caller-supplied macro creates a message table.
- Defines addon message codes starting at `JMSG_FIRSTADDONCODE=1000` and ending at `JMSG_LASTADDONCODE`.
- Feature-gated messages cover BMP, GIF, PPM/PGM, Utah RLE, and Targa support.
- Common messages cover invalid color-map files, too many output colors, `ungetc` failure, unknown input format, and unsupported output format.
- If `TARGA_SUPPORTED` is not compiled, the Targa-specific diagnostic becomes a "support not compiled" message.

Dependencies and interactions:
- Included by `cdjpeg.h` after `jerror.h`, making app-specific messages available beside core JPEG library errors.
- `cjpeg.c` and `djpeg.c` include it with `JMESSAGE` defined to create `cdjpeg_message_table`, then attach that table to the IJG error manager.
- Format modules such as BMP/GIF/PPM/RLE/Targa readers and writers use these message codes.

Risk notes:
- The active enum/table contents depend on compile-time feature macros, so all compilation units that share message codes must use consistent feature definitions.
- It is not a standalone include guard in the usual sense; its multi-include behavior depends on `JMESSAGE` and `JMAKE_ENUM_LIST`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/cderror.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/cdjpeg.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/cdjpeg.c

Common runtime support routines for IJG command-line applications.

Key points:
- Optionally installs signal handlers (`enable_signal_catcher`) for `SIGINT` and `SIGTERM` when `NEED_SIGNAL_CATCHER` is enabled, calling `jpeg_destroy` before process exit so temporary files and JPEG memory are cleaned up.
- Optional progress-monitor support (`PROGRESS_REPORT`) prints percent completion to stderr, including extra application-level passes not known to the JPEG library.
- `keymatch` performs case-insensitive, minimum-length abbreviation matching for command-line switches.
- `read_stdin` and `write_stdout` put standard streams into binary mode where required, using `setmode` or `fdopen` depending on configured macros.

Dependencies and interactions:
- Includes `cdjpeg.h`, ctype, and optionally signal/fcntl/io headers.
- Called by `cjpeg.c` and `djpeg.c` for option parsing, binary stdio setup, progress display, and temporary-file cleanup.
- The signal catcher stores one global `j_common_ptr`, so it is aimed at single active JPEG command-line processes.

Risk notes:
- Signal cleanup depends on a global pointer and calls nontrivial cleanup from a signal handler; this reflects historical portability goals rather than modern async-signal-safety practice.
- Progress percentage divides by `pass_limit`; callers rely on IJG progress manager invariants to avoid invalid limits.
- Binary stdio reopening is highly platform-dependent and controlled by `jconfig.h`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/cdjpeg.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/cdjpeg.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/cdjpeg.h

Shared declarations for IJG sample applications `cjpeg` and `djpeg`.

Key points:
- Defines `JPEG_CJPEG_DJPEG` and `JPEG_INTERNAL_OPTIONS` before including `jinclude.h`, `jpeglib.h`, `jerror.h`, and `cderror.h`, enabling app-specific feature macros and internal options.
- Declares the `cjpeg_source_struct` input-module interface: `start_input`, `get_pixel_rows`, `finish_input`, input file, row buffer, and buffer height.
- Declares the `djpeg_dest_struct` output-module interface: `start_output`, `put_pixel_rows`, `finish_output`, output file, row buffer, and buffer height.
- Defines `cdjpeg_progress_mgr`, extending `jpeg_progress_mgr` with extra pass counts and cached printed percent.
- Provides short external-name aliases under `NEED_SHORT_EXTERNAL_NAMES` for systems with limited linker symbol length.
- Declares module factories for BMP, GIF, PPM/PGM, RLE, and Targa readers/writers.
- Declares command support routines from `rdswitch.c`, color-map reading from `rdcolmap.c`, and common helpers from `cdjpeg.c`.
- Defines portable `READ_BINARY`, `WRITE_BINARY`, and exit-code macros.

Dependencies and interactions:
- This is the interface contract between `cjpeg.c`/`djpeg.c` and format-specific modules such as `rdbmp.c`, `rdppm.c`, `wrgif.c`, and `wrbmp.c`.
- Compile-time feature macros in `jconfig.h` decide which declared factories are actually available.

Risk notes:
- The header intentionally exposes internal JPEG options to applications; it is not part of the stable core library API.
- Factory declarations are unconditional, but callers guard use by feature macros; inconsistent `jconfig.h` settings can produce link failures.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/cdjpeg.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/cjpeg.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/cjpeg.c

Command-line JPEG compressor front end.

Key points:
- Creates an app-specific message table from `cderror.h`, initializes `jpeg_compress_struct`, attaches the message table, and uses IJG default error handling.
- `select_file_type` detects input format from the first byte, constrained by portable `ungetc` behavior; Targa can be forced with `-targa` because not all Targa files are first-byte-identifiable.
- `usage` lists baseline and advanced switches, feature-gated by compile-time support for entropy optimization, progressive mode, arithmetic coding, DCT methods, smoothing, multiscan scripts, and Targa.
- `parse_switches` handles quality, grayscale, DCT method, restart intervals, smoothing, max memory, output filename, verbose/debug, arithmetic coding, baseline quantization, external quantization tables, quantization slots, sampling factors, progressive mode, scan scripts, optimization, and Targa forcing.
- Parsing runs twice: a first pass finds file names before the source format is known, and a second real pass after input header parsing applies colorspace-dependent defaults and delayed options.
- `main` opens input/output according to Unix or two-file command-line style, starts optional progress monitoring, initializes the selected source module, calls `jpeg_default_colorspace`, sets `jpeg_stdio_dest`, starts compression, repeatedly pulls source pixel rows and writes scanlines, then finishes and cleans up.

Dependencies and interactions:
- Depends on `cdjpeg.h`, `jversion.h`, source modules (`jinit_read_*`), switch helpers (`read_quant_tables`, `read_scan_script`, `set_quant_slots`, `set_sample_factors`), and common helpers from `cdjpeg.c`.
- Format support is selected by `BMP_SUPPORTED`, `GIF_SUPPORTED`, `PPM_SUPPORTED`, `RLE_SUPPORTED`, and `TARGA_SUPPORTED`.

Risk notes:
- Input auto-detection only examines one byte, so unsupported or ambiguous formats depend on explicit user switches.
- Command-line parsing uses global `outfilename` and `is_targa`; this is suitable for process-level CLI use, not reentrant library embedding.
- Options that allocate/read external files are deliberately delayed; changes to parsing order must preserve that two-pass design.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/cjpeg.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/ckconfig.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/ckconfig.c

Manual configuration probe program for IJG JPEG builds.

Key points:
- Intended to be edited, compiled, and run on systems without Autoconf support to generate `jconfig.h`.
- Starts with optimistic defines for standard headers, prototypes, unsigned char/short, `void`, `const`, and complete incomplete-type support; comments instruct users to flip defines based on the first compiler error.
- Probes or exercises include `stddef.h`, `stdlib.h`, string vs BSD strings, `sys/types.h` for `size_t`, ANSI prototypes, method-pointer declarations, unsigned types, `void *`, function pointers returning void, `const`, incomplete structure pointers, and external-name length collisions.
- Runtime helpers test whether plain `char` is signed and whether right-shift of negative `long` is arithmetic or logical.
- `main` writes a generated `jconfig.h` with detected/assumed macros plus app-format defaults: BMP/GIF/PPM/Targa enabled, RLE disabled, two-file command line and signal catcher disabled, optional progress commented out.
- Prints post-run guidance choosing `makefile.ansi` or `makefile.unix` based on prototype support.

Dependencies and interactions:
- Alternative to the generated `configure` script for producing `jconfig.h`.
- The generated header drives conditional compilation in `jinclude.h`, `jmorecfg.h`, `cdjpeg.h`, memory managers, and application modules.

Risk notes:
- Because users are expected to edit the file between compile attempts, the output reflects manual decisions as much as automatic detection.
- The generated defaults are generic IJG defaults and may not match the 9front/Ghostscript build system if used directly.
- The runtime tests assume 8-bit `char` and 32-bit-relevant `long` behavior; nontraditional machines are warned as likely unsupported.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/ckconfig.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/configure -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/configure

Autoconf 2.12-generated configuration script for the IJG JPEG subtree.

Key points:
- Parses standard Autoconf directory, host/build/target, program-transform, cache, quiet, site, `--with-*`, and `--enable-*` options.
- Package-specific help covers `--enable-shared`, `--enable-static`, and `--enable-maxmem[=N]`; `--with-maxmem` remains supported for compatibility with older IJG releases.
- Locates source directory by checking for `jcmaster.c`, loads site scripts, opens `config.log`, normalizes locale variables, and builds `confdefs.h`.
- Detects C compiler (`gcc` then `cc`), compiler usability/cross status, GNU C, C preprocessor, function prototypes, standard headers, string header style, `size_t`, unsigned char/short, `void`, working `const`, inline spelling, incomplete-type behavior, short external names, signedness of `char`, signed right shifts, and whether `fopen` accepts binary `b` mode.
- Finds `install-sh`/`install.sh`, chooses a BSD-compatible install program, detects `ranlib`, and optionally configures GNU libtool for shared/static builds.
- Selects JPEG memory manager: default `jmemnobs.$(O)`, `jmemansi.$(O)` when temp-file support and `tmpfile()` are available, or `jmemname.$(O)` with `NEED_SIGNAL_CATCHER` and optional `NO_MKTEMP`.
- Extracts `JPEG_LIB_VERSION` from `jpeglib.h`.
- Sets substitutions controlling `ansi2knr` use, libtool comments, forced shared-library install, include flags, object/archive suffixes, link command, install commands, memory manager, and generated headers.
- Writes `config.status`, which generates `Makefile` from `makefile.cfg` and `jconfig.h` from `jconfig.cfg` using sed substitution fragments.

Dependencies and interactions:
- Consumes `makefile.cfg`, `jconfig.cfg`, `jpeglib.h`, optional `ltconfig`/`ltmain.sh`, and the install helper.
- Its generated `jconfig.h` controls the same compile-time feature gates read by `cdjpeg.h`, `cderror.h`, `cjpeg.c`, `djpeg.c`, memory managers, and library internals.

Risk notes:
- This is very old Autoconf output; it uses temporary files, generated shell code, legacy option spellings, and historical compiler probes that may not represent modern platforms cleanly.
- Cross-compiling paths assume signed `char`, signed right shift, and working binary `fopen` unless overridden, which may produce subtly wrong `jconfig.h`.
- `--enable-maxmem` accepts only numeric megabytes and converts to bytes with `expr`; malformed values are rejected, but very large values depend on shell/arithmetic limits.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/configure -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/djpeg.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/djpeg.c

Command-line JPEG decompressor front end.

Key points:
- Builds an addon message table from `cderror.h`, initializes `jpeg_decompress_struct`, and attaches app-specific message range metadata to the IJG error manager.
- Defines output format enum values for BMP, GIF, OS/2 BMP, PPM/PGM, RLE, Targa, and TIFF placeholder, with `DEFAULT_FMT` defaulting to PPM unless overridden.
- `usage` lists decompression, color quantization, scaling, output format, DCT, dithering, colormap, smoothing, memory, output file, and verbosity switches, feature-gated by compile-time support macros.
- `parse_switches` handles output format selection, color count/quantization, DCT method, dither mode, verbose/debug, fast-mode bundle, grayscale output, external color-map reading, max memory, fancy upsampling suppression, one-pass quantization, output filename, and IDCT scaling.
- Installs custom marker processors for JPEG COM and APP12 markers; `print_text_marker` emits marker text at trace level, escaping nonprintable characters and normalizing CR/LF forms.
- `main` opens input/output, starts optional progress monitoring, sets `jpeg_stdio_src`, reads the JPEG header, reparses real options, initializes the selected destination module, starts decompression, writes the output header, reads scanlines into the destination buffer, emits rows, finishes output/decompression, cleans up, and exits with warning status when appropriate.

Dependencies and interactions:
- Depends on `cdjpeg.h`, `jversion.h`, destination modules (`jinit_write_*`), `read_color_map`, and common helpers from `cdjpeg.c`.
- Uses core IJG APIs including `jpeg_set_marker_processor`, `jpeg_read_header`, `jpeg_start_decompress`, `jpeg_read_scanlines`, and `jpeg_finish_decompress`.

Risk notes:
- The marker printer assumes a non-suspending data source, as stated in comments; it calls `ERREXIT` if suspension would be needed.
- Output format enum includes `FMT_TIFF`, but no TIFF writer is selected in the switch; unsupported/default cases raise `JERR_UNSUPPORTED_FORMAT`.
- Like `cjpeg`, CLI state is global/static and designed for one process invocation, not reentrant embedding.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/djpeg.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/example.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/example.c

Illustrative skeleton for embedding the IJG JPEG library in an application.

Key points:
- Shows a compression routine, `write_JPEG_file`, that uses external RGB image globals, opens a binary output stream, initializes `jpeg_compress_struct` with standard error handling, sets image dimensions/components/colorspace, applies default compression parameters, sets quality, starts compression, writes scanlines top-to-bottom, finishes, closes, and destroys the JPEG object.
- Documents required input pixel layout: row-major `JSAMPLE` arrays with adjacent component samples, e.g. RGB triplets.
- Explains compressor state variables, partial scanline return semantics, temporary-file use for full-image buffering modes, signal-handler considerations, and top-to-bottom scanline ordering.
- Defines a custom error manager (`my_error_mgr`) embedding `jpeg_error_mgr` plus `jmp_buf`.
- `my_error_exit` calls the standard output-message hook and uses `longjmp` to return control to the caller instead of exiting.
- `read_JPEG_file` demonstrates decompression with setjmp-based recovery: opens input, initializes decompressor, sets stdio source, reads header, starts decompression, allocates a one-scanline buffer via the JPEG memory manager, reads scanlines, passes them to an application-provided sink, finishes, destroys, closes, and reports success/failure.
- Notes that the sample intentionally omits useful application behavior and should be read with `libjpeg.doc`.

Dependencies and interactions:
- Includes `stdio.h`, `jpeglib.h`, and `setjmp.h`.
- References application-provided symbols `image_buffer`, `image_height`, `image_width`, and `put_scanline_someplace`.
- Demonstrates public libjpeg APIs rather than Ghostscript-specific wrappers.

Risk notes:
- It is sample code, not directly runnable; required external image storage and output sink are undeclared implementations.
- The decompression buffer allocation after `jpeg_start_decompress` is acknowledged as slightly outside ideal memory-accounting practice; robust code can call `jpeg_calc_output_dimensions` earlier.
- The custom error path must destroy the JPEG object and close the file after `longjmp`; callers adapting this pattern must keep object/error lifetimes aligned.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/example.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/install-sh -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/install-sh

Portable shell install helper derived from X11R5.

Key points:
- Provides BSD-install-like behavior for one file or one directory at a time, avoiding the filename `install.sh` where make implicit rules might create an `install` target artifact.
- Supports dry-run behavior through `DOITPROG`, configurable tool variables (`MVPROG`, `CPPROG`, `CHMODPROG`, `CHOWNPROG`, `CHGRPPROG`, `STRIPPROG`, `RMPROG`, `MKDIRPROG`), and options `-c`, `-d`, `-m`, `-o`, `-g`, `-s`, `-t=...`, and `-b=...`.
- Parses source/destination operands, validates source existence for file installs, treats destination directories by appending the source basename, and derives destination directory with sed.
- Creates missing destination directories component by component using an IFS workaround for old shells.
- Directory mode installs create the directory if absent, then apply owner/group/strip/chmod commands as requested.
- File installs copy or move into a temporary file in the destination directory, set owner/group/strip/chmod options, remove the old destination, then rename the temp file into final position.

Dependencies and interactions:
- Located by `configure` as the auxiliary install script and substituted into generated Makefiles when no suitable system install program is found.
- Used at build/install time only; not part of libjpeg or Ghostscript runtime.

Risk notes:
- Many variable expansions are unquoted, reflecting historical shell portability; paths containing whitespace or shell metacharacters are unsafe.
- The temporary filename uses `#inst.$$#` in the destination directory, so concurrent installs into the same directory by the same PID namespace pattern could collide in unusual conditions.
- The script installs only one file at a time and intentionally preserves old BSD-shell compatibility over modern robustness.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/install-sh -->