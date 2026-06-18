# sources/distributed-fs/ceph-client/arch/m68k/fpsp040/stan.S

Purpose: implements FPSP `ftan`, with `stan` computing tangent for normalized finite operands and `stand` forwarding denormal handling. It provides both the fast table-reduction path for common inputs and a multi-iteration high-magnitude argument reduction path.

Important APIs/types/functions: exported labels are `stan`, `stand`, and the shared `PITBL` table of split `N*pi/2` values for `-32 <= N <= 32`. Local constants include polynomial coefficients `TANP1..TANP3` and `TANQ1..TANQ4`, `TWOBYPI`, `INVTWOPI`, and split `2*pi` constants. Common exits are `t_extdnrm` and `t_frcinx`.

Control flow: `stand` branches to `t_extdnrm`. `stan` loads `%fp0`, forms a compact absolute magnitude, returns `X` for `|X| < 2^-40`, uses `PITBL` when `|X| < 15*pi`, and otherwise enters `REDUCEX`. The fast path converts `X*2/pi` to integer `N`, subtracts split `N*pi/2`, derives the odd/even quadrant bit, and evaluates `tan(r)` as `U/V` for even quadrants or `-V/U` for odd quadrants. The slow path repeatedly reduces large arguments using scaled `2/pi`, scaled split `pi/2`, and a compensated `(R,r)` remainder until the fast polynomial can be used.

State and persistence: no persistent state. Uses FPSP scratch offsets `INARG`, `TWOTO63`, `ENDFLAG`, and `N`; saves `%fp2-%fp5` and `%d2` during slow reduction. `%d1` carries the user FPCR value restored before the final floating operation.

Dependencies/integration: included by the FPSP unimplemented-instruction flow and selected from `tbldo.S` for `ftan`. It depends on `fpsp.h` scratch offsets and exception exits. The polynomial result is left in `%fp0` and final exception status is delegated to `t_frcinx`.

Risks: argument reduction is precision-sensitive, especially the table address calculation, the odd-quadrant bit derived from the rotated integer multiple, and the special pre-reduction for the largest compact exponent. Any corruption of `%fp0/%fp1` as a compensated remainder pair in `REDUCEX` can produce quadrant errors. The slow path has many scratch-register assumptions.

Test signals: cover tiny inputs, denormal inputs, all signs, values around multiples of `pi/2`, near `15*pi`, very large finite operands, odd/even quadrant transitions, FPCR rounding modes, inexact flag propagation, and monotonicity/ULP checks near zeros and vertical asymptotes.
