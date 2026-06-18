## sources/distributed-fs/ceph-client/arch/m68k/fpsp040/slog2.S

### Purpose
`slog2.S` implements base-10 and base-2 logarithm wrappers for the FPSP. It delegates natural logarithm calculation to `slogn`/`slognd`, applies reciprocal-log constants, and includes an optimized exact path for powers of two in `FLOG2`.

### Important APIs, Types, And Functions
Exports are `slog10d`, `slog10`, `slog2d`, and `slog2`. Constants are `INV_L10` and `INV_L2`. It depends on `t_frcinx`, `t_operr`, `slogn`, and `slognd`. Local labels include `continue` and `invalid`.

### Control Flow
Each entry first rejects negative inputs with `t_operr`, then sets FPCR behavior for the helper calculation. `slog10d`/`slog10` compute natural log and multiply by `1/log(10)`. `slog2d` computes natural log and multiplies by `1/log(2)`. `slog2` additionally detects exact powers of two by examining the significand; for those inputs it returns the unbiased exponent directly as an exact floating value, otherwise it follows the natural-log path.

### State, Persistence, And Dependencies
The routine saves/restores FPCR around helper calls and returns `%fp0`. It has no persistent state. It depends on `slogn.S` for domain handling of zero and positive values, and on exact extended operand representation for power-of-two detection.

### Integration Points
`tbldo.S` dispatches FLOG10 and FLOG2 normal/denormal cases here, though symbol aliases in the table may use wrapper names for shared implementations. Exception flow is handled by `t_operr`, `t_frcinx`, and `gen_except`.

### Risks
Negative input detection must preserve `-0` behavior expected by lower-level log code. Exact power-of-two optimization must only trigger when all fraction bits except the integer bit are clear; otherwise it can skip inexact status and return a wrong integer log. FPCR restoration is necessary so helper default precision does not leak.

### Test Signals
Test positive powers of two, non-powers near powers of two, denormal positives, zero, negative values, and large/small normals. Verify exact integer results for powers of two, invalid operation for negatives, divide-by-zero behavior through `slogn` for zero, and correct scaling for log10/log2 against high-precision references.
