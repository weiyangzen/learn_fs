# sources/distributed-fs/ceph-client/lib/math/rational.c

Purpose: Computes the best bounded rational approximation of an input fraction.

Important APIs/types/functions: Exports `rational_best_approximation(given_numerator, given_denominator, max_numerator, max_denominator, best_numerator, best_denominator)`.

Control flow: Uses continued fractions. It repeatedly derives the next Euclidean quotient, builds convergents, and when the next convergent exceeds numerator or denominator limits, chooses between the previous convergent and a final semi-convergent based on closeness.

State and persistence: Stateless; outputs are written through caller pointers.

Dependencies/integration: Optional `CONFIG_RATIONAL`, used by drivers configuring clocks/PLLs or fixed-ratio hardware registers.

Risks: Assumes nonzero denominator for meaningful input; multiplication in convergent updates can overflow unsigned long for extreme values.

Test signals: `tests/rational_kunit.c` covers exact, bounded, near-zero, numerator-limited, denominator-limited, convergent, and semi-convergent cases.
