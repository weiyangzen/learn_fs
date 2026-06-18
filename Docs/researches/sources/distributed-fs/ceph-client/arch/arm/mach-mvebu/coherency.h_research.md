# sources/distributed-fs/ceph-client/arch/arm/mach-mvebu/coherency.h

Purpose: Declarations for MVEBU coherency support shared with C and assembly.

Important APIs/types/functions: Declares `coherency_base`, `coherency_phys_base`, `set_cpu_coherent()`, `coherency_init()`, and `coherency_available()`.

Control flow: No runtime flow.

State and persistence: Exposes global coherency mapping/physical base state.

Dependencies and integration points: Used by board init, SMP/PM code, and `coherency_ll.S`.

Risks: Declaration/type drift breaks low-level assembly and SMP coherency entry.

Test signals: Compile MVEBU coherency and boot SMP/DMA workloads.
