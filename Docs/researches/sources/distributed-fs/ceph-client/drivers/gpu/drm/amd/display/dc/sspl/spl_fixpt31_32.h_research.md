# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/sspl/spl_fixpt31_32.h

Purpose: this header defines the fixed31_32 numeric type and most inline arithmetic/comparison helpers used throughout SPL. It documents the signed 31-integer/32-fraction fixed-point representation and exposes non-inline math implemented in `spl_fixpt31_32.c`.

Important APIs and types: `struct spl_fixed31_32` wraps a signed 64-bit `value`. Constants include zero, epsilon, half, and one. Inline helpers cover construction from int, negation, absolute value, relational comparisons, min/max/clamp, shifts, add/subtract with overflow assertions, multiplication/division by int, fixed division, power, floor/round/ceil, and truncation. External functions cover fraction construction, multiply/square, reciprocal, sinc/sin/cos, exp/log, hardware packing (`u4d19`, `u3d19`, `u2d19`, `u0d19`, clamped u0 formats, `s4d19`), and reconstruction from packed fields.

Control flow and state: most inline functions are pure value transforms. Overflow and invalid assumptions call `SPL_ASSERT`, which may only warn depending on build configuration. No dynamic state is stored.

Dependencies and integration: it includes `spl_debug.h` and `spl_os_types.h` for assertions, integer types, division helpers, and `SPL_NAMESPACE`. It is included by `dc_spl_types.h`, filter headers, EASF lookup code, and custom-float conversion.

Risks and tests: the header redefines `LLONG_MIN/MAX` defensively, which can interact with compiler/system definitions. Shift helpers depend on sane shift counts and valid ranges. Some documented math functions have restricted domains but the declarations do not encode those constraints. Tests should compile both with and without existing `LLONG_*` definitions, validate inline overflow assertions, and compare all public conversions and rounding helpers with expected bit patterns.
