# sources/distributed-fs/ceph-client/arch/loongarch/kvm/tlb.c

Purpose: provides LoongArch KVM TLB invalidation helpers for all guest entries or a single guest physical address.

Important APIs, types, and functions: `kvm_flush_tlb_all()` and `kvm_flush_tlb_gpa(struct kvm_vcpu *vcpu, unsigned long gpa)`.

Control flow: all-entry flush disables local IRQs, issues `invtlb_all(INVTLB_ALLGID)`, and restores IRQ state. GPA flush requires IRQs disabled, masks the GPA to the architecture granularity, and issues `invtlb(INVTLB_GID_ADDR, current GSTAT.GID, gpa)`.

State and persistence: changes processor TLB state only; does not mutate KVM structures.

Dependencies and integration points: used by VPID cycling, CPU virtualization enable/disable, MMU mapping changes, and late vCPU requests.

Risks: wrong GID or address masking can leave stale translations. Caller must satisfy IRQ-disabled assertion for GPA flush.

Test signals: memory remap/dirty-log tests, VPID wrap tests, guest TLB stale mapping stress, and lockdep assertions.
