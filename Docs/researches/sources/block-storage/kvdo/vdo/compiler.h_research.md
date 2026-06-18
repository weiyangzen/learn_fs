# File Research: sources/block-storage/kvdo/vdo/compiler.h

## Purpose

Provides compiler convenience macros used by the kvdo source.

## Contents

- Includes Linux compiler and READ/WRITE-once support headers.
- Defines `const_container_of()` for deriving a const parent pointer from a const member pointer.
- Defines `INLINE` as `__attribute__((always_inline)) inline`.
- Defines `__STRING(x)` as a simple stringification macro.

## Notable Details

`INLINE` exists because plain `inline` depends on optimization settings.
