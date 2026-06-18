# sources/distributed-fs/ceph-client/arch/arm/mach-mmp/Makefile

Purpose: Build glue for Marvell MMP platform support.

Important APIs/types/functions: Builds `common.o`, `time.o`, DT board files, `mmp3.o`, and optional `platsmp.o` according to CPU/machine/SMP symbols.

Control flow: No runtime flow.

State and persistence: No runtime state.

Dependencies and integration points: Depends on MMP Kconfig symbols.

Risks: Incorrect object gating can include wrong machine descriptors or omit SMP/timer support.

Test signals: Compile matrix for PXA168/PXA910/MMP2/MMP3 and SMP on/off.
