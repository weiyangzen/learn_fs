# sources/distributed-fs/ceph-client/arch/m68k/fpsp040/bugfix.S

Purpose: Motorola FPSP workaround code for 68040 FPU bug 1238, repairing affected fsave frames/results before normal FPSP completion.

Important API and labels: exports `b1238_fix`; key labels include `op0`, `op0_xu`, `op0_xi`, `op0_xb`, `op2sgl`, `op2_xu`, `op2_xi`, `op2_com`, case labels, `finish`, and `fix_done`. It can jump to `fpsp_fmt_error` when a busy frame cannot be reconstructed safely.

Control flow and state: the routine inspects the FPSP fsave frame and command/register fields, branches by operand/result class, manipulates ETEMP/FPTEMP/WBTEMP bits and tag fields, reconstructs or adjusts exponent/mantissa/sign bits, handles FP register destinations, and returns when either no fix is required or the frame is corrected.

Dependencies and integration: uses `fpsp.h` frame offsets and is called from general exception cleanup paths before `fpsp_done` or real exception dispatch. It modifies only the FPSP local/fsave frame and saved user FPU state.

Risks and test signals: this is errata-specific and frame-format-specific; incorrect version/format interpretation can corrupt user floating-point state. Test with Motorola FPSP bug 1238 trigger cases, unsupported frame formats, FP0-FP3 destinations, and exception paths that continue to real F-line handling.
