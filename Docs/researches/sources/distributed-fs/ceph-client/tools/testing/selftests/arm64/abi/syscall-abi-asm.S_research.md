# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/abi/syscall-abi-asm.S

Purpose: assembly engine for `syscall-abi.c`, loading synthetic GPR/FPSIMD/SVE/SME state, issuing a syscall, and saving post-syscall state for C-side validation.

Important APIs/types/functions: exports `do_syscall`; defines SME instruction encoding macros `_ldr_za`, `_str_za`, `_ldr_zt`, `_str_zt`; uses globals `gpr_in/out`, `fpr_in/out`, `z_in/out`, `p_in/out`, `ffr_in/out`, `za_in/out`, `zt_in/out`, and `svcr_in/out`.

Control flow: saves callee-saved registers and input VLs, optionally writes SVCR and loads ZA/ZT0, loads GPRs and either FPSIMD or SVE predicate/vector/FFR state, executes `svc #0`, stores all relevant register state, records SVCR/ZA/ZT0 when SME is active, clears SVCR for future tests, restores callee-saved registers, and returns.

State and persistence: all state is exchanged through global buffers in the linked C file; no files.

Dependencies/integration: requires arm64 SVE/SME assembler support or raw encodings, `syscall-abi.h` bit definitions, and matching buffer layouts in `syscall-abi.c`.

Risks and test signals: any mismatch between vector length, buffer sizing, or register save order can create false ABI failures. The comment says x8 in GPR input selects syscall number; C-side checks validate preservation rules after return.
