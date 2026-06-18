# sources/distributed-fs/ceph-client/arch/m68k/fpsp040/x_unfl.S

Purpose: implements `fpsp_unfl`, the underflow exception handler. It denormalizes, rounds, and stores intermediate results for 68881/68882-compatible trap-disabled behavior, while preparing enabled underflow and inexact trap paths.

Important APIs/types/functions: exported label is `fpsp_unfl`. Internal helper `unf_res` performs precision selection, operand selection, `denorm`, `round`, store dispatch, condition-code updates, and accrued-underflow updates. External dependencies are `denorm`, `round`, `store`, `g_rndpr`, `g_opcls`, `g_dfmtou`, `real_unfl`, `real_inex`, `fpsp_done`, and `b1238_fix`.

Control flow: the handler saves state and calls `unf_res`. If underflow traps are enabled, it performs E3 cleanup and branches to `real_unfl`. If disabled, it checks enabled/reported inexact and may branch to `real_inex`. Otherwise it finishes through `fpsp_done`, with E3 dirty-bit clearing and bug1238 repair where needed. `unf_res` chooses `WBTEMP` for E3 and `FPTEMP` for E1, handles `fsgldiv/fsglmul` precision quirks, denormalizes, rounds with FPCR mode, adjusts single/double denormal exponent bias for opclass 3 memory stores, calls `store`, and sets zero/negative condition codes for FP-register stores.

State and persistence: no persistence. It mutates the result operand, destination, FPSR condition/accrued bits, `FPR_DIRTY_BITS`, `FPSR_SHADOW`, and E-byte state. It relies on stack-passed precision/mode data between `denorm` and `round`.

Dependencies/integration: tightly coupled to `round.S`, `x_store.S`, `util.S`, and `fpsp.h`. Kernel-level exits are `real_unfl`, `real_inex`, and `fpsp_done`.

Risks: comments warn that `%d0` guard/round/sticky bits and `%a0` must not be corrupted between `denorm` and `round`. Bias adjustment for single/double memory denormals is easy to break. Inexact/accrued-underflow handling depends on `FPSR_EXCEPT` bits set by rounding.

Test signals: underflow to FP register and memory, extended/single/double destinations, fsglmul/fsgldiv precision overrides, exact vs inexact underflow, enabled underflow traps, enabled inexact chaining, signed zero/smallest denormal results, and E3 dirty-bit repair.
