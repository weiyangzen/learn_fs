# sources/distributed-fs/ceph-client/include/linux/polynomial.h

Purpose: declares a small polynomial evaluator interface for drivers that model hardware calibration or conversion curves.

Important APIs and types: `struct polynomial_term` stores degree, coefficient, per-degree divider, and leftover divider. `struct polynomial` stores a total divider and flexible array of terms, with the last term required to have degree 0. `polynomial_calc()` evaluates the polynomial for an input value.

Control flow: callers define a static term array ordered for evaluation, terminate it with degree 0, and pass input data to `polynomial_calc()` to receive a scaled integer result.

State and persistence: no mutable state is held; descriptors are caller-owned and may be static platform/calibration data.

Dependencies and integration points: standalone Linux header using integer types; intended for sensor, power, or platform drivers needing integer polynomial conversion without floating point.

Risks and test signals: risks include missing degree-0 terminator, overflow from high-degree/coefficient combinations, incorrect divider distribution, and sign/rounding surprises. Test known calibration vectors, boundary values, negative coefficients, divider leftovers, and static descriptor termination.
