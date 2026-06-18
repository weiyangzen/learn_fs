# sources/distributed-fs/ceph-client/arch/arm/mach-mvebu/dove.c

Purpose: Marvell Dove DT machine support.

Important APIs/types/functions: Defines Dove init, compatible table, and `DT_MACHINE_START(DOVE_DT, ...)`.

Control flow: Init sets up MBUS and Tauros2/cache/PMU pieces as appropriate, then populates DT devices.

State and persistence: State includes machine descriptor and initialized cache/MBUS platform state.

Dependencies and integration points: Depends on Dove PMU, Tauros2 cache support, MBUS, and DT platform drivers.

Risks: Descriptor delegates most work to drivers; cache/MBUS init mismatches affect DMA/peripherals.

Test signals: Boot Dove DT and verify cache, MBUS devices, timer/irq, and restart.
