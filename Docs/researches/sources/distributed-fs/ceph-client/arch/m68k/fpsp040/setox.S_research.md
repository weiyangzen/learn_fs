## sources/distributed-fs/ceph-client/arch/m68k/fpsp040/setox.S

### Purpose
`setox.S` implements `FETOX` (`exp(x)`) and `FETOXM1` (`exp(x)-1`) for the 68040 FPSP. It provides normal and denormal entries and is a shared backend for other hyperbolic functions.

### Important APIs, Types, And Functions
Exports are `setoxd`, `setox`, `setoxm1d`, and `setoxm1`. The file defines polynomial coefficients for exp and expm1 (`EXPA*`, `EM1A*`, `EM1B*`), scaling constants (`L2`, `TWO140`, `TWON140`), overflow/underflow sentinels (`HUGE`, `TINY`), and a 64-entry `EXPTBL` for table-based reconstruction. Scratch aliases include `ADJFLAG`, `SCALE`, `ADJSCALE`, `SC`, and `ONEBYSC`. It depends on `t_extdnrm`, `t_unfl`, and `t_ovfl`; normal exits use `t_frcinx`.

### Control Flow
`setoxd` handles denormal input by returning `1 + x`-like behavior with forced inexact. `setox` classifies input into small, main, and big ranges. The main path computes a table index `N ~= round(x * 64/log2)`, splits it into scale and residual parts, evaluates a polynomial approximation of the residual exponential, and multiplies by the tabulated scale. Large positive/negative values route to overflow or underflow helpers. `setoxm1d` returns denormal input through `t_extdnrm`; `setoxm1` uses specialized small-input and main paths to preserve cancellation-sensitive `exp(x)-1`, with fallback to the exp path for large values.

### State, Persistence, And Dependencies
The routines use FPU registers, `%a0` operand storage, and FPSP scratch fields, but no persistent state. They depend on exact table indexing, FPCR control restoration, and shared exception helpers for final status.

### Integration Points
`tbldo.S` dispatches FETOX and FETOXM1 here. `scosh.S`, `stanh.S`, and other hyperbolic routines call `setox` or `setoxm1` as helper functions. Exception status flows through `kernel_ex.S` and `gen_except`.

### Risks
The table/polynomial reconstruction is numerically delicate: wrong `N`, wrong scale split, or wrong residual sign changes results over broad ranges. `exp(x)-1` needs special small-input handling; replacing it with `exp(x)-1` directly loses precision near zero. Overflow/underflow thresholds must match 68881-compatible behavior and rounding modes.

### Test Signals
Test exp and expm1 for denormals, signed zeros, tiny positive/negative values, moderate values, table-boundary inputs, and near overflow/underflow limits. Compare against high-precision references and verify monotonicity, exact `expm1(0)`, inexact status, underflow for large negative inputs, and overflow for large positive inputs.
