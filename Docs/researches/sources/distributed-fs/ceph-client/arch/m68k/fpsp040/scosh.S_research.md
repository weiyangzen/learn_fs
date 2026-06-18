## sources/distributed-fs/ceph-client/arch/m68k/fpsp040/scosh.S

### Purpose
`scosh.S` implements the FPSP `FCOSH` hyperbolic cosine operation. It computes `cosh(X)` for normal and denormal double-extended inputs and returns the result in `%fp0`.

### Important APIs, Types, And Functions
Exports are `scosh` and `scoshd`. Constants include split log2 values `T1`/`T2` and `TWO16380` for large-result reconstruction. It depends on `t_ovfl`, `t_frcinx`, and `setox`.

### Control Flow
`scoshd` returns approximately `1` for denormal input via `t_frcinx`. `scosh` takes `|X|`, checks magnitude, and for ordinary inputs calls `setox` to compute `exp(|X|)`, then returns `(exp(|X|) + 1/exp(|X|))/2`. For larger but not overflowing inputs it computes a scaled exponential form using split constants to avoid premature overflow. Huge inputs branch to `t_ovfl`.

### State, Persistence, And Dependencies
The routine uses `%fp0`/`%fp1`, the operand slot at `%a0` for `setox`, and no persistent state. It relies on `setox.S` for exponential approximation and on exception helpers for inexact/overflow reporting.

### Integration Points
`tbldo.S` dispatches FCOSH normal and denormal cases here. The routine composes with `setox` and the standard exception generation path.

### Risks
Overflow threshold handling is the main risk. Cosh is always positive and grows quickly, so using the ordinary formula beyond its safe range can overflow intermediate values before the final result should overflow. Denormal and tiny inputs should return near 1 with inexact status, not the input.

### Test Signals
Test denormal inputs, zero, small finite values, moderate values, near-overflow large values, and huge values. Check positive-only result sign, monotonicity in `|X|`, inexact status, and overflow status at the documented threshold.
