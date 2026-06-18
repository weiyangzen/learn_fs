# sources/compression/zstd/lib/libzstd.pc.in

Purpose: Template for generating the `libzstd.pc` pkg-config metadata file used by downstream build systems to discover include paths, link flags, version, URL, description, and license for libzstd.

Important fields: Substitution variables are `@PREFIX@`, `@EXEC_PREFIX@`, `@INCLUDEDIR@`, `@LIBDIR@`, `@VERSION@`, `@LIBS_MT@`, and `@LIBS_PRIVATE@`. The generated package is named `zstd`, describes the library as a fast lossless compression algorithm, points to `https://facebook.github.io/zstd/`, emits `Libs: -L${libdir} -lzstd @LIBS_MT@`, `Libs.private: @LIBS_PRIVATE@`, and `Cflags: -I${includedir} @LIBS_MT@`.

Control flow: This file is not executed directly. The install/configure or make install flow substitutes placeholders with installation directories, the libzstd version, and platform-specific threading/private libraries, then installs the resulting `.pc` file for pkg-config consumers.

State and persistence behavior: The template itself has no runtime state. The generated `.pc` file becomes persistent installation metadata and affects every downstream compile or link command that uses `pkg-config --cflags --libs zstd`.

Dependencies and integration points: Consumed by libzstd packaging/install scripts. Downstream build tools read the generated file through pkg-config. `@LIBS_MT@` integrates thread flags into both compile and link lines when needed, while `@LIBS_PRIVATE@` supports static-link-only dependencies.

Risks: Incorrect substitution of prefix/libdir/includedir breaks downstream discovery. Putting `@LIBS_MT@` in `Cflags` may be necessary for some threading models but can leak linker-like flags into compile commands if substituted poorly. License text says `BSD-3-Clause OR GPL-2.0-only`, while the surrounding source comments often describe a BSD-style license plus GPLv2 choice; packaging checks should confirm the intended SPDX expression for this vendored version.

Test signals: After install, run `pkg-config --modversion zstd`, `--cflags`, `--libs`, and `--static --libs`; compile and link a tiny zstd consumer with shared and static settings; verify relocated prefix values and platform-specific thread/private libraries.
