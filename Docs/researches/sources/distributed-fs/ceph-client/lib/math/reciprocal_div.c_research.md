# sources/distributed-fs/ceph-client/lib/math/reciprocal_div.c

Purpose: Computes reciprocal multiplier descriptors used to replace repeated integer division by multiply/shift sequences.

Important APIs/types/functions: Exports `reciprocal_value(u32 d)` and `reciprocal_value_adv(u32 d, u8 prec)`, returning `struct reciprocal_value` and `struct reciprocal_value_adv`.

Control flow: Basic path computes ceil log2, multiplier `m`, and two shifts from the divisor. Advanced path computes low/high multiplier bounds at requested precision, shifts them down until bounds would collapse, and records whether the multiplier is wider than 32 bits.

State and persistence: Stateless.

Dependencies/integration: Core math object used by networking and performance-sensitive code that precomputes division constants.

Risks: Divisor assumptions are enforced mostly by callers; advanced path warns for `l == 32` because `1ULL << (32 + l)` would overflow.

Test signals: No local KUnit here; correctness is normally tested by reciprocal-div users and header inline division helpers.
