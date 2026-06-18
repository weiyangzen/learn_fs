## sources/distributed-fs/ceph-client/include/linux/cordic.h

Purpose: This header declares a fixed-point CORDIC helper for computing sine/cosine-like I/Q coordinates without floating point.

Important APIs, types, and functions: Constants include `CORDIC_ANGLE_GEN`, `CORDIC_PRECISION_SHIFT` at 16, and `CORDIC_NUM_ITER`. `CORDIC_FIXED(X)` converts an integer to fixed point, while `CORDIC_FLOAT(X)` rounds fixed point back toward integer representation. `struct cordic_iq` holds signed 32-bit in-phase (`i`) and quadrature (`q`) coordinates. `cordic_calc_iq(s32 theta)` computes I/Q for an angle in degrees.

Control flow: Implementation code normalizes input angle to the supported range and iteratively applies CORDIC rotations for `CORDIC_NUM_ITER` steps. The header exposes the fixed-point scaling contract.

State and persistence: No state is stored. Results are pure values derived from the input angle.

Dependencies and integration points: It depends on `linux/types.h` and is used by drivers needing trigonometric values in kernel space, especially wireless/radio code where floating point is unavailable.

Risks and test signals: Risks include fixed-point overflow, rounding surprises in `CORDIC_FLOAT`, angle normalization errors outside -180..180 degrees, and precision regressions from constant changes. Test signals include known-angle checks for 0, 90, 180, -90 degrees; out-of-range angle normalization; and comparison against high-precision reference values within expected error.
