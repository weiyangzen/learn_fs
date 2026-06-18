## sources/distributed-fs/ceph-client/arch/arm/vfp/vfpdouble.c

### Purpose
Implements software emulation for ARM VFP double-precision instructions, including arithmetic, comparisons, conversions, NaN handling, and dispatch from decoded opcodes.

### Important APIs, Types, And Functions
Key functions include `vfp_double_normaliseround`, `vfp_double_fsqrt`, `vfp_compare`, `vfp_double_fcvts`, integer conversion helpers, multiply/add/divide helpers, `vfp_double_multiply`, `vfp_double_add`, `vfp_double_multiply_accumulate`, and exported dispatcher `vfp_double_cpdo`. Dispatch tables `fops_ext[]` and `fops[]` map instruction fields to operations.

### Control Flow
`vfp_double_cpdo()` decodes destination/source registers and opcode class, fetches operands with `vfp_get_double`, and calls the relevant operation. Operations unpack operands, classify special values, handle NaNs and exceptions, perform integer/significand arithmetic, normalize and round, write results through `vfp_put_double` or conversion stores, and return FPSCR exception bits.

### State, Persistence, And Dependencies
Uses transient `struct vfp_double` values and hardware VFP register accessors from `vfphw.S`. Persistent state is FPSCR flags and per-thread saved registers managed by `vfpmodule.c`. It depends on helper math in `vfp.h` and instruction field macros in `vfpinstr.h`.

### Integration Points
Called by `vfp_emulate_instruction()` when a bounced CPDO double instruction requires software handling. It shares sqrt estimate logic with single precision and returns exception masks to `vfp_raise_exceptions`.

### Risks
IEEE corner cases are dense: signaling NaNs, signed zero, denormals, inexact, overflow, underflow, and conversion saturation all need exact FPSCR behavior. Division and sqrt iterative estimates are sensitive to normalization invariants.

### Test Signals
Run double-precision FP conformance suites, NaN propagation tests, conversion boundary tests, and perf/software-emulation counters for bounced instructions.
