# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/kvm_booke_hv_asm.h

Purpose: defines the assembler-side BookE HV exception redirection macro for guest-state exceptions on embedded hypervisor-capable cores.

Important APIs/types/functions: the assembler macro `DO_KVM intno srr1` checks MSR[GS] through `mtocrf` and branches to `kvmppc_handler_<intno>_<srr1>` inside a CPU feature section when `CONFIG_KVM_BOOKE_HV` and `CPU_FTR_EMB_HV` are enabled.

Control flow: normal exception prologues arrive with scratch registers already populated according to 32-bit or 64-bit entry conventions documented in the header. If the exception came from guest state, the macro branches into KVM; otherwise execution falls through to the host exception handler label.

State and persistence: no C state is stored here. It relies on prologue-saved scratch registers, PACA exception save areas, thread save areas, and bolted TLB miss state.

Dependencies and integration points: includes `feature-fixups.h`; integrates with BookE HV exception vectors, KVM BookE handler labels, MSR[GS] guest-state detection, and CPU feature patching.

Risks: register convention comments are part of the ABI between exception prologues and KVM handlers. A wrong `srr1` variant or missing feature patching can route host exceptions into KVM or miss guest exits.

Test signals: build `CONFIG_KVM_BOOKE_HV`, boot an e500mc/e6500 HV guest, inject normal and critical/debug/machine-check exceptions from guest and host contexts, and verify host-only exceptions fall through.
