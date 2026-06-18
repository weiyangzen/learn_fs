# sources/distributed-fs/ceph-client/arch/m68k/fpsp040/x_snan.S

Purpose: implements `fpsp_snan`, the signaling-NaN exception handler. It quiets/stores results for disabled traps, prepares enabled trap frames, handles integer move-out special cases, and preserves inexact chaining semantics.

Important APIs/types/functions: exported label is `fpsp_snan`. Internal helpers include `move_out`, `sto_long`, `sto_word`, `sto_byte`, `wrt_dn`, `not_out`, `dst_nan`, `issrc`, `report_snan`, and `end_snan`. External dependencies are `get_fline`, `mem_write`, `real_snan`, `real_inex`, `fpsp_done`, and `reg_dest`.

Control flow: after saving state, disabled SNAN traps call `move_out` and then check for enabled inexact. Enabled traps distinguish move-out instructions from non-move-out instructions; move-out gets corrected storage before reporting. Reporting paths expand the unimplemented frame into a busy frame, shadow FPSR, set `sx_mask`, restore state, and branch to `real_snan` or `fpsp_done`. For byte/word/long move-out, it writes the upper ETEMP mantissa with the quiet bit set either to memory or a Dn register.

State and persistence: no persistence. It writes user destinations for move-out integer formats, updates FPSR condition code negative bit based on source/destination NaN sign, rewrites the fsave frame to busy format, and may rewrite `EXC_VEC` for inexact.

Dependencies/integration: depends on `fpsp.h` frame layouts, `mem_write`, `reg_dest`, and real kernel exception handlers. It shares destination-register decoding style with `x_operr.S`.

Risks: frame expansion depends on version-specific sizes (`VER_40` vs revised frame), and incorrect counts would corrupt the exception stack. SNAN priority between destination and source NaNs is explicitly encoded; changing it affects IEEE exception reporting. Integer destination writes use `EXC_EA == 0` as the data-register indicator.

Test signals: disabled and enabled SNAN traps, move-out to byte/word/long Dn and memory, quiet-bit setting in stored mantissa, source-vs-destination NaN priority, negative condition code setting, inexact chaining, and busy-frame construction for both frame versions.
