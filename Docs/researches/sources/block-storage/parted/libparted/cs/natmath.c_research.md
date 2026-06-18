# File Research: sources/block-storage/parted/libparted/cs/natmath.c

This file implements natural-number and modular arithmetic helpers for libparted alignment constraints.

Core model:
- A `PedAlignment` represents sectors satisfying `sector = offset + X * grain_size`.
- `ped_alignment_any` is offset `0`, grain size `1`.
- `ped_alignment_none` is `NULL`.
- Grain size `0` represents a single exact sector at `offset`.

Arithmetic helpers:
- `abs_mod()` implements mathematically positive modulo for negative values.
- `ped_round_down_to()`, `ped_round_up_to()`, and `ped_round_to_nearest()` round sectors to grain multiples.
- `ped_greatest_common_divisor()` implements Euclid’s algorithm.

Alignment lifecycle:
- `ped_alignment_init()` initializes preallocated storage, normalizing offset modulo grain size when grain size is nonzero.
- `ped_alignment_new()` allocates an alignment.
- `ped_alignment_destroy()` frees it.
- `ped_alignment_duplicate()` copies it.

Intersection:
- `extended_euclid()` computes GCD plus coefficients.
- `ped_alignment_intersect()` computes an alignment satisfying two input congruence constraints.
- The implementation uses the Chinese Remainder Theorem idea:
  - New grain size is the least common multiple.
  - New offset is solved via extended Euclid.
  - Inconsistent constraints return `NULL`.

Alignment operations:
- `_closest_inside_geometry()` adjusts aligned sectors into a geometry range.
- `ped_alignment_align_up()` returns the nearest aligned sector at or after a target, constrained by geometry if supplied.
- `ped_alignment_align_down()` returns the nearest aligned sector at or before a target.
- `ped_alignment_align_nearest()` chooses the closer up/down aligned sector.
- `ped_alignment_is_aligned()` checks both geometry membership and congruence/exact-sector matching.

Research notes:
- This is the mathematical foundation for `constraint.c`; partition start/end placement depends on these congruence operations.
- Exact-sector alignments use `grain_size == 0`, so code must avoid treating zero grain size as a normal modulo divisor.
