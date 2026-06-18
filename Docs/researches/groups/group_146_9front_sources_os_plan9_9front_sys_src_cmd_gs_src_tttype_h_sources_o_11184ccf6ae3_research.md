# Group Research: group_146_9front_sources_os_plan9_9front_sys_src_cmd_gs_src_tttype_h_sources_o_11184ccf6ae3

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/tttype.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/tttype.h

FreeType 1 high-level public API header bundled in Ghostscript’s TrueType support.

Key points:
- Defines public `TT_*` scalar, fixed-point, vector, matrix, outline, bounding-box, raster-map, metrics, face-property, and handle types.
- Uses architecture macros such as `ARCH_LOG2_SIZEOF_LONG` / `ARCH_LOG2_SIZEOF_INT` to choose 32-bit fixed-point storage.
- Exposes handle wrappers for engine, stream, face, instance, glyph, and charmap objects using one-field structs for compile-time type separation.
- Declares lifecycle APIs: `TT_Init_FreeType`, `TT_Done_FreeType`, face open/close/flush, instance creation/destruction, glyph creation/destruction.
- Declares font access APIs for properties, raw table data, charmaps, names, glyph loading, glyph metrics, outlines, bitmap/pixmap rendering, outline allocation/copy/rendering, and matrix/vector transforms.
- Defines load flags `TTLOAD_SCALE_GLYPH`, `TTLOAD_HINT_GLYPH`, and `TTLOAD_DEFAULT`.
- Defines `MAKE_TT_TAG` for TrueType table tags.
- Defines callback ID and callback type for glyph outline loading.
- Defines the main `TT_Error` code space for API, table, memory, file, glyph loader, bytecode interpreter, internal, and raster errors.

Dependencies and interactions:
- Included by `tttypes.h`, which adds internal typedefs and handle conversion macros.
- Used by Ghostscript’s FreeType-derived TrueType loader modules such as `ttload`, `ttobjs`, `tttables`, and interpreter support.
- Public structures are consumed by client-facing glyph/font code and by internal conversion helpers.

Research relevance:
- This is the public contract for the vendored FreeType 1 TrueType engine inside Ghostscript. It determines how fonts, glyphs, outlines, metrics, charmaps, and raster targets are represented across the old Ghostscript font bridge.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/tttype.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/tttypes.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/tttypes.h

Internal FreeType-derived common type header for Ghostscript TrueType code.

Key points:
- Includes `ttconfig.h` and the public `tttype.h`.
- Defines compact aliases: `Byte`, `UShort`, `Short`, `ULong`, `Long`, `Fixed`, `Int`, `Integer`, and pointer aliases.
- Selects `Fixed` from `int` or `long` based on `SIZEOF_INT` / `SIZEOF_LONG`.
- Defines `Pointer`, coordinate pointer types, and touch-table pointer type.
- Supplies `Bool`, `TRUE`, `FALSE`, and `NULL` fallbacks.
- Defines TrueType rounding mode constants.
- Defines point flag masks for on-curve and touched-X/Y state.
- Defines generic `SUCCESS` / `FAILURE` constants and `MIN`, `MAX`, `ABS` macros.
- Defines `HANDLE_*` conversion macros for the typed wrapper handles declared in `tttype.h`.

Dependencies and interactions:
- Used by FreeType-derived internals that need simple scalar aliases and access to opaque handle internals.
- Bridges public `TT_*` types to internal `PFace`, `PInstance`, `PGlyph`, and charmap structures.

Research relevance:
- This header is the internal type glue for Ghostscript’s bundled TrueType subsystem and is important for understanding fixed-point size assumptions and handle casting.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/tttypes.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/turboc.cfg -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/turboc.cfg

Tiny Borland/Turbo C compiler warning configuration file.

Key points:
- Contains five lines of command-line warning switches.
- Disables or adjusts many Turbo C warning classes, including duplicate, return, structure, unused, ambiguous, conversion, and pointer-related diagnostics.
- Ends with `-N`, a Turbo C option.

Dependencies and interactions:
- Intended for old Borland/Turbo C builds rather than the Unix/Plan 9 build path.
- No source code symbols are defined here.

Research relevance:
- Historical build-support artifact for legacy PC compiler compatibility in the Ghostscript source tree.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/turboc.cfg -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/ugcclib.mak -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/ugcclib.mak

Unix/gcc makefile for Ghostscript graphics-library testing rather than the full interpreter.

Key points:
- Builds into `./libobj`, names the output `gslib`, and includes `version.mak`.
- Configures Ghostscript runtime paths, init file, feature devices, device list, bundled JPEG/libpng/zlib/JBIG2/ICC/IJS settings, compiler flags, X11 paths, and platform options.
- Uses `gcc`, `ar`, and `ranlib`; defaults to debug-style `CFLAGS_DEBUG`.
- Includes core fragments: `unixhead.mak`, `gs.mak`, `lib.mak`, image/ICC/IJS makefiles, `devs.mak`, `contrib.mak`, and `unix-aux.mak`.
- Replaces the standard `unixlink.mak` final link with custom rules for `$(GS_XE)` and `libgsgraph.a`.
- The final link builds from `gslib.o`, selected no-GC/config objects, library objects, and device objects.

Dependencies and interactions:
- Depends on generated link scripts from the generic Ghostscript make system.
- Shares Unix platform modules from `unix-aux.mak`.
- Includes `unix-end.mak` for standard directory/debug/profile support.

Research relevance:
- Useful for distinguishing full Ghostscript interpreter builds from library-only testing builds in the old source tree.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/ugcclib.mak -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/unistd_.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/unistd_.h

Portable wrapper/substitute for Unix `unistd.h`.

Key points:
- Includes `std.h` before any headers that may include `sys/types.h`.
- Includes `<io.h>` for OS/2 and Win32.
- For MSVC, maps POSIX-like names to CRT underscore forms: `fsync`, `read`, `isatty`, `setmode`, `fstat`, `dup`, `open`, and `close`.
- For Borland Win32, maps a smaller set of functions to underscore forms.
- Falls back to including system `<unistd.h>` elsewhere.

Dependencies and interactions:
- Used by portable Ghostscript modules that need POSIX file-descriptor routines.
- Interacts with Windows compiler wrappers and the broader `std*.h` portability layer.

Research relevance:
- Captures Ghostscript’s old cross-platform file-descriptor compatibility strategy, especially for Windows compilers.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/unistd_.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/unix-aux.mak -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/unix-aux.mak

Common Unix makefile fragment for platform modules and auxiliary build tools.

Key points:
- Defines Unix platform module `unix_.dev` from `gp_getnv`, `gp_unix`, `gp_unifs`, `gp_unifn`, `gp_stdia`, and `gp_unix_cache`, including `nosync`.
- Defines older System V platform module `sysv_.dev` using `gp_sysv`.
- Provides object compile rules for Unix platform source files.
- Builds auxiliary generators: `echogs`, `genarch`, `genconf`, `gendev`, `genht`, and `geninit`.
- Generates `gconfig_.h` by probing `/usr/include` for directory/time headers and local JPEG memory headers.
- Includes comments about Ultrix `sh -e` behavior and old optimizer issues.

Dependencies and interactions:
- Included by Unix top-level makefiles and the library test makefile.
- Produces generated config headers consumed by core Ghostscript sources.
- Assumes `$(ECHOGS_XE)` is available for generated text output.

Research relevance:
- Central to the Unix portability layer: platform abstraction objects, generated feature headers, and build-time helper tools all originate here.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/unix-aux.mak -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/unix-dll.mak -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/unix-dll.mak

Unix shared-object build fragment for Ghostscript.

Key points:
- Defines shared-object build directories `../soobj` and `../sobin`.
- Defines small loader executables `gsc` and `gsx`; `gsx` links GTK display support via `gtk-config`.
- Defines shared library names and symlink chain: `lib$(GS).so`, `.major`, and `.major.minor`.
- Uses recursive make with `SODEFS` to build the shared library with `-shared`, `-soname`, PIC flags, alternate object directories, `STDIO_IMPLEMENTATION=c`, and display device override.
- Provides targets `so`, `sodebug`, `install-so`, `soinstall`, `SODIRS`, and `soclean`.
- Installs loaders and the shared library into `bindir` / `libdir`.

Dependencies and interactions:
- Included by `unix-gcc.mak`.
- Uses `GS_VERSION_MAJOR`, `GS_VERSION_MINOR`, and `GS_SONAME*` values from `version.mak` and local variables.
- Relies on normal Unix build targets via recursive make.

Research relevance:
- Documents how this Ghostscript snapshot could build a Unix shared library plus small loader binaries before the newer configure-based build style.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/unix-dll.mak -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/unix-end.mak -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/unix-end.mak

Late Unix makefile fragment for directory setup, debug/profile builds, config header generation, and tags.

Key points:
- Defines `STDDIRS` to create binary, generated, and object directories for graphics and interpreter components.
- Defines `PGDIRS` / `PGDEFS` / `pg` / `pgclean` for profiling builds.
- Defines `DEBUGDIRS` / `DEBUGDEFS` / `debug` / `debugclean` for debug builds.
- Generates `gconfigv.h` with `USE_ASM`, `USE_FPU`, `EXTEND_NAMES`, and `SYSTEM_CONSTANTS_ARE_WRITABLE`.
- Provides an `etags` target over graphics and PostScript source headers.

Dependencies and interactions:
- Included near the end of Unix top-level makefiles.
- Uses `ECHOGS_XE`, `TOP_MAKEFILES`, `USE_ASM`, `FPU_TYPE`, and path variables set earlier.

Research relevance:
- Captures build variants and generated platform constants for Unix Ghostscript builds.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/unix-end.mak -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/unix-gcc.mak -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/unix-gcc.mak

Top-level Unix/gcc/X11 Ghostscript makefile.

Key points:
- Configures build directories, install directories, runtime search path, init file, feature/device list, third-party source directories, archive tools, compiler/linker flags, X11 include/lib paths, FPU setting, and synchronization module.
- Defaults to `gcc`, `-O2`, `-Wall`, strict prototype warnings, `-fno-builtin`, `-fno-common`, and `-DHAVE_MKSTEMP`.
- Defaults to `SYNC=nosync` and `STDLIBS=-lm`; comments explain how to enable POSIX sync with pthreads.
- Enables language features including PostScript Level 3, PDF, DPS, TrueType font support, EPSF, pipe device, and FAPI.
- Selects a broad set of X11, printer, raster image, TIFF, PNG, JPEG, PDF/PS/PXL writer, bbox, DeviceN, and spot-color devices.
- Adds `GX_COLOR_INDEX_TYPE='unsigned long long'`.
- Includes the full chain of Ghostscript make fragments: Unix head, graphics library, interpreter, compiled fonts, image libraries, ICC/IJS, devices, contrib, Unix auxiliary/link/DLL/end/install fragments.
- Generates `$(AK)` by detecting old gcc 2.7 optimizer bugs and writing either `-Dconst=` or warning flags.

Dependencies and interactions:
- Main Unix build driver for this Ghostscript tree.
- Pulls together graphics library, PostScript interpreter, bundled libraries, device modules, and install/shared-library fragments.

Research relevance:
- Defines the canonical GCC Unix build configuration and device surface for this vendored Ghostscript snapshot.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/unix-gcc.mak -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/unixansi.mak -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/unixansi.mak

Top-level portable Unix/ANSI C/X11 Ghostscript makefile.

Key points:
- Mirrors the Unix build layout from `unix-gcc.mak` but avoids GCC-specific assumptions.
- Leaves `CC` to the platform unless an ANSI-compatible compiler must be specified.
- Uses simpler flags: standard `-O`, debug `-g`, profile `-pg -O`, and generic `XCFLAGS`.
- Configures runtime/install directories, bundled JPEG/libpng/zlib/JBIG2/ICC/IJS source directories, X11 paths, `FPU_TYPE=1`, and `SYNC=nosync`.
- Enables PostScript Level 3, PDF, DPS, TrueType font support, EPSF, pipe, and FAPI.
- Device list is narrower than `unix-gcc.mak`, though it still includes X11 devices, printers, raster outputs, TIFF/PNG/JPEG, PDF/PS/PXL writers, and bbox.
- Includes Unix head, graphics library, interpreter, compiled fonts, image libraries, ICC/IJS, devices, contrib, Unix auxiliary/link/end/install fragments.
- Provides `distclean` and `maintainer-clean`.

Dependencies and interactions:
- Depends on the same generic Ghostscript make fragments as the GCC file but omits `unix-dll.mak`.
- Uses `CC_NO_WARN=$(CC_)` rather than GCC warning suppression.

Research relevance:
- Shows the portable Unix build path for non-GCC ANSI compilers and provides a contrast with the GCC/X11 build profile.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/unixansi.mak -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/unixhead.mak -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/unixhead.mak

Early common Unix makefile fragment.

Key points:
- Sets `PLATFORM=unix_`.
- Defines command/object/executable syntax for Unix: object suffix `o`, empty executable suffix, `-c`, `-D`, `-I`, `-o`.
- Defines path separator `/`, shell `/bin/sh`, and generic commands `cat`, `cp`, and `rm -f`.
- Defines genconf argument forms for linker files.
- Sets compiler command aliases `CC_D` and `CC_INT`.
- Clears PC-specific assembler variables that would otherwise produce warnings.
- Defines default `std` target as `STDDIRS default`.

Dependencies and interactions:
- Included after compiler-specific options and before core `gs.mak`, `devs.mak`, and `contrib.mak`.
- Supplies basic syntax variables used by all subsequent make fragments.

Research relevance:
- This is the small but essential Unix syntax adapter for the old Ghostscript make system.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/unixhead.mak -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/unixinst.mak -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/unixinst.mak

Final Unix makefile fragment containing install targets.

Key points:
- Defines `install` as `install-exec install-scripts install-data`.
- `install-exec` installs the Ghostscript executable into `bindir`.
- `install-scripts` installs command scripts after rewriting `GS_EXECUTABLE=...`.
- Defines library/resource/documentation/example/man source directories relative to `PSLIBDIR`.
- `install-libdata` installs core `.ps`, Fontmap/cidfmap/FAPI files, PPD/RPD/UPP/XBM/XPM files, and generated `gs_*.ps` / `pdf*.ps`.
- `install-resdata` copies all Resource categories except CVS.
- `install-doc` copies selected HTML/text documentation.
- `install-man` installs localized manpages and creates symlinks for related commands.
- `install-examples` installs sample PostScript/PDF/EPS files.

Dependencies and interactions:
- Uses `INSTALL_PROGRAM`, `INSTALL_DATA`, `gsdatadir`, `scriptdir`, `docdir`, `mandir`, and `exdir` from top-level makefiles.
- Included last by Unix makefiles.

Research relevance:
- Defines the runtime filesystem layout of Ghostscript installations produced by this source tree.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/unixinst.mak -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/unixlink.mak -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/unixlink.mak

Unix final link makefile fragment.

Key points:
- Uses `.NOEXPORT` to prevent GNU make from exporting all environment variables and overflowing old System V command limits.
- Defines interpreter archive object groups: `INT_ARCHIVE_ALL`, `XE_ALL`.
- Provides optional archive target `$(GS).a` using `ar` and `ranlib`.
- Defines final `$(GS_XE)` link rule by generating a shell/link transcript with `echogs`, appending `ld.tr`, adding extra and standard libraries, and executing it through `$(SH)`.
- Sets `LD_RUN_PATH` when `XLIBDIR` is non-empty.
- Clears many large environment variables before executing the final link for SCO Unix environment-space limits.

Dependencies and interactions:
- Included by Unix top-level makefiles.
- Consumes generated object/link lists from `gs.mak`, `int.mak`, `devs.mak`, and related fragments.

Research relevance:
- Captures how old Ghostscript avoided command-line and environment-size limits during Unix linking.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/unixlink.mak -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/vdtrace.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/vdtrace.c

Implementation of Ghostscript’s debug-only visual tracing helper.

Key points:
- Defines global trace interface pointers `vd_trace0` and `vd_trace1`, plus a 128-byte `vd_flags` enable table.
- Maintains current scaled point position in private globals `px` and `py`.
- Scales incoming coordinates using interface origin, scale, and shift fields.
- Implements visual path calls: move, line, multi-line, cubic curve, bar, square, rectangle, quadrilateral, curve outline, circle, round marker, and text.
- If a backend lacks `curveto`, `vd_impl_curveto` flattens cubic Beziers into line segments in `DEBUG` builds.
- `vd_setflag` enables/disables trace categories by low 7 bits of a character.
- Most functions no-op immediately if `vd_trace1 == NULL`.

Dependencies and interactions:
- Includes `math_.h`, `gxfixed.h`, and `vdtrace.h`.
- Called through macros in `vdtrace.h` only when `VD_TRACE && DEBUG` is active.
- Backend behavior is supplied by `vd_trace_interface` function pointers.

Research relevance:
- Debug visualization hook for rendering/path internals. It is not part of normal release behavior but can affect debug diagnostics and visual stepping.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/vdtrace.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/vdtrace.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/vdtrace.h

Interface and macro layer for Ghostscript visual tracing.

Key points:
- Defines `vd_trace_interface`, a backend callback table with scale/origin/shift state and drawing operations.
- Declares global tracing pointers `vd_trace0`, `vd_trace1`, and flag table `vd_flags`.
- Declares implementation helpers from `vdtrace.c`.
- Defines `RGB(r,g,b)` if absent.
- When `VD_TRACE && DEBUG`, macros acquire/release a drawing context, query scale/size/origin, set scale/origin/shift, erase, build paths, draw primitives, fill/stroke, set color/line width, draw text, wait, save/restore, and disable tracing.
- When tracing is disabled or not a debug build, all drawing macros compile to no-ops and simple constants.
- The documented contract requires `vd_get_dc`, drawing calls, then `vd_release_dc`.

Dependencies and interactions:
- Requires Ghostscript macro conventions such as `BEGIN`, `END`, and `DO_NOTHING` from surrounding headers.
- Used by debug-capable modules, including Windows display/debug code.

Research relevance:
- Provides a zero-cost-in-release visual debugging abstraction over path and rendering behavior.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/vdtrace.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/version.mak -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/version.mak

Ghostscript version makefile fragment.

Key points:
- Defines `GS_VERSION_MAJOR=8`, `GS_VERSION_MINOR=53`, and `GS_VERSION_MINOR0=53`.
- Defines `GS_REVISIONDATE=20051020`.
- Derives `GS_VERSION=853`, `GS_DOT_VERSION=8.53`, and `GS_REVISION=$(GS_VERSION)`.
- Used by build and installation makefiles for versioned paths, library names, archive names, and installer text.

Dependencies and interactions:
- Included by nearly every platform makefile in this group.
- `unix-dll.mak`, install fragments, and Windows packaging rules depend on these values.

Research relevance:
- Establishes this bundled Ghostscript source as version 8.53 with revision date 2005-10-20.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/version.mak -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/vms_x_fix.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/vms_x_fix.h

VMS compatibility header that remaps X11/Motif/Xt/pthread/VMS routine names to uppercase linker symbols.

Key points:
- Guarded by `vms_x_fix_INCLUDED`.
- Intended to repair Xlib definitions when compiling on VMS with `/name=(as_is)`.
- Defines hundreds of macros mapping mixed/lowercase APIs to uppercase names, including:
  - Xlib and X extension functions (`XOpenDisplay`, `XDrawLine`, `XPutImage`, etc.).
  - Motif `Xm*` functions and widget classes.
  - Xt toolkit functions and widget classes.
  - X resource manager functions.
  - selected private `_Xm*` and `_Xt*` symbols.
  - VMS `lib$*` and `sys$*` routines.
  - pthread APIs to uppercase VMS symbols.
- Contains a duplicate `XrmStringToQuark` mapping.
- Declares `extern void XtFree(char*)` inside `extern "C"` guards.

Dependencies and interactions:
- Included by `x_.h` for VMS non-GNU compiler paths before DECWindows headers.
- Exists solely for VMS name-mangling/link compatibility.

Research relevance:
- Large portability shim for building Ghostscript’s X11 display driver on VMS. It has no runtime logic but heavily affects symbol resolution on that platform.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/vms_x_fix.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/vmsmath.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/vmsmath.h

Substitute `math.h` for GNU C on VAX/VMS.

Key points:
- Defines `HUGE_VAL` based on `CC$gfloat`.
- Declares classic double-returning math functions manually: trigonometric, hyperbolic, exponential/log, power, modulus, square root, rounding, absolute, complex absolute, and hypotenuse.
- Wrapped in `vmsmath_INCLUDED` and `__MATH` guards.

Dependencies and interactions:
- Used by VMS builds when the normal system math header is unavailable or unsuitable.
- Related to the broader Ghostscript portability headers such as `math_.h`.

Research relevance:
- Historical VAX/VMS compiler compatibility shim for math declarations.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/vmsmath.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/watclib.mak -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/watclib.mak

Watcom C/C++ makefile for MS-DOS library testing.

Key points:
- Default target builds `$(GLOBJ)gslib.exe`.
- Sets DOS-style Ghostscript root paths, runtime search path, and `GS=gslib`.
- Defaults `DEBUG`, `TDEBUG`, and `NOPRIVATE` to enabled unless overridden.
- Uses `debugobj` for generated/object/output directories by default.
- Configures bundled JPEG/libpng/zlib/JBIG2/ICC/IJS sources and `IJSEXECTYPE=win`.
- Chooses Watcom version, library paths, DOS extender stub, CPU/FPU type, and sync module.
- Includes `wccommon.mak`, `wctail.mak`, `devs.mak`, `contrib.mak`, and `winplat.mak`.
- Defines platform module `watclib_.dev` from Watcom/DOS/Win32 platform objects.
- Links `gslib.exe` with Watcom link scripts and selected library-only objects.

Dependencies and interactions:
- Uses Watcom make syntax and variables from `wccommon.mak`.
- Reuses Windows platform module rules when `WAT32` is enabled.

Research relevance:
- Legacy DOS/Watcom path for exercising Ghostscript as a graphics library rather than a standard interpreter.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/watclib.mak -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/watcw32.mak -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/watcw32.mak

Watcom C++ makefile for 32-bit Windows Ghostscript builds.

Key points:
- Builds Windows GUI executable `gswin32`, console executable `gswin32c`, and DLL `gsdll32` when `MAKEDLL=1`.
- Configures build/install roots, runtime search path, debug flags, executable names, third-party sources, Watcom compiler/resource/linker paths, CPU/FPU type, and `SYNC=winsync`.
- Enables PostScript/PDF/TrueType/EPSF features and a large set of display, printer, bitmap, TIFF, PNG, JPEG, PDF/PS/PXL devices.
- Sets Windows/Watcom compile flags, including `CHECK_INTERRUPTS`, `_Windows`, `__WIN32__`, and `_WATCOM_`.
- Builds auxiliary tools with Watcom compiler/linker.
- Uses Watcom `.BEFORE` to create output directories.
- Defines object groups for small DLL loaders, large non-DLL executables, console executables, and DLL builds.
- Links either two small EXEs plus a large DLL or two large EXEs based on `MAKEDLL`.

Dependencies and interactions:
- Includes `version.mak`, `winlib.mak`, and `winint.mak`.
- Relies on generated link lists and Windows resources from shared Windows make fragments.

Research relevance:
- Primary Watcom Win32 build recipe and an important source of platform-specific output topology.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/watcw32.mak -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/wccommon.mak -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/wccommon.mak

Common Watcom C/C++ makefile section for DOS and Windows builds.

Key points:
- Documents required parameters supplied by Watcom platform makefiles.
- Uses `.NOCHECK` and extends suffixes for Watcom make behavior.
- Disables shared third-party libraries: JPEG, libpng, zlib, and JBIG2 are built in.
- Defines DOS/Watcom command, object, executable, include, define, output, and path syntax.
- Provides batch-file wrappers for copy/remove commands.
- Selects Watcom compiler, linker, stub, and resource compiler based on `WCVERSION`, including hosted Win95/NT variants.
- Sets include directories and whether tools are 32-bit-hosted (`WAT32`).
- Normalizes FPU defaults based on CPU type.
- Defines assembler suffix rule and default `dosdefault`.
- Constructs debug/privacy/optimization flags and compiler command variables `CC`, `CCAUX`, `CC_`, `CC_D`, `CC_INT`, and `CC_NO_WARN`.

Dependencies and interactions:
- Included by `watclib.mak` and related Watcom makefiles.
- Feeds `wctail.mak` and generic Ghostscript fragments with platform syntax.

Research relevance:
- Core Watcom portability layer for old DOS/Windows Ghostscript builds.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/wccommon.mak -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/wctail.mak -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/wctail.mak

Tail fragment common to Watcom DOS/Windows makefiles.

Key points:
- Includes version, graphics library, JPEG, zlib, libpng, JBIG2, ICC, and IJS make fragments.
- Builds auxiliary programs `echogs`, `genarch`, `genconf`, `gendev`, and `geninit` with Watcom object/link rules and temporary link scripts.
- Uses Watcom DOS extender stubs and stack options for some auxiliary programs.
- Generates blank `gconfig_.h`.
- Generates `gconfigv.h` with `USE_ASM`, `USE_FPU`, `EXTEND_NAMES`, and `SYSTEM_CONSTANTS_ARE_WRITABLE`.

Dependencies and interactions:
- Depends on Watcom syntax and tool variables from `wccommon.mak`.
- Included before device/contrib/platform fragments in Watcom builds.

Research relevance:
- Completes the shared Watcom build pipeline by wiring generic libraries and build-time generators.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/wctail.mak -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/windows_.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/windows_.h

Ghostscript wrapper around `<windows.h>`.

Key points:
- Defines `STRICT` before including Windows headers.
- For Watcom, defines `LPRGBQUAD` and adapts `BEGIN_THREAD` to Watcom’s `_beginthread` signature with an extra stack-bottom argument.
- For non-Watcom, defines null equivalents of Watcom 32-to-16-bit glue macros such as `AllocAlias16`, `FreeAlias16`, `MK_FP16`, `MK_FP32`, `GetProc16`, and `ReleaseProc16`.
- For Win32, maps `_fstrtok` to `strtok`.
- For Borland C, maps `exception_code()` to `__exception_code`.

Dependencies and interactions:
- Included by Windows platform code and makefile dependency rules.
- Supports MSVC, Borland, and Watcom differences.

Research relevance:
- Small but central Windows portability wrapper for compiler and 16/32-bit compatibility differences.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/windows_.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/winint.mak -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/winint.mak

Common interpreter makefile section for 32-bit Microsoft Windows.

Key points:
- Includes generic interpreter and compiled-font makefiles.
- Defines Windows interpreter compile commands and resource compiler include handling.
- Defines default paths for WinZip self-extractor, zip tool, setup executable, and uninstall executable.
- Builds icon resources from `.icx` files using `echogs`.
- Builds short EXE and DLL resource files by generating temporary `.rc` files.
- Defines Windows object groups for DLL, non-DLL, console, and graphical builds.
- Compiles Windows frontend modules: `dwdll`, `dwnodll`, `dwmain`, `dwmainc`, `dwimg`, `dwtext`, `dwtrace` in debug builds, `dwreg`, setup, install, and uninstall modules.
- Provides `zip` and `archive` targets for AFPL Ghostscript Win32 distribution packaging with setup/uninstall programs and font packaging.

Dependencies and interactions:
- Designed to be acceptable to MSVC, Watcom, and Borland make dialects; only simple conditionals are allowed.
- Included by Windows top-level makefiles such as `watcw32.mak`.
- Relies on `winlib.mak`, `int.mak`, `cfonts.mak`, resource files, and generated Ghostscript version variables.

Research relevance:
- Defines the Windows interpreter frontend, resources, installer tooling, and distribution archive generation.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/winint.mak -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/winlib.mak -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/winlib.mak

Common graphics-library makefile section for 32-bit Windows.

Key points:
- Disables shared third-party libraries for Windows builds, including Jasper.
- Sets default platform `mswin32_`.
- Uses `ccf32.tr` as an auxiliary dependency/response file to avoid command-line length limits.
- Defines Windows command/object/executable syntax and batch wrappers for copy/remove.
- Supports conditional UFST and FreeType bridge flags when `UFST_ROOT` or `FT_ROOT` are set.
- Includes core graphics/device/contrib and bundled-library make fragments.
- Includes `winplat.mak` and `pcwin.mak`.
- Generates blank `gconfig_.h` and standard `gconfigv.h`.
- Defines `mswin32_.dev` from `gp_mswin`, `gp_wgetv`, and `gp_stdia`, including `nosync` and `winplat`.
- Defines separable Windows I/O feature devices: `mshandle.dev`, `msprinter.dev`, and `mspoll.dev`.

Dependencies and interactions:
- Included by Windows platform makefiles before interpreter-specific `winint.mak`.
- Provides platform abstraction modules used by Windows GUI/console/DLL builds.

Research relevance:
- Main Windows platform library layer for Ghostscript device and I/O integration.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/winlib.mak -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/winplat.mak -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/winplat.mak

Common 32-bit Windows platform module makefile fragment.

Key points:
- Defines generic Windows platform module `winplat.dev` from `gp_ntfs` and `gp_win32`.
- Compiles `gp_ntfs.c` and `gp_win32.c` with Windows include dependencies.
- Defines synchronization module `winsync.dev` from `gp_wsync`.
- `winsync.dev` replaces `nosync` in the generated module list.

Dependencies and interactions:
- Included by `winlib.mak` and `watclib.mak`.
- Supplies platform and synchronization modules to Windows and Watcom builds.

Research relevance:
- Minimal Windows OS abstraction and synchronization build wiring.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/winplat.mak -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/wmin.mak -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/wmin.mak

Makefile fragment for compiled Wadalab free Kanji font objects.

Key points:
- Sets `ccfonts_ps=gs_kanji gs_ccfnt`.
- Defines object and stem lists for `wmin` and many `wminrXX` generated C font chunks.
- Covers chunks from `wminr21` through `wminr74`, grouped across `ccfonts1` through `ccfonts7`.
- Comment notes it does not include rules for creating the `wmin*.c` files.

Dependencies and interactions:
- Used by compiled-font build paths through Ghostscript’s `cfonts.mak`-style machinery.
- Supplies object lists, not compile rules.

Research relevance:
- Historical compiled Japanese font packaging support in the Ghostscript build tree.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/wmin.mak -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/wrfont.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/wrfont.c

Shared font serialization output helper for the FAPI FreeType bridge.

Key points:
- Implements `WRF_init`, `WRF_wbyte`, `WRF_wtext`, `WRF_wstring`, `WRF_wfloat`, and `WRF_wint`.
- `WRF_output` writes into a caller buffer but always increments `m_count`, allowing callers to discover required size even when the buffer is too small.
- Supports optional Type 1 eexec-style byte encryption using key `55665`, factor `52845`, and offset `22719`.
- `WRF_wfloat` and `WRF_wint` format through `sprintf`.

Dependencies and interactions:
- Includes `wrfont.h` and `stdio_.h`.
- Used by `write_t1.c` and `write_t2.c` for serializing minimal font wrappers for FreeType.

Research relevance:
- Core buffered output and encryption utility for Ghostscript’s FAPI font serialization path.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/wrfont.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/wrfont.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/wrfont.h

Header for shared font serialization output helper.

Key points:
- Includes `stdpre.h`.
- Defines `WRF_output` with current buffer pointer, buffer limit, total byte count, encryption flag, and encryption key.
- Declares byte/text/string/float/integer writer functions and initializer.

Dependencies and interactions:
- Used by Type 1 and Type 2 serializer implementations.
- Depends on Ghostscript’s `bool` definition from `stdpre.h`.

Research relevance:
- Public local contract for the small font writer utility used by FAPI FreeType bridge code.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/wrfont.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/write_t1.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/write_t1.c

Serializer for a minimal Type 1 PostScript font wrapper for the FAPI FreeType bridge.

Key points:
- Public entry point is `FF_serialize_type1_font`.
- Writes `%!PS-AdobeFont-1`, a main dictionary, and an eexec-encrypted Private dictionary.
- Main dictionary writes `/FontType 1`, `/FontMatrix`, `StandardEncoding`, and `/FontBBox`.
- Private dictionary writes `/MinFeature`, `/password`, `/lenIV -1`, blue-zone fields, stem fields, force-bold data, and subrs.
- Pulls font feature values from `FAPI_font` callbacks: `get_word`, `get_long`, `get_float`, and `get_subr`.
- Converts some values from 16-scaled values back to font units.
- `write_subrs` writes subroutines through `RD ... NP` records and supports buffer-short sizing behavior.
- The comment explicitly notes the output is non-standard: no `/Charstrings` and no `/PaintType`; glyphs are supplied to FreeType through incremental interface mechanisms.

Dependencies and interactions:
- Includes `wrfont.h`, `write_t1.h`, and `<assert.h>`.
- Relies on FAPI feature IDs from `ifapi.h`.

Research relevance:
- Important bridge code for feeding existing Ghostscript Type 1 font metadata into FreeType without constructing a complete standard Type 1 font file.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/write_t1.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/write_t1.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/write_t1.h

Header for Type 1 font serialization through the FAPI FreeType bridge.

Key points:
- Includes `ifapi.h`.
- Declares `FF_serialize_type1_font(FAPI_font*, unsigned char*, long)`.
- Documents that the serializer emits PostScript code suitable for passing to FreeType via FAPI.

Dependencies and interactions:
- Implemented by `write_t1.c`.
- Used by FAPI FreeType integration code that needs to synthesize a Type 1 wrapper.

Research relevance:
- Small API boundary for Type 1 serialization in the Ghostscript font bridge.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/write_t1.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/write_t2.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/write_t2.c

Serializer for a minimal Type 2/CFF font wrapper for the FAPI FreeType bridge.

Key points:
- Public entry point is `FF_serialize_type2_font`.
- Writes a CFF header, dummy name index, top/font dictionary index, empty string index, subr index, charset, CharStrings index, and Private dictionary.
- Implements CFF integer and real-number encoders.
- Uses placeholder five-byte integer slots for charset, CharStrings, and Private dictionary offsets/lengths, then patches them when positions are known.
- Charset is intentionally minimal: currently one character, with `.notdef` assumptions.
- CharStrings index contains empty charstrings only to communicate glyph count to FreeType.
- Subr index serializes subroutines obtained from `FAPI_font->get_subr`.
- Private dictionary writes blue-zone, stem, force-bold, default width, and nominal width values.
- Reads `defaultWidthX` and `nominalWidthX` by casting `a_fapi_font->client_font_data` to `gs_font_type1*`.
- Like `wrfont`, returns total required byte count even if the caller buffer is too small.

Dependencies and interactions:
- Includes `wrfont.h`, `write_t2.h`, `ghost.h`, `gxfont.h`, `gxfont1.h`, and `<assert.h>`.
- Uses FAPI feature IDs and Ghostscript Type 1 font internals.

Research relevance:
- Minimal CFF wrapper generation for FreeType’s incremental font path. It is intentionally not a full CFF font serialization of all glyph data.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/write_t2.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/write_t2.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/write_t2.h

Header for Type 2/CFF font serialization through the FAPI FreeType bridge.

Key points:
- Includes `ifapi.h`.
- Declares `FF_serialize_type2_font(FAPI_font*, unsigned char*, long)`.
- Documents that the output can be passed to FreeType via FAPI.

Dependencies and interactions:
- Implemented by `write_t2.c`.
- Used by FreeType bridge code needing a CFF wrapper around Ghostscript font data.

Research relevance:
- Small API boundary for Type 2/CFF serialization in the Ghostscript font bridge.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/write_t2.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/x_.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/x_.h

Ghostscript wrapper for X11 headers used by the X display driver.

Key points:
- Undefines `private` before including X headers because some X implementations use it as a member name.
- Defines `have_Xdebug` except on VMS.
- For VMS GNU C, maps selected mixed-case X/Xt function names to lowercase forms to match GNU C name transformation behavior.
- For VMS non-GNU paths, includes `vms_x_fix.h`.
- Includes DECWindows headers on VMS and standard `<X11/...>` headers elsewhere.
- Supplies compatibility for older X11:
  - Defines `XtOffsetOf` via `offsetof` or `XtOffset`.
  - Sets `HaveStdCMap` based on `XtSpecificationRelease >= 4`.
  - Provides `XVisualIDFromVisual` fallback for X11R3.
  - Defines `XInitImage(im) 1` before X11R6.
- Restores Ghostscript’s `private` macro as `private_`.

Dependencies and interactions:
- Used by Ghostscript X11 display/device source.
- Interacts with `vms_x_fix.h` for VMS symbol handling.

Research relevance:
- Main X11 portability wrapper, bridging VMS, old X11 releases, and Ghostscript’s internal macro conventions.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/x_.h -->