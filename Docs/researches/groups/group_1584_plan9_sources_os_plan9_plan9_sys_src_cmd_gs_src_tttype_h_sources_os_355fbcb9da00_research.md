# Group Research: group_1584_plan9_sources_os_plan9_plan9_sys_src_cmd_gs_src_tttype_h_sources_os_355fbcb9da00

Scope: `Docs/research_subset_a.md`, specifically `sources/os/plan9/plan9` under the bundled Ghostscript source tree. I read all 34 listed files completely. The supplied internal group report path was not present in the workspace, so this report is based on the source files themselves.

This group covers Ghostscript 8.53 portability/build support plus font serialization helpers: FreeType-derived TrueType headers, Unix and Windows make fragments, X/VMS compatibility wrappers, visual tracing hooks, and FAPI FreeType bridge serialization for Type 1 and CFF/Type 2 fonts.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/tttype.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/tttype.h

FreeType-derived public TrueType high-level API header, modified in Ghostscript by removing the TrueType instruction interpreter.

Key points:
- Defines public `TT_` scalar types, fixed-point types, vectors, matrices, outlines, bounding boxes, glyph metrics, raster maps, and TrueType table structures.
- Exposes typed opaque handles for engine, stream, face, instance, glyph, and charmap objects via single-pointer structs to preserve type checking.
- Declares face management APIs: initialize/finalize engine, open faces/collections, query properties, read font/table data, flush/close faces.
- Declares instance APIs for resolutions, character sizes, pixel sizes, transform flags, metrics, generic user pointers, and cleanup.
- Declares glyph APIs for creating/loading glyphs, retrieving outlines/metrics, rendering bitmaps or pixmaps, and outline allocation/copy/render/transform helpers.
- Declares charmap/name-table enumeration and lookup APIs.
- Defines callback registration for glyph outline loading.
- Defines grouped error constants for API failures, missing tables, memory/file errors, glyph loader problems, bytecode interpreter errors, internal failures, and raster errors.

Dependencies and interactions:
- Included by `tttypes.h` and other TrueType support code.
- Depends on architecture macros such as `ARCH_LOG2_SIZEOF_LONG` and `ARCH_LOG2_SIZEOF_INT` for fixed-size type selection.
- API surface is FreeType 1-style and supports Ghostscript’s embedded TrueType/font handling path.

Research relevance:
- This is the main public contract for the bundled TrueType engine used by Ghostscript’s font subsystem.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/tttype.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/tttypes.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/tttypes.h

FreeType-derived internal common type header for the TrueType engine.

Key points:
- Includes `ttconfig.h` and `tttype.h`.
- Defines internal scalar aliases: `Byte`, `UShort`, `Short`, `ULong`, `Long`, `Fixed`, `Int`, `Integer`, pointer aliases, `Pointer`, `PCoordinates`, and `PTouchTable`.
- Defines `Bool`, `TRUE`, `FALSE`, and `NULL` fallbacks.
- Defines `PStorage` based on Plan 9, pointer size, and integer/long size; Plan 9 amd64 uses `unsigned long long *`, other Plan 9 builds use `unsigned int *`.
- Defines TrueType rounding constants and touch flag masks.
- Defines simple `SUCCESS`/`FAILURE` constants and `MIN`, `MAX`, `ABS` macros.
- Provides handle conversion macros from public `TT_*` handles to internal pointer types such as `PEngine_Instance`, `PFace`, `PInstance`, `PGlyph`, and `PCMapTable`.

Dependencies and interactions:
- Internal TrueType implementation code uses this to bridge public typed handles to internal engine structs.
- The Plan 9-specific `PStorage` branch is the local portability change most relevant to this source tree.

Research relevance:
- Establishes internal portability assumptions for the bundled TrueType engine, including pointer-sized storage handling.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/tttypes.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/turboc.cfg -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/turboc.cfg

Tiny Turbo C compiler configuration file.

Key points:
- Contains warning-control switches such as `-wdup`, `-wret`, `-wstr`, `-waus`, `-wdef`, and others.
- Ends with `-N`.
- No logic or dependencies; it is a compiler option file.

Research relevance:
- Historical build-portability artifact for old DOS/Turbo C builds.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/turboc.cfg -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/ugcclib.mak -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/ugcclib.mak

Unix/gcc makefile for Ghostscript graphics library testing.

Key points:
- Builds in `./libobj`, names output `gslib`, and uses `version.mak`.
- Configures Ghostscript library/resource/font search paths under `/usr/local/share/ghostscript`.
- Uses gcc with warnings and debug flags by default; links against `-lm` plus optional X11 libraries.
- Chooses mostly library features such as DPS, PostScript level libraries, CIE, path, pattern, halftone, raster-op, and CMap support.
- Defines device list centered on X11, basic PNM/PBM/PGM/PPM devices, `djet500`, `bitcmyk`, and `bbox`.
- Includes common make fragments for core library, JPEG, zlib, libpng, JBIG2, icclib, ijs, devices, contrib, and Unix auxiliary rules.
- Replaces `unixlink.mak` with custom link/archive rules for `$(GS_XE)` and `libgsgraph.a`.

Dependencies and interactions:
- Depends on many shared make fragments and generated trace files from `echogs`.
- Uses `unix-aux.mak` and `unix-end.mak` but not the standard interpreter link path.

Research relevance:
- Specialized Unix gcc build target for library-oriented Ghostscript testing rather than the normal interpreter executable.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/ugcclib.mak -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/unistd_.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/unistd_.h

Portable wrapper/substitute for Unix `unistd.h`.

Key points:
- Includes `std.h` before system headers.
- Includes `<io.h>` for OS/2 and Win32.
- For Microsoft C, maps POSIX-like names to underscore-prefixed CRT calls: `fsync`, `read`, `isatty`, `setmode`, `fstat`, `dup`, `open`, and `close`.
- For Borland C on Win32, maps `fsync`, `read`, `isatty`, and `setmode`.
- Falls back to including system `<unistd.h>` otherwise.

Dependencies and interactions:
- Used by platform I/O code such as `gp_stdia.c` and Windows console make rules.
- Works with Ghostscript’s wrapper-header convention using `_` suffix names.

Research relevance:
- Small but central portability adapter for low-level file descriptor APIs across Unix and Windows compilers.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/unistd_.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/unix-aux.mak -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/unix-aux.mak

Common Unix partial makefile for platform modules and auxiliary build tools.

Key points:
- Defines `UNIX_AUX_MAK`.
- Builds `unix_.dev` from Unix platform objects including `gp_getnv`, `gp_unix`, `gp_unifs`, `gp_unifn`, `gp_stdia`, and `gp_unix_cache`, including `nosync`.
- Builds `sysv_.dev` for older System V platforms using `gp_sysv`.
- Defines compilation rules for Unix platform objects and build tools: `echogs`, `genarch`, `genconf`, `gendev`, `genht`, and `geninit`.
- Generates `gconfig_.h` by probing `/usr/include` for directory/time headers and checking for `jmemsys.h`.

Dependencies and interactions:
- Included by Unix top-level makefiles before linking.
- Produces generated config headers consumed by wrapper headers and platform modules.

Research relevance:
- Encodes Unix platform abstraction and configure-lite behavior for non-autoconf builds.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/unix-aux.mak -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/unix-dll.mak -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/unix-dll.mak

Unix shared object build fragment.

Key points:
- Defines `so`, `sodebug`, `install-so`, `soinstall`, `SODIRS`, and `soclean` targets.
- Builds shared library names `lib$(GS).so`, major symlink, and major/minor versioned library.
- Builds small loader executables: console `$(GS)c` and Gtk/display-capable `$(GS)x`.
- Uses recursive make with `SODEFS` to redirect object/bin dirs to `../soobj` and `../sobin`, enable `-shared`, set soname, and force `STDIO_IMPLEMENTATION=c`.
- Installs shared library and loader symlinks under `$(libdir)` and `$(bindir)`.

Dependencies and interactions:
- Included by `unix-gcc.mak`.
- Relies on `GS_VERSION_MAJOR` and `GS_VERSION_MINOR` from `version.mak`.

Research relevance:
- Documents Ghostscript’s legacy Unix shared-library packaging and loader architecture.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/unix-dll.mak -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/unix-end.mak -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/unix-end.mak

Common near-final Unix makefile fragment for build directories, debug/profile targets, generated variant config, and tags.

Key points:
- Defines `STDDIRS`, `PGDIRS`, and `DEBUGDIRS` to create bin/generated/object directories.
- Defines recursive `pg`, `pgclean`, `debug`, and `debugclean` targets with adjusted flags and output directories.
- Generates `gconfigv.h` with `USE_ASM`, `USE_FPU`, `EXTEND_NAMES`, and `SYSTEM_CONSTANTS_ARE_WRITABLE`.
- Adds `TAGS` target using `etags`.

Dependencies and interactions:
- Included late by Unix and Desqview/X configurations.
- Depends on `ECHOGS_XE`, `TOP_MAKEFILES`, and variables set by platform makefiles.

Research relevance:
- Centralizes variant build directory handling and generated compile-time capability constants.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/unix-end.mak -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/unix-gcc.mak -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/unix-gcc.mak

Primary Unix/gcc/X11 Ghostscript makefile.

Key points:
- Sets build directories, install paths, runtime resource paths, `GS=gs`, and `BUILD_TIME_GS=gs`.
- Enables `CAPOPT=-DHAVE_MKSTEMP`.
- Configures bundled third-party libraries: JPEG 6, libpng 1.2.8, zlib, jbig2dec, icclib, and ijs.
- Uses gcc with strict warnings, `-fno-builtin`, `-fno-common`, standard/debug/profile/SO flags, and `GX_COLOR_INDEX_TYPE='unsigned long long'`.
- Defaults to `SYNC=nosync` and `STDLIBS=-lm`.
- Configures X11 include/lib paths under `/usr/X11R6`.
- Enables language features including PostScript Level 3, PDF, DPS Next, TrueType fonts, EPSF, pipe, and FAPI.
- Defines extensive device sets: X11 devices, BMP, Epson/HP/Canon printer drivers, fax, PCX, PBM/PNM/PPM, TIFF, PNG, JPEG, PDF/PS/PXL writers, `bbox`, spot/devicen/XCF, and others.
- Includes Unix core fragments plus `unixlink.mak`, `unix-dll.mak`, `unix-end.mak`, and `unixinst.mak`.
- Generates `cc.tr` to work around gcc 2.7 const optimizer behavior.

Dependencies and interactions:
- Main top-level makefile for Unix gcc manual builds.
- Pulls in interpreter, library, device, contrib, install, and shared-library rules.

Research relevance:
- Canonical legacy Unix gcc build configuration for the Ghostscript tree in this Plan 9 source import.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/unix-gcc.mak -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/unixansi.mak -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/unixansi.mak

Unix/ANSI C/X11 Ghostscript makefile for non-gcc ANSI compilers.

Key points:
- Mirrors `unix-gcc.mak` structure but leaves `CC` unset for a platform ANSI compiler.
- Uses simpler flags: `CFLAGS_STANDARD=-O`, `CFLAGS_DEBUG=-g`, `CFLAGS_PROFILE=-pg -O`.
- Configures install paths, runtime resource paths, JPEG/libpng/zlib/JBIG2/icclib/ijs sources, X11 settings, `SYNC=nosync`, and `STDLIBS=-lm`.
- Enables the same major language features as Unix gcc: PostScript Level 3, PDF, DPS Next, TrueType fonts, EPSF, pipe, and FAPI.
- Defines a somewhat smaller/default device list than `unix-gcc.mak`, with overflow device variables for PNM-style devices.
- Includes the same core Unix/interpreter/library/device/install make fragments except gcc-specific `cc.tr`.

Dependencies and interactions:
- Intended for hand-edited platform builds where gcc is not the compiler.
- Notes that callers should define a 64-bit `GX_COLOR_INDEX_TYPE` if available.

Research relevance:
- Shows the non-gcc Unix portability path and the minimum compiler assumptions Ghostscript expected.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/unixansi.mak -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/unixhead.mak -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/unixhead.mak

Common Unix makefile header fragment.

Key points:
- Sets `PLATFORM=unix_`.
- Defines command/object/executable syntax variables for Unix builds: `C_`, `D_`, `I_`, `O_`, `OBJ=o`, empty `XE`, `/` path separator, `/bin/sh`, `cat`, `cp`, and `rm -f`.
- Defines `CONFILES` and `CONFLDTR` arguments for `genconf`.
- Defines `CC_D`, `CC_INT`, and empty `BEGINFILES`.
- Clears PC-specific assembly placeholders such as `PCFBASM`.
- Defines `std: STDDIRS default`.

Dependencies and interactions:
- Included after compiler-specific options and before core Ghostscript makefiles.
- Provides variable conventions consumed throughout all Unix make fragments.

Research relevance:
- Establishes the Unix make variable ABI for the rest of the Ghostscript build system.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/unixhead.mak -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/unixinst.mak -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/unixinst.mak

Final Unix install-target makefile fragment.

Key points:
- Defines aggregate `install: install-exec install-scripts install-data`.
- `install-exec` installs the Ghostscript executable.
- `install-scripts` installs many helper scripts, rewriting `GS_EXECUTABLE=...` to match `$(GS)`.
- `install-data` delegates to library data, resource data, docs, man pages, and examples.
- `install-libdata` installs Fontmap files, PostScript utility files, `gs_*.ps`, `pdf*.ps`, PPD/RPD/UPP/XBM/XPM files.
- `install-resdata` copies Resource subdirectories except CVS.
- `install-doc` installs a fixed HTML/documentation page list.
- `install-man` installs localized man pages and creates symlinks for related tools.
- `install-examples` installs example PostScript/PDF/EPS files.

Dependencies and interactions:
- Depends on directory variables from the top-level Unix makefiles.
- Uses `instcopy` through `INSTALL_PROGRAM` and `INSTALL_DATA`.

Research relevance:
- Captures Ghostscript’s runtime layout: executable, scripts, lib/resource data, docs, man pages, examples.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/unixinst.mak -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/unixlink.mak -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/unixlink.mak

Common Unix interpreter link fragment.

Key points:
- Defines `UNIXLINK_MAK`.
- Uses `.NOEXPORT` to avoid huge environment-expanded command lines on limited System V systems.
- Defines interpreter archive objects and final executable object list.
- Provides `$(GS).a` archive target for the complete interpreter, though not used by standard builds.
- Defines final `$(GS_XE)` link step by writing a shell script/trailer with `echogs`, concatenating `ld.tr`, and appending extra and standard libraries.
- Sets `LD_RUN_PATH` when `XLIBDIR` is present.
- Clears large make variables in the environment during final shell execution to work around SCO Unix limits.

Dependencies and interactions:
- Consumes object/link traces produced by earlier make fragments.
- Included by Unix top-level makefiles after device and interpreter object lists are known.

Research relevance:
- Shows how Ghostscript avoided command-line length and environment limitations in legacy Unix final linking.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/unixlink.mak -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/vdtrace.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/vdtrace.c

Implementation of Ghostscript’s visual tracer service.

Key points:
- Defines global trace interfaces `vd_trace0`, `vd_trace1`, and `vd_flags[128]`.
- Maintains current scaled point state in private `px`, `py`.
- Provides scale helpers from source coordinates to trace display coordinates using origin, scale, and shift fields.
- Implements drawing wrappers: move, line, multi-line, curve, bar, square, rectangle, quadrilateral, curve stroke, circle, round marker, and text.
- If the trace interface lacks a `curveto` callback, DEBUG builds flatten Beziers into line segments using a second-derivative estimate and `hypot`, `ceil`, `sqrt`.
- `vd_setflag` toggles per-character tracing flags.

Dependencies and interactions:
- Includes `math_.h`, `gxfixed.h`, and `vdtrace.h`.
- Called only through macros in `vdtrace.h`; most calls are compiled out outside DEBUG/VD_TRACE.

Research relevance:
- Diagnostic-only visualization hook for graphics/path debugging; no normal rendering semantics should depend on it.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/vdtrace.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/vdtrace.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/vdtrace.h

Public interface and macros for visual tracing.

Key points:
- Defines `vd_trace_interface` callback table with size queries, DC acquire/release, erase, path construction, drawing primitives, fill/stroke, color/line width, text, wait, and transform update callbacks.
- Declares `vd_trace0`, `vd_trace1`, `vd_flags`, and implementation functions from `vdtrace.c`.
- Defines `RGB(r,g,b)` fallback.
- When `VD_TRACE && DEBUG`, macros conditionally acquire a trace context based on `vd_flags`, emit scaled drawing primitives, query size/scale/origin, and save/restore/disable tracing.
- When not tracing or not DEBUG, all tracing macros become `DO_NOTHING`/constants.
- Comments define the painting contract: acquire with `vd_get_dc`, draw, release with `vd_release_dc`; some primitives paint immediately while path primitives may require fill/stroke.

Dependencies and interactions:
- Requires Ghostscript macros such as `BEGIN`, `END`, `DO_NOTHING`, and `false` from surrounding headers.
- Used by graphics debugging code and optionally by Windows tracing integration.

Research relevance:
- Important for understanding debug-only instrumentation boundaries and why trace calls should be side-effect free in release builds.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/vdtrace.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/version.mak -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/version.mak

Ghostscript version make fragment.

Key points:
- Defines Ghostscript version 8.53.
- Sets `GS_VERSION_MAJOR=8`, `GS_VERSION_MINOR=53`, `GS_VERSION_MINOR0=53`.
- Sets revision date `GS_REVISIONDATE=20051020`.
- Derives `GS_VERSION=853`, `GS_DOT_VERSION=8.53`, and `GS_REVISION=$(GS_VERSION)`.

Dependencies and interactions:
- Included by many makefiles to set install directories, sonames, archive names, packaging names, and documentation text.

Research relevance:
- Anchors this source import to Ghostscript 8.53-era build and runtime paths.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/version.mak -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/vms_x_fix.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/vms_x_fix.h

VMS compatibility header that remaps mixed-case X/Motif/Xt/pthread/system symbols to uppercase external names.

Key points:
- Intended to repair Xlib definitions when compiling on VMS with `/name=(as_is)`.
- Contains a large table of `#define` aliases for Xlib, Motif `Xm*`, Xt, Xrm, Xmu, pthread, `lib$*`, and `sys$*` names.
- Includes widget class object aliases such as `topLevelShellWidgetClass`, `xmTextWidgetClass`, and many Motif class records.
- Declares `extern void XtFree(char*)` with C++ linkage protection at the end.
- Does not implement behavior; it only changes symbol spelling before headers/linkage.

Dependencies and interactions:
- Included from `x_.h` for non-GNU VMS builds.
- Addresses VMS linker/case behavior for external symbols in X-related drivers.

Research relevance:
- Large portability shim for historical VMS X11/Motif support.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/vms_x_fix.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/vmsmath.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/vmsmath.h

Substitute `math.h` for GNU C on VAX/VMS.

Key points:
- Defines `HUGE_VAL` differently based on `CC$gfloat`.
- Declares classic K&R-style prototypes for common math functions: trig, hyperbolic, exp/log, pow, `modf`, `fmod`, `sqrt`, `ceil`, `floor`, `fabs`, `cabs`, and `hypot`.
- Guarded by `vmsmath_INCLUDED` and `__MATH`.

Dependencies and interactions:
- Used where VAX/VMS GNU C lacks a usable system `math.h`.

Research relevance:
- Minimal historical portability wrapper for old VMS compiler environments.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/vmsmath.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/watclib.mak -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/watclib.mak

Watcom C/C++ makefile for MS-DOS library testing.

Key points:
- Default target builds `$(GLOBJ)gslib.exe`.
- Defaults to debug-oriented settings: `DEBUG=1`, `TDEBUG=1`, `NOPRIVATE=1`.
- Uses `GS=gslib`, output directories under `.\debugobj`, and runtime paths under `c:/gs/gs$(GS_DOT_VERSION)`.
- Configures JPEG/libpng/zlib/JBIG2/icclib/ijs source roots.
- Selects Watcom version/toolchain, CPU/FPU type, library paths, DOS extender stub, and default sync.
- Includes `wccommon.mak`, `wctail.mak`, device/contrib makefiles, and `winplat.mak`.
- Builds `watclib_.dev` from `gp_getnv`, `gp_iwatc`, and either DOS filesystem/platform objects or Windows platform include depending on `WAT32`.
- Defines link-response generation and final `gslib.exe` link using `wlink`.

Dependencies and interactions:
- Shares Watcom common rules with other DOS/Windows Watcom builds.
- Uses `winplat.dev` when building with 32-bit Watcom tools.

Research relevance:
- Historical Watcom DOS library-test build path.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/watclib.mak -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/watcw32.mak -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/watcw32.mak

Watcom C++ makefile for 32-bit Windows Ghostscript.

Key points:
- Builds Windows GUI `gswin32`, console `gswin32c`, and DLL `gsdll32` by default with `MAKEDLL=1`.
- Sets install/runtime roots under `c:/gs/gs$(GS_DOT_VERSION)`.
- Configures Watcom tool paths from `%WATCOM%`, CPU/FPU flags, Windows resource compiler, linker, and `SYNC=winsync`.
- Defines language features: PostScript Level 3, PDF, DPS Next, TrueType fonts, and EPSF.
- Defines Windows/default devices plus printer, bitmap, fax, PCX, PBM/PNM/PPM, TIFF, PNG, JPEG, PDF/PS/PXL writer, and other device groups.
- Includes `version.mak`, `winlib.mak`, and `winint.mak`.
- Generates `ccf32.tr` compiler response file with Windows and Watcom defines.
- Builds auxiliary tools, creates directories via Watcom `.BEFORE`, compiles `gp_mktmp`, and links either small EXE loaders plus big DLL or large standalone EXEs.

Dependencies and interactions:
- Uses common Windows interpreter/resource rules from `winint.mak`.
- Uses platform and library modules from `winlib.mak`/`winplat.mak`.

Research relevance:
- Full legacy 32-bit Windows Watcom build configuration, including DLL-vs-standalone linking structure.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/watcw32.mak -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/wccommon.mak -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/wccommon.mak

Common Watcom C/C++ makefile section for MS-DOS and Windows.

Key points:
- Used by Watcom DOS/Windows makefiles and documents required input variables.
- Enables `.NOCHECK` and adds extensions to satisfy Watcom make.
- Forces built-in third-party libraries: `SHARE_JPEG=0`, `SHARE_LIBPNG=0`, `SHARE_ZLIB=0`, `SHARE_JBIG2=0`.
- Defines DOS/Watcom command syntax, path separator, object/executable extensions, batch-file copy/remove commands, and `genconf` argument forms.
- Selects Watcom compiler/linker/resource tools based on `WCVERSION`, including 9.5, 10.0, 10.5, 11.0, and 10.695 hosted tools.
- Sets include directories, binder, CPU/FPU-derived flags, assembly/object rules, and default target.
- Computes debug/privacy flags and final compiler command macros: `CC`, `CCAUX`, `CC_`, `CC_D`, `CC_INT`, and `CC_NO_WARN`.

Dependencies and interactions:
- Included before `wctail.mak` and platform-specific make logic.
- Centralizes Watcom command-line spelling and tool selection.

Research relevance:
- Encapsulates the Watcom build system portability layer.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/wccommon.mak -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/wctail.mak -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/wctail.mak

Tail fragment common to Watcom makefiles.

Key points:
- Includes `version.mak`, core `gs.mak`, `lib.mak`, JPEG, zlib, libpng, JBIG2, icclib, and ijs make fragments.
- Defines auxiliary tool build/link rules for `echogs`, `genarch`, `genconf`, `gendev`, and `geninit`.
- Uses temporary response file `_temp_.tr` for Watcom linker options, stubs, stacks, and library paths.
- Generates blank `gconfig_.h`.
- Generates `gconfigv.h` with `USE_ASM`, `USE_FPU`, `EXTEND_NAMES`, and `SYSTEM_CONSTANTS_ARE_WRITABLE`.

Dependencies and interactions:
- Complements `wccommon.mak`.
- Used before DOS/Watcom-specific device and platform rules.

Research relevance:
- Provides common generated-tool and generated-config behavior for Watcom builds.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/wctail.mak -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/windows_.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/windows_.h

Ghostscript wrapper for `windows.h`.

Key points:
- Defines `STRICT` before including `<windows.h>`.
- For Watcom, defines `LPRGBQUAD` and adapts `BEGIN_THREAD` to Watcom’s `_beginthread(proc, NULL, stksize, data)` signature.
- For non-Watcom builds, defines `BEGIN_THREAD` with the usual `_beginthread(proc, stksize, data)` signature.
- Provides null Win32 equivalents for Watcom 32-to-16-bit glue helpers such as `AllocAlias16`, `FreeAlias16`, `MK_FP16`, `MK_FP32`, `GetProc16`, and `ReleaseProc16`.
- Under Win32, maps `_fstrtok` to `strtok`.
- For Borland C, maps `exception_code()` to `__exception_code`.

Dependencies and interactions:
- Included by Windows platform and interpreter code.
- Abstracts compiler-specific Windows API and threading differences.

Research relevance:
- Small portability wrapper for Windows compiler/runtime quirks.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/windows_.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/winint.mak -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/winint.mak

Common interpreter makefile section for 32-bit Windows.

Key points:
- Includes `int.mak` and `cfonts.mak`.
- Defines Windows interpreter compile macros and `GLCPP`.
- Sets paths for WinZip self-extractor, zip tool, setup, and uninstall executables.
- Builds icon resources from `.icx` text form using `echogs`.
- Builds resource files for small EXE loader and DLL/main program.
- Defines object sets for big EXE, console EXE, small EXE loader, and DLL modes.
- Compiles Windows interpreter modules such as `dwnodll`, `gsdll`, `gp_msdll`, `dwmainc`, `dwdllc`, `dwnodllc`, `dwdll`, `dwimg`, `dwtrace`, `dwmain`, `dwtext`, and `dwreg`.
- Compiles setup and uninstall program modules/resources.
- Defines `zip` and `archive` targets for Win32 distribution packaging, including self-extracting archive text generated through `echogs`.

Dependencies and interactions:
- Must be acceptable to MSVC, Watcom, and Borland make dialects, so conditionals are limited.
- Used by Windows compiler-specific top-level makefiles.

Research relevance:
- Central Windows interpreter/resource/package build layer.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/winint.mak -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/winlib.mak -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/winlib.mak

Common 32-bit Windows library makefile section.

Key points:
- Forces bundled/non-shared third-party libraries for JPEG, libpng, zlib, JBIG2, and Jasper.
- Defaults `PLATFORM=mswin32_`.
- Defines `AK=$(GLGENDIR)\ccf32.tr` to avoid command-line length limits.
- Defines Windows command syntax and batch-file copy/remove helpers.
- Sets optional bridge flags for UFST and FreeType if corresponding roots are set.
- Includes core library/device/contrib make fragments and Windows platform fragments.
- Generates blank `gconfig_.h` and `gconfigv.h`.
- Builds `mswin32_.dev` from `gp_mswin`, `gp_wgetv`, `gp_stdia`, and includes `nosync` plus `winplat`.
- Defines separable Windows I/O features: `mshandle.dev`, `msprinter.dev`, and `mspoll.dev`.

Dependencies and interactions:
- Used by Windows compiler-specific makefiles before `winint.mak`.
- Coordinates graphics-library platform objects and Windows-specific IO devices.

Research relevance:
- Defines the Windows platform module set and Windows-specific Ghostscript IO devices.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/winlib.mak -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/winplat.mak -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/winplat.mak

Common Windows platform make fragment used by 32-bit Windows and Watcom MS-DOS builds.

Key points:
- Defines `winplat.dev` from `gp_ntfs` and `gp_win32`.
- Compiles `gp_ntfs.c` with DOS/memory/stdio/string/windows and Ghostscript utility headers.
- Compiles `gp_win32.c` with DOS/malloc/stdio/string/windows and Ghostscript platform/memory headers.
- Defines `winsync.dev` from `gp_wsync`, replacing `nosync`.
- Compiles `gp_wsync.c` with Windows and Ghostscript platform/memory headers.

Dependencies and interactions:
- Included by `winlib.mak` and `watclib.mak`.
- Supplies common filesystem/path and synchronization platform modules.

Research relevance:
- The most filesystem-adjacent file in this group: it wires Windows NTFS/path support and Win32 platform/synchronization objects into Ghostscript modules.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/winplat.mak -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/wmin.mak -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/wmin.mak

Makefile fragment for compiling Wadalab free Kanji font chunks into the executable.

Key points:
- Defines `ccfonts_ps=gs_kanji gs_ccfnt`.
- Groups many generated `wmin*.obj` files into `ccfonts1_` through `ccfonts7_`.
- Corresponding source/base names are listed in `ccfonts1` through `ccfonts7`.
- Comments state it does not include rules for creating the `wmin*.c` files.

Dependencies and interactions:
- Used by compiled-font support.
- Relates to Ghostscript initialization/font resources rather than platform code.

Research relevance:
- Historical compiled-in Japanese font resource list.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/wmin.mak -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/wrfont.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/wrfont.c

Support routines for serializing fonts as PostScript-like byte streams for the FAPI FreeType bridge.

Key points:
- Implements `WRF_init`, `WRF_wbyte`, `WRF_wtext`, `WRF_wstring`, `WRF_wfloat`, and `WRF_wint`.
- Maintains output pointer, byte limit, total byte count, optional encryption flag, and encryption key.
- `WRF_wbyte` writes only if within buffer limit but always increments total count, allowing callers to compute required size even with a short buffer.
- When encryption is enabled, applies Type 1 eexec-style encryption using key `55665`, factor `52845`, and offset `22719`.
- Formats floats and integers with `sprintf`.

Dependencies and interactions:
- Used by `write_t1.c` and `write_t2.c`.
- Struct and prototypes are in `wrfont.h`.

Research relevance:
- Shared bounded-output and encryption primitive for FAPI font serialization.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/wrfont.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/wrfont.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/wrfont.h

Header for font serialization output helpers.

Key points:
- Includes `stdpre.h`.
- Defines `WRF_output` with current output pointer, buffer limit, total count, encryption flag, and eexec key.
- Declares byte/text/string/float/int writer functions.
- Comments explain the output is intended to be passed to FreeType through the FAPI FreeType bridge.

Dependencies and interactions:
- Consumed by Type 1 and Type 2 serialization implementations.

Research relevance:
- Defines the small output abstraction used by FAPI font serializers.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/wrfont.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/write_t1.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/write_t1.c

Serializes a Type 1 font as textual PostScript for FreeType via the FAPI FreeType bridge.

Key points:
- Public function is `FF_serialize_type1_font`.
- Writes a `%!PS-AdobeFont-1` leading comment, a small main dictionary, and an encrypted Private dictionary.
- Main dictionary writes `/FontType 1`, `/FontMatrix`, `/Encoding StandardEncoding`, `/FontBBox`, then enters `eexec`.
- Private dictionary enables `WRF_output` encryption, writes four dummy bytes, then writes Type 1 private entries such as `MinFeature`, `password`, `lenIV -1`, `BlueFuzz`, `BlueScale`, `BlueShift`, blues arrays, `ForceBold`, `StdHW`, `StdVW`, `StemSnapH`, `StemSnapV`, and `/Subrs`.
- Reads font features through `FAPI_font` callbacks: `get_word`, `get_long`, `get_float`, and `get_subr`.
- Converts fixed or scaled values back to font units using divisors, commonly `16`.
- Handles short buffers by relying on `WRF_output` total-count semantics.

Dependencies and interactions:
- Includes `wrfont.h`, `write_t1.h`, and `<assert.h>`.
- Comments note the PostScript is non-standard because `/CharStrings` and `/PaintType` are omitted; FreeType gets glyph data through its incremental interface.

Research relevance:
- Key bridge between Ghostscript FAPI font data and FreeType Type 1 ingestion.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/write_t1.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/write_t1.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/write_t1.h

Header for Type 1 font serialization.

Key points:
- Includes `ifapi.h`.
- Declares `long FF_serialize_type1_font(FAPI_font*, unsigned char*, long)`.
- The function writes serialized Type 1 font data into a caller buffer and returns the full required length.

Dependencies and interactions:
- Implemented by `write_t1.c`.
- Used by the FAPI FreeType bridge.

Research relevance:
- Public FAPI bridge entry point for Type 1 serialization.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/write_t1.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/write_t2.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/write_t2.c

Serializes a Type 2/CFF font in binary format for FreeType via the FAPI FreeType bridge.

Key points:
- Public function is `FF_serialize_type2_font`.
- Writes CFF header, dummy name index, top/font dictionary index, empty string index, subrs index, charset, charstrings index, and private dictionary.
- Encodes Type 2 integers using compact CFF number forms and writes larger values with 4-byte big-endian encoding.
- Encodes Type 2 real numbers from `sprintf("%f")` into CFF nibble format.
- Top dictionary writes FontBBox, FontMatrix, Standard Encoding, placeholders for charset and CharStrings offsets, and placeholder size/offset for Private dictionary.
- Charset is minimal and currently reports one character, enough for FreeType incremental use.
- CharStrings index contains empty charstrings and exists mainly to communicate glyph count.
- Subrs index writes offsets and subroutine data from `FAPI_font->get_subr`.
- Private dictionary writes hinting/private features including blue zones, stem data, force-bold, default width, and nominal width.
- Extracts default/nominal widths directly from `gs_font_type1` via `a_fapi_font->client_font_data`.

Dependencies and interactions:
- Includes `wrfont.h`, `write_t2.h`, `ghost.h`, `gxfont.h`, and `gxfont1.h`.
- Relies on FAPI callbacks for font features and subroutines.
- Uses `fixed2float` for Type 1 font width fields.

Research relevance:
- Key bridge for converting Ghostscript/FAPI Type 1-like data to minimal CFF/Type 2 data that FreeType can consume incrementally.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/write_t2.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/write_t2.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/write_t2.h

Header for Type 2/CFF font serialization.

Key points:
- Includes `ifapi.h`.
- Declares `long FF_serialize_type2_font(FAPI_font*, unsigned char*, long)`.
- The function writes binary Type 2/CFF font data and returns total required length.

Dependencies and interactions:
- Implemented by `write_t2.c`.
- Used by the FAPI FreeType bridge.

Research relevance:
- Public FAPI bridge entry point for Type 2/CFF serialization.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/write_t2.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/x_.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/x_.h

Wrapper for including X11 headers in Ghostscript’s X11 driver.

Key points:
- Temporarily undefines Ghostscript’s `private` macro because some X headers use `private` as a member name, then restores it as `private_`.
- Defines `have_Xdebug` for non-VMS builds.
- For VMS GNU C, maps the subset of X/Xt names used by Ghostscript to lowercase names to avoid GNU C’s mixed-case external name transformation.
- For non-GNU VMS, includes `vms_x_fix.h`.
- Includes DECWindows headers on VMS and standard `<X11/...>` headers elsewhere.
- Provides fallback for old X11R3 lacking `XtOffsetOf`.
- Defines `HaveStdCMap` based on `XtSpecificationRelease >= 4`; for older X11, supplies `XVisualIDFromVisual`.
- Defines no-op successful `XInitImage` for pre-X11R6.

Dependencies and interactions:
- Used by Ghostscript X11 device code.
- Works with `vms_x_fix.h` for VMS portability.

Research relevance:
- Central X11 compatibility wrapper across Unix, VMS, and old X11 releases.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/x_.h -->