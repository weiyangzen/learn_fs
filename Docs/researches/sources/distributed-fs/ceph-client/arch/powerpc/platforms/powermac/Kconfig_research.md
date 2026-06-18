# sources/distributed-fs/ceph-client/arch/powerpc/platforms/powermac/Kconfig

Purpose: Kconfig definitions for Apple PowerMac support, 64-bit PowerMac extensions, and 32-bit PowerSurge SMP upgrade cards.

Important APIs and control flow: `PPC_PMAC` selects core PowerMac dependencies such as MPIC, forced PCI, indirect PCI/MPC106 on PPC32, hash MMU support, and optional CUDA reset. `PPC_PMAC64` selects U3 DART, MPIC U3 HT IRQ support, generic timebase sync, and 970 nap. `PPC_PMAC32_PSURGE` enables PowerSurge CPU-card SMP support with muxed IPIs and nomap IRQ domains.

State, dependencies, and risks: state is compile-time platform selection. Dependencies decide which PowerMac files and subsystems are built. Risks are broad default-y coverage, CPU endian/Book3S assumptions, and EXPERT-only SMP upgrade support being lightly tested. Test signals are 32-bit and 64-bit PowerMac build coverage, PowerSurge SMP configs, and correct dependency selection for PCI/MPIC/DART.
