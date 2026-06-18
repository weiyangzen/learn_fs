# sources/distributed-fs/ceph-client/arch/m68k/fpsp040/x_unsupp.S

Purpose: implements `fpsp_unsupp`, the FPSP handler for unsupported data type exceptions such as packed formats, denormalized numbers, and unnormalized numbers. It normalizes/unpacks operands, restores the operation into the 040 where possible, and posts generated exceptions.

Important APIs/types/functions: exported label is `fpsp_unsupp`. It calls `get_op`, `res_func`, `gen_except`, and `fpsp_fmt_error`.

Control flow: the handler links a local frame, performs `fsave`, saves volatile and FP state, stores the fsave version in `VER_TMP`, validates a 4x 68040 frame, clears live FPSR/FPCR, preserves or clears selected saved FPSR fields depending on whether the instruction is `fmove out`, sets `UFLG_TMP`, calls `get_op`, calls `res_func` to repair the stack frame or perform packed move-out storage, pushes an idle-format word with the saved version, and branches to `gen_except`.

State and persistence: no persistence. It mutates saved FPSR state, `UFLG_TMP`, the fsave frame, and operand/result scratch built by `get_op`/`res_func`.

Dependencies/integration: depends on `fpsp.h` frame layouts and on the operand decoder/result restorer pair. `gen_except` owns final exception posting and return.

Risks: unsupported-data handling is frame-format sensitive. The special FPSR preservation for `fmove out` keeps condition codes and SNAN/accrued state, while other operations clear condition and exception bytes; mixing those paths would change user-visible status. `res_func` must correctly decide whether to restart hardware or complete a packed store in software.

Test signals: packed input/output, denormal and unnormalized operands, `fmove out` vs non-`fmove out` FPSR preservation, invalid fsave frame, `UFLG_TMP` behavior in `get_op`, and final `gen_except` posting.
