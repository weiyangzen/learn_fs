# sources/distributed-fs/ceph-client/arch/m68k/fpsp040/stanh.S

Purpose: implements FPSP `ftanh`, with `stanh` for normalized finite inputs and `stanhd` for denormalized inputs. The routine computes `tanh(X)` in `%fp0` while preserving sign and exception behavior expected by 68881/68882-compatible software.

Important APIs/types/functions: exported labels are `stanh` and `stanhd`. It uses scratch aliases `X`, `SGN`, and `V`, range table `BOUNDS1` for `2^-40` and `(5/2)*log(2)`, and calls shared exponential helpers `setoxm1` and `setox`. Common exits are `t_extdnrm` and `t_frcinx`.

Control flow: denormal input jumps to `t_extdnrm`. For `2^-40 < |X| < (5/2)*log(2)`, the routine computes `Y=2|X|`, `Z=expm1(Y)`, and returns `sign(X)*Z/(Z+2)`. For larger inputs below `50*log(2)`, it computes `exp(2|X|)` and returns `sign - sign*2/(exp(Y)+1)`. For huge inputs it returns `sign - sign*epsilon`; for tiny normalized inputs it returns the source value.

State and persistence: no persistent state. It stores a copy of the input in FPSP scratch memory, keeps the sign in `SGN`, and uses `%d1` as the saved FPCR restored before the final visible arithmetic operation.

Dependencies/integration: depends on `fpsp.h`, `setox`, `setoxm1`, `t_frcinx`, and `t_extdnrm`. It is selected by `tbldo.S` for normal and denormal `ftanh` source classes.

Risks: the code manipulates the extended exponent directly to form `2|X|`; malformed scratch state or unexpected source format would be dangerous. Boundary behavior around `2^-40`, `(5/2)*log(2)`, and `50*log(2)` determines whether inexact and saturation behavior match hardware expectations.

Test signals: verify denormal and tiny inputs return `X`, moderate values use the expm1 formula, large positive/negative values approach signed one without premature overflow, threshold equality cases, signed zero behavior, FPCR rounding modes, and inexact/accrued flags via `t_frcinx`.
