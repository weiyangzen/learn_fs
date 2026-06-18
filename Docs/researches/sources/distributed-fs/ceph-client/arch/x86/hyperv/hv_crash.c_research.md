## `sources/distributed-fs/ceph-client/arch/x86/hyperv/hv_crash.c`

Purpose: root-partition Hyper-V crash/kdump support. It coordinates Linux and hypervisor crash handling, devirtualizes the root partition through a disable-hypervisor hypercall, and allows hypervisor RAM to be captured in vmcore.

Important APIs and functions: `hv_root_crash_init()` registers NMI handling, locates the hypervisor crash dump area, sets up trampoline/page tables, and overrides crash stop handling. `hv_crash_nmi_local()`, `hv_crash_stop_other_cpus()`, and `crash_nmi_callback()` synchronize CPUs and invoke `HVCALL_DISABLE_HYP_EX`. `hv_crash_c_entry()` restores long-mode kernel CPU state after the assembly trampoline returns. Helper setup functions build low-4G trampoline data and temporary page tables.

Control flow: on hypervisor crash, NMIs arrive and the shared crash dump area marks the condition. On Linux crash, the panic CPU sends NMIs to others. Non-BSP CPUs save state and spin; BSP waits for quorum, optionally notifies Hyper-V of root crash, saves CPU context, fixes TSS/page tables, issues the disable hypercall, and resumes via `hv_trampoline.S` into `hv_crash_c_entry()`, which restores registers and calls crash kexec.

State and persistence: global crash context, crash dump area pointer `hv_cda`, low-memory trampoline physical address, temporary page tables, CPU wait count, and booleans tracking hypervisor/Linux crash. Enables `crash_kexec_post_notifiers` and `hv_crash_enabled`.

Dependencies and integration points: Hyper-V root partition hypercalls, NMI subsystem, crash/kexec, APIC NMI delivery, page table primitives, GDT/IDT/TSS manipulation, Intel PT emergency stop, and the matching trampoline assembly.

Risks: this is panic/NMI/devirtualization code with little recovery latitude. Low-4G allocation, 5-level paging exclusion, exact struct offsets, TSS busy-bit handling, and interrupt-free hypercall buffers are critical. Wrong context restore can hang before vmcore capture.

Test signals: root partition kdump with loaded crash kernel, hypervisor crash simulation, Linux panic on BSP and non-BSP CPUs, no 5-level paging path, vmcore contains hypervisor RAM, and boot log says both Linux and hypervisor kdump support enabled.
