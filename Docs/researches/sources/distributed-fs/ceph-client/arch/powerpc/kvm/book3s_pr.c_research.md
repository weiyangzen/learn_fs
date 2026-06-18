# sources/distributed-fs/ceph-client/arch/powerpc/kvm/book3s_pr.c

Purpose: this is the main implementation for Book3S PR KVM, where guests run without hypervisor mode, generally in problem state. It wires vCPU lifecycle, guest entry/exit, shadow MSR handling, MMU fault handling, facility/FPU ownership, PAPR/OSI/PV hcalls, one-reg state, memory invalidation, dirty logging, and module registration.

Important APIs: key entry points include `kvmppc_vcpu_run_pr()`, `kvmppc_handle_exit_pr()`, `kvmppc_copy_to_svcpu()`, `kvmppc_copy_from_svcpu()`, `kvmppc_set_msr_pr()`, `kvmppc_set_pvr_pr()`, `kvmppc_handle_pagefault()`, `kvmppc_giveup_ext()`, `kvmppc_giveup_fac()`, `kvmppc_set_fscr()`, vCPU create/free/load/put helpers, one-reg get/set handlers, VM init/destroy, and the `kvm_ops_pr` registration table.

Control flow: `kvmppc_vcpu_run_pr()` validates vCPU sanity, prepares interrupt entry, gives up host math state, optionally preloads FP, fixes EE state, and calls the assembly `__kvmppc_vcpu_run()`. Guest exits arrive at `kvmppc_handle_exit_pr()`, which decodes the Book3S interrupt number. Storage exits call `kvmppc_handle_pagefault()` to translate guest addresses, map shadow PTEs, inject guest faults, or route MMIO. Syscall exits dispatch in-kernel PAPR hcalls where possible or exit to userspace. Program/facility/math exits either emulate instructions, enable guest-owned facilities, or inject guest interrupts. Before re-entry it calls `kvmppc_prepare_to_enter()` and repairs lost external state.

State and persistence: per-vCPU state includes shadow vCPU content, shadow MSR, guest-owned FP/VMX/VSX bits, FSCR/TAR, SLB shadows, BAT/SR state, TM state, PVR-derived feature flags, split-real hack flags, timing counters, and shared page. Per-VM state includes `hpt_mutex`, enabled hcall bitmap, RTAS token list, and global relocation-on-exception user count for firmware set-mode platforms.

Dependencies and integration: it integrates with `book3s_interrupts.S` and `book3s_segment.S`, PR MMU implementations, `book3s_pr_papr.c`, RTAS, XICS, paired-single emulation, Linux FPU/Altivec/VSX context management, KVM MMU notifiers, and KVM core ops. Module init sets `kvmppc_pr_ops` and initializes the HPTE cache.

Risks: this file is the central correctness boundary for PR KVM. Risks include stale shadow translations, split-real address fixup mistakes, host math-state leakage, incorrect TM save/restore, facility masking errors, PVR feature misclassification, bad return-code choice between `RESUME_GUEST` and `RESUME_GUEST_NV`, and guest-visible behavior diverging from PAPR.

Test signals: boot 32-bit and 64-bit Book3S guests, PAPR guests, radix-host rejection, HPT mode on POWER9, dirty logging, MMIO, single-step debug, FPU/VMX/VSX/TAR/TM facilities, paired-single guests, split real mode, magic page transitions, and all major exit classes. Watch for bad registers after re-entry, missing guest interrupts, stale mappings, and host state corruption.
