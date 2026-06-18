# sources/distributed-fs/ceph-client/arch/x86/xen/Makefile

Purpose: Selects x86 Xen object files and special compiler flags according to the Xen Kconfig feature set.

Important behavior: It disables function tracing for low-level debug/time/IRQ spinlock objects and disables stack protector for early `enlighten_pv.o` and `mmu_pv.o`, which run before normal stack-protector setup. Common objects include `enlighten.o`, `mmu.o`, `time.o`, `grant-table.o`, and `suspend.o`. HVM/PVHVM adds HVM enlightenment, MMU, suspend, and platform unplug support. PV adds setup/APIC/PMU/suspend/p2m/enlighten/MMU/IRQ/multicall/asm support. PVH, SMP, PV spinlock, debugfs, Dom0 VGA, and EFI objects are conditional.

Control flow and state: Build composition controls runtime initialization paths registered through `hypervisor_x86`, paravirt ops, initcalls, and exported Xen helpers. There is no persistent state in the Makefile itself.

Dependencies and integration points: It mirrors `Kconfig` symbols and ties C/assembly modules into the x86 Xen subsystem. The object split matters because PV early boot cannot tolerate instrumentation or stack protector before GDT/TLS are initialized.

Risks and test signals: Incorrect object selection can lead to missing symbols or subtle boot failures in one guest mode. Test signals are allmodconfig/allyesconfig builds, PV boot without stack protector faults, HVM/PVH boot with platform unplug, and debugfs/EFI/Dom0-specific link coverage.
