# sources/distributed-fs/ceph-client/arch/powerpc/kvm/book3s_xics.c

Purpose: this file implements the emulated XICS interrupt controller for Book3S KVM. It models interrupt source controllers (ICS), interrupt presentation controllers (ICP), PAPR XICS hcalls, KVM device attributes, debugfs state, and passthrough IRQ mapping metadata.

Important APIs: source control functions include `kvmppc_xics_set_xive()`, `get_xive()`, `int_on()`, `int_off()`, and `kvmppc_xics_set_irq()`. ICP/hcall handlers include `kvmppc_xics_hcall()`, `kvmppc_xics_rm_complete()`, `kvmppc_h_xirr()`, `h_ipi()`, `h_cppr()`, `h_eoi()`, and `h_ipoll()`. Device/lifecycle functions include `kvm_xics_ops`, `kvmppc_xics_connect_vcpu()`, `kvmppc_xics_free_icp()`, `kvmppc_xics_get_icp()`, `kvmppc_xics_set_icp()`, and mapped IRQ setters.

Control flow: `ics_deliver_irq()` updates per-source P/Q state, handles MSI versus LSI behavior, and calls `icp_deliver_irq()` when an interrupt should be presented. `icp_deliver_irq()` locks the source, resolves the target server, handles masked-pending and resend state, and attempts an atomic ICP delivery. ICP state transitions use `icp_try_update()` with a 64-bit compare/exchange on `union kvmppc_icp_state`; successful output queues `BOOK3S_INTERRUPT_EXTERNAL` and may kick the target vCPU. Hcalls manipulate XIRR, CPPR, MFRR, EOI, and resend checks according to PAPR-like state transitions. Device attrs serialize/restore source state for migration.

State and persistence: `struct kvmppc_xics` owns an array of up to 1024 ICS pointers and per-device flags. Each `struct kvmppc_ics` has a spinlock and 1024 `ics_irq_state` entries. Each vCPU can own one `struct kvmppc_icp` with atomic CPPR/MFRR/pending/XISR state and resend bitmap. Source state contains priority, saved priority, server, P/Q bits, resend, masked pending, LSI/MSI mode, host IRQ, and interrupt CPU.

Dependencies and integration: integrates with Book3S interrupt queuing, KVM device framework, KVM IRQ routing, migration attrs, RTAS/PAPR hcalls, optional real-mode HV completion, debugfs, and passthrough IRQ acknowledgement via `kvm_notify_acked_irq()`.

Risks: the code intentionally mixes spinlocked ICS state with lockless atomic ICP updates; memory barriers around resend maps are critical. Server lookup is linear across vCPUs. Restoring ICP/ICS state from userspace must be internally consistent or interrupts can be lost/replayed. Real-mode completion uses deferred action bits and must be cleared exactly once.

Test signals: MSI and LSI injection, mask/unmask with pending interrupts, XIRR/CPPR/EOI/IPI/IPOLL hcalls, migration get/set of ICP and source attrs, passthrough IRQ acknowledgement, vCPU connect/free, real-mode too-hard completion, and debugfs inspection. Watch for stuck external interrupts, lost resends, invalid priority ordering, and migration state rejection.
