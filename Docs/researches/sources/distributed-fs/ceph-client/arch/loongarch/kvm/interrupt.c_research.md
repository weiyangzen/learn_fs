# sources/distributed-fs/ceph-client/arch/loongarch/kvm/interrupt.c

Purpose: handles pending virtual interrupt and exception delivery into LoongArch guest CSR state.

Important APIs, types, and functions: `kvm_deliver_intr()`, `kvm_pending_timer()`, `kvm_deliver_exception()`, and internal `kvm_irq_deliver()`, `kvm_irq_clear()`, `_kvm_deliver_exception()`. `priority_to_irq[]` maps KVM priorities to CPU interrupt bits.

Control flow: clear bits are processed before pending bits. Timer/IPI/SWI/AVEC lines update ESTAT, while HWI lines update root GINTC. AVEC invokes `dmsintc_inject_irq()` when message interrupts are available. Exception delivery writes BADV/BADI/PRMD/CRMD/ERA/ESTAT and redirects PC to `EENTRY + code * vector_size`.

State and persistence: consumes and clears `vcpu->arch.irq_pending`, `irq_clear`, `exception_pending`, and `esubcode`; writes guest hardware CSRs. Timer delivery checks for TVAL inversion and preserves timer interrupt state.

Dependencies and integration points: called by `vcpu.c` immediately before guest entry. Integrated with DMSINTC, CSR helpers, timer emulation, and `kvm_queue_exception()` users in exit handling.

Risks: interrupt bit mapping and CSR side effects must match hardware. Exception and interrupt simultaneous delivery relies on ESTAT encoding. Timer inversion handling is subtle.

Test signals: guest interrupt-controller driver tests, timer interrupt delivery, queued exception injection for MMIO/ADE/INE, AVEC vectors, and migration of ESTAT/GINTC state.
