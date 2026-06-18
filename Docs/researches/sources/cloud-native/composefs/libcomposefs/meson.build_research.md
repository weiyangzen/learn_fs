# sources/cloud-native/composefs/libcomposefs/meson.build

## Purpose
This Meson file builds libcomposefs and its small internal static utility library, declares source membership, applies composefs hash/visibility flags, links dependencies, generates pkg-config metadata, and installs public headers.

## Important APIs, Types, And Functions
It defines `internal_source_files`, `libcomposefs_internal`, `source_files`, `libcomposefs`, `pkg.generate`, and `install_headers`. Installed headers are `lcfs-writer.h`, `lcfs-erofs.h`, and `lcfs-mount.h`.

## Control Flow
Meson first builds `composefs-internal` from utils, then builds both shared and static `composefs` libraries from core sources, linking libcrypto and the internal library. It passes `composefs_hash_cflags` and hidden visibility flags from the top-level build.

## State And Persistence
Build outputs are libraries, pkg-config files, and installed headers. It does not generate runtime state.

## Dependencies And Integration Points
Consumes `config_inc`, `composefs_hash_cflags`, `hidden_visibility_cflags`, `libcrypto_dep`, and version variables defined in top-level `meson.build`.

## Risks
Adding a new public API source or header requires updating this file. Hash compile flags must remain consistent with the bundled gnulib implementation.

## Test Signals
Every Meson test depends on this target. ABI exposure is checked by compiling `tests/test-lcfs.c` against the library.
