<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/uapi/asm/sigcontext.h -->
# sources/distributed-fs/ceph-client/arch/loongarch/include/uapi/asm/sigcontext.h

Purpose: defines LoongArch signal context ABI, including optional extended contexts.
Important APIs and types: declares `struct sigcontext`, `struct sctx_info`, `fpu_context`, `lsx_context`, `lasx_context`, and `lbt_context`, plus magic numbers, alignment constants, and flags such as `SC_USED_FP` and address-error flags.
Control flow: signal delivery writes these records; `rt_sigreturn` parses magic/alignment-linked contexts and restores CPU/FPU/vector/LBT state.
State and persistence: user stack signal frames are ABI state visible to signal handlers, debuggers, and libcs.
Dependencies and integration: must match kernel signal code, FPU/LSX/LASX/LBT save/restore, UAPI `ucontext.h`, and ptrace register formats.
Risks and test signals: ABI drift breaks signal restore or vector-state preservation. Signals include signal selftests, sigaltstack, vector/LBT signal tests, and GDB signal handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/uapi/asm/sigcontext.h -->
