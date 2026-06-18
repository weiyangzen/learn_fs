## sources/distributed-fs/ceph-client/arch/m68k/fpsp040/kernel_ex.S

### Purpose
`kernel_ex.S` provides helper routines that force FPSR status, condition codes, and default results for exceptional cases detected inside FPSP transcendental and arithmetic routines. Instead of immediately invoking OS traps, these helpers set the user FPSR/FPCR-facing state so `gen_except` can later decide whether the exception is enabled and reportable.

### Important APIs, Types, And Functions
Exports include `t_dz`, `t_dz2`, `t_operr`, `t_unfl`, `t_ovfl`, `t_ovfl2`, `t_inx2`, `t_frcinx`, `t_extdnrm`, `t_resdnrm`, `dst_nan`, `src_nan`, and `t_avoid_unsupp`. Static constants represent negative infinity, positive infinity, NaN, and huge finite extended values. External dependencies are `ovf_r_k`, `unf_sub`, and `nrm_set`. The code uses `USER_FPSR`, `FPCR_ENABLE`, `FPSR_CC`, `FPSR_EXCEPT`, `ETEMP`, `FPTEMP`, and scratch operands from `fpsp.h`.

### Control Flow
Each `t_*` entry handles one exception/result family. Divide-by-zero returns signed infinity when disabled or records enabled trap status when enabled. `t_operr` records invalid operation. Underflow and overflow paths inspect FPCR enable bits: disabled traps compute substitute rounded finite, zero, denormal, infinity, or huge results, while enabled traps preserve operands and mark status. `t_inx2` and `t_frcinx` set inexact/accrued bits. `dst_nan` and `src_nan` propagate NaNs and distinguish signaling from quiet NaNs. `t_extdnrm` and `t_resdnrm` normalize or underflow denormal results, and `t_avoid_unsupp` rewrites denormal operands to avoid repeated unsupported-data traps on hardware replay.

### State, Persistence, And Dependencies
The file mutates saved FPSR state and the temporary/result operand in the FPSP local frame. No persistent kernel state is kept. It depends on callers placing operands in `ETEMP` or `FPTEMP`, on FPCR enable bits being current, and on downstream `gen_except` interpreting the same FPSR status/accrued masks.

### Integration Points
Transcendental files call these helpers at exceptional boundaries: logs call `t_dz`/`t_operr`, trig/hyperbolic routines call `t_frcinx`, exp/cosh/scale call `t_ovfl`/`t_unfl`, and denorm-specific entries call `t_extdnrm` or `t_resdnrm`. `res_func.S` and lower-level underflow/overflow helpers also use the same result-normalization contract.

### Risks
The biggest risk is disagreement between result substitution and FPCR trap-enable state. Disabled traps must return the architecturally required value and set accrued bits; enabled traps must avoid corrupting the operand frame that will be reported. NaN propagation is another sensitive area because signaling NaNs must raise invalid operation while quiet NaNs generally propagate. `t_avoid_unsupp` touches nested fsave-frame state and can cause replay loops if it fails to recognize denorms correctly.

### Test Signals
Tests should run each exception helper with FPCR traps enabled and disabled and compare FPSR bits plus returned fp0/operand images. Useful cases are signed divide by zero, invalid operation from out-of-domain functions, overflow under each rounding mode, gradual underflow, denormal result normalization, quiet NaN propagation, signaling NaN invalid operation, and replay of denormal operands without an unsupported loop.
