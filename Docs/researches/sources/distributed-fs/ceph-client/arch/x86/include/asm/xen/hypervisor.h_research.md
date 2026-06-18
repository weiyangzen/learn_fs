<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/xen/hypervisor.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/xen/hypervisor.h

Purpose: Exposes core Xen hypervisor state and x86-specific Xen helpers used outside the hypercall wrapper: shared info pointers, Xen signature discovery, PV dom0 MSI restore, CPU hotplug registration, PVH setup, lazy-mode batching, and ACPI capability sanitization.

Important APIs/types/functions: `HYPERVISOR_shared_info`, `xen_start_info`, `XEN_SIGNATURE`, `xen_cpuid_base()`, `xen_initdom_restore_msi()`, `xen_arch_register_cpu()`, `xen_arch_unregister_cpu()`, `xen_pvh_init()`, `mem_map_via_hcall()`, `enum xen_lazy_mode`, per-CPU `xen_lazy_mode`, `enter_lazy()`, `leave_lazy()`, `xen_get_lazy_mode()`, and `xen_sanitize_proc_cap_bits()`.

Control flow: Xen initialization discovers the CPUID base, maps shared/start info, and registers optional platform hooks. MMU and CPU update paths enter and leave lazy mode around batched operations, using BUG checks to enforce nesting correctness.

State and persistence behavior: Persistent state includes the Xen shared-info pointer, start-info pointer, and per-CPU lazy-mode state. PVH and dom0 helpers alter boot memory maps, MSI state, and ACPI processor capability views in external subsystems.

Dependencies and integration points: Depends on x86 `cpuid_base_hypervisor()`, BUG checks, per-CPU variables, boot params, PCI, ACPI, and Xen domain config symbols. Integrates with Xen PV/PVH boot, dom0 ACPI, CPU hotplug, MSI restoration, and paravirtual MMU batching.

Risks and test signals: Risks include lazy-mode imbalance, wrong CPUID leaf selection, BUG-only stubs called in unsupported configs, and PVH memory-map mismatch. Test Xen PV, PVH, dom0, CPU hotplug, MSI restore after suspend/resume, ACPI processor reporting, and debug builds that catch lazy-mode nesting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/xen/hypervisor.h -->
