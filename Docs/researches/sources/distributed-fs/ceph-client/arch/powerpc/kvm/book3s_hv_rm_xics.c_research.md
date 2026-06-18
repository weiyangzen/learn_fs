# sources/distributed-fs/ceph-client/arch/powerpc/kvm/book3s_hv_rm_xics.c

## Purpose

`book3s_hv_rm_xics.c` implements real-mode XICS interrupt-controller handling for Book3S HV KVM. It lets common interrupt hcalls and pass-through MSI delivery complete without exiting to virtual mode when state is simple, while flagging `H_TOO_HARD` when host work, debugging, notifier callbacks, or vcpu kicking cannot safely be handled in real mode.

## Important APIs, Types, And Functions

Global tunables are `h_ipi_redirect` and `kvm_irq_bypass`. Key functions are `xics_rm_h_xirr_x()`, `xics_rm_h_xirr()`, `xics_rm_h_ipi()`, `xics_rm_h_cppr()`, `xics_rm_h_eoi()`, `kvmppc_deliver_irq_passthru()`, and `kvmppc_xics_ipi_action()`. Local helpers include `ics_rm_check_resend()`, `icp_send_hcore_msg()`, `grab_next_hostcore()`, `find_available_hostcore()`, `icp_rm_set_vcpu_irq()`, `icp_rm_clr_vcpu_irq()`, `icp_rm_try_update()`, `icp_rm_try_to_deliver()`, `icp_rm_deliver_irq()`, `icp_rm_down_cppr()`, `ics_rm_eoi()`, `icp_eoi()`, and real-mode per-CPU IRQ stat updating.

The main types are `struct kvmppc_xics`, `struct kvmppc_icp`, `union kvmppc_icp_state`, `struct kvmppc_ics`, `struct ics_irq_state`, `struct kvmppc_irq_map`, and `struct kvmppc_passthru_irqmap`.

## Control Flow

Interrupt delivery starts in `icp_rm_deliver_irq()`. It finds the ICS and IRQ source, locks the ICS, resolves the target ICP if the interrupt moved servers, handles resend filtering, marks masked interrupts as `masked_pending`, tries to deliver by atomically replacing ICP `xisr` and `pending_pri`, and handles rejected interrupts by recursively retrying delivery. Failed delivery marks source `resend`, updates the ICP resend bitmap, and retries if the ICP `need_resend` flag was cleared in the race window.

`xics_rm_h_xirr()` clears the vcpu external interrupt indication, atomically accepts the current pending interrupt by returning XISR|CPPR in GPR4, sets CPPR to the pending priority, and clears `xisr`. `xics_rm_h_ipi()` updates MFRR, may replace the pending interrupt with XICS_IPI, handles rejected interrupts and resend checks, and returns `H_TOO_HARD` if real-mode deferred work accumulated. `xics_rm_h_cppr()` raises or lowers CPPR, clearing local interrupt output when raising priority and invoking `icp_rm_down_cppr()` when lowering priority may expose resends or IPIs. `xics_rm_h_eoi()` lowers CPPR based on XIRR, skips ICS EOI for IPIs, and for real IRQs advances LSI/MSI PQ state, redelivers if needed, records EOI notifiers as deferred actions, and adjusts pass-through affinity through OPAL if host IRQ affinity no longer matches the guest core.

Pass-through delivery in `kvmppc_deliver_irq_passthru()` updates IRQ stats in real mode, converts the real interrupt to a virtual hwirq, atomically updates MSI PQ state, delivers to the ICP when P transitions to presented, EOIs the real interrupt through OPAL or XICS MMIO, and returns either direct-delivery status or a host-completion request.

## State And Persistence Behavior

ICP state is a 64-bit atomic state machine containing CPPR, MFRR, XISR, pending priority, output EE, and need-resend. ICS state persists per-source priority, server, resend, masked-pending, LSI/MSI PQ state, host IRQ, and interrupt CPU. Vcpu state records pending external exceptions, stats, and deferred real-mode actions in `icp->rm_action`, `rm_kick_target`, and `rm_eoied_irq`. Host-core redirection uses `kvmppc_host_rm_ops_hv->rm_core[]` state and data until `kvmppc_xics_ipi_action()` runs in host context.

## Dependencies And Integration Points

The real-mode hcall table in `book3s_hv_rmhandlers.S` calls the XICS hcall handlers. Completion of deferred operations is handled by virtual-mode XICS code in `book3s_xics.c`. The file integrates with OPAL interrupt calls, PowerNV PCI MSI EOI, host IPI machinery, KVM vcpu kick callbacks, irq descriptors/statistics, and the Book3S XICS data structures declared in `book3s_xics.h`.

## Risks

The atomic ICP transitions are race-sensitive. Incorrect ordering around `resend`, `resend_map`, and `need_resend` can lose interrupts. Real-mode cannot safely perform all host actions, so missing an `H_TOO_HARD` condition can execute unsafe work in real mode, while excessive `H_TOO_HARD` harms latency. Pass-through EOI and affinity adjustment can misroute interrupts if `intr_cpu` or OPAL server updates are wrong. Per-CPU stat increments handle vmalloc per-CPU storage manually, which is architecture-sensitive.

## Test Signals

Signals include XICS guests issuing `H_XIRR`, `H_XIRR_X`, `H_IPI`, `H_CPPR`, and `H_EOI` in real mode, interrupt rejection/resend storms, masked MSI and LSI sources, vcpu kick redirection when a target vcpu is not loaded, irq ack notifier fallback, pass-through MSI delivery and EOI, host IPI completion through `kvmppc_xics_ipi_action()`, and real-mode debug forcing `H_TOO_HARD`.
