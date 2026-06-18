# sources/distributed-fs/ceph-client/arch/arm/mach-mvebu/board-v7.c

Purpose: MVEBU ARMv7 DT machine initialization for Armada 370/375/38x/39x/XP.

Important APIs/types/functions: Defines board init, restart, L2/cache/coherency/PMSU integration, compatible tables, and DT machine descriptor.

Control flow: Machine init sets up SoC-specific services, coherency fabric, MBUS/device population, cpuidle/PM hooks, and restart path as appropriate before handing devices to DT.

State and persistence: State includes initialized coherency/PMSU/global platform hooks and registered platform devices. Hardware state includes MBUS/coherency/cache/restart controller setup.

Dependencies and integration points: Depends on MVEBU coherency, PMSU, CPU reset, system controller, OF platform population, L2 cache, and DT compatibles.

Risks: Init ordering is critical: coherency must be ready before DMA-heavy devices, and restart/PM hooks must match SoC. Missing DT nodes degrade features.

Test signals: Boot Armada V7 boards, verify DMA coherency, SMP, restart, cpuidle/suspend, and device population.
