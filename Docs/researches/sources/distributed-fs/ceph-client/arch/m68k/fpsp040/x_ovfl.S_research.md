# sources/distributed-fs/ceph-client/arch/m68k/fpsp040/x_ovfl.S

Purpose: implements `fpsp_ovfl`, the overflow exception handler. It computes and stores the 68881-compatible overflow result for trap-disabled behavior, prepares the exceptional operand for trap-enabled behavior, and chains to inexact when required.

Important APIs/types/functions: exported label is `fpsp_ovfl`. Internal helper `ovf_adj` selects `WBTEMP` or `ETEMP`, normalizes sign into `LOCAL_SGN`, chooses opclass-specific overflow result routines `ovf_r_x2` or `ovf_r_x3`, and calls `store`. External exits are `real_ovfl`, `real_inex`, and `fpsp_done`; `b1238_fix` repairs known E3 frame cases.

Control flow: after saving state, it sets the accrued inexact bit the 040 fails to set, calls `ovf_adj` to store the rounded overflow result, then checks whether overflow traps are enabled. Enabled overflow branches to `real_ovfl` after E3 dirty-bit cleanup. Disabled overflow checks inexact enable and may branch to `real_inex`; otherwise it finishes via `fpsp_done`, using the E3 path to clear dirty bits, call `b1238_fix`, shadow FPSR, and set `sx_mask`.

State and persistence: no persistence. It mutates `FPSR_AEXCEPT`, destination FP register/memory via `store`, `FPR_DIRTY_BITS`, `FPSR_SHADOW`, and `E_BYTE` status bits.

Dependencies/integration: depends on `fpsp.h`, `util.S` overflow selectors, `x_store.S` store conversion, kernel real exception handlers, and `b1238_fix` from the FPSP bug-fix path.

Risks: E1 vs E3 operand selection changes whether `ETEMP` or `WBTEMP` is used. Opclass 3 move-out must preserve condition codes around `ovf_r_x3`. Inexact handling in this file tests only the enable bit for `inex2`, reflecting hardware-specific assumptions.

Test signals: overflow for register and memory destinations, all rounding modes/signs/precisions, opclass 3 condition-code preservation, enabled overflow trap exceptional operand, disabled overflow with and without inexact enabled, E3 dirty-bit cleanup, and bug1238 cases.
