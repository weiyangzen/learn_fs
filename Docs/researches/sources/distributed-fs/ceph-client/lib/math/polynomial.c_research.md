# sources/distributed-fs/ceph-client/lib/math/polynomial.c

Purpose: Evaluates integer polynomials with redistributed factors to preserve precision and avoid overflow.

Important APIs/types/functions: Exports GPL-only `polynomial_calc(const struct polynomial *poly, long data)`, consuming `struct polynomial` and `struct polynomial_term` from `linux/polynomial.h`.

Control flow: Iterates terms until a degree-zero term is processed, repeatedly applies `mult_frac(tmp, data, divider)` per degree, divides by each term’s leftover divider, accumulates, then applies `total_divider` or 1 if zero.

State and persistence: Stateless; polynomial descriptors are caller-owned constants/data.

Dependencies/integration: Optional `CONFIG_POLYNOMIAL` object for sensor/driver calibration formulas.

Risks: Caller must supply terms in descending degree ending with degree 0 and choose factors that prevent overflow; no validation guards malformed descriptors.

Test signals: No local KUnit in this subset; comments include a temperature/PVT conversion example useful for consumer tests.
