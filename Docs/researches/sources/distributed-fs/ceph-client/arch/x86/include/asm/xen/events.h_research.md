<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/xen/events.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/xen/events.h

Purpose: Provides x86-specific Xen event-channel and IPI definitions, plus helpers for interrupt-state checks and event-channel rebind capability.

Important APIs/types/functions: `enum ipi_vector` with `XEN_RESCHEDULE_VECTOR`, function-call, spin-unlock, IRQ-work, and NMI vectors; `xen_irqs_disabled()`, `xchg_xen_ulong`, `xen_have_vector_callback`, `xen_support_evtchn_rebind()`, and `xen_percpu_upcall`.

Control flow: Xen event code calls `xen_irqs_disabled()` while handling upcalls and uses `xen_support_evtchn_rebind()` to decide whether event channels can be moved away from vCPU 0. The decision depends on PV/HVM mode and vector-callback availability.

State and persistence behavior: Persistent state is external: `xen_have_vector_callback` and `xen_percpu_upcall` record feature selection. This header only exposes the state and uses x86 `xchg` as the ordering primitive.

Dependencies and integration points: Depends on Xen domain mode helpers and x86 interrupt flag decoding. Integrates with event channels, IPI delivery, IRQ work, NMI routing, and HVM callback-vector setup.

Risks and test signals: Risks include incorrect interrupt-flag interpretation, event-channel affinity bugs on HVM guests without vector callbacks, and missing memory ordering assumptions. Test with PV and HVM event delivery, per-CPU upcalls, IRQ affinity changes, suspend/resume, CPU hotplug, and high-rate event-channel workloads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/xen/events.h -->
