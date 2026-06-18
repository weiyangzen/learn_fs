# sources/compression/xz/CMakeLists.txt

## Purpose
This is the top-level CMake build for XZ Utils. It configures package metadata, system feature probes, liblzma build composition, command-line tools, scripts, documentation, installation components, package config files, and optional tests.

## Important APIs, Options, and Functions
Important options include `BUILD_SHARED_LIBS`, `XZ_SYMBOL_VERSIONING`, `XZ_THREADS`, `XZ_SMALL`, `XZ_CHECKS`, `XZ_EXTERNAL_SHA256`, `XZ_MATCH_FINDERS`, `XZ_ENCODERS`, `XZ_DECODERS`, `XZ_MICROLZMA_ENCODER`, `XZ_MICROLZMA_DECODER`, `XZ_LZIP_DECODER`, `XZ_SANDBOX`, tool toggles, `XZ_NLS`, `XZ_DOC`, and `XZ_DOXYGEN`. Helper functions `my_install_symlinks()`, `my_install_man_lang()`, and `my_install_man()` centralize install-time symlink and man-page behavior. It imports tuklib CMake modules for large-file, integer, CPU core, physical memory, program-name, and multibyte-string detection.

## Control Flow and State
Configuration reads `version.h`, starts the `xz` C project, normalizes Release optimization, rejects old MSVC, sets common compile definitions, detects system extensions and platform APIs, then constructs `liblzma` incrementally from selected checks, match finders, encoders, decoders, threading, CRC acceleration, SHA implementation, symbol visibility, Windows resources, and symbol version scripts. It generates `liblzma-config*.cmake` and `liblzma.pc`, defines optional command tools (`xz`, `xzdec`, `lzmadec`, `lzmainfo`), configures scripts, installs docs, and includes `tests/tests.cmake` if present.

## Dependencies and Integration
The file depends on CMake 3.20+, GNUInstallDirs, CMake package helpers, C compiler/linker feature checks, gettext/Intl for NLS, Threads, platform SDK headers, and the repository's `src/`, `lib/`, `po/`, `po4a/`, `doc/`, `doxygen/`, and `tests/` trees. It is a peer to the autotools build, so option parity and installed ABI/package metadata are critical integration points.

## Risks and Test Signals
Risk concentrates in option interactions: disabled encoders/decoders must remove dependent formats, Landlock conflicts with sanitizers, Win95 threads plus small mode require constructor support, and symbol versioning must match platform/linker support. The CI matrix exercises many combinations through this file, including Windows, MSYS2, BSD, musl, sanitizers, and feature-disabled builds.
