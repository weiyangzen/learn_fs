# sources/distributed-fs/ceph-client/arch/parisc/math-emu/sfmpy.c

Purpose: implements `sgl_fmpy`, single-precision floating-point multiplication.

Important APIs and types: uses `sgl_floating_point` operands, a destination pointer, and FP status. It depends on `Sbit*`, `Slow4`, and `Sgl_*` macros for nibble-wise multiplication and IEEE field manipulation.

Control flow: the routine computes the result sign, handles NaNs, infinities, zero times infinity invalid cases, and zero operands. It calculates the biased destination exponent, normalizes denormals, left-shifts one operand for guard space, then performs a four-bit-at-a-time shift/add multiply. After left-justifying the product, it extracts guard and sticky bits, rounds according to the status rounding mode, and handles overflow, underflow, denormalization, and inexact.

State and persistence: writes one FP result and updates exception flags in `*status`. No static state is used.

Dependencies and integration: called directly by `fpudispatch.c` for `FMPY` and by multi-op emulation in `decode_06` and `decode_26`.

Risks: the product alignment and sticky accumulation depend on exact bit positions. The file has separate pre-round and underflow-round paths that must remain consistent. Invalid `inf * 0` handling must preserve NaN quieting priority.

Test signals: multiply normal, subnormal, zero, infinity, and NaN operands; verify signed zero, overflow largest-versus-infinity selection by rounding mode, underflow tininess, inexact traps, and exact powers of two.
