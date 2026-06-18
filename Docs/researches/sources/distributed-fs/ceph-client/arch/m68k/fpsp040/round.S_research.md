## sources/distributed-fs/ceph-client/arch/m68k/fpsp040/round.S

### Purpose
`round.S` supplies shared rounding, normalization, and denormalization primitives for the FPSP package. It rounds internal extended-format operands according to FPCR precision and rounding mode, extracts guard/round/sticky bits, normalizes mantissas, and constructs denormal results for underflow-sensitive code paths.

### Important APIs, Types, And Functions
Exports are `round`, `nrm_zero`, `nrm_set`, `denorm`, and `dnrm_lp`. The main caller contract for `round` is `%a0` pointing at an internal extended operand, `%d1` carrying precision in the high word and mode in the low word, and `%d0{31:29}` carrying guard/round/sticky bits. Internal tables `mode_tab`, `add_to_l`, and `trunct` dispatch by rounding mode or precision. It uses `USER_FPSR`, `LOCAL_EX`, `LOCAL_SGN`, `LOCAL_HI`, `LOCAL_LO`, `LOCAL_GRS`, and scratch space from `fpsp.h`.

### Control Flow
`round` first calls `ext_grs` to align guard/round/sticky bits for extended, single, or double precision. Exact results are truncated to the target precision. Inexact results set `inx2a_mask` in `USER_FPSR` and branch by rounding mode: toward plus/minus infinity conditionally increments based on sign, toward zero truncates, and round-to-nearest increments for guard-bit cases with tie-to-even behavior. `nrm_zero` and `nrm_set` shift mantissas and adjust exponents until normalized or zero. `denorm` and `dnrm_lp` shift a normalized internal value down to single/double/extended denormal thresholds while preserving sticky/inexact information.

### State, Persistence, And Dependencies
The routines mutate the operand at `%a0`, `%d0`/`%d1` scratch values, and inexact bits in `USER_FPSR`. There is no persistent state. All semantics depend on the internal extended operand layout and rounding constants in `fpsp.h`.

### Integration Points
The file is a shared dependency for `get_op.S`, `res_func.S`, `kernel_ex.S`, `sint.S`, `smovecr.S`, `scale.S`, and underflow helpers. It is also the normalization backend for denormal inputs and results throughout the FPSP tree.

### Risks
Rounding bugs are cross-cutting. A wrong guard/round/sticky extraction shifts all single/double results by one ulp, and tie-to-even mistakes show only on exact half-way cases. Denormalization must preserve sticky state across multiword shifts; losing it suppresses inexact/underflow flags. Carry propagation on increment can overflow the mantissa and must increment the exponent without dropping the hidden bit.

### Test Signals
High-signal tests include all four rounding modes, all three precisions, tie-to-even cases, carry-out from mantissa increment, exact truncation, inexact flag setting, zero normalization, leading-one normalization across high and low mantissa words, gradual underflow to denorm, catastrophic underflow to zero, and sticky-bit preservation for shifts greater than one word.
