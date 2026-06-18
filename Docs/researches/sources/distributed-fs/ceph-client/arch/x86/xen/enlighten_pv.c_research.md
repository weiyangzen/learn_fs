# sources/distributed-fs/ceph-client/arch/x86/xen/enlighten_pv.c

Purpose: Implements the core Xen PV paravirt backend and first C boot path. It replaces privileged CPU/MMU/interrupt operations with Xen hypercalls, sets PV CPU capabilities, rewrites IDT/GDT/TLS handling, manages PV event upcalls, and boots the kernel from Xen `start_info`.

Important APIs/types/functions: Major entry points include `xen_start_kernel()`, `xen_pv_init_platform()`, `xen_setup_vcpu_info_placement()`, `xen_init_capabilities()`, `xen_cpuid()`, descriptor operations (`xen_load_gdt()`, `xen_load_idt()`, `xen_write_*_entry()`), segment/MSR/control-register hooks, `xen_pv_evtchn_do_upcall()`, trap conversion helpers, PV machine ops, NMI reason handling, EDD boot-param import, and PV CPU hotplug callbacks.

Control flow: `xen_start_kernel()` clears BSS, records `start_info`, patches early iret, marks PV domain state, installs `pv_info` and `pv_ops`, initializes IRQ/APIC/MMU ops, builds p2m and page tables, sets GDT before stack-protected code, disables incompatible features, registers CPU hotplug, maps the kernel into physical memory, sets IOPL, fills boot params/initrd/cmdline, handles Dom0 vs DomU legacy/PCI/ACPI/VGA differences, initializes runstate/EFI, and jumps into normal x86 reservations. Runtime context switches enter lazy CPU mode and batch descriptor/TLS changes.

State and persistence behavior: Persistent PV state includes `xen_initial_gdt`, per-CPU lazy mode and shadow TLS descriptors, optional preemptible hypercall flags, cached CR0 values, boot CPUID MWAIT leaf overrides, `xen_msr_safe`, and per-CPU IDT descriptors. Trap tables and descriptor pages are mirrored to Xen, with guest page permissions changed to satisfy hypervisor validation.

Dependencies and integration points: It ties Linux paravirt ops to Xen hypercalls, event channels, PMU emulation, MTRR/ACPI firmware data, APIC/SMP/time/MMU setup, PCI, boot params, hvc consoles, virtio grant restrictions, and PV assembly stubs.

Risks and test signals: This is extremely boot-order-sensitive because stack protector, percpu base, interrupt flags, and vCPU info are not fully initialized early. Descriptor conversion must not expose unsupported IST paths. MSR safe/unsafe behavior changes fault handling. Test signals include PV Dom0/DomU boot, SMP hotplug, trap delivery for NMI/#DB/#DF/#MC, syscall/MSR setup, TLS/LDT changes, EDD/VGA import, ACPI Dom0 behavior, and absence of early stack or paravirt faults.
