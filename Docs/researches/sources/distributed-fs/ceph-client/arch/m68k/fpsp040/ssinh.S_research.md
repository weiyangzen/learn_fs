# sources/distributed-fs/ceph-client/arch/m68k/fpsp040/ssinh.S

Purpose: implements the Motorola 68040 FPSP software routine for `fsinh`, with `ssinh` handling finite normalized inputs and `ssinhd` handling denormalized inputs. The routine computes `sinh(X)` in `%fp0` from the extended-precision operand pointed to by `%a0`, preserving the FPSP contract that common exception transfer code handles final inexact/overflow posting.

Important APIs/types/functions: exported labels are `ssinh` and `ssinhd`. `ssinhd` immediately branches to `t_extdnrm`, because denormalized `sinh(x)` is treated as `x` with denormal/inexact handling delegated. `ssinh` calls shared exponential helpers `setoxm1` for the normal range and `setox` for the large-but-not-overflow range, then exits through `t_frcinx` or `t_ovfl`. Constants `T1` and `T2` split `16381*log(2)` into leading/trailing terms for accurate large-argument reduction.

Control flow: `ssinh` loads the input, compacts the sign/exponent/high mantissa into `%d0`, and compares `|X|` against two thresholds. For `|X| <= 16380*log(2)`, it computes `z = expm1(|X|)` and returns `sign(X) * 0.5 * (z + z/(1+z))`. For `16380*log(2) < |X| <= 16480*log(2)`, it subtracts split `16381*log(2)` and computes `sign(X)*2^16380*exp(reduced)`. Beyond that it branches to `t_ovfl`.

State and persistence: no persistent state is owned. The routine uses `%a0` as the operand/scratch pointer, `%a1` to preserve the compacted original sign, `%d1` for the saved user FPCR value, the FPU stack for temporary extended values, and the FPSP scratch frame indirectly through `setox`/`setoxm1`.

Dependencies/integration: depends on `fpsp.h` frame/register offsets and on common FPSP routines `setox`, `setoxm1`, `t_frcinx`, `t_ovfl`, and `t_extdnrm`. It is dispatched by `tbldo.S` for `fsinh` normal and denormal source tags.

Risks: correctness relies on exact threshold constants, split-log constants, and restoring the user's FPCR only for the final operation that should raise user-visible exceptions. The routine stores `%fp0` back through `%a0` before calling exponential helpers; callers must provide a valid FPSP scratch operand area. Boundary values around the two large-argument thresholds are the highest-risk cases.

Test signals: exercise denormal input, signed zero, small finite values, normal positive/negative ranges, values just below and above `16380*log(2)`, values near `16480*log(2)`, overflow sign propagation, and FPCR rounding/inexact behavior through `t_frcinx`.
