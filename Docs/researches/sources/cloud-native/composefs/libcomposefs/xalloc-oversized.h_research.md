# sources/cloud-native/composefs/libcomposefs/xalloc-oversized.h

## Purpose
This gnulib header provides `xalloc_oversized(n, s)`, a macro that detects multiplication sizes too large for reliable allocation.

## Important APIs, Types, And Functions
`__xalloc_oversized` implements the portable division check. `xalloc_oversized` selects compiler builtins for GCC configurations where they are safe, otherwise uses the portable macro.

## Control Flow
Callers evaluate the macro before allocating arrays. `hash.c` uses it while computing bucket array sizes.

## State And Persistence
No state. It only prevents invalid allocation size calculations.

## Dependencies And Integration Points
Includes `stddef.h` and `stdint.h`. Integrated by `hash.c`.

## Risks
It is macro-based, so callers must pass side-effect-free arguments as documented. Incorrect compiler feature conditions could misdetect overflow on unusual targets.

## Test Signals
No direct tests. Indirectly exercised by hash initialization/rehash under writer/loader hash-table usage.
