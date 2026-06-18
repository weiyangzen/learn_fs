# sources/distributed-fs/ceph-client/arch/arm/mach-mvebu/armada-370-xp.h

Purpose: Small Armada 370/XP SMP declaration header.

Important APIs/types/functions: Declares `armada_xp_secondary_startup()` and `armada_xp_smp_ops`.

Control flow: No runtime flow.

State and persistence: No state.

Dependencies and integration points: Integrates assembly secondary startup with C SMP ops.

Risks: Symbol mismatches break secondary CPU boot linkage.

Test signals: Compile Armada XP SMP and boot secondary CPUs.
