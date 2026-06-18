# sources/distributed-fs/ceph-client/arch/arm/mach-mvebu/cpu-reset.c

Purpose: MVEBU per-CPU reset controller helper.

Important APIs/types/functions: Defines CPU reset/deassert helpers including `mvebu_cpu_reset_deassert()` and initialization over DT reset-controller registers.

Control flow: Init maps CPU reset registers, and callers deassert/reset secondary CPU lines during SMP boot or hotplug.

State and persistence: Global mapped reset base and hardware CPU reset state are the key state.

Dependencies and integration points: Depends on DT reset-controller/system-controller nodes, SMP boot code, and MVEBU common declarations.

Risks: Wrong CPU id/register bit mapping prevents secondary CPU boot or can reset the wrong core.

Test signals: Boot all CPUs and exercise CPU hotplug on Armada boards.
