# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/kvm_book3s.h

Purpose: declares the main Book3S KVM architecture interface: shadow segment/BAT state, HPTE caches, virtual-core scheduling state, Book3S per-vcpu MMU state, interrupt injection helpers, HPT/radix MMU operations, nested-HV hooks, transactional-memory save/restore, and common register accessors.

Important APIs/types/functions: core types are `struct kvmppc_bat`, `struct kvmppc_sid_map`, `struct hpte_cache`, `struct kvmppc_vcore`, and `struct kvmppc_vcpu_book3s`. Exported operations cover hash and radix translation (`kvmppc_mmu_map_page`, `kvmppc_book3s_radix_page_fault`, `kvmppc_mmu_radix_xlate`), HPTE cache lifecycle, HPT hypercalls (`kvmppc_do_h_enter`, `kvmppc_do_h_remove`), dirty logging, page pinning, interrupt priority queues, BAT/MSR/FSCR updates, nested guest entry and nested TLB invalidation, and accessors for GPR, CR, XER, LR, CTR, PC, FPR, VSX, VMX, VCORE timing, and DEC expiry state.

Control flow: Book3S guest execution enters through PR or HV backends, maps faults through HPT or radix paths, queues pending interrupts by priority, and returns to guest or host using resume flags from `kvm_asm.h`. Accessor macros for nestedv2 reload/dirty tracking conditionally call expensive guest-state-buffer helpers only when `kvmhv_is_nestedv2()` is active; otherwise they collapse to no-ops.

State and persistence: persistent VM state is held in `vcpu->arch.book3s`, `vcpu->arch.vcore`, HPTE hash lists, VSID context arrays, SLB shadows, BAT arrays, LPCR/PCR/timebase fields, and dirty/rmap structures. Virtual-core state persists across runs and coordinates runnable threads, napping threads, stolen/preempted time, and online counts.

Dependencies and integration points: depends on Linux KVM core, `kvm_book3s_asm.h`, guest-state-buffer support, HPTE constants from `kvm_host.h`, radix page-table code, XICS/XIVE interrupt code, pSeries hypercalls, and nested-HV support.

Risks: this is a cross-subsystem contract header; changes can break assembly entry, KVM ioctls, nested virtualization, memory-slot dirty logging, or interrupt delivery. HPTE cache and rmap updates require careful locking/RCU. Nestedv2 dirty tracking must not be skipped for registers that are cached in the guest-state buffer.

Test signals: run Book3S PR and HV guest boot tests, HPT and radix memory-pressure tests, migration dirty-log tests, nested guest entry/TLB invalidation tests, XICS/XIVE interrupt injection, TM emulation tests, and KVM selftests that exercise one-reg access and vcpu run/exit state.
