## sources/distributed-fs/ceph-client/arch/m68k/fpsp040/ssin.S

### Purpose
`ssin.S` implements `FSIN`, `FCOS`, and `FSINCOS` for the 68040 FPSP. It performs range reduction, selects sine or cosine polynomial approximations, handles tiny and denormal inputs, and returns one or two FPU results depending on the instruction.

### Important APIs, Types, And Functions
Exports are `ssind`, `scosd`, `ssin`, `scos`, `ssincosd`, and `ssincos`. Constants include range bounds, `2/pi`, inverse `2*pi`, split `2*pi` values, and sine/cosine polynomial coefficients `SINA*` and `COSB*`. Scratch aliases include `INARG`, `X`, `RPRIME`, `SPRIME`, `POSNEG1`, `TWOTO63`, `ENDFLAG`, `N`, and `ADJN`. It depends on `PITBL`, `t_extdnrm`, `sto_cos`, and `t_frcinx`.

### Control Flow
Denormal sine returns the input through `t_extdnrm`; denormal cosine returns one through `t_frcinx`. Normal `ssin` and `scos` set an adjustment value (`ADJN`) to distinguish sine from cosine, classify the magnitude, and for ordinary `|X| < 15*pi` reduce `X` to `N*pi/2 + r` with `|r| <= pi/4`. The quadrant determines sign and whether to evaluate the sine odd polynomial or cosine even polynomial. Very tiny sine returns `X`, tiny cosine returns `1`, and larger inputs go through `REDUCEX`, which computes `X rem 2*pi` using split constants and loops until the reduced argument is in range. `ssincos` computes both polynomials and uses quadrant parity to store sine in `%fp0` and cosine through `sto_cos`/`%fp1`.

### State, Persistence, And Dependencies
The routine uses FPSP scratch operands, FPU registers, and sometimes the operand slot at `%a0`; no persistent state is stored. It depends on external `PITBL` data for high-quality range reduction and on `sto_cos` to place the second result for FSINCOS.

### Integration Points
`tbldo.S` dispatches FSIN, FCOS, and FSINCOS normal and denormal opcodes here. Exception helpers record inexact/denormal status, and the common FPSP completion path stores results or reports exceptions.

### Risks
Argument reduction dominates correctness. Large inputs require split-constant reduction; small mistakes produce wrong quadrants and signs even when polynomial code is correct. FSINCOS has two result registers and sign rules, so it is more integration-sensitive than single-result sine/cosine. Tiny inputs must return exactly `x` or `1` with appropriate status, not reduced polynomial noise.

### Test Signals
Test signed zeros, denormals, tiny magnitudes, quadrant boundaries, multiples of `pi/2`, values near `15*pi`, large finite arguments requiring `REDUCEX`, and FSINCOS destination handling. Verify sine/cosine signs by quadrant, identity consistency, inexact status, and ulp accuracy against a high-precision range-reduction oracle.
