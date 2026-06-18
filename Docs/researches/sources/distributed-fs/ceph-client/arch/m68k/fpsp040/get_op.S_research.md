## sources/distributed-fs/ceph-client/arch/m68k/fpsp040/get_op.S

### Purpose
`get_op.S` decodes and normalizes operands for 68040 unsupported data/format and unimplemented instruction exceptions. It determines the instruction opclass, converts unnormalized and packed operands into the FPSP internal extended format, updates source/destination tags, and prepares the next module, typically `do_func` for unimplemented operations or `res_func` for unsupported data-format recovery.

### Important APIs, Types, And Functions
Exports are `get_op`, `uns_getop`, `uni_getop`, and rounding-sensitive constant tables `PIRN`, `PIRZRM`, `PIRP`, `SMALRN`, `SMALRZRM`, `SMALRP`, `BIGRN`, `BIGRZRM`, `BIGRP`, plus power-of-ten tables `PTENRN`, `PTENRM`, and `PTENRP`. Important internal helpers are `chk_dy_mo`, `mk_norm`, `unpack`, `fix_nan`, `move_unpack`, and `fix_stag`. It calls external `nrm_zero`, `decbin`, and `round`, and uses `fpsp.h` tags and fields such as `CMDREG1B`, `STAG`, `DTAG`, `ETEMP`, `FPTEMP`, `WBTEMP`, and `DY_MO_FLG`.

### Control Flow
`get_op` distinguishes unsupported and unimplemented entry paths, then branches on the opclass and move-out direction bits in `CMDREG1B`. Unsupported opclass 3 move-outs may pack a source operand immediately. Dyadic/monadic state is computed by `chk_dy_mo`. Extended, single, double, and packed operands flow through tag checks; unnormalized numbers are normalized with `mk_norm`, denormal tags are preserved for later handling, and packed decimal values are unpacked through `unpack` and `decbin`. The `fix_nan`/`move_unpack` path canonicalizes NaN, zero, normal, and infinity classifications and updates FPSR condition codes where fmove semantics require it.

### State, Persistence, And Dependencies
The routine mutates only the FPSP stack frame: source and destination tags, temporary operands, condition-code/status bytes, and scratch fields. The exported constant tables are read-only data consumed here and by `smovecr.S`. It depends on exact 68881/68882 opclass encodings carried in the 68040 command registers and on shared normalization semantics from `round.S`.

### Integration Points
The caller is the unsupported-format handler (`unsupp`, vector 55) or unimplemented-instruction handler (`unimp`, vector 11). Successful normalization feeds `do_func`, `res_func`, packed conversion helpers, or hardware replay through `frestore`. The move-constant implementation in `smovecr.S` uses the constant tables defined here, so table ordering and rounding variants are part of the local ABI.

### Risks
Risks cluster around tag accuracy and packed conversion. If `STAG`/`DTAG` is updated inconsistently with the actual temporary operand, later `res_func` or hardware replay will treat a denorm as normal or vice versa. Packed decimal unpacking depends on exact k-factor, sign, and exponent handling. The rounding-specific constants differ by one low bit in several entries; sharing the wrong table between RN/RZ/RM/RP changes required IEEE results.

### Test Signals
High-value tests include unsupported extended unnorm, single denorm, double denorm, packed move-in, packed move-out, and dyadic operations with only the source or destination denormalized. Compare output tags, saved operands, and FPSR condition codes before replay. FMOVECR tests should verify all constants under all four rounding modes because this file owns the canonical constant data.
