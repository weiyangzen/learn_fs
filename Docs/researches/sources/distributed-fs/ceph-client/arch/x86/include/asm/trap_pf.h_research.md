# sources/distributed-fs/ceph-client/arch/x86/include/asm/trap_pf.h

Purpose: names x86 page-fault error-code bits used by fault handlers and diagnostics.

Important APIs/types/functions: `enum x86_pf_error_code` with `X86_PF_PROT`, `WRITE`, `USER`, `RSVD`, `INSTR`, `PK`, `SHSTK`, `SGX`, and `RMP`.

Control flow: none; this is a constants header. Fault handlers decode hardware-provided error code bits using these masks.

State/persistence: no state.

Dependencies/integration: depends on `linux/bits.h`. Integrated with page fault, signal, KVM/TDX/SEV, SGX, protection-key, and control-flow enforcement paths.

Risks/test signals: wrong bit assignments would misclassify protection, user/kernel, instruction-fetch, shadow-stack, SGX, or RMP faults. Test via page-fault selftests, pkeys, CET/shadow stack tests, SGX/SEV-SNP paths where available, and fault log decoding.
