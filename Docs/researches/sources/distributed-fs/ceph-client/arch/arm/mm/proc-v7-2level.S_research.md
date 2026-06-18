# sources/distributed-fs/ceph-client/arch/arm/mm/proc-v7-2level.S

## Purpose
This file contains the ARMv7 non-LPAE, two-level page-table implementation pieces shared by the main ARMv7 processor support: context switching, PTE installation, memory attribute constants, TTB setup macro, and control-register values.

## Important APIs, Types, and Functions
It defines `cpu_v7_switch_mm()` for 32-bit TTBR0 updates and `cpu_v7_set_pte_ext()` for Linux-to-hardware small-page PTE conversion. It defines TTB flag constants for UP/SMP, PRRR/NMRR values for TEX remap attributes, `v7_ttb_setup`, and `v7_crval`.

## Control Flow
`switch_mm()` reads `mm->context.id`, applies page-table walk cacheability/shareability flags, optionally preserves PID bits in CONTEXTIDR, applies erratum barriers, writes CONTEXTIDR, then writes TTBR0. `set_pte_ext()` stores the Linux PTE, constructs a hardware PTE with permissions, TEX, XN, valid/young/none checks, stores the hardware copy at the expected offset, and cleans the PTE cache line on UP.

## State and Persistence Behavior
The file mutates TTBR0, CONTEXTIDR, hardware PTE words, and possibly PTE cache state. Constants and macros are assembled into the ARMv7 proc setup path.

## Dependencies and Integration Points
It is included/paired with `proc-v7.S` for non-LPAE builds. It depends on ARMv7 CP15, SMP alternatives, ARM errata options, page-table bit definitions, and `proc-macros.S` helpers.

## Risks
PTE bit translation controls executable, user, readonly, dirty, and valid semantics. TTB flags affect page-table walk coherency on SMP. CONTEXTIDR/PID insertion must preserve ASID bits. LPAE builds must use `proc-v7-3level.S` instead.

## Test Signals
Build ARMv7 non-LPAE UP and SMP kernels, run ASID/context-switch stress, permission and NX tests, module/vmalloc `set_memory_*()` tests, and page-table debug checks. Exercise configurations with `CONFIG_PID_IN_CONTEXTIDR` and erratum 754322.
