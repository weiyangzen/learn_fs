# sources/distributed-fs/ceph-client/include/linux/minmax.h

## Purpose
Defines type-checked min/max/clamp macros, unsigned variants, array min/max, range tests, swap, and unsafe constant-only legacy forms while avoiding multiple evaluation.

## Important APIs/Types
Public macros include `min`, `max`, `umin`, `umax`, `min3`, `max3`, `min_t`, `max_t`, `min_not_zero`, `clamp`, `clamp_t`, `clamp_val`, `min_array`, `max_array`, `in_range`, `swap`, `MIN`, `MAX`, `MIN_T`, and `MAX_T`. Internal helpers check signedness compatibility and use unique temporaries.

## Control Flow
Macros expand to compile-time type checks and conditional comparisons. Clamp bounds a value after checking constant limit ordering. Array helpers reduce non-empty arrays/pointers. `in_range` selects 32-bit or 64-bit arithmetic based on operand sizes.

## State And Persistence
No persistent state. `swap` mutates its two lvalue operands; other macros use scoped temporaries.

## Dependencies And Integration Points
Depends on build-bug, compiler, const, and type helpers. Used broadly across kernel scalar comparisons and bounds logic.

## Risks
Intentional signedness build failures, unsafe `MIN`/`MAX` with side effects, zero-length arrays, misunderstood `in_range` overflow semantics, and bypassed checks with `_t` or `_val` variants.

## Test Signals
Compile-time signedness tests, side-effect single-evaluation tests, clamp ordering checks, array reductions, 32/64-bit range edge cases, and review/sparse coverage for unsafe macros.
