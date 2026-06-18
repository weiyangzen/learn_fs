## sources/distributed-fs/ceph-client/arch/m68k/fpsp040/satanh.S

### Purpose
`satanh.S` implements the FPSP `FATANH` inverse hyperbolic tangent operation. It returns `atanh(X)` in `%fp0` for normal inputs and has a denormal entry that preserves the expected near-zero behavior.

### Important APIs, Types, And Functions
Exports are `satanh` and `satanhd`. It depends on `t_dz`, `t_operr`, `t_frcinx`, `t_extdnrm`, and `slognp1`. The main transformation uses FPU temporaries and stores the `log1p` helper argument through `%a0`.

### Control Flow
`satanhd` uses `t_extdnrm` because `atanh(x) ~= x` for denormal `x`. `satanh` computes `|X|` and branches for boundary cases. For `|X| < 1`, it forms `z = 2X/(1-X)` and calls `slognp1` to compute `log(1+z)`, then halves the result. For `|X| == 1`, it returns divide-by-zero behavior through `t_dz`; for `|X| > 1`, it raises invalid operation via `t_operr`. Normal finite results route through `t_frcinx`.

### State, Persistence, And Dependencies
No persistent state is used. The routine mutates the operand slot at `%a0` for the `slognp1` call and relies on shared FPSR exception helpers for status. It depends on `slognp1` implementing accurate log-one-plus behavior for transformed arguments.

### Integration Points
`tbldo.S` dispatches FATANH normal and denormal cases here. The routine composes with `slogn.S`, `kernel_ex.S`, and `gen_except` for math and exception reporting.

### Risks
Domain boundaries at `-1` and `+1` are critical: equality must produce divide-by-zero, while greater magnitude must produce invalid operation. The formula `2X/(1-X)` magnifies error near `X = 1`, so branch order and exact comparisons matter. Sign handling must be preserved through the log1p call.

### Test Signals
Test denormals, signed zeros, small values, values near `+/-1`, exact `+1` and `-1`, and out-of-domain values. Check odd symmetry, divide-by-zero status at exact endpoints, invalid-operation status outside the domain, and inexact status for normal nonzero results.
