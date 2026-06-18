## sources/distributed-fs/ceph-client/arch/m68k/fpsp040/sgetem.S

### Purpose
`sgetem.S` implements `FGETEXP` and `FGETMAN` for the FPSP. It extracts the unbiased exponent or normalized mantissa from a double-extended operand, including denormal-specific paths.

### Important APIs, Types, And Functions
Exports are `sgetexp`, `sgetexpd`, `sgetman`, and `sgetmand`. It depends on `nrm_set` for denormal exponent recovery. Internal labels `shft`, `cont`, `upper`, and `shft_end` normalize denormal mantissas for `FGETMAN`.

### Control Flow
`sgetexp` reads the exponent word, strips/adjusts the bias, converts the integer exponent to floating-point, and returns it in `%fp0`. `sgetexpd` first normalizes the denormal operand with `nrm_set`, then returns the recovered exponent. `sgetman` forces the exponent field to the canonical mantissa range while preserving sign, returning a significand in `%fp0`. `sgetmand` shifts denormal mantissa bits until the high bit is set before restoring the canonical exponent and sign.

### State, Persistence, And Dependencies
The routine mutates the operand image at `%a0` when normalizing or setting the mantissa exponent, and returns through `%fp0`. It has no persistent state. It depends on the internal extended layout from `fpsp.h` and shared normalization semantics.

### Integration Points
`tbldo.S` dispatches FGETEXP/FGETMAN normal and denormal cases here; infinities are routed elsewhere as invalid operation. Results continue through standard FPSP result storage and exception handling.

### Risks
Denormal exponent recovery is sensitive to the exact number of left shifts. An off-by-one shift gives an exponent and mantissa that are both plausible but wrong. Sign preservation for `FGETMAN` matters because the mantissa keeps the original sign. Special cases must remain filtered consistently by the dispatch table.

### Test Signals
Test normal powers of two, non-power normal values, positive and negative denormals, signed zeros if dispatched, and values near exponent boundaries. Verify exponent bias removal, mantissa range/sign, and consistency with `x = getman(x) * 2**getexp(x)` for finite nonzero inputs.
