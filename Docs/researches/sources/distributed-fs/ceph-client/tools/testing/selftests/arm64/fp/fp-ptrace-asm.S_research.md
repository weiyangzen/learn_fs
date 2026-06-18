<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/fp/fp-ptrace-asm.S -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/fp/fp-ptrace-asm.S

Purpose: assembly half of the comprehensive FP/SVE/SME ptrace test. It loads known register state from globals, stops for parent ptrace manipulation, saves resulting state back to globals, stops again, and exits streaming mode before returning.

Important APIs and symbols: exports `load_and_save(int flags)`. It consumes `HAVE_SVE`, `HAVE_SME`, `HAVE_SME2`, `HAVE_FA64`, and `HAVE_FPMR` from `fp-ptrace.h`, and SME helper macros from `sme-inst.h`. It accesses globals such as `v_in/out`, `z_in/out`, `p_in/out`, `ffr_in/out`, `za_in/out`, `zt_in/out`, `svcr_in/out`, `sve_vl_out`, `sme_vl_out`, and `fpmr_in/out`.

Control flow: save callee scratch registers, load FPSIMD V registers unconditionally, optionally set SVCR and load ZA/ZT for SME, optionally load SVE or streaming SVE Z/P/FFR state, optionally load FPMR, then execute `brk #0`. After the parent writes regsets, it saves FPSIMD/FPMR/SME/SVE/FFR state back to memory, executes a second `brk #0`, clears SME state, restores temporaries, and returns.

State and persistence: state is intentionally global and shared with `fp-ptrace.c` via fork-inherited virtual addresses. The BRK instructions are synchronization points; the parent advances PC by 4 to continue.

Dependencies and integration: tied directly to `fp-ptrace.c` and Linux NT_ARM_* ptrace regset semantics. It uses encoded SME/SME2 instructions for portability across assemblers.

Risks: any mismatch in global layout, VL selection, or SVCR mode invalidates comparisons. FFR is skipped when base SME lacks FA64, and streaming mode must be cleared before returning to avoid contaminating the C runtime.

Test signals: correct behavior is observed through parent-side ptrace reads and memory comparisons; failures surface as kselftest mismatch diagnostics in `fp-ptrace.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/fp/fp-ptrace-asm.S -->
