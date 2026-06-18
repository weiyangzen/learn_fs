## sources/distributed-fs/ceph-client/arch/m68k/fpsp040/slogn.S

### Purpose
`slogn.S` implements natural logarithm (`FLOGN`) and log-one-plus (`FLOGNP1`) for the FPSP. It provides normal and denormal entries and uses table reduction plus polynomial approximation to meet the documented monotonicity and accuracy targets.

### Important APIs, Types, And Functions
Exports are `slognd`, `slogn`, `slognp1d`, and `slognp1`. Constants include range bounds, `LOGOF2`, polynomial coefficients `LOGA*` and `LOGB*`, `TWO`, `LTHOLD`, and a 64-entry `LOGTBL` containing precomputed reciprocal/significand and log values. Scratch aliases include `ADJK`, `X`, `F`, `KLOG2`, and `SAVEU`. Dependencies are `t_extdnrm`, `t_operr`, and `t_dz`; normal exits use `t_frcinx`.

### Control Flow
`slognd` normalizes denormal input and adjusts the effective exponent before using the main log logic. `slogn` rejects negatives, handles zero through divide-by-zero, and for `|X-1| < 1/16` uses a near-one odd polynomial in `u = 2(X-1)/(X+1)`. Otherwise it decomposes `X = 2**k * Y`, chooses a table value `F`, computes `u = (Y-F)/F`, evaluates a polynomial approximation to `log(1+u)`, and reconstructs `k*log(2) + log(F) + poly`. `slognp1` uses a cancellation-aware path for small `X`, otherwise forms `1+X` and uses the same decomposition, with special cases for `X = -1`, `X < -1`, `X = 0`, and tiny values.

### State, Persistence, And Dependencies
The routine mutates FPSP scratch float slots and `%a0` operand storage but does not persist state. It depends on exact exponent/significand decoding, table indexing, and exception helpers. Several paths temporarily adjust `ADJK` to account for denormal normalization or log1p reconstruction.

### Integration Points
`slog2.S` calls `slogn`/`slognd` for base conversions, `satanh.S` calls `slognp1`, and `tbldo.S` dispatches FLOGN/FLOGNP1 here. Results and exceptions feed the shared FPSP reporting machinery.

### Risks
Log near one and log1p near zero are cancellation-sensitive; using the general decomposition for those cases would lose precision. Domain boundary handling is subtle: `log(0)` is divide-by-zero, `log(negative)` is invalid operation, `log1p(-1)` is divide-by-zero, and `log1p(x<-1)` is invalid. Table index or exponent adjustment mistakes shift the result by multiples of `log(2)`.

### Test Signals
Test `log(1)`, values very close to 1, powers of two, denormals, zero, negatives, large/small normals, `log1p(0)`, tiny `log1p` inputs, `log1p(-1)`, and `log1p` just below `-1`. Check monotonicity, domain exception class, inexact status, and ulp accuracy.
