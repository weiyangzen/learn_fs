# sources/distributed-fs/ceph-client/arch/powerpc/platforms/Kconfig

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/Kconfig -->
## sources/distributed-fs/ceph-client/arch/powerpc/platforms/Kconfig

### Purpose
Top-level PowerPC platform Kconfig aggregation and shared platform feature definitions.

### Important APIs, Types, And Functions
Sources platform submenus for powernv, pseries, chrp, 512x, 52xx, powermac, pasemi, ps3, cell, 8xx, 82xx, 83xx, 85xx, 86xx, embedded6xx, 44x, amigaone, book3s, and microwatt. Defines shared symbols such as `KVM_GUEST`, `EPAPR_PARAVIRT`, `PPC_HASH_MMU_NATIVE`, `PPC_OF_BOOT_TRAMPOLINE`, `PPC_DT_CPU_FTRS`, `PPC_SMP_MUXED_IPI`, `IPIC`, `MPIC`, `MPIC_TIMER`, `FSL_MPIC_TIMER_WAKEUP`, `PPC_EPAPR_HV_PIC`, `MPIC_MSGR`, `PPC_I8259`, RTAS/EEH/idle/TAU/QE/CPM options, and RTC helpers.

### Control Flow
No runtime flow. These symbols control compilation, architecture features, and driver availability.

### State, Persistence, And Dependencies
State is build configuration. Dependencies are cross-Kconfig selections and architecture capability relationships.

### Integration Points
This is the platform configuration hub consumed by top-level and per-platform Makefiles.

### Risks
Shared feature symbols affect many platforms; bad dependencies can create invalid builds or silently disable platform support.

### Test Signals
Run broad PowerPC config builds, verify menu visibility, selected symbols, and compile coverage for MPIC, RTAS, EEH, CPM, and platform submenus.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/Kconfig -->
