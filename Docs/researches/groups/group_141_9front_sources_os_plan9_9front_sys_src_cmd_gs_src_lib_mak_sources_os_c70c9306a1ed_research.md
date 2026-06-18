# Group Research: group_141_9front_sources_os_plan9_9front_sys_src_cmd_gs_src_lib_mak_sources_os_c70c9306a1ed

Scope verified against `Docs/research_subset_a.md`: `sources/os/plan9/9front` is included. All listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/lib.mak -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/lib.mak

## Purpose
Platform-independent Ghostscript graphics-library make fragment. It defines generated/source/object directory aliases, compiler command macros, header dependency macros, object compilation rules, and `.dev` module assembly rules for the core graphics library and many optional Ghostscript facilities.

## Main Structure
- Establishes `GLSRC`, `GLGEN`, `GLOBJ`, `GLCC`, specialized compiler wrappers for JPEG/zlib/ICC/JBIG2, and `LIB_MAK`.
- Defines dependency aliases for generic headers, platform interfaces, generated configuration headers, C library wrapper headers, memory manager headers, graphics headers, stream/filter headers, color/font/image/device headers, and auxiliary generator dependencies.
- Provides object rules for memory management, bitmap operations, synchronization, platform glue, MD5, visual debugging, graphics state/path/color/image/font/device code, filters, clists, page/vector devices, Type 1/TrueType/CID/pattern/shading/transparency support, ROM/disk/Mac resource IODevices, UFST bridge hooks, and platform-specific shared modules.
- Assembles feature/device modules with `SETMOD`, `ADDMOD`, `SETDEV`, `SETDEV2`, `ADDCOMP`, and `-replace`/`-include` relationships.

## Important Build Products
- Core library features: `libs.dev`, `libx.dev`, `libd.dev`, `libcore.dev`.
- Stream/filter modules: `sfile.dev`, `cfe.dev`, `cfd.dev`, `sdcte.dev`, `sdctd.dev`, `lzwe.dev`, `lzwd.dev`, `smd5.dev`, `sarc4.dev`, `saes.dev`, `sjbig2.dev`, `sjpx.dev`, `pdiff.dev`, `pngp.dev`, `rle.dev`, `rld.dev`, `szlibe.dev`, `szlibd.dev`.
- Device/library features: `page.dev`, `clist.dev`, `vector.dev`, `iscale.dev`, `roplib.dev`, `async.dev`, `ttflib.dev`, `cidlib.dev`, `cmaplib.dev`, `patlib.dev`, `psf1lib.dev`, `psf2lib.dev`, `cmyklib.dev`, `psl2lib.dev`, `funclib.dev`, `cielib.dev`, `sicclib.dev`, `psl3lib.dev`, `translib.dev`, `shadelib.dev`, `romfs.dev`, `macres.dev`.

## Integration Notes
- Consumed by platform makefiles such as Unix, Mac, and Windows builds after they define directory, compiler, and module-building macros.
- Depends on other partial makefiles for generated configuration/device metadata and third-party libraries.
- `md5.c` is built through a generated wrapper header/copy path so `memory_.h` is included before the original MD5 header.

## Risks and Edge Cases
- Very macro-heavy; missing platform definitions break many rules indirectly.
- Some dependencies reference names that are not defined locally or look inconsistent in this file, including `memory_h`, `stdint_`, `vtrace_h`, `gsdebug_h`, and `gsfixed_h`; these may be supplied by other make fragments or may be old makefile defects.
- `.dev` module ordering matters because later features replace or include earlier pseudo-features.
- Clean separation between base, optional, and testing-only modules is encoded only by variable membership and `.dev` inclusion, not by a central manifest.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/lib.mak -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/libpng.mak -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/libpng.mak

## Purpose
Ghostscript partial makefile for building or sharing libpng support used by PNG output drivers.

## Main Structure
- Maps historical Ghostscript variables `PSRCDIR`/`PVERSION` to `PNGSRCDIR`/`PNGVERSION`.
- Defines PNG source/generated/object directory aliases and `PNGCC`.
- Provides `png.clean`, `png.config-clean`, and object rules for selected libpng writer-side modules.
- Defines `libpng.dev` as a copy of either `libpng_0.dev` or `libpng_1.dev` depending on `SHARE_LIBPNG`.

## Important Build Products
- Compiled objects: `png`, `pngwio`, `pngmem`, `pngerror`, `pngset`, `pngtrans`, `pngwrite`, `pngwtran`, `pngwutil`.
- `libpng_1.dev`: shared-lib wrapper that links `LIBPNG_NAME` and includes zlib encode support.
- `libpng_0.dev`: static module grouping PNG objects and including zlib plus version-specific `lpg$(PNGVERSION).dev`.
- `lpg$(PNGVERSION).dev`: version-specific module for `pngwio` plus zlib `crc32`.

## Integration Notes
- Must be included after zlib support because `zlibe.dev` and `crc32.dev` are required.
- Used by platform makefiles that set `SHARE_LIBPNG`, `LIBPNG_NAME`, and libpng source version variables.

## Risks and Edge Cases
- Comment explicitly states clean rules are broad and “wrong” because they delete object files non-selectively.
- Only a subset of libpng modules is built here, aimed at Ghostscript writer/output use rather than a complete standalone libpng build.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/libpng.mak -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/macgenmcpxml.sh -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/macgenmcpxml.sh

## Purpose
Shell generator for a CodeWarrior XML project file for classic Mac OS / Carbon Ghostscript library builds.

## Main Structure
- Emits a full XML/DTD header with `WriteXMLHeader`.
- Helper functions emit `<FILE>`, `<FILEREF>`, scalar settings, path settings, target setting lists, target definitions, and project groups.
- Parses command-line `.o` arguments, strips paths, converts them to `.c`, and builds `CFILES`.
- Defines Carbon and classic library lists, target names, and emits a project with Carbon debug and classic debug targets.

## Important Settings
- Compiler prefix header is selected by target:
  - Carbon debug: `macos_carbon_d_pre.h`
  - Carbon non-debug: `macos_carbon_pre.h`
  - Classic debug: `macos_classic_d_pre.h`
  - Classic non-debug: no prefix value.
- Search paths include project `src`, `obj`, root, CodeWarrior MacOS Support, MSL, jbig2dec, and Jasper include paths.
- PPC project type is `SharedLibrary`.

## Integration Notes
- Invoked from `macos-mcp.mak` using the object list from `ldt.tr`.
- Output is redirected to `ghostscript.mcp.xml`, then marked as CodeWarrior text metadata by `SetFile`.

## Risks and Edge Cases
- Library filenames with spaces are explicitly noted as unsupported by the group-generation loop.
- XML is emitted by unescaped `echo`; paths containing XML-significant characters would break the output.
- The parser only recognizes `*.o` arguments and ignores other link tokens except literal backslash continuations.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/macgenmcpxml.sh -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/macos-fw.mak -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/macos-fw.mak

## Purpose
Partial makefile for Mac OS X/Darwin shared library and framework targets.

## Main Structure
- Defines shared-object output directories `SOOBJRELDIR` and `SOBINRELDIR`.
- Defines simple loader executable names, dylib names, soname variants, and symlink rules.
- Defines `SODEFS` to run recursive make with dynamic-library linker flags and separate generated/object directories.
- Provides `so`, `sodebug`, `install-so`, `soinstall`, `framework`, `framework_install`, `SODIRS`, and `soclean` targets.

## Important Build Products
- Dylib names: `lib$(GS).dylib`, major, and major/minor variants.
- Loader executable: `$(GS)c$(XE)` built from `dxmainc.c`.
- Framework tree under `$(BINDIR)/../sobin/$(FRAMEWORK_NAME).framework`.

## Integration Notes
- Included by `macosx.mak`.
- Framework packaging copies public headers `iapi.h`, `ierrors.h`, `gdevdsp.h`, `Info-macos.plist`, `lib`, `man`, `doc`, and the built dylib into the framework layout.

## Risks and Edge Cases
- Comments note the install name is framework-oriented and can make plain `.dylib` usage secondary or broken.
- Uses `rm -rf` for framework rebuild/install paths; prefix values must be correct.
- Symlink rules assume Unix-like filesystem semantics.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/macos-fw.mak -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/macos-mcp.mak -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/macos-mcp.mak

## Purpose
Makefile that generates a Metrowerks CodeWarrior XML project from a Darwin/Mac OS X host for building Ghostscript targeting classic Mac OS/Carbon.

## Main Structure
- Defines Ghostscript source/generated/object directories and includes `version.mak`.
- Sets classic Mac runtime paths, feature selection, bundled third-party library settings, compiler/linker stubs, device lists, and build feature modules.
- Includes the normal Ghostscript make fragments with `CC=echo` so dependency/link traces can be generated rather than compiled.
- Adds Mac device/platform module rules and auxiliary generator builds with real `cc`.
- Generates `ghostscript.mcp.xml` by copying `macsystypes.h` to generated `sys/types.h`, invoking `macgenmcpxml.sh` over `ldt.tr`, and copying generated config source files.

## Important Build Products
- `macos.dev`: Mac display/device module.
- `macos_.dev`: platform module containing Mac file/IO/stdin/glue objects plus `gp_getnv`, `gp_nsync`, `gdevemap`, and `gsdll`.
- `macpoll.dev`: polling feature for interpreter builds.
- `ghostscript.mcp.xml`: CodeWarrior import project.

## Integration Notes
- Includes `gs.mak`, `lib.mak`, `int.mak`, fonts, JPEG, zlib, libpng, jbig2, Jasper, icclib, devices, contrib, and Unix end fragments.
- The default `GS_XE` target depends on link trace generation and XML generation rather than producing a normal Unix executable.

## Risks and Edge Cases
- `CC=echo` means normal compile commands are intentionally not real; auxiliary tools use `CCAUX=cc`.
- Assumes `/Developer/Tools/SetFile` exists.
- IJS is commented out as not ported to Mac OS Classic.
- Full device list is large and may produce project/library filename issues when combined with `macgenmcpxml.sh` limitations.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/macos-mcp.mak -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/macos_carbon_d_pre.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/macos_carbon_d_pre.h

## Purpose
CodeWarrior prefix header for the Mac OS Carbon debug target.

## Main Content
- Include guard `macos_carbon_d_pre_INCLUDED`.
- Defines `__CARBON__`.
- Defines `DEBUG 1` for verbose/debug Ghostscript builds.

## Integration Notes
- Selected by `macgenmcpxml.sh` when generating the Carbon debug target settings.

## Risks and Edge Cases
- Only build-time macro definitions; any behavior depends on source files checking `__CARBON__` and `DEBUG`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/macos_carbon_d_pre.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/macos_carbon_pre.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/macos_carbon_pre.h

## Purpose
CodeWarrior prefix header for non-debug Mac OS Carbon targets.

## Main Content
- Include guard `macos_carbon_pre_INCLUDED`.
- Defines `__CARBON__`.

## Integration Notes
- Selected by `macgenmcpxml.sh` for Carbon non-debug/final target settings.

## Risks and Edge Cases
- Minimal prefix; no debug symbols or diagnostics are enabled here.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/macos_carbon_pre.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/macos_classic_d_pre.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/macos_classic_d_pre.h

## Purpose
CodeWarrior prefix header for classic Mac OS debug targets.

## Main Content
- Include guard `macos_classic_d_pre_INCLUDED`.
- Defines `DEBUG` without an explicit value.

## Integration Notes
- Selected by `macgenmcpxml.sh` for the classic PPC debug target.

## Risks and Edge Cases
- `DEBUG` is defined empty rather than `1`; code using `#ifdef DEBUG` works, but numeric `#if DEBUG` behavior differs.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/macos_classic_d_pre.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/macosx.mak -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/macosx.mak

## Purpose
Mac OS X/Darwin GCC/framework Ghostscript configuration makefile.

## Main Structure
- Defines build directories, install commands, framework paths, runtime resource/font paths, Ghostscript executable name, build-time Ghostscript, and third-party source/library options.
- Sets Darwin-oriented compiler/linker flags, default devices, features, band-list storage, file/stdio implementation, and synchronization mode.
- Includes Unix/Ghostscript partial makefiles, third-party makefiles, device/contrib makefiles, `macos-fw.mak`, and Unix install tail.

## Important Defaults
- Framework prefix: `/Library/Frameworks/Ghostscript.framework`.
- `GS_LIB_DEFAULT` includes framework resources plus `/Library/Fonts` and `/System/Library/Fonts`.
- `CAPOPT=-DHAVE_MKSTEMP`.
- `SHARE_ZLIB=1`; JPEG, PNG, JBIG2 use bundled builds by default.
- Default output devices emphasize PNG output plus PNM/JPEG/PDF/PS/PXL/bbox.

## Integration Notes
- `macos-fw.mak` supplies shared-library/framework targets.
- Uses normal Unix-style build fragments, unlike `macos-mcp.mak` which generates CodeWarrior project XML.

## Risks and Edge Cases
- `SYNC=nosync` by default even on Darwin unless changed.
- X11 variables are empty by default.
- Framework resource layout is encoded in make variables and packaging rules, so version/path changes affect runtime lookup.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/macosx.mak -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/macsystypes.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/macsystypes.h

## Purpose
Mac CodeWarrior replacement for generated `sys/types.h` during project generation/build.

## Main Content
- Include guard `__sys_types_h__`.
- Includes `<MacTypes.h>` and `<unix.h>`.
- Defines `CHECK_INTERRUPTS`.
- Defines `GX_COLOR_INDEX_TYPE UInt64`.
- Renames `main` to `gs_main`.
- Ensures `__MACOS__` is defined.

## Integration Notes
- Copied by `macos-mcp.mak` to `obj/sys/types.h`.
- Provides Mac system typing and build macros expected by Ghostscript portability wrappers.

## Risks and Edge Cases
- `main` macro replacement affects all included compilation units and must be scoped to this build mode.
- Uses CodeWarrior/Mac-specific headers that are not portable to modern non-CodeWarrior toolchains.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/macsystypes.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/main.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/main.h

## Purpose
Backward-compatible Ghostscript interface wrapper for old single-interpreter clients of `gsmain.c`.

## Main Structure
- Includes `iapi.h`, `imain.h`, and `iminst.h`.
- Contains legacy macro aliases for `gs_init*`, library path setup, file/string execution, and debug stack dumping.
- The entire legacy interface body is disabled by `#if 0`.

## Integration Notes
- Present for compatibility naming and include stability, but exports no active wrappers beyond including the modern API headers.

## Risks and Edge Cases
- Consumers expecting old macros from this header will not get them because the block is disabled.
- Comments preserve historical API migration information but not active behavior.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/main.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/malloc_.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/malloc_.h

## Purpose
Ghostscript portability wrapper for `malloc.h`/allocation declarations across old C libraries and platforms.

## Main Structure
- Includes `std.h` first to satisfy Ghostscript ordering requirements.
- Selects `<alloc.h>`, `<stdlib.h>`, `<malloc.h>`, or manual `malloc`/`free` declarations depending on compiler/platform macros.
- Defines `gs_realloc` as either a Ghostscript replacement or a direct `realloc` wrapper.

## Integration Notes
- Used by `lib.mak` dependency graph as `malloc__h`.
- On Linux defines `malloc__need_realloc` and declares `gs_realloc(void *, size_t, size_t)`.

## Risks and Edge Cases
- Contains historical platform conditionals for very old compilers/Unix variants.
- Linux realloc substitution changes call semantics to include old and new sizes.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/malloc_.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/math_.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/math_.h

## Purpose
Ghostscript portability wrapper for `math.h`.

## Main Structure
- Includes `std.h`, then either `vmsmath.h` or standard `<math.h>`.
- Defines `M_PI` if missing.
- Defines `degrees_to_radians`, `radians_to_degrees`, and exact `MAX_FLOAT` constants for VAX and IEEE-like platforms.
- Supplies or aliases `hypot` for selected systems.
- Declares `gs_sqrt` and intercepts `sqrt` in `DEBUG` builds.

## Integration Notes
- Used throughout graphics/math-heavy Ghostscript modules via `math__h` dependencies.

## Risks and Edge Cases
- `sqrt` macro interception can surprise code that expects the raw library function under `DEBUG`.
- Fallback `hypot` macro may evaluate arguments more than once through multiplication expressions.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/math_.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/md5.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/md5.c

## Purpose
Standalone independent MD5 implementation derived from RFC 1321 concepts, exposing init/append/finish digest operations.

## Main Structure
- Includes `md5.h` and `<string.h>`.
- Determines byte order statically via `ARCH_IS_BIG_ENDIAN` or dynamically at runtime.
- Defines MD5 constants `T1` through `T64`.
- `md5_process` processes one 64-byte block through MD5 rounds F, G, H, and I.
- `md5_init` initializes count and digest state.
- `md5_append` updates bit count, buffers partial blocks, and processes full 64-byte blocks.
- `md5_finish` pads the message, appends length, and writes the 16-byte digest.

## Integration Notes
- Built specially in `lib.mak` to prepend Ghostscript memory header handling before compiling generated `md5.c`.
- Used by stream digest support through `smd5.dev`.

## Risks and Edge Cases
- `md5_append` takes `int nbytes`; very large single append lengths are limited by signed integer range, though total count is stored in two 32-bit words.
- Uses pointer alignment arithmetic through `data - (const md5_byte_t *)0`, a historical idiom that can be compiler-sensitive.
- MD5 is cryptographically broken for collision resistance; suitable only for legacy checksums/digests where security is not required.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/md5.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/md5.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/md5.h

## Purpose
Public header for the standalone MD5 implementation.

## Main Content
- Defines `md5_byte_t` as `unsigned char`.
- Defines `md5_word_t` as `unsigned int`.
- Defines `md5_state_t` with bit count, four-word digest buffer, and 64-byte partial block buffer.
- Declares `md5_init`, `md5_append`, and `md5_finish`, wrapped in `extern "C"` for C++.

## Integration Notes
- Documents optional `ARCH_IS_BIG_ENDIAN` behavior for compile-time byte-order specialization.

## Risks and Edge Cases
- Assumes `unsigned int` is 32 bits, matching the intended Ghostscript-era target assumptions.
- Header is generic and not Ghostscript-specific, but `lib.mak` wraps compilation for Ghostscript include ordering.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/md5.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/md5main.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/md5main.c

## Purpose
Standalone command-line utility for the MD5 package.

## Main Structure
- Supports `--test`, `--t-values`, and `--version`.
- `do_test` runs seven RFC 1321 test vectors and compares hex digests.
- `do_t_values` prints generated `T1` through `T64` constants from `floor(2^32 * abs(sin(i)))`.
- `main` dispatches on one argument or prints usage.

## Integration Notes
- Intended compilation example: `gcc -o md5main -lm md5main.c md5.c`.
- Not part of the Ghostscript runtime library path unless explicitly built as a utility.

## Risks and Edge Cases
- Returns `0` after usage text for invalid arguments, so misuse is not signaled as command failure.
- Uses `sprintf` into a fixed correctly sized hex buffer for known 16-byte digest output.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/md5main.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/memory_.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/memory_.h

## Purpose
Ghostscript portability wrapper for memory/string routines such as `memcpy`, `memcmp`, `memmove`, `memset`, and `memchr`.

## Main Structure
- Includes `std.h` first.
- Handles Turbo C, VMS, POSIX/STDC, HP-UX, Watcom, THINK C, BSDI, FreeBSD, MSVC, old BSD, UTEK, System V, and Sun variants.
- Defines `memcmp_inline`.
- Maps missing or profiling-substituted routines to Ghostscript implementations: `gs_memmove`, `gs_memcpy`, `gs_memset`, `gs_memchr`.

## Integration Notes
- Used widely across `lib.mak` object dependencies.
- Replacement implementations are declared here and supplied elsewhere, noted as `gsmisc.c` for missing routines.

## Risks and Edge Cases
- Old BSD `bcmp` semantics differ from `memcmp`; comment warns it may return only zero/non-zero.
- Profiling mode replaces standard memory functions even if the platform supplies them.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/memory_.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/mkromfs.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/mkromfs.c

## Purpose
Utility that compresses files into a binary `gsromfs` image for Ghostscript’s `%rom%` IODevice.

## Main Structure
- Defines ROM filesystem block size as 4096 bytes and computes zlib compression buffer size.
- `romfs_inode` stores file name, length, compressed block count, data arrays, and metadata.
- `put_int32` writes big-endian 32-bit values.
- `inode_clear` frees per-inode memory.
- `inode_write` writes inode header, path, block-size table, and compressed blocks.
- `main` opens `gsromfs`, iterates input file paths, compresses each file block-by-block with zlib, writes records, and frees buffers.

## Output Format Signals
- Per file: next-inode offset, original length, path length, path bytes, compressed block lengths, compressed data.
- Logs compression and write details to stdout.

## Risks and Edge Cases
- No error checking for `malloc`, `calloc`, `fopen`, `fseek`, `ftell`, `fread`, or output file creation.
- Division by zero if an input file has length 0 when printing compression percentage.
- Local `offset` in `main` is unused.
- `node->offset` is computed as per-record size, not accumulated global file offset; reader expectations must match that design.
- `cbuf` is not freed before exit, though process teardown reclaims it.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/mkromfs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/msvc32.mak -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/msvc32.mak

## Purpose
Primary NMAKE makefile for 32-bit/64-bit Microsoft Visual C++ Ghostscript executable and DLL builds on Windows.

## Main Structure
- Defines configurable directories, install paths, runtime library path, debug/release flags, executable/DLL names, third-party source directories, build-time Ghostscript, and `MAKEDLL`.
- Detects or defaults MSVC versions 4 through 8 and sets compiler, linker, resource compiler, include, and library directories.
- Defines CPU/FPU options, synchronization module, feature/devices, large color-index support, and UFST flags.
- Includes `msvccmd.mak`, `winlib.mak`, `msvctail.mak`, and `winint.mak`.
- Provides link rules for DLL-based small GUI/console loaders or large standalone GUI/console executables.

## Important Build Products
- GUI executable: `gswin32.exe` by default.
- Console executable: `gswin32c.exe`.
- DLL: `gsdll32.dll`.
- Setup/uninstall executables when `MAKEDLL=1`.
- Response files such as `lib32.rsp` and `gswin32.rsp`.

## Integration Notes
- Uses `winlib.mak` and `winint.mak` for Windows platform and interpreter object sets.
- `DEBUGDEFS` target recursively builds debug variants in separate directories.

## Risks and Edge Cases
- Many version/path defaults are historical and target old Visual Studio layouts.
- 64-bit support relies on DDK/VS-specific paths and conditionals.
- Conditional near the default target check uses `Win64` casing while most later logic uses `WIN64`, which may affect defaulting behavior depending on NMAKE definitions.
- Link steps rely on generated response files and cleanup commands; failed intermediate steps may leave stale `.rsp`/`.tr` files.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/msvc32.mak -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/msvccmd.mak -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/msvccmd.mak

## Purpose
Common MSVC command/flag definition fragment for Ghostscript Windows builds.

## Main Structure
- Sets MSVC-version-specific linker/compiler quirks such as `/QI0f` and `CCAUX_TAIL`.
- Defines path separator, shell macro, object/compiler switches, and genconf arguments.
- Provides `dosdefault` target to make the default target work under DOS/NMAKE conventions.
- Defines warning, CPU, FPU, debug, optimization, stack-check, precompiled-header, include, and runtime-library flags.
- Constructs `CC`, `CPP`, `CC_`, `CC_D`, `CC_INT`, `CC_NO_WARN`, `CCAUX`, and `CCWINFLAGS`.

## Integration Notes
- Included by `msvc32.mak` and `msvclib.mak`.
- Depends on variables such as `MSVC_VERSION`, `CPU_FAMILY`, `FPU_TYPE`, `DEBUG`, `TDEBUG`, `DEBUGSYM`, `MAKEDLL`, and generated `ccf32.tr`.

## Risks and Edge Cases
- Optimization settings encode historical MSVC 5 compiler bug workarounds.
- Debug/release runtime library flags switch between `/MT`, `/MTd`, and symbol options.
- Modern MSVC behavior may differ substantially from these legacy assumptions.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/msvccmd.mak -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/msvclib.mak -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/msvclib.mak

## Purpose
NMAKE makefile for building a Microsoft Visual C++ Ghostscript library/tester configuration rather than the full Windows interpreter application.

## Main Structure
- Defines runtime/install defaults, debug flags, directory defaults, third-party sources, compiler path detection, CPU/FPU settings, synchronization module, and feature/device selection.
- Sets `STDIO_IMPLEMENTATION` empty because the library build only allows normal file I/O.
- Sets `LIB_ONLY`, `MAKEDLL=0`, and `PLATFORM=mslib32_`.
- Includes `version.mak`, `msvccmd.mak`, `winlib.mak`, and `msvctail.mak`.
- Adds `gp_mslib` platform object and `mslib32_.dev`.

## Important Build Products
- `mslib32_.dev`: library platform module including `gp_mslib` and `mswin32_.dev`.
- `gslib.exe` by default: console library tester executable linked from Ghostscript library components.

## Integration Notes
- Shares most command generation and Windows library logic with `msvc32.mak`.
- Feature set is library-oriented and uses graphics-library `.dev` features rather than full interpreter Windows UI modules.

## Risks and Edge Cases
- Defaults to `TDEBUG=1` due to historical MSVC 5 optimization concerns, producing slower/larger builds.
- Supports only older MSVC versions in comments/defaults compared with `msvc32.mak`.
- Link rule manually appends required library-only objects to a trace file.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/msvclib.mak -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/msvctail.mak -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/msvctail.mak

## Purpose
Common tail fragment for MSVC/NMAKE Ghostscript builds, focused on auxiliary tools and common Windows library response files.

## Main Structure
- Rule for `ccf32.tr` creates generated/object/bin directories and writes common preprocessor flags.
- Builds auxiliary generators: `echogs`, `genarch`, `genconf`, `gendev`, `genht`, and `geninit`.
- Has special 64-bit `genarch` path using separate compile/link steps.
- Defines `LIBCTR` response file with common Windows libraries.

## Integration Notes
- Included after `msvccmd.mak` and platform variables are established.
- Supports both full Windows and library-only builds.

## Risks and Edge Cases
- Directory creation is tied to the first generation of `ccf32.tr` as a workaround for NMAKE lacking `.BEFORE`.
- Common libraries are hard-coded: `shell32`, `comdlg32`, `gdi32`, `user32`, `winspool`, `advapi32`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/msvctail.mak -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/oparc.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/oparc.h

## Purpose
Header declaring PostScript arc operator implementations.

## Main Content
- Include guard `oparc_INCLUDED`.
- Declares `zarc`, `zarcn`, and `zarct`, each taking `i_ctx_t *`.

## Integration Notes
- Comment explains these declarations are separate from `opextern.h` because arc operators are not included in PDF-only configurations.

## Risks and Edge Cases
- Requires `i_ctx_t` to be declared before inclusion.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/oparc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/opcheck.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/opcheck.h

## Purpose
Macro utilities for Ghostscript PostScript operator operand validation.

## Main Structure
- Defines type checks: `check_type_only`, `check_stype_only`, array checks, procedure checks.
- Defines access checks: read, write, execute, and combined type/access checks.
- Defines unsigned integer bound checks: `check_int_leu`, `check_int_leu_only`, `check_int_ltu`.
- Declares `check_proc_failed`.

## Integration Notes
- Requires allocation/reference/error context headers such as `ialloc.h`, `iref.h`, and `ierrors.h`.
- Used by operator implementations to return PostScript errors such as `e_typecheck`, `e_invalidaccess`, and `e_rangecheck`.

## Risks and Edge Cases
- Macros assume surrounding code has `return_error`, `BEGIN`, `END`, and reference helpers in scope.
- Some macros evaluate ref arguments multiple times or require lvalue-like `ref` expressions.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/opcheck.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/opdef.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/opdef.h

## Purpose
Operator definition/catalog interface for Ghostscript’s PostScript interpreter.

## Main Structure
- Defines `op_def` entries with operator name string and C procedure pointer.
- Provides macros for dictionary-bound operator tables and table terminators.
- Defines fixed table chunk size: `OP_DEFS_LOG2_MAX_SIZE=4`, `OP_DEFS_MAX_SIZE=16`.
- Declares global `op_defs_all` and `op_def_count`.
- Defines operator index helpers for normal operators and internal `%` operators.
- Defines `op_array_table` for procedure-defined operators in global/local tables.
- Declares `op_index_ref`.

## Integration Notes
- Operator source files declare arrays ending with `op_def_end(iproc)`.
- Makefiles must split any operator definition table over 16 entries into multiple tables and multiple `-oper` entries.
- Supports separate dictionaries such as `filterdict`, `level2dict`, and `ll3dict`.

## Risks and Edge Cases
- Operator table size limit is structural and enforced by build/source organization, not dynamic allocation.
- Internal operators have packed size 0 and require lookup by procedure address.
- Correct indexing is central to `bind`, packed arrays, and operator execution behavior.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/gs/src/opdef.h -->