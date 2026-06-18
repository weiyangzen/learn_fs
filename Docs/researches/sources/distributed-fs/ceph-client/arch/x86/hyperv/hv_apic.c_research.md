## `sources/distributed-fs/ceph-client/arch/x86/hyperv/hv_apic.c`

Purpose: installs Hyper-V enlightened APIC operations for EOI/TPR/ICR access and IPI delivery.

Important APIs and functions: `hv_apic_init()` patches the global APIC callbacks. `hv_enable_coco_interrupt()` updates vector injection state. `hv_apic_read/write/icr_read/icr_write/eoi_write()` route selected APIC accesses through synthetic Hyper-V MSRs. `__send_ipi_one()`, `__send_ipi_mask()`, and `__send_ipi_mask_ex()` implement fast and extended IPI hypercalls.

Control flow: initialization checks Hyper-V recommendation hints. Cluster IPI support replaces APIC IPI callbacks while retaining `orig_apic` fallback. APIC access recommendation replaces EOI and, in xAPIC mode, read/write/ICR accessors. IPI senders validate vectors, translate Linux CPUs to Hyper-V VP numbers, use the fast 64-bit mask hypercall when possible, fall back to extended VP sets for larger VP indexes, and finally fall back to original APIC operations on unsupported cases.

State and persistence: `orig_apic` snapshots previous APIC methods. VP assist pages can suppress EOI MSR writes via lazy EOI. Per-CPU hypercall input pages are used transiently with interrupts disabled.

Dependencies and integration points: `ms_hyperv` hints/features, Hyper-V hypercall helpers, APIC callback patching, CPU-to-VP mapping, tracing, confidential-computing isolation checks, and VP assist pages allocated in `hv_init.c`.

Risks: wrong fallback behavior can lose IPIs. VP set construction must handle sparse/high VP indexes. Lazy EOI cannot be used under some confidential VM modes. IPI paths run with tight interrupt and ordering constraints.

Test signals: SMP boot and CPU hotplug under Hyper-V, high CPU-count guests requiring extended masks, interrupt delivery tests, APIC timer operation, and tracepoints for IPI calls.
