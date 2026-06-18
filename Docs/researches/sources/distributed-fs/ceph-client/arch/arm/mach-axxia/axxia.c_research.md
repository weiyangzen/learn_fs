# sources/distributed-fs/ceph-client/arch/arm/mach-axxia/axxia.c

Purpose: registers the LSI Axxia AXM55xx DT machine descriptor.

Important APIs/types/functions: `axxia_dt_match[]` and `DT_MACHINE_START(AXXIA_DT, ...)`.

Control flow: selected during ARM DT machine matching, with SMP handled separately by Axxia CPU method code.

State and persistence: descriptor-only; no mutable state.

Dependencies and integration: depends on Kconfig/Makefile and Axxia device-tree compatibles.

Risks: compatible drift prevents the platform from selecting the intended machine descriptor.

Test signals: AXM55xx DT boot and SMP method registration.
