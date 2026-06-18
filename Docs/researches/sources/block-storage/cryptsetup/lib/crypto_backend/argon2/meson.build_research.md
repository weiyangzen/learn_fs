# File Research: sources/block-storage/cryptsetup/lib/crypto_backend/argon2/meson.build

## Purpose
Meson build definition for bundled Argon2.

## Key Content
Defines `libargon2_sources` with BLAKE2b, Argon2 API, core, encoding, and thread sources. Adds `opt.c` when `use_internal_sse_argon2` is enabled, otherwise `ref.c`. Builds a static `argon2` library with C89 and optimization level 3, includes `blake2`, and links thread dependency.

## Dependencies and Coupling
Meson counterpart to `argon2/Makemodule.am`.

## Invariants and Risks
Only C source files are listed; headers are included transitively. Meson and Autotools source selection must stay equivalent.
