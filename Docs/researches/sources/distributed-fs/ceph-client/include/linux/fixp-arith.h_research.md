# sources/distributed-fs/ceph-client/include/linux/fixp-arith.h

## Purpose
This header provides simple fixed-point trigonometry and interpolation helpers for kernel code that cannot use floating point.

## APIs, types, and control flow
`sin_table[]` stores sine values for 0..90 degrees scaled to signed 32-bit range. `__fixp_sin32()` folds degrees into quadrants and sign; `fixp_sin32()` normalizes arbitrary signed degrees into 0..359. Cosine is `fixp_sin32(v + 90)`, and 16-bit variants right-shift the 32-bit result. `fixp_sin32_rad(radians, twopi)` maps caller-defined radian units to degrees, interpolates between adjacent table entries, and uses `div_s64()` for precision. `fixp_linear_interpolate()` computes a y value from two points.

## State and dependencies
The table is static const. There is no mutable state. Dependencies are `BUG_ON`, `div_s64`, and integer types. `fixp_sin32_rad()` hard-stops with `BUG_ON(twopi > 1 << 18)` to avoid overflow.

## Integration, risks, and tests
This is useful for drivers needing approximate geometry without FPU use. Risks include kernel BUG from unvalidated `twopi`, interpolation overflow for large deltas, precision limits from degree table spacing, and division by zero if `twopi < 360` makes `dx` zero. Tests should compare known quadrants, negative angles, wraparound, radian interpolation, boundary `twopi`, and linear interpolation degenerate cases.
