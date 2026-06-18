## `sources/distributed-fs/ceph-client/arch/x86/hyperv/hv_init.c`

Purpose: main x86 Hyper-V initialization, CPU lifecycle, hypercall page setup, VP assist pages, reenlightenment, hibernation syscore operations, panic reporting, PCI quirks, and initialization status helpers.

Important APIs and functions: exported state includes `hv_hypercall_pg`, `hv_ghcb_pg`, and `hv_vp_assist_page`. Key functions are `hyperv_init()`, `hyperv_cleanup()`, `hv_cpu_init()`, `hv_cpu_die()`, `set_hv_tscchange_cb()`, `clear_hv_tscchange_cb()`, `hyperv_stop_tsc_emulation()`, `hyperv_report_panic()`, `hv_is_hyperv_initialized()`, and `hv_apicid_to_vp_index()`. x86-64 uses a static call for `hv_std_hypercall()`.

Control flow: `hyperv_init()` verifies the Hyper-V hypervisor, runs common init, allocates VP assist/GHCB state, registers CPU hotplug callbacks, writes guest OS ID, initializes or skips the hypercall page depending on isolation/paravisor mode, calls root crash init when appropriate, hooks timers/APIC/PCI/MSI domains, queries capabilities, records VTL, and optionally starts VTL early init. CPU online allocates/maps VP assist pages, enables the VP assist MSR, maps GHCB pages for SNP paravisor, and enables stimer vector injection. Suspend disables hypercalls and CPU0 state; resume reinitializes and restores.

State and persistence: global hypercall page pointer and static-call target, saved hypercall pointer across hibernation, per-CPU GHCB mappings, per-CPU VP assist pages, reenlightenment callback, and Hyper-V MSR-programmed guest ID/hypercall state.

Dependencies and integration points: Hyper-V common code, APIC and timer setup, syscore, cpuhotplug, GHCB/SNP/TDX isolation helpers, root crash support, PCI/MSI IRQ domain, VMBus hypercall pages, and x86 initialization hooks.

Risks: early boot order is delicate: LAPIC timers, hypercall page permissions, confidential VM page encryption, and static-call updates must occur in the right context. Panic cleanup avoids `static_call_update()` after CPUs stop. VP assist page zeroing prevents lazy-EOI offline hangs.

Test signals: Hyper-V guest boot, root partition boot, TDX/SNP paravisor and no-paravisor paths, CPU hotplug, hibernation, reenlightenment/TSC frequency changes, panic MSR reporting, and `hv_is_hyperv_initialized()` consumers.
