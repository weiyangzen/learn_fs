## sources/distributed-fs/ceph-client/arch/m68k/fpsp040/res_func.S

### Purpose
`res_func.S` resolves unsupported data-format exceptions after operands have been decoded by `get_op`. Its core job is to normalize denormalized operands when that lets the 68040 replay and complete the instruction. It also implements the cases that cannot be replayed directly, notably packed move-out and several conversion/wraparound corner cases.

### Important APIs, Types, And Functions
Exports are `res_func` and `p_move`. Important internal regions are monadic/dyadic denorm handling, `wrap_div`, `wrap_add`, `wrap_sub`, `wrap_cmp`, `wrap_mul`, force-overflow/underflow paths, integer conversion helpers `li`, `wi`, `bi`, floating move-out helpers `xp`, `sgp`, `dp`, and packed output helpers `pack_out`, `p_movez`, `p_movei`, `p_moven`, `p_dyd0` through `p_dyd7`. External dependencies include `mem_write`, `bindec`, `get_fline`, `round`, `denorm`, `dest_ext`, `dest_dbl`, `dest_sgl`, `unf_sub`, `nrm_set`, `dnrm_lp`, `ovf_res`, `reg_dest`, `t_ovfl`, and `t_unfl`.

### Control Flow
`res_func` starts by clearing denorm/result flags and dispatches between dyadic destination handling, monadic source handling, and opclass 3 move-out. Denormal operands are converted into internal extended format, normalized with `nrm_set`, retagged, and usually written back so the hardware can retry. For operations that can generate wraparound or forced exceptions, opcode decoding routes through add/sub/mul/div/cmp-specific logic to decide whether to fix the stack, force overflow, force underflow, or finish in software. Move-out paths convert to integer or floating destination formats, check bounds (`sp_bnds`, `dp_bnds`), use rounding/denormal helpers, and call `mem_write` for memory destinations. Packed move-out routes through `bindec` and the `p_move*` dispatch tables.

### State, Persistence, And Dependencies
All mutable state is in FPSP local variables and the fsave frame: `DNRM_FLG`, `RES_FLG`, `CU_ONLY`, `DY_MO_FLG`, `STAG`, `DTAG`, `ETEMP`, `FPTEMP`, and scratch operands. It depends on `get_op.S` having tagged operands correctly and on `fpsp.h` command-register field definitions. Memory persistence occurs only when move-out instructions write to user memory through `mem_write`.

### Integration Points
The unsupported exception handler invokes `res_func` after `get_op`. Successful normalization flows back to hardware replay via the surrounding FPSP handler. Store and conversion flows integrate with `mem_write`, `reg_dest`, binary/decimal conversion, and destination-format routines. Exception generation is delegated to `kernel_ex.S` helpers and later `gen_except`.

### Risks
This is one of the densest FPSP files and has high regression risk. Small mistakes in tag transitions can produce repeated unsupported traps, incorrect replay, or corrupted user memory. Move-out conversion depends on destination size, rounding mode, signed range, and inexact/overflow status. Wraparound detection for arithmetic opcodes is highly branch-heavy and can easily force the wrong underflow/overflow behavior if command decoding changes.

### Test Signals
Tests should cover replay after source-only, destination-only, and both-operand denorms; packed decimal move-out to memory; integer byte/word/long conversion at boundaries; single/double/extended move-out under all rounding modes; denorm-to-zero and smallest-denorm results; arithmetic wrap cases for add, sub, mul, div, and cmp; and user-memory fault behavior through `mem_write`.
