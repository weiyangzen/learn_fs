## sources/distributed-fs/ceph-client/arch/m68k/fpsp040/sacos.S

### Purpose
`sacos.S` implements the 68040 FPSP `FACOS` transcendental operation. It computes arccosine for a double-extended input at `%a0`, returning the result in `%fp0`, with a separate denormal-input entry.

### Important APIs, Types, And Functions
Exports are `sacos` and `sacosd`. The file defines `PI` and `PIBY2` constants and depends on `t_operr`, `t_frcinx`, and `satan`. The caller supplies the input in FPSP extended format at `%a0`; `%d1` carries the user FPCR mode/precision as used by the surrounding transcendental framework.

### Control Flow
`sacosd` treats denormal input as an inexact arccosine of zero and returns `pi/2` through `t_frcinx`. `sacos` loads `X`, checks `|X|` against 1, and for the normal domain `|X| < 1` computes `z = (1 - X) / (1 + X)`, then calls `satan` on `sqrt(z)` and doubles the arctangent result. For `|X| == 1`, it returns zero for `+1` and `pi` for `-1`; for `|X| > 1`, it branches to `t_operr` for invalid operation.

### State, Persistence, And Dependencies
The routine uses `%fp0` and `%fp1`, temporarily overwrites the input slot at `%a0` before calling `satan`, and may save/restore FPCR state around the helper call. No persistent state is kept. It depends on `satan` accepting its input at `%a0` and on `kernel_ex.S` exception helpers setting FPSR state.

### Integration Points
`tbldo.S` dispatches normal and denormal `FACOS` opcodes to `sacos`/`sacosd`, while infinity and NaN special cases are generally filtered before entry. Results and exception bits flow back through `t_frcinx`/`t_operr` and then `gen_except`.

### Risks
The transformation `(1-X)/(1+X)` is sensitive near `X = -1` because the denominator approaches zero; boundary classification must be exact. The helper call changes FPCR behavior, so failure to restore user exception controls would leak state into later arithmetic. Domain errors for `|X| > 1` must generate invalid operation rather than returning a numeric value.

### Test Signals
Tests should cover `acos(+0)`, `acos(-0)`, `acos(+1)`, `acos(-1)`, values just inside and just outside `[-1,1]`, denormal inputs, and all rounding modes. Compare monotonicity and ulp error against a high-precision oracle, and verify invalid-operation status for out-of-domain inputs.
