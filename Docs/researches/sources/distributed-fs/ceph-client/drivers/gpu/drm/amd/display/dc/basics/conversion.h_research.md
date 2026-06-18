# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/basics/conversion.h

Purpose: declares the display core conversion helper API for fixed-point-to-register packing, matrix conversion, ratio reduction, and integer log2. It is the public contract consumed by color management, hardware sequencing, DMUB support, and other display modules that need consistent fixed-point register encodings.

Important APIs and types: exposes `fixed_point_to_int_frac()`, `convert_float_matrix()`, `convert_hw_matrix()`, and `reduce_fraction()` from `conversion.c`. It also provides `static inline unsigned int log_2(unsigned int num)`, a thin wrapper around the kernel `ilog2()` helper. The API is based on `struct fixed31_32` from `include/fixed31_32.h` and standard integer types.

Control flow: the header itself has no runtime state or complex flow. It provides prototypes and one inline forwarding function. The conversion functions operate on caller-provided buffers and are expected to be linked from `conversion.c`.

State and persistence: no state is declared. The functions are stateless utilities; persistence and lifetime are entirely owned by the caller's input/output arrays and scalar pointers.

Dependencies and integration points: depends on `include/fixed31_32.h` and on the kernel environment providing `ilog2()`. It is included by display color-programming modules such as DPP, MPC, DWB, DCE transform, `dc_common.c`, and DMUB service code. Because it centralizes S2D13 and related packing behavior, changes to prototypes or semantics have broad display-pipeline impact.

Risks: the header does not document valid ranges for `integer_bits`, `fractional_bits`, buffer mutability, or denominator constraints for `reduce_fraction()`, so incorrect callers can trigger overflow, truncation, or divide-by-zero in the implementation. `log_2()` inherits `ilog2()` assumptions; callers must avoid passing zero unless their platform definition explicitly handles it.

Test signals: compile coverage should include every caller that includes the header to catch signature drift. Behavioral tests should target the implementation, while API-level checks should verify that all matrix conversion callers pass the expected S2D13 buffer lengths and that `log_2()` is never invoked with invalid zero input.
