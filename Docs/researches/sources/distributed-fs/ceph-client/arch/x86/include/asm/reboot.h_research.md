<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/reboot.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/reboot.h

Purpose: declares x86 machine reboot, halt, poweroff, shutdown, and crash shutdown operations. Important type is `struct machine_ops`; important APIs include `machine_ops`, `crashing_cpu`, `native_machine_crash_shutdown()`, `native_machine_shutdown()`, `machine_real_restart()`, `nmi_shootdown_cpus()`, and `run_crash_ipi_callback()`.

Control flow: generic reboot/poweroff paths dispatch through `machine_ops`; crash paths mark `crashing_cpu`, shoot down other CPUs via NMI callbacks, and may enter real-mode restart. State is runtime machine operation pointers and crash CPU identity.

Dependencies include kdebug, `pt_regs`, realmode reboot assembly dispatch values `MRR_BIOS`/`MRR_APM`, SMP/NMI infrastructure, and crash-kexec. Risks include failed CPU shootdown, unsafe callback execution in NMI/crash context, and mismatched realmode dispatch constants. Test signals include reboot, halt, poweroff, emergency restart, crash dump, NMI shootdown, and BIOS/APM restart modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/reboot.h -->
