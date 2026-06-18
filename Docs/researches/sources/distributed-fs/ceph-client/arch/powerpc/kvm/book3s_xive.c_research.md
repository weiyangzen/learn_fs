<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kvm/book3s_xive.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/kvm/book3s_xive.c

Purpose: Implements the Book3S KVM XICS-compatible interrupt controller backed by the POWER XIVE hardware. It lets a guest use legacy XICS hcalls while KVM manages XIVE VPs, interrupt queues, escalation interrupts, emulated IPIs, pass-through IRQs, source state, migration state, and debugfs visibility.

Important APIs/types/functions: Exports `kvm_xive_ops`, `kvmppc_xive_xics_hcall()`, `kvmppc_xive_connect_vcpu()`, `kvmppc_xive_cleanup_vcpu()`, `kvmppc_xive_set_xive()`, `kvmppc_xive_get_xive()`, `kvmppc_xive_int_on()`, `kvmppc_xive_int_off()`, `kvmppc_xive_set_irq()`, `kvmppc_xive_set_mapped()`, `kvmppc_xive_clr_mapped()`, `kvmppc_xive_get_icp()`, `kvmppc_xive_set_icp()`, `kvmppc_xive_push_vcpu()`, `kvmppc_xive_pull_vcpu()`, `kvmppc_xive_rearm_escalation()`, source allocation/free helpers, queue debug helpers, and VP/server sizing helpers.

Control flow: Device creation allocates or reuses a `kvmppc_xive`, initializes queue geometry and flags, and stores it in `kvm->arch.xive`. `connect_vcpu` allocates a VP, IPI, queues, and escalation IRQs. Guest XICS hcalls dispatch through `kvmppc_xive_xics_hcall()`: `H_XIRR` acknowledges TIMA pending bits, scans queues, and returns XIRR; `H_CPPR` changes CPPR and either pushes pending work or rescans rerouted entries; `H_EOI` performs ESB EOI and pending re-evaluation; `H_IPI` updates MFRR and triggers the target IPI; `H_IPOLL` peeks without consuming. Source configuration provisions queues, masks/unmasks via ESB PQ transitions, retargets through OPAL `xive_native_configure_irq()`, and maintains queue counts. Migration get/set converts XIVE queue/PQ state into XICS-compatible source and ICP state.

State and persistence: Persistent VM state includes VP block IDs, per-vCPU CPPR/hardware CPPR/MFRR/pending bits, queue pages, queue counters, escalation IRQs, source blocks, guest/saved/actual priority, P/Q snapshots, LSI assertion, pass-through hardware IRQ data, delayed restore IRQs, and source migration counters. State is protected by `xive->lock`, per-source `arch_spinlock_t`, `vcpu->mutex` during teardown, atomics for queue occupancy, and explicit barriers around CPPR/MFRR/PQ/EOI races.

Dependencies and integration points: Depends on Linux KVM Book3S, XICS ABI constants, XIVE native/OPAL helpers, irqdomain/IRQ affinity, debugfs/seq_file, KVM device attributes, hcall dispatch, and Book3S guest entry code that pushes/pulls XIVE context. Native XIVE mode uses its shared helpers and `reset_mapped` hook when ESB pages are exposed to guests.

Risks: The main risk is interrupt loss, duplication, or queue overflow across mask/unmask, retargeting, EOI, and migration. The code relies on subtle memory ordering between `guest_priority`, `in_eoi`, MFRR, CPPR, ESB MMIO, and escalation state. Pass-through mapping must preserve host IRQ ownership and clear guest ESB mappings. Device release intentionally recycles `kvmppc_xive` storage, so lifetime assumptions are delicate.

Test signals: Strong signals include POWER9/POWER10 KVM guests in XICS-on-XIVE mode, hotplugged vCPUs, hcall stress for XIRR/CPPR/EOI/IPI/IPOLL, LSI and MSI injection, irqfd/MSI pass-through map/unmap, migration save/restore with pending interrupts, cede/escalation wakeups, debugfs source/queue inspection, lockdep/KCSAN, and Book3S KVM selftests or QEMU pseries interrupt-controller tests.

Source read size: 2976 lines, 77630 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kvm/book3s_xive.c -->
