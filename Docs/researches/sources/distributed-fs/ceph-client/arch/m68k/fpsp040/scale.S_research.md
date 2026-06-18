## sources/distributed-fs/ceph-client/arch/m68k/fpsp040/scale.S

### Purpose
`scale.S` implements the FPSP `FSCALE` operation, scaling a floating-point source by a power of two derived from the destination/source exponent operand according to 68881-compatible semantics. It handles normal results, denormal results, overflow, and underflow.

### Important APIs, Types, And Functions
The export is `sscale`. Constants include `SRC_BNDS`, and the file depends on `t_ovfl2`, `t_unfl`, `round`, and `t_resdnrm`. Important local paths include `src_small`, `src_in`, `src_pos`, `src_neg`, `denorm`, `fix_dnrm`, `fix_unfl`, `sm_dnrm`, `dst_dnrm`, and `src_out`. Scratch flags in `L_SCR1` and `L_SCR2` hold sign and inexact information.

### Control Flow
`sscale` extracts the integer scaling exponent from the source operand, records its sign, and handles exponents too small or too large to affect the destination normally. In-range positive and negative scaling adjusts the destination exponent and checks for normal, denormal, overflow, or underflow outcomes. Denormal paths shift mantissas, round when bits are lost, return signed zero or smallest denorm for directed rounding modes, and call `t_resdnrm` when a reportable denormal result must be exposed. Overflow and underflow branch to `t_ovfl2` or `t_unfl`.

### State, Persistence, And Dependencies
The routine mutates the FPSP temporary/result operand and scratch long fields. It uses FPCR rounding mode and FPSR status through helpers but has no persistent state. It depends on `round.S` for correct inexact rounding and on `kernel_ex.S` helpers for exception state.

### Integration Points
`do_func` dispatches unimplemented FSCALE here. Results return through standard FPSP result storage or exception reporting, depending on whether the helper paths set status and whether traps are enabled.

### Risks
FSCALE has many boundary cases: source exponent too small to matter, source exponent too large, destination becoming denormal, catastrophic underflow, directed rounding from zero to smallest denorm, and sign-preserving zero. Off-by-one exponent thresholds or missing sticky bits will produce incorrect gradual-underflow behavior.

### Test Signals
Tests should scale normal, denormal, zero, large, and tiny operands by positive and negative scale factors. Include values crossing normal/denormal thresholds, catastrophic underflow, overflow, all rounding modes, signed zero results, and directed-rounding cases that choose smallest positive or negative denorm.
