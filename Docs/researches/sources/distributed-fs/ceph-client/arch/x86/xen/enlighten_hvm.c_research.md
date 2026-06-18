# sources/distributed-fs/ceph-client/arch/x86/xen/enlighten_hvm.c

Purpose: Initializes Xen HVM/PVHVM guest enlightenments: shared-info mapping, callback vector handling, vCPU setup, event/interrupt/time/MMU hooks, device unplug, nopv behavior, and hypervisor registration.

Important APIs/types/functions: `xen_hvm_init_shared_info()` maps Xen shared info into a reserved PFN. `reserve_shared_info()` and `xen_hvm_init_mem_mapping()` transition the mapping from early memremap to normal virtual addressing. `init_hvm_pv_info()` detects CPUID Xen data and vCPU id. `sysvec_xen_hvm_callback` handles event-channel upcalls. CPU hotplug uses `xen_cpu_up_prepare_hvm()` and `xen_cpu_dead_hvm()`. `xen_hvm_guest_init()`, `xen_hvm_guest_late_init()`, and `xen_platform_hvm()` implement the hypervisor init flow. `x86_hyper_xen_hvm` exports the registration.

Control flow and state: Detection checks Xen CPUID and respects `nopv`/`xen_nopv`, with special PVH handling. Initialization reserves a low RAM page for shared info, maps it via `XENMEM_add_to_physmap`, initializes vCPU pointers, installs panic and SMP hotplug hooks, unplugs emulated devices, and installs Xen IRQ/time/MMU ops. Late init upgrades ACPI-discovered PVH and sets restart behavior. `xen_percpu_upcall` controls per-CPU callback EOI behavior.

Dependencies and integration points: It depends on CPUID Xen leaves, memory ops, event channels, ACPI CPU UID, APIC/IO-APIC, kexec/crash hooks, virtio restricted-memory callbacks, platform unplug, SMP, timer, and HVM MMU support.

Risks and test signals: Incorrect shared-info reservation or remapping breaks event channels and pvclock. `nopv` exceptions for PVH are policy-sensitive. CPU hotplug must not double-register vCPU info. Test signals include HVM and PVH boot, per-CPU vector callbacks, no-vector fallback, CPU online/offline, kexec soft reset, crash shutdown, virtio grant restrictions, and emulated device unplug behavior.
