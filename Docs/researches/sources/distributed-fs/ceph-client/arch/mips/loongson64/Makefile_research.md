<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/loongson64/Makefile -->
# sources/distributed-fs/ceph-client/arch/mips/loongson64/Makefile

Purpose: Selects Loongson-3/Loongson64 platform objects.

Important APIs/types/functions: Core `MACH_LOONGSON64` objects include CP2 exception handling, DMA, setup, init, env, time, and reset. Optional objects include SMP, NUMA, HPET, suspend sleeper, PCI quirks, CPUCFG emulation, and sysfs boardinfo.

Control flow: Object inclusion follows kernel config symbols such as `CONFIG_SMP`, `CONFIG_NUMA`, `CONFIG_RS780_HPET`, and `CONFIG_SYSFS`.

State and persistence: Build metadata only.

Dependencies and integration: Wires platform-specific boot, firmware, power, and exception code into the MIPS kernel build.

Risks: Missing config dependencies can leave required hooks absent, especially suspend requiring both `pm.o` and `sleeper.o`.

Test signals: Loongson64 defconfigs should link all selected platform hooks without unresolved symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/loongson64/Makefile -->
