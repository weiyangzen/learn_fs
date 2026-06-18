# sources/distributed-fs/ceph-client/arch/arm/mach-berlin/berlin.c

Purpose: registers Marvell Berlin DT machine support.

Important APIs/types/functions: Berlin compatible table for BG2/BG2CD/BG2Q families and `DT_MACHINE_START(BERLIN_DT, ...)` with SMP ops when configured.

Control flow: ARM machine matching selects the descriptor; SMP startup is provided by Berlin CPU method code.

State and persistence: descriptor-only state.

Dependencies and integration: depends on Berlin Kconfig symbols, Makefile objects, and DT root compatibles.

Risks: missing compatible entries prevent affected Berlin boards from booting under this descriptor.

Test signals: boot across BG2/BG2CD/BG2Q DTs and secondary CPU online when SMP is enabled.
