# sources/distributed-fs/ceph-client/arch/m68k/fpsp040/sto_res.S

Purpose: stores FPSP function results into the user-requested floating-point destination register after a software-emulated function completes. `sto_res` stores the primary result from `%fp0`; `sto_cos` stores the cosine half of `fsincos` from `%fp1`.

Important APIs/types/functions: exported labels are `sto_res` and `sto_cos`. They decode destination register fields from `CMDREG1B`: `sto_res` uses bits `{#6:#3}`, while `sto_cos` uses bits `{#13:#3}`. For registers `%fp0-%fp3`, they write the saved user register slots (`USER_FP0`..`USER_FP3`); for `%fp4-%fp7`, they build a dynamic `fmovemx` mask and move directly.

Control flow: each entry extracts the destination register number, branches to explicit `%fp0-%fp3` cases for saved-frame copies, or pushes `%fp0`/`%fp1` and restores it through a computed FPU dynamic mask for higher registers. It returns to the unimplemented-instruction handler, which later restores saved registers and posts exceptions.

State and persistence: no persistence. The only state updated is the FPSP local exception frame's saved `USER_FPn` images or the live higher-numbered FPU destination register.

Dependencies/integration: depends on `fpsp.h` command register and saved-register offsets. Called by `x_unimp.S` after `do_func` unless `STORE_FLG` suppresses result storage. `sto_cos` supports `ssincos`-style dual outputs.

Risks: destination bitfield decoding must match the 68040 command word layout. If `%fp0-%fp3` saved copies are not updated, later exception cleanup would restore stale values and lose the computed result. Dynamic masks for `%fp4-%fp7` depend on the `7 - dest` convention used by `fmovemx`.

Test signals: test all eight destination FP registers for normal monadic results, all `fsincos` cosine destination encodings, preservation of `%d2/%a0` caller assumptions, and restoration paths that reload `%fp0-%fp3` from `USER_FPn`.
