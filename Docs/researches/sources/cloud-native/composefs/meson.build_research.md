# sources/cloud-native/composefs/meson.build

## Purpose
The top-level Meson build defines the composefs project, compiler warnings, dependencies, feature probes, generated config header, subdirectories, library versioning, and subproject dependency export.

## Important APIs, Types, And Functions
It declares project version `1.0.8`, libcomposefs ABI version `1.4.0`, `composefs_hash_cflags`, dependency probes for fuse3 and libcrypto, `configuration_data` entries, visibility flags, `config_h`, `config_inc`, subdirs, and `composefs_dep`.

## Control Flow
Meson checks compiler flags, headers, required libc functions, optional endian/reallocarray/mount API features, visibility support, and optional dependencies. It configures `config.h`, enters `libcomposefs`, `tools`, `tests`, and conditionally `man`.

## State And Persistence
Build configuration state is emitted to `config.h`; build outputs include libraries, tools, tests, and optional man pages.

## Dependencies And Integration Points
This file coordinates the whole composefs source tree. `config.h` macros control OpenSSL use, FUSE support, endian includes, mount API paths, and symbol visibility.

## Risks
Feature detection affects runtime code paths in mount and fsverity logic. Warning flags are strict and may break builds on new compilers. `libcrypto_dep` is not feature-optional in this file even though fsverity has fallback SHA-256 code.

## Test Signals
All Meson tests rely on this configuration. Valgrind setup in tests depends on generated build targets.
