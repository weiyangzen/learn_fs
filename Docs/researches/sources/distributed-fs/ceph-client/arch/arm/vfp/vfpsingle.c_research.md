## sources/distributed-fs/ceph-client/arch/arm/vfp/vfpsingle.c

### Purpose
Implements software emulation for ARM VFP single-precision instructions, including arithmetic, comparisons, conversions, square root, NaN handling, and opcode dispatch.

### Important APIs, Types, And Functions
Key functions include `vfp_single_normaliseround`, `vfp_estimate_sqrt_significand`, `vfp_single_fsqrt`, `vfp_compare`, conversion helpers, `vfp_single_multiply`, `vfp_single_add`, `vfp_single_multiply_accumulate`, arithmetic operations `fmac/fnmac/fmsc/fnmsc/fmul/fnmul/fadd/fsub/fdiv`, and dispatcher `vfp_single_cpdo`. Tables `fops_ext[]` and `fops[]` map opcodes.

### Control Flow
`vfp_single_cpdo()` extracts single register operands, fetches values, dispatches by opcode, and writes results. Arithmetic paths unpack IEEE single values, handle special classes, perform significand math, normalize/round, and return exception flags. Conversion paths translate between single, double, signed integers, and unsigned integers with FPSCR-controlled rounding.

### State, Persistence, And Dependencies
Uses transient `struct vfp_single` values and accesses actual VFP registers through `vfp_get_float`/`vfp_put_float`. Persistent state is FPSCR flags and the current thread's VFP register image. Depends on `vfp.h` and `vfpinstr.h`.

### Integration Points
Called by `vfp_emulate_instruction()` for bounced single-precision CPDO instructions; shares exception propagation with `vfpmodule.c` and double conversion with `vfpdouble.c`.

### Risks
Single precision still has complex IEEE behavior around denormals, signed zero, NaNs, saturation, and exact inexact/underflow flag timing. Register extraction differs from double register encodings.

### Test Signals
Run single-precision FP conformance vectors, conversion boundary cases, denormal/NaN tests, and tests that force software emulation rather than hardware completion.
