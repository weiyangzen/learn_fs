# sources/distributed-fs/ceph-client/arch/m68k/fpsp040/x_unimp.S

Purpose: implements `fpsp_unimp`, the 68040 FPSP handler for unimplemented floating-point instructions. It decodes operands, runs the software function dispatcher, stores results, and posts any generated exceptions.

Important APIs/types/functions: exported labels are `fpsp_unimp` and `uni_2`. It calls `get_op`, `do_func`, `sto_res`, `gen_except`, and `fpsp_fmt_error`.

Control flow: `fpsp_unimp` links a local frame and creates an fsave state frame, then enters `uni_2`. `uni_2` saves volatile data/address and FP registers, validates the fsave version as a 4x 68040 frame, clears transient FPSR exception/condition bits and FPCR user exceptions for internal computation, clears `UFLG_TMP`, calls `get_op`, clears `STORE_FLG`, calls `do_func`, captures any new FPU exception state with `fsave`, stores `%fp0` through `sto_res` unless `STORE_FLG` says not to, and branches to `gen_except`.

State and persistence: no persistence. It mutates the FPSP local frame, saved FPSR/FPCR, `UFLG_TMP`, `STORE_FLG`, operand scratch fields populated by `get_op`, and destination FP register state via `sto_res`.

Dependencies/integration: central integration point for `get_op.S`, `do_func.S`, `tbldo.S`, `sto_res.S`, and `gen_except.S`. `x_fline.S` can branch directly into `uni_2` after synthesizing an unimplemented frame for `fmovecr`.

Risks: fsave frame validation is the only guard before deep FPSP emulation. Clearing FPSR/FPCR bits is intentional; failing to restore/post via `gen_except` would lose user-visible exceptions. `STORE_FLG` must be honored for functions that store through specialized paths.

Test signals: unimplemented monadic functions, dyadic functions, invalid fsave version to format error, `STORE_FLG` suppression, result storage to all FP destinations, generated overflow/underflow/inexact propagation, and `x_fline` `uni_2` entry compatibility.
