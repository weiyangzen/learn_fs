## sources/distributed-fs/ceph-client/arch/m68k/fpsp040/sint.S

### Purpose
`sint.S` implements `FINT` and `FINTRZ` integer-rounding operations for the FPSP, plus an internal `sintdo` entry used by binary/decimal conversion. It rounds a double-extended input to an integral floating-point value and returns it in `%fp0`.

### Important APIs, Types, And Functions
Exports are `sint`, `sintd`, `sintrz`, and `sintdo`. It depends on `dnrm_lp`, `nrm_set`, `round`, `t_inx2`, `ld_pone`, `ld_mone`, `ld_pzero`, `ld_mzero`, and `snzrinx`. Scratch `L_SCR1` stores the selected rounding mode.

### Control Flow
`sint` extracts the user's rounding mode; `sintrz` forces round-to-zero; `sintdo` accepts a caller-provided mode. The main path converts the operand to internal extended format, classifies exponent ranges, returns the input unchanged for exponent >= 63, returns signed zero or one for exponent < 0 according to rounding mode, and otherwise denormalizes to expose fractional bits, calls `round`, normalizes, restores IEEE sign/exponent layout, and loads `%fp0`. `sintd` handles denormal inputs using the documented rounding-mode table.

### State, Persistence, And Dependencies
The routine mutates the operand at `%a0`, scratch mode state, and inexact FPSR bits via `t_inx2`. It has no persistent state. It depends on shared rounding/normalization and on load-constant helpers from other FPSP utility files.

### Integration Points
`tbldo.S` dispatches FINT and FINTRZ here, and `bindec.S` uses `sintdo` during packed decimal conversion. Exception status is propagated through `kernel_ex.S` and `gen_except`.

### Risks
The exponent thresholds determine whether fractional bits exist; off-by-one errors around exponent 0 and 63 change large or tiny values. Directed rounding for tiny negative and positive values must return signed zero or signed one exactly as the table states. `sintrz` must not leak the user's rounding mode into the operation.

### Test Signals
Test all rounding modes with values just below and above integers, `+/-0.5`, tiny normals, denormals, large already-integral values, values around `2**63`, signed zeros, and `FINTRZ` under non-zero user rounding modes. Verify inexact status when fractional bits are discarded.
