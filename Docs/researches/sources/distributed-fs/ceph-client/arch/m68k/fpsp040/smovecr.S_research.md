## sources/distributed-fs/ceph-client/arch/m68k/fpsp040/smovecr.S

### Purpose
`smovecr.S` implements the unimplemented `FMOVECR` constant-load instruction. It decodes the constant offset from the instruction, selects a rounding-mode-specific precomputed constant, and returns the rounded value in `%fp0`.

### Important APIs, Types, And Functions
The export is `smovcr`. It depends on `nrm_set`, `round`, and the constant tables exported by `get_op.S`: `PIRN`, `PIRZRM`, `PIRP`, `SMALRN`, `SMALRZRM`, `SMALRP`, `BIGRN`, `BIGRZRM`, and `BIGRP`. Internal labels select `PI_TBL`, `SM_TBL`, `BG_TBL`, `set_finx`, `no_finx`, and `fin_fcr`.

### Control Flow
`smovcr` extracts the 7-bit offset from `CMDREG1B` and the rounding mode from `USER_FPCR`. Offset 0 selects pi. Offsets `0x0b` through `0x0e` select small constants such as log10(2), e, log2(e), and log10(e). Offsets `0x30` through `0x3f` select large constants including ln(2), ln(10), and powers of ten. Unsupported offset ranges return zero. For constants with known inexact encodings, `set_finx` records inexact; for destination precisions below extended, the routine converts to internal format and calls `round`.

### State, Persistence, And Dependencies
The routine reads instruction and FPCR state from the FPSP frame and may set inexact FPSR bits. It returns `%fp0` and has no persistent state. It depends on `get_op.S` table ordering and on the FPCR precision/mode bit layout from `fpsp.h`.

### Integration Points
`tbldo.S` dispatches FMOVECR opcodes to `smovcr`, and `get_op.S` defines the tables it consumes. Final exception reporting follows the standard inexact path.

### Risks
The offset map is architectural. Returning zero for reserved offsets is intentional; accidentally treating a reserved offset as a table index can read unrelated data. Rounding-mode-specific low bits are precomputed, so using RN data for RZ/RM/RP is incorrect. Inexact status differs per constant and offset group and must be preserved.

### Test Signals
Test all architected FMOVECR offsets under RN, RZ, RM, and RP, plus reserved offset ranges that should return zero. Verify extended, single, and double precision outputs, inexact flag behavior, pi low-bit variants, powers-of-ten table entries, and no out-of-range table access.
