# sources/distributed-fs/ceph-client/arch/x86/xen/enlighten.c

Purpose: Contains Xen guest state common to PV, HVM, and PVH modes: hypercall function selection, vCPU info placement, restore handling, panic/reboot handling, console preferences, vCPU pinning, extra-memory accounting, and shared exported globals.

Important APIs/types/functions: It defines the `xen_hypercall` static call, per-CPU `xen_vcpu`, `xen_vcpu_info`, and `xen_vcpu_id`, `machine_to_phys_mapping`, `xen_start_info`, `HYPERVISOR_shared_info`, `xen_domain_type`, and `xen_start_flags`. Key functions include `xen_hypercall_setfunc()`, `__xen_hypercall_setfunc()`, `xen_cpuhp_setup()`, `xen_vcpu_restore()`, `xen_vcpu_info_reset()`, `xen_vcpu_setup()`, `xen_banner()`, `xen_running_on_version_or_later()`, `xen_add_preferred_consoles()`, `xen_reboot()`, `xen_panic_handler_init()`, `xen_pin_vcpu()`, `xen_add_extra_mem()`, and `arch_xen_unpopulated_init()`.

Control flow and state: HVM/PVH guests start with a generic hypercall static call and switch to AMD/Hygon or Intel calling convention after vendor detection; PV replaces it earlier. vCPU setup maps per-CPU `vcpu_info` when supported, otherwise resets pointers into shared info. Restore temporarily downs other vCPUs, refreshes runstate/vCPU info, and brings them back up. Panic handling changes shutdown behavior when no crash kernel is loaded. Extra memory regions are reserved and later handed to unpopulated-page allocation or ballooning.

Dependencies and integration points: This file links Xen core interfaces with Linux CPU hotplug, static calls, panic notifiers, kexec, console selection, PMU shutdown, scheduler ops, memory resources, and balloon/unpopulated page handling.

Risks and test signals: vCPU info registration is one-shot per CPU, so restore/hotplug ordering is fragile. Hypercall function selection must be noinstr-safe. Panic policy changes visible shutdown behavior. Test signals include CPU hotplug and suspend/resume across Xen versions, HVM/PVH AMD/Intel hypercalls, panic with/without crash kernel, console ordering, vCPU pinning errors, and balloon target correctness from released pages.
