# Group Research: group_1579_plan9_sources_os_plan9_plan9_sys_src_cmd_gs_src_lib_mak_sources_os__2669c5a0136f

This group covers Ghostscript build-system, portability, hashing, ROM-resource, and interpreter-operator support files under the Plan 9 source tree. These are imported Ghostscript sources rather than native Plan 9 filesystem implementation files. The filesystem-adjacent material is mainly Ghostscript file stream wiring, command-list storage selection, platform file-system modules, and `%rom%` archive generation.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/lib.mak -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/lib.mak

`lib.mak` is the platform-independent Ghostscript graphics-library makefile. Including platform makefiles must define `GLSRCDIR`, `GLGENDIR`, and `GLOBJDIR`; this file derives source, generated, object, compiler, include, and feature-module macros from them.

It first declares a large dependency graph for generated headers, platform interfaces, C-library wrapper headers, Ghostscript memory/GC types, streams, graphics-state internals, devices, fonts, filters, color spaces, command-list rendering, third-party library bridges, and platform abstraction headers. The dependency list is deliberately ordered bottom-to-top for older `make` implementations that expand macros too early.

The executable-rule body builds most of the Ghostscript graphics library: memory managers, bitmap support, synchronization stubs, platform utilities, MD5 support, graphics state, paths, fills, strokes, images, color conversion, halftones, font caches, memory/page/vector devices, stream filters, command-list rendering, Type 1/2/42/CID font support, CIE/ICC/separation color, Display PostScript support, transparency, shading, RasterOp, async page rendering, UFST bridge hooks, and platform `gp_*` implementations.

The `.dev` module targets are central integration points. `libs.dev`, `libx.dev`, `libd.dev`, and `libcore.dev` compose the core graphics library; many optional features use `SETMOD`, `ADDMOD`, `ADDCOMP`, and `-include` to declare link objects, initialization procedures, image types, IODevices, and replacement modules.

Filesystem-adjacent logic is build wiring rather than filesystem implementation. It builds `sfile.dev` for file streams, `clfile.dev` and `clmemory.dev` for file-backed or RAM-backed band lists, `romfs.dev` for the `%rom%` IODevice, `gsiodisk.$(OBJ)` for `%disk%` IODevices, `gp_dosfs`, `gp_dosfe`, `gp_unifs`, and `gp_unifn` for platform filename/filesystem behavior, and `pipe.dev` for the pipe IODevice.

Primary risks are maintenance fragility, handwritten dependency sprawl, historical platform branches, and feature/module coupling scattered through generated `.dev` files. Several comments note misplaced modules or optional pieces that compile for coverage but are not linked into base configurations.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/lib.mak -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/libpng.mak -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/libpng.mak

`libpng.mak` is a partial Ghostscript makefile for PNG writer support. It documents required variables for zlib and libpng source, generated, and object directories, but also notes a historical bug: callers still define `PSRCDIR` and `PVERSION`, so the file maps those to `PNGSRCDIR` and `PNGVERSION`.

The file compiles writer-side libpng modules: `png.c`, `pngwio.c`, `pngmem.c`, `pngerror.c`, `pngset.c`, `pngtrans.c`, `pngwrite.c`, `pngwtran.c`, and `pngwutil.c`. Compilation uses Ghostscript-provided include and flag macros through `PNGCC`.

It supports shared and bundled libpng modes. `libpng.dev` is copied from `libpng_$(SHARE_LIBPNG).dev`; shared mode records `-lib $(LIBPNG_NAME)` and includes zlib encode support, while bundled mode links local PNG objects, zlib encode support, and a version-specific `lpg$(PNGVERSION).dev` module for `pngwio` and `crc32`.

The file depends directly on `zlib.mak` products and is focused on output devices rather than filesystem behavior. A maintenance warning says the non-config clean rule is wrong because it deletes object files too broadly instead of selectively removing this makefile’s products.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/libpng.mak -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/macgenmcpxml.sh -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/macgenmcpxml.sh

`macgenmcpxml.sh` generates a Metrowerks CodeWarrior XML project file for classic Mac OS and Carbon Ghostscript library targets. It emits XML directly to stdout from shell functions.

The script defines writers for the project DTD/header, file records, file references, simple settings, recursive search-path settings, target settings, targets, and project groups. `WriteSETTINGLIST` encodes CodeWarrior panel settings for target output, access paths, build extras, PPC metadata, C compiler mode, warnings, code generation, optimization, linker behavior, and PEF output.

At runtime it scans command-line arguments for `.o` file names, strips path prefixes, converts them to `.c`, and stores them in `CFILES`. It then builds two active targets: `GhostscriptLib Carbon (Debug)` and `GhostscriptLib PPC (Debug)`. Prefix headers are selected by target: Carbon debug uses `macos_carbon_d_pre.h`, Carbon final would use `macos_carbon_pre.h`, Classic debug uses `macos_classic_d_pre.h`, and Classic final uses no prefix.

Integration is through `macos-mcp.mak`, which runs this script over the generated link trace and redirects output to `ghostscript.mcp.xml`. Risks are direct XML interpolation without escaping, fragile shell word splitting, and a documented limitation that library file names containing spaces are not handled by the library group loop.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/macgenmcpxml.sh -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/macos-fw.mak -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/macos-fw.mak

`macos-fw.mak` is a partial makefile for Mac OS X/Darwin shared-object and framework builds. It defines separate shared-object build directories, loader names, `.dylib` naming, versioned symlinks, and framework packaging paths.

The shared-library targets create `lib$(GS).$(major).$(minor).dylib` and symlink the major-version and unversioned names to it. `SODEFS` drives recursive make invocations with dynamic-library linker flags, callout stdio, display-device selection, and relocated generated/object directories.

Targets include `so`, `sodebug`, `install-so`, `soinstall`, `framework`, `framework_install`, `SODIRS`, and `soclean`. The framework target lays out `Versions/<version>`, `Headers`, `Resources`, top-level symlinks, bundled PostScript resources, manual pages, docs, and selected public headers.

This file is included by `macosx.mak` and assumes Darwin shell tools such as `ln`, `cp`, `mkdir`, and `rm`. Comments note that the dynamic-library install name is framework-oriented, so plain `.dylib` use is secondary and less clean.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/macos-fw.mak -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/macos-mcp.mak -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/macos-mcp.mak

`macos-mcp.mak` generates a CodeWarrior XML project from a Unix/Darwin make run. It is not intended to compile Ghostscript directly in this pass; it sets `CC=echo` so the normal make graph emits object names, while auxiliary generators are built with the real `cc`.

The options configure source/object/generated directories, runtime library paths, Mac OS platform identity, third-party source locations, bundled library use, classic Mac features, device sets, band-list storage, file/stdio implementations, and no-sync threading. It includes the normal Ghostscript make fragments, including `gs.mak`, `lib.mak`, `int.mak`, third-party makefiles, device makefiles, and `unix-end.mak`, to reproduce the standard dependency graph.

It adds Mac-specific device and platform module rules for `gdevmac`, `gp_mac`, `gp_macio`, `gp_stdin`, `gp_getnv`, `gp_nsync`, `gdevemap`, `gsdll`, and optional `gp_macpoll`. It also supplies rules for generated helper executables and an intentionally blank `gconfig_.h`.

The final project target copies `macsystypes.h` to `obj/sys/types.h`, runs `macgenmcpxml.sh` over the link trace to produce `ghostscript.mcp.xml`, copies generated configuration source stubs, and sets Mac file type/creator metadata with `/Developer/Tools/SetFile`. This is fragile historical glue for CodeWarrior-era Mac builds.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/macos-mcp.mak -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/macos_carbon_d_pre.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/macos_carbon_d_pre.h

`macos_carbon_d_pre.h` is a CodeWarrior prefix header for the debug Carbon target. It defines `__CARBON__` and `DEBUG 1`.

It is selected by `macgenmcpxml.sh` for the `GhostscriptLib Carbon (Debug)` target. Its effect is compile-time selection of Carbon APIs plus Ghostscript debug/verbose code paths.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/macos_carbon_d_pre.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/macos_carbon_pre.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/macos_carbon_pre.h

`macos_carbon_pre.h` is the non-debug CodeWarrior prefix header for Carbon builds. It only defines `__CARBON__`.

The project generator would use it for a final Carbon target. It has no includes or runtime logic, only compile-time platform selection.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/macos_carbon_pre.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/macos_classic_d_pre.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/macos_classic_d_pre.h

`macos_classic_d_pre.h` is a CodeWarrior prefix header for the debug classic Mac OS target. It defines `DEBUG` without a numeric value.

It is selected for `GhostscriptLib PPC (Debug)` by `macgenmcpxml.sh`. Unlike the Carbon debug prefix, it does not define `__CARBON__`, so compilation remains on the classic Mac OS path.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/macos_classic_d_pre.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/macosx.mak -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/macosx.mak

`macosx.mak` is the Darwin/gcc Ghostscript configuration makefile. It sets build directories, framework installation paths, runtime resource paths, compiler/linker flags, third-party library choices, feature devices, output devices, and Ghostscript platform policy.

It targets a framework-style installation under `/Library/Frameworks/Ghostscript.framework`. Runtime search paths cover bundled library/resources plus `/Library/Fonts` and `/System/Library/Fonts`. It enables `HAVE_MKSTEMP`, uses `cc`, chooses bundled JPEG/PNG/JBIG2/ICC with shared zlib, and defaults to `nosync`.

The default devices emphasize file conversion on macOS: PNG devices, selected PNM/PBM/PGM devices, JPEG devices, PDF/PS writers, PXL, and bbox. X11/display support is disabled by default. Band lists default to file storage, file I/O uses `stdio`, and stdio uses callouts.

The file includes the main Unix/Ghostscript make fragments plus `macos-fw.mak` for shared library and framework targets. Risks are historical Darwin assumptions, framework-oriented shared-object install naming, and no pthread synchronization unless the platform configuration is changed.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/macosx.mak -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/macsystypes.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/macsystypes.h

`macsystypes.h` is a substitute `sys/types.h` for the classic Mac CodeWarrior project path. `macos-mcp.mak` copies it to `obj/sys/types.h`.

It includes `<MacTypes.h>` and `<unix.h>`, defines `CHECK_INTERRUPTS`, sets `GX_COLOR_INDEX_TYPE` to `UInt64`, remaps `main` to `gs_main`, and ensures `__MACOS__` is defined.

There is disabled experimental wrapping for `fprintf`, `fputs`, and `getenv`. The header exists to let Ghostscript’s Unix-flavored includes compile under the old Mac toolchain.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/macsystypes.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/main.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/main.h

`main.h` is a backward-compatible interface shim for older Ghostscript clients of `gsmain.c`. It includes `iapi.h`, `imain.h`, and `iminst.h`.

All compatibility macros and declarations are inside `#if 0`, so this version effectively only provides the include guard and newer main API headers. The disabled block maps old single-interpreter APIs such as `gs_init0`, `gs_run_file`, and `gs_run_string` onto `gs_main_instance_default()` calls.

The file documents a removed compatibility layer while preventing old include paths from failing. There is no active runtime behavior beyond included declarations.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/main.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/malloc_.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/malloc_.h

`malloc_.h` is Ghostscript’s portable wrapper for allocation declarations. It includes `std.h` before any platform header that may include `sys/types.h`.

The header selects an allocation header for old compilers and platforms: Turbo C uses `<alloc.h>`, modern POSIX/STDC/VMS-style paths use `<stdlib.h>`, some old BSD-like paths declare `malloc` and `free` manually, and remaining systems include `<malloc.h>`.

It defines `gs_realloc(ptr, old_size, new_size)` as a portability abstraction. On Linux it declares a Ghostscript replacement and marks `malloc__need_realloc`; elsewhere it maps directly to `realloc`. The risk is historical platform branching and reliance on legacy compiler macros.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/malloc_.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/math_.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/math_.h

`math_.h` is Ghostscript’s portable wrapper for `<math.h>`. It includes `std.h`, then either `vmsmath.h` for GNU VAX/VMS or the system math header.

It ensures `M_PI` exists, defines degree/radian conversion constants, and supplies an exact `MAX_FLOAT` expression for IEEE and VAX float formats. It handles missing or undeclared `hypot`, including `_hypot` on MSVC and a `sqrt(x*x+y*y)` fallback on selected older systems.

For debugging, it declares `gs_sqrt` and redefines `sqrt(x)` to include file/line information when `DEBUG` is set. The header is a portability shim with numerically important constants and debug instrumentation.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/math_.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/md5.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/md5.c

`md5.c` implements MD5 from RFC 1321 using the standalone interface in `md5.h`. It is L. Peter Deutsch’s independent implementation under a permissive license distinct from the surrounding Ghostscript license headers.

The core `md5_process` routine processes one 64-byte block. It handles little-endian aligned data directly, copies unaligned little-endian data, and byte-swaps for big-endian CPUs. If `ARCH_IS_BIG_ENDIAN` is not defined, byte order is detected dynamically.

The file defines the 64 MD5 constants, Boolean functions, rotate macro, and four MD5 rounds. `md5_init` initializes bit counters and digest state, `md5_append` updates length accounting and processes full/partial blocks, and `md5_finish` pads the message, appends the bit length, and writes the 16-byte digest in little-endian order.

Integration in Ghostscript is via `lib.mak` and stream digest support. Security note: MD5 is cryptographically broken for collision resistance, so this code is suitable only for historical compatibility or non-adversarial checksums.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/md5.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/md5.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/md5.h

`md5.h` declares the standalone MD5 API. It defines `md5_byte_t` as `unsigned char`, `md5_word_t` as `unsigned int`, and `md5_state_t` with two bit-count words, four digest state words, and a 64-byte accumulation buffer.

The exported API is `md5_init`, `md5_append`, and `md5_finish`, wrapped in `extern "C"` for C++ callers. The header documents compile-time or runtime byte-order handling through `ARCH_IS_BIG_ENDIAN`.

It has no Ghostscript-specific types. Consumers can use it as a compact standalone hashing interface, subject to MD5’s modern cryptographic limitations.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/md5.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/md5main.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/md5main.c

`md5main.c` is a standalone utility program for the MD5 implementation. It includes `md5.h`, math, stdio, and string headers.

The program supports `--test`, `--t-values`, and `--version`. `--test` runs the RFC 1321 section A.5 test vectors and reports mismatches. `--t-values` computes and prints the 64 sine-derived MD5 constants in the source format used by `md5.c`. `--version` prints the package date string.

This file is not part of the Ghostscript runtime. It is a developer/test helper for validating or regenerating constants for the MD5 library.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/md5main.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/memory_.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/memory_.h

`memory_.h` is Ghostscript’s portable wrapper for memory and string-copy functions. It includes `std.h` first, then chooses system declarations or Ghostscript substitutes based on compiler/platform macros.

For Turbo C it uses `<mem.h>` and an inline `memcmp` path. For modern POSIX/STDC/VMS/HPUX/Watcom/Think C/BSDI/FreeBSD/MSVC cases it uses `<string.h>`. Older BSD/UTEK paths map `memcpy` to `bcopy`, `memcmp` to `bcmp`, declare `bcopy/bcmp/bzero`, and request Ghostscript replacements for missing functions. Some System V/Sun paths request a replacement `memmove`.

Under `PROFILE`, it forces Ghostscript replacements for `memset`, `memcpy`, and `memmove`. Requested substitutions are declared as `gs_memmove`, `gs_memcpy`, `gs_memset`, and `gs_memchr`, with macros redirecting standard names. The main risk is compatibility complexity and semantic differences such as old `bcmp` return values.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/memory_.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/mkromfs.c -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/mkromfs.c

`mkromfs.c` generates a compressed static data image for Ghostscript’s `%rom%` IODevice. It packs PostScript source files, resources, and fonts into a binary image named `gsromfs` so they can be compiled into the executable.

For each command-line path, it opens the file, computes the file length, splits contents into 4096-byte blocks, compresses each block with zlib `compress`, stores per-block compressed lengths, and writes an inode-like record. The record contains the next-inode offset, original file length, path length, path bytes, block-size table, and compressed data blocks.

`romfs_inode` stores the path name, optional tree links, block count, original length, offset, compressed data size, compressed block pointers, and block lengths. `inode_clear` frees allocated inode memory. `inode_write` serializes the inode and logs write details. `put_int32` writes big-endian 32-bit fields.

Risks are significant: allocation and file-open failures are mostly unchecked, `strdup` is not validated, `fseek`/`ftell` errors are ignored, `offset` in `main` is unused, zero-length files would divide by zero in the compression ratio print, and `data_lengths` are written with host-endian `fwrite` even though header fields are big-endian. This is historical build tooling rather than robust archive infrastructure.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/mkromfs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/msvc32.mak -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/msvc32.mak

`msvc32.mak` is the top-level Microsoft Visual C++ makefile for 32-bit Windows Ghostscript, with conditional support for 64-bit compiler paths. It targets `nmake` and makes most configuration overridable through `!ifndef`.

The options cover build directories, install/runtime paths, debug modes (`DEBUG`, `TDEBUG`, `DEBUGSYM`, `NOPRIVATE`), executable and DLL names, `MAKEDLL`, third-party source locations, IJG/libpng/zlib/JBIG2/Jasper/ICC/IJS settings, large 64-bit `gx_color_index`, warnings, MSVC version detection, Visual Studio/DDK tool paths, include/lib environment setup, CPU/FPU selection, synchronization module, language features, band-list storage, file/stdio implementations, UFST flags, and a large default Windows device set.

After including `msvccmd.mak`, `winlib.mak`, `msvctail.mak`, and `winint.mak`, it defines the Windows outputs. In DLL mode it builds small GUI and console loaders plus `gsdll32.dll`; without DLL mode it builds large GUI and console executables. It also links setup and uninstall helpers in DLL mode and provides recursive debug/debugclean targets.

Filesystem relevance is indirect: `GS_LIB_DEFAULT` defines Windows runtime resource paths, `BAND_LIST_STORAGE=file` selects file-backed band lists, and `FILE_IMPLEMENTATION=stdio` selects the file stream backend. The file is old Windows build glue with risks around MSVC version assumptions, quoted path handling, response-file generation through shell `echo`, and synchronization with included feature/device make fragments.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/msvc32.mak -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/msvccmd.mak -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/msvccmd.mak

`msvccmd.mak` defines shared command, compiler, and linker macros for MSVC Ghostscript builds. It is included by both `msvc32.mak` and `msvclib.mak`.

It handles MSVC 4 versus later differences, current-directory syntax, object/output switches, genconf options, optional assembly placeholders, a `dosdefault` target, MSVC 8 deprecation warning suppressions, CPU/FPU flags for i386/PPC/alpha branches, `NOPRIVATE` and `DEBUG` defines, precompiled-header settings, debug versus optimized compiler/linker flags, stack-check/probe flags, and special 64-bit include ordering.

The resulting macros include `GENOPT`, `CCFLAGS`, `CC`, `CPP`, `CC_`, `CC_D`, `CC_INT`, `CC_NO_WARN`, `CCAUX`, and Windows-specific compile variants. `MAKEDLL` determines whether ordinary compilation is for DLL or EXE output.

This file is a pure build-command layer. Its risk is historical compiler behavior encoded in conditionals, especially workarounds for old optimizer bugs, stack-probe differences, and MSVC-version-specific switches.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/msvccmd.mak -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/msvclib.mak -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/msvclib.mak

`msvclib.mak` is the Microsoft Visual C++ makefile for building the Ghostscript graphics library test executable rather than the full Windows interpreter package. It is aimed at MSVC 4.1 or later on Windows NT/95-era systems and uses `nmake` conditionals.

The file configures Ghostscript runtime paths, debug options, compiler/tool locations, CPU/FPU defaults, `winsync`, third-party source locations, band-list storage, file I/O implementation, and a library-oriented feature/device set. Unlike the full interpreter makefile, `STDIO_IMPLEMENTATION` is forced blank because callout stdio is not allowed for the library target.

It sets `LIB_ONLY` to include `gslib.obj`, `gsnogc.obj`, `gconfig.obj`, and `gscdefs.obj`, forces `MAKEDLL=0`, sets `PLATFORM=mslib32_`, then includes `version.mak`, `msvccmd.mak`, `winlib.mak`, and `msvctail.mak`.

The platform-specific library module builds `gp_mslib.obj`, creates `mslib32_.dev` by including `mswin32_.dev`, and links the console library tester `$(GS_XE)` using a generated trace and response file. Filesystem relevance is limited to runtime path defaults and file-backed band-list/file-stream choices.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/msvclib.mak -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/msvctail.mak -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/msvctail.mak

`msvctail.mak` is the common tail section for MSVC Ghostscript makefiles. It supplies auxiliary program rules and common Windows library response-file generation.

The first rule creates build directories and writes `ccf32.tr`, a compiler flag trace containing `GENOPT`, `CHECK_INTERRUPTS`, `_Windows`, and `__WIN32__`. It then defines build rules for auxiliary tools: `echogs`, optional `genarch`, `genconf`, `gendev`, `genht`, and `geninit`. The 64-bit `genarch` case uses separate compile and link steps.

It also defines `LIBCTR=$(GLGEN)libc32.tr`, which records standard Windows libraries: `shell32.lib`, `comdlg32.lib`, `gdi32.lib`, `user32.lib`, `winspool.lib`, and `advapi32.lib`.

This file has no runtime filesystem implementation. Its main role is MSVC build bootstrap, directory creation, and shared response-file support.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/msvctail.mak -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/oparc.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/oparc.h

`oparc.h` declares Ghostscript arc operator entry points: `zarc`, `zarcn`, and `zarct`.

The declarations are separate from broader operator extern headers because these operators are not included in PDF-only configurations. The file depends on the interpreter context type `i_ctx_t` being available to includers.

There is no filesystem behavior; this is a small interpreter operator interface header.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/oparc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/opcheck.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/opcheck.h

`opcheck.h` defines operand-checking macros for Ghostscript interpreter operators. It expects surrounding includes to provide allocation context, ref accessors, and error codes.

The macros check object type, structured type, array/procedure status, read/write/execute access, combined type/access requirements, and integer ranges against unsigned bounds. `check_proc_failed` is declared for procedure validation that may also account for stack underflow.

These macros return Ghostscript errors such as `e_typecheck`, `e_invalidaccess`, and `e_rangecheck` directly from operator functions. The file is interpreter safety glue, not filesystem code.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/opcheck.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/opdef.h -->
# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/opdef.h

`opdef.h` defines the Ghostscript operator-definition interface. Operator source files declare arrays of `op_def` entries mapping encoded operator names to C procedure pointers, typically ending with `op_def_end(iproc)`.

It supports dictionary-scoped operator groups through `op_def_begin_dict`, plus helpers for `filterdict`, `level2dict`, and `ll3dict`. Tables are limited to 16 entries, so larger operator files must split definitions across multiple tables and makefile `-oper` entries.

The header declares the global operator-definition catalog, indexing helpers, internal-operator detection for names beginning with `%`, and conversion from operator index to `ref`. It also defines `op_array_table` for global and local procedure-defined operator arrays, including table refs, name-index tables, counts, base indices, attributes, and GC root pointers.

This is core interpreter dispatch metadata. There is no filesystem behavior, but it is tightly coupled to generated operator tables and the makefile feature system.
<!-- END FILE RESEARCH: sources/os/plan9/plan9/sys/src/cmd/gs/src/opdef.h -->