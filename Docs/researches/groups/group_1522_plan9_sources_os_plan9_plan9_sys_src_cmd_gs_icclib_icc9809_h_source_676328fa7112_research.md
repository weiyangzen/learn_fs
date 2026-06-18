# Group Research: group_1522_plan9_sources_os_plan9_plan9_sys_src_cmd_gs_icclib_icc9809_h_source_676328fa7112

Scope: `Docs/research_subset_a.md`, source tree `sources/os/plan9/plan9`. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/icclib/icc9809.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/icclib/icc9809.h

ICC profile format header corresponding to ICC.1:1998-09, modified for icclib V2.00 and related ColorSync/ICC additions.

Key behavior:
- Defines ICC constants such as `icMagicNumber`, `icVersionNumber`, profile flags, device attribute bits, screening flags, phosphor/colorant IDs, and ColorSync video-card gamma format values.
- Provides numeric typedefs for ICC on-disk integer/fixed/signature types, using `ORD32`/`INR32` when supplied, SGI-specific typedefs under `__sgi`, and default C integer typedefs otherwise.
- Defines major ICC signature enums: tag signatures, technology signatures, tag type signatures, color space signatures, profile class signatures, platform signatures, measurement/rendering/illuminant values, device media/dither/settings signatures, and response-curve measurement units.
- Models ICC variable-length binary records with the `data[icAny]` convention.
- Defines primitive array/tag payload structures including integer arrays, fixed arrays, date/time, XYZ numbers, curves, data blocks, LUT8/LUT16, measurements, named colors, profile sequence descriptions, text descriptions, screening, UCR/BG, viewing conditions, CRD info, device settings, response curves, tag bases, tag wrappers, tag table entries, profile headers, and full profile layout.
- Keeps obsolete `icNamedColor` and `icNamedColorType` declarations for older profile compatibility.

Dependencies:
- Standalone C header; optionally depends on external platform typedefs `ORD8`, `ORD16`, `ORD32`, `INR8`, `INR16`, `INR32` or SGI `sgidefs.h`.
- Consumers must supply byte-order conversion and allocation/parsing logic elsewhere.

Research notes:
- This is binary-format schema, not executable logic.
- The default typedefs assume `long` is the correct 32-bit storage size, which is risky on LP64 platforms unless `ORD32`/`INR32` override definitions are used.
- The structs describe on-disk ICC records but do not enforce packing, alignment, bounds, or endian conversion.
- Many structures contain trailing variable data; callers must compute sizes from tag lengths/counts and avoid using `sizeof` as the full payload size.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/icclib/icc9809.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/ansi2knr.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/ansi2knr.c

Utility that converts ANSI C function definitions to K&R-style definitions for traditional C compilers.

Key behavior:
- Contains a large embedded license/comment preamble, then portable C implementation guarded for systems with or without GNU `configure` output.
- `main` accepts `ansi2knr input_file [output_file]`, supports the historical `--varargs` switch, emits a `#line` directive, reads the input into a fixed 5000-byte buffer, and converts only recognized function definitions.
- `skipspace` skips whitespace and C comments forward or backward.
- `writeblanks` overwrites spans with spaces while preserving newlines.
- `test1` detects candidate function definitions by requiring an identifier at the left margin, a non-keyword function name, a parenthesized argument list, and suitable trailing syntax.
- `convert1` rewrites a detected ANSI-style header into K&R form by extracting argument names, erasing embedded prototype arguments, handling function-pointer/array declarators, handling `void` parameter lists, and converting varargs to `va_alist`/`va_dcl`.
- Avoids converting prototypes because Ghostscript/IJG declaration macros resemble prototypes and can confuse the parser.

Dependencies:
- Uses stdio, ctype, string APIs, malloc/free, and optional `config.h`.
- Has portability branches for BSD strings, VMS declarations, MSDOS malloc header, K&R library declarations, and `isascii` behavior.

Research notes:
- This is a heuristic source-to-source transformer, not a full C parser.
- It intentionally recognizes only a narrow definition style and can be confused by macros or other left-margin constructs that mimic function definitions.
- The fixed input buffer and repeated string manipulation make it unsuitable for arbitrary modern C without validation.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/ansi2knr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/cderror.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/cderror.h

Application-specific IJG message-code header for `cjpeg`, `djpeg`, and their image format modules.

Key behavior:
- Uses the IJG `JMESSAGE(code,string)` inclusion pattern.
- On first inclusion without `JMESSAGE`, defines the `ADDON_MESSAGE_CODE` enum beginning at `JMSG_FIRSTADDONCODE=1000`.
- On repeated inclusion without `JMESSAGE`, expands to no-ops.
- When included with a caller-defined `JMESSAGE`, emits message table entries.
- Defines conditional error/trace/warning messages for BMP, GIF, PPM/PGM, RLE, and Targa support.
- Defines shared application messages for bad color map files, excessive output colors, failed `ungetc`, unknown input format, and unsupported output format.
- Ends enum generation with `JMSG_LASTADDONCODE`.

Dependencies:
- Depends on feature macros such as `BMP_SUPPORTED`, `GIF_SUPPORTED`, `PPM_SUPPORTED`, `RLE_SUPPORTED`, and `TARGA_SUPPORTED`.
- Intended to be used with IJG `jerror.c`/`jpeg_error_mgr` addon message table fields.

Research notes:
- This header is deliberately multi-include and macro-driven.
- Message availability changes at compile time with supported image formats, so numeric addon codes depend on build configuration.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/cderror.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/cdjpeg.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/cdjpeg.c

Common support routines shared by IJG command-line applications such as `cjpeg`, `djpeg`, and `jpegtran`.

Key behavior:
- Under `NEED_SIGNAL_CATCHER`, installs handlers for `SIGINT`/`SIGTERM`; the handler suppresses tracing, calls `jpeg_destroy`, and exits to clean memory/temp files.
- Under `PROGRESS_REPORT`, defines `progress_monitor`, `start_progress_monitor`, and `end_progress_monitor` for stderr percentage output across library and application extra passes.
- `keymatch` performs case-insensitive matching of possibly abbreviated command-line switches with a minimum abbreviation length.
- `read_stdin` and `write_stdout` put standard streams into binary mode using optional `setmode` or `fdopen` portability hooks.

Dependencies:
- Includes `cdjpeg.h`, ctype, and optional signal/fcntl/io headers.
- Calls IJG common APIs such as `jpeg_destroy`.
- Relies on compile-time feature macros from `jconfig.h`.

Research notes:
- Most code is conditional portability glue.
- The signal handler uses a single static `sig_cinfo`, so it is intended for one active JPEG object per process.
- Binary-mode handling is critical for non-Unix platforms but usually inert on Plan 9/Unix-like environments.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/cdjpeg.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/cdjpeg.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/cdjpeg.h

Shared declarations for IJG sample applications `cjpeg` and `djpeg`; not used by the core JPEG library.

Key behavior:
- Defines `JPEG_CJPEG_DJPEG` and `JPEG_INTERNAL_OPTIONS` before including IJG headers so application feature switches are visible.
- Declares the `cjpeg_source_struct` source-module interface: `start_input`, `get_pixel_rows`, `finish_input`, input `FILE`, row buffer, and buffer height.
- Declares the `djpeg_dest_struct` output-module interface: `start_output`, `put_pixel_rows`, `finish_output`, output `FILE`, row buffer, and buffer height.
- Defines `cdjpeg_progress_mgr`, extending `jpeg_progress_mgr` with extra pass accounting and cached percentage.
- Provides short external-name mappings under `NEED_SHORT_EXTERNAL_NAMES`.
- Declares image module factories for BMP, GIF, PPM, RLE, and Targa readers/writers.
- Declares cjpeg option helpers from `rdswitch.c`, djpeg color map helper from `rdcolmap.c`, common helpers from `cdjpeg.c`, and binary `fopen` mode macros.
- Defines portable exit codes, including VMS-specific success/warning behavior.

Dependencies:
- Includes `jinclude.h`, `jpeglib.h`, `jerror.h`, and `cderror.h`.
- Depends on the rest of the IJG application modules to implement the declared factories/helpers.

Research notes:
- This is the application-module contract for file format adapters.
- It exposes internal option macros because the command-line tools need to know which optional formats/features were compiled.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/cdjpeg.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/cjpeg.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/cjpeg.c

Command-line JPEG compressor front end from the IJG sample applications.

Key behavior:
- Builds an addon message table from `cderror.h`.
- `select_file_type` picks an input reader by first byte or by explicit `-targa`; supports BMP, GIF, PPM/PGM, RLE, and Targa when compiled.
- `usage` prints supported switches based on compiled features.
- `parse_switches` handles compressor options including arithmetic coding, baseline quantizers, DCT method, debug/verbose tracing, grayscale output, max memory, entropy optimization, output filename, progressive mode, quality, quantization-table file, quantization slots, restart intervals, sampling factors, scan scripts, input smoothing, and Targa forcing.
- Delays some option application until image header/color space is known: quality/table processing, qslots, sampling factors, progressive setup, and scan scripts.
- `main` creates a `jpeg_compress_struct`, installs standard errors plus addon messages, optionally enables signal cleanup, sets default compressor parameters, parses filenames, opens binary input/output, initializes progress reporting, selects and starts the source module, updates default colorspace from input, reparses switches for real, starts compression, writes scanlines from the source manager, finishes input/compression, destroys the object, closes files, and exits with warning status if needed.

Dependencies:
- Uses `cdjpeg.h`, `jversion.h`, IJG compressor APIs, format-reader modules, `rdswitch.c` helpers, and optional Macintosh command-line support.
- Uses compile-time feature macros for optional codecs and compressor capabilities.

Research notes:
- The two-pass switch parse is intentional: first pass finds filenames; second pass applies settings after input color space is known.
- File type detection only consumes one byte because portable `ungetc` guarantees only one pushed-back character.
- Unsupported compile-time features fail early with explicit messages.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/cjpeg.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/ckconfig.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/ckconfig.c

Manual configuration helper that compiles and runs to generate `jconfig.h` for IJG builds on systems without autoconf.

Key behavior:
- Starts with editable `#define`/`#undef` probes for standard headers, BSD strings, `sys/types.h`, special size_t includes, prototypes, `unsigned char`, `unsigned short`, `void`, `const`, incomplete types, and short external names.
- Provides small test functions to exercise prototypes, method-pointer declarations, `void *`, function pointers returning void, const behavior, and duplicate external-name handling.
- `is_char_signed` detects signedness and warns if `char` does not appear to be 8 bits.
- `is_shifting_signed` detects whether right shift of negative `long` values is arithmetic or logical.
- `main` writes `jconfig.h` with detected/configured macros, internal JPEG right-shift setting, and application feature defaults for BMP/GIF/PPM/Targa support, disabled RLE, Unix-style command line, signal catcher, binary mode, and optional progress reporting.
- Prints user guidance about using `makefile.ansi` or `makefile.unix`.

Dependencies:
- Uses stdio plus optional stddef, stdlib, strings/string, sys/types, and a placeholder special include.
- Assumes the user may need to edit the file based on compiler errors before running it.

Research notes:
- This is a historical interactive portability probe, not an automatic robust configure system.
- The generated application feature defaults may need manual adjustment for the target platform.
- It writes directly to `jconfig.h` in the current directory.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/ckconfig.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/configure -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/configure

Autoconf 2.12-generated configure script for the IJG JPEG library subtree.

Key behavior:
- Parses standard configure options plus IJG additions: `--enable-shared`, `--enable-static`, and `--enable-maxmem[=N]`; also supports older `--with-maxmem`.
- Sets installation directory variables, program transform options, cache/site handling, source directory discovery, logging to `config.log`, and locale normalization.
- Locates an acceptable C compiler, detects cross-compilation, GNU C, C preprocessor invocation, and default CFLAGS.
- Probes C language/library features: function prototypes, stddef/stdlib/string headers, `size_t`, unsigned char/short, `void`, working `const`, inline spelling, incomplete type behavior, short external names, char signedness, signed right shift, and binary `fopen("b")` support.
- Locates `install-sh`/`install.sh`, selects a BSD-compatible install program, and finds `ranlib`.
- Optionally configures GNU libtool via `ltconfig`, setting object/library suffix variables and install/link commands.
- Chooses memory manager object: `jmemnobs.$(O)` by default, `jmemansi.$(O)` when maxmem and `tmpfile()` are available, or `jmemname.$(O)` with signal catcher/mktemp checks otherwise.
- Extracts `JPEG_LIB_VERSION` from `jpeglib.h`.
- Decides whether `ansi2knr` is needed based on prototype support and whether `-DBSD` is needed for it.
- Generates `config.status`, then creates `Makefile` from `makefile.cfg` and `jconfig.h` from `jconfig.cfg`.

Dependencies:
- Requires POSIX-ish `/bin/sh`, sed, grep/egrep, compiler/linker tools, source files such as `jcmaster.c`, templates `makefile.cfg` and `jconfig.cfg`, and helper scripts such as `install-sh`; optional libtool files are used when shared/static libtool builds are enabled.

Research notes:
- This is generated build infrastructure, not handwritten runtime code.
- Cross-compiling paths use assumptions for char signedness, right shift, and binary fopen behavior.
- The script creates and removes `conftest*`, `confdefs*`, `config.log`, `config.cache`, and `config.status` artifacts during normal execution.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/configure -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/djpeg.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/djpeg.c

Command-line JPEG decompressor front end from the IJG sample applications.

Key behavior:
- Builds an addon message table from `cderror.h`.
- Defines output format enum values for BMP, GIF, OS/2 BMP, PPM/PGM, RLE, Targa, and TIFF placeholder, with `DEFAULT_FMT` defaulting to PPM.
- `usage` prints decompression/output switches based on compiled capabilities.
- `parse_switches` handles output format selection, color quantization, IDCT method, dithering, debug/verbose tracing, fast mode, grayscale output, external color map loading, max memory, fancy upsampling suppression, one-pass quantization, output filename, and scaling.
- `jpeg_getc` reads marker bytes from the JPEG source manager and rejects suspension.
- `print_text_marker` replaces selected marker processors to print COM and APP12 marker payloads as readable text when tracing is enabled.
- `main` creates a decompressor, installs standard and addon errors, installs COM/APP12 marker processors, optionally enables signal cleanup, parses filenames, opens binary input/output, starts progress reporting, reads JPEG headers, reparses switches for real, chooses an output destination module, starts decompression, streams scanlines into the output module, finishes output/decompression in the correct memory-lifetime order, destroys the object, closes files, and exits with warning status if needed.

Dependencies:
- Uses `cdjpeg.h`, `jversion.h`, ctype, IJG decompressor APIs, destination modules, `rdcolmap.c`, and optional Macintosh command-line support.
- Compile-time feature macros determine available output modules and options.

Research notes:
- Like `cjpeg`, switch parsing is split so file handling and trace level are available before full parameter application.
- Marker printing relies on a non-suspending data source.
- Output module initialization occurs after option parsing and before `jpeg_start_decompress` so format modules can force crucial settings such as quantization.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/djpeg.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/example.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/example.c

Documentation-style sample code showing how to embed the IJG JPEG library for compression and decompression.

Key behavior:
- Declares external application image inputs `image_buffer`, `image_height`, and `image_width`.
- `write_JPEG_file` demonstrates compression setup: standard error manager, `jpeg_create_compress`, stdio destination, image dimensions/components/colorspace, defaults, quality setting, `jpeg_start_compress`, one-row-at-a-time `jpeg_write_scanlines`, `jpeg_finish_compress`, file close, and `jpeg_destroy_compress`.
- Defines `my_error_mgr`, extending `jpeg_error_mgr` with a `jmp_buf`.
- `my_error_exit` overrides fatal error handling by printing the message then `longjmp`ing to caller-controlled cleanup.
- `read_JPEG_file` demonstrates decompression with error recovery: open input first, install custom error manager, establish `setjmp`, create decompressor, stdio source, read header, start decompression, allocate a one-row sample array from the JPEG memory manager, read scanlines, pass rows to application hook `put_scanline_someplace`, finish, destroy, close, and return success/failure.

Dependencies:
- Uses stdio, setjmp, and `jpeglib.h`.
- References external application data and a placeholder output hook `put_scanline_someplace`.

Research notes:
- This file is not intended to be a standalone program.
- It intentionally shows a minimal compressor path and a more robust decompressor path with fatal-error recovery.
- Comments call out important API contracts: set error manager before object creation, keep error manager lifetime tied to JPEG object, use binary file mode where required, and destroy JPEG objects on errors.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/example.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/install-sh -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/install-sh

Portable shell install helper derived from X11R5 `install.sh`.

Key behavior:
- Supports testing via `DOITPROG=echo`.
- Allows tool overrides through environment variables such as `MVPROG`, `CPPROG`, `CHMODPROG`, `CHOWNPROG`, `CHGRPPROG`, `STRIPPROG`, `RMPROG`, and `MKDIRPROG`.
- Parses BSD-like options: `-c` copy instead of move, `-d` create directory, `-m` mode, `-o` owner, `-g` group, `-s` strip, `-t=` transform sed expression, and `-b=` transform basename suffix.
- Validates source and destination arguments, handles directory destinations by appending the source basename, and emulates `dirname` with sed.
- Creates missing destination directories component by component.
- For directory creation, applies optional owner/group/strip/chmod commands.
- For file installation, copies or moves to a temp file in the destination directory, applies ownership/group/strip/mode changes, removes any previous destination, then renames the temp file into place.

Dependencies:
- Requires `/bin/sh`, sed, basename, and basic file utilities.
- Intended for use by configure-generated Makefiles when a system install program is missing or unsuitable.

Research notes:
- Installs one file at a time.
- Uses an old temp-file name pattern `#inst.$$#`; interrupted installs rely on traps for cleanup.
- Does not quote all path uses consistently by modern standards, so paths with spaces or shell metacharacters are unsafe.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/install-sh -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jcapimin.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jcapimin.c

Minimum public API implementation for the compression side of the IJG JPEG library, used by both full compression and transcoding-only cases.

Key behavior:
- `jpeg_CreateCompress` validates library version and struct size, preserves caller-provided error manager and client data, zeroes the compression object, initializes the memory manager, clears permanent object pointers/tables, sets default input gamma, and enters `CSTATE_START`.
- `jpeg_destroy_compress` and `jpeg_abort_compress` delegate to common destroy/abort routines.
- `jpeg_suppress_tables` marks all defined quantization and Huffman tables as already-written or not-written for abbreviated stream control.
- `jpeg_finish_compress` validates state, finishes the first pass if scanline/raw input was active, runs remaining multipass coefficient-output passes, writes the file trailer, terminates destination output, and aborts/reset-frees working memory.
- `jpeg_write_marker` writes a complete COM/APPn-style marker between start-compress and first data write.
- `jpeg_write_m_header` and `jpeg_write_m_byte` provide piecemeal marker writing.
- `jpeg_write_tables` emits an abbreviated table-only datastream, initializing the destination and marker writer, writing tables, terminating the destination, and intentionally not aborting afterward to avoid freeing application-owned allocations from the JPEG memory manager.

Dependencies:
- Internal IJG headers `jinclude.h` and `jpeglib.h`.
- Calls memory manager, marker writer, destination manager, master controller, coefficient controller, and common API routines.

Research notes:
- State checks are strict and protect public API call ordering.
- Marker writing is only legal before the first scanline/raw-data write.
- The table-writing behavior intentionally changed from older releases to avoid surprising applications, at the cost of possible leaks if callers repeat it without resetting.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jcapimin.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jcapistd.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jcapistd.c

Standard public compressor API implementation for normal full-image compression.

Key behavior:
- `jpeg_start_compress` requires `CSTATE_START`, optionally unsuppresses all tables, resets error/destination modules, initializes the full compression master, prepares the first pass, sets `next_scanline` to zero, and transitions to `CSTATE_SCANNING` or `CSTATE_RAW_OK`.
- `jpeg_write_scanlines` requires scanline state, warns on excess calls, updates progress monitor state, lets the master perform delayed pass startup on first data write, clamps input rows to the remaining image height, calls the main controller’s `process_data`, advances `next_scanline`, and returns rows consumed.
- `jpeg_write_raw_data` requires raw-data state, warns on excess calls, updates progress, performs delayed startup, requires at least one full iMCU row, calls the coefficient controller directly, handles suspension by returning zero, advances `next_scanline`, and returns the iMCU-row height.

Dependencies:
- Internal IJG compressor modules via `jpeglib.h`: destination manager, master controller, main controller, coefficient controller, progress monitor, and table suppression routine from `jcapimin.c`.

Research notes:
- This file is separated from `jcapimin.c` so transcoding-only programs need not link the whole compressor.
- Delayed pass startup is what allows applications to write special markers after `jpeg_start_compress` and before image data.
- Raw-data callers must supply exactly enough component data for an iMCU row contract.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jcapistd.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jccoefct.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jccoefct.c

Compression coefficient buffer controller: top-level bridge between forward DCT/quantization and entropy encoding.

Key behavior:
- Enables full-image coefficient buffering when entropy optimization or compressor multiscan support is compiled.
- Defines private `my_coef_controller` containing public controller methods, iMCU row counters, current MCU counters, a per-MCU block pointer buffer, and optional per-component virtual coefficient arrays.
- `start_iMCU_row` initializes row counters differently for interleaved and noninterleaved scans, with bottom-image handling.
- `start_pass_coef` selects pass behavior: single pass-through, first save-and-pass pass, or later output-only pass.
- `compress_data` handles single-pass compression: builds MCU block lists from source sample planes, runs forward DCT, creates dummy right-edge and bottom-edge blocks with DC values chosen for compact entropy coding, calls entropy `encode_mcu`, and preserves counters on suspension.
- `compress_first_pass` handles multipass first pass: DCTs all components into virtual block arrays, pads right and bottom edges, then emits the current strip through `compress_output`.
- `compress_output` reads MCU block pointers from virtual arrays for the current scan and feeds entropy coding, preserving counters on suspension.
- `jinit_c_coef_controller` allocates the controller, installs `start_pass`, and either allocates full-image virtual arrays padded to sampling factors or a single-MCU large buffer.

Dependencies:
- Internal IJG compressor types and services from `jinclude.h` and `jpeglib.h`.
- Uses memory manager allocation/virtual-array APIs, forward DCT module, entropy encoder, component geometry, and buffer-mode enums.

Research notes:
- Suspension support is stateful: `mcu_ctr` and `MCU_vert_offset` are saved so encoding can resume.
- In single-pass suspension, the current MCU may be re-DCTed on retry.
- Dummy block DC replication at image edges is an intentional compression-size optimization.
- Full coefficient buffering is required for optimized Huffman coding and multiscan/progressive-style output paths.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jccoefct.c -->