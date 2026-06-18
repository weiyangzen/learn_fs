<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/processor-flags.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/processor-flags.h

Purpose: Publishes x86 EFLAGS, CR0, CR3, CR4, CR8, legacy Cyrix register, and initial CR0 state bit definitions usable from C and assembly.

Important APIs/types/functions: `X86_EFLAGS_*`, `X86_CR0_*`, `X86_CR3_*`, `X86_CR4_*`, `X86_CR8_TPR`, `CX86_*`, and `CR0_STATE`.

Control flow: Low-level kernel, boot, virtualization, signal, ptrace, and userspace tooling use these constants to test or program processor control state.

State and persistence behavior: The header owns no state; it names CPU register bits whose values persist in task context, vCPU context, or processor control registers.

Dependencies and integration points: Depends on Linux constant macros. Integrates with boot paging, CR4 feature enablement, VMX, SMEP/SMAP/PKE/CET/FRED/LAM, ptrace flag reporting, signal contexts, KVM, and low-level assembly.

Risks and test signals: Risks include wrong bit positions for new features, 32-bit handling of high CR4 bits, and stale reserved assumptions. Test boot on feature-rich CPUs, virtualization CR intercepts, ptrace/signal flag reporting, LAM/CET/FRED config builds, and assembly include paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/processor-flags.h -->
